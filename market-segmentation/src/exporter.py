import csv
import re
from datetime import datetime

from .config import OUTPUT_EXPORTS_DIR
from .detail import extract_detail_row
from .variants import extract_variant_row
from .clipboard import copy_csv_to_clipboard


def export_to_csv(asins: list[str]) -> str | None:
    """
    Build a CSV from all cached detail + variant data for the given ASINs.
    Each attribute gets three columns: attribute-base, attribute-variations, attribute-count.

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

    attribute_names: set[str] = set()
    for key in all_variant_keys:
        if key != "asin":
            if key.endswith("_count"):
                attribute_names.add(key[:-6])
            else:
                m = re.match(r"^(.+)_\d+$", key)
                if m:
                    attribute_names.add(m.group(1))

    variant_fields = []
    for attr in sorted(attribute_names):
        variant_fields.append(f"{attr}-base")
        variant_fields.append(f"{attr}-variations")
        variant_fields.append(f"{attr}-count")

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
                variant_row = variant_rows[asin]
                attr_data: dict[str, dict] = {}
                for key, value in variant_row.items():
                    if key == "asin":
                        continue
                    if key.endswith("_count"):
                        attr_name = key[:-6]
                        if attr_name not in attr_data:
                            attr_data[attr_name] = {}
                        attr_data[attr_name]["count"] = value
                    else:
                        m = re.match(r"^(.+)_(\d+)$", key)
                        if m:
                            attr_name = m.group(1)
                            index = int(m.group(2))
                            if attr_name not in attr_data:
                                attr_data[attr_name] = {}
                            if "values" not in attr_data[attr_name]:
                                attr_data[attr_name]["values"] = {}
                            attr_data[attr_name]["values"][index] = value

                for attr_name, data in attr_data.items():
                    values = data.get("values", {})
                    count = data.get("count", len(values))
                    row[f"{attr_name}-base"] = values.get(1, "-")
                    variation_values = [
                        values[i] for i in sorted(values.keys()) if i > 1
                    ]
                    row[f"{attr_name}-variations"] = (
                        ", ".join(variation_values) if variation_values else "-"
                    )
                    row[f"{attr_name}-count"] = count

            for field in variant_fields:
                if field not in row:
                    if field.endswith("-count"):
                        row[field] = 1
                    else:
                        row[field] = "-"

            writer.writerow(row)

    copy_csv_to_clipboard(out_path)
    return str(out_path)
