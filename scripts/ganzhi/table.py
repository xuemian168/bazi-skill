"""Load table.json and answer single-fact lookups (stems, branches, NaYin, 生克, 十神)."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

TABLE_PATH = Path(__file__).with_name("table.json")


@lru_cache(maxsize=1)
def load_table() -> dict:
    return json.loads(TABLE_PATH.read_text(encoding="utf-8"))


def stems() -> dict[str, dict]:
    return {row["name"]: row for row in load_table()["stems"]}


def branches() -> dict[str, dict]:
    return {row["name"]: row for row in load_table()["branches"]}


@lru_cache(maxsize=1)
def jiazi() -> tuple[str, ...]:
    """The sixty pillars in order, 甲子 first."""
    stem_names = [row["name"] for row in load_table()["stems"]]
    branch_names = [row["name"] for row in load_table()["branches"]]
    return tuple(stem_names[i % 10] + branch_names[i % 12] for i in range(60))


def nayin(pillar: str) -> str:
    for first, second, name in load_table()["nayin"]:
        if pillar in (first, second):
            return name
    raise KeyError(pillar)


def validate_pillar(pillar: str) -> str | None:
    """Return an error message, or None when `pillar` is one of the sixty."""
    if pillar in jiazi():
        return None
    if len(pillar) == 2 and pillar[0] in stems() and pillar[1] in branches():
        return f"{pillar} 不是六十甲子之一（阳干只配阳支，阴干只配阴支）"
    return f"{pillar} 不是合法干支"


def element_relation(a: str, b: str) -> str:
    """Describe how element `a` relates to `b`, always naming the actor first."""
    table = load_table()
    if a == b:
        return f"{a} 与 {b} 同五行"
    if table["generates"][a] == b:
        return f"{a} 生 {b}"
    if table["generates"][b] == a:
        return f"{b} 生 {a}"
    if table["controls"][a] == b:
        return f"{a} 克 {b}"
    return f"{b} 克 {a}"


def ten_god(day_stem: str, other_stem: str) -> str:
    """十神 of `other_stem` relative to the day master."""
    table = load_table()
    dm, other = stems()[day_stem], stems()[other_stem]
    same_polarity = dm["yinyang"] == other["yinyang"]
    a, b = dm["element"], other["element"]
    if a == b:
        return "比肩" if same_polarity else "劫财"
    if table["generates"][a] == b:
        return "食神" if same_polarity else "伤官"
    if table["controls"][a] == b:
        return "偏财" if same_polarity else "正财"
    if table["controls"][b] == a:
        return "七杀" if same_polarity else "正官"
    return "偏印" if same_polarity else "正印"


def season_states(month_branch: str) -> dict:
    """旺相休囚死 of the five elements under the given month branch."""
    branch = branches()[month_branch]
    key = "季月" if branch["ji_month"] else branch["season"]
    return {"season": key, "states": load_table()["season_states"][key]}
