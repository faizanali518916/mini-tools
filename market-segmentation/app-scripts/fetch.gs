const RAPIDAPI_KEY = "<YOUR_RAPIDAPI_KEY_HERE> "; // Replace with your actual RapidAPI key
const RAPIDAPI_HOST = "real-time-amazon-data.p.rapidapi.com";
const DATA_SHEET_NAME = "data";

function fetchProductData() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getSheetByName(DATA_SHEET_NAME);
  if (!sheet) return;

  const lastRow = sheet.getLastRow();
  const data = sheet.getRange(1, 1, lastRow, 2).getValues();
  const requests = [];
  const indices = [];

  for (let i = 0; i < data.length; i++) {
    const asin = data[i][0].toString().trim();
    const existing = data[i][1].toString().trim();

    if (asin && !existing) {
      requests.push({
        url: `https://${RAPIDAPI_HOST}/product-details?asin=${encodeURIComponent(asin)}&country=US`,
        method: "GET",
        headers: {
          "x-rapidapi-host": RAPIDAPI_HOST,
          "x-rapidapi-key": RAPIDAPI_KEY,
        },
        muteHttpExceptions: true,
      });
      indices.push(i + 1);
    }

    if (
      requests.length === 10 ||
      (i === data.length - 1 && requests.length > 0)
    ) {
      const responses = UrlFetchApp.fetchAll(requests);

      responses.forEach((res, index) => {
        const row = indices[index];
        const status = res.getResponseCode();
        const content = res.getContentText();
        sheet
          .getRange(row, 2)
          .setValue(status === 200 ? content : `ERROR: ${status}`);
      });

      requests.length = 0;
      indices.length = 0;
      Utilities.sleep(1000);
    }
  }

  SpreadsheetApp.getUi().alert("Process Complete.");
}
