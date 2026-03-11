from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# ── API Keys ─────────────────────────────────────────────────────────────────
# Outscraper API key (for product details)
OUTSCRAPER_API_KEY = "OWNmYmUyMThhZGE5NGZiZmFmMzE0NTc0YTlhYTIwZmR8ZTZiNDczMDE3MA"

# Canopy API key (for product variants)
CANOPY_API_KEY = "c035cb61-9a15-4212-ab11-7785b77cd91f"

# ── Paths ─────────────────────────────────────────────────────────────────────
INPUT_FILE = BASE_DIR / "input.txt"

OUTPUT_DETAIL_DIR = BASE_DIR / "outputs" / "detail"
OUTPUT_VARIANT_DIR = BASE_DIR / "outputs" / "variant"
OUTPUT_EXPORTS_DIR = BASE_DIR / "outputs" / "exports"
