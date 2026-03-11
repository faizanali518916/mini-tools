import json
import time

import requests

from .config import CANOPY_API_KEY, OUTPUT_VARIANT_DIR


def is_variant_cached(asin: str) -> bool:
    return (OUTPUT_VARIANT_DIR / f"{asin}.json").exists()


def fetch_variant(asin: str) -> dict:
    """
    Fetch product variants from Canopy API for a single ASIN.
    Saves the raw response to outputs/variant/<ASIN>.json and returns it.
    Skips the API call if the file already exists.
    """
    path = OUTPUT_VARIANT_DIR / f"{asin}.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))

    url = f"https://rest.canopyapi.co/api/amazon/product/variants?asin={asin}&domain=US"
    headers = {"accept": "application/json", "API-KEY": CANOPY_API_KEY}

    response = requests.get(url, headers=headers, timeout=60)
    response.raise_for_status()
    data = response.json()

    OUTPUT_VARIANT_DIR.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=4), encoding="utf-8")

    time.sleep(1)
    return data


def extract_variant_row(asin: str) -> dict | None:
    """
    Parse a cached variant JSON and return a flat dict with all attribute counts and values.
    Dynamically handles any attribute names (flavor, size, color, material, etc).
    Returns None if the file is missing or parsing fails.
    """
    path = OUTPUT_VARIANT_DIR / f"{asin}.json"
    if not path.exists():
        return None

    raw = json.loads(path.read_text(encoding="utf-8"))
    try:
        variants = raw.get("data", {}).get("amazonProduct", {}).get("variants", None)

        # Null or empty variants — return bare row so exporter fills attribute columns
        if not variants:
            return {"asin": asin}

        # Collect all unique attribute names and their values
        attributes: dict[str, set[str]] = {}
        for var in variants:
            for attr in var.get("attributes", []):
                name = attr.get("name", "").lower().replace(" ", "_")
                val = attr.get("value", "")
                if name not in attributes:
                    attributes[name] = set()
                if val:
                    attributes[name].add(val)

        # Variants present but no attributes extracted
        if not attributes:
            return {"asin": asin}

        # Build row with counts and sorted values
        row: dict = {"asin": asin}
        for attr_name in sorted(attributes.keys()):
            values = sorted(attributes[attr_name])
            row[f"{attr_name}_count"] = len(values)
            for i, v in enumerate(values, start=1):
                row[f"{attr_name}_{i}"] = v

        return row
    except Exception:
        return None
