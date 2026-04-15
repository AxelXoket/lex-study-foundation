"""Domain configuration schemas loaded from YAML files.

These schemas define the structure of user-facing config YAML files
in the ``configs/`` directory. They are validated at load time so that
errors are caught before any expensive operations begin.

Usage::

    from project_blank.config.schemas import load_generation_config

    config = load_generation_config("configs/generation/general_turkish.yaml")
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field, field_validator

# ============================================================================
# Generation config
# ============================================================================

class TierConfig(BaseModel):
    """Token budgets per answer tier."""

    short: int = Field(default=180, ge=50, le=500)
    medium: int = Field(default=400, ge=100, le=800)
    long: int = Field(default=650, ge=200, le=1500)
    list: int = Field(default=450, ge=100, le=800)


class GenerationConfig(BaseModel):
    """Configuration for the data generation pipeline."""

    # Target
    target_count: int = Field(default=500, ge=10, le=100_000)
    domain: str = Field(default="general_educational")

    # Tiers
    tier_budgets: TierConfig = Field(default_factory=TierConfig)
    tier_weights: dict[str, float] = Field(
        default={"short": 0.20, "medium": 0.35, "long": 0.35, "list": 0.10},
    )

    # Worker settings
    parallel_workers: int = Field(default=20, ge=1, le=100)
    batch_size: int = Field(default=20, ge=1, le=100)

    # Provider
    provider: str = Field(default="gemini")
    model: str = Field(default="gemini-2.5-flash")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)

    # Search
    search_enabled: bool = Field(default=True)

    # Scenarios (pedagogical evolution scenarios, max 8)
    scenarios: list[str] = Field(default_factory=list)

    @field_validator("tier_weights")
    @classmethod
    def _check_weights_sum(cls, v: dict[str, float]) -> dict[str, float]:
        total = sum(v.values())
        if not (0.99 <= total <= 1.01):
            msg = f"Tier weights must sum to 1.0, got {total:.3f}"
            raise ValueError(msg)
        return v


# ============================================================================
# Training config
# ============================================================================

class LoraConfig(BaseModel):
    """LoRA / QLoRA adapter configuration."""

    r: int = Field(default=64, ge=4, le=256)
    alpha: int = Field(default=128, ge=4, le=512)
    dropout: float = Field(default=0.05, ge=0.0, le=0.5)
    target_modules: list[str] = Field(
        default=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
    )
    use_dora: bool = Field(default=False)


class TrainingConfig(BaseModel):
    """Configuration for LoRA fine-tuning."""

    # Model
    base_model: str = Field(default="mistralai/Mistral-7B-Instruct-v0.3")

    # Data
    data_path: str = Field(default="data/training/instruct.jsonl")
    max_seq_length: int = Field(default=768, ge=128, le=8192)
    eval_ratio: float = Field(default=0.05, ge=0.01, le=0.2)

    # Training
    epochs: float = Field(default=2.0, ge=0.1, le=20.0)
    learning_rate: float = Field(default=4e-5, ge=1e-6, le=1e-2)
    batch_size: int = Field(default=8, ge=1, le=64)
    gradient_accumulation: int = Field(default=2, ge=1, le=32)
    warmup_ratio: float = Field(default=0.05, ge=0.0, le=0.3)
    weight_decay: float = Field(default=0.01, ge=0.0, le=0.5)
    max_grad_norm: float = Field(default=0.3, ge=0.0, le=10.0)

    # Quantization
    use_4bit: bool = Field(default=True)

    # Quality boosts
    use_neftune: bool = Field(default=True)
    neftune_alpha: float = Field(default=5.0, ge=0.0, le=50.0)

    # Adapter
    lora: LoraConfig = Field(default_factory=LoraConfig)

    # Output
    output_dir: str = Field(default="runs/latest")

    @property
    def effective_batch_size(self) -> int:
        return self.batch_size * self.gradient_accumulation


# ============================================================================
# Loaders
# ============================================================================

def _load_yaml(path: str | Path) -> dict[str, Any]:
    """Load and return a YAML file as a dict."""
    p = Path(path)
    if not p.is_file():
        msg = f"Config file not found: {p}"
        raise FileNotFoundError(msg)
    with p.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        msg = f"Config file must contain a YAML mapping, got {type(data).__name__}"
        raise TypeError(msg)
    return data


def load_generation_config(path: str | Path) -> GenerationConfig:
    """Load and validate a generation config from YAML."""
    return GenerationConfig(**_load_yaml(path))


def load_training_config(path: str | Path) -> TrainingConfig:
    """Load and validate a training config from YAML."""
    return TrainingConfig(**_load_yaml(path))
