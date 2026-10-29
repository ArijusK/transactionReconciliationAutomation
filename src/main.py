from pathlib import Path
import logging
import sys
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
    find_currency_mismatches,
    split_unmatchable,
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

    # Find validation problems
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

    internal_invalid_amounts = find_invalid_amounts(
        internal_df
    )

    bank_invalid_amounts = find_invalid_amounts(
        bank_df
    )

    internal_invalid_dates = find_invalid_dates(
        internal_df
    )

    bank_invalid_dates = find_invalid_dates(
        bank_df
    )

    # Only use valid currencies from valid rows
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

        fx_summary_df = pd.DataFrame(
            exchange_rates
        )

        fx_rates = {
            rate["quote_currency"]: rate["rate"]
            for rate in exchange_rates
        }

    except ExchangeRateError as error:
        logging.warning(error)
        logging.warning(
            "Amounts in different currencies will not be compared"
        )
        fx_summary_df = pd.DataFrame()
        fx_rates = {}


    logging.info("Reconciling transactions")

    _, _, excluded_from_matching = split_unmatchable(
        internal_df,
        bank_df
    )

    reconciled = reconcile_transactions(
        internal_df,
        bank_df
    )

    missing_from_bank, missing_from_internal = (
        find_missing_transactions(reconciled)
    )
    
    amount_mismatches = find_amount_mismatches(reconciled, fx_rates)
    status_mismatches = find_status_mismatches(reconciled)
    currency_mismatches = find_currency_mismatches(reconciled)

    results = {
        "missing_from_bank": missing_from_bank,
        "missing_from_internal": missing_from_internal,
        "amount_mismatches": amount_mismatches,
        "status_mismatches": status_mismatches,
        "currency_mismatches": currency_mismatches,
        "excluded_from_matching": excluded_from_matching,
        "internal_missing_ids": internal_missing_ids,
        "bank_missing_ids": bank_missing_ids,
        "internal_duplicates": internal_duplicates,
        "bank_duplicates": bank_duplicates,
        "internal_invalid_amounts": internal_invalid_amounts,
        "bank_invalid_amounts": bank_invalid_amounts,
        "internal_invalid_dates": internal_invalid_dates,
        "bank_invalid_dates": bank_invalid_dates,
        "internal_invalid_currencies": internal_invalid_currencies,
        "bank_invalid_currencies": bank_invalid_currencies,
    }

    summary_df = build_summary(internal_df, bank_df, results)

    print_summary(summary_df)

    export_results(summary_df, fx_summary_df, results)

    logging.info("Reconciliation report generated successfully")


def run():
    try:
        main()

    except Exception as error:
        logging.error(error)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(run())


