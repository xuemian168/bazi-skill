import json
import subprocess
import sys
import unittest
from datetime import date
from pathlib import Path

from ganzhi.facts import build_facts
from ganzhi.pillars import day_pillar, hour_pillar
from ganzhi.relations import find_relations
from ganzhi.table import (
    element_relation,
    jiazi,
    load_table,
    nayin,
    season_states,
    ten_god,
    validate_pillar,
)

REPO = Path(__file__).resolve().parents[1]
CLI = REPO / "scripts" / "ganzhi_facts.py"

# Captured once from lunar-javascript (the host project's calendar authority).
LUNAR_DAY_PILLARS = {
    "1900-01-01": "甲戌",
    "1949-10-01": "甲子",
    "1981-01-14": "壬辰",
    "2000-01-01": "戊午",
    "2024-02-29": "癸亥",
    "2026-10-30": "丁丑",
    "2050-12-31": "乙酉",
}
LUNAR_NAYIN_SAMPLE = {
    "甲子": "海中金", "丙子": "涧下水", "戊子": "霹雳火", "甲午": "沙中金",
    "甲辰": "覆灯火", "丙午": "天河水", "壬子": "桑柘木", "癸亥": "大海水",
}


def relation_types(pillars):
    return {(r["type"], tuple(m["char"] for m in r["members"])) for r in find_relations(pillars)}


class TableIntegrityTest(unittest.TestCase):
    def test_sixty_distinct_pillars(self):
        self.assertEqual(len(set(jiazi())), 60)
        self.assertEqual(jiazi()[0], "甲子")
        self.assertEqual(jiazi()[-1], "癸亥")

    def test_nayin_covers_every_pillar_in_consecutive_pairs(self):
        rows = load_table()["nayin"]
        self.assertEqual(len(rows), 30)
        for i, (first, second, name) in enumerate(rows):
            self.assertEqual((first, second), (jiazi()[2 * i], jiazi()[2 * i + 1]))
            self.assertIn(name[-1], load_table()["elements"])

    def test_nayin_matches_lunar_javascript(self):
        for pillar, name in LUNAR_NAYIN_SAMPLE.items():
            self.assertEqual(nayin(pillar), name)

    def test_cycles_are_permutations_and_controls_skip_one(self):
        t = load_table()
        for cycle in (t["generates"], t["controls"]):
            self.assertEqual(sorted(cycle), sorted(t["elements"]))
            self.assertEqual(sorted(cycle.values()), sorted(t["elements"]))
        for element in t["elements"]:
            self.assertEqual(t["controls"][element], t["generates"][t["generates"][element]])

    def test_season_states_follow_the_rule(self):
        t = load_table()
        ruling = {"春": "木", "夏": "火", "秋": "金", "冬": "水", "季月": "土"}
        for season, element in ruling.items():
            gen, ctl = t["generates"], t["controls"]
            produces_me = next(e for e in gen if gen[e] == element)
            controls_me = next(e for e in ctl if ctl[e] == element)
            self.assertEqual(
                t["season_states"][season],
                {element: "旺", gen[element]: "相", produces_me: "休", controls_me: "囚", ctl[element]: "死"},
            )

    def test_folk_scale_follows_polarity(self):
        for row in load_table()["stems"]:
            expected = ("大" if row["yinyang"] == "阳" else "小") + row["element"]
            self.assertEqual(row["folk_scale"], expected)

    def test_branch_main_hidden_stem_matches_branch_element(self):
        stem_element = {row["name"]: row["element"] for row in load_table()["stems"]}
        for row in load_table()["branches"]:
            self.assertEqual(stem_element[row["hidden"][0]], row["element"], row["name"])


class LookupTest(unittest.TestCase):
    def test_element_relation_names_the_actor_first(self):
        self.assertEqual(element_relation("水", "火"), "水 克 火")
        self.assertEqual(element_relation("火", "水"), "水 克 火")
        self.assertEqual(element_relation("木", "火"), "木 生 火")
        self.assertEqual(element_relation("火", "木"), "木 生 火")
        self.assertEqual(element_relation("土", "土"), "土 与 土 同五行")

    def test_ten_gods(self):
        cases = {
            ("甲", "甲"): "比肩", ("甲", "乙"): "劫财", ("甲", "丙"): "食神", ("甲", "丁"): "伤官",
            ("甲", "戊"): "偏财", ("甲", "己"): "正财", ("甲", "庚"): "七杀", ("甲", "辛"): "正官",
            ("甲", "壬"): "偏印", ("甲", "癸"): "正印",
            ("癸", "丙"): "正财", ("癸", "丁"): "偏财", ("癸", "戊"): "正官", ("癸", "己"): "七杀",
        }
        for (dm, other), god in cases.items():
            self.assertEqual(ten_god(dm, other), god, f"{dm}->{other}")

    def test_season_state_of_ji_month(self):
        self.assertEqual(season_states("丑")["season"], "季月")
        self.assertEqual(season_states("子")["states"]["水"], "旺")
        self.assertEqual(season_states("寅")["states"]["土"], "死")

    def test_validate_pillar(self):
        self.assertIsNone(validate_pillar("丙午"))
        self.assertIn("六十甲子", validate_pillar("甲丑"))
        self.assertIn("不是合法干支", validate_pillar("丙"))


class PillarTest(unittest.TestCase):
    def test_day_pillar_matches_lunar_javascript(self):
        for day, pillar in LUNAR_DAY_PILLARS.items():
            self.assertEqual(day_pillar(date.fromisoformat(day)), pillar, day)

    def test_hour_pillar_five_rats(self):
        self.assertEqual(hour_pillar("甲", "子"), "甲子")
        self.assertEqual(hour_pillar("己", "丑"), "乙丑")
        self.assertEqual(hour_pillar("戊", "午"), "戊午")
        self.assertEqual(hour_pillar("丁", "午"), "丙午")  # 2026-10-30 12:00 per lunar-javascript
        self.assertEqual(hour_pillar("癸", "亥"), "癸亥")


class RelationTest(unittest.TestCase):
    def test_pair_relations(self):
        found = relation_types([("日柱", "癸卯"), ("流月", "戊戌")])
        self.assertIn(("天干五合", ("癸", "戊")), found)
        self.assertIn(("六合", ("卯", "戌")), found)

    def test_one_pair_can_carry_several_relations(self):
        found = {kind for kind, _ in relation_types([("年柱", "乙巳"), ("日柱", "甲申")])}
        self.assertEqual(found, {"六合", "相刑", "六破"})

    def test_half_combo_requires_middle_branch(self):
        self.assertIn(("半合", ("申", "子")), relation_types([("a", "庚申"), ("b", "壬子")]))
        kinds = {kind for kind, _ in relation_types([("a", "庚申"), ("b", "壬辰")])}
        self.assertNotIn("半合", kinds)

    def test_full_sets(self):
        found = relation_types([("年柱", "庚申"), ("月柱", "甲子"), ("日柱", "戊辰")])
        self.assertIn(("三合", ("申", "子", "辰")), found)
        found = relation_types([("年柱", "甲寅"), ("月柱", "己巳"), ("日柱", "庚申")])
        self.assertIn(("三刑", ("寅", "巳", "申")), found)

    def test_self_punishment_only_for_listed_branches(self):
        self.assertIn(("自刑", ("午", "午")), relation_types([("a", "丙午"), ("b", "甲午")]))
        self.assertEqual(relation_types([("a", "甲子"), ("b", "丙子")]), set())


class FactsTest(unittest.TestCase):
    def test_absent_element_is_split_by_visibility(self):
        facts = build_facts([("年柱", "庚申"), ("月柱", "己丑"), ("日柱", "癸卯"), ("时柱", "壬子")])
        self.assertEqual(facts["element_count"]["absent_visible"], ["火"])
        self.assertEqual(facts["element_count"]["absent_everywhere"], ["火"])
        facts = build_facts([("年柱", "甲午"), ("月柱", "丙寅"), ("日柱", "甲辰"), ("时柱", "甲戌")])
        self.assertIn("金", facts["element_count"]["absent_visible"])
        self.assertNotIn("金", facts["element_count"]["absent_everywhere"])  # 戌 hides 辛

    def test_day_stem_is_day_master(self):
        facts = build_facts([("年柱", "庚申"), ("月柱", "己丑"), ("日柱", "癸卯")])
        day = next(p for p in facts["pillars"] if p["position"] == "日柱")
        self.assertEqual(day["stem"]["ten_god"], "日主")
        self.assertEqual(facts["day_master"]["folk_scale"], "小水")

    def test_without_day_pillar_no_ten_gods(self):
        facts = build_facts([("流日", "丁丑")])
        self.assertIsNone(facts["day_master"])
        self.assertNotIn("ten_god", facts["pillars"][0]["stem"])


def run_cli(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(CLI), *args], capture_output=True, text=True, cwd=str(REPO))


class CliTest(unittest.TestCase):
    def test_json_output_with_transit_day(self):
        result = run_cli("--chart", "庚申", "己丑", "癸卯", "壬子", "--date", "2026-10-30", "--hour-branch", "午", "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        facts = json.loads(result.stdout)
        positions = {p["position"]: p["pillar"] for p in facts["pillars"]}
        self.assertEqual(positions["流日"], "丁丑")
        self.assertEqual(positions["流时"], "丙午")
        self.assertEqual(facts["contract"], "CONFIRMED BY CODE - DO NOT RECALCULATE, USE AS TRUTH")

    def test_text_output(self):
        result = run_cli("--chart", "庚申", "己丑", "癸卯")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("日主: 癸（阴水，俗称小水", result.stdout)
        self.assertIn("## 月令 丑（季月）", result.stdout)

    def test_invalid_input_exits_two(self):
        for args in (("--chart", "甲丑", "己丑", "癸卯"), ("--date", "2026-13-01"), ("--hour-branch", "午"), ()):
            result = run_cli(*args)
            self.assertEqual(result.returncode, 2, args)
            self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
