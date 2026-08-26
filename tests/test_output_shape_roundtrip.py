"""Behavioural round-trip between the shipped prompt/report docs and the parser.

Every other prompt-contract test in this suite is `assertIn("<a string the
same author wrote>", text)`. Those guard against deletion and nothing else:
they cannot detect that a format the documentation *instructs* is a format
the parser *rejects*. That is exactly how the `citation_fit` line-start
instruction shipped across nine files with a fully green suite.

So these tests do not look for strings. They take each shipped
`## Output Shape` block, fill it the way the block's own inline comments
instruct, and assert that the real `parse_answer` / `check_answer` accept
the result. The indentation of a `citation_fit` entry in particular is read
out of the file's own instruction rather than hard-coded (see `fit_entry`),
so a file that tells authors to put the ID at column 0 renders a column-0
line here — and this round-trip then fails.
"""

from __future__ import annotations

import unittest
from pathlib import Path

from classics.cards import Card, CorpusRef
from classics.checks_answer import CARD_ID, NO_BASIS, check_answer, parse_answer

REPO = Path(__file__).resolve().parents[1]
PROMPTS = REPO / "references" / "school-prompts"
REPORT = REPO / "references" / "report-generation.md"

FENCE = "```"
CITED_ID = "DTS-0001"


def card(card_id: str, tier: str = "核心论断") -> Card:
    return Card(
        id=card_id,
        classic="典籍",
        quote="原文",
        plain="白话",
        premises=("前提",),
        tier=tier,
        schools=("旺衰扶抑",),
        rivals=(),
        boundary="边界",
        corpus=CorpusRef("corpus/a.txt", 1, 1),
        source_file="f.md",
        line=1,
    )


LIBRARY = [card(CITED_ID)]


def fenced_block_after(text: str, heading_test) -> str | None:
    """The first fenced block following the first line matching `heading_test`."""
    lines = text.splitlines()
    start = next((i for i, line in enumerate(lines) if heading_test(line)), None)
    if start is None:
        return None
    opened = next(
        (i for i in range(start + 1, len(lines)) if lines[i].startswith(FENCE)), None
    )
    if opened is None:
        return None
    closed = next(
        (i for i in range(opened + 1, len(lines)) if lines[i].startswith(FENCE)), None
    )
    if closed is None:
        return None
    return "\n".join(lines[opened + 1 : closed])


def output_shape(text: str) -> str | None:
    return fenced_block_after(text, lambda line: line.strip() == "## Output Shape")


def split_comment(rest: str) -> tuple[str, str]:
    """Split a template line's remainder into (value, inline comment)."""
    value, marker, comment = rest.partition("#")
    return value.strip(), comment.strip() if marker else ""


def fit_entry(instruction: str, card_id: str) -> str:
    """Render one `citation_fit` entry exactly as the file's own comment says.

    The comment is the contract an author (human or model) follows, so the
    indentation is derived from it rather than assumed. A file whose
    instruction does not call for indentation renders the ID at column 0 —
    which `checks_answer.CONTINUATION` does not accept, so the round-trip
    below fails and names the file. That is the intended behaviour: the
    instruction and the parser must agree, and this is what checks it.
    """
    indent = "  " if "缩进" in instruction else ""
    return f"{indent}{card_id} — 月令与藏干齐备，符合该条适用前提"


def fill(
    block: str,
    citations_value: str,
    keep_citations_comment: bool,
    enum_choice: str | None = None,
) -> str:
    """Fill an Output Shape template the way its own comments instruct.

    `enum_choice` picks which alternative of a `a | b | c` enum value the
    fill selects, when that alternative is offered; otherwise the first
    alternative is taken. It exists so the no-citation fill can honour
    ziping-pattern-master's own Method Checklist 3b, which requires
    `formal_pattern` to be downgraded to `pattern_tendency` when no
    核心论断/操作规则 card supports it.
    """
    filled: list[str] = []
    for raw in block.splitlines():
        key, marker, rest = raw.partition(":")
        if not marker:
            filled.append(raw)
            continue
        key = key.strip()
        value, comment = split_comment(rest)

        if key == "citations":
            line = f"citations: {citations_value}"
            if keep_citations_comment and comment:
                line = f"{line}   # {comment}"
            filled.append(line)
        elif key == "citation_fit":
            filled.append("citation_fit:")
            if citations_value != NO_BASIS:
                filled.append(fit_entry(comment, citations_value))
        elif key == "rival_resolution":
            # Conditional field: only required when two mutually-竞合 cards
            # are cited, which this single-citation fill never does.
            continue
        elif "|" in value:
            # A closed enum written as alternatives; an author picks one.
            options = [part.strip() for part in value.split("|")]
            picked = enum_choice if enum_choice in options else options[0]
            filled.append(f"{key}: {picked}")
        elif value:
            filled.append(f"{key}: {value}")
        else:
            filled.append(f"{key}: 略")
    return "\n".join(filled) + "\n"


def prompts_with_citations() -> list[tuple[str, str]]:
    """(filename, Output Shape block) for every prompt that declares citations."""
    found: list[tuple[str, str]] = []
    for path in sorted(PROMPTS.glob("*.md")):
        block = output_shape(path.read_text(encoding="utf-8"))
        if block and "citations:" in block:
            found.append((path.name, block))
    return found


class OutputShapeRoundTripTest(unittest.TestCase):
    def test_every_citing_prompt_is_discovered(self):
        # Guards the guard: if the extraction silently stops finding blocks,
        # every test below would pass vacuously.
        names = [name for name, _ in prompts_with_citations()]
        self.assertEqual(len(names), 9, names)
        self.assertIn("referee.md", names)
        self.assertIn("compatibility-master.md", names)

    def test_output_shape_filled_with_a_real_citation_validates(self):
        for name, block in prompts_with_citations():
            with self.subTest(prompt=name):
                text = fill(block, CITED_ID, keep_citations_comment=False)
                self.assertEqual(
                    check_answer(parse_answer(text), LIBRARY), [], f"\n{text}"
                )

    def test_output_shape_filled_with_no_classical_basis_validates(self):
        # The template ships an inline hint comment on the citations line and
        # three masters are told to always write no_classical_basis, so the
        # value-plus-retained-hint form is the one those masters produce.
        for name, block in prompts_with_citations():
            with self.subTest(prompt=name):
                text = fill(
                    block,
                    NO_BASIS,
                    keep_citations_comment=True,
                    enum_choice="pattern_tendency",
                )
                self.assertEqual(
                    check_answer(parse_answer(text), LIBRARY), [], f"\n{text}"
                )


class WorkedExampleRoundTripTest(unittest.TestCase):
    """The four classics-backed masters ship a worked `citation_fit` example.
    A shipped example that the parser rejects is worse than no example."""

    def test_every_shipped_citation_fit_example_is_accepted(self):
        seen = 0
        for path in sorted(PROMPTS.glob("*.md")):
            text = path.read_text(encoding="utf-8")
            block = fenced_block_after(
                text, lambda line: line.strip().endswith("例如：")
            )
            if block is None or "citation_fit:" not in block:
                continue
            seen += 1
            ids = sorted(set(CARD_ID.findall(block)))
            self.assertTrue(ids, f"{path.name}: example cites no card id")
            answer = parse_answer(f"citations: {', '.join(ids)}\n{block}\n")
            with self.subTest(prompt=path.name):
                self.assertEqual(
                    check_answer(answer, [card(i) for i in ids]), [], f"\n{block}"
                )
        self.assertEqual(seen, 4, "expected four worked examples")


class ReportIndexRoundTripTest(unittest.TestCase):
    """The 依据索引 example in report-generation.md is what a report author
    copies. It must be detected as report-type input and must validate."""

    def test_documented_index_example_validates(self):
        block = fenced_block_after(
            REPORT.read_text(encoding="utf-8"),
            lambda line: line.strip().startswith("## 依据索引"),
        )
        self.assertIsNotNone(block, "no fenced 依据索引 example in report-generation.md")
        ids = sorted(set(CARD_ID.findall(block)))
        self.assertTrue(ids, "the documented example cites no card id")
        answer = parse_answer(block)
        self.assertTrue(answer["is_report"], f"not detected as a report:\n{block}")
        self.assertEqual(
            check_answer(answer, [card(i) for i in ids]), [], f"\n{block}"
        )


if __name__ == "__main__":
    unittest.main()
