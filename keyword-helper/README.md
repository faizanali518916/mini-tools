# Keyword Helper

An interactive CLI tool for finding, cleaning, and managing keywords in Excel spreadsheets.

## Features

- **Search** - Find keywords across single or multiple sheets
- **Deduplicate** - Remove duplicate keywords while preserving sheet organization
- **Color-code** - View status with green/red row highlighting
- **Multi-sheet support** - Merge and analyze data from multiple worksheets
- **Export** - Save cleaned data back to Excel

## Getting Started

1. Install Git if you do not already have it: <https://git-scm.com/downloads>
2. Clone this repository:

   ```bash
   git clone <repo-url>
   cd mini-tools/keyword-helper
   ```

3. Run the setup script once to create the virtual environment and install dependencies:

   ```bat
   setup.bat
   ```

4. Start the tool with:

   ```bat
   run.bat
   ```

## How It Works

The batch files do most of the setup work now:

- `setup.bat` creates the local `venv` folder and installs the Python requirements.
- `run.bat` activates that environment and launches `main.py`.

If you prefer to run things manually, you can still create and activate a virtual environment yourself, but that is no longer required for normal use.

## Optional Manual Setup

```bash
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

## Usage

```bash
.\venv\Scripts\activate
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
