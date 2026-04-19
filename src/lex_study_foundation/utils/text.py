"""Shared text-normalization layer.

Every pipeline stage that touches text content should use this module
as the single source for normalization. Functions are small, explicit,
deterministic, and safe for Turkish educational text.

Design principles:
- NFC Unicode normalization (non-lossy, preserves Turkish characters)
- No lowercasing, no case-folding, no punctuation removal
- No "smart" rewrites that silently change content
- Each function is independently usable
- ``clean_text()`` is the convenience pipeline using safe defaults

Usage::

    from lex_study_foundation.utils.text import clean_text, is_probably_broken_text

    cleaned = clean_text(raw_input)
    if is_probably_broken_text(raw_input):
        log.warning("Input looks corrupted")
"""

from __future__ import annotations

import re
import unicodedata

__all__ = [
    "clean_text",
    "is_probably_broken_text",
    "normalize_newlines",
    "normalize_unicode",
    "normalize_whitespace",
    "strip_control_chars",
]

# ── Pre-compiled patterns ───────────────────────────────────────────────────

# Matches C0 control chars (U+0000-U+001F) and C1 (U+0080-U+009F),
# EXCEPT \n (U+000A) and \t (U+0009) which we want to preserve.
_CONTROL_CHAR_RE = re.compile(
    r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f\x80-\x9f]"
)

# Matches runs of horizontal whitespace (spaces and tabs) within a line.
_HORIZONTAL_WS_RE = re.compile(r"[ \t]+")


# ── Public API ──────────────────────────────────────────────────────────────


def normalize_unicode(text: str) -> str:
    """Normalize Unicode to NFC (Canonical Composition).

    NFC composes decomposed characters (base + combining diacritical)
    into single precomposed code points without changing semantics.
    This is non-lossy and preserves all Turkish characters identically.

    Idempotent: calling on already-NFC text returns the same string.
    """
    return unicodedata.normalize("NFC", text)


def normalize_whitespace(text: str) -> str:
    """Normalize horizontal whitespace on a per-line basis.

    For each line:
    - Collapse runs of spaces/tabs into a single space.
    - Strip leading and trailing whitespace.

    Lines are split by ``\\n``, processed individually, and rejoined.
    Consecutive blank lines are preserved (no aggressive collapse).

    This function does NOT touch newlines themselves — call
    ``normalize_newlines()`` first if ``\\r\\n`` / ``\\r`` cleanup is needed.
    """
    lines = text.split("\n")
    normalized = []
    for line in lines:
        # Collapse horizontal whitespace, then strip edges
        line = _HORIZONTAL_WS_RE.sub(" ", line).strip()
        normalized.append(line)
    return "\n".join(normalized)


def normalize_newlines(text: str) -> str:
    r"""Convert all line endings to ``\n``.

    Handles:
    - ``\r\n`` (Windows) → ``\n``
    - standalone ``\r`` (old Mac) → ``\n``
    """
    # Order matters: replace \r\n first, then standalone \r
    return text.replace("\r\n", "\n").replace("\r", "\n")


def strip_control_chars(text: str) -> str:
    r"""Remove C0/C1 control characters, preserving ``\n`` and ``\t``.

    Removes characters in ranges U+0000–U+0008, U+000B, U+000C,
    U+000E–U+001F, U+007F, U+0080–U+009F.

    Does NOT preserve ``\r`` — use ``normalize_newlines()`` before this
    function if ``\r`` needs to be converted rather than stripped.
    """
    return _CONTROL_CHAR_RE.sub("", text)


def clean_text(text: str) -> str:
    """Apply the full safe normalization pipeline.

    Pipeline order (each step feeds into the next)::

        strip_control_chars  →  remove dangerous control chars
        normalize_newlines   →  unify line endings to \\n
        normalize_unicode    →  NFC composition
        normalize_whitespace →  per-line horizontal cleanup

    This is the recommended default entry point for cleaning raw text.
    """
    text = strip_control_chars(text)
    text = normalize_newlines(text)
    text = normalize_unicode(text)
    text = normalize_whitespace(text)
    return text


def is_probably_broken_text(text: str) -> bool:
    """Heuristic check for obviously corrupted or garbage text.

    Returns ``True`` if the text shows signs of encoding corruption:
    - High ratio of Unicode replacement characters (U+FFFD)
    - Excessive non-printable / control character density

    This is a quick sanity check, not a comprehensive validator.
    Clean Turkish text will always return ``False``.
    """
    if not text:
        return False

    length = len(text)

    # Count replacement characters (U+FFFD) — strong signal of encoding failure
    replacement_count = text.count("\ufffd")
    if replacement_count > 0 and replacement_count / length > 0.05:
        return True

    # Count non-printable characters (excluding normal whitespace)
    non_printable = sum(
        1
        for ch in text
        if not ch.isprintable() and ch not in ("\n", "\t", "\r")
    )
    return non_printable > 0 and non_printable / length > 0.10
