"""Project path resolution.

All path logic lives here so that no other module does its own
``Path(__file__).parent.parent...`` gymnastics.

Directory layout::

    project_root/
    ├── configs/          User-facing YAML configs
    ├── data/
    │   ├── seeds/        Curated seed questions
    │   ├── raw/          Raw generated data
    │   ├── processed/    After validation + dedup
    │   ├── training/     Final training-ready JSONL
    │   ├── evaluation/   Eval prompt sets + results
    │   └── cache/        SQLite persistent cache
    ├── runs/             Training run outputs
    └── models/           Exported models
"""

from __future__ import annotations

from pathlib import Path


def _find_project_root() -> Path:
    """Walk up from this file to find the directory containing pyproject.toml."""
    current = Path(__file__).resolve()
    for parent in [current, *current.parents]:
        if (parent / "pyproject.toml").is_file():
            return parent
    # Fallback: assume src/lex_study_foundation/utils/paths.py → 4 levels up
    return current.parent.parent.parent.parent


# ── Root ────────────────────────────────────────────────────────────────────
PROJECT_ROOT: Path = _find_project_root()

# ── Config ──────────────────────────────────────────────────────────────────
CONFIGS_DIR: Path = PROJECT_ROOT / "configs"

# ── Data pipeline stages ────────────────────────────────────────────────────
DATA_DIR: Path = PROJECT_ROOT / "data"
SEEDS_DIR: Path = DATA_DIR / "seeds"
RAW_DIR: Path = DATA_DIR / "raw"
PROCESSED_DIR: Path = DATA_DIR / "processed"
TRAINING_DIR: Path = DATA_DIR / "training"
EVAL_DIR: Path = DATA_DIR / "evaluation"
BENCHMARK_DIR: Path = EVAL_DIR / "benchmarks"
CACHE_DIR: Path = DATA_DIR / "cache"

# ── Outputs ─────────────────────────────────────────────────────────────────
RUNS_DIR: Path = PROJECT_ROOT / "runs"
MODELS_DIR: Path = PROJECT_ROOT / "models"


def ensure_dirs() -> None:
    """Create all expected directories if they don't exist."""
    for d in [
        SEEDS_DIR,
        RAW_DIR,
        PROCESSED_DIR,
        TRAINING_DIR,
        BENCHMARK_DIR,
        CACHE_DIR,
        RUNS_DIR,
        MODELS_DIR,
    ]:
        d.mkdir(parents=True, exist_ok=True)


def get_all_paths() -> dict[str, str]:
    """Return a name → absolute path mapping for display."""
    return {
        "project_root": str(PROJECT_ROOT),
        "configs": str(CONFIGS_DIR),
        "data": str(DATA_DIR),
        "  seeds": str(SEEDS_DIR),
        "  raw": str(RAW_DIR),
        "  processed": str(PROCESSED_DIR),
        "  training": str(TRAINING_DIR),
        "  evaluation": str(EVAL_DIR),
        "  cache": str(CACHE_DIR),
        "runs": str(RUNS_DIR),
        "models": str(MODELS_DIR),
    }
