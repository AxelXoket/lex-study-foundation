"""Tests for the shared text-normalization layer."""

from __future__ import annotations

import unicodedata

from lex_study_foundation.utils.text import (
    clean_text,
    is_probably_broken_text,
    normalize_newlines,
    normalize_unicode,
    normalize_whitespace,
    strip_control_chars,
)

# ── Turkish test constants ──────────────────────────────────────────────────

TURKISH_LOWER = "çğıöşü"
TURKISH_UPPER = "ÇĞİÖŞÜ"
TURKISH_SENTENCE = "Türkiye Cumhuriyeti Anayasası'nın 10. maddesi eşitlik ilkesini düzenler."


# ── normalize_unicode ───────────────────────────────────────────────────────


class TestNormalizeUnicode:
    """NFC normalization tests."""

    def test_already_nfc_is_idempotent(self) -> None:
        """Text already in NFC form should pass through unchanged."""
        text = "Türkçe metin: çğıöşü ÇĞİÖŞÜ"
        assert normalize_unicode(text) == text

    def test_nfd_input_becomes_nfc(self) -> None:
        """NFD-decomposed text should be composed to NFC."""
        # ö as NFD: o + combining diaeresis (U+0308)
        nfd_text = unicodedata.normalize("NFD", "ö")
        assert len(nfd_text) == 2  # base + combining
        result = normalize_unicode(nfd_text)
        assert result == "ö"
        assert len(result) == 1  # single precomposed char

    def test_turkish_chars_survive(self) -> None:
        """All Turkish-specific characters must survive normalization."""
        result = normalize_unicode(TURKISH_LOWER + TURKISH_UPPER)
        assert result == TURKISH_LOWER + TURKISH_UPPER


# ── normalize_whitespace ────────────────────────────────────────────────────


class TestNormalizeWhitespace:
    """Per-line whitespace normalization tests."""

    def test_multiple_spaces_collapse(self) -> None:
        """Multiple consecutive spaces should become a single space."""
        assert normalize_whitespace("hello   world") == "hello world"

    def test_tabs_and_spaces_collapse(self) -> None:
        """Mixed tabs and spaces should collapse to a single space."""
        assert normalize_whitespace("hello \t\t  world") == "hello world"

    def test_leading_trailing_stripped(self) -> None:
        """Leading and trailing whitespace on each line should be stripped."""
        assert normalize_whitespace("  hello  ") == "hello"

    def test_consecutive_blank_lines_preserved(self) -> None:
        """Consecutive blank lines must be preserved, not collapsed."""
        text = "line one\n\n\nline two"
        result = normalize_whitespace(text)
        assert result == "line one\n\n\nline two"

    def test_multiline_per_line_processing(self) -> None:
        """Each line should be processed independently."""
        text = "  line  one  \n  line  two  "
        result = normalize_whitespace(text)
        assert result == "line one\nline two"


# ── normalize_newlines ──────────────────────────────────────────────────────


class TestNormalizeNewlines:
    """Line ending normalization tests."""

    def test_crlf_to_lf(self) -> None:
        r"""Windows \r\n should become \n."""
        assert normalize_newlines("line1\r\nline2") == "line1\nline2"

    def test_standalone_cr_to_lf(self) -> None:
        r"""Standalone \r should become \n."""
        assert normalize_newlines("line1\rline2") == "line1\nline2"

    def test_lf_preserved(self) -> None:
        r"""Unix \n should pass through unchanged."""
        text = "line1\nline2\nline3"
        assert normalize_newlines(text) == text

    def test_windows_crlf_roundtrip(self) -> None:
        r"""Text with \r\n should normalize to \n only."""
        windows_text = "Madde 1\r\nMadde 2\r\nMadde 3\r\n"
        result = normalize_newlines(windows_text)
        assert "\r" not in result
        assert result == "Madde 1\nMadde 2\nMadde 3\n"


# ── strip_control_chars ─────────────────────────────────────────────────────


class TestStripControlChars:
    """Control character stripping tests."""

    def test_removes_null_byte(self) -> None:
        """Null bytes (U+0000) should be removed."""
        assert strip_control_chars("hello\x00world") == "helloworld"

    def test_removes_bell_and_backspace(self) -> None:
        """Bell (U+0007) and backspace (U+0008) should be removed."""
        assert strip_control_chars("test\x07\x08text") == "testtext"

    def test_preserves_newline(self) -> None:
        r"""\n must be preserved."""
        assert strip_control_chars("line1\nline2") == "line1\nline2"

    def test_preserves_tab(self) -> None:
        r"""\t must be preserved."""
        assert strip_control_chars("col1\tcol2") == "col1\tcol2"

    def test_removes_c1_controls(self) -> None:
        """C1 control characters (U+0080–U+009F) should be removed."""
        # U+0085 (NEXT LINE), U+008A, U+008D
        text = "test\x85\x8a\x8dtext"
        assert strip_control_chars(text) == "testtext"


# ── clean_text ──────────────────────────────────────────────────────────────


class TestCleanText:
    """Full pipeline tests."""

    def test_pipeline_produces_expected_output(self) -> None:
        """The full clean pipeline should handle a messy input correctly."""
        messy = "  Hukuk \x07  fakültesi  \r\n  öğrencileri  "
        result = clean_text(messy)
        assert result == "Hukuk fakültesi\nöğrencileri"

    def test_already_clean_text_unchanged(self) -> None:
        """Already clean Turkish text should pass through without changes."""
        text = TURKISH_SENTENCE
        assert clean_text(text) == text

    def test_turkish_chars_survive_full_pipeline(self) -> None:
        """All Turkish characters must survive the complete pipeline."""
        text = f"Küçük: {TURKISH_LOWER} Büyük: {TURKISH_UPPER}"
        result = clean_text(text)
        assert TURKISH_LOWER in result
        assert TURKISH_UPPER in result


# ── is_probably_broken_text ─────────────────────────────────────────────────


class TestIsProbablyBrokenText:
    """Broken text detection tests."""

    def test_garbage_with_replacement_chars(self) -> None:
        """Text with many U+FFFD should be detected as broken."""
        broken = "\ufffd" * 10 + "hello"
        assert is_probably_broken_text(broken) is True

    def test_clean_turkish_not_broken(self) -> None:
        """Clean Turkish text must NOT be flagged as broken."""
        assert is_probably_broken_text(TURKISH_SENTENCE) is False

    def test_empty_string_not_broken(self) -> None:
        """Empty string should not be flagged as broken."""
        assert is_probably_broken_text("") is False

    def test_high_control_char_density_is_broken(self) -> None:
        """Text dominated by control characters should be flagged."""
        broken = "\x00\x01\x02\x03\x04\x05\x06\x07\x08" + "ab"
        assert is_probably_broken_text(broken) is True
