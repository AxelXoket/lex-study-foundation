# Project Blank — Architecture

See [implementation_plan.md](../implementation_plan.md) for the full architecture document.

## Quick Reference

### CLI Commands

```bash
python -m project_blank doctor           # Environment health check
python -m project_blank info             # Project metadata
python -m project_blank paths            # Resolved directory paths
python -m project_blank validate-config  # Validate a YAML config
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
