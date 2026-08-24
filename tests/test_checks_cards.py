import tempfile
import unittest
from pathlib import Path

from classics.cards import Card, CorpusRef, Rival
from classics.checks_cards import check_cards
from classics.corpus import sha256_of

QUOTE = "能知衰旺之真机，其于三命之奥，思过半矣。"
CORPUS_BODY = "滴天髓\n通神论·衰旺\n能知衰旺之真机其于三命之奥思过半矣\n"


def make_card(**overrides) -> Card:
    base = dict(
        id="DTS-0001",
        classic="滴天髓·通神论·衰旺",
        quote=QUOTE,
        plain="判旺衰看得令得地得势的实际承载。",
        premises=("已知月令",),
        tier="核心论断",
        schools=("旺衰扶抑",),
        rivals=(),
        boundary="从格、化格不适用",
        corpus=CorpusRef("corpus/ditiansui.txt", 3, 3),
        source_file="20-wangshuai.md",
        line=3,
    )
    base.update(overrides)
    return Card(**base)


class CheckCardsTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        (self.root / "corpus").mkdir()
        corpus_file = self.root / "corpus" / "ditiansui.txt"
        corpus_file.write_text(CORPUS_BODY, encoding="utf-8")
        (self.root / "corpus" / "PROVENANCE.md").write_text(
            f"## corpus/ditiansui.txt\n- sha256: {sha256_of(corpus_file)}\n",
            encoding="utf-8",
        )

    def tearDown(self):
        self._tmp.cleanup()

    def test_valid_card_passes(self):
        self.assertEqual(check_cards([make_card()], self.root), [])

    def test_duplicate_id_is_reported(self):
        errors = check_cards([make_card(), make_card()], self.root)
        self.assertTrue(any("重复" in e for e in errors), errors)

    def test_reserved_prefix_is_rejected(self):
        errors = check_cards([make_card(id="YHZP-0001")], self.root)
        self.assertTrue(any("尚未启用" in e for e in errors), errors)

    def test_unknown_prefix_is_rejected(self):
        errors = check_cards([make_card(id="ZZZ-0001")], self.root)
        self.assertTrue(any("前缀" in e for e in errors), errors)

    def test_bad_tier_is_reported(self):
        errors = check_cards([make_card(tier="很重要")], self.root)
        self.assertTrue(any("层级" in e for e in errors), errors)

    def test_bad_school_is_reported(self):
        errors = check_cards([make_card(schools=("玄学派",))], self.root)
        self.assertTrue(any("流派" in e for e in errors), errors)

    def test_quote_absent_from_corpus_is_reported(self):
        errors = check_cards([make_card(quote="此句原文不存在于语料")], self.root)
        self.assertTrue(any("原文" in e for e in errors), errors)

    def test_corpus_line_out_of_range_is_reported(self):
        errors = check_cards(
            [make_card(corpus=CorpusRef("corpus/ditiansui.txt", 99, 99))], self.root
        )
        self.assertTrue(any("行号" in e for e in errors), errors)

    def test_missing_corpus_file_is_reported(self):
        errors = check_cards(
            [make_card(corpus=CorpusRef("corpus/nope.txt", 1, 1))], self.root
        )
        self.assertTrue(any("nope.txt" in e for e in errors), errors)

    def test_one_way_rival_is_reported(self):
        a = make_card(id="DTS-0001", rivals=(Rival("ZPZQ-0001", "对立"),))
        b = make_card(id="ZPZQ-0001", rivals=())
        errors = check_cards([a, b], self.root)
        self.assertTrue(any("双向" in e for e in errors), errors)

    def test_bidirectional_rival_passes(self):
        a = make_card(id="DTS-0001", rivals=(Rival("ZPZQ-0001", "对立"),))
        b = make_card(id="ZPZQ-0001", rivals=(Rival("DTS-0001", "对立"),))
        self.assertEqual(check_cards([a, b], self.root), [])

    def test_rival_pointing_at_unknown_card_is_reported(self):
        errors = check_cards([make_card(rivals=(Rival("QTBJ-9999", "x"),))], self.root)
        self.assertTrue(any("QTBJ-9999" in e for e in errors), errors)

    def test_sha256_mismatch_is_reported(self):
        (self.root / "corpus" / "PROVENANCE.md").write_text(
            "## corpus/ditiansui.txt\n- sha256: deadbeef\n", encoding="utf-8"
        )
        errors = check_cards([make_card()], self.root)
        self.assertTrue(any("sha256" in e for e in errors), errors)


if __name__ == "__main__":
    unittest.main()
