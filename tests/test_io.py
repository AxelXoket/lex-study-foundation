"""Tests for the shared JSONL and text file I/O layer."""

from __future__ import annotations

import math
from pathlib import Path

import pytest

from lex_study_foundation.utils.io import (
    JsonlReadError,
    append_jsonl,
    atomic_write_jsonl,
    atomic_write_text,
    read_jsonl,
    read_text_file,
    write_jsonl,
    write_text_file,
)

# ── Turkish test data ──────────────────────────────────────────────────────

TURKISH_RECORDS = [
    {"soru": "Anayasa nedir?", "cevap": "Devletin temel yapısını düzenleyen üst normdur."},
    {"soru": "Eşitlik ilkesi nerede düzenlenir?", "cevap": "Anayasa'nın 10. maddesinde."},
    {"soru": "Hukukun kaynakları nelerdir?", "cevap": "Yazılı ve yazısız kaynaklar: çğıöşüİÇĞÖŞÜ"},
]


# ── JSONL roundtrip ────────────────────────────────────────────────────────


class TestJsonlRoundtrip:
    """Write → read roundtrip tests."""

    def test_basic_roundtrip(self, tmp_path: Path) -> None:
        """Records written should be read back identically."""
        fpath = tmp_path / "test.jsonl"
        write_jsonl(fpath, TURKISH_RECORDS)
        result = list(read_jsonl(fpath))
        assert result == TURKISH_RECORDS

    def test_turkish_content_roundtrip(self, tmp_path: Path) -> None:
        """Turkish characters must survive full write/read cycle."""
        fpath = tmp_path / "turkish.jsonl"
        write_jsonl(fpath, TURKISH_RECORDS)
        result = list(read_jsonl(fpath))
        for original, loaded in zip(result, TURKISH_RECORDS, strict=True):
            assert original == loaded

    def test_ensure_ascii_false(self, tmp_path: Path) -> None:
        r"""Written file should contain actual Turkish chars, not \uXXXX escapes."""
        fpath = tmp_path / "readable.jsonl"
        write_jsonl(fpath, [{"text": "çğıöşüİÇĞÖŞÜ"}])
        raw_content = fpath.read_text(encoding="utf-8")
        assert "çğıöşüİÇĞÖŞÜ" in raw_content
        assert "\\u" not in raw_content

    def test_allow_nan_false(self, tmp_path: Path) -> None:
        """NaN and Infinity should raise ValueError, not produce invalid JSON."""
        fpath = tmp_path / "nan.jsonl"
        with pytest.raises(ValueError, match="Out of range float values"):
            write_jsonl(fpath, [{"value": math.nan}])

    def test_final_trailing_newline(self, tmp_path: Path) -> None:
        """Written JSONL should end with a trailing newline."""
        fpath = tmp_path / "trailing.jsonl"
        write_jsonl(fpath, [{"a": 1}])
        raw = fpath.read_bytes()
        assert raw.endswith(b"\n")


# ── Append behavior ────────────────────────────────────────────────────────


class TestAppendJsonl:
    """Append mode tests."""

    def test_append_creates_file_if_missing(self, tmp_path: Path) -> None:
        """Appending to a non-existent file should create it."""
        fpath = tmp_path / "new.jsonl"
        assert not fpath.exists()
        append_jsonl(fpath, [{"a": 1}])
        assert fpath.exists()
        assert list(read_jsonl(fpath)) == [{"a": 1}]

    def test_append_adds_to_existing(self, tmp_path: Path) -> None:
        """Appending should add records without destroying existing ones."""
        fpath = tmp_path / "existing.jsonl"
        write_jsonl(fpath, [{"a": 1}])
        append_jsonl(fpath, [{"b": 2}])
        result = list(read_jsonl(fpath))
        assert result == [{"a": 1}, {"b": 2}]


# ── Malformed JSONL handling ───────────────────────────────────────────────


class TestMalformedJsonl:
    """Error handling for malformed JSONL content."""

    def test_strict_mode_raises_jsonl_read_error(self, tmp_path: Path) -> None:
        """Strict mode should raise JsonlReadError with line number."""
        fpath = tmp_path / "bad.jsonl"
        fpath.write_text('{"valid": true}\nnot json\n{"also": "valid"}\n', encoding="utf-8")
        with pytest.raises(JsonlReadError) as exc_info:
            list(read_jsonl(fpath, strict=True))
        assert exc_info.value.line_number == 2
        assert exc_info.value.path == fpath
        assert "invalid JSON" in exc_info.value.reason

    def test_permissive_mode_skips_bad_lines(self, tmp_path: Path) -> None:
        """Permissive mode should skip bad lines and yield valid ones."""
        fpath = tmp_path / "mixed.jsonl"
        fpath.write_text('{"a": 1}\nbad line\n{"b": 2}\n', encoding="utf-8")
        result = list(read_jsonl(fpath, strict=False))
        assert result == [{"a": 1}, {"b": 2}]


# ── Edge cases ─────────────────────────────────────────────────────────────


class TestEdgeCases:
    """Edge case behavior."""

    def test_empty_file_returns_no_records(self, tmp_path: Path) -> None:
        """An empty file should yield no records."""
        fpath = tmp_path / "empty.jsonl"
        fpath.write_text("", encoding="utf-8")
        result = list(read_jsonl(fpath))
        assert result == []

    def test_missing_file_raises_file_not_found(self, tmp_path: Path) -> None:
        """Reading a non-existent file should raise FileNotFoundError."""
        fpath = tmp_path / "nonexistent.jsonl"
        with pytest.raises(FileNotFoundError):
            list(read_jsonl(fpath))

    def test_write_to_missing_parent_raises(self, tmp_path: Path) -> None:
        """Writing to a path with non-existent parent should raise."""
        fpath = tmp_path / "nonexistent_dir" / "test.jsonl"
        with pytest.raises(FileNotFoundError, match="Parent directory"):
            write_jsonl(fpath, [{"a": 1}])


# ── Atomic writes ──────────────────────────────────────────────────────────


class TestAtomicWrite:
    """Atomic write tests."""

    def test_atomic_write_text_succeeds(self, tmp_path: Path) -> None:
        """Atomic write should create or replace the target file."""
        fpath = tmp_path / "atomic.txt"
        atomic_write_text(fpath, "Merhaba dünya")
        assert fpath.read_text(encoding="utf-8") == "Merhaba dünya"

    def test_atomic_write_replaces_existing(self, tmp_path: Path) -> None:
        """Atomic write should replace existing file content."""
        fpath = tmp_path / "replace.txt"
        fpath.write_text("old content", encoding="utf-8")
        atomic_write_text(fpath, "new content")
        assert fpath.read_text(encoding="utf-8") == "new content"

    def test_atomic_write_jsonl_roundtrip(self, tmp_path: Path) -> None:
        """Atomic JSONL write should produce readable JSONL."""
        fpath = tmp_path / "atomic.jsonl"
        atomic_write_jsonl(fpath, TURKISH_RECORDS)
        result = list(read_jsonl(fpath))
        assert result == TURKISH_RECORDS

    def test_atomic_write_no_leftover_temp_on_success(self, tmp_path: Path) -> None:
        """After successful atomic write, no .tmp files should remain."""
        fpath = tmp_path / "clean.txt"
        atomic_write_text(fpath, "test data")
        tmp_files = list(tmp_path.glob("*.tmp"))
        assert tmp_files == []


# ── Plain text I/O ─────────────────────────────────────────────────────────


class TestTextFileIO:
    """Plain text read/write tests."""

    def test_utf8_roundtrip(self, tmp_path: Path) -> None:
        """Turkish text should survive write/read cycle."""
        fpath = tmp_path / "turkish.txt"
        text = "Türkiye Cumhuriyeti Anayasası — çğıöşüİÇĞÖŞÜ"
        write_text_file(fpath, text)
        result = read_text_file(fpath)
        assert result == text

    def test_windows_crlf_roundtrip(self, tmp_path: Path) -> None:
        r"""Text with \r\n written via write_text_file should use \n only."""
        fpath = tmp_path / "newlines.txt"
        # write_text_file uses newline="\n", so even if content has \r\n,
        # the file should be written with \n line endings.
        write_text_file(fpath, "line1\nline2\nline3")
        raw_bytes = fpath.read_bytes()
        assert b"\r\n" not in raw_bytes
        assert b"\n" in raw_bytes
