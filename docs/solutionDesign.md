# Solution Design

## Objective

Automate transaction reconciliation between internal records and bank records.

## Inputs

- internalTransactions.csv
- bankTransactions.csv, or a PDF bank statement passed with `--bank-statement`

## Required Fields

- transaction_id
- date
- currency
- amount
- status

## Processing

The application:

1. Loads the internal transaction CSV file, and the bank transactions from either the bank CSV file or a PDF statement extracted with Claude.
2. Validates the presence of required columns.
3. Normalizes currency values.
4. Checks for missing and duplicate transaction IDs.
5. Checks for invalid amounts.
6. Checks for invalid dates.
7. Checks for unsupported currencies.
8. Identifies supported currencies used by the input datasets.
9. Retrieves EUR-based exchange rates from an external REST API.
10. Continues reconciliation if the FX service is unavailable.
11. Sets aside rows with blank or duplicated transaction IDs for manual review.
12. Merges the remaining internal and bank rows using `transaction_id`.
13. Identifies transactions missing from either source.
14. Compares transaction amounts to the cent, converting with FX rates when the currencies differ.
15. Compares transaction statuses.
16. Compares transaction currencies.
17. Builds a reconciliation summary.
18. Generates a formatted multi-sheet Excel report.

## Outputs

The application generates:

output/reconciliationReport.xlsx

When a PDF statement is used, the extracted bank transactions are also saved to:

output/extractedBankTransactions.csv

The Excel report contains the following sheets:
- Summary
- FX Rates
- Matched By ID
- Missing From Bank
- Missing From Internal
- Amount Mismatches
- Status Mismatches
- Currency Mismatches
- Excluded From Matching
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

The rates are used to compare amounts when the internal and bank currencies differ. The bank amount is converted into the internal currency and compared within `FX_TOLERANCE` (1%), because current rates are used rather than the rates on the transaction date.

If the service is unavailable or returns an unexpected response, the application logs a warning, skips the cross-currency amount comparison and continues generating the reconciliation report.

## LLM Document Extraction

PDF bank statements are sent to the Claude API (`claude-opus-5-5`) as a base64 document. Structured outputs constrain the response to a JSON schema with the required fields, so the extracted rows have the same columns and types as `bankTransactions.csv`.

Claude is instructed to copy values as printed rather than correct them. Validation and reconciliation remain deterministic Python code, so the model only reads the document and never decides whether a transaction matches.

If the API key is missing, the API call fails, or the response is incomplete (`max_tokens` or `refusal`), a `StatementExtractionError` is raised and the run fails rather than reconciling partial data.

## Error Handling

The application handles:

- missing input files
- empty input files
- missing required columns
- invalid transaction data
- unsupported currencies
- exchange-rate API failures
- PDF statement extraction failures
- output file access errors

Any failure is logged and the process exits with code `1`, so schedulers and RPA tools can detect failed runs.

## Testing

Automated tests are implemented using pytest.

The test suite covers:

- missing transactions
- missing transaction IDs
- blank and duplicated IDs excluded from matching
- amount mismatches, rounding noise and tolerances
- cross-currency amount comparison
- status mismatches
- currency mismatches
- missing required columns
- duplicate transaction IDs
- invalid amounts
- invalid dates
- currency normalization
- invalid currencies
- successful exchange-rate API responses
- exchange-rate API failures and unexpected responses
- end-to-end runs, including exit codes and runs without FX data
- Excel report layout and amount formatting
- PDF statement extraction with a mocked Claude API client
- end-to-end runs with an extracted statement
