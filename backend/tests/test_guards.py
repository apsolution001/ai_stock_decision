"""Static guards for the coding standards that a unit test cannot otherwise catch."""

import ast
import re
from pathlib import Path

APP_DIR = Path(__file__).resolve().parents[1] / "app"
CLOCK_FILE = APP_DIR / "core" / "clock.py"

# now()/utcnow()/today() on a datetime-class receiver (datetime.datetime, datetime.date,
# pandas.Timestamp all share this vocabulary, so one set covers all of them).
_DATETIME_NOW_ATTRS = {"now", "utcnow", "today"}
_TIME_MODULE_ATTRS = {"time", "time_ns", "localtime", "gmtime", "ctime", "strftime"}
_TIME_DIRECT_NAMES = {"time", "time_ns", "localtime", "gmtime", "ctime", "strftime"}
_DATETIME_CLASS_IMPORT_NAMES = {"datetime", "date"}
_WALL_CLOCK_STRING_ARGS = {"now", "today"}

AliasMap = dict[str, set[str]]


def _collect_import_aliases(tree: ast.Module) -> AliasMap:
    """Resolve the names this file's own imports bind, grouped by wall-clock receiver kind.

    Aliasing (`import x as y`, `from x import y as z`) is resolved here so the caller never
    has to guess what a bare name refers to.
    """
    aliases: AliasMap = {
        "datetime_module": set(),
        "datetime_class": set(),
        "time_module": set(),
        "time_direct": set(),
        "pandas_module": set(),
        "numpy_module": set(),
    }
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                bound = alias.asname or alias.name
                if alias.name == "datetime":
                    aliases["datetime_module"].add(bound)
                elif alias.name == "time":
                    aliases["time_module"].add(bound)
                elif alias.name == "pandas":
                    aliases["pandas_module"].add(bound)
                elif alias.name == "numpy":
                    aliases["numpy_module"].add(bound)
        elif isinstance(node, ast.ImportFrom):
            if node.module == "datetime":
                for alias in node.names:
                    if alias.name in _DATETIME_CLASS_IMPORT_NAMES:
                        aliases["datetime_class"].add(alias.asname or alias.name)
            elif node.module == "time":
                for alias in node.names:
                    if alias.name in _TIME_DIRECT_NAMES:
                        aliases["time_direct"].add(alias.asname or alias.name)
    return aliases


def _has_wall_clock_string_arg(node: ast.Call) -> bool:
    return any(
        isinstance(arg, ast.Constant) and arg.value in _WALL_CLOCK_STRING_ARGS for arg in node.args
    )


def _is_wall_clock_call(node: ast.Call, aliases: AliasMap) -> bool:
    func = node.func

    # A direct wall-clock function alias call, e.g. `time()` from `from time import time`.
    if isinstance(func, ast.Name):
        return func.id in aliases["time_direct"]

    if not isinstance(func, ast.Attribute):
        return False

    # <datetime-class-alias>.now/utcnow/today(...)
    if (
        func.attr in _DATETIME_NOW_ATTRS
        and isinstance(func.value, ast.Name)
        and func.value.id in aliases["datetime_class"]
    ):
        return True

    # <time-module-alias>.time/time_ns/localtime/gmtime/ctime/strftime(...)
    # (deliberately excludes monotonic/perf_counter: those never read the wall clock)
    if (
        func.attr in _TIME_MODULE_ATTRS
        and isinstance(func.value, ast.Name)
        and func.value.id in aliases["time_module"]
    ):
        return True

    # Two-level attribute access: <dt-module>.datetime.now(...), <dt-module>.date.today(...),
    # <pandas-alias>.Timestamp.now/today/utcnow(...)
    if isinstance(func.value, ast.Attribute) and isinstance(func.value.value, ast.Name):
        root = func.value.value.id
        mid = func.value.attr
        if root in aliases["datetime_module"]:
            if mid == "datetime" and func.attr in _DATETIME_NOW_ATTRS:
                return True
            if mid == "date" and func.attr == "today":
                return True
        if (
            root in aliases["pandas_module"]
            and mid == "Timestamp"
            and func.attr in _DATETIME_NOW_ATTRS
        ):
            return True

    # <pandas-alias>.to_datetime("now"|"today")
    if (
        isinstance(func.value, ast.Name)
        and func.value.id in aliases["pandas_module"]
        and func.attr == "to_datetime"
        and _has_wall_clock_string_arg(node)
    ):
        return True

    # <numpy-alias>.datetime64("now"|"today")
    return bool(
        isinstance(func.value, ast.Name)
        and func.value.id in aliases["numpy_module"]
        and func.attr == "datetime64"
        and _has_wall_clock_string_arg(node)
    )


def _reads_wall_clock(source: str, filename: str = "<snippet>") -> bool:
    """AST-based wall-clock detector.

    Receivers are resolved from this file's own imports so aliasing (`import time as t`)
    can't hide a wall-clock read, and an unrelated `.now()` on some other object (e.g.
    `clock.now()`, `self._clock.now()`) can't trigger a false positive.
    """
    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        raise AssertionError(f"could not parse {filename} for the wall-clock guard: {exc}") from exc
    aliases = _collect_import_aliases(tree)
    return any(
        _is_wall_clock_call(node, aliases) for node in ast.walk(tree) if isinstance(node, ast.Call)
    )


def _sources() -> list[Path]:
    return sorted(APP_DIR.rglob("*.py"))


def test_guard_sees_the_app_tree() -> None:
    assert CLOCK_FILE in _sources()


def test_only_clock_reads_the_wall_clock() -> None:
    offenders = [
        str(path.relative_to(APP_DIR))
        for path in _sources()
        if path != CLOCK_FILE and _reads_wall_clock(path.read_text(encoding="utf-8"), str(path))
    ]
    assert offenders == [], f"use app.core.clock.now() instead: {offenders}"


def test_wall_clock_detector_catches_aliases() -> None:
    flagged = [
        "import datetime as dt\ndt.datetime.now()",
        "from datetime import datetime as DT\nDT.now()",
        "from time import time\ntime()",
        "import time\ntime.time()",
        "from datetime import date\ndate.today()",
        "import time as t\nt.time()",
        "from time import localtime\nlocaltime()",
        "import pandas as pd\npd.Timestamp.now()",
        "import numpy as np\nnp.datetime64('now')",
    ]
    for source in flagged:
        assert _reads_wall_clock(source), f"should flag: {source!r}"

    not_flagged = [
        "from app.core import clock\nclock.now()",
        "class A:\n    def f(self):\n        return self._clock.now()",
        "import time\ntime.monotonic()",
        "import time\ntime.perf_counter()",
        "x = 1\nprint(x)",
    ]
    for source in not_flagged:
        assert not _reads_wall_clock(source), f"should not flag: {source!r}"


def test_no_float_money_in_risk() -> None:
    offenders = [
        str(path.relative_to(APP_DIR))
        for path in sorted((APP_DIR / "risk").rglob("*.py"))
        if re.search(r"\bfloat\s*\(", path.read_text(encoding="utf-8"))
    ]
    assert offenders == [], f"money must be Decimal: {offenders}"
