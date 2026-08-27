"""Normalise text before comparing a card quote against corpus source text.

Rules follow spec 5.5: drop all whitespace and punctuation, keep everything
else verbatim. No traditional/simplified conversion — card and corpus must
already agree on glyph form.

The punctuation set is a deliberate superset of the spec list: PDF-extracted
and mixed-source corpora routinely carry half-width punctuation, and omitting
it would cause spurious verification failures. See plan deviation A.
"""

from __future__ import annotations

PUNCTUATION = frozenset(
    "。，、；：？！「」『』《》〈〉（）()·—…“”‘’"
    ",.;:?!\"\'-[]{}<>"
)


def normalize(text: str) -> str:
    """Return `text` with whitespace and punctuation removed."""
    return "".join(ch for ch in text if not ch.isspace() and ch not in PUNCTUATION)
