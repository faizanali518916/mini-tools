from .config import INPUT_FILE


def read_asins() -> list[str]:
    """Read ASINs from input.txt, one per line. Returns a deduplicated ordered list."""
    if not INPUT_FILE.exists():
        INPUT_FILE.write_text(
            "# Paste one ASIN per line below this comment\n", encoding="utf-8"
        )
        return []

    lines = INPUT_FILE.read_text(encoding="utf-8").splitlines()
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
