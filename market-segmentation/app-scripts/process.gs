const SOURCE_SHEET_NAME = 'data';
const OUTPUT_SHEET_NAME = 'product_report';

function normalizeValue(val) {
	if (val === null || val === undefined) return '';
	return val.toString().toLowerCase().trim();
}

function buildProductReport() {
	const ss = SpreadsheetApp.getActiveSpreadsheet();
	const sourceSheet = ss.getSheetByName(SOURCE_SHEET_NAME);
	if (!sourceSheet) return;

	const lastRow = sourceSheet.getLastRow();
	const parsedRows = [];
	const rootKeys = new Set();
	const infoKeys = new Set();
	const detailsKeys = new Set();
	const variationDims = new Set();

	const generalMap = {
		country: 'Country',
		product_slug: 'Slug',
		unit_count: 'Unit Count',
		unit_price: 'Unit Price',
		product_url: 'Product URL',
		product_photo: 'Photo URL',
		product_title: 'Product Title',
		product_price: 'Current Price',
		product_star_rating: 'Star Rating',
		product_num_ratings: 'Ratings Count',
		product_original_price: 'Original Price',
	};

	const generalKeys = Object.keys(generalMap);

	const productExclude = ['ASIN', 'Best Sellers Rank', 'UPC'];

	for (let row = 1; row <= lastRow; row++) {
		const asin = sourceSheet.getRange(row, 1).getValue().toString().trim();
		const rawJson = sourceSheet.getRange(row, 2).getValue().toString().trim();
		if (!asin || !rawJson || rawJson.startsWith('ERROR')) continue;

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

		generalKeys.forEach((key) => {
			if (d[key] !== undefined) rootKeys.add(key);
		});

		Object.keys(info).forEach((key) => {
			if (!productExclude.includes(key)) infoKeys.add(key);
		});

		Object.keys(details).forEach((key) => {
			if (!productExclude.includes(key)) detailsKeys.add(key);
		});

		varDims.forEach((dim) => variationDims.add(dim));
		parsedRows.push({ asin, d, info, details });
	}

	const sortedRootKeys = generalKeys.filter((key) => rootKeys.has(key));
	const sortedInfoKeys = Array.from(infoKeys).sort();
	const sortedDetailsKeys = Array.from(detailsKeys).sort();
	const sortedVarDims = Array.from(variationDims).sort();

	const displayRootHeaders = sortedRootKeys.map((key) => generalMap[key] || key);

	const headers = ['Original ASIN', ...displayRootHeaders, ...sortedInfoKeys, ...sortedDetailsKeys];

	sortedVarDims.forEach((dim) => {
		const label = dim.charAt(0).toUpperCase() + dim.slice(1);
		headers.push(`Variations: ${label}`, `${label} Count`);
	});

	const groups = [
		{ name: 'Identity', width: 1, color: '#444444' },
		{ name: 'General Info', width: sortedRootKeys.length, color: '#2c3e50' },
		{
			name: 'Product Information',
			width: sortedInfoKeys.length,
			color: '#1a1a2e',
		},
		{
			name: 'Product Details',
			width: sortedDetailsKeys.length,
			color: '#2c3e50',
		},
		{ name: 'Variations', width: sortedVarDims.length * 2, color: '#1a1a2e' },
	];

	let outputSheet = ss.getSheetByName(OUTPUT_SHEET_NAME) || ss.insertSheet(OUTPUT_SHEET_NAME);
	outputSheet.clear();

	outputSheet.getRange(2, 1, 1, headers.length).setValues([headers]);

	const finalDataMatrix = parsedRows.map((rowObj) => {
		const rowValues = [rowObj.asin];

		const dataGroups = [
			{ keys: sortedRootKeys, data: rowObj.d },
			{ keys: sortedInfoKeys, data: rowObj.info },
			{ keys: sortedDetailsKeys, data: rowObj.details },
		];

		dataGroups.forEach((group) => {
			group.keys.forEach((key) => {
				rowValues.push(normalizeValue(group.data[key] || ''));
			});
		});

		sortedVarDims.forEach((dim) => {
			const dimData = (rowObj.d.product_variations || {})[dim] || [];
			const joinedValues = dimData
				.map((v) => v.value)
				.filter(Boolean)
				.join(', ');

			rowValues.push(normalizeValue(joinedValues));
			rowValues.push(dimData.length || 0);
		});

		return rowValues;
	});

	if (finalDataMatrix.length > 0) {
		outputSheet.getRange(3, 1, finalDataMatrix.length, headers.length).setValues(finalDataMatrix);
	}

	let currentCol = 1;
	groups.forEach((group) => {
		if (group.width > 0) {
			const range = outputSheet.getRange(1, currentCol, 1, group.width);
			if (group.width > 1) range.merge();
			range
				.setValue(group.name)
				.setBackground(group.color)
				.setFontColor('#ffffff')
				.setFontWeight('bold')
				.setHorizontalAlignment('center')
				.setVerticalAlignment('middle');
			currentCol += group.width;
		}
	});

	const totalRows = finalDataMatrix.length + 2;
	const totalCols = headers.length;

	outputSheet
		.getRange(2, 1, 1, totalCols)
		.setBackground('#34495e')
		.setFontColor('#ffffff')
		.setFontWeight('bold')
		.setFontSize(9);
	outputSheet.setFrozenRows(2);

	if (totalRows > 2) {
		outputSheet.setRowHeights(3, totalRows - 2, 20);
		const dataRange = outputSheet.getRange(3, 1, totalRows - 2, totalCols);
		dataRange.setFontSize(9).setVerticalAlignment('middle').setWrapStrategy(SpreadsheetApp.WrapStrategy.CLIP);
		for (let r = 3; r <= totalRows; r++) {
			if (r % 2 === 0) outputSheet.getRange(r, 1, 1, totalCols).setBackground('#f0f4ff');
		}
	}

	for (let i = 1; i <= totalCols; i++) {
		const width = Math.max(headers[i - 1].length * 8, 100);
		outputSheet.setColumnWidth(i, Math.min(width, 300));
	}

	SpreadsheetApp.getUi().alert(`✅ Grouped Report built! ${finalDataMatrix.length} products.`);
}
