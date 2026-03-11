import copy

import questionary
from rich.table import Table
from rich.panel import Panel
from rich import box

from .styles import console, custom_style, RED_FILL, GREEN_FILL, WHITE_FILL
from .ui import banner
from .excel_utils import get_row_color, get_data_rows, sort_sheet


def get_multi_sheet_data(wb, sheet_names):
    """Merge data from multiple sheets. Returns dict: sheet_name -> list of (row_idx, keyword)."""
    merged_data = {}
    for sheet_name in sheet_names:
        ws = wb[sheet_name]
        data_rows = get_data_rows(ws)
        merged_data[sheet_name] = [
            (row_idx, str(ws.cell(row=row_idx, column=1).value or ""))
            for row_idx in data_rows
        ]
    return merged_data


def view_multi_sheets(wb, sheet_names):
    """Display merged keywords from multiple sheets with pagination."""
    banner()
    merged_data = get_multi_sheet_data(wb, sheet_names)

    all_rows = []
    for sheet_name in sheet_names:
        for row_idx, keyword in merged_data[sheet_name]:
            all_rows.append((sheet_name, row_idx, keyword))

    total = len(all_rows)
    page_size = 500
    total_pages = (total + page_size - 1) // page_size

    if total_pages > 1:
        page_choices = [
            f"Page {i+1}  ({i*page_size + 1}-{min((i+1)*page_size, total)})"
            for i in range(total_pages)
        ]
        banner()
        page_choice = questionary.select(
            f"Select page to view ({total_pages} pages total):",
            choices=page_choices,
            style=custom_style,
        ).ask()
        if page_choice is None:
            return
        page_num = int(page_choice.split()[1]) - 1
    else:
        page_num = 0

    start_idx = page_num * page_size
    end_idx = min(start_idx + page_size, total)
    page_rows = all_rows[start_idx:end_idx]

    banner()
    page_info = f" [Page {page_num + 1}/{total_pages}]" if total_pages > 1 else ""
    table = Table(
        title=f"📋  Merged Keywords from {len(sheet_names)} sheets{page_info}",
        box=box.ROUNDED,
        border_style="bright_magenta",
        header_style="bold bright_cyan",
        show_lines=False,
        padding=(0, 2),
    )
    table.add_column("#", style="dim", width=6, justify="right")
    table.add_column("Sheet", style="bright_magenta", width=15)
    table.add_column("Keyword", style="white", min_width=30)
    table.add_column("Status", justify="center", width=12)

    for display_idx, (sheet_name, row_idx, keyword) in enumerate(
        page_rows, start=start_idx + 1
    ):
        ws = wb[sheet_name]
        row = [ws.cell(row=row_idx, column=1)]
        color = get_row_color(row)
        if color == "green":
            status = "[bold green]✔ Relevant[/bold green]"
            kw_style = "green"
        elif color == "red":
            status = "[bold red]✘ Irrelevant[/bold red]"
            kw_style = "red"
        else:
            status = "[dim]—[/dim]"
            kw_style = "white"
        table.add_row(
            str(display_idx), sheet_name, f"[{kw_style}]{keyword}[/{kw_style}]", status
        )

    console.print(table)
    console.print()

    green_count = 0
    red_count = 0
    for sheet_name in sheet_names:
        ws = wb[sheet_name]
        for row_idx, _ in merged_data[sheet_name]:
            row = [ws.cell(row=row_idx, column=1)]
            if get_row_color(row) == "green":
                green_count += 1
            elif get_row_color(row) == "red":
                red_count += 1
    unmarked = total - green_count - red_count

    stats = Table(box=box.SIMPLE, show_header=False, padding=(0, 1))
    stats.add_column(style="bold")
    stats.add_column()
    stats.add_row("[bright_cyan]Total[/bright_cyan]", str(total))
    stats.add_row("[green]Relevant[/green]", str(green_count))
    stats.add_row("[red]Irrelevant[/red]", str(red_count))
    stats.add_row("[dim]Unmarked[/dim]", str(unmarked))
    console.print(
        Panel(stats, title="Statistics", border_style="bright_magenta", box=box.ROUNDED)
    )
    console.print()

    questionary.press_any_key_to_continue(style=custom_style).ask()


def keyword_search_multi(wb, sheet_names, filepath):
    """Search across multiple sheets and mark matches."""
    banner()
    query = questionary.text(
        "Enter search keyword / substring:",
        style=custom_style,
    ).ask()

    if query is None:
        return

    query_lower = query.strip().lower()
    if not query_lower:
        console.print("[yellow]  Empty search query. Returning to menu.[/yellow]\n")
        questionary.press_any_key_to_continue(style=custom_style).ask()
        return

    matches = {}
    for sheet_name in sheet_names:
        ws = wb[sheet_name]
        data_rows = get_data_rows(ws)
        sheet_matches = []
        for row_idx in data_rows:
            cell = ws.cell(row=row_idx, column=1)
            value = str(cell.value).lower() if cell.value is not None else ""
            if query_lower in value:
                sheet_matches.append(row_idx)
        if sheet_matches:
            matches[sheet_name] = sheet_matches

    banner()
    if not matches:
        console.print(
            f"[yellow]  No keywords found containing '[bold]{query}[/bold]' in selected sheets.[/yellow]\n"
        )
        questionary.press_any_key_to_continue(style=custom_style).ask()
        return

    total_matches = sum(len(rows) for rows in matches.values())
    table = Table(
        title=f"🔍  Results for '{query}'  ({total_matches} matches)",
        box=box.ROUNDED,
        border_style="bright_cyan",
        header_style="bold bright_cyan",
        show_lines=False,
        padding=(0, 2),
    )
    table.add_column("#", style="dim", width=6, justify="right")
    table.add_column("Sheet", style="bright_magenta", width=15)
    table.add_column("Row", style="dim", width=6, justify="right")
    table.add_column("Keyword", style="white", min_width=30)

    match_idx = 1
    for sheet_name in sheet_names:
        if sheet_name not in matches:
            continue
        ws = wb[sheet_name]
        for row_idx in matches[sheet_name]:
            keyword = str(ws.cell(row=row_idx, column=1).value or "")
            lower_kw = keyword.lower()
            start = lower_kw.find(query_lower)
            if start != -1:
                before = keyword[:start]
                match = keyword[start : start + len(query_lower)]
                after = keyword[start + len(query_lower) :]
                display = (
                    f"{before}[bold bright_magenta]{match}[/bold bright_magenta]{after}"
                )
            else:
                display = keyword
            table.add_row(str(match_idx), sheet_name, str(row_idx), display)
            match_idx += 1

    console.print(table)
    console.print()

    action = questionary.select(
        "What would you like to do with these results?",
        choices=[
            "🟢  Mark all as RELEVANT (green)",
            "🔴  Mark all as IRRELEVANT (red)",
            "⊘  Mark all as NEUTRAL (unmarked)",
            "↩  Back to menu (no changes)",
        ],
        style=custom_style,
    ).ask()

    if action is None or "Back" in action:
        return

    if "NEUTRAL" in action:
        fill = WHITE_FILL
        label = "neutral"
        target_color = None
    elif "IRRELEVANT" in action:
        fill = RED_FILL
        label = "irrelevant"
        target_color = "red"
    else:
        fill = GREEN_FILL
        label = "relevant"
        target_color = "green"

    marked_count = 0
    skipped_count = 0

    for sheet_name in matches:
        ws = wb[sheet_name]
        for row_idx in matches[sheet_name]:
            row = [ws.cell(row=row_idx, column=1)]
            current_color = get_row_color(row)

            if target_color == "red" and current_color == "green":
                skipped_count += 1
                continue
            elif target_color == "green" and current_color == "red":
                skipped_count += 1
                continue

            for col_idx in range(1, ws.max_column + 1):
                ws.cell(row=row_idx, column=col_idx).fill = fill
            marked_count += 1

    for sheet_name in sheet_names:
        ws = wb[sheet_name]
        sort_sheet(ws)

    wb.save(filepath)

    if skipped_count > 0:
        console.print(
            f"\n[bold green]  ✔ Marked {marked_count} rows as {label} and re-sorted all sheets.\n"
            f"  ⊘ Skipped {skipped_count} rows (protected by existing marking)[/bold green]\n"
        )
    else:
        console.print(
            f"\n[bold green]  ✔ Marked {marked_count} rows as {label} and re-sorted all sheets.[/bold green]\n"
        )
    questionary.press_any_key_to_continue(style=custom_style).ask()


def export_clean_multi(wb, sheet_names, filepath):
    """Export cleaned data from multiple sheets to a single new sheet."""
    banner()

    new_name = "merged_clean"
    counter = 1
    while new_name in wb.sheetnames:
        counter += 1
        new_name = f"merged_clean_{counter}"

    name = questionary.text(
        "Name for the merged clean sheet:",
        default=new_name,
        style=custom_style,
    ).ask()

    if name is None:
        return

    name = name.strip() or new_name

    new_ws = wb.create_sheet(title=name)
    new_ws["A1"] = "Keyword"

    dest_row = 2
    total_copied = 0
    total_skipped = 0

    for sheet_name in sheet_names:
        ws = wb[sheet_name]
        data_rows = get_data_rows(ws)
        for row_idx in data_rows:
            row_cells = [
                ws.cell(row=row_idx, column=c) for c in range(1, ws.max_column + 1)
            ]
            color = get_row_color(row_cells)
            if color == "red":
                total_skipped += 1
                continue
            for col_idx in range(1, ws.max_column + 1):
                src = ws.cell(row=row_idx, column=col_idx)
                dst = new_ws.cell(row=dest_row, column=col_idx)
                dst.value = src.value
                dst.fill = copy.copy(src.fill)
                dst.font = copy.copy(src.font)
            dest_row += 1
            total_copied += 1

    wb.save(filepath)

    console.print(
        Panel(
            f"[bold green]✔  Created sheet '[bright_cyan]{name}[/bright_cyan]'\n\n"
            f"   Sheets merged:   [white]{len(sheet_names)}[/white]\n"
            f"   Rows copied:     [white]{total_copied}[/white]\n"
            f"   Rows removed:    [red]{total_skipped}[/red] (irrelevant)[/bold green]",
            border_style="green",
            box=box.ROUNDED,
            padding=(1, 3),
        )
    )
    console.print()
    questionary.press_any_key_to_continue(style=custom_style).ask()
