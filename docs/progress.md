# Progress Log

---

## 2026-04-15 (Tuesday) - 21:30

### Phase 1: Skeleton Structure ✅

Project foundation built from scratch. No code migrated from old project.

**What was done:**
- Initialized repo with `src/lex_study_foundation/` package layout
- CLI entrypoint via Typer - 4 working commands (`doctor`, `info`, `paths`, `validate-config`) + 8 stubs for future phases
- Config system - Pydantic Settings for `.env` secrets, Pydantic schemas for YAML validation
- Utility modules - Rich console with Windows UTF-8 fix, project path resolution, safe GPU detection
- Data schemas - `Tier` (StrEnum with token budgets), `Message`, `TrainingExample`
- YAML configs - generation config (general Turkish educational), training config (pilot LoRA)
- Quality gates - Ruff (lint/format), Pyright (types), pre-commit hooks, gitleaks (secret scanning)
- Test suite - 12 smoke tests, all passing
- BAT wrappers - `setup_env.bat`, `run.bat` (thin, no logic)
- Documentation - README, architecture quick-reference

**Verification:**
- `pytest` → 12/12 pass
- `ruff check` → clean
- `python -m lex_study_foundation doctor` → functional
- All CLI commands responsive

**Stack:** Python 3.12 (originally built on 3.14, migrated to 3.12.10 in Phase 2.5), Typer, Rich, Pydantic v2, PyYAML, Hatchling, Ruff, Pytest

---

## 2026-04-19 (Saturday) - Phase 2: Behavioral Spec & Utility Foundation

### Phase 2a: Behavioral Specification 🔒

Behavioral specification locked. Defines the target model personality for university-level
law students (1st-4th year). Covers tone, empathy boundaries, teaching flexibility,
precision profile, Turkish clarity, uncertainty behavior, and dataset reflection principle.

This document is the Phase 2 reference baseline for all later data-generation decisions.

### Phase 2b: Utility Foundation ✅

Shared text-normalization and JSONL/IO layers built, tested, and verified.

**What was done:**
- `utils/text.py` - NFC Unicode normalization, per-line whitespace cleanup, newline normalization, control char stripping, broken-text detection. All Turkish-safe, no case-folding.
- `utils/io.py` - JSONL read (generator, strict/permissive), write, append, atomic write via tempfile+os.replace (Windows-safe). Custom `JsonlReadError` exception. Shared `_dump_json_line()` helper.
- `tests/test_text.py` - 24 tests covering normalization stability, Turkish preservation, Windows `\r\n` roundtrip, broken text detection.
- `tests/test_io.py` - 18 tests covering JSONL roundtrip, Turkish content, ensure_ascii=False, atomic writes, malformed handling, edge cases.
- JSONL rules adopted: UTF-8, no BOM, `ensure_ascii=False`, `allow_nan=False`, trailing newline, strict-by-default.

**Verification:**
- `pytest` → 54/54 pass
- `ruff check` → clean
- All CLI commands still responsive
- Turkish characters survive full read/write roundtrip
- Atomic writes work correctly on Windows

---

## 2026-04-22 (Tuesday) - 02:30 - ml-intern Companion Dashboard

### Separate Repo: `ml-intern` - Hardened Architecture ✅

`ml-intern` companion dashboard restructured from scratch. Migrated from a flat `app/` + `pip`
layout to a properly packaged, security-hardened, `uv`-based project with strict repo boundaries.

**What was done:**
- `app/` → `src/ml_intern/` package layout (hatchling, `src/` layout)
- Frontend assets moved inside the package (`src/ml_intern/static/`)
- `pyproject.toml` created - CLI entry point: `ml-intern serve` (Typer, subcommand-based)
- `uv sync` + `uv tool install -e .` - both dev and global CLI paths verified
- `git init` + `.gitignore` - `.env`, `.venv`, caches, session artifacts excluded
- **Split settings:** `IntegrationSettings` (lex connection) + `ResearchProviderSettings` (ml-intern tokens) - same `.env`, clean conceptual boundary
- **Deterministic `.env` loading:** resolved from package location via `Path(__file__)`, never CWD-dependent. `ML_INTERN_ENV_FILE` override supported.
- **Subprocess env allowlist:** removed `os.environ.copy()` → only OS runtime vars forwarded. Provider secrets (Anthropic, HF, GitHub, Gemini, OpenAI) protected via **deny list** - raises `RuntimeError` if detected.
- **Secret redaction:** regex-based pattern matching applied to all output, errors, session summaries
- **Process kill on cancel:** `process.kill()` + `await process.wait()` - no orphan process risk
- **Output buffer cap:** max 5000 lines per job
- **Health state:** `healthy` / `degraded` / `unavailable` enum + `research_status` (disabled/unconfigured/available)
- **PYTHONPATH test:** lex CLI runs successfully without PYTHONPATH injection - editable install `.pth` mechanism is sufficient
- **Secret boundary docs:** fully documented in README - which secrets belong where, what is never forwarded, and why

**Security decisions:**
- ml-intern secrets (Anthropic, HF, GitHub) → belong to ml-intern only, NEVER forwarded to lex subprocesses
- lex secrets (Gemini) → belong to lex only, lex CLI loads from its own `.env`, ml-intern does not inject
- `RuntimeError` instead of `assert` - prevents security bypass in Python optimized mode
- Research mode in V1 is infrastructure/feature-flag only, no real provider-backed features yet

**Verification:**
- `uv sync` → 27 packages, successful
- `uv run ml-intern serve` → dashboard loads, Connected status, doctor command executes
- `uv tool install -e .` → `ml-intern` command works globally
- `ml-intern` → shows help, `ml-intern serve` → starts server
- `.env` not staged in git, `.venv` not staged - hygiene clean
- Subprocess succeeds without PYTHONPATH

**Stack:** Python 3.12 (originally built on 3.14, migrated to 3.12.10 in Phase 2.5), FastAPI, Uvicorn, Typer, Pydantic v2, pydantic-settings, Hatchling, uv

---
