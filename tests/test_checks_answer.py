import textwrap
import unittest

from classics.cards import Card, CorpusRef, Rival
from classics.checks_answer import check_answer, parse_answer


def card(card_id: str, tier: str, rivals=()) -> Card:
    return Card(
        id=card_id,
        classic="典籍",
        quote="原文",
        plain="白话",
        premises=("前提",),
        tier=tier,
        schools=("旺衰扶抑",),
        rivals=rivals,
        boundary="边界",
        corpus=CorpusRef("corpus/a.txt", 1, 1),
        source_file="f.md",
        line=1,
    )


LIBRARY = [
    card("DTS-0001", "核心论断", (Rival("ZPZQ-0001", "取用先后不同"),)),
    card("ZPZQ-0001", "核心论断", (Rival("DTS-0001", "取用先后不同"),)),
    card("SMTH-0001", "例证"),
]

GOOD = textwrap.dedent(
    """\
    school: strength-balance-master
    citations: DTS-0001
    citation_fit:
      DTS-0001 — 本造月令与藏干齐备，满足该条前提
    pattern_call: formal_pattern
    """
)


class ParseAnswerTest(unittest.TestCase):
    def test_parses_citations_and_fit(self):
        answer = parse_answer(GOOD)
        self.assertEqual(answer["citations"], ["DTS-0001"])
        self.assertEqual(answer["citation_fit_ids"], ["DTS-0001"])
        self.assertEqual(answer["pattern_call"], "formal_pattern")
        self.assertFalse(answer["is_report"])

    def test_detects_report_input(self):
        answer = parse_answer("依据索引\n| DTS-0001 | 滴天髓 | 原文 | 理由 |\n")
        self.assertTrue(answer["is_report"])

    def test_no_classical_basis_yields_empty_citations(self):
        answer = parse_answer("citations: no_classical_basis\n")
        self.assertEqual(answer["citations"], [])
        self.assertTrue(answer["no_classical_basis"])


class CheckAnswerTest(unittest.TestCase):
    def test_good_answer_passes(self):
        self.assertEqual(check_answer(parse_answer(GOOD), LIBRARY), [])

    def test_no_classical_basis_passes(self):
        text = "school: xiangfa-blind-master\ncitations: no_classical_basis\n"
        self.assertEqual(check_answer(parse_answer(text), LIBRARY), [])

    def test_missing_citations_field_is_reported(self):
        errors = check_answer(parse_answer("school: x\n"), LIBRARY)
        self.assertTrue(any("citations" in e for e in errors), errors)

    def test_unknown_card_id_is_reported(self):
        text = "citations: DTS-9999\ncitation_fit:\n  DTS-9999 — 理由\n"
        errors = check_answer(parse_answer(text), LIBRARY)
        self.assertTrue(any("DTS-9999" in e for e in errors), errors)

    def test_citation_without_fit_is_reported(self):
        text = "citations: DTS-0001\n"
        errors = check_answer(parse_answer(text), LIBRARY)
        self.assertTrue(any("citation_fit" in e for e in errors), errors)

    def test_formal_pattern_on_example_tier_only_is_reported(self):
        text = (
            "citations: SMTH-0001\n"
            "citation_fit:\n  SMTH-0001 — 理由\n"
            "pattern_call: formal_pattern\n"
        )
        errors = check_answer(parse_answer(text), LIBRARY)
        self.assertTrue(any("层级" in e for e in errors), errors)

    def test_rival_pair_without_resolution_is_reported(self):
        text = (
            "citations: DTS-0001, ZPZQ-0001\n"
            "citation_fit:\n  DTS-0001 — 理由\n  ZPZQ-0001 — 理由\n"
        )
        errors = check_answer(parse_answer(text), LIBRARY)
        self.assertTrue(any("rival_resolution" in e for e in errors), errors)

    def test_rival_pair_with_resolution_passes(self):
        text = (
            "citations: DTS-0001, ZPZQ-0001\n"
            "citation_fit:\n  DTS-0001 — 理由\n  ZPZQ-0001 — 理由\n"
            "rival_resolution: ZPZQ-0001 over DTS-0001 — 本任务以定格为目标\n"
        )
        self.assertEqual(check_answer(parse_answer(text), LIBRARY), [])

    def test_report_body_id_missing_from_index_is_reported(self):
        text = textwrap.dedent(
            """\
            正文提到 DTS-0001 与 ZPZQ-0001。

            ## 依据索引

            | 卡片ID | 出处 | 原文 | 适用理由 |
            | DTS-0001 | 滴天髓 | 原文 | 理由 |
            """
        )
        errors = check_answer(parse_answer(text), LIBRARY)
        self.assertTrue(any("依据索引" in e and "ZPZQ-0001" in e for e in errors), errors)

    def test_report_with_complete_index_passes(self):
        text = textwrap.dedent(
            """\
            citations: DTS-0001
            citation_fit:
              DTS-0001 — 理由

            ## 依据索引

            | 卡片ID | 出处 | 原文 | 适用理由 |
            | DTS-0001 | 滴天髓 | 原文 | 理由 |
            """
        )
        self.assertEqual(check_answer(parse_answer(text), LIBRARY), [])


if __name__ == "__main__":
    unittest.main()
