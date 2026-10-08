from pathlib import Path
import logging
import pandas as pd

from src.exchange_rates import (
    get_exchange_rates,
    ExchangeRateError,
)

from src.loader import load_transactions
from src.validator import (
    VALID_CURRENCIES,
    validate_columns,
    find_invalid_transactions,
    find_invalid_amounts,
    find_invalid_dates,
    normalize_currency,
    find_invalid_currencies
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

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s"
)

def main():
    internal_file = DATA_DIR / "internalTransactions.csv"
    bank_file = DATA_DIR / "bankTransactions.csv"

    logging.info("Loading transaction files")

    internal_df = load_transactions(internal_file)
    bank_df = load_transactions(bank_file)

    logging.info("Validating input data")

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

    internal_df = normalize_currency(internal_df)
    bank_df = normalize_currency(bank_df)

    used_currencies = set(
    internal_df["currency"]
    ).union(
        set(bank_df["currency"])
    )

    valid_used_currencies = (
    used_currencies & VALID_CURRENCIES
    )

    try:
        logging.info("Fetching exchange rates")

        exchange_rates = get_exchange_rates(
            valid_used_currencies,
            base_currency="EUR"
        )

        fx_summary_df = pd.DataFrame(exchange_rates)

    except ExchangeRateError as error:
        logging.warning(error)
        fx_summary_df = pd.DataFrame()

    logging.info("Reconciling transactions")

    reconciled = reconcile_transactions(
        internal_df,
        bank_df
    )

    missing_from_bank, missing_from_internal = (
            find_missing_transactions(reconciled)
    )
    
    amount_mismatches = find_amount_mismatches(reconciled)
    status_mismatches = find_status_mismatches(reconciled)

    internal_invalid_currencies = find_invalid_currencies(
    internal_df
    )

    bank_invalid_currencies = find_invalid_currencies(
        bank_df
    )
    
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
        status_mismatches,
        internal_missing_ids,
        bank_missing_ids,
        internal_duplicates,
        bank_duplicates,
        internal_invalid_amounts,
        bank_invalid_amounts,
        internal_invalid_dates,
        bank_invalid_dates,
        internal_invalid_currencies,
        bank_invalid_currencies,
    )   

    print_summary(
        internal_df,
        bank_df,
        missing_from_bank,
        missing_from_internal,
        amount_mismatches,
        status_mismatches,
        internal_missing_ids,
        bank_missing_ids,
        internal_duplicates,
        bank_duplicates,
        internal_invalid_amounts,
        bank_invalid_amounts,
        internal_invalid_dates,
        bank_invalid_dates,
        internal_invalid_currencies,
        bank_invalid_currencies,
    )

    export_results(
        summary_df,
        fx_summary_df,
        missing_from_bank,
        missing_from_internal,
        amount_mismatches,
        status_mismatches,
        internal_missing_ids,
        bank_missing_ids,
        internal_duplicates,
        bank_duplicates,
        internal_invalid_amounts,
        bank_invalid_amounts,
        internal_invalid_dates,
        bank_invalid_dates,
        internal_invalid_currencies,
        bank_invalid_currencies,
    )

    logging.info("Reconciliation report generated successfully")


if __name__ == "__main__":
    try:
        main()

    except Exception as error:
        logging.error(error)


