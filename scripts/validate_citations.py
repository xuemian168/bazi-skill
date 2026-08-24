#!/usr/bin/env python3
"""Validate classics citations: card library self-check, or answer citation use."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from classics.cards import load_cards
from classics.checks_answer import check_answer, parse_answer
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

    try:
        cards, parse_errors = load_cards(cards_dir)
    except Exception as exc:  # noqa: BLE001
        print(f"无法读取卡片文件: {exc}", file=sys.stderr)
        return 2

    if show_count:
        print(f"cards: {len(cards)}")
    return report(parse_errors + check_cards(cards, classics_root))


def run_answer_mode(answer_path: str, classics_root: Path) -> int:
    cards_dir = classics_root / "cards"
    if not cards_dir.is_dir():
        print(f"缺少卡片目录: {cards_dir}", file=sys.stderr)
        return 2

    try:
        cards, parse_errors = load_cards(cards_dir)
    except Exception as exc:  # noqa: BLE001
        print(f"无法读取卡片文件: {exc}", file=sys.stderr)
        return 2

    if parse_errors:
        print("卡片库本身无效，先修复后再校验答案：", file=sys.stderr)
        for error in parse_errors:
            print(f"- {error}", file=sys.stderr)
        return 2

    if answer_path == "-":
        text = sys.stdin.read()
    else:
        path = Path(answer_path)
        if not path.is_file():
            print(f"找不到答案文件: {path}", file=sys.stderr)
            return 2
        try:
            text = path.read_text(encoding="utf-8")
        except Exception as exc:  # noqa: BLE001
            print(f"无法读取答案文件: {exc}", file=sys.stderr)
            return 2

    return report(check_answer(parse_answer(text), cards))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument(
        "--cards",
        metavar="CLASSICS_ROOT",
        help="Card library self-check. Directory containing cards/ and corpus/",
    )
    mode.add_argument(
        "--answer",
        metavar="FILE",
        help="Answer or report to check, or '-' for stdin",
    )
    parser.add_argument(
        "--classics-root",
        default="references/classics",
        help="Card library root used by --answer (default: references/classics)",
    )
    parser.add_argument("--count", action="store_true", help="Print parsed card count")
    args = parser.parse_args()

    if args.cards:
        return run_cards_mode(Path(args.cards), args.count)
    return run_answer_mode(args.answer, Path(args.classics_root))


if __name__ == "__main__":
    raise SystemExit(main())
