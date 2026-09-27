"""Static guards for the coding standards that a unit test cannot otherwise catch."""

import ast
import re
from pathlib import Path

APP_DIR = Path(__file__).resolve().parents[1] / "app"
CLOCK_FILE = APP_DIR / "core" / "clock.py"

_NOW_ATTRS = {"now", "utcnow", "today"}
_TIME_MODULE_ATTRS = {"time", "time_ns", "monotonic", "perf_counter"}
_TIME_IMPORT_NAMES = {"time", "time_ns"}


def _reads_wall_clock(source: str) -> bool:
    """AST-based wall-clock detector: survives import aliasing that a regex can't see through."""
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if node.func.attr in _NOW_ATTRS:
                return True
            if (
                node.func.attr in _TIME_MODULE_ATTRS
                and isinstance(node.func.value, ast.Name)
                and node.func.value.id == "time"
            ):
                return True
        if (
            isinstance(node, ast.ImportFrom)
            and node.module == "time"
            and any(alias.name in _TIME_IMPORT_NAMES for alias in node.names)
        ):
            return True
    return False


def _sources() -> list[Path]:
    return sorted(APP_DIR.rglob("*.py"))


def test_guard_sees_the_app_tree() -> None:
    assert CLOCK_FILE in _sources()


def test_only_clock_reads_the_wall_clock() -> None:
    offenders = [
        str(path.relative_to(APP_DIR))
        for path in _sources()
        if path != CLOCK_FILE and _reads_wall_clock(path.read_text(encoding="utf-8"))
    ]
    assert offenders == [], f"use app.core.clock.now() instead: {offenders}"


def test_wall_clock_detector_catches_aliases() -> None:
    flagged = [
        "import datetime as dt\ndt.datetime.now()",
        "from datetime import datetime as DT\nDT.now()",
        "from time import time\ntime()",
        "import time\ntime.time()",
        "from datetime import date\ndate.today()",
    ]
    for source in flagged:
        assert _reads_wall_clock(source), f"should flag: {source!r}"
    assert not _reads_wall_clock("x = 1\nprint(x)")


def test_no_float_money_in_risk() -> None:
    offenders = [
        str(path.relative_to(APP_DIR))
        for path in sorted((APP_DIR / "risk").rglob("*.py"))
        if re.search(r"\bfloat\s*\(", path.read_text(encoding="utf-8"))
    ]
    assert offenders == [], f"money must be Decimal: {offenders}"
