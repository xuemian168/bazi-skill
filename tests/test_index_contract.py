import unittest
from pathlib import Path

from classics import CARD_TIERS, ENABLED_PREFIXES, SCHOOLS
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

    def test_empty_topic_files_parse_cleanly(self):
        cards, errors = load_cards(CLASSICS / "cards")
        self.assertEqual(errors, [])
        self.assertEqual(cards, [])


if __name__ == "__main__":
    unittest.main()
