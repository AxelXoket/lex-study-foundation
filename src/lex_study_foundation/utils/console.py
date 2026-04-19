"""Rich console singleton and display helpers.

All console output in the project goes through this module.
This ensures consistent styling, width, and behavior across all commands.
"""

from __future__ import annotations

import os
import sys

# ── Windows UTF-8 fix ───────────────────────────────────────────────────────
# Turkish Windows defaults to cp1254, which can't render Rich's Unicode
# box-drawing characters. Force UTF-8 before any Rich output.
if sys.platform == "win32":
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from rich.console import Console
from rich.table import Table
from rich.theme import Theme
from rich.tree import Tree

# ── Project-wide theme ──────────────────────────────────────────────────────
_THEME = Theme(
    {
        "info": "cyan",
        "success": "bold green",
        "warning": "bold yellow",
        "error": "bold red",
        "header": "bold magenta",
        "dim": "dim",
        "key": "bold cyan",
        "value": "white",
    }
)

# ── Singleton console ───────────────────────────────────────────────────────
console = Console(theme=_THEME, highlight=False, force_terminal=True)
err_console = Console(theme=_THEME, stderr=True, highlight=False, force_terminal=True)


# ── Display helpers ─────────────────────────────────────────────────────────

def print_header(title: str) -> None:
    """Print a styled section header."""
    console.print()
    console.print(f"  {title}", style="header")
    console.print("  " + "─" * len(title), style="dim")


def print_kv(key: str, value: str, *, indent: int = 2) -> None:
    """Print a key-value pair with consistent styling."""
    pad = " " * indent
    console.print(f"{pad}[key]{key}:[/key] [value]{value}[/value]")


def status_table(rows: list[tuple[str, str, str]]) -> Table:
    """Create a status table for doctor-style checks.

    Each row is (name, status_emoji, detail).
    """
    table = Table(show_header=True, header_style="bold", padding=(0, 1))
    table.add_column("Check", style="key", min_width=25)
    table.add_column("Status", justify="center", min_width=4)
    table.add_column("Detail", style="dim")

    for name, status, detail in rows:
        table.add_row(name, status, detail)

    return table


def path_tree(paths: dict[str, str]) -> Tree:
    """Create a Rich tree from a name→path mapping."""
    tree = Tree("[header]Project Paths[/header]")
    for name, path in paths.items():
        tree.add(f"[key]{name}[/key]: {path}")
    return tree
