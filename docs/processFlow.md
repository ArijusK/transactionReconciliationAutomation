# Process Flow

## Current State (AS-IS)

1. Analyst receives internal transaction records.
2. Analyst receives bank transaction records.
3. Analyst opens both files.
4. Transactions are compared manually.
5. Missing or mismatched transactions are identified.
6. Analyst creates an exception report.
7. Exceptions are reviewed manually.

## Future State (TO-BE)

1. Internal and bank transaction files are provided to the Python automation.
2. Required columns are validated.
3. Currency values are normalized.
4. Data-quality issues such as missing IDs, duplicates, invalid amounts, invalid dates, and invalid currencies are identified.
5. Relevant exchange rates are retrieved from an external API when available.
6. Transactions are matched automatically using transaction IDs.
7. Missing transactions and amount, status, and currency mismatches are identified.
8. A reconciliation summary is generated.
9. An Excel report is created automatically.
10. The analyst reviews the generated exceptions and validation results.

## Expected Benefits

- Reduced manual comparison work
- Faster reconciliation
- More consistent exception detection
- Reduced risk of human error
- Easier review of discrepancies