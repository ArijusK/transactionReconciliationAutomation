from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

REQUIRED_COLUMNS = [
    "transaction_id",
    "date",
    "currency",
    "amount",
    "status"
]

def load_transactions(file_path):
    return pd.read_csv(file_path)

def reconcile_transcations(internal_df, bank_df):
    return internal_df.merge(
        bank_df,
        on="transaction_id",
        how="outer",
        suffixes=("_internal", "_bank"),
        indicator=True
    )

def find_missing_transactions(reconciled):
    missing_from_bank = reconciled[
        reconciled["_merge"] == "left_only"
    ]

    missing_from_internal = reconciled[
        reconciled["_merge"] == "right_only"
    ]

    return missing_from_bank, missing_from_internal

def find_amount_mismatches(reconciled):
    both = reconciled[
       reconciled["_merge"] == "both"
    ].copy()

    return both[
        both["amount_internal"] != both["amount_bank"]
    ]

def find_status_mismatches(reconciled):
    both = reconciled[
           reconciled["_merge"] == "both"
        ].copy()

    return both[
        both["status_internal"] != both["status_bank"]
    ]

def validate_columns(df, required_columns, file_name):
    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"{file_name} is missing required columns: {missing_columns}"
        )
    

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

    reconciled = reconcile_transcations(
        internal_df,
        bank_df
    )

    missing_from_bank, missing_from_internal = (
        find_missing_transactions(reconciled)
    )

    amount_mismatches = find_amount_mismatches(reconciled)
    status_mismatches = find_status_mismatches(reconciled)

    print("\nMISSING FROM BANK")
    print(missing_from_bank)

    print("\nMISSING FROM INTERNAL")
    print(missing_from_internal)

    print("\nAMOUNT MISMATCHES")
    print(
        amount_mismatches[
            [
                "transaction_id",
                "amount_internal",
                "amount_bank",
            ]
        ]
    )

    print("\nSTATUS MISMATCHES")
    print(
        status_mismatches[
            [
                "transaction_id",
                "status_internal",
                "status_bank",
            ]
        ]
    )


if __name__ == "__main__":
    main()


