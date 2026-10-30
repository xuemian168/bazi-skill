"""Keep the human-readable tables in bazi-domain-reference.md in step with table.json."""

import re
import unittest
from pathlib import Path

from ganzhi.table import load_table

REPO = Path(__file__).resolve().parents[1]
DOC = (REPO / "references" / "bazi-domain-reference.md").read_text(encoding="utf-8")
ELEMENT_EN = {"wood": "木", "fire": "火", "earth": "土", "metal": "金", "water": "水"}
POLARITY_EN = {"yang": "阳", "yin": "阴"}


def table_rows(header_start: str) -> list[list[str]]:
    lines = DOC[DOC.index(header_start):].splitlines()
    rows = []
    for line in lines[2:]:
        if not line.startswith("|"):
            break
        rows.append([cell.strip() for cell in line.strip("|").split("|")])
    return rows


def line_after(label: str) -> str:
    return re.search(rf"^{re.escape(label)}(.*)$", DOC, re.MULTILINE).group(1)


class DomainReferenceSyncTest(unittest.TestCase):
    def test_stem_table(self):
        rows = table_rows("| Stem |")
        expected = [[r["name"], r["yinyang"], r["element"]] for r in load_table()["stems"]]
        self.assertEqual([[s, POLARITY_EN[p], ELEMENT_EN[e]] for s, p, e in rows], expected)

    def test_branch_table(self):
        rows = table_rows("| Branch |")
        expected = [[r["name"], r["element"]] for r in load_table()["branches"]]
        self.assertEqual([[b, ELEMENT_EN[e]] for b, e, _ in rows], expected)

    def test_hidden_stem_table(self):
        rows = table_rows("| Branch | Main |")
        expected = [[r["name"], r["hidden"]] for r in load_table()["branches"]]
        self.assertEqual([[row[0], [c for c in row[1:] if c]] for row in rows], expected)

    def test_cycles(self):
        t = load_table()
        for label, key in (("Generating cycle: ", "generates"), ("Controlling cycle: ", "controls")):
            chain = [ELEMENT_EN[w] for w in re.findall(r"[a-z]+", line_after(label))]
            self.assertEqual(len(chain), 6)
            for a, b in zip(chain, chain[1:]):
                self.assertEqual(t[key][a], b, label)

    def test_branch_relation_lists(self):
        t = load_table()
        pairs = {
            "- Six clashes: ": set(t["branch_clashes"]),
            "- Six combinations: ": {row["pair"] for row in t["branch_six_combos"]},
            "- Harms: ": set(t["branch_harms"]),
        }
        for label, expected in pairs.items():
            listed = {frozenset(p) for p in re.findall(r"[子丑寅卯辰巳午未申酉戌亥]{2}", line_after(label))}
            self.assertEqual(listed, {frozenset(p) for p in expected}, label)
        sets = {
            "- Three combinations: ": {row["set"] for row in t["branch_three_combos"]},
            "- Three meetings: ": {row["set"] for row in t["branch_three_meetings"]},
        }
        for label, expected in sets.items():
            self.assertEqual(set(re.findall(r"[子丑寅卯辰巳午未申酉戌亥]{3}", line_after(label))), expected, label)


if __name__ == "__main__":
    unittest.main()
