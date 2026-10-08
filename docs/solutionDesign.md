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

1. Loads internal and bank transaction CSV files.
2. Validates the presence of required columns.
3. Normalizes currency values.
4. Checks for missing and duplicate transaction IDs.
5. Checks for invalid amounts.
6. Checks for invalid dates.
7. Checks for unsupported currencies.
8. Identifies supported currencies used by the input datasets.
9. Retrieves EUR-based exchange rates from an external REST API.
10. Continues reconciliation if the FX service is unavailable.
11. Merges internal and bank datasets using `transaction_id`.
12. Identifies transactions missing from either source.
13. Compares transaction amounts.
14. Compares transaction statuses.
15. Compares transaction currencies.
16. Builds a reconciliation summary.
17. Generates a formatted multi-sheet Excel report.

## Outputs

The application generates:

output/reconciliationReport.xlsx

The Excel report contains the following sheets:
- Summary
- FX Rates
- Missing From Bank
- Missing From Internal
- Amount Mismatches
- Status Mismatches
- Currency Mismatches
- Internal Missing IDs
- Bank Missing IDs
- Internal Duplicates
- Bank Duplicates
- Internal Invalid Amounts
- Bank Invalid Amounts
- Internal Invalid Dates
- Bank Invalid Dates
- Internal Bad Currency
- Bank Bad Currency

## External Integration

The application retrieves EUR-based exchange rates from an external REST API for supported currencies present in the transaction data.

The FX integration is supplementary. If the service is unavailable, the application logs a warning and continues generating the reconciliation report.

## Error Handling

The application handles:

- missing input files
- empty input files
- missing required columns
- invalid transaction data
- unsupported currencies
- exchange-rate API failures
- output file access errors

## Testing

Automated tests are implemented using pytest.

The test suite covers:

- missing transactions
- missing transaction IDs
- amount mismatches
- status mismatches
- currency mismatches
- missing required columns
- duplicate transaction IDs
- invalid amounts
- invalid dates
- currency normalization
- invalid currencies
- successful exchange-rate API responses
- exchange-rate API failures