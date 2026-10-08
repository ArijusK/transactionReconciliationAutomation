from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"

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
    
def find_invalid_transactions(df):
    missing_ids = df[
        df["transaction_id"].isna()
    ]

    duplicate_ids = df[
        df["transaction_id"].duplicated(keep=False)
    ]

    return missing_ids, duplicate_ids

def find_invalid_amounts(df):
    numeric_amounts = pd.to_numeric(
        df["amount"],
        errors="coerce"
    )

    invalid_amounts = df[
        numeric_amounts.isna()
    ]

    return invalid_amounts

def find_invalid_dates(df):
    parsed_dates = pd.to_datetime(
        df["date"],
        errors="coerce"
    )

    invalid_dates = df[
        parsed_dates.isna()
    ]

    return invalid_dates

def print_summary(
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
        bank_invalid_dates,       
):
    print("\nRECONCILATION SUMMARY")
    print("----------------------")
    print(f"Internal transactions: {len(internal_df)}")
    print(f"Bank transactions: {len(bank_df)}")
    print(f"Missing from bank: {len(missing_from_bank)}")
    print(f"Missing from internal: {len(missing_from_internal)}")
    print(f"Amount mismatches: {len(amount_mismatches)}")
    print(f"Status mismatches: {len(status_mismatches)}")
    print(f"Internal duplicates: {len(internal_duplicates)}")
    print(f"Bank duplicates: {len(bank_duplicates)}")
    print(f"Internal invalid amounts: {len(internal_invalid_amounts)}")
    print(f"Bank invalid amounts: {len(bank_invalid_amounts)}")
    print(f"Internal invalid dates: {len(internal_invalid_dates)}")
    print(f"Bank invalid dates: {len(bank_invalid_dates)}")

def export_results(
        missing_from_bank,
        missing_from_internal,
        amount_mismatches,
        status_mismatches
):
    OUTPUT_DIR.mkdir(exist_ok=True)

    report_path = OUTPUT_DIR / "reconcilationReport.xlsx"

    with pd.ExcelWriter(report_path, engine="openpyxl") as writer:
        missing_from_bank.to_excel(
            writer,
            sheet_name="Missing From Bank",
            index=False
        )
        
        missing_from_internal.to_excel(
            writer,
            sheet_name="Missing From Internal",
            index=False
        )
    
        amount_mismatches[
            [
                "transaction_id",
                "amount_internal",
                "amount_bank"
            ]
        ].to_excel(
            writer,
            sheet_name="Amount Miscmatches",
            index=False
        )
    
        status_mismatches[
            [
                "transaction_id",
                "status_internal",
                "status_bank"
            ]
        ].to_excel(
            writer,
            sheet_name="Status Mismatches",
            index=False
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

    reconciled = reconcile_transcations(
        internal_df,
        bank_df
    )

    missing_from_bank, missing_from_internal = (
        find_missing_transactions(reconciled)
    )

    amount_mismatches = find_amount_mismatches(reconciled)
    status_mismatches = find_status_mismatches(reconciled)

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
        missing_from_bank,
        missing_from_internal,
        amount_mismatches,
        status_mismatches
    )


if __name__ == "__main__":
    main()


