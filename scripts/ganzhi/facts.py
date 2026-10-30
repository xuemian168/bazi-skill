"""Assemble a GanZhi fact packet for prompts, and render it as text."""

from __future__ import annotations

from itertools import combinations

from .relations import Pillar, find_relations
from .table import branches, element_relation, load_table, nayin, season_states, stems, ten_god

CONTRACT = "CONFIRMED BY CODE - DO NOT RECALCULATE, USE AS TRUTH"
NATAL_POSITIONS = ("年柱", "月柱", "日柱", "时柱")


def _stem_facts(name: str, day_stem: str | None, is_day_master: bool) -> dict:
    row = stems()[name]
    facts = {
        "name": name,
        "yinyang": row["yinyang"],
        "element": row["element"],
        "folk_scale": row["folk_scale"],
        "image": row["image"],
    }
    if day_stem:
        facts["ten_god"] = "日主" if is_day_master else ten_god(day_stem, name)
    return facts


def _branch_facts(name: str, day_stem: str | None) -> dict:
    row = branches()[name]
    hidden = []
    for stem in row["hidden"]:
        entry = {"stem": stem, "element": stems()[stem]["element"]}
        if day_stem:
            entry["ten_god"] = ten_god(day_stem, stem)
        hidden.append(entry)
    return {
        "name": name,
        "yinyang": row["yinyang"],
        "element": row["element"],
        "zodiac": row["zodiac"],
        "hidden": hidden,
    }


def _pillar_facts(position: str, pillar: str, day_stem: str | None) -> dict:
    label = nayin(pillar)
    return {
        "position": position,
        "pillar": pillar,
        "nayin": label,
        "nayin_element": label[-1],
        "stem": _stem_facts(pillar[0], day_stem, position == "日柱"),
        "branch": _branch_facts(pillar[1], day_stem),
    }


def _element_count(natal: list[Pillar]) -> dict:
    elements = load_table()["elements"]
    visible = dict.fromkeys(elements, 0)
    hidden = dict.fromkeys(elements, 0)
    for _, gz in natal:
        visible[stems()[gz[0]]["element"]] += 1
        visible[branches()[gz[1]]["element"]] += 1
        for stem in branches()[gz[1]]["hidden"]:
            hidden[stems()[stem]["element"]] += 1
    return {
        "visible": visible,
        "hidden": hidden,
        "absent_visible": [e for e in elements if visible[e] == 0],
        "absent_everywhere": [e for e in elements if visible[e] == 0 and hidden[e] == 0],
        "note": "visible=天干+地支本身五行计数，hidden=藏干计数；计数不等于旺衰，表面不见不等于命局缺。",
    }


def _element_relations(pillars: list[Pillar]) -> list[dict]:
    rows = []
    for (pos_a, gz_a), (pos_b, gz_b) in combinations(pillars, 2):
        sa, sb = stems()[gz_a[0]], stems()[gz_b[0]]
        ba, bb = branches()[gz_a[1]], branches()[gz_b[1]]
        rows.append(
            {
                "a": pos_a,
                "b": pos_b,
                "stem": element_relation(sa["element"], sb["element"]),
                "stem_chars": f"{gz_a[0]}{sa['element']} / {gz_b[0]}{sb['element']}",
                "branch": element_relation(ba["element"], bb["element"]),
                "branch_chars": f"{gz_a[1]}{ba['element']} / {gz_b[1]}{bb['element']}",
            }
        )
    return rows


def _notes(pillars: list[Pillar], relations: list[dict], has_date: bool) -> list[str]:
    t = load_table()
    notes = list(t["notes"])
    if any(pos in ("月柱", "流月") for pos, _ in pillars):
        notes.append(t["season_states_note"])
    if any(r["type"] == "六合" and {m["char"] for m in r["members"]} == {"午", "未"} for r in relations):
        notes.append(t["branch_six_combos_note"])
    if any(r["type"] == "天干相冲" for r in relations):
        notes.append(t["stem_clashes_note"])
    notes.append(t["branch_half_combo_note"])
    if has_date:
        notes.append(t["day_pillar_note"])
    if any(pos == "流时" and gz[1] == "子" for pos, gz in pillars):
        notes.append(t["hour_stem_start_note"])
    return notes


def build_facts(pillars: list[Pillar], date_text: str | None = None) -> dict:
    """`pillars` lists natal positions (年柱..时柱) first, then luck/transit positions."""
    by_position = dict(pillars)
    day_stem = by_position["日柱"][0] if "日柱" in by_position else None
    natal = [(pos, gz) for pos, gz in pillars if pos in NATAL_POSITIONS]
    relations = find_relations(pillars)

    facts: dict = {"contract": CONTRACT, "table_version": load_table()["version"]}
    if date_text:
        facts["date"] = date_text
    facts["day_master"] = _stem_facts(day_stem, None, False) if day_stem else None
    facts["pillars"] = [_pillar_facts(pos, gz, day_stem) for pos, gz in pillars]
    facts["month_command"] = {
        pos: {"branch": by_position[pos][1], **season_states(by_position[pos][1])}
        for pos in ("月柱", "流月")
        if pos in by_position
    }
    facts["element_count"] = _element_count(natal) if natal else None
    facts["element_relations"] = _element_relations(pillars)
    facts["relations"] = relations
    facts["notes"] = _notes(pillars, relations, date_text is not None)
    return facts


def _members(relation: dict) -> str:
    return " + ".join(f"{m['position']}{m['char']}" for m in relation["members"])


def render_text(facts: dict) -> str:
    lines = [f"# 干支事实（{facts['contract']}）", f"table: scripts/ganzhi/table.json v{facts['table_version']}"]
    if "date" in facts:
        lines.append(f"date: {facts['date']}")
    dm = facts["day_master"]
    if dm:
        lines.append(f"日主: {dm['name']}（{dm['yinyang']}{dm['element']}，俗称{dm['folk_scale']}，意象{dm['image']}）")

    lines.append("\n## 各柱")
    for p in facts["pillars"]:
        s, b = p["stem"], p["branch"]
        stem_god = f"，{s['ten_god']}" if "ten_god" in s else ""
        hidden = "、".join(
            h["stem"] + h["element"] + (f"({h['ten_god']})" if "ten_god" in h else "") for h in b["hidden"]
        )
        lines.append(
            f"- {p['position']} {p['pillar']}｜纳音 {p['nayin']}｜"
            f"干 {s['name']}={s['yinyang']}{s['element']}（{s['folk_scale']}）{stem_god}｜"
            f"支 {b['name']}={b['yinyang']}{b['element']}（{b['zodiac']}），藏 {hidden}"
        )

    for pos, cmd in facts["month_command"].items():
        states = "、".join(f"{e}{state}" for e, state in cmd["states"].items())
        title = "月令" if pos == "月柱" else "流月月令"
        lines.append(f"\n## {title} {cmd['branch']}（{cmd['season']}）旺相休囚死\n- {states}")

    count = facts["element_count"]
    if count:
        lines.append("\n## 原局五行计数")
        lines.append("- 干支本身: " + "、".join(f"{e}{n}" for e, n in count["visible"].items()))
        lines.append("- 藏干: " + "、".join(f"{e}{n}" for e, n in count["hidden"].items()))
        lines.append(f"- 干支本身不见: {'、'.join(count['absent_visible']) or '无'}；连藏干也不见: {'、'.join(count['absent_everywhere']) or '无'}")
        lines.append(f"- {count['note']}")

    lines.append("\n## 柱间五行生克")
    for r in facts["element_relations"]:
        lines.append(
            f"- {r['a']} × {r['b']}：干 {r['stem_chars']} → {r['stem']}；支 {r['branch_chars']} → {r['branch']}"
        )

    lines.append("\n## 刑冲合害")
    if not facts["relations"]:
        lines.append("- 无")
    for r in facts["relations"]:
        result = f" → {r['result']}" if r["result"] else ""
        lines.append(f"- [{r['level']}] {r['type']}{result}：{_members(r)}")

    lines.append("\n## 口径说明")
    lines.extend(f"- {note}" for note in facts["notes"])
    return "\n".join(lines)
