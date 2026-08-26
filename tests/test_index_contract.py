import re
import unittest
from pathlib import Path

from classics import CARD_TIERS, ENABLED_PREFIXES, PREFIX_CORPUS, SCHOOLS
from classics.cards import load_cards

REPO = Path(__file__).resolve().parents[1]
CLASSICS = REPO / "references" / "classics"
INDEX = CLASSICS / "index.md"

TOPICS = (
    "10-yueling",
    "20-wangshuai",
    "30-tiaohou",
    "40-shishen",
    "50-geju",
    "60-shensha",
    "70-yunsui",
)


class IndexContractTest(unittest.TestCase):
    def test_index_exists(self):
        self.assertTrue(INDEX.is_file(), f"missing {INDEX}")

    def test_all_topic_files_exist(self):
        for topic in TOPICS:
            path = CLASSICS / "cards" / f"{topic}.md"
            self.assertTrue(path.is_file(), f"missing {path}")

    def test_index_has_three_routing_tables(self):
        text = INDEX.read_text(encoding="utf-8")
        for heading in ("主题 → 卡片文件", "流派 → 主题", "典籍 → 主题"):
            self.assertIn(heading, text, f"index.md missing routing table: {heading}")

    def test_index_documents_every_tier(self):
        text = INDEX.read_text(encoding="utf-8")
        for tier in CARD_TIERS:
            self.assertIn(tier, text, f"index.md missing tier: {tier}")

    def test_index_documents_every_enabled_prefix(self):
        text = INDEX.read_text(encoding="utf-8")
        for prefix in ENABLED_PREFIXES:
            self.assertIn(prefix, text, f"index.md missing prefix: {prefix}")

    def test_index_documents_no_classical_basis(self):
        self.assertIn("no_classical_basis", INDEX.read_text(encoding="utf-8"))

    def test_index_routes_every_school(self):
        text = INDEX.read_text(encoding="utf-8")
        for school in SCHOOLS:
            self.assertIn(school, text, f"index.md missing school: {school}")

    def test_prefix_corpus_mapping_matches_the_documented_table(self):
        # `PREFIX_CORPUS` enforces index.md's 「典籍 → 主题」 table, so the
        # two must not be able to drift apart: the row is the contract and
        # the constant is its enforcement. Parsed out of the table rather
        # than asserted as a substring, so a changed filename in either
        # place fails here.
        documented: dict[str, tuple[str, ...]] = {}
        row = re.compile(
            r"^\|\s*`([A-Z]{3,4})`\s*\|[^|]*\|[^|]*\|\s*(.+?)\s*\|\s*$"
        )
        for line in INDEX.read_text(encoding="utf-8").splitlines():
            match = row.match(line)
            if match:
                documented[match.group(1)] = tuple(
                    path.strip("` ")
                    for path in match.group(2).split("、")
                    if path.strip("` ")
                )
        self.assertEqual(documented, dict(PREFIX_CORPUS))

    def test_every_enabled_prefix_has_a_corpus_binding(self):
        self.assertEqual(sorted(PREFIX_CORPUS), sorted(ENABLED_PREFIXES))

    def test_empty_topic_files_parse_cleanly(self):
        cards, errors = load_cards(CLASSICS / "cards")
        self.assertEqual(errors, [])
        self.assertEqual(cards, [])


if __name__ == "__main__":
    unittest.main()
