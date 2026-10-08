from pathlib import Path

from src.loader import load_transactions
from src.validator import (
    validate_columns,
    find_invalid_transactions,
    find_invalid_amounts,
    find_invalid_dates,
)
from src.reconciler import (
    reconcile_transactions,
    find_missing_transactions,
    find_amount_mismatches,
    find_status_mismatches,
)
from src.report import (
    build_summary,
    print_summary,
    export_results,
)

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

REQUIRED_COLUMNS = [
    "transaction_id",
    "date",
    "currency",
    "amount",
    "status"
]


def main():
    internal_file = DATA_DIR / "internalTransactions.csv"
    bank_file = DATA_DIR / "bankTransactions.csv"

    internal_df = load_transactions(internal_file)
    bank_df = load_transactions(bank_file)

    validate_columns(
        internal_df,
        REQUIRED_COLUMNS,
        "internalTransactions.csv"
    )

    validate_columns(
        bank_df,
        REQUIRED_COLUMNS,
        "bankTransactions.csv"
    )

    reconciled = reconcile_transactions(
        internal_df,
        bank_df
    )

    missing_from_bank, missing_from_internal = (
            find_missing_transactions(reconciled)
    )
    
    amount_mismatches = find_amount_mismatches(reconciled)
    status_mismatches = find_status_mismatches(reconciled)


    internal_missing_ids, internal_duplicates = (
        find_invalid_transactions(internal_df)
    )

    bank_missing_ids, bank_duplicates = (
        find_invalid_transactions(bank_df)
    )

    internal_invalid_amounts = find_invalid_amounts(internal_df)
    bank_invalid_amounts = find_invalid_amounts(bank_df)

    internal_invalid_dates = find_invalid_dates(internal_df)
    bank_invalid_dates = find_invalid_dates(bank_df) 

    summary_df = build_summary(
        internal_df,
        bank_df,
        missing_from_bank,
        missing_from_internal,
        amount_mismatches,
        status_mismatches
    )

    print_summary(
        internal_df,
        bank_df,
        missing_from_bank,
        missing_from_internal,
        amount_mismatches,
        status_mismatches,
        internal_duplicates,
        bank_duplicates,
        internal_invalid_amounts,
        bank_invalid_amounts,
        internal_invalid_dates,
        bank_invalid_dates
    )

    export_results(
        summary_df,
        missing_from_bank,
        missing_from_internal,
        amount_mismatches,
        status_mismatches
    )


if __name__ == "__main__":
    main()


