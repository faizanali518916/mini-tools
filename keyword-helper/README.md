# Keyword Helper

An interactive CLI tool for finding, cleaning, and managing keywords in Excel spreadsheets.

## Features

- **Search** - Find keywords across single or multiple sheets
- **Deduplicate** - Remove duplicate keywords while preserving sheet organization
- **Color-code** - View status with green/red row highlighting
- **Multi-sheet support** - Merge and analyze data from multiple worksheets
- **Export** - Save cleaned data back to Excel

## Installation

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Usage

```bash
python main.py
```

Then:

1. Select your Excel file
2. Choose which sheets to work with
3. Use the menu to search, deduplicate, or export keywords

## Requirements

- openpyxl
- rich
- questionary
