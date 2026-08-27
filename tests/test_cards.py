import textwrap
import unittest

from classics.cards import CorpusRef, Rival, parse_cards_text

VALID = textwrap.dedent(
    """\
    # 旺衰

    ### DTS-0001
    - 典籍: 滴天髓·通神论·衰旺
    - 原文: 能知衰旺之真机，其于三命之奥，思过半矣。
    - 白话: 判旺衰不看五行数量，而看得令、得地、得势三者的实际承载。
    - 适用前提:
      - 已知月令
      - 已知日主
    - 层级: 核心论断
    - 流派: 旺衰扶抑, 子平格局
    - 竞合:
      - ZPZQ-0001 — 子平真诠主张先以月令定格
    - 反例边界: 从格、化格不适用此条
    - corpus: corpus/ditiansui.txt#L3-L3
    """
)


class ParseCardsTest(unittest.TestCase):
    def test_parses_all_fields(self):
        cards, errors = parse_cards_text(VALID, "20-wangshuai.md")
        self.assertEqual(errors, [])
        self.assertEqual(len(cards), 1)
        card = cards[0]
        self.assertEqual(card.id, "DTS-0001")
        self.assertEqual(card.classic, "滴天髓·通神论·衰旺")
        self.assertEqual(card.tier, "核心论断")
        self.assertEqual(card.premises, ("已知月令", "已知日主"))
        self.assertEqual(card.schools, ("旺衰扶抑", "子平格局"))
        self.assertEqual(card.rivals, (Rival("ZPZQ-0001", "子平真诠主张先以月令定格"),))
        self.assertEqual(card.corpus, CorpusRef("corpus/ditiansui.txt", 3, 3))
        self.assertEqual(card.source_file, "20-wangshuai.md")
        self.assertEqual(card.line, 3)

    def test_single_line_corpus_ref_without_end(self):
        text = VALID.replace("#L3-L3", "#L7")
        cards, errors = parse_cards_text(text, "f.md")
        self.assertEqual(errors, [])
        self.assertEqual(cards[0].corpus, CorpusRef("corpus/ditiansui.txt", 7, 7))

    def test_missing_required_field_is_reported(self):
        text = VALID.replace("- 反例边界: 从格、化格不适用此条\n", "")
        cards, errors = parse_cards_text(text, "f.md")
        self.assertEqual(cards, [])
        self.assertTrue(any("反例边界" in e for e in errors), errors)

    def test_bad_corpus_ref_is_reported(self):
        text = VALID.replace("corpus/ditiansui.txt#L3-L3", "ditiansui.txt:3")
        cards, errors = parse_cards_text(text, "f.md")
        self.assertEqual(cards, [])
        self.assertTrue(any("corpus" in e for e in errors), errors)

    def test_bad_rival_line_is_reported(self):
        text = VALID.replace("ZPZQ-0001 — 子平真诠主张先以月令定格", "ZPZQ-0001")
        cards, errors = parse_cards_text(text, "f.md")
        self.assertEqual(cards, [])
        self.assertTrue(any("竞合" in e for e in errors), errors)

    def test_rivals_optional(self):
        text = VALID.replace(
            "- 竞合:\n  - ZPZQ-0001 — 子平真诠主张先以月令定格\n", ""
        )
        cards, errors = parse_cards_text(text, "f.md")
        self.assertEqual(errors, [])
        self.assertEqual(cards[0].rivals, ())

    def test_malformed_card_id_heading_is_ignored_not_crashed(self):
        cards, errors = parse_cards_text("### not-an-id\n- 典籍: x\n", "f.md")
        self.assertEqual(cards, [])
        self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
