import pandas as pd

VALID_CURRENCIES = {
    "EUR",
    "USD",
    "GBP",
}

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

def normalize_currency(df):
    df = df.copy()

    df["currency"] = (
        df["currency"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    return df

def find_invalid_currencies(df):
    return df[
        ~df["currency"].isin(VALID_CURRENCIES)
    ]