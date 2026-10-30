"""Day and hour pillars. Year/month pillars depend on 节气 and stay out of scope."""

from __future__ import annotations

from datetime import date

from .table import jiazi, load_table


def day_pillar(day: date) -> str:
    anchor = load_table()["day_pillar_anchor"]
    anchor_day = date.fromisoformat(anchor["date"])
    offset = jiazi().index(anchor["pillar"])
    return jiazi()[(day.toordinal() - anchor_day.toordinal() + offset) % 60]


def hour_pillar(day_stem: str, hour_branch: str) -> str:
    """五鼠遁: the 子-hour stem comes from the day stem, then steps with the branch."""
    table = load_table()
    stem_names = [row["name"] for row in table["stems"]]
    branch_names = [row["name"] for row in table["branches"]]
    start = stem_names.index(table["hour_stem_start"][day_stem])
    steps = branch_names.index(hour_branch)
    return stem_names[(start + steps) % 10] + hour_branch
