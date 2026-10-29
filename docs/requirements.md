# Business Requirements

## Business Problem

Operations teams may need to compare internal transaction records with bank transaction records.

Manual reconciliation is repetitive and can make it harder to consistently identify missing or mismatched transactions.

## Goal

Automate transaction reconciliation so that analysts can focus on reviewing exceptions instead of comparing every transaction manually.

## User Stories

### Story 1: Reconcile transactions

As an operations analyst, I want internal and bank transactions to be matched automatically so that I can quickly identify discrepancies.

#### Acceptance Criteria

- Transactions are matched using `transaction_id`.
- Transactions present in both sources are compared.
- Transactions missing from either source are identified.
- Transactions with a blank or duplicated ID are excluded from matching and listed for manual review.
- The reconciliation completes without manual row-by-row comparison.

### Story 2: Detect amount mismatches

As an operations analyst, I want amount differences to be identified automatically so that incorrect transaction values can be investigated.

#### Acceptance Criteria

- The internal amount is compared with the bank amount, to the cent.
- A transaction is flagged when the difference is larger than the configured tolerance.
- When the currencies differ, the bank amount is converted into the internal currency using FX rates and compared within an FX tolerance.
- Rows with an invalid amount are not compared; they are reported by validation.
- The report shows the transaction ID, both currencies and amounts, the converted amount and the difference.

### Story 3: Detect status mismatches

As an operations analyst, I want status differences to be identified so that inconsistent transaction states can be reviewed.

#### Acceptance Criteria

- Internal and bank statuses are compared.
- A transaction is flagged when the statuses differ.
- The report shows both status values.

### Story 4: Detect currency mismatches

As an operations analyst, I want currency differences to be identified so that transactions with inconsistent currencies can be investigated.

#### Acceptance Criteria

- Internal and bank currencies are compared for matching transaction IDs.
- A transaction is flagged when the currencies differ.
- The report shows the transaction ID and both currency values.

### Story 5: Validate input data

As an automation user, I want invalid input data to be detected before reconciliation so that unreliable data does not silently produce incorrect results.

#### Acceptance Criteria

- Required columns are checked.
- Missing transaction IDs are detected.
- Duplicate transaction IDs are detected.
- Invalid amounts are detected.
- Invalid dates are detected.
- Currency values are normalized before comparison.
- Unsupported currencies are identified.

### Story 6: Generate a reconciliation report

As an operations analyst, I want reconciliation results exported into an Excel report so that I can review and share the results easily.

#### Acceptance Criteria

- A summary sheet is generated, including the number of transactions matched by ID.
- Transactions matched by ID are listed with the internal and bank values side by side.
- Missing transactions are shown in separate sheets, with only the columns from the side that has the transaction.
- Amount mismatches are shown in a dedicated sheet.
- Status mismatches are shown in a dedicated sheet.
- The Excel report is saved in the `output` directory.
- Currency mismatches are shown in a dedicated sheet.
- Amounts are shown with two decimals.

### Story 7: Retrieve exchange-rate information

As an operations analyst, I want amounts in different currencies to be compared using exchange rates, and the rates included in the report, so that I can see whether a cross-currency transaction has the same value.

#### Acceptance Criteria

- Exchange rates are retrieved only for supported currencies used in the input data.
- EUR is used as the base currency.
- Exchange-rate results are included in an FX Rates worksheet.
- Exchange rates are used to compare amounts in different currencies.
- If the exchange-rate API is unavailable or returns an unexpected response, the reconciliation still completes and amounts in different currencies are not compared.
- A warning is logged when FX data cannot be retrieved.

### Story 8: Extract bank transactions from PDF statements

As an operations analyst, I want bank transactions to be extracted from PDF bank statements automatically so that I can reconcile them without retyping the statement into a spreadsheet.

#### Acceptance Criteria

- A PDF statement can be passed with `--bank-statement` instead of reading `bankTransactions.csv`.
- Extracted transactions have the same columns as `bankTransactions.csv`.
- Values are copied as printed, so invalid values are still reported by validation.
- Extracted transactions are saved to `output/extractedBankTransactions.csv` for review.
- If extraction fails or is incomplete, the run fails with a clear error instead of reconciling partial data.
- Automated tests do not call the API.

## Definition of Done

A feature is considered complete when:

- the implementation works as intended;
- relevant automated tests pass;
- input errors are handled appropriately;
- documentation is updated when necessary;
- the application runs successfully from the project root;
- the application exits with a non-zero status when it fails.