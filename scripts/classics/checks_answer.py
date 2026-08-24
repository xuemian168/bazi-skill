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

CARD_ID = re.compile(r"\b([A-Z]{3,4}-\d{4})\b")
FIELD = re.compile(r"^([a-z_]+)\s*[:：]\s*(.*)$")
INDEX_HEADING = re.compile(r"依据索引")
NO_BASIS = "no_classical_basis"


def parse_answer(text: str) -> dict[str, object]:
    """Extract the citation-relevant shape of an answer or report."""
    lines = text.splitlines()
    fields: dict[str, str] = {}
    fit_ids: list[str] = []
    rival_resolutions: list[str] = []
    current: str | None = None
    index_start: int | None = None

    for offset, raw in enumerate(lines):
        if index_start is None and INDEX_HEADING.search(raw):
            index_start = offset
        field = FIELD.match(raw)
        if field:
            key, value = field.group(1), field.group(2).strip()
            current = key
            if key == "rival_resolution" and value:
                rival_resolutions.append(value)
            else:
                fields[key] = value
            continue
        if current == "citation_fit" and raw.strip():
            fit_ids.extend(CARD_ID.findall(raw))
        elif current == "rival_resolution" and raw.strip():
            rival_resolutions.append(raw.strip())

    raw_citations = fields.get("citations")
    no_basis = raw_citations is not None and NO_BASIS in raw_citations
    citations = [] if no_basis else CARD_ID.findall(raw_citations or "")

    body_ids: list[str] = []
    index_ids: list[str] = []
    if index_start is not None:
        body_ids = CARD_ID.findall("\n".join(lines[:index_start]))
        index_ids = CARD_ID.findall("\n".join(lines[index_start:]))

    return {
        "has_citations_field": raw_citations is not None,
        "no_classical_basis": no_basis,
        "citations": citations,
        "citation_fit_ids": fit_ids,
        "pattern_call": fields.get("pattern_call", ""),
        "rival_resolutions": rival_resolutions,
        "is_report": index_start is not None,
        "body_ids": body_ids,
        "index_ids": index_ids,
    }


def check_answer(answer: dict[str, object], cards: list[Card]) -> list[str]:
    """Run every mode-B rule. Empty list means citation use is valid."""
    errors: list[str] = []
    by_id = {card.id: card for card in cards}
    citations: list[str] = answer["citations"]

    if not answer["has_citations_field"]:
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

    cited = set(citations)
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

    if answer["is_report"]:
        indexed = set(answer["index_ids"])
        for card_id in sorted(set(answer["body_ids"])):
            if card_id not in indexed:
                errors.append(f"正文引用的 {card_id} 未出现在「依据索引」章节")
        for card_id in sorted(indexed):
            if card_id not in by_id:
                errors.append(f"「依据索引」列出了不存在的卡片 {card_id}")

    return errors
