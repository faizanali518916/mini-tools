import os
from pathlib import Path

from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich import box

from .styles import console


def clear():
    os.system("cls" if os.name == "nt" else "clear")


def banner():
    clear()
    console.print(
        Panel(
            Text("🔬  MARKET SEGMENTATION", justify="center", style="bold white"),
            subtitle="[dim]ASIN research & analysis tool[/dim]",
            border_style="bright_cyan",
            box=box.DOUBLE_EDGE,
            padding=(1, 4),
        )
    )
    console.print()


def show_asin_table(asins: list[str], detail_dir: Path, variant_dir: Path):
    """Print a status table showing which ASINs are cached for details and variants."""
    table = Table(
        title=f"📦  ASIN Status  ({len(asins)} total)",
        box=box.ROUNDED,
        border_style="bright_cyan",
        header_style="bold bright_cyan",
        show_lines=False,
        padding=(0, 2),
    )
    table.add_column("#", style="dim", width=5, justify="right")
    table.add_column("ASIN", style="white", width=14)
    table.add_column("Detail", justify="center", width=14)
    table.add_column("Variant", justify="center", width=14)

    for i, asin in enumerate(asins, start=1):
        detail_ok = (detail_dir / f"{asin}.json").exists()
        variant_ok = (variant_dir / f"{asin}.json").exists()
        d_label = (
            "[bold green]✔ cached[/bold green]" if detail_ok else "[dim]— pending[/dim]"
        )
        v_label = (
            "[bold green]✔ cached[/bold green]"
            if variant_ok
            else "[dim]— pending[/dim]"
        )
        table.add_row(str(i), asin, d_label, v_label)

    console.print(table)
    console.print()

    detail_done = sum(1 for a in asins if (detail_dir / f"{a}.json").exists())
    variant_done = sum(1 for a in asins if (variant_dir / f"{a}.json").exists())
    console.print(
        f"  [bright_cyan]Details:[/bright_cyan]  [green]{detail_done}[/green] cached  "
        f"[dim]{len(asins) - detail_done} pending[/dim]    "
        f"[bright_cyan]Variants:[/bright_cyan]  [green]{variant_done}[/green] cached  "
        f"[dim]{len(asins) - variant_done} pending[/dim]\n"
    )
