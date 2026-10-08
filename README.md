# Transaction Reconciliation Automation

A Python-based automation project that compares internal transaction records with bank transaction records, validates input data, identifies discrepancies, and generates a structured Excel reconciliation report.

This project was built to simulate a real-world financial operations automation workflow.

## Business Problem

Financial operations teams often need to compare transaction data from multiple systems to confirm that records match correctly.

Performing this process manually can be:

- repetitive
- time-consuming
- prone to human error
- difficult to scale as transaction volume increases

The goal of this project is to automate the reconciliation process and allow an analyst to focus only on transactions that require investigation.

## Solution

The application loads transaction data from two CSV files:

- internal transaction records
- bank transaction records

It then validates the input data, reconciles transactions using their transaction IDs, identifies exceptions, and generates an Excel report containing the reconciliation results.

## Features

The application currently supports:

- CSV transaction data loading
- required-column validation
- missing transaction ID detection
- duplicate transaction ID detection
- invalid amount detection
- invalid date detection
- transaction matching by transaction ID
- detection of transactions missing from bank records
- detection of transactions missing from internal records
- amount mismatch detection
- status mismatch detection
- reconciliation summary generation
- multi-sheet Excel report generation
- automatic Excel column sizing
- frozen Excel header rows
- logging
- basic error handling
- automated testing with pytest

## Example Reconciliation

The sample datasets contain several intentionally introduced exceptions.

The automation detects:

| Transaction | Issue |
|---|---|
| TX003 | Amount mismatch |
| TX005 | Missing from bank records |
| TX006 | Status mismatch |
| TX007 | Missing from internal records |

Example:

```text
TX003

Internal amount: 810.50
Bank amount:     800.50
```

## Reconciliation Workflow

```text
Internal Transactions        Bank Transactions
          │                         │
          └──────────┬──────────────┘
                     │
                     ▼
              Load CSV Files
                     │
                     ▼
              Validate Data
                     │
                     ▼
          Match Transaction IDs
                     │
                     ▼
            Compare Transactions
                     │
          ┌──────────┼──────────┐
          ▼          ▼          ▼
       Missing     Amount     Status
     Transactions Mismatch   Mismatch
          │          │          │
          └──────────┼──────────┘
                     ▼
              Generate Report
                     │
                     ▼
        reconciliationReport.xlsx
```

## Project Structure

```text
TransactionReconciliationAutomation/
│
├── data/
│   ├── internalTransactions.csv
│   └── bankTransactions.csv
│
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── loader.py
│   ├── validator.py
│   ├── reconciler.py
│   └── report.py
│
├── tests/
│   └── test_reconciliation.py
│
├── output/
│
├── .gitignore
├── README.md
└── requirements.txt
```

## Module Responsibilities

### `loader.py`

Responsible for loading transaction files into pandas DataFrames.

### `validator.py`

Contains input validation logic including:

- required columns
- missing transaction IDs
- duplicate IDs
- invalid amounts
- invalid dates

### `reconciler.py`

Contains the main reconciliation logic including:

- transaction matching
- missing transaction detection
- amount mismatch detection
- status mismatch detection

### `report.py`

Responsible for:

- generating reconciliation summaries
- exporting results to Excel
- formatting Excel worksheets

### `main.py`

Coordinates the complete workflow.

## Technologies Used

- Python
- pandas
- openpyxl
- pytest
- Git
- GitHub

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/ArijusK/transactionReconciliationAutomation.git
```

### 2. Enter the project directory

```bash
cd transactionReconciliationAutomation
```

### 3. Create a virtual environment

```bash
python -m venv .venv
```

### 4. Activate the virtual environment

On Windows:

```bash
.venv\Scripts\activate
```

### 5. Install dependencies

```bash
python -m pip install -r requirements.txt
```

## Running the Application

From the project root directory, run:

```bash
python -m src.main
```

The application will:

1. load both transaction files
2. validate the input data
3. reconcile transactions
4. identify exceptions
5. print a summary
6. generate an Excel report

The generated report is saved to:

```text
output/reconciliationReport.xlsx
```

## Excel Report

The generated workbook contains multiple sheets:

- Summary
- Missing From Bank
- Missing From Internal
- Amount Mismatches
- Status Mismatches

The report includes formatted headers, automatic column sizing, and frozen header rows.

## Running Tests

Run the automated test suite with:

```bash
python -m pytest
```

The tests cover areas such as:

- missing transactions
- amount mismatches
- status mismatches
- missing required columns
- duplicate transaction IDs
- invalid amounts
- invalid dates

## Example Summary

```text
RECONCILIATION SUMMARY
----------------------
Internal transactions: 6
Bank transactions: 6
Missing from bank: 1
Missing from internal: 1
Amount mismatches: 1
Status mismatches: 1
Internal duplicates: 0
Bank duplicates: 0
Internal invalid amounts: 0
Bank invalid amounts: 0
Internal invalid dates: 0
Bank invalid dates: 0
```

## What I Learned

This project helped me practice:

- working with tabular data using pandas
- designing reusable Python functions
- separating application logic into modules
- validating business data
- handling exceptions
- generating Excel reports programmatically
- writing automated tests
- using Git and GitHub for version control
- thinking about automation from a business-process perspective

## Future Improvements

Possible future enhancements include:

- configurable input filenames
- currency validation
- exchange-rate API integration
- database storage
- command-line arguments
- logging to a file
- additional transaction matching rules
- configurable reconciliation tolerances
- richer Excel formatting
- automated report timestamps

## Purpose

This project was created as a portfolio project to demonstrate Python-based business process automation and financial data reconciliation.