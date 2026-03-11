import os

from rich.panel import Panel
from rich.text import Text
from rich import box

from .styles import console


def clear():
    os.system("cls" if os.name == "nt" else "clear")


def banner():
    clear()
    console.print(
        Panel(
            Text("⌨  KEYWORD HELPER", justify="center", style="bold white"),
            subtitle="[dim]Interactive keyword management tool[/dim]",
            border_style="bright_magenta",
            box=box.DOUBLE_EDGE,
            padding=(1, 4),
        )
    )
    console.print()
