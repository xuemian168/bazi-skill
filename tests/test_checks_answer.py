import textwrap
import unittest

from classics.cards import Card, CorpusRef, Rival
from classics.checks_answer import NO_BASIS, check_answer, parse_answer


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
        answer = parse_answer("## 依据索引\n| DTS-0001 | 滴天髓 | 原文 | 理由 |\n")
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


class ContinuationTerminationTest(unittest.TestCase):
    """Critical #1: a blank line ends a citation_fit/rival_resolution block,
    and continuation lines must be indented and start with the card id —
    not merely mention one anywhere later in the document."""

    def test_report_index_table_does_not_satisfy_citation_fit_or_rival_resolution(self):
        # The decisive case from the finding: a report's 依据索引 table
        # lists every cited id by construction. Before the fix, an empty
        # citation_fit block and a missing rival_resolution both got
        # silently satisfied by the table rows that followed.
        text = textwrap.dedent(
            """\
            citations: DTS-0001, ZPZQ-0001
            citation_fit:

            ## 依据索引

            | 卡片ID | 出处 | 原文 | 适用理由 |
            | DTS-0001 | 滴天髓 | 原文 | 理由 |
            | ZPZQ-0001 | 子平真诠 | 原文 | 理由 |
            """
        )
        errors = check_answer(parse_answer(text), LIBRARY)
        self.assertTrue(any("citation_fit" in e for e in errors), errors)
        self.assertTrue(any("rival_resolution" in e for e in errors), errors)

    def test_placeholder_rival_resolution_is_not_satisfied_by_later_prose(self):
        text = (
            "citations: DTS-0001, ZPZQ-0001\n"
            "citation_fit:\n  DTS-0001 — 理由\n  ZPZQ-0001 — 理由\n"
            "rival_resolution: 见下表\n"
            "\n"
            "完整说明另见 DTS-0001 与 ZPZQ-0001 相关条目。\n"
        )
        errors = check_answer(parse_answer(text), LIBRARY)
        self.assertTrue(any("rival_resolution" in e for e in errors), errors)


class FieldRecognitionTest(unittest.TestCase):
    """Critical #2: field keys are recognised case-insensitively and when
    indented, by lowercasing the matched key — not by checking it against a
    closed vocabulary. Round 1 tried a closed vocabulary (KNOWN_FIELDS) and
    rejected any other field-shaped line as an error; that rejected every
    real school-prompt Output Shape, which emits many fields this module
    doesn't otherwise care about (scope, core_thesis, confidence, ...).
    Round 2 replaced it with plain normalise-and-ignore: an unrecognised
    key is stored and ignored, exactly as an unindented lowercase one
    always was."""

    def test_capitalised_pattern_call_is_recognised(self):
        text = (
            "citations: SMTH-0001\n"
            "citation_fit:\n  SMTH-0001 — 理由\n"
            "Pattern_call: formal_pattern\n"
        )
        errors = check_answer(parse_answer(text), LIBRARY)
        self.assertTrue(any("层级" in e for e in errors), errors)

    def test_indented_pattern_call_is_recognised(self):
        text = (
            "citations: SMTH-0001\n"
            "citation_fit:\n  SMTH-0001 — 理由\n"
            "  pattern_call: formal_pattern\n"
        )
        errors = check_answer(parse_answer(text), LIBRARY)
        self.assertTrue(any("层级" in e for e in errors), errors)

    def test_unrelated_field_is_stored_and_ignored_not_reported_as_an_error(self):
        text = (
            "citations: DTS-0001\n"
            "citation_fit:\n  DTS-0001 — 理由\n"
            "confidence: medium\n"
        )
        self.assertEqual(check_answer(parse_answer(text), LIBRARY), [])


class NoClassicalBasisTest(unittest.TestCase):
    """Critical #3: no_classical_basis must match the whole value, not
    appear as a substring; and it may not coexist with real citation ids."""

    def test_hint_comment_left_on_the_line_does_not_disable_checks(self):
        text = "citations: DTS-9999   # 或 no_classical_basis\n"
        errors = check_answer(parse_answer(text), LIBRARY)
        self.assertTrue(any("DTS-9999" in e for e in errors), errors)

    def test_no_classical_basis_mixed_with_real_ids_is_reported(self):
        text = "citations: DTS-0001, no_classical_basis\ncitation_fit:\n  DTS-0001 — 理由\n"
        errors = check_answer(parse_answer(text), LIBRARY)
        self.assertTrue(any(NO_BASIS in e for e in errors), errors)

    def test_no_classical_basis_glued_to_cjk_text_is_still_detected_as_mixed(self):
        # Round 3: NO_BASIS_TOKEN used \b, the exact construct Important #5
        # established as unreliable at a CJK/ASCII boundary in this module.
        # \b does not fire between "用" and "n", so a token glued directly
        # onto Chinese prose with no separating space used to silently skip
        # this diagnostic (the citation ids themselves were still checked
        # normally either way — this only loses the supplementary hint).
        text = "citations: DTS-0001且无引用no_classical_basis\ncitation_fit:\n  DTS-0001 — 理由\n"
        errors = check_answer(parse_answer(text), LIBRARY)
        self.assertTrue(any(NO_BASIS in e for e in errors), errors)


class UnspacedCjkCardIdTest(unittest.TestCase):
    """Important #5: \\b does not fire between a CJK character and an ASCII
    letter/digit, so ids embedded in unspaced Chinese prose must still be
    found via lookaround rather than \\b."""

    def test_unspaced_cjk_prose_ids_are_detected_in_report_body(self):
        text = textwrap.dedent(
            """\
            本造依DTS-0001定格，又参SMTH-0001之例。

            ## 依据索引

            | 卡片ID | 出处 | 原文 | 适用理由 |
            | DTS-0001 | 滴天髓 | 原文 | 理由 |
            """
        )
        errors = check_answer(parse_answer(text), LIBRARY)
        self.assertTrue(
            any("依据索引" in e and "SMTH-0001" in e for e in errors), errors
        )


class ReportWindowAnchorTest(unittest.TestCase):
    """Important #6: the 依据索引 anchor must be a heading-shaped line, and
    the last such line wins over an earlier one."""

    def test_prose_mention_without_a_heading_is_not_report_mode(self):
        text = (
            "citations: DTS-0001\n"
            "citation_fit:\n  DTS-0001 — 理由\n"
            "完整出处详见依据索引说明文档。\n"
        )
        answer = parse_answer(text)
        self.assertFalse(answer["is_report"])

    def test_repeated_heading_uses_the_last_occurrence(self):
        text = textwrap.dedent(
            """\
            ## 依据索引

            正文提到 ZPZQ-0001，最终依据见下方表格。

            ## 依据索引

            | 卡片ID | 出处 | 原文 | 适用理由 |
            | DTS-0001 | 滴天髓 | 原文 | 理由 |
            """
        )
        errors = check_answer(parse_answer(text), LIBRARY)
        self.assertTrue(
            any("依据索引" in e and "ZPZQ-0001" in e for e in errors), errors
        )

    def test_trailing_comment_after_heading_marker_is_detected(self):
        # Round 3: the brief's own canonical marker line (task-6-brief.md:24)
        # carries a trailing comment explaining the marker's purpose. The
        # round-1/2 heading regex required the line to end immediately
        # after 依据索引, so an input written exactly as the brief's own
        # documentation shows was not detected as a report at all, silently
        # skipping rule 6 entirely. Round 4 additionally requires the ATX
        # marker (see BareIndexLineIsNotAHeadingTest), so the marker line
        # here carries both the `##` and the trailing comment.
        text = (
            "citations: DTS-0001\n"
            "citation_fit:\n  DTS-0001 — 理由\n"
            "## 依据索引                             # 报告型输入的判别标记\n"
            "| DTS-0001 | 滴天髓 | 原文 | 理由 |\n"
        )
        answer = parse_answer(text)
        self.assertTrue(answer["is_report"])
        self.assertEqual(check_answer(answer, LIBRARY), [])


class DuplicateCitationsFieldTest(unittest.TestCase):
    """Important #7: a repeated citations: key (e.g. from an aggregated
    multi-persona document) must be reported, not silently overwritten."""

    def test_duplicate_citations_field_is_reported(self):
        text = (
            "citations: DTS-9999\n"
            "citation_fit:\n  DTS-9999 — 理由\n"
            "citations: DTS-0001\n"
            "citation_fit:\n  DTS-0001 — 理由\n"
        )
        errors = check_answer(parse_answer(text), LIBRARY)
        self.assertTrue(any("citations" in e and "多次" in e for e in errors), errors)


class InlineCitationFitTest(unittest.TestCase):
    """Minor #9: citation_fit written on a single line (the natural way to
    write one citation) must still be counted, not just the multi-line
    indented form."""

    def test_inline_citation_fit_single_line_is_recognised(self):
        text = "citations: DTS-0001\ncitation_fit: DTS-0001 — 月令齐备\n"
        self.assertEqual(check_answer(parse_answer(text), LIBRARY), [])


# The realistic Output Shape below is what round 1's KNOWN_FIELDS closed
# vocabulary rejected outright: every field here is one the current
# references/school-prompts/*.md Output Shape blocks already require, and
# round 1 flagged seven of them (scope, core_thesis, supporting_evidence,
# counter_evidence, warnings, confidence, recommended_wording) as
# "无法识别的字段". This is the test whose absence let that ship.
REALISTIC_MASTER_OUTPUT = textwrap.dedent(
    """\
    school: ziping-pattern-master
    scope: 全局
    core_thesis: 月令为寅
    pattern_call: pattern_tendency
    supporting_evidence: 略
    counter_evidence: 略
    warnings: 略
    citations: DTS-0001
    citation_fit:
      DTS-0001 — 月令与藏干齐备
    confidence: medium
    recommended_wording: 略
    """
)


class RealisticMasterOutputShapeTest(unittest.TestCase):
    def test_full_school_prompt_output_shape_with_many_fields_passes(self):
        self.assertEqual(
            check_answer(parse_answer(REALISTIC_MASTER_OUTPUT), LIBRARY), []
        )


class ContinuationLineIsNotAFieldTest(unittest.TestCase):
    """Round 2's flagged interaction with round 1's continuation-state
    fix: a citation_fit continuation line is indented and starts with an
    uppercase card id followed by a space and an em dash, not by a colon,
    so FIELD must not match it — verified explicitly rather than reasoned
    about, including a reason string that itself contains a colon
    (adversarial: if FIELD somehow matched past the id, this colon later
    in the line would be the next thing it could latch onto)."""

    def test_indented_citation_fit_continuation_is_not_parsed_as_a_field(self):
        text = (
            "citations: DTS-0001, ZPZQ-0001\n"
            "citation_fit:\n"
            "  DTS-0001 — 例如：月令与藏干需要匹配\n"
            "  ZPZQ-0001 — 日干与月令地支均已确认\n"
            "rival_resolution: ZPZQ-0001 over DTS-0001 — 本任务以定格为目标\n"
        )
        answer = parse_answer(text)
        # If the first continuation line had been mis-parsed as a field,
        # `current` would no longer be "citation_fit" by the time the
        # second continuation line is reached, and ZPZQ-0001 would be
        # silently dropped from citation_fit_ids.
        self.assertEqual(answer["citation_fit_ids"], ["DTS-0001", "ZPZQ-0001"])
        self.assertEqual(check_answer(answer, LIBRARY), [])


class ReportCitationsFieldOptionalTest(unittest.TestCase):
    """Post-Task-11 correction: a report's 依据索引 table already declares
    which cards are cited (id column) and why each applies (本盘适用理由
    column) — that table *is* the report layer's citation mechanism.
    Requiring a separate machine-readable `citations:`/`citation_fit:`
    field pair on top of it conflates the master layer with the report
    layer and puts master-facing scaffolding into a reader-facing
    artefact. For report-type input (`is_report` true) those two fields'
    *presence* becomes optional. Everything else must still catch a
    report exactly as it would catch a master output with the same
    content — is_report must not become a way to bypass a check."""

    def test_report_without_citations_field_passes(self):
        text = textwrap.dedent(
            """\
            正文提到 DTS-0001。

            ## 依据索引

            | 卡片ID | 出处 | 原文 | 适用理由 |
            | DTS-0001 | 滴天髓 | 原文 | 理由 |
            """
        )
        self.assertEqual(check_answer(parse_answer(text), LIBRARY), [])

    def test_report_without_citations_field_still_catches_body_index_mismatch(self):
        # The guard that must survive: omitting citations: must not also
        # blind rule 6 (body id must appear in the index).
        text = textwrap.dedent(
            """\
            正文提到 DTS-0001 与 ZPZQ-0001。

            ## 依据索引

            | 卡片ID | 出处 | 原文 | 适用理由 |
            | DTS-0001 | 滴天髓 | 原文 | 理由 |
            """
        )
        errors = check_answer(parse_answer(text), LIBRARY)
        self.assertTrue(
            any("依据索引" in e and "ZPZQ-0001" in e for e in errors), errors
        )
        self.assertFalse(
            any("citations" in e and "缺少" in e for e in errors), errors
        )

    def test_report_with_malformed_citations_field_still_fails(self):
        # citations:/citation_fit: are optional, not exempt: supplied and
        # wrong must still be caught, not silently skipped because the
        # input is a report.
        text = textwrap.dedent(
            """\
            citations: DTS-9999

            正文提到 DTS-0001。

            ## 依据索引

            | 卡片ID | 出处 | 原文 | 适用理由 |
            | DTS-0001 | 滴天髓 | 原文 | 理由 |
            """
        )
        errors = check_answer(parse_answer(text), LIBRARY)
        self.assertTrue(any("DTS-9999" in e for e in errors), errors)

    def test_report_without_citations_field_still_requires_rival_resolution(self):
        # Adjudication between competing cards must stay visible in the
        # report itself, not only in the referee's working notes — this
        # must not become reachable by simply not writing citations:.
        text = textwrap.dedent(
            """\
            正文同时依 DTS-0001 与 ZPZQ-0001 定格。

            ## 依据索引

            | 卡片ID | 出处 | 原文 | 适用理由 |
            | DTS-0001 | 滴天髓 | 原文 | 理由 |
            | ZPZQ-0001 | 子平真诠 | 原文 | 理由 |
            """
        )
        errors = check_answer(parse_answer(text), LIBRARY)
        self.assertTrue(any("rival_resolution" in e for e in errors), errors)

    def test_non_report_without_citations_field_is_still_rejected(self):
        # The non-report path (master/referee output) is untouched: no
        # 依据索引 heading means citations: is still mandatory.
        errors = check_answer(parse_answer("school: x\n"), LIBRARY)
        self.assertTrue(
            any("citations" in e and "缺少" in e for e in errors), errors
        )


class ReportFormalPatternTierEvidenceTest(unittest.TestCase):
    """Round 2 correction: the pattern_call tier gate (rule 4) read only the
    `citations` field-derived list, the same narrow evidence source the
    rival-pair guard (rule 5) used before it was widened to also draw on
    `index_ids` for report-type input. Before the citations-field
    relaxation this was invisible, because `citations:` was mandatory so
    rule 4's evidence source was always populated whenever the input was
    otherwise valid. After the relaxation, a fully correct report that
    declares its 核心论断-tier support solely through the 依据索引 table —
    with no `citations:` field at all — was falsely rejected by a stray
    `pattern_call: formal_pattern` line, because `citations` was always
    empty for such a report and `any(... for c in citations ...)` over an
    empty list is always False."""

    def test_report_formal_pattern_satisfied_via_index_only(self):
        text = textwrap.dedent(
            """\
            pattern_call: formal_pattern
            正文提到 DTS-0001。

            ## 依据索引

            | 卡片ID | 出处 | 原文 | 适用理由 |
            | DTS-0001 | 滴天髓 | 能知衰旺之真机 | 月令齐备 |
            """
        )
        self.assertEqual(check_answer(parse_answer(text), LIBRARY), [])

    def test_report_formal_pattern_still_fails_without_strong_tier_evidence_anywhere(self):
        # Regression guard: widening the evidence source to include the
        # index must not turn rule 4 into a check that never fires for
        # reports. SMTH-0001 is 例证 tier (not 核心论断/操作规则), cited
        # only through the index, with no citations: field either.
        text = textwrap.dedent(
            """\
            pattern_call: formal_pattern
            正文提到 SMTH-0001。

            ## 依据索引

            | 卡片ID | 出处 | 原文 | 适用理由 |
            | SMTH-0001 | 某书 | 原文 | 理由 |
            """
        )
        errors = check_answer(parse_answer(text), LIBRARY)
        self.assertTrue(any("层级" in e for e in errors), errors)


class BareIndexLineIsNotAHeadingTest(unittest.TestCase):
    """Round 4 / I2: the report relaxation turned a false `is_report` from a
    safe over-application of rule 6 into a citations bypass — a report no
    longer needs a `citations:` field. The bare, unmarked line `依据索引`
    was accepted as the section anchor, and no file under `references/`
    documents that form; `report-generation.md` documents `## 依据索引`.
    So any answer containing a lone `依据索引` line — including one that
    merely reproduces the report template inside a code fence — silently
    lost the mandatory-citations rule."""

    def test_bare_unmarked_line_does_not_make_an_answer_a_report(self):
        text = "正文说了一堆结构性判断。\n依据索引\n"
        answer = parse_answer(text)
        self.assertFalse(answer["is_report"])
        errors = check_answer(answer, LIBRARY)
        self.assertTrue(any("citations" in e and "缺少" in e for e in errors), errors)

    def test_every_atx_level_is_still_accepted(self):
        for marker in ("#", "##", "###", "####", "#####", "######"):
            with self.subTest(marker=marker):
                answer = parse_answer(
                    f"{marker} 依据索引\n| DTS-0001 | 滴天髓 | 原文 | 理由 |\n"
                )
                self.assertTrue(answer["is_report"])

    def test_last_atx_heading_still_wins_over_an_earlier_one(self):
        # The last-match-wins behaviour is an earlier fix and must survive.
        text = textwrap.dedent(
            """\
            ## 依据索引

            正文提到 ZPZQ-0001，最终依据见下方表格。

            ## 依据索引

            | DTS-0001 | 滴天髓 | 原文 | 理由 |
            """
        )
        errors = check_answer(parse_answer(text), LIBRARY)
        self.assertTrue(
            any("依据索引" in e and "ZPZQ-0001" in e for e in errors), errors
        )


class DecoratedPatternCallTest(unittest.TestCase):
    """Round 4 / I3: the tier gate compared `pattern_call` for exact
    equality, so annotating the enum value — `formal_pattern（正官格）`, a
    natural thing for a model to write — silently disabled the only
    machine-enforced form of spec 8.1's hard rule. `pattern_call` is a
    closed enum (ziping-pattern-master.md:59), so matching its leading
    token is safe; the closed-vocabulary objection that applies to field
    *keys* does not apply to this value."""

    EXAMPLE_TIER_ONLY = (
        "citations: SMTH-0001\n"
        "citation_fit:\n  SMTH-0001 — 理由\n"
        "pattern_call: {}\n"
    )

    def test_decorated_formal_pattern_still_triggers_the_tier_gate(self):
        for value in (
            "formal_pattern（正官格）",
            "formal_pattern (正官格)",
            "formal_pattern —— 正官格",
            "formal_pattern | pattern_tendency | no_stable_pattern",
            "formal_pattern  # 已确认",
        ):
            with self.subTest(value=value):
                errors = check_answer(
                    parse_answer(self.EXAMPLE_TIER_ONLY.format(value)), LIBRARY
                )
                self.assertTrue(any("层级" in e for e in errors), errors)

    def test_other_enum_values_do_not_trigger_the_tier_gate(self):
        for value in (
            "pattern_tendency",
            "no_stable_pattern",
            "evidence_gap",
            "pattern_tendency（近正官）",
        ):
            with self.subTest(value=value):
                self.assertEqual(
                    check_answer(
                        parse_answer(self.EXAMPLE_TIER_ONLY.format(value)), LIBRARY
                    ),
                    [],
                )

    def test_a_longer_token_starting_with_the_enum_value_is_not_matched(self):
        # The leading token must be the whole token, not a prefix: a value
        # that merely starts with the enum text is a different value.
        self.assertEqual(
            check_answer(
                parse_answer(self.EXAMPLE_TIER_ONLY.format("formal_pattern_v2")),
                LIBRARY,
            ),
            [],
        )

    def test_strong_tier_support_still_satisfies_a_decorated_value(self):
        text = (
            "citations: DTS-0001\n"
            "citation_fit:\n  DTS-0001 — 理由\n"
            "pattern_call: formal_pattern（正官格）\n"
        )
        self.assertEqual(check_answer(parse_answer(text), LIBRARY), [])


class EmptyReportIndexTest(unittest.TestCase):
    """Round 4 / I6b: the relaxation's premise is that the 依据索引 table
    *is* the report layer's citation declaration. A report whose table
    names no card at all therefore declares nothing, yet used to pass —
    the same silence that is rejected outright for a master output. This
    restores the relaxation's own premise without pretending to implement
    spec 8.3's unimplementable body-claim coverage check (see plan
    deviation E)."""

    EMPTY_INDEX = textwrap.dedent(
        """\
        本造月令为寅，日主得令，格取正官，用神为财。

        ## 依据索引

        | 卡片ID | 典籍出处 | 原文 | 本盘适用理由 |
        |---|---|---|---|
        """
    )

    def test_empty_index_without_any_declaration_is_reported(self):
        errors = check_answer(parse_answer(self.EMPTY_INDEX), LIBRARY)
        self.assertTrue(any("依据索引" in e and "未列出" in e for e in errors), errors)

    def test_empty_index_with_a_citations_field_passes(self):
        text = f"citations: {NO_BASIS}\n\n{self.EMPTY_INDEX}"
        self.assertEqual(check_answer(parse_answer(text), LIBRARY), [])

    def test_empty_index_with_an_explicit_no_basis_statement_passes(self):
        text = self.EMPTY_INDEX.replace(
            "本造月令为寅，日主得令，格取正官，用神为财。",
            "本造月令为寅，日主得令。该部分为象法推演，无典籍条文支撑。",
        )
        self.assertEqual(check_answer(parse_answer(text), LIBRARY), [])

    def test_non_empty_index_needs_no_extra_declaration(self):
        text = self.EMPTY_INDEX + "| DTS-0001 | 滴天髓 | 原文 | 理由 |\n"
        self.assertEqual(check_answer(parse_answer(text), LIBRARY), [])


class NoBasisWithTemplateCommentTest(unittest.TestCase):
    """Round 4 / M3: every master template ships an inline hint comment on
    the `citations:` line, and three masters are told to always write
    `no_classical_basis`. The exact-match test ran against the raw value
    including that comment, so the shipped template's own output was
    rejected with `citations 为空` — a message that is untrue of the
    input. The trailing comment is not part of the value; the equality
    test itself stays exact."""

    def test_template_comment_after_no_classical_basis_is_accepted(self):
        text = f"citations: {NO_BASIS}   # 或逗号分隔的卡片 ID\n"
        answer = parse_answer(text)
        self.assertTrue(answer["no_classical_basis"])
        self.assertEqual(check_answer(answer, LIBRARY), [])

    def test_shipped_master_template_comment_is_accepted(self):
        text = (
            f"citations: {NO_BASIS}      "
            f"# 必填。逗号分隔的卡片 ID，如 <卡片ID>；确无可引则写 {NO_BASIS}\n"
        )
        self.assertEqual(check_answer(parse_answer(text), LIBRARY), [])

    def test_a_value_that_merely_contains_the_token_is_still_rejected(self):
        # Exactness is unchanged: only a trailing comment is stripped.
        errors = check_answer(parse_answer(f"citations: 无 {NO_BASIS}\n"), LIBRARY)
        self.assertTrue(any("为空" in e for e in errors), errors)

    def test_hint_comment_still_does_not_hide_a_real_id(self):
        errors = check_answer(
            parse_answer(f"citations: DTS-9999   # 或 {NO_BASIS}\n"), LIBRARY
        )
        self.assertTrue(any("DTS-9999" in e for e in errors), errors)


if __name__ == "__main__":
    unittest.main()
