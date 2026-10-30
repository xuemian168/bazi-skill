"""Detect stem/branch interactions among labelled pillars (natal + luck + transit)."""

from __future__ import annotations

from itertools import combinations

from .table import load_table

Pillar = tuple[str, str]  # (position label, 干支)


def _pair_index(pairs: list[str]) -> set[frozenset[str]]:
    return {frozenset(pair) for pair in pairs}


def _member(position: str, char: str) -> dict:
    return {"position": position, "char": char}


def _pair_relations() -> list[tuple[str, str, dict[frozenset[str], str | None]]]:
    """(level, type, {pair: result}) for every two-member relation in the table."""
    t = load_table()
    combos = {frozenset(row["pair"]): row["result"] for row in t["stem_combos"]}
    six = {frozenset(row["pair"]): row["result"] for row in t["branch_six_combos"]}
    half: dict[frozenset[str], str | None] = {}
    for row in t["branch_three_combos"]:
        first, middle, last = row["set"]
        half[frozenset((first, middle))] = row["result"]
        half[frozenset((middle, last))] = row["result"]
    punish: dict[frozenset[str], str | None] = {}
    for row in t["branch_punishments"]:
        for a, b in combinations(row["set"], 2):
            punish[frozenset((a, b))] = row["name"]
    return [
        ("干", "天干五合", combos),
        ("干", "天干相冲", dict.fromkeys(_pair_index(t["stem_clashes"]))),
        ("支", "六合", six),
        ("支", "半合", half),
        ("支", "六冲", dict.fromkeys(_pair_index(t["branch_clashes"]))),
        ("支", "相刑", punish),
        ("支", "六害", dict.fromkeys(_pair_index(t["branch_harms"]))),
        ("支", "六破", dict.fromkeys(_pair_index(t["branch_breaks"]))),
    ]


def pair_relations(pillars: list[Pillar]) -> list[dict]:
    self_punish = set(load_table()["branch_self_punishments"])
    found = []
    for (pos_a, gz_a), (pos_b, gz_b) in combinations(pillars, 2):
        for level, kind, table in _pair_relations():
            idx = 0 if level == "干" else 1
            a, b = gz_a[idx], gz_b[idx]
            key = frozenset((a, b))
            if a != b and key in table:
                found.append(
                    {
                        "level": level,
                        "type": kind,
                        "members": [_member(pos_a, a), _member(pos_b, b)],
                        "result": table[key],
                    }
                )
        if gz_a[1] == gz_b[1] and gz_a[1] in self_punish:
            found.append(
                {
                    "level": "支",
                    "type": "自刑",
                    "members": [_member(pos_a, gz_a[1]), _member(pos_b, gz_b[1])],
                    "result": None,
                }
            )
    return found


def full_set_relations(pillars: list[Pillar]) -> list[dict]:
    """三合 / 三会 / 三刑 whose every member branch appears somewhere in `pillars`."""
    t = load_table()
    groups = [("三合", row["set"], row["result"]) for row in t["branch_three_combos"]]
    groups += [("三会", row["set"], row["result"]) for row in t["branch_three_meetings"]]
    groups += [
        ("三刑", row["set"], row["name"]) for row in t["branch_punishments"] if len(row["set"]) == 3
    ]
    found = []
    for kind, members, result in groups:
        holders = {char: [pos for pos, gz in pillars if gz[1] == char] for char in members}
        if all(holders.values()):
            found.append(
                {
                    "level": "支",
                    "type": kind,
                    "members": [
                        _member(pos, char) for char in members for pos in holders[char]
                    ],
                    "result": result,
                }
            )
    return found


def find_relations(pillars: list[Pillar]) -> list[dict]:
    return pair_relations(pillars) + full_set_relations(pillars)
