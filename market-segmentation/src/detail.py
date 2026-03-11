import json
import time

import requests

from .config import OUTSCRAPER_API_KEY, OUTPUT_DETAIL_DIR


def is_detail_cached(asin: str) -> bool:
    return (OUTPUT_DETAIL_DIR / f"{asin}.json").exists()


def fetch_detail(asin: str) -> dict:
    """
    Fetch product details from Outscraper for a single ASIN.
    Saves the raw response to outputs/detail/<ASIN>.json and returns it.
    Skips the API call if the file already exists.
    """
    path = OUTPUT_DETAIL_DIR / f"{asin}.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))

    url = (
        f"https://api.outscraper.cloud/amazon-products"
        f"?query=https://www.amazon.com/dp/{asin}&limit=1&async=false"
    )
    headers = {"X-API-KEY": OUTSCRAPER_API_KEY}

    response = requests.get(url, headers=headers, timeout=60)
    response.raise_for_status()
    data = response.json()

    OUTPUT_DETAIL_DIR.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=4), encoding="utf-8")

    time.sleep(1)
    return data


def _clean_text(text) -> str:
    if isinstance(text, str):
        return text.replace("\u200e", "").strip()
    return text if text is not None else "N/A"


def extract_detail_row(asin: str) -> dict | None:
    """
    Parse a cached detail JSON and return a flat dict of product fields.
    Returns None if the file is missing or parsing fails.
    """
    path = OUTPUT_DETAIL_DIR / f"{asin}.json"
    if not path.exists():
        return None

    entry = json.loads(path.read_text(encoding="utf-8"))
    try:
        if entry.get("status") != "Success" or not entry.get("data"):
            return None

        product = entry["data"][0][0]
        asin_val = product.get("asin", asin)
        details = product.get("details", {})

        row = {
            "asin": asin_val,
            "name": product.get("name"),
            "price": product.get("price"),
            "url": f"amazon.com/dp/{asin_val}",
            "category": (
                product.get("categories", ["N/A"])[0]
                if product.get("categories")
                else "N/A"
            ),
        }

        for key, value in details.items():
            cleaned_key = key.lower().replace(" ", "_")
            row[cleaned_key] = _clean_text(value)

        return row
    except Exception:
        return None
