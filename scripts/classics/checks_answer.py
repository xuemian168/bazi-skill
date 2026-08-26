"""Mode B: verify how an answer uses classics citations (spec 9.1).

Input is the `key: value` text block that school masters and the referee
already emit, or a report containing a 依据索引 section.

「孤证不立」is deliberately NOT checked here: classifying a claim as
event-level is not reliably possible from free text, and a check that
silently misses cases is worse than no check. It stays a referee prompt
rule (spec 8.2 item 4).
"""

from __future__ import annotations

import re

from .cards import Card

_CARD_ID_CORE = r"[A-Z]{3,4}-\d{4}"
# Lookaround instead of \b: \b does not fire between a CJK character and an
# ASCII letter/digit (both count as \w), so unspaced Chinese prose like
# "依DTS-0001定格" would otherwise hide the id entirely.
CARD_ID = re.compile(rf"(?<![A-Za-z0-9])({_CARD_ID_CORE})(?![A-Za-z0-9-])")
# A continuation line of a citation_fit/rival_resolution block: indented,
# and starting with a card id (not merely containing one somewhere).
CONTINUATION = re.compile(rf"^\s+({_CARD_ID_CORE})(?![A-Za-z0-9-])")
FIELD = re.compile(r"^\s*([A-Za-z_]+)\s*[:：]\s*(.*)$")
# A bare heading line: "依据索引" alone, or a markdown ATX heading of it,
# with an optional trailing comment (the brief's own canonical example is
# "依据索引                                # 报告型输入的判别标记" — a line
# ending immediately after the heading text would miss that literal form).
# Anchoring to the whole line (rather than a substring search) means a
# table of contents entry or a closing sentence that merely mentions the
# heading text does not get mistaken for the section boundary.
INDEX_HEADING = re.compile(r"^\s*(?:#{1,6}\s*)?依据索引\s*(?:#.*)?$")
NO_BASIS = "no_classical_basis"
# Lookaround instead of \b, for the same reason CARD_ID uses it: \b does
# not fire between a CJK character and an ASCII letter/digit, so
# "无引用no_classical_basis" (no space before the token) would otherwise
# never match.
NO_BASIS_TOKEN = re.compile(rf"(?<![A-Za-z0-9_]){re.escape(NO_BASIS)}(?![A-Za-z0-9_])")


def parse_answer(text: str) -> dict[str, object]:
    """Extract the citation-relevant shape of an answer or report."""
    lines = text.splitlines()
    fields: dict[str, str] = {}
    citations_field_count = 0
    fit_ids: list[str] = []
    rival_resolutions: list[str] = []
    current: str | None = None
    index_start: int | None = None

    for offset, raw in enumerate(lines):
        if INDEX_HEADING.match(raw):
            # Last occurrence wins: an earlier heading-shaped line (e.g. a
            # template block quoted for illustration) should not anchor the
            # window ahead of the real, final section.
            index_start = offset

        if not raw.strip():
            # A blank line always ends a citation_fit/rival_resolution
            # continuation block; without this, every non-blank line to
            # end-of-document keeps getting scanned for card ids under
            # whichever field was last seen (including 依据索引 table
            # rows, which would then auto-satisfy citation_fit/rival
            # checks on every report by construction).
            current = None
            continue

        field = FIELD.match(raw)
        if field:
            # Lowercasing here (rather than restricting to a closed
            # vocabulary) is the whole fix: it makes `Pattern_call:` and
            # `  pattern_call:` normalise to the same key as `pattern_call:`
            # so rule 4's tier gate still runs. A field the module doesn't
            # otherwise care about (e.g. `confidence:`, `scope:` — real
            # fields the school-prompt Output Shapes already emit) is
            # simply stored and ignored, exactly as before this fix round;
            # there is no vocabulary to be missing from.
            key = field.group(1).lower()
            value = field.group(2).strip()
            current = key
            if key == "citations":
                citations_field_count += 1
                fields[key] = value
            elif key == "citation_fit":
                fields[key] = value
                if value:
                    fit_ids.extend(CARD_ID.findall(value))
            elif key == "rival_resolution":
                if value:
                    rival_resolutions.append(value)
            else:
                fields[key] = value
            continue

        continuation = CONTINUATION.match(raw)
        if not continuation:
            continue
        if current == "citation_fit":
            fit_ids.extend(CARD_ID.findall(raw))
        elif current == "rival_resolution":
            rival_resolutions.append(raw.strip())

    raw_citations = fields.get("citations")
    no_basis = raw_citations is not None and raw_citations.strip() == NO_BASIS
    citations = [] if no_basis else CARD_ID.findall(raw_citations or "")
    mixed_basis = bool(citations) and bool(
        NO_BASIS_TOKEN.search(raw_citations or "")
    )

    body_ids: list[str] = []
    index_ids: list[str] = []
    if index_start is not None:
        body_ids = CARD_ID.findall("\n".join(lines[:index_start]))
        index_ids = CARD_ID.findall("\n".join(lines[index_start:]))

    return {
        "has_citations_field": raw_citations is not None,
        "no_classical_basis": no_basis,
        "mixed_no_classical_basis": mixed_basis,
        "citations": citations,
        "citation_fit_ids": fit_ids,
        "pattern_call": fields.get("pattern_call", ""),
        "rival_resolutions": rival_resolutions,
        "is_report": index_start is not None,
        "body_ids": body_ids,
        "index_ids": index_ids,
        "duplicate_citations_field": citations_field_count > 1,
    }


def check_answer(answer: dict[str, object], cards: list[Card]) -> list[str]:
    """Run every mode-B rule. Empty list means citation use is valid."""
    errors: list[str] = []
    by_id = {card.id: card for card in cards}
    citations: list[str] = answer["citations"]
    is_report: bool = answer["is_report"]

    if answer["duplicate_citations_field"]:
        errors.append(
            "`citations` 字段出现多次，请为每份分析分别校验"
            "（不支持单份输入中出现多个 citations 块）"
        )

    if answer["mixed_no_classical_basis"]:
        errors.append(f"`citations` 中同时出现引用 ID 与 {NO_BASIS}，请二选一")

    if not answer["has_citations_field"]:
        # Report-type input already declares which cards it relies on
        # through the 依据索引 table itself (card id + 本盘适用理由
        # columns) — that table *is* the report layer's citation
        # mechanism. Requiring a separate machine-readable `citations:`
        # field on top of it duplicates the table and puts master-layer
        # scaffolding into a reader-facing artefact, so its *presence* is
        # only mandatory for non-report input. When the field IS supplied
        # on a report, it is still validated exactly like a master output
        # (see the loop below) — this only relaxes absence, not content.
        if not is_report:
            errors.append(f"缺少 `citations` 字段（无可引时应写 {NO_BASIS}）")
    elif not citations and not answer["no_classical_basis"]:
        errors.append(f"`citations` 为空；无可引时应显式写 {NO_BASIS}")

    for card_id in citations:
        if card_id not in by_id:
            errors.append(f"引用了不存在的卡片 {card_id}")
        if card_id not in answer["citation_fit_ids"]:
            errors.append(f"{card_id} 缺少对应的 citation_fit 说明")

    if answer["pattern_call"] == "formal_pattern":
        strong = {"核心论断", "操作规则"}
        if not any(
            by_id[c].tier in strong for c in citations if c in by_id
        ):
            errors.append(
                "pattern_call 为 formal_pattern 但无「核心论断」或「操作规则」"
                "层级的卡片支撑，应降级为 pattern_tendency"
            )

    # Report-type input may have no `citations:` field at all now, so the
    # rival-pair guard must not key off that field alone — otherwise
    # simply omitting `citations:` on a report would silently drop the
    # requirement that a cited rival pair carry a visible
    # rival_resolution. `index_ids` is what the report actually claims to
    # rely on (every id appearing in/after the 依据索引 heading), so it is
    # folded in whenever the input is a report, whether or not
    # `citations:` was also supplied.
    cited = set(citations)
    if is_report:
        cited |= set(answer["index_ids"])
    resolved = "\n".join(answer["rival_resolutions"])
    for card_id in sorted(cited):
        card = by_id.get(card_id)
        if card is None:
            continue
        for rival in card.rivals:
            if rival.card_id not in cited or rival.card_id < card_id:
                continue
            if not (card_id in resolved and rival.card_id in resolved):
                errors.append(
                    f"{card_id} 与 {rival.card_id} 互为竞合，"
                    f"必须给出同时点到两者的 rival_resolution"
                )

    if is_report:
        indexed = set(answer["index_ids"])
        for card_id in sorted(set(answer["body_ids"])):
            if card_id not in indexed:
                errors.append(f"正文引用的 {card_id} 未出现在「依据索引」章节")
        for card_id in sorted(indexed):
            if card_id not in by_id:
                errors.append(f"「依据索引」列出了不存在的卡片 {card_id}")

    return errors
