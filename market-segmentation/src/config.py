import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

# ── API Keys ─────────────────────────────────────────────────────────────────
# Outscraper API key (for product details)
OUTSCRAPER_API_KEY = os.getenv("OUTSCRAPER_API_KEY", "NULL")

# Canopy API key (for product variants)
CANOPY_API_KEY = os.getenv("CANOPYAI_API_KEY", "NULL")

# ── Paths ─────────────────────────────────────────────────────────────────────
INPUT_DIR = BASE_DIR / "inputs"
INPUT_FILE = INPUT_DIR / "input.txt"
OUTPUT_DETAIL_DIR = BASE_DIR / "outputs" / "detail"
OUTPUT_VARIANT_DIR = BASE_DIR / "outputs" / "variant"
OUTPUT_EXPORTS_DIR = BASE_DIR / "outputs" / "exports"
