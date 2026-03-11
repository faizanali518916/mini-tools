import sys

import questionary

from .styles import console, custom_style, INPUT_DIR
from .ui import banner


def pick_file():
    """Let the user pick an .xlsx file from input/."""
    banner()
    xlsx_files = sorted(INPUT_DIR.glob("*.xlsx"))
    if not xlsx_files:
        console.print(
            "[bold red]  No .xlsx files found in input/ directory.[/bold red]"
        )
        console.print("[dim]  Place your Excel files there and try again.[/dim]\n")
        sys.exit(1)

    choices = [f.name for f in xlsx_files]
    chosen = questionary.select(
        "Select an Excel file:",
        choices=choices,
        style=custom_style,
        instruction="(↑/↓ to move, Enter to select)",
    ).ask()

    if chosen is None:
        sys.exit(0)

    return INPUT_DIR / chosen


def pick_sheet(wb):
    """Let the user pick one or multiple worksheets."""
    banner()
    sheets = wb.sheetnames

    mode = questionary.select(
        "How many sheets would you like to work with?",
        choices=["Single sheet", "Multiple sheets (merged)"],
        style=custom_style,
    ).ask()

    if mode is None:
        sys.exit(0)

    if "Single" in mode:
        chosen = questionary.select(
            "Select a worksheet:",
            choices=sheets,
            style=custom_style,
            instruction="(↑/↓ to move, Enter to select)",
        ).ask()
        if chosen is None:
            sys.exit(0)
        return [chosen]
    else:
        chosen = questionary.checkbox(
            "Select worksheets to merge:",
            choices=sheets,
            style=custom_style,
            instruction="(↑/↓ to move, Space to select, Enter to confirm)",
        ).ask()
        if not chosen:
            sys.exit(0)
        return chosen
