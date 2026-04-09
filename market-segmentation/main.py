#!/usr/bin/env python3
"""
Market Segmentation - Interactive CLI for fetching and analysing Amazon ASIN data.

Usage:
  1. Add ASINs (one per line) to .txt files in the input/ directory
  2. Run:  py main.py
  3. Select input file when prompted
"""

import sys
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

import questionary
from rich.panel import Panel
from rich.json import JSON
from rich import box

from src.config import (
    OUTPUT_DETAIL_DIR,
    OUTPUT_VARIANT_DIR,
    OUTPUT_EXPORTS_DIR,
    INPUT_DIR,
)
from src.styles import console, custom_style
from src.ui import banner, show_asin_table
from src.asin_reader import read_asins, list_input_files
from src.detail import is_detail_cached, fetch_detail
from src.variants import is_variant_cached, fetch_variant
from src.exporter import export_to_csv
from src.clipboard import list_export_csvs, copy_csv_to_clipboard


def select_scope(asins: list[str]) -> list[str]:
    """Ask the user for a scope (specific / range / all) and return the selected ASINs."""
    scope = questionary.select(
        "Select scope:",
        choices=[
            "🎯  Specific ASIN (choose by index)",
            "📏  Range  (start to end index)",
            "🌐  All ASINs",
        ],
        style=custom_style,
    ).ask()

    if scope is None:
        return []

    if "Specific" in scope:
        choices = [f"[{i}]  {a}" for i, a in enumerate(asins, start=1)]
        chosen = questionary.select(
            "Select ASIN:",
            choices=choices,
            style=custom_style,
            instruction="(up/down to move, Enter to select)",
        ).ask()
        if chosen is None:
            return []
        idx = int(chosen.split("]")[0].lstrip("[")) - 1
        return [asins[idx]]

    if "Range" in scope:
        start_str = questionary.text(
            f"Start index  (1 to {len(asins)}):", style=custom_style
        ).ask()
        end_str = questionary.text(
            f"End index    (1 to {len(asins)}, inclusive):", style=custom_style
        ).ask()
        try:
            start = max(1, int(start_str)) - 1
            end = min(len(asins), int(end_str))
            return asins[start:end]
        except (ValueError, TypeError):
            console.print("[red]  Invalid range. Returning to menu.[/red]\n")
            return []

    return asins


def run_fetch(targets: list[str], fetch_fn, cached_fn, label: str):
    """Fetch data for each ASIN in targets, up to 4 requests in parallel."""
    banner()

    to_skip = [a for a in targets if cached_fn(a)]
    to_fetch = [a for a in targets if not cached_fn(a)]

    for asin in to_skip:
        console.print(
            f"  [dim]{asin}[/dim]  [cyan]{label}[/cyan]  "
            f"[yellow]already cached, skipping[/yellow]"
        )

    fetched = 0
    errors = 0

    with ThreadPoolExecutor(max_workers=4) as executor:
        future_to_asin = {executor.submit(fetch_fn, asin): asin for asin in to_fetch}
        completed = 0
        for future in as_completed(future_to_asin):
            asin = future_to_asin[future]
            completed += 1
            try:
                future.result()
                console.print(
                    f"  [{completed}/{len(to_fetch)}]  [white]{asin}[/white]  "
                    f"[cyan]{label}[/cyan]  [bold green]saved[/bold green]"
                )
                fetched += 1
            except Exception as exc:
                console.print(
                    f"  [{completed}/{len(to_fetch)}]  [white]{asin}[/white]  "
                    f"[cyan]{label}[/cyan]  [bold red]error: {exc}[/bold red]"
                )
                errors += 1

    console.print()
    console.print(
        Panel(
            f"[white]Fetched:[/white] [green]{fetched}[/green]   "
            f"[white]Skipped (cached):[/white] [yellow]{len(to_skip)}[/yellow]   "
            f"[white]Errors:[/white] [red]{errors}[/red]",
            border_style="green" if errors == 0 else "yellow",
            box=box.ROUNDED,
            padding=(0, 2),
        )
    )
    console.print()
    questionary.press_any_key_to_continue(style=custom_style).ask()


def run_fetch_both(targets: list[str]):
    """Fetch detail then variant for each ASIN, up to 4 ASINs processed in parallel."""
    banner()
    total = len(targets)
    console.print(
        f"[cyan]Preparing to fetch {total} ASINs (detail \u2192 variant per ASIN)...[/cyan]\n"
    )

    results = {
        "detail": {"fetched": 0, "skipped": 0, "errors": 0},
        "variant": {"fetched": 0, "skipped": 0, "errors": 0},
    }
    lock = threading.Lock()

    def process_asin(asin: str, idx: int):
        # ── Step 1: Detail ───────────────────────────────────────────────────
        if is_detail_cached(asin):
            console.print(
                f"  [{idx}/{total}]  [dim]{asin}[/dim]  "
                f"[cyan]detail[/cyan]  [yellow]cached[/yellow]"
            )
            with lock:
                results["detail"]["skipped"] += 1
        else:
            try:
                fetch_detail(asin)
                console.print(
                    f"  [{idx}/{total}]  [white]{asin}[/white]  "
                    f"[cyan]detail[/cyan]  [bold green]\u2713[/bold green]"
                )
                with lock:
                    results["detail"]["fetched"] += 1
            except Exception as exc:
                console.print(
                    f"  [{idx}/{total}]  [white]{asin}[/white]  "
                    f"[cyan]detail[/cyan]  [bold red]\u2717 {exc}[/bold red]"
                )
                with lock:
                    results["detail"]["errors"] += 1

        # ── Step 2: Variant ──────────────────────────────────────────────────
        if is_variant_cached(asin):
            console.print(
                f"  [{idx}/{total}]  [dim]{asin}[/dim]  "
                f"[cyan]variant[/cyan]  [yellow]cached[/yellow]"
            )
            with lock:
                results["variant"]["skipped"] += 1
        else:
            try:
                fetch_variant(asin)
                console.print(
                    f"  [{idx}/{total}]  [white]{asin}[/white]  "
                    f"[cyan]variant[/cyan]  [bold green]\u2713[/bold green]"
                )
                with lock:
                    results["variant"]["fetched"] += 1
            except Exception as exc:
                console.print(
                    f"  [{idx}/{total}]  [white]{asin}[/white]  "
                    f"[cyan]variant[/cyan]  [bold red]\u2717 {exc}[/bold red]"
                )
                with lock:
                    results["variant"]["errors"] += 1

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [
            executor.submit(process_asin, asin, i)
            for i, asin in enumerate(targets, start=1)
        ]
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as exc:
                console.print(f"  [bold red]FATAL: {exc}[/bold red]")

    # Summary
    console.print()
    detail_stats = results["detail"]
    variant_stats = results["variant"]

    console.print(
        Panel(
            f"[white]Details:[/white]  [green]{detail_stats['fetched']}[/green] fetched  "
            f"[yellow]{detail_stats['skipped']}[/yellow] cached  "
            f"[red]{detail_stats['errors']}[/red] errors\n"
            f"[white]Variants:[/white] [green]{variant_stats['fetched']}[/green] fetched  "
            f"[yellow]{variant_stats['skipped']}[/yellow] cached  "
            f"[red]{variant_stats['errors']}[/red] errors",
            border_style=(
                "green"
                if (detail_stats["errors"] + variant_stats["errors"] == 0)
                else "yellow"
            ),
            box=box.ROUNDED,
            padding=(0, 2),
        )
    )
    console.print()
    questionary.press_any_key_to_continue(style=custom_style).ask()


def select_input_file():
    """Let user choose an input file from the input directory."""
    input_files = list_input_files()

    if not input_files:
        console.print(
            "[yellow]  No input files found in the [bright_cyan]input/[/bright_cyan] directory.\n"
            "  Please add .txt files with ASINs (one per line) and run again.[/yellow]\n"
        )
        questionary.press_any_key_to_continue(style=custom_style).ask()
        return None

    choices = [f.name for f in input_files]
    selected = questionary.select(
        "Select input file:",
        choices=choices,
        style=custom_style,
        instruction="(up/down to move, Enter to select)",
    ).ask()

    if selected is None:
        return None

    return INPUT_DIR / selected


def main():
    for d in (OUTPUT_DETAIL_DIR, OUTPUT_VARIANT_DIR, OUTPUT_EXPORTS_DIR):
        d.mkdir(parents=True, exist_ok=True)

    try:
        while True:
            banner()

            input_file = select_input_file()
            if input_file is None:
                continue

            asins = read_asins(input_file)

            if not asins:
                console.print(
                    f"[yellow]  No ASINs found in [bright_cyan]{input_file.name}[/bright_cyan].\n"
                    "  Add one ASIN per line and run again.[/yellow]\n"
                )
                questionary.press_any_key_to_continue(style=custom_style).ask()
                continue

            show_asin_table(asins, OUTPUT_DETAIL_DIR, OUTPUT_VARIANT_DIR)

            action = questionary.select(
                "What would you like to do?",
                choices=[
                    "-> Fetch Product Details",
                    "-> Fetch Product Variants",
                    "-> Fetch Both (Details + Variants)",
                    "-> Export Processed ASINs to CSV",
                    "-> Copy CSV to Clipboard",
                    "-> Search ASIN & View JSON",
                    "-> Refresh Status",
                    "-> Exit",
                ],
                style=custom_style,
                instruction="(up/down to move, Enter to select)",
            ).ask()

            if action is None or "Exit" in action:
                banner()
                console.print("  [dim]Goodbye![/dim]\n")
                break

            elif "Details" in action:
                banner()
                show_asin_table(asins, OUTPUT_DETAIL_DIR, OUTPUT_VARIANT_DIR)
                targets = select_scope(asins)
                if targets:
                    run_fetch(targets, fetch_detail, is_detail_cached, "detail")

            elif "Variants" in action:
                banner()
                show_asin_table(asins, OUTPUT_DETAIL_DIR, OUTPUT_VARIANT_DIR)
                targets = select_scope(asins)
                if targets:
                    run_fetch(targets, fetch_variant, is_variant_cached, "variants")

            elif "Both" in action:
                banner()
                show_asin_table(asins, OUTPUT_DETAIL_DIR, OUTPUT_VARIANT_DIR)
                targets = select_scope(asins)
                if targets:
                    run_fetch_both(targets)

            elif "Export" in action:
                banner()
                show_asin_table(asins, OUTPUT_DETAIL_DIR, OUTPUT_VARIANT_DIR)

                detail_ready = [a for a in asins if is_detail_cached(a)]
                variant_ready = [a for a in asins if is_variant_cached(a)]
                exportable = sorted(
                    set(detail_ready) | set(variant_ready),
                    key=lambda a: asins.index(a),
                )

                if not exportable:
                    console.print(
                        "[yellow]  No processed ASINs yet. "
                        "Fetch details or variants first.[/yellow]\n"
                    )
                    questionary.press_any_key_to_continue(style=custom_style).ask()
                    continue

                console.print(
                    f"  [white]{len(exportable)}[/white] ASINs ready to export  "
                    f"([green]{len(detail_ready)}[/green] with detail, "
                    f"[green]{len(variant_ready)}[/green] with variants)\n"
                )

                confirm = questionary.confirm(
                    "Export all processed ASINs to CSV?",
                    default=True,
                    style=custom_style,
                ).ask()

                if confirm:
                    out_path = export_to_csv(exportable)
                    if out_path:
                        console.print(
                            Panel(
                                f"[bold green]CSV exported successfully!\n\n"
                                f"   [white]File:[/white]  [bright_cyan]{out_path}[/bright_cyan]\n"
                                f"   [white]ASINs:[/white] {len(exportable)}[/bold green]",
                                border_style="green",
                                box=box.ROUNDED,
                                padding=(1, 3),
                            )
                        )
                        console.print()
                    else:
                        console.print(
                            "[red]  Export failed — no data to write.[/red]\n"
                        )
                    questionary.press_any_key_to_continue(style=custom_style).ask()

            # ── Copy CSV to Clipboard ────────────────────────────────────
            elif "Clipboard" in action:
                banner()
                csvs = list_export_csvs(OUTPUT_EXPORTS_DIR)
                if not csvs:
                    console.print(
                        "[yellow]  No CSV files found in exports directory.[/yellow]\n"
                    )
                    questionary.press_any_key_to_continue(style=custom_style).ask()
                    continue

                csv_choices = [f"  {c.name}" for c in csvs]
                chosen = questionary.select(
                    f"Select CSV file to copy ({len(csvs)} available):",
                    choices=csv_choices,
                    style=custom_style,
                    instruction="(up/down to move, Enter to select)",
                ).ask()

                if chosen:
                    csv_path = csvs[csv_choices.index(chosen)]
                    if copy_csv_to_clipboard(csv_path):
                        console.print(
                            Panel(
                                f"[bold green]CSV copied to clipboard!\n\n"
                                f"   [white]File:[/white]  [bright_cyan]{csv_path.name}[/bright_cyan]\n\n"
                                f"   Ready to paste in Excel[/bold green]",
                                border_style="green",
                                box=box.ROUNDED,
                                padding=(1, 3),
                            )
                        )
                    else:
                        console.print("[red]  Failed to copy to clipboard.[/red]\n")
                    console.print()
                    questionary.press_any_key_to_continue(style=custom_style).ask()

            # ── Search & View ASIN JSON ──────────────────────────────────
            elif "Search" in action:
                banner()

                available_asins = [
                    a for a in asins if is_detail_cached(a) or is_variant_cached(a)
                ]

                if not available_asins:
                    console.print(
                        "[yellow]  No JSON data available for the current ASINs.\n"
                        "  Fetch details or variants first.[/yellow]\n"
                    )
                    questionary.press_any_key_to_continue(style=custom_style).ask()
                    continue

                chosen_asin = questionary.autocomplete(
                    "Search ASIN:",
                    choices=available_asins,
                    style=custom_style,
                    validate=lambda val: val in available_asins
                    or "Select a valid ASIN",
                ).ask()

                if chosen_asin:
                    d_path = OUTPUT_DETAIL_DIR / f"{chosen_asin}.json"
                    v_path = OUTPUT_VARIANT_DIR / f"{chosen_asin}.json"

                    if d_path.exists():
                        console.print(
                            f"\n[bold cyan]── Detail JSON ({chosen_asin}) ──[/bold cyan]"
                        )
                        console.print(JSON(d_path.read_text(encoding="utf-8")))

                    if v_path.exists():
                        console.print(
                            f"\n[bold cyan]── Variant JSON ({chosen_asin}) ──[/bold cyan]"
                        )
                        console.print(JSON(v_path.read_text(encoding="utf-8")))

                    console.print()
                    questionary.press_any_key_to_continue(style=custom_style).ask()

    except KeyboardInterrupt:
        console.print("\n  [dim]Interrupted. Goodbye![/dim]\n")
        sys.exit(0)


if __name__ == "__main__":
    main()
