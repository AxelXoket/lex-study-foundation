"""Shared test fixtures."""

from __future__ import annotations

import pytest


@pytest.fixture
def clean_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Clear all project-related env vars for a clean test environment."""
    for var in [
        "GEMINI_API_KEY",
        "BASE_MODEL",
        "LOG_LEVEL",
    ]:
        monkeypatch.delenv(var, raising=False)
