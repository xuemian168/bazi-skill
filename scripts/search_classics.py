#!/usr/bin/env python3
"""Search the classics card library, or fall back to raw corpus lines."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from classics.cards import load_cards
from classics.search import search_cards, search_corpus


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query", help="Search text")
    parser.add_argument(
        "--classics-root",
        default="references/classics",
        help="Directory containing cards/ and corpus/ (default: references/classics)",
    )
    parser.add_argument("--topic", help="Restrict to a cards/*.md filename fragment")
    parser.add_argument("--school", help="Restrict to one school name")
    parser.add_argument(
        "--corpus", action="store_true", help="Search raw corpus lines instead of cards"
    )
    parser.add_argument("--limit", type=int, default=10, help="Max hits (default: 10)")
    args = parser.parse_args()

    root = Path(args.classics_root)

    if args.corpus:
        try:
            hits = search_corpus(root, args.query, limit=args.limit)
        except Exception as exc:  # noqa: BLE001
            print(f"无法读取语料文件: {exc}", file=sys.stderr)
            return 2
        if not hits:
            print("no hits")
            return 1
        for value, rel, line, context in hits:
            print(f"{value:.4f}  {rel}#L{line}  {context}")
        return 0

    cards_dir = root / "cards"
    if not cards_dir.is_dir():
        print(f"缺少卡片目录: {cards_dir}", file=sys.stderr)
        return 2

    try:
        cards, errors = load_cards(cards_dir)
    except Exception as exc:  # noqa: BLE001
        print(f"无法读取卡片文件: {exc}", file=sys.stderr)
        return 2

    if errors:
        print("卡片库无效，先运行 validate_citations.py --cards", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 2

    hits = search_cards(
        cards, args.query, topic=args.topic, school=args.school, limit=args.limit
    )
    if not hits:
        print("no hits")
        return 1
    for value, card in hits:
        print(f"{value:.4f}  {card.id}  [{card.tier}]  {card.classic}")
        print(f"          {card.plain}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
