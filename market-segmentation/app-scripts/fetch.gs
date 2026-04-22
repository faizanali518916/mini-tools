const RAPIDAPI_KEY = '9aabaef681msha864065f0de675ap18598ajsn414cf1663b2a';
const RAPIDAPI_HOST = 'real-time-amazon-data.p.rapidapi.com';
const DATA_SHEET_NAME = 'data';

function fetchProductData() {
	const ss = SpreadsheetApp.getActiveSpreadsheet();
	const sheet = ss.getSheetByName(DATA_SHEET_NAME);

	if (!sheet) {
		SpreadsheetApp.getUi().alert(`Sheet "${DATA_SHEET_NAME}" not found.`);
		return;
	}

	const lastRow = sheet.getLastRow();
	if (lastRow < 1) {
		Logger.log('No ASINs found in column A.');
		return;
	}

	let processed = 0;

	for (let row = 1; row <= lastRow; row++) {
		const asinCell = sheet.getRange(row, 1);
		const resultCell = sheet.getRange(row, 2);

		const asin = asinCell.getValue().toString().trim();
		if (!asin) continue; // Skip empty ASIN rows

		// ✅ Skip if column B already has data (avoid wasted API calls)
		const existingValue = resultCell.getValue().toString().trim();
		if (existingValue !== '') {
			Logger.log(`Row ${row}: ASIN ${asin} already fetched, skipping.`);
			continue;
		}

		Logger.log(`Row ${row}: Fetching data for ASIN ${asin}...`);

		try {
			const url = `https://${RAPIDAPI_HOST}/product-details?asin=${encodeURIComponent(asin)}&country=US`;

			const options = {
				method: 'GET',
				headers: {
					'Content-Type': 'application/json',
					'x-rapidapi-host': RAPIDAPI_HOST,
					'x-rapidapi-key': RAPIDAPI_KEY,
				},
				muteHttpExceptions: true,
			};

			const response = UrlFetchApp.fetch(url, options);
			const statusCode = response.getResponseCode();

			if (statusCode === 200) {
				const json = response.getContentText();
				resultCell.setValue(json);
				Logger.log(`Row ${row}: ✅ Success for ASIN ${asin}`);
			} else {
				resultCell.setValue(`ERROR: HTTP ${statusCode} – ${response.getContentText()}`);
				Logger.log(`Row ${row}: ❌ Failed with status ${statusCode}`);
			}
		} catch (e) {
			resultCell.setValue(`ERROR: ${e.message}`);
			Logger.log(`Row ${row}: ❌ Exception – ${e.message}`);
		}

		processed++;
		Utilities.sleep(500); // Polite delay between calls
	}

	Logger.log(`Done. Processed ${processed} ASINs.`);
	SpreadsheetApp.getUi().alert(`✅ Done. Fetched data for ${processed} ASINs.`);
}
