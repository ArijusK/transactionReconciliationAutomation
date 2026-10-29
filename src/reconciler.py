import pandas as pd


def split_unmatchable(internal_df, bank_df):
    duplicated_ids = set(
        internal_df.loc[internal_df["transaction_id"].duplicated(), "transaction_id"]
    ) | set(
        bank_df.loc[bank_df["transaction_id"].duplicated(), "transaction_id"]
    )

    def is_unmatchable(df):
        return (
            df["transaction_id"].isna()
            | df["transaction_id"].isin(duplicated_ids)
        )

    internal_excluded = is_unmatchable(internal_df)
    bank_excluded = is_unmatchable(bank_df)

    excluded = pd.concat(
        [
            internal_df[internal_excluded].assign(source="internal"),
            bank_df[bank_excluded].assign(source="bank"),
        ],
        ignore_index=True,
    )

    return (
        internal_df[~internal_excluded],
        bank_df[~bank_excluded],
        excluded,
    )

def reconcile_transactions(internal_df, bank_df):
    internal_df, bank_df, _ = split_unmatchable(
        internal_df,
        bank_df
    )

    return internal_df.merge(
        bank_df,
        on="transaction_id",
        how="outer",
        suffixes=("_internal", "_bank"),
        indicator=True,
        validate="one_to_one"
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

    amount_internal = pd.to_numeric(both["amount_internal"], errors="coerce")
    amount_bank = pd.to_numeric(both["amount_bank"], errors="coerce")

    comparable = amount_internal.notna() & amount_bank.notna()

    return both[
        comparable & (amount_internal != amount_bank)
    ]

def find_status_mismatches(reconciled):
    both = reconciled[
           reconciled["_merge"] == "both"
        ].copy()

    return both[
        both["status_internal"] != both["status_bank"]
    ]

def find_currency_mismatches(reconciled):
    both = reconciled[
        reconciled["_merge"] == "both"
    ].copy()

    return both[
        both["currency_internal"] != both["currency_bank"]
    ]