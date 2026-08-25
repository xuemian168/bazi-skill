"""Zero-dependency Chinese retrieval over cards and corpus.

2-gram split plus term-frequency weighting, normalised by sqrt(doc length)
to keep long corpus lines from dominating. No jieba, no embeddings — the
skill has no runtime and must stay standard-library only.
"""

from __future__ import annotations

import math
from pathlib import Path

from .cards import Card
from .corpus import read_lines
from .normalize import normalize


def bigrams(text: str) -> list[str]:
    """Overlapping 2-grams of the normalised text."""
    cleaned = normalize(text)
    return [cleaned[i : i + 2] for i in range(len(cleaned) - 1)]


def score(query_grams: list[str], doc: str) -> float:
    """Sum of query-gram frequencies in `doc`, damped by document length."""
    if not query_grams:
        return 0.0
    cleaned = normalize(doc)
    if not cleaned:
        return 0.0
    total = sum(cleaned.count(gram) for gram in query_grams)
    if total == 0:
        return 0.0
    return total / math.sqrt(len(cleaned))


def _card_haystack(card: Card) -> str:
    return " ".join(
        (card.quote, card.plain, card.classic, card.boundary, *card.premises)
    )


def search_cards(
    cards: list[Card],
    query: str,
    topic: str | None = None,
    school: str | None = None,
    limit: int = 10,
) -> list[tuple[float, Card]]:
    """Rank cards by relevance to `query`, optionally filtered."""
    grams = bigrams(query)
    hits: list[tuple[float, Card]] = []
    for card in cards:
        if topic and topic not in card.source_file:
            continue
        if school and school not in card.schools:
            continue
        value = score(grams, _card_haystack(card))
        if value > 0:
            hits.append((value, card))
    hits.sort(key=lambda item: (-item[0], item[1].id))
    return hits[:limit]


def search_corpus(
    classics_root: Path,
    query: str,
    limit: int = 10,
    window: int = 1,
) -> list[tuple[float, str, int, str]]:
    """Rank corpus lines. Returns (score, relative path, line number, context)."""
    grams = bigrams(query)
    corpus_dir = classics_root / "corpus"
    if not corpus_dir.is_dir():
        return []

    hits: list[tuple[float, str, int, str]] = []
    for path in sorted(corpus_dir.glob("*.txt")):
        lines = read_lines(path)
        rel = f"corpus/{path.name}"
        for index, line in enumerate(lines, start=1):
            value = score(grams, line)
            if value <= 0:
                continue
            low = max(0, index - 1 - window)
            high = min(len(lines), index + window)
            hits.append((value, rel, index, " / ".join(lines[low:high])))
    hits.sort(key=lambda item: (-item[0], item[1], item[2]))
    return hits[:limit]
