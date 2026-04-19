# Lex Study Foundation — Architecture

See [implementation_plan.md](../implementation_plan.md) for the full architecture document.

## Quick Reference

### CLI Commands

```bash
python -m lex_study_foundation doctor           # Environment health check
python -m lex_study_foundation info             # Project metadata
python -m lex_study_foundation paths            # Resolved directory paths
python -m lex_study_foundation validate-config  # Validate a YAML config
```

### Data Pipeline Stages

```
seeds/ → raw/ → processed/ → training/
```

### Tier System

| Tier | Max Tokens | Turkish | Description |
|------|-----------|---------|-------------|
| short | 180 | KISA | 1-2 sentences |
| medium | 400 | NORMAL | 3-5 sentences |
| long | 650 | DETAYLI | 1-2 paragraphs |
| list | 450 | LİSTE | Bullet points |

### Shared Utilities

Text normalization and JSONL I/O are centralized:

- `utils/text.py` — NFC normalization, whitespace/newline cleanup, control char stripping, broken-text detection
- `utils/io.py` — JSONL read/write/append, atomic writes, plain text I/O (all UTF-8)
