import pandas as pd

from src.main import (
    reconcile_transactions,
    find_missing_transactions,
    find_amount_mismatches,
    find_status_mismatches,
)


def test_missing_transactions():
    internal_df = pd.DataFrame({
        "transaction_id": ["TX001", "TX002"],
        "date": ["2026-10-01","2026-10-02"],
        "currency": ["EUR", "EUR"],
        "amount": [100.0, 200.0],
        "status": ["SETTLED", "SETTLED"],
    })

    bank_df = pd.DataFrame({
        "transaction_id": ["TX001", "TX003"],
        "date": ["2026-10-01", "2026-10-03"],
        "currency": ["EUR", "EUR"],
        "amount": [100.0, 300.0],
        "status": ["SETTLED", "SETTLED"],
    })

    reconciled = reconcile_transactions(
        internal_df,
        bank_df
    )

    missing_from_bank, missing_from_internal = (
        find_missing_transactions(reconciled)
    )

    assert len(missing_from_bank) == 1
    assert len(missing_from_internal) == 1

    assert (
        missing_from_bank.iloc[0]["transaction_id"]
        == "TX002"
    )

    assert (
        missing_from_internal.iloc[0]["transaction_id"]
        == "TX003"
    )

def test_amount_mismatch():
    internal_df = pd.DataFrame({
        "transaction_id": ["TX001"],
        "date": ["2026-10-01"],
        "currency": ["EUR"],
        "amount": [100.0],
        "status": ["SETTLED"],
    })

    bank_df = pd.DataFrame({
        "transaction_id": ["TX001"],
        "date": ["2026-10-01"],
        "currency": ["EUR"],
        "amount": [150.0],
        "status": ["SETTLED"],
    })

    reconciled = reconcile_transactions(
        internal_df,
        bank_df
    )

    amount_mismatches = find_amount_mismatches(
        reconciled
    )

    assert len(amount_mismatches) == 1
    assert (
        amount_mismatches.iloc[0]["transaction_id"]
        == "TX001"
    )

def test_status_mismatch():
    internal_df = pd.DataFrame({
        "transaction_id": ["TX001"],
        "date": ["2026-10-01"],
        "currency": ["EUR"],
        "amount": [100.0],
        "status": ["PENDING"],
    })

    bank_df = pd.DataFrame({
        "transaction_id": ["TX001"],
        "date": ["2026-10-01"],
        "currency": ["EUR"],
        "amount": [100.0],
        "status": ["SETTLED"],
    })

    reconciled = reconcile_transactions(
        internal_df,
        bank_df
    )

    status_mismatches = find_status_mismatches(
        reconciled
    )

    assert len(status_mismatches) == 1