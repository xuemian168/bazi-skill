#!/usr/bin/env python3
"""Print table-backed GanZhi facts (生克, 十神, 纳音, 刑冲合害, 流日) for a chart and transit."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date

from ganzhi.facts import NATAL_POSITIONS, build_facts, render_text
from ganzhi.pillars import day_pillar, hour_pillar
from ganzhi.table import branches, validate_pillar

LUCK_OPTIONS = (("dayun", "大运"), ("liunian", "流年"), ("liuyue", "流月"))


def collect_pillars(args: argparse.Namespace) -> tuple[list[tuple[str, str]], str | None, list[str]]:
    pillars: list[tuple[str, str]] = []
    errors: list[str] = []

    if args.chart:
        if len(args.chart) not in (3, 4):
            errors.append("--chart 需要 3 柱（年 月 日）或 4 柱（年 月 日 时）")
        pillars += list(zip(NATAL_POSITIONS, args.chart))

    for option, label in LUCK_OPTIONS:
        value = getattr(args, option)
        if value:
            pillars.append((label, value))

    errors += [message for _, gz in pillars if (message := validate_pillar(gz))]

    date_text = None
    if args.date:
        try:
            day = date.today() if args.date == "today" else date.fromisoformat(args.date)
        except ValueError:
            errors.append(f"--date 需要 YYYY-MM-DD 或 today，收到 {args.date}")
        else:
            date_text = day.isoformat()
            pillars.append(("流日", day_pillar(day)))

    if args.hour_branch:
        if args.hour_branch not in branches():
            errors.append(f"--hour-branch 需要一个地支，收到 {args.hour_branch}")
        elif not date_text:
            errors.append("--hour-branch 需要同时给 --date（时干由流日日干按五鼠遁推出）")
        else:
            pillars.append(("流时", hour_pillar(dict(pillars)["流日"][0], args.hour_branch)))

    if not pillars and not errors:
        errors.append("至少给出 --chart、--date、--dayun、--liunian、--liuyue 之一")
    return pillars, date_text, errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--chart", nargs="+", metavar="干支", help="原局四柱：年 月 日 [时]，如 庚申 己丑 癸卯 壬子")
    parser.add_argument("--dayun", metavar="干支", help="当前大运（由宿主项目算出）")
    parser.add_argument("--liunian", metavar="干支", help="流年（依立春交接，由宿主项目算出）")
    parser.add_argument("--liuyue", metavar="干支", help="流月（依节交接，由宿主项目算出）")
    parser.add_argument("--date", metavar="YYYY-MM-DD", help="公历日期或 today；本脚本直接算出流日日柱")
    parser.add_argument("--hour-branch", metavar="地支", help="流时地支（不做真太阳时换算，只按五鼠遁配时干）")
    parser.add_argument("--json", action="store_true", help="输出 JSON 而不是文本")
    args = parser.parse_args()

    pillars, date_text, errors = collect_pillars(args)
    if errors:
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 2

    facts = build_facts(pillars, date_text)
    if args.json:
        print(json.dumps(facts, ensure_ascii=False, indent=2))
    else:
        print(render_text(facts))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
