"""Environment-based settings loaded from .env via pydantic-settings.

This is the ONLY place in the codebase that reads environment variables
or secret values. All other modules receive settings through dependency
injection or by importing ``get_settings()``.

Usage::

    from project_blank.config.settings import get_settings

    settings = get_settings()
    print(settings.active_provider)
    print(settings.base_model)
"""

from __future__ import annotations

import logging
from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from project_blank.utils.paths import PROJECT_ROOT

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Application settings loaded from environment / .env file.

    Secrets are stored as plain strings here because they are API keys
    used in HTTP headers, not passwords. ``SecretStr`` would add friction
    without meaningful security benefit in this context.
    """

    model_config = SettingsConfigDict(
        env_file=str(PROJECT_ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",  # Don't crash on unknown env vars
        case_sensitive=False,
    )

    # ── API keys ────────────────────────────────────────────────────────
    gemini_api_key: str = Field(
        default="",
        description="Comma-separated Gemini API keys for rotation",
    )
    openai_api_key: str = Field(
        default="",
        description="OpenAI API key",
    )

    # ── Provider ────────────────────────────────────────────────────────
    active_provider: Literal["gemini", "openai"] = Field(
        default="gemini",
        description="Which LLM provider to use for data generation",
    )

    # ── Model ───────────────────────────────────────────────────────────
    base_model: str = Field(
        default="mistralai/Mistral-7B-Instruct-v0.3",
        description="HuggingFace model ID or local path for the base model",
    )

    # ── Logging ─────────────────────────────────────────────────────────
    log_level: str = Field(
        default="INFO",
        description="Python logging level",
    )

    # ── Validators ──────────────────────────────────────────────────────
    @field_validator("log_level")
    @classmethod
    def _normalize_log_level(cls, v: str) -> str:
        v = v.upper()
        valid = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if v not in valid:
            logger.warning("Invalid LOG_LEVEL '%s', defaulting to INFO", v)
            return "INFO"
        return v

    # ── Derived helpers ─────────────────────────────────────────────────
    @property
    def gemini_keys(self) -> list[str]:
        """Parse comma-separated Gemini keys into a list."""
        if not self.gemini_api_key:
            return []
        return [k.strip() for k in self.gemini_api_key.split(",") if k.strip()]

    @property
    def has_api_keys(self) -> bool:
        """Check if at least one API key is configured."""
        return bool(self.gemini_keys or self.openai_api_key)

    @property
    def env_file_exists(self) -> bool:
        """Check if .env file is present."""
        return Path(self.model_config.get("env_file", "")).is_file()


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Cached singleton for settings. Call this, don't instantiate directly."""
    return Settings()
