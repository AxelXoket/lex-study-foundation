"""Data pipeline modules.

Stages:
    1. Seeds        — curated seed questions (data/seeds/)
    2. Generation   — synthetic data via LLM APIs (data/raw/)
    3. Validation   — quality checks + safety filtering
    4. Dedup        — exact hash + semantic deduplication (data/processed/)
    5. Formatting   — convert to training format (data/training/)

Implementation status: Phase 1 stubs only. Real logic arrives in Phase 3.
"""
