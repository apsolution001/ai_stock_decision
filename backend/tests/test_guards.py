"""Static guards for the coding standards that a unit test cannot otherwise catch."""

import re
from pathlib import Path

APP_DIR = Path(__file__).resolve().parents[1] / "app"
CLOCK_FILE = APP_DIR / "core" / "clock.py"
WALL_CLOCK = re.compile(r"\b(datetime\.now|datetime\.utcnow|date\.today|time\.time)\s*\(")


def _sources() -> list[Path]:
    return sorted(APP_DIR.rglob("*.py"))


def test_guard_sees_the_app_tree() -> None:
    assert CLOCK_FILE in _sources()


def test_only_clock_reads_the_wall_clock() -> None:
    offenders = [
        str(path.relative_to(APP_DIR))
        for path in _sources()
        if path != CLOCK_FILE and WALL_CLOCK.search(path.read_text(encoding="utf-8"))
    ]
    assert offenders == [], f"use app.core.clock.now() instead: {offenders}"


def test_no_float_money_in_risk() -> None:
    offenders = [
        str(path.relative_to(APP_DIR))
        for path in sorted((APP_DIR / "risk").rglob("*.py"))
        if re.search(r"\bfloat\s*\(", path.read_text(encoding="utf-8"))
    ]
    assert offenders == [], f"money must be Decimal: {offenders}"
