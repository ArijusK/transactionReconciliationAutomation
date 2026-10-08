import pandas as pd

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

    return df[
        numeric_amounts.isna()
    ]

def find_invalid_dates(df):
    parsed_dates = pd.to_datetime(
        df["date"],
        errors="coerce"
    )

    return df[
        parsed_dates.isna()
    ]

