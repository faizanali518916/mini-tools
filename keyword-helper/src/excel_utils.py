import copy


def get_row_color(row):
    """Return 'red', 'green', or None based on the fill of the first cell."""
    cell = row[0]
    fill = cell.fill
    if fill and fill.start_color and fill.start_color.rgb:
        rgb = str(fill.start_color.rgb)
        if rgb in ("00FF4C4C", "FF4C4C", "FFFF4C4C"):
            return "red"
        if rgb in ("004CFF4C", "4CFF4C", "FF4CFF4C"):
            return "green"
    return None


def get_data_rows(ws):
    """Return list of row indices that have data in the first column (skip empty rows)."""
    data_rows = []
    for row_idx in range(2, ws.max_row + 1):
        cell = ws.cell(row=row_idx, column=1)
        if cell.value is not None:
            data_rows.append(row_idx)
    return data_rows


def sort_sheet(ws):
    """
    Sort sheet in-place so green rows are on top, uncolored in the middle,
    and red rows at the bottom. Row 1 is treated as a header and kept.
    """
    data_rows = get_data_rows(ws)
    if not data_rows:
        return

    rows_data = []
    for row_idx in data_rows:
        row_cells = []
        for col_idx in range(1, ws.max_column + 1):
            cell = ws.cell(row=row_idx, column=col_idx)
            row_cells.append(
                {
                    "value": cell.value,
                    "fill": copy.copy(cell.fill),
                    "font": copy.copy(cell.font),
                }
            )
        rows_data.append((row_idx, row_cells))

    def sort_key(item):
        _row_idx, row = item
        fill = row[0]["fill"]
        if fill and fill.start_color and fill.start_color.rgb:
            rgb = str(fill.start_color.rgb)
            if rgb in ("004CFF4C", "4CFF4C", "FF4CFF4C"):
                return 0  # green first
            if rgb in ("00FF4C4C", "FF4C4C", "FFFF4C4C"):
                return 2  # red last
        return 1  # uncolored middle

    rows_data.sort(key=sort_key)

    for i, (_orig_row_idx, row) in enumerate(rows_data):
        dest_row_idx = data_rows[i]
        for col_idx, cell_data in enumerate(row, start=1):
            cell = ws.cell(row=dest_row_idx, column=col_idx)
            cell.value = cell_data["value"]
            cell.fill = cell_data["fill"]
            cell.font = cell_data["font"]
