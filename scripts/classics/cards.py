"""Parse classics knowledge cards from references/classics/cards/*.md.

Card format is fixed by spec 5.4. This module reports structural problems
only (missing fields, malformed values); semantic rules such as tier
enumeration and bidirectional rival closure live in checks_cards.py.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

CARD_HEADING = re.compile(r"^###\s+([A-Z]{3,4}-\d{4})\s*$")
SCALAR_FIELD = re.compile(r"^-\s+([^:：]+)[:：]\s*(.*)$")
LIST_ITEM = re.compile(r"^\s{2,}-\s+(.*)$")
CORPUS_REF = re.compile(r"^(corpus/[A-Za-z0-9_.\-]+)#L(\d+)(?:-L(\d+))?$")
RIVAL_LINE = re.compile(r"^([A-Z]{3,4}-\d{4})\s*(?:—|--)\s*(.+)$")

SCALAR_KEYS = ("典籍", "原文", "白话", "层级", "流派", "反例边界", "corpus")
LIST_KEYS = ("适用前提", "竞合")
REQUIRED_KEYS = SCALAR_KEYS + ("适用前提",)


@dataclass(frozen=True)
class CorpusRef:
    path: str
    start: int
    end: int


@dataclass(frozen=True)
class Rival:
    card_id: str
    note: str


@dataclass(frozen=True)
class Card:
    id: str
    classic: str
    quote: str
    plain: str
    premises: tuple[str, ...]
    tier: str
    schools: tuple[str, ...]
    rivals: tuple[Rival, ...]
    boundary: str
    corpus: CorpusRef
    source_file: str
    line: int


def _split_blocks(text: str) -> list[tuple[str, int, list[str]]]:
    blocks: list[tuple[str, int, list[str]]] = []
    current: tuple[str, int, list[str]] | None = None
    for offset, raw in enumerate(text.splitlines(), start=1):
        heading = CARD_HEADING.match(raw)
        if heading:
            if current is not None:
                blocks.append(current)
            current = (heading.group(1), offset, [])
            continue
        if current is not None:
            if raw.startswith("### ") or raw.startswith("## "):
                blocks.append(current)
                current = None
                continue
            current[2].append(raw)
    if current is not None:
        blocks.append(current)
    return blocks


def _parse_fields(body: list[str]) -> dict[str, object]:
    fields: dict[str, object] = {}
    pending_list_key: str | None = None
    for raw in body:
        if not raw.strip():
            continue
        item = LIST_ITEM.match(raw)
        if item and pending_list_key:
            fields.setdefault(pending_list_key, []).append(item.group(1).strip())
            continue
        scalar = SCALAR_FIELD.match(raw)
        if not scalar:
            continue
        key, value = scalar.group(1).strip(), scalar.group(2).strip()
        if key in LIST_KEYS:
            pending_list_key = key
            fields.setdefault(key, [])
            if value:
                fields[key].append(value)
            continue
        pending_list_key = None
        fields[key] = value
    return fields


def _build_card(
    card_id: str,
    line: int,
    fields: dict[str, object],
    source_file: str,
    errors: list[str],
) -> Card | None:
    where = f"{source_file}:{line} {card_id}"
    ok = True
    for key in REQUIRED_KEYS:
        value = fields.get(key)
        if value is None or (isinstance(value, str) and not value) or value == []:
            errors.append(f"{where}: 缺少必填字段 `{key}`")
            ok = False

    corpus_raw = fields.get("corpus", "")
    corpus_ref = None
    if isinstance(corpus_raw, str) and corpus_raw:
        match = CORPUS_REF.match(corpus_raw)
        if not match:
            errors.append(
                f"{where}: `corpus` 必须形如 corpus/<file>#L<a>-L<b>，实际为 {corpus_raw!r}"
            )
            ok = False
        else:
            start = int(match.group(2))
            end = int(match.group(3)) if match.group(3) else start
            if end < start:
                errors.append(f"{where}: `corpus` 行号区间倒置 L{start}-L{end}")
                ok = False
            corpus_ref = CorpusRef(match.group(1), start, end)

    rivals: list[Rival] = []
    for entry in fields.get("竞合", []) or []:
        match = RIVAL_LINE.match(entry)
        if not match:
            errors.append(
                f"{where}: `竞合` 条目必须形如 `<ID> — <差异说明>`，实际为 {entry!r}"
            )
            ok = False
            continue
        rivals.append(Rival(match.group(1), match.group(2).strip()))

    if not ok or corpus_ref is None:
        return None

    schools = tuple(
        part.strip()
        for part in re.split(r"[,，]", str(fields["流派"]))
        if part.strip()
    )
    return Card(
        id=card_id,
        classic=str(fields["典籍"]),
        quote=str(fields["原文"]),
        plain=str(fields["白话"]),
        premises=tuple(fields["适用前提"]),
        tier=str(fields["层级"]),
        schools=schools,
        rivals=tuple(rivals),
        boundary=str(fields["反例边界"]),
        corpus=corpus_ref,
        source_file=source_file,
        line=line,
    )


def parse_cards_text(text: str, source_file: str) -> tuple[list[Card], list[str]]:
    """Parse one cards/*.md file body. Returns (cards, structural errors)."""
    cards: list[Card] = []
    errors: list[str] = []
    for card_id, line, body in _split_blocks(text):
        card = _build_card(card_id, line, _parse_fields(body), source_file, errors)
        if card is not None:
            cards.append(card)
    return cards, errors


def load_cards(cards_dir: Path) -> tuple[list[Card], list[str]]:
    """Parse every *.md under `cards_dir`, sorted by filename."""
    cards: list[Card] = []
    errors: list[str] = []
    for path in sorted(cards_dir.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        parsed, parse_errors = parse_cards_text(text, path.name)
        cards.extend(parsed)
        errors.extend(parse_errors)
    return cards, errors
