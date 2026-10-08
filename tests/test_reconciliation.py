import pandas as pd
import pytest

from src.main import (
    reconcile_transactions,
    find_missing_transactions,
    find_amount_mismatches,
    find_status_mismatches,
    validate_columns,
    find_invalid_transactions,
    find_invalid_amounts,
    find_invalid_dates,
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

def test_missing_required_column():
    df = pd.DataFrame({
        "transaction_id": ["TX001"],
        "date": ["2026-10-01"],
        "currency": ["EUR"],
        "status": ["SETTLED"],
    })

    required_columns = [
        "transaction_id",
        "date",
        "currency",
        "amount",
        "status",
    ]

    with pytest.raises(ValueError):
        validate_columns(
            df,
            required_columns,
            "test.csv"
        )

def test_duplicate_transaction_ids():
    df = pd.DataFrame({
        "transaction_id": ["TX001", "TX001"],
        "date": ["2026-10-01", "2026-10-01"],
        "currency": ["EUR", "EUR"],
        "amount": [100.0, 100.0],
        "status": ["SETTLED", "SETTLED"],
    })

    missing_ids, duplicate_ids = (
        find_invalid_transactions(df)
    )

    assert len(missing_ids) == 0
    assert len(duplicate_ids) == 2

def test_invalid_amount():
    df = pd.DataFrame({
        "transaction_id": ["TX001"],
        "date": ["2026-10-01"],
        "currency": ["EUR"],
        "amount": ["not-a-number"],
        "status": ["SETTLED"],
    })

    invalid_amounts = find_invalid_amounts(df)

    assert len(invalid_amounts) == 1

def test_invalid_date():
    df = pd.DataFrame({
        "transaction_id": ["TX001"],
        "date": ["not-a-date"],
        "currency": ["EUR"],
        "amount": [100.0],
        "status": ["SETTLED"],
    })

    invalid_dates = find_invalid_dates(df)

    assert len(invalid_dates) == 1