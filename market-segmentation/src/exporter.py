import csv
from datetime import datetime

from .config import OUTPUT_EXPORTS_DIR
from .detail import extract_detail_row
from .variants import extract_variant_row
from .clipboard import copy_csv_to_clipboard


def export_to_csv(asins: list[str]) -> str | None:
    """
    Build a combined CSV from all cached detail + variant data for the given ASINs.
    Dynamically handles all detail and variant attributes.
    Returns the output file path, or None if there is nothing to export.
    """
    OUTPUT_EXPORTS_DIR.mkdir(parents=True, exist_ok=True)

    # ── Pass 1: collect all rows and determine dynamic column names ────────
    detail_rows: dict[str, dict] = {}
    variant_rows: dict[str, dict] = {}
    all_detail_keys: set[str] = set()
    all_variant_keys: set[str] = set()

    for asin in asins:
        d = extract_detail_row(asin)
        if d:
            detail_rows[asin] = d
            all_detail_keys.update(d.keys())

        v = extract_variant_row(asin)
        if v:
            variant_rows[asin] = v
            all_variant_keys.update(v.keys())

    if not detail_rows and not variant_rows:
        return None

    # ── Build fieldnames ──────────────────────────────────────────────────────
    base_fields = ["asin", "name", "price", "url", "category"]
    base_set = set(base_fields)
    dynamic_detail = sorted(k for k in all_detail_keys if k not in base_set)
    variant_fields = sorted(k for k in all_variant_keys if k != "asin")

    fieldnames = base_fields + dynamic_detail + variant_fields

    # ── Write CSV ─────────────────────────────────────────────────────────────
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = OUTPUT_EXPORTS_DIR / f"export_{timestamp}.csv"

    exported_asins = set(detail_rows) | set(variant_rows)

    with open(out_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for asin in asins:
            if asin not in exported_asins:
                continue
            row: dict = {}
            if asin in detail_rows:
                row.update(detail_rows[asin])
            else:
                row["asin"] = asin
            if asin in variant_rows:
                row.update(variant_rows[asin])
            # Attributes completely absent for this ASIN get count=1 + placeholder value
            missing_attrs = {
                f[:-6]
                for f in variant_fields
                if f.endswith("_count") and not row.get(f)
            }
            for field in variant_fields:
                if not row.get(field):
                    if field.endswith("_count"):
                        row[field] = 1
                    elif field.endswith("_1") and field[:-2] in missing_attrs:
                        row[field] = "Base Product (no variations found)"
                    else:
                        row[field] = "-"
            writer.writerow(row)

    copy_csv_to_clipboard(out_path)
    return str(out_path)
