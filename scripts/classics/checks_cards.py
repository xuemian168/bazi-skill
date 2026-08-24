"""Mode A: card library self-check (spec 9.1)."""

from __future__ import annotations

from pathlib import Path

from . import CARD_TIERS, ENABLED_PREFIXES, RESERVED_PREFIXES, SCHOOLS
from .cards import Card
from .corpus import parse_provenance, read_lines, sha256_of, slice_lines
from .normalize import normalize


def _check_identity(cards: list[Card], errors: list[str]) -> None:
    seen: dict[str, Card] = {}
    for card in cards:
        where = f"{card.source_file}:{card.line} {card.id}"
        if card.id in seen:
            first = seen[card.id]
            errors.append(
                f"{where}: 卡片 ID 重复，已在 {first.source_file}:{first.line} 出现"
            )
        else:
            seen[card.id] = card

        prefix = card.id.split("-", 1)[0]
        if prefix in RESERVED_PREFIXES:
            errors.append(f"{where}: 前缀 `{prefix}` 尚未启用，本期不得使用")
        elif prefix not in ENABLED_PREFIXES:
            errors.append(
                f"{where}: 未知前缀 `{prefix}`，本期合法前缀为 {list(ENABLED_PREFIXES)}"
            )


def _check_enums(cards: list[Card], errors: list[str]) -> None:
    for card in cards:
        where = f"{card.source_file}:{card.line} {card.id}"
        if card.tier not in CARD_TIERS:
            errors.append(
                f"{where}: 层级 `{card.tier}` 不在枚举 {list(CARD_TIERS)} 内"
            )
        for school in card.schools:
            if school not in SCHOOLS:
                errors.append(f"{where}: 流派 `{school}` 不在枚举 {list(SCHOOLS)} 内")


def _check_rivals(cards: list[Card], errors: list[str]) -> None:
    by_id = {card.id: card for card in cards}
    for card in cards:
        where = f"{card.source_file}:{card.line} {card.id}"
        for rival in card.rivals:
            target = by_id.get(rival.card_id)
            if target is None:
                errors.append(f"{where}: 竞合指向不存在的卡片 {rival.card_id}")
                continue
            if card.id not in {back.card_id for back in target.rivals}:
                errors.append(
                    f"{where}: 竞合必须双向，{rival.card_id} 未回指 {card.id}"
                )


def _check_quotes(cards: list[Card], classics_root: Path, errors: list[str]) -> None:
    cache: dict[str, list[str] | None] = {}
    for card in cards:
        where = f"{card.source_file}:{card.line} {card.id}"
        rel = card.corpus.path
        if rel not in cache:
            path = classics_root / rel
            cache[rel] = read_lines(path) if path.is_file() else None
        lines = cache[rel]
        if lines is None:
            errors.append(f"{where}: 语料文件不存在 {rel}")
            continue
        chunk = slice_lines(lines, card.corpus.start, card.corpus.end)
        if chunk is None:
            errors.append(
                f"{where}: corpus 行号超出范围 "
                f"L{card.corpus.start}-L{card.corpus.end}（{rel} 共 {len(lines)} 行）"
            )
            continue
        if normalize(card.quote) not in normalize(chunk):
            errors.append(
                f"{where}: 原文未出现在 {rel}#L{card.corpus.start}-L{card.corpus.end}"
            )


def _check_provenance(cards: list[Card], classics_root: Path, errors: list[str]) -> None:
    referenced = sorted({card.corpus.path for card in cards})
    if not referenced:
        return
    recorded, provenance_errors = parse_provenance(
        classics_root / "corpus" / "PROVENANCE.md"
    )
    errors.extend(provenance_errors)
    for rel in referenced:
        path = classics_root / rel
        if not path.is_file():
            continue
        if rel not in recorded:
            errors.append(f"PROVENANCE 未登记语料 {rel}")
            continue
        actual = sha256_of(path)
        if actual != recorded[rel]:
            errors.append(
                f"{rel} 的 sha256 与 PROVENANCE 不一致："
                f"实际 {actual}，登记 {recorded[rel]}"
            )


def check_cards(cards: list[Card], classics_root: Path) -> list[str]:
    """Run every mode-A rule. Empty list means the card library is valid."""
    errors: list[str] = []
    _check_identity(cards, errors)
    _check_enums(cards, errors)
    _check_rivals(cards, errors)
    _check_quotes(cards, classics_root, errors)
    _check_provenance(cards, classics_root, errors)
    return errors
