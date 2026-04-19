"""Configuration system for Lex Study Foundation.

Two layers:
    1. ``Settings`` — environment variables + secrets (from .env)
    2. Domain configs — YAML files validated by Pydantic schemas
"""

from lex_study_foundation.config.settings import Settings

__all__ = ["Settings"]
