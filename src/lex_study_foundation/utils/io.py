"""Shared JSONL and text file I/O layer.

All file reading/writing in the project should go through this module
to guarantee consistent encoding, format, and error behavior.

Design principles:
- UTF-8 only, no BOM
- JSONL: one valid JSON value per line, newline-delimited
- ``ensure_ascii=False`` for readable Turkish output
- ``allow_nan=False`` for strict JSON compliance
- Strict mode by default; permissive mode is opt-in
- Atomic writes via tempfile + os.replace for safe full-rewrites
- Append logic is completely separate from rewrite logic
- pathlib.Path throughout

Usage::

    from lex_study_foundation.utils.io import read_jsonl, write_jsonl, atomic_write_jsonl

    records = list(read_jsonl("data/raw/output.jsonl"))
    write_jsonl("data/processed/clean.jsonl", records)
"""

from __future__ import annotations

import contextlib
import json
import logging
import os
import tempfile
from collections.abc import Iterator
from pathlib import Path
from typing import Any

__all__ = [
    "JsonlReadError",
    "append_jsonl",
    "atomic_write_jsonl",
    "atomic_write_text",
    "read_jsonl",
    "read_text_file",
    "write_jsonl",
    "write_text_file",
]

logger = logging.getLogger(__name__)


# ── Custom exception ───────────────────────────────────────────────────────


class JsonlReadError(Exception):
    """Raised when a JSONL file contains a malformed line in strict mode.

    Attributes:
        path: The file path being read.
        line_number: 1-indexed line number of the malformed line.
        reason: Short description of what went wrong.
    """

    def __init__(self, path: Path, line_number: int, reason: str) -> None:
        self.path = path
        self.line_number = line_number
        self.reason = reason
        super().__init__(f"{path}:{line_number}: {reason}")


# ── Internal helpers ────────────────────────────────────────────────────────


def _dump_json_line(record: Any) -> str:
    """Serialize a single record to a JSON string.

    Used by both ``write_jsonl`` and ``atomic_write_jsonl`` to guarantee
    identical serialization rules everywhere.
    """
    return json.dumps(record, ensure_ascii=False, allow_nan=False)


def _validate_parent_dir(path: Path) -> None:
    """Raise FileNotFoundError if the parent directory does not exist."""
    parent = path.parent
    if not parent.is_dir():
        msg = f"Parent directory does not exist: {parent}"
        raise FileNotFoundError(msg)


# ── JSONL I/O ──────────────────────────────────────────────────────────────


def read_jsonl(path: str | Path, *, strict: bool = True) -> Iterator[dict[str, Any]]:
    """Read a JSONL file, yielding one parsed dict per line.

    Args:
        path: Path to the JSONL file.
        strict: If True (default), raise ``JsonlReadError`` on any malformed
            line. If False, skip malformed lines and log a warning.

    Yields:
        Parsed dict for each valid JSON line.

    Raises:
        FileNotFoundError: If the file does not exist.
        JsonlReadError: If strict=True and a line is malformed.
    """
    path = Path(path)
    if not path.is_file():
        msg = f"File not found: {path}"
        raise FileNotFoundError(msg)

    with path.open("r", encoding="utf-8") as fh:
        for line_number, raw_line in enumerate(fh, start=1):
            line = raw_line.strip()
            if not line:
                # Skip blank lines (not valid JSONL records)
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError as exc:
                if strict:
                    raise JsonlReadError(
                        path=path,
                        line_number=line_number,
                        reason=f"invalid JSON: {exc}",
                    ) from exc
                logger.warning("%s:%d: skipped — invalid JSON: %s", path, line_number, exc)


def write_jsonl(path: str | Path, records: list[dict[str, Any]]) -> None:
    """Write records to a JSONL file (full rewrite).

    Creates the file if it does not exist. Overwrites if it does.
    Writes a final trailing newline.

    Args:
        path: Target file path.
        records: List of dicts to serialize.

    Raises:
        FileNotFoundError: If the parent directory does not exist.
    """
    path = Path(path)
    _validate_parent_dir(path)

    with path.open("w", encoding="utf-8", newline="\n") as fh:
        for record in records:
            fh.write(_dump_json_line(record))
            fh.write("\n")


def append_jsonl(path: str | Path, records: list[dict[str, Any]]) -> None:
    """Append records to a JSONL file.

    Creates the file if it does not exist. Appends to existing content
    if it does. Each record is written on its own line.

    Args:
        path: Target file path.
        records: List of dicts to serialize and append.

    Raises:
        FileNotFoundError: If the parent directory does not exist.
    """
    path = Path(path)
    _validate_parent_dir(path)

    with path.open("a", encoding="utf-8", newline="\n") as fh:
        for record in records:
            fh.write(_dump_json_line(record))
            fh.write("\n")


# ── Plain text I/O ─────────────────────────────────────────────────────────


def read_text_file(path: str | Path) -> str:
    """Read a text file as UTF-8 and return its content.

    Args:
        path: Path to the text file.

    Raises:
        FileNotFoundError: If the file does not exist.
    """
    path = Path(path)
    if not path.is_file():
        msg = f"File not found: {path}"
        raise FileNotFoundError(msg)

    return path.read_text(encoding="utf-8")


def write_text_file(path: str | Path, text: str) -> None:
    """Write text to a file as UTF-8 (full rewrite).

    Args:
        path: Target file path.
        text: Content to write.

    Raises:
        FileNotFoundError: If the parent directory does not exist.
    """
    path = Path(path)
    _validate_parent_dir(path)

    with path.open("w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)


# ── Atomic writes ──────────────────────────────────────────────────────────


def atomic_write_text(path: str | Path, text: str) -> None:
    """Atomically write text to a file.

    Writes to a temporary file in the same directory, then replaces the
    target file. This ensures the target is never left in a partial state.

    On Windows, the temp file is explicitly closed before ``os.replace()``
    to avoid file-locking issues with ``NamedTemporaryFile``.

    Args:
        path: Target file path.
        text: Content to write.

    Raises:
        FileNotFoundError: If the parent directory does not exist.
    """
    path = Path(path)
    _validate_parent_dir(path)

    # Create temp file in the same directory (same filesystem for os.replace)
    fd = tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        newline="\n",
        dir=path.parent,
        suffix=".tmp",
        delete=False,
    )
    temp_path = fd.name
    try:
        fd.write(text)
        fd.flush()
        os.fsync(fd.fileno())
        fd.close()  # MUST close before os.replace on Windows
        os.replace(temp_path, path)
    except BaseException:
        fd.close()
        # Clean up the temp file on any failure
        with contextlib.suppress(OSError):
            os.unlink(temp_path)
        raise


def atomic_write_jsonl(path: str | Path, records: list[dict[str, Any]]) -> None:
    """Atomically write JSONL records to a file.

    Same atomic pattern as ``atomic_write_text``: writes to a temp file
    and replaces the target only after successful write. Uses the shared
    ``_dump_json_line()`` helper for consistent serialization.

    Args:
        path: Target file path.
        records: List of dicts to serialize.

    Raises:
        FileNotFoundError: If the parent directory does not exist.
    """
    path = Path(path)
    _validate_parent_dir(path)

    fd = tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        newline="\n",
        dir=path.parent,
        suffix=".tmp",
        delete=False,
    )
    temp_path = fd.name
    try:
        for record in records:
            fd.write(_dump_json_line(record))
            fd.write("\n")
        fd.flush()
        os.fsync(fd.fileno())
        fd.close()  # MUST close before os.replace on Windows
        os.replace(temp_path, path)
    except BaseException:
        fd.close()
        with contextlib.suppress(OSError):
            os.unlink(temp_path)
        raise
