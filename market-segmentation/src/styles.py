import questionary
from questionary import Style
from rich.console import Console

console = Console()

custom_style = Style(
    [
        ("qmark", "fg:#E91E63 bold"),
        ("question", "fg:#FFFFFF bold"),
        ("answer", "fg:#00BCD4 bold"),
        ("pointer", "fg:#E91E63 bold"),
        ("highlighted", "fg:#E91E63 bold"),
        ("selected", "fg:#00BCD4"),
        ("separator", "fg:#757575"),
        ("instruction", "fg:#9E9E9E"),
        ("text", "fg:#FFFFFF"),
    ]
)
