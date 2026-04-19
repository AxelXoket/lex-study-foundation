"""CLI entrypoint for Lex Study Foundation.

All commands are visible-console-first on Windows. No hidden subprocesses,
no ``pythonw``, no swallowed stdout/stderr. Progress, errors, and logs
are always printed to the active terminal.

Usage::

    python -m lex_study_foundation --help
    python -m lex_study_foundation doctor
    python -m lex_study_foundation paths
    python -m lex_study_foundation validate-config configs/generation/general_turkish.yaml

Or via the installed script::

    lex-study-foundation doctor
"""

from __future__ import annotations

import platform
import sys
from pathlib import Path

import typer
from rich.table import Table

from lex_study_foundation import __version__
from lex_study_foundation.utils.console import (
    console,
    path_tree,
    print_header,
    print_kv,
    status_table,
)
from lex_study_foundation.utils.paths import CONFIGS_DIR, ensure_dirs, get_all_paths

# ── Typer app ───────────────────────────────────────────────────────────────
app = typer.Typer(
    name="lex-study-foundation",
    help="Turkish Educational LLM Fine-Tuning System",
    no_args_is_help=True,
    rich_markup_mode="rich",
    add_completion=False,
)


# ============================================================================
# doctor — environment health check
# ============================================================================
@app.command()
def doctor() -> None:
    """Check environment health and report readiness status."""
    from lex_study_foundation.config.settings import get_settings
    from lex_study_foundation.utils.gpu import detect_gpu

    print_header("Lex Study Foundation — Doctor")
    checks: list[tuple[str, str, str]] = []

    # 1. Python version
    py_ver = platform.python_version()
    py_ok = sys.version_info >= (3, 11)
    checks.append((
        "Python ≥ 3.11",
        "✓" if py_ok else "✗",
        f"Python {py_ver}",
    ))

    # 2. Platform
    checks.append((
        "Platform",
        "ℹ",
        f"{platform.system()} {platform.release()} ({platform.machine()})",
    ))

    # 3. .env file
    settings = get_settings()
    checks.append((
        ".env file",
        "✓" if settings.env_file_exists else "⚠",
        "found" if settings.env_file_exists else "missing — copy .env.example to .env",
    ))

    # 4. API keys
    if settings.has_api_keys:
        checks.append(("API keys", "✓", f"Gemini: {len(settings.gemini_keys)} key(s)"))
    else:
        checks.append(("API keys", "⚠", "none configured — needed for data generation"))

    # 5. GPU
    gpu = detect_gpu()
    if gpu.available:
        checks.append((
            "GPU",
            "✓",
            f"{gpu.name} ({gpu.vram_total_gb} GB, {gpu.compute_capability})",
        ))
        checks.append(("CUDA", "ℹ", gpu.cuda_version))
        checks.append(("BF16", "ℹ", gpu.bf16_supported))
        checks.append(("PyTorch", "ℹ", gpu.torch_version))
    else:
        checks.append(("GPU", "⚠", gpu.name))
        checks.append(("PyTorch", "ℹ", gpu.torch_version))

    # 6. Project directories
    ensure_dirs()
    checks.append(("Project directories", "✓", "created / verified"))

    # 7. Config files
    gen_cfg = CONFIGS_DIR / "generation" / "general_turkish.yaml"
    train_cfg = CONFIGS_DIR / "training" / "pilot_lora.yaml"
    cfg_ok = gen_cfg.is_file() and train_cfg.is_file()
    checks.append((
        "Config files",
        "✓" if cfg_ok else "⚠",
        "found" if cfg_ok else "some config files missing",
    ))

    # Print results
    console.print()
    console.print(status_table(checks))
    console.print()

    # Summary
    errors = sum(1 for _, s, _ in checks if s == "✗")
    warnings = sum(1 for _, s, _ in checks if s == "⚠")
    if errors:
        console.print(f"  [error]{errors} error(s) must be fixed before proceeding.[/error]")
    elif warnings:
        console.print(f"  [warning]{warnings} warning(s) — non-blocking but worth addressing.[/warning]")
    else:
        console.print("  [success]All checks passed. Environment is ready.[/success]")
    console.print()


# ============================================================================
# info — project metadata
# ============================================================================
@app.command()
def info() -> None:
    """Print project metadata, version, and platform info."""
    print_header("Lex Study Foundation — Info")
    print_kv("Version", __version__)
    print_kv("Python", platform.python_version())
    print_kv("Platform", f"{platform.system()} {platform.release()}")
    print_kv("Architecture", platform.machine())
    print_kv("CLI framework", "Typer + Rich")
    print_kv("Config system", "Pydantic v2 + pydantic-settings")
    console.print()


# ============================================================================
# paths — show resolved project paths
# ============================================================================
@app.command()
def paths() -> None:
    """Print all resolved project directory paths."""
    print_header("Lex Study Foundation — Paths")
    console.print()
    console.print(path_tree(get_all_paths()))
    console.print()


# ============================================================================
# validate-config — load and validate a YAML config
# ============================================================================
@app.command("validate-config")
def validate_config(
    config_path: str = typer.Argument(help="Path to YAML config file"),
    config_type: str = typer.Option(
        "auto",
        "--type",
        "-t",
        help="Config type: 'generation', 'training', or 'auto' (infer from path)",
    ),
) -> None:
    """Load and validate a YAML config file against its schema."""
    from lex_study_foundation.config.schemas import load_generation_config, load_training_config

    print_header("Lex Study Foundation — Config Validation")

    p = Path(config_path)
    if not p.is_file():
        console.print(f"  [error]File not found: {p}[/error]")
        raise typer.Exit(1)

    # Auto-detect type from path
    if config_type == "auto":
        if "generation" in p.parts or "generation" in p.stem:
            config_type = "generation"
        elif "training" in p.parts or "training" in p.stem or "lora" in p.stem:
            config_type = "training"
        else:
            console.print("  [error]Cannot auto-detect config type. Use --type.[/error]")
            raise typer.Exit(1)

    try:
        if config_type == "generation":
            cfg = load_generation_config(p)
            console.print(f"  [success]✓ Valid generation config: {p.name}[/success]")
            console.print()

            table = Table(show_header=True, header_style="bold", padding=(0, 1))
            table.add_column("Parameter", style="key")
            table.add_column("Value", style="value")
            table.add_row("domain", cfg.domain)
            table.add_row("target_count", str(cfg.target_count))
            table.add_row("provider", cfg.provider)
            table.add_row("model", cfg.model)
            table.add_row("parallel_workers", str(cfg.parallel_workers))
            table.add_row("tier_budgets", str(cfg.tier_budgets.model_dump()))
            table.add_row("tier_weights", str(cfg.tier_weights))
            table.add_row("scenarios", str(len(cfg.scenarios)) + " defined")
            console.print(table)

        elif config_type == "training":
            cfg = load_training_config(p)
            console.print(f"  [success]✓ Valid training config: {p.name}[/success]")
            console.print()

            table = Table(show_header=True, header_style="bold", padding=(0, 1))
            table.add_column("Parameter", style="key")
            table.add_column("Value", style="value")
            table.add_row("base_model", cfg.base_model)
            table.add_row("data_path", cfg.data_path)
            table.add_row("max_seq_length", str(cfg.max_seq_length))
            table.add_row("epochs", str(cfg.epochs))
            table.add_row("learning_rate", str(cfg.learning_rate))
            table.add_row("effective_batch", str(cfg.effective_batch_size))
            table.add_row("lora_r", str(cfg.lora.r))
            table.add_row("lora_alpha", str(cfg.lora.alpha))
            table.add_row("use_dora", str(cfg.lora.use_dora))
            table.add_row("use_neftune", str(cfg.use_neftune))
            table.add_row("use_4bit", str(cfg.use_4bit))
            table.add_row("output_dir", cfg.output_dir)
            console.print(table)

        else:
            console.print(f"  [error]Unknown config type: {config_type}[/error]")
            raise typer.Exit(1)

    except FileNotFoundError as e:
        console.print(f"  [error]{e}[/error]")
        raise typer.Exit(1) from e
    except (ValueError, TypeError) as e:
        console.print(f"  [error]Validation failed: {e}[/error]")
        raise typer.Exit(1) from e

    console.print()


# ============================================================================
# Stubs — registered but not yet implemented
# ============================================================================

def _stub(name: str, phase: int) -> None:
    """Print a 'not yet implemented' message for a deferred command."""
    console.print(f"\n  [warning]⚠ '{name}' is not yet implemented. Target: Phase {phase}[/warning]\n")


@app.command()
def generate(
    config: str | None = typer.Option(None, "--config", "-c", help="Generation config YAML"),
) -> None:
    """Run the data generation pipeline. [Phase 3]"""
    _stub("generate", 3)


@app.command()
def validate(
    input_path: str | None = typer.Option(None, "--input", "-i", help="Input JSONL file"),
) -> None:
    """Run batch validation on a JSONL dataset. [Phase 3]"""
    _stub("validate", 3)


@app.command()
def dedup(
    input_path: str | None = typer.Option(None, "--input", "-i", help="Input JSONL"),
    output_path: str | None = typer.Option(None, "--output", "-o", help="Output JSONL"),
) -> None:
    """Run deduplication pipeline. [Phase 3]"""
    _stub("dedup", 3)


@app.command()
def train(
    config: str | None = typer.Option(None, "--config", "-c", help="Training config YAML"),
) -> None:
    """Run LoRA fine-tuning. [Phase 4]"""
    _stub("train", 4)


@app.command()
def merge(
    run_dir: str | None = typer.Option(None, "--run", "-r", help="Run directory"),
) -> None:
    """Merge LoRA adapter with base model. [Phase 4]"""
    _stub("merge", 4)


@app.command(name="eval")
def evaluate(
    model_path: str | None = typer.Option(None, "--model", "-m", help="Model path"),
    config: str | None = typer.Option(None, "--config", "-c", help="Eval config YAML"),
) -> None:
    """Run evaluation benchmarks. [Phase 5]"""
    _stub("eval", 5)


@app.command()
def quantize(
    model_path: str | None = typer.Option(None, "--model", "-m", help="Merged model path"),
    output_format: str = typer.Option("gguf", "--format", "-f", help="Output format"),
) -> None:
    """Export model to quantized format. [Phase 6]"""
    _stub("quantize", 6)


@app.command()
def chat(
    model_path: str | None = typer.Option(None, "--model", "-m", help="Model path"),
) -> None:
    """Interactive chat with a model. [Phase 7]"""
    _stub("chat", 7)
