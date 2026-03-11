import questionary

from .styles import console, custom_style
from .ui import banner


def show_instructions():
    """Display help and instructions for using the tool."""
    banner()
    instructions = """
[bold bright_cyan]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/bold bright_cyan]
[bold white]KEYWORD HELPER - USER GUIDE[/bold white]
[bold bright_cyan]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/bold bright_cyan]

[bold green]📁 GETTING STARTED[/bold green]
1. Select an Excel file from the [bright_cyan]input/[/bright_cyan] directory
2. Choose to work with a single sheet or multiple sheets (merged)
3. Use the main menu to perform operations

[bold green]👁 VIEW DATA[/bold green]
• See all keywords in the current sheet(s)
• Shows keyword status: [green]Relevant[/green], [red]Irrelevant[/red], or Unmarked
• Displays statistics: total, relevant, irrelevant counts
• If >500 keywords, data is paginated (500 per page)

[bold green]🔍 KEYWORD SEARCH[/bold green]
• Search for keywords containing a specific substring
• Search is case-insensitive
• View all matching keywords in a results table
• Then choose to:
  → [green]Mark as RELEVANT[/green] (green highlight)
  → [red]Mark as IRRELEVANT[/red] (red highlight)
  → [cyan]Mark as NEUTRAL[/cyan] (remove any marking)
  → Cancel with no changes

[bold green]⚠️ PROTECTION RULES[/bold green]
• If a keyword is already marked [green]Relevant[/green], you cannot mark it [red]Irrelevant[/red]
• If a keyword is already marked [red]Irrelevant[/red], you cannot mark it [green]Relevant[/green]
• Neutral markings can override anything

[bold green]📤 EXPORT CLEAN SHEET[/bold green]
• Creates a new sheet combining only relevant/unmarked keywords
• Removes all [red]Irrelevant[/red] rows automatically
• Choose a custom name for the new sheet
• Works across merged sheets too!

[bold green]🧹 REMOVE DUPLICATE KEYWORDS[/bold green]
• Finds duplicate keywords (case-insensitive)
• Keeps the first occurrence, removes duplicates
• Only works on single sheets
• Warns you before deleting

[bold green]🔗 MULTI-SHEET MODE[/bold green]
• Select multiple sheets when prompted
• All operations work on merged data
• Marks apply to matching keywords across all sheets
• Export creates a single merged clean sheet

[bold green]📄 SWITCH WORKSHEETS[/bold green]
• Change to a different sheet or sheet combination anytime

[bold green]📂 SWITCH FILE[/bold green]
• Load a different Excel file

[bold green]💾 AUTO-SAVE[/bold green]
• All changes are saved immediately to the Excel file

[bold green]📊 AUTO-SORT[/bold green]
• After marking keywords, the sheet auto-sorts:
  1. [green]Relevant[/green] keywords at the top
  2. Unmarked in the middle
  3. [red]Irrelevant[/red] at the bottom

[bold bright_cyan]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/bold bright_cyan]
"""
    console.print(instructions)
    console.print()
    questionary.press_any_key_to_continue(style=custom_style).ask()
