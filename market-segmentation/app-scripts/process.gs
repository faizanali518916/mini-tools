// ============================================================
// SCRIPT 2 (REVISED): Dynamic JSON Parser with Grouped Headers
// ============================================================

const SOURCE_SHEET_NAME = "data";
const OUTPUT_SHEET_NAME = "product_report";

function buildProductReport() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sourceSheet = ss.getSheetByName(SOURCE_SHEET_NAME);

  if (!sourceSheet) {
    SpreadsheetApp.getUi().alert(`Sheet "${SOURCE_SHEET_NAME}" not found.`);
    return;
  }

  const lastRow = sourceSheet.getLastRow();
  const parsedRows = [];

  const rootKeys = new Set();
  const infoKeys = new Set();
  const detailsKeys = new Set();
  const variationDims = new Set();

  // ── Step 1: Discovery Pass ──────────────────────────────────
  for (let row = 1; row <= lastRow; row++) {
    const asin = sourceSheet.getRange(row, 1).getValue().toString().trim();
    const rawJson = sourceSheet.getRange(row, 2).getValue().toString().trim();

    if (!asin || !rawJson || rawJson.startsWith("ERROR")) continue;

    let parsed;
    try {
      parsed = JSON.parse(rawJson);
    } catch (e) {
      continue;
    }

    const d = parsed.data || {};
    const details = d.product_details || {};
    const info = d.product_information || {};
    const varDims = d.product_variations_dimensions || [];

    Object.keys(d).forEach((key) => {
      if (
        (typeof d[key] !== "object" || d[key] === null) &&
        key.toLowerCase() !== "asin"
      ) {
        rootKeys.add(key);
      }
    });

    Object.keys(details).forEach((key) => {
      if (key.toLowerCase() !== "asin") detailsKeys.add(key);
    });

    Object.keys(info).forEach((key) => {
      if (key.toLowerCase() !== "asin") infoKeys.add(key);
    });

    varDims.forEach((dim) => variationDims.add(dim));

    parsedRows.push({ asin, d, info, details });
  }

  const sortedRootKeys = Array.from(rootKeys).sort();
  const sortedInfoKeys = Array.from(infoKeys).sort();
  const sortedDetailsKeys = Array.from(detailsKeys).sort();
  const sortedVarDims = Array.from(variationDims).sort();

  // ── Step 2: Build Header Logic ──────────────────────────────
  const headers = [
    "Original ASIN",
    ...sortedRootKeys,
    ...sortedInfoKeys,
    ...sortedDetailsKeys,
  ];
  sortedVarDims.forEach((dim) => {
    const formattedDim = dim.charAt(0).toUpperCase() + dim.slice(1);
    headers.push(`Variations: ${formattedDim}`, `${formattedDim} Count`);
  });

  // Define Group Widths for Merging
  const groups = [
    { name: "Identity", width: 1, color: "#444444" },
    { name: "General Info", width: sortedRootKeys.length, color: "#2c3e50" },
    {
      name: "Product Information",
      width: sortedInfoKeys.length,
      color: "#1a1a2e",
    },
    {
      name: "Product Details",
      width: sortedDetailsKeys.length,
      color: "#2c3e50",
    },
    { name: "Variations", width: sortedVarDims.length * 2, color: "#1a1a2e" },
  ];

  // ── Step 3: Set up Output Sheet ─────────────────────────────
  let outputSheet = ss.getSheetByName(OUTPUT_SHEET_NAME);
  if (outputSheet) {
    outputSheet.clearContents();
    outputSheet.clearFormats();
    outputSheet.clearNotes();
  } else {
    outputSheet = ss.insertSheet(OUTPUT_SHEET_NAME);
  }

  outputSheet.getRange(2, 1, 1, headers.length).setValues([headers]);

  // ── Step 4: Map and Write Data ──────────────────────────────
  const finalDataMatrix = [];
  for (const rowObj of parsedRows) {
    const rowValues = [rowObj.asin];
    sortedRootKeys.forEach((key) => rowValues.push(rowObj.d[key] || ""));
    sortedInfoKeys.forEach((key) => rowValues.push(rowObj.info[key] || ""));
    sortedDetailsKeys.forEach((key) =>
      rowValues.push(rowObj.details[key] || ""),
    );
    sortedVarDims.forEach((dim) => {
      const dimData = (rowObj.d.product_variations || {})[dim] || [];
      rowValues.push(
        dimData
          .map((v) => v.value)
          .filter(Boolean)
          .join(", "),
      );
      rowValues.push(dimData.length || 0);
    });
    finalDataMatrix.push(rowValues);
  }

  if (finalDataMatrix.length > 0) {
    outputSheet
      .getRange(3, 1, finalDataMatrix.length, headers.length)
      .setValues(finalDataMatrix);
  }

  // ── Step 5: Formatting Grouped Headers (Row 1) ──────────────
  let currentCol = 1;
  groups.forEach((group) => {
    if (group.width > 0) {
      const range = outputSheet.getRange(1, currentCol, 1, group.width);
      if (group.width > 1) range.merge();
      range
        .setValue(group.name)
        .setBackground(group.color)
        .setFontColor("#ffffff")
        .setFontWeight("bold")
        .setHorizontalAlignment("center")
        .setVerticalAlignment("middle");
      currentCol += group.width;
    }
  });

  // ── Step 6: General Formatting ──────────────────────────────
  const totalRows = finalDataMatrix.length + 2;
  const totalCols = headers.length;

  // Sub-header Styling (Row 2)
  const subHeaderRange = outputSheet.getRange(2, 1, 1, totalCols);
  subHeaderRange
    .setBackground("#34495e")
    .setFontColor("#ffffff")
    .setFontWeight("bold")
    .setFontSize(9);

  outputSheet.setFrozenRows(2);

  if (totalRows > 2) {
    outputSheet.setRowHeights(3, totalRows - 2, 20);
    const dataRange = outputSheet.getRange(3, 1, totalRows - 2, totalCols);
    dataRange
      .setVerticalAlignment("middle")
      .setFontSize(9)
      .setWrapStrategy(SpreadsheetApp.WrapStrategy.CLIP);

    // Alternating Colors
    for (let r = 3; r <= totalRows; r++) {
      if (r % 2 === 0)
        outputSheet.getRange(r, 1, 1, totalCols).setBackground("#f0f4ff");
    }
  }

  // Auto-width
  for (let i = 1; i <= totalCols; i++) {
    const width = Math.max(headers[i - 1].length * 8, 100);
    outputSheet.setColumnWidth(i, Math.min(width, 300));
  }

  SpreadsheetApp.getUi().alert(
    `✅ Grouped Report built! ${finalDataMatrix.length} products.`,
  );
}
