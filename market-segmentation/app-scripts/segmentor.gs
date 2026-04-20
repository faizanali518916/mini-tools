function generateSegmentationReports() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const toolSheet = ss.getSheetByName("Tool");
  const logRange = toolSheet.getRange("G4:L7");
  const dataSheet = ss.getSheetByName("Alignment");

  logRange.clearContent().setValue("🚀 Generating custom styled reports...");

  try {
    const startColLetter = toolSheet
      .getRange("E6")
      .getValue()
      .toString()
      .toUpperCase();
    const endColLetter = toolSheet
      .getRange("E7")
      .getValue()
      .toString()
      .toUpperCase();
    const startCol = columnToNumber(startColLetter);
    const endCol = columnToNumber(endColLetter);

    const salesCol = endCol + 1;
    const revenueCol = endCol + 2;

    let reportSheet = ss.getSheetByName("Segmentation Reports");
    if (reportSheet) {
      reportSheet.clear();
      reportSheet.getCharts().forEach((c) => reportSheet.removeChart(c));
    } else {
      reportSheet = ss.insertSheet("Segmentation Reports");
    }

    let cursorRow = 2;
    const startDataCol = 2;
    const lastRow = dataSheet.getLastRow();

    for (let col = startCol; col <= endCol; col++) {
      const colName = dataSheet.getRange(3, col).getValue() || "Value";
      const numRowsToRead = lastRow - 3;
      if (numRowsToRead <= 0) continue;

      const dataValues = dataSheet.getRange(4, col, numRowsToRead).getValues();
      const salesValues = dataSheet
        .getRange(4, salesCol, numRowsToRead)
        .getValues();
      const revenueValues = dataSheet
        .getRange(4, revenueCol, numRowsToRead)
        .getValues();

      let summary = {};
      let totalSales = 0,
        totalRev = 0;

      dataValues.forEach((row, index) => {
        let val = row[0] === "" || row[0] === null ? "N/A" : row[0];
        let s = parseFloat(salesValues[index][0]) || 0;
        let r = parseFloat(revenueValues[index][0]) || 0;

        if (!summary[val]) summary[val] = { sales: 0, revenue: 0 };
        summary[val].sales += s;
        summary[val].revenue += r;
        totalSales += s;
        totalRev += r;
      });

      const sortedKeys = Object.keys(summary).sort((a, b) => {
        return summary[b].sales - summary[a].sales;
      });

      const result = renderFormattedTable(
        reportSheet,
        cursorRow,
        startDataCol,
        colName,
        summary,
        totalSales,
        totalRev,
        sortedKeys,
      );

      addMarketShareChart(
        reportSheet,
        cursorRow,
        startDataCol,
        result.numRows,
        colName,
      );

      cursorRow = result.nextRow + 3;
    }

    for (let i = startDataCol; i <= startDataCol + 4; i++) {
      reportSheet.autoResizeColumn(i);
    }

    logRange.setValue(
      `✅ Success! Dashboard generated at ${new Date().toLocaleTimeString()}`,
    );
  } catch (e) {
    logRange.setValue("❌ Error: " + e.message);
  }
}

function renderFormattedTable(
  sheet,
  startRow,
  startCol,
  title,
  data,
  totalSales,
  totalRev,
  sortedKeys,
) {
  const keys = Object.keys(data);
  const numRows = keys.length;

  sheet
    .getRange(startRow, startCol, 1, 5)
    .merge()
    .setValue(title.toUpperCase())
    .setBackground("#B6D7A8")
    .setFontWeight("bold")
    .setFontSize(14)
    .setHorizontalAlignment("center")
    .setBorder(
      true,
      true,
      true,
      true,
      null,
      null,
      "black",
      SpreadsheetApp.BorderStyle.SOLID,
    );

  const headerRange = sheet.getRange(startRow + 1, startCol, 1, 5);
  headerRange
    .setValues([
      [
        title,
        "MONTHLY SALES",
        "MONTHLY REVENUE",
        "MARKET SHARE UNIT",
        "MARKET SHARE REVENUE",
      ],
    ])
    .setBackground("#000000")
    .setFontColor("#FFFFFF")
    .setFontWeight("bold")
    .setHorizontalAlignment("center")
    .setBorder(
      true,
      true,
      true,
      true,
      null,
      null,
      "black",
      SpreadsheetApp.BorderStyle.SOLID,
    );

  sheet.getRange(startRow + 1, startCol + 3).setBackground("#7f6000");
  sheet.getRange(startRow + 1, startCol + 4).setBackground("#660000");

  let tableData = sortedKeys.map((key) => [
    key,
    data[key].sales,
    data[key].revenue,
    totalSales > 0 ? data[key].sales / totalSales : 0,
    totalRev > 0 ? data[key].revenue / totalRev : 0,
  ]);

  const dataRange = sheet.getRange(startRow + 2, startCol, numRows, 5);
  dataRange.setValues(tableData).setHorizontalAlignment("center");

  dataRange.setBorder(
    null,
    true,
    null,
    true,
    null,
    true,
    "black",
    SpreadsheetApp.BorderStyle.DOTTED,
  );
  sheet
    .getRange(startRow + 2, startCol, numRows, 1)
    .setBorder(
      null,
      true,
      null,
      true,
      null,
      null,
      "black",
      SpreadsheetApp.BorderStyle.SOLID,
    );
  sheet
    .getRange(startRow + 2, startCol + 4)
    .setBorder(
      null,
      null,
      null,
      true,
      null,
      null,
      "black",
      SpreadsheetApp.BorderStyle.SOLID,
    );

  sheet.getRange(startRow + 2, startCol + 1, 1, 4).setBackground("#ffff00");

  const totalRowIndex = startRow + 2 + numRows;
  sheet
    .getRange(totalRowIndex, startCol, 1, 5)
    .setValues([["TOTAL", totalSales, totalRev, "", ""]])
    .setBackground("#D9D9D9")
    .setFontWeight("bold")
    .setBorder(
      true,
      true,
      true,
      true,
      null,
      null,
      "black",
      SpreadsheetApp.BorderStyle.SOLID,
    );

  sheet
    .getRange(startRow + 2, startCol + 1, numRows + 1, 1)
    .setNumberFormat("#,##0");
  sheet
    .getRange(startRow + 2, startCol + 2, numRows + 1, 1)
    .setNumberFormat("$#,##0.00");
  sheet
    .getRange(startRow + 2, startCol + 3, numRows, 2)
    .setNumberFormat("0.00%");

  return { nextRow: totalRowIndex + 1, numRows: numRows };
}

function addMarketShareChart(sheet, startRow, tableStartCol, numRows, title) {
  const labelRange = sheet.getRange(startRow + 2, tableStartCol, numRows, 1);
  const unitShareRange = sheet.getRange(
    startRow + 2,
    tableStartCol + 3,
    numRows,
    1,
  );
  const revShareRange = sheet.getRange(
    startRow + 2,
    tableStartCol + 4,
    numRows,
    1,
  );

  const dynamicHeight = (numRows + 3) * 21;

  const chart = sheet
    .newChart()
    .setChartType(Charts.ChartType.BAR)
    .addRange(labelRange)
    .addRange(unitShareRange)
    .addRange(revShareRange)
    .setOption("isStacked", true)
    .setOption("hAxis.format", "0%")
    .setOption("legend.position", "top")
    .setOption("series", {
      0: { labelInLegend: "Market Share Unit" },
      1: { labelInLegend: "Market Share Revenue" },
    })
    .setOption("colors", ["#4A86E8", "#FF9900"])
    .setOption("chartArea", {
      left: "15%",
      top: "5%",
      width: "80%",
      height: "85%",
    })
    .setPosition(startRow, tableStartCol + 6, 0, 0)
    .setOption("height", dynamicHeight)
    .setOption("width", 1000)
    .build();

  sheet.insertChart(chart);
}

function columnToNumber(letter) {
  let column = 0,
    length = letter.length;
  for (let i = 0; i < length; i++) {
    column += (letter.charCodeAt(i) - 64) * Math.pow(26, length - i - 1);
  }
  return column;
}
