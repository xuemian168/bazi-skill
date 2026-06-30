#!/usr/bin/env python3
"""Validate a K-line AnalysisResult JSON payload."""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any


SECTIONS = [
    "personality",
    "career",
    "wealth",
    "fengShui",
    "marriage",
    "health",
    "family",
]


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def load_json(path: str) -> Any:
    if path == "-":
        return json.load(sys.stdin)
    with Path(path).open("r", encoding="utf-8") as fh:
        return json.load(fh)


def validate_rating(errors: list[str], obj: dict[str, Any], path: str) -> None:
    rating = obj.get("rating")
    if not is_number(rating) or not 1 <= rating <= 10:
        fail(errors, f"{path}.rating must be a number from 1 to 10")
    if not isinstance(obj.get("content"), str) or not obj["content"].strip():
        fail(errors, f"{path}.content must be a non-empty string")


def validate_timeline(
    errors: list[str],
    timeline: Any,
    birth_year: int | None,
) -> None:
    if not isinstance(timeline, list):
        fail(errors, "timeline must be an array")
        return
    if len(timeline) != 100:
        fail(errors, f"timeline must contain exactly 100 entries, got {len(timeline)}")

    peak_count = 0
    up_count = 0
    down_count = 0

    for idx, item in enumerate(timeline):
        path = f"timeline[{idx}]"
        if not isinstance(item, dict):
            fail(errors, f"{path} must be an object")
            continue

        expected_age = idx + 1
        age = item.get("age")
        if age != expected_age:
            fail(errors, f"{path}.age must be {expected_age}, got {age!r}")

        year = item.get("year")
        if birth_year is not None and year != birth_year + idx:
            fail(errors, f"{path}.year must be {birth_year + idx}, got {year!r}")
        elif not isinstance(year, int) or isinstance(year, bool):
            fail(errors, f"{path}.year must be an integer")

        for key in ("open", "close", "high", "low"):
            value = item.get(key)
            if not is_number(value) or not 0 <= value <= 100:
                fail(errors, f"{path}.{key} must be a finite number from 0 to 100")

        open_ = item.get("open")
        close = item.get("close")
        high = item.get("high")
        low = item.get("low")
        if all(is_number(v) for v in (open_, close, high, low)):
            if high < max(open_, close):
                fail(errors, f"{path}.high must be >= max(open, close)")
            if low > min(open_, close):
                fail(errors, f"{path}.low must be <= min(open, close)")
            if close > open_:
                up_count += 1
            if close < open_:
                down_count += 1

        for key in ("summary", "detailedReview"):
            if not isinstance(item.get(key), str) or not item[key].strip():
                fail(errors, f"{path}.{key} must be a non-empty string")

        if item.get("isPeak") is True:
            peak_count += 1

    if peak_count != 1:
        fail(errors, f"timeline must mark exactly one isPeak=true entry, got {peak_count}")
    if up_count == 0:
        fail(errors, "timeline must include at least one rising candle with close > open")
    if down_count == 0:
        fail(errors, "timeline must include at least one falling candle with close < open")


def validate_payload(payload: Any, explicit_birth_year: int | None) -> list[str]:
    errors: list[str] = []
    if not isinstance(payload, dict):
        return ["root must be a JSON object"]

    for key in ("mainAttribute", "generalComment", "volatilityAnalysis"):
        if not isinstance(payload.get(key), str) or not payload[key].strip():
            fail(errors, f"{key} must be a non-empty string")

    overall = payload.get("overallScore")
    if not is_number(overall) or not 1 <= overall <= 10:
        fail(errors, "overallScore must be a number from 1 to 10")

    investment = payload.get("investment")
    if not isinstance(investment, dict):
        fail(errors, "investment must be an object")
    else:
        validate_rating(errors, investment, "investment")
        for key in ("opportunityYear", "style"):
            if not isinstance(investment.get(key), str) or not investment[key].strip():
                fail(errors, f"investment.{key} must be a non-empty string")

    for section in SECTIONS:
        value = payload.get(section)
        if not isinstance(value, dict):
            fail(errors, f"{section} must be an object")
        else:
            validate_rating(errors, value, section)

    birth_year = explicit_birth_year
    if birth_year is None and isinstance(payload.get("birthYear"), int) and not isinstance(payload.get("birthYear"), bool):
        birth_year = payload["birthYear"]

    if birth_year is not None and not 1800 <= birth_year <= 2200:
        fail(errors, f"birthYear looks out of expected range: {birth_year}")

    validate_timeline(errors, payload.get("timeline"), birth_year)
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("json_file", help="Path to JSON file, or '-' for stdin")
    parser.add_argument("--birth-year", type=int, help="Expected first timeline year")
    args = parser.parse_args()

    try:
        payload = load_json(args.json_file)
    except Exception as exc:  # noqa: BLE001
        print(f"Invalid JSON: {exc}", file=sys.stderr)
        return 2

    errors = validate_payload(payload, args.birth_year)
    if errors:
        print("INVALID")
        for error in errors:
            print(f"- {error}")
        return 1

    print("VALID")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
