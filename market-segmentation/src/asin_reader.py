from pathlib import Path
from typing import Optional, List
from .config import INPUT_DIR, INPUT_FILE


def list_input_files() -> List[Path]:
    """List all text files in the input directory."""
    if not INPUT_DIR.exists():
        INPUT_DIR.mkdir(parents=True, exist_ok=True)
        return []

    txt_files = sorted(INPUT_DIR.glob("*.txt"))
    return txt_files


def read_asins(input_file: Optional[Path] = None) -> List[str]:
    """Read ASINs from input file, one per line. Returns a deduplicated ordered list.

    Args:
        input_file: Path to the input file. If None, defaults to input.txt.
    """
    if input_file is None:
        input_file = INPUT_FILE

    if not input_file.exists():
        input_file.write_text(
            "# Paste one ASIN per line below this comment\n", encoding="utf-8"
        )
        return []

    lines = input_file.read_text(encoding="utf-8").splitlines()
    seen = set()
    asins = []
    for line in lines:
        asin = line.strip().upper()
        if not asin or asin.startswith("#"):
            continue
        if asin not in seen:
            seen.add(asin)
            asins.append(asin)
    return asins
