"""Corpus access: line reads, 1-indexed slicing, and PROVENANCE.md parsing.

Line numbers are the anchor for every card's `corpus` field, so corpus files
must never be re-flowed after ingest (spec 7.2).
"""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

SECTION = re.compile(r"^##\s+(corpus/[A-Za-z0-9_.\-]+)\s*$")
SHA_FIELD = re.compile(r"^-\s+sha256\s*[:：]\s*([0-9a-fA-F]+)\s*$")


def sha256_of(path: Path) -> str:
    """Hex sha256 of the file's raw bytes."""
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def read_lines(path: Path) -> list[str]:
    """Corpus lines without trailing newlines."""
    return path.read_text(encoding="utf-8").splitlines()


def slice_lines(lines: list[str], start: int, end: int) -> str | None:
    """Join lines `start`..`end` inclusive, 1-indexed. None if out of range."""
    if start < 1 or end < start or end > len(lines):
        return None
    return "".join(lines[start - 1 : end])


def parse_provenance(path: Path) -> tuple[dict[str, str], list[str]]:
    """Map corpus relative path -> recorded sha256. Returns (mapping, errors)."""
    if not path.is_file():
        return {}, [f"缺少 PROVENANCE 清单: {path}"]

    mapping: dict[str, str] = {}
    errors: list[str] = []
    current: str | None = None
    for raw in path.read_text(encoding="utf-8").splitlines():
        section = SECTION.match(raw)
        if section:
            if current is not None and current not in mapping:
                errors.append(f"PROVENANCE 段 `{current}` 缺少 sha256 字段")
            current = section.group(1)
            continue
        if current is None:
            continue
        sha = SHA_FIELD.match(raw)
        if sha:
            mapping[current] = sha.group(1).lower()
    if current is not None and current not in mapping:
        errors.append(f"PROVENANCE 段 `{current}` 缺少 sha256 字段")
    return mapping, errors
