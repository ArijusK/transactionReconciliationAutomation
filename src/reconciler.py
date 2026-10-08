def reconcile_transactions(internal_df, bank_df):
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