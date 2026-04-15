"""Configuration system for Project Blank.

Two layers:
    1. ``Settings`` — environment variables + secrets (from .env)
    2. Domain configs — YAML files validated by Pydantic schemas
"""

from project_blank.config.settings import Settings

__all__ = ["Settings"]
