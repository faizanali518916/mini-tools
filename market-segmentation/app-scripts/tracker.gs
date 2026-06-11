const DOMAIN = 'US';
const SHEET_NAME = 'Tracking';

const API_KEY = '297609b4-8b2b-4e09-ab80-bfd2dde14f8a';
const API_BASE_URL = 'https://rest.canopyapi.co/api/amazon/product';

function updateAmazonPrices() {
	const ss = SpreadsheetApp.getActiveSpreadsheet();
	const sheet = ss.getSheetByName(SHEET_NAME) || ss.getActiveSheet();

	const lastRow = sheet.getLastRow();
	const lastCol = sheet.getLastColumn();

	if (lastRow < 2) throw new Error('No ASIN data found. ASINs should start from row 2 in column A.');

	const timezone = ss.getSpreadsheetTimeZone();
	const todayHeader = Utilities.formatDate(new Date(), timezone, 'M/d/yyyy');
	const headers = sheet.getRange(1, 1, 1, lastCol).getValues()[0].map(String);
	let todayCol = headers.findIndex((h) => h.trim() === todayHeader) + 1;

	if (todayCol === 0) {
		todayCol = lastCol + 1;
		sheet.getRange(1, todayCol).setValue(todayHeader);
	}

	const previousPriceCol = 2;
	const totalRows = asinValues.length;
	const asinValues = sheet.getRange(2, 1, lastRow - 1, 1).getValues();
	const previousPriceValues = sheet.getRange(2, previousPriceCol, lastRow - 1, 1).getValues();

	for (let i = 0; i < totalRows; i++) {
		const rowNumber = i + 2;
		const asin = String(asinValues[i][0]).trim();
		const oldPriceRaw = previousPriceValues[i][0];

		let result = '';

		if (!asin) {
			result = '';
			sheet.getRange(rowNumber, todayCol).setValue(result);
			Logger.log(`processed blank ${i + 1}/${totalRows}`);
			SpreadsheetApp.flush();
			continue;
		}

		try {
			const currentPrice = fetchAmazonPrice_(asin, API_KEY);

			if (currentPrice === null || currentPrice === undefined || isNaN(currentPrice)) result = 'Price Not Found';
			else {
				const oldPrice = parsePrice_(oldPriceRaw);
				const formattedPrice = formatPrice_(currentPrice);

				if (!oldPrice || oldPrice <= 0) {
					result = `${formattedPrice} (N/A)`;
				} else {
					const pctChange = ((currentPrice - oldPrice) / oldPrice) * 100;
					const formattedChange = formatPercentChange_(pctChange);

					result = `${formattedPrice} (${formattedChange})`;
				}
			}
		} catch (error) {
			result = `Error: ${error.message}`;
		}

		sheet.getRange(rowNumber, todayCol).setValue(result);

		Logger.log(`processed ${asin} ${i + 1}/${totalRows}`);

		Utilities.sleep(300);
	}

	sheet.getRange(1, todayCol).setFontWeight('bold');
	sheet.autoResizeColumn(todayCol);
}

function fetchAmazonPrice_(asin, apiKey) {
	const url = `${API_BASE_URL}?asin=${encodeURIComponent(asin)}&domain=${encodeURIComponent(DOMAIN)}`;

	const options = {
		method: 'get',
		muteHttpExceptions: true,
		headers: {
			accept: 'application/json',
			'API-KEY': apiKey,
		},
	};

	const response = UrlFetchApp.fetch(url, options);
	const statusCode = response.getResponseCode();
	const body = response.getContentText();

	if (statusCode < 200 || statusCode >= 300) {
		throw new Error(`API ${statusCode}`);
	}

	const json = JSON.parse(body);

	const product = json?.data?.amazonProduct;
	const price = product?.price?.value;

	if (price === null || price === undefined) return null;

	return Number(price);
}

function parsePrice_(value) {
	if (value === null || value === undefined || value === '') return null;

	if (typeof value === 'number') {
		return value;
	}

	const text = String(value);
	const match = text.match(/-?\d+(\.\d+)?/);

	return match ? Number(match[0]) : null;
}

function formatPrice_(price) {
	return Number(price).toFixed(2);
}

function formatPercentChange_(pct) {
	const rounded = Math.round(pct);

	if (rounded > 0) return `+${rounded}%`;
	if (rounded < 0) return `${rounded}%`;

	return `0%`;
}
