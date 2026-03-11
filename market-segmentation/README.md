# Market Segmentation

An interactive CLI tool for fetching and analyzing Amazon product data. Retrieves product details and variant information using external APIs.

## Features

- **Fetch Details** - Get comprehensive product information (price, category, ratings, etc.)
- **Fetch Variants** - Retrieve all product variants and their attributes
- **Parallel Processing** - Fetch details and variants concurrently for faster results
- **Caching** - Avoid redundant API calls by caching results locally
- **Export to CSV** - Combine and export processed data for analysis
- **Clipboard Copy** - Quick access to export files

## Installation

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Setup

1. Create a `src/config.py` file with your API keys:

   ```python
   OUTSCRAPER_API_KEY = "your-key-here"
   CANOPY_API_KEY = "your-key-here"
   ```

2. Create `input.txt` with ASINs (one per line):
   ```
   B0FW38PNW3
   B0G1S35RBB
   B0G8ZTW97F
   ```

## Usage

```bash
python main.py
```

Select from the menu:

- **Fetch Product Details** - Get details for specific/range/all ASINs
- **Fetch Product Variants** - Get variant information
- **Fetch Both** - Parallel fetch of details and variants (faster!)
- **Export** - Generate CSV from processed data
- **Copy to Clipboard** - Copy export file path

## How It Works

- **Details** come from the Outscraper API
- **Variants** come from the Canopy API
- Results are cached in `outputs/detail/` and `outputs/variant/`
- Cached files prevent duplicate API calls

## Requirements

- requests >= 2.31.0
- questionary >= 2.0.1
- rich >= 13.7.0
