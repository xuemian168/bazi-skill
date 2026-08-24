#!/usr/bin/env python3
"""Validate classics citations: card library self-check, or answer citation use."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from classics.cards import load_cards
from classics.checks_cards import check_cards


def report(errors: list[str]) -> int:
    if errors:
        print("INVALID")
        for error in errors:
            print(f"- {error}")
        return 1
    print("VALID")
    return 0


def run_cards_mode(classics_root: Path, show_count: bool) -> int:
    cards_dir = classics_root / "cards"
    if not cards_dir.is_dir():
        print(f"缺少卡片目录: {cards_dir}", file=sys.stderr)
        return 2

    cards, parse_errors = load_cards(cards_dir)
    if show_count:
        print(f"cards: {len(cards)}")
    return report(parse_errors + check_cards(cards, classics_root))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--cards",
        metavar="CLASSICS_ROOT",
        help="Card library self-check. Directory containing cards/ and corpus/",
    )
    parser.add_argument("--count", action="store_true", help="Print parsed card count")
    args = parser.parse_args()

    if not args.cards:
        parser.error("请指定 --cards <CLASSICS_ROOT>")
    return run_cards_mode(Path(args.cards), args.count)


if __name__ == "__main__":
    raise SystemExit(main())
