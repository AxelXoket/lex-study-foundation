<p align="center">
  <h1 align="center">lex-study-foundation</h1>
  <p align="center">
    <strong>Turkish Educational LLM Fine-Tuning System</strong>
  </p>
  <p align="center">
    <img src="https://img.shields.io/badge/python-3.12+-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python">
    <img src="https://img.shields.io/badge/license-GPL--3.0-blue?style=flat-square" alt="License">
    <img src="https://img.shields.io/badge/model-Gemma_4_E4B-FF6F00?style=flat-square&logo=google&logoColor=white" alt="Gemma">
    <img src="https://img.shields.io/badge/data-Gemini_2.5_Flash-4285F4?style=flat-square&logo=google&logoColor=white" alt="Gemini">
    <img src="https://img.shields.io/badge/language-Turkish-red?style=flat-square" alt="Turkish">
  </p>
</p>

---

A clean, modular system for fine-tuning Gemma 4 E4B on Turkish educational content, with planned specialization toward law-study assistance.

## Project Scope

**This project is:**
- A Turkish educational LLM fine-tuning system
- Built around Google Gemma 4 E4B-it (~4B effective / 8B total params, 128K context)
- Data generation powered by Gemini 2.5 Flash
- Focused on explanation quality, concept comparison, and structured study assistance
- Later adaptable toward law-study exam preparation
- Designed for local deployment: train → evaluate → quantize → run locally

**This project is NOT:** a general chatbot, a web search assistant, a multimodal system, a professional legal advisor, or a universal tutor.

## Quick Start

```bash
# 1. Install uv (if not already installed)
pip install uv

# 2. Create venv and install dependencies
uv venv
uv pip install -e ".[dev]"

# 3. Copy and fill in environment variables
copy .env.example .env
# Edit .env with your API keys

# 4. Verify environment
python -m lex_study_foundation doctor

# 5. See available commands
python -m lex_study_foundation --help
```

Or on Windows, use the convenience scripts:
```cmd
tools\setup_env.bat    &:: One-time setup
tools\run.bat doctor   &:: Run any command
```

## Architecture

```
src/lex_study_foundation/     Python package (all source code)
configs/               YAML config files
data/                  Data pipeline stages (seeds → raw → processed → training)
runs/                  Training run outputs (per-experiment)
models/                Exported models (merged, quantized)
docs/                  Documentation
tools/                 BAT convenience wrappers (thin, no logic)
tests/                 pytest test suite
```

## Pipeline Phases

| Phase | Description | Status |
|-------|-------------|--------|
| 0. Skeleton | Project structure, CLI, config, tooling | ✅ Done |
| 1. Data schemas | Pydantic models, tier system | ✅ Done |
| 2. Utils | Text processing, IO layer, behavioral spec | ✅ Done |
| 3. Generation | Synthetic data pipeline | 🔲 Planned |
| 4. Training | LoRA/QLoRA fine-tuning | 🔲 Planned |
| 5. Evaluation | Benchmark-based eval | 🔲 Planned |
| 6. Quantization | GGUF export | 🔲 Planned |
| 7. Deployment | Local chat interface | 🔲 Planned |

## Development

```bash
# Run tests
pytest

# Lint + format
ruff check src/ tests/
ruff format src/ tests/

# Type check
pyright

# Pre-commit (all checks)
pre-commit run --all-files
```

## Hardware Target

- GPU: NVIDIA RTX 5080 (16 GB VRAM)
- CPU: AMD Ryzen 9800X3D
- RAM: 64 GB DDR5
- OS: Windows 11

## License

This project is licensed under the GNU General Public License v3.0 — see the [LICENSE](LICENSE) file for details.
