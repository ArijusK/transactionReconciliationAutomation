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
2. Input files are validated.
3. Transactions are matched automatically using transaction IDs.
4. Missing transactions and mismatches are identified.
5. A reconciliation summary is generated.
6. An Excel report is created automatically.
7. Analyst reviews only the exceptions.

## Expected Benefits

- Reduced manual comparison work
- Faster reconciliation
- More consistent exception detection
- Reduced risk of human error
- Easier review of discrepancies