import os
from pathlib import Path

import pandas as pd

from .styles import console


def list_export_csvs(export_dir: Path) -> list[Path]:
    """List all CSV files in the export directory, newest first."""
    if not export_dir.exists():
        return []
    csvs = sorted(
        export_dir.glob("*.csv"),
        key=os.path.getmtime,
        reverse=True,
    )
    return csvs


def copy_csv_to_clipboard(csv_path: Path) -> bool:
    """
    Copy a CSV file to clipboard using pandas.
    Returns True if successful, False otherwise.
    """
    try:
        df = pd.read_csv(csv_path)
        df.to_clipboard(index=False, sep="\t")
        return True
    except Exception as e:
        console.print(f"[red]Error copying to clipboard: {e}[/red]")
        return False
