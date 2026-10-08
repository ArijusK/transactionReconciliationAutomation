# Solution Design

## Objective

Automate transaction reconciliation between internal records and bank records.

## Inputs

- internalTransactions.csv
- bankTransactions.csv

## Required Fields

- transaction_id
- date
- currency
- amount
- status

## Processing

The application:

1. Loads both CSV files.
2. Validates required columns.
3. Checks for missing and duplicate transaction IDs.
4. Checks for invalid amounts and dates.
5. Merges datasets using transaction_id.
6. Identifies missing transactions.
7. Compares transaction amounts.
8. Compares transaction statuses.
9. Builds a reconciliation summary.
10. Generates an Excel report.

## Outputs

The application generates:

```text
output/reconciliationReport.xlsx