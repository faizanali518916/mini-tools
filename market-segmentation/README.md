# Market Segmentation

This Google Sheets workflow fetches Amazon product JSON, cleans it into a structured report, and generates segmentation dashboards from the cleaned data.

## What The Three Apps Script Files Do

### `fetch.gs`

Reads ASINs from column A of the `data` sheet, calls the RapidAPI product-details endpoint, and writes the raw JSON response into column B.

### `process.gs`

Reads the raw JSON in `data`, flattens and cleans the payload, and writes a grouped table into `product_report`.

### `segmentor.gs`

Reads selected columns from `product_report`, aggregates them into market-share tables, and builds charts on a `Segmentation Reports` sheet.

## Google Sheets Setup

These scripts are designed to be pasted into a Google Sheets bound Apps Script project. They are not a standalone desktop app.

1. Open the Google Sheet that will hold the workflow.
2. Go to Extensions > Apps Script.
3. Create a new script project or open the bound project.
4. Add the three script files from `app-scripts/`:
   - `fetch.gs`
   - `process.gs`
   - `segmentor.gs`
5. Save the project and authorize it the first time you run a function.

## Required Sheet Names

The scripts expect these sheet names exactly:

- `data`
- `product_report`
- `tool`
- `Segmentation Reports` is created automatically by `segmentor.gs` if it does not exist.

If a sheet is missing, the relevant script will stop or fail quietly depending on the function.

## Sheet Layout Requirements

### `data`

This is the staging sheet for raw API results.

- Column A: ASIN values
- Column B: raw JSON response or error message written by `fetchProductData()`

`fetchProductData()` reads every non-empty ASIN in column A and skips rows where column B already has content.

### `product_report`

This is the cleaned and structured output sheet created by `buildProductReport()`.

- Row 1: grouped section headers
- Row 2: field headers
- Row 3 and below: cleaned product rows

The script builds this sheet from the JSON stored in `data!B:B`.

### `tool`

This sheet is used as the control panel for segmentation.

- `E6`: start column letter for the range you want to segment
- `E7`: end column letter for the range you want to segment
- `G4:L7`: status/log area used by `generateSegmentationReports()`

The segmentation script reads the column letters from `E6` and `E7`, then groups values from `product_report` between those columns.

## Setup Steps

1. Create or open a Google Sheet.
2. Rename or create a sheet named `data`.
3. Paste ASINs into `data!A:A`.
4. Add the Apps Script files from `app-scripts/`.
5. Make sure the `tool` sheet exists before running the segmentation script.
6. Update the RapidAPI key in `fetch.gs` before using the fetch function.

## Usage Flow

Run the scripts in this order:

1. `fetchProductData()`
   - Reads ASINs from `data!A:A`
   - Writes raw JSON into `data!B:B`

2. `buildProductReport()`
   - Reads the raw JSON from `data`
   - Skips rows with empty cells or values that start with `ERROR`
   - Writes the cleaned report into `product_report`

3. Prepare the `tool` sheet
   - Enter the start column letter in `E6`
   - Enter the end column letter in `E7`
   - Use the columns in `product_report` that represent the category you want to segment

4. `generateSegmentationReports()`
   - Builds a segmented summary sheet
   - Creates one table and chart per selected column
   - Writes progress and errors into the `tool` sheet

## Important Behavior Notes

- `fetchProductData()` uses the active spreadsheet and processes rows one by one with a short delay between requests.
- The fetch script skips rows that already have output in column B, so it will not overwrite existing results.
- `buildProductReport()` normalizes text values to lowercase and trims whitespace before writing them to `product_report`.
- `segmentor.gs` expects the selected analysis columns to live inside `product_report` and uses the two columns immediately after the selected range as monthly sales and monthly revenue values.
- If you want to use `segmentor.gs` as-is, make sure the selected range and the trailing sales/revenue columns match that expectation.

## Recommended Data Flow

1. Paste ASINs into `data!A:A`.
2. Run `fetchProductData()` to fill `data!B:B` with raw JSON.
3. Run `buildProductReport()` to create `product_report`.
4. Use the `tool` sheet to choose the segment columns.
5. Run `generateSegmentationReports()` to build the dashboard.

## API Key

`fetch.gs` currently stores the RapidAPI key directly in the script. Replace it with your own key before running the fetch step.

## Notes On The Existing Project Files

The repository also includes a separate Python CLI tool in `keyword-helper/`, but the Google Sheets workflow described above is entirely driven by the three scripts in `market-segmentation/app-scripts/`.
