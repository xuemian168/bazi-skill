import tempfile
import unittest
from pathlib import Path

from classics.cards import Card, CorpusRef, Rival
from classics.checks_cards import check_cards
from classics.corpus import sha256_of

QUOTE = "能知衰旺之真机，其于三命之奥，思过半矣。"
CORPUS_BODY = "滴天髓\n通神论·衰旺\n能知衰旺之真机其于三命之奥思过半矣\n"

# A second corpus, dedicated to pinning range verification: the RANGE_QUOTE
# text appears only on line 5, not line 3, so a card citing the wrong range
# can only be caught if `_check_quotes` actually searches the cited slice
# rather than the whole file. It is the ZPZQ corpus because a card's ID
# prefix must match the corpus file it cites (`_check_prefix_corpus`), so a
# second corpus needs a second, matching prefix rather than an arbitrary
# filename.
RANGE_QUOTE = "范围验证专用原文片段"
ZPZQ_CORPUS_BODY = (
    "子平真诠\n"
    "论用神\n"
    "能知衰旺之真机其于三命之奥思过半矣\n"
    "第四行内容与原文无关\n"
    "范围验证专用原文片段\n"
)


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


def make_zpzq_card(**overrides) -> Card:
    """A card whose ID prefix and corpus file are both 子平真诠."""
    base = dict(
        id="ZPZQ-0001",
        classic="子平真诠·论用神",
        corpus=CorpusRef("corpus/ziping-zhenquan.txt", 3, 3),
    )
    base.update(overrides)
    return make_card(**base)


class CheckCardsTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        (self.root / "corpus").mkdir()
        corpus_file = self.root / "corpus" / "ditiansui.txt"
        corpus_file.write_text(CORPUS_BODY, encoding="utf-8")
        zpzq_file = self.root / "corpus" / "ziping-zhenquan.txt"
        zpzq_file.write_text(ZPZQ_CORPUS_BODY, encoding="utf-8")
        (self.root / "corpus" / "PROVENANCE.md").write_text(
            f"## corpus/ditiansui.txt\n- sha256: {sha256_of(corpus_file)}\n"
            f"## corpus/ziping-zhenquan.txt\n- sha256: {sha256_of(zpzq_file)}\n",
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

    def test_quote_normalizing_to_empty_is_reported(self):
        errors = check_cards([make_card(quote="……")], self.root)
        self.assertTrue(any("原文正规化后为空" in e for e in errors), errors)

    def test_quote_present_outside_cited_range_is_reported(self):
        errors = check_cards(
            [
                make_zpzq_card(
                    quote=RANGE_QUOTE,
                    corpus=CorpusRef("corpus/ziping-zhenquan.txt", 3, 3),
                )
            ],
            self.root,
        )
        self.assertTrue(any("原文" in e for e in errors), errors)

    def test_quote_present_within_cited_range_passes(self):
        errors = check_cards(
            [
                make_zpzq_card(
                    quote=RANGE_QUOTE,
                    corpus=CorpusRef("corpus/ziping-zhenquan.txt", 5, 5),
                )
            ],
            self.root,
        )
        self.assertEqual(errors, [])

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
        a = make_card(rivals=(Rival("ZPZQ-0001", "对立"),))
        b = make_zpzq_card(rivals=())
        errors = check_cards([a, b], self.root)
        self.assertTrue(any("双向" in e for e in errors), errors)

    def test_bidirectional_rival_passes(self):
        a = make_card(rivals=(Rival("ZPZQ-0001", "对立"),))
        b = make_zpzq_card(rivals=(Rival("DTS-0001", "对立"),))
        self.assertEqual(check_cards([a, b], self.root), [])

    def test_self_referencing_rival_is_reported(self):
        # M2: a card naming its own ID passed mode A, then made itself
        # uncitable in mode B with the incoherent message
        # "DTS-0001 与 DTS-0001 互为竞合". 竞合 means two cards disagree;
        # a card cannot disagree with itself.
        errors = check_cards([make_card(rivals=(Rival("DTS-0001", "自指"),))], self.root)
        self.assertTrue(any("自身" in e for e in errors), errors)
        self.assertFalse(any("双向" in e for e in errors), errors)

    def test_rival_pointing_at_unknown_card_is_reported(self):
        errors = check_cards([make_card(rivals=(Rival("QTBJ-9999", "x"),))], self.root)
        self.assertTrue(any("QTBJ-9999" in e for e in errors), errors)

    def test_prefix_not_matching_its_corpus_file_is_reported(self):
        # I4: nothing used to bind a card's ID prefix to its corpus file, so
        # a DTS card could verify its quote against the 子平真诠 corpus and
        # come back VALID. The quote really is at that location — but the
        # location does not belong to the book the ID (and 典籍) names, so
        # the citation is mis-attributed while looking fully verified.
        errors = check_cards(
            [
                make_card(
                    quote=RANGE_QUOTE,
                    corpus=CorpusRef("corpus/ziping-zhenquan.txt", 5, 5),
                )
            ],
            self.root,
        )
        self.assertTrue(any("前缀与语料不符" in e for e in errors), errors)

    def test_prefix_matching_its_corpus_file_passes(self):
        self.assertEqual(check_cards([make_card(), make_zpzq_card()], self.root), [])

    def test_sha256_mismatch_is_reported(self):
        (self.root / "corpus" / "PROVENANCE.md").write_text(
            "## corpus/ditiansui.txt\n- sha256: deadbeef\n", encoding="utf-8"
        )
        errors = check_cards([make_card()], self.root)
        self.assertTrue(any("sha256" in e for e in errors), errors)


if __name__ == "__main__":
    unittest.main()
