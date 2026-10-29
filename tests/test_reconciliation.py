import pandas as pd
import pytest

from src.reconciler import (
    reconcile_transactions,
    find_missing_transactions,
    find_amount_mismatches,
    find_status_mismatches,
    find_currency_mismatches,
    split_unmatchable,
)

from src.validator import (
    validate_columns,
    find_invalid_transactions,
    find_invalid_amounts,
    find_invalid_dates,
    normalize_currency,
    find_invalid_currencies,
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

def test_missing_transaction_id():
    df = pd.DataFrame({
        "transaction_id": ["TX001", None],
        "date": ["2026-10-01", "2026-10-02"],
        "currency": ["EUR", "EUR"],
        "amount": [100.0, 200.0],
        "status": ["SETTLED", "SETTLED"],
    })

    missing_ids, duplicate_ids = find_invalid_transactions(df)

    assert len(missing_ids) == 1
    assert len(duplicate_ids) == 0

def test_blank_ids_are_not_matched_together():
    internal_df = pd.DataFrame({
        "transaction_id": ["TX001", None],
        "date": ["2026-10-01", "2026-10-02"],
        "currency": ["EUR", "EUR"],
        "amount": [100.0, 999.0],
        "status": ["SETTLED", "SETTLED"],
    })

    bank_df = pd.DataFrame({
        "transaction_id": ["TX001", None],
        "date": ["2026-10-01", "2026-10-02"],
        "currency": ["EUR", "USD"],
        "amount": [100.0, 5.0],
        "status": ["SETTLED", "PENDING"],
    })

    reconciled = reconcile_transactions(
        internal_df,
        bank_df
    )

    assert reconciled["transaction_id"].tolist() == ["TX001"]

def test_duplicate_ids_are_set_aside():
    internal_df = pd.DataFrame({
        "transaction_id": ["TX001", "TX001", "TX002"],
        "date": ["2026-10-01", "2026-10-01", "2026-10-02"],
        "currency": ["EUR", "EUR", "EUR"],
        "amount": [100.0, 100.0, 200.0],
        "status": ["SETTLED", "SETTLED", "SETTLED"],
    })

    bank_df = pd.DataFrame({
        "transaction_id": ["TX001", "TX002"],
        "date": ["2026-10-01", "2026-10-02"],
        "currency": ["EUR", "EUR"],
        "amount": [100.0, 200.0],
        "status": ["SETTLED", "SETTLED"],
    })

    reconciled = reconcile_transactions(
        internal_df,
        bank_df
    )

    missing_from_bank, missing_from_internal = (
        find_missing_transactions(reconciled)
    )

    assert reconciled["transaction_id"].tolist() == ["TX002"]
    assert len(missing_from_bank) == 0
    assert len(missing_from_internal) == 0

    _, _, excluded = split_unmatchable(
        internal_df,
        bank_df
    )

    assert excluded["source"].tolist() == [
        "internal",
        "internal",
        "bank",
    ]

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

def make_pair(internal_amount, bank_amount, internal_currency="EUR", bank_currency="EUR"):
    internal_df = pd.DataFrame({
        "transaction_id": ["TX001"],
        "date": ["2026-10-01"],
        "currency": [internal_currency],
        "amount": [internal_amount],
        "status": ["SETTLED"],
    })

    bank_df = pd.DataFrame({
        "transaction_id": ["TX001"],
        "date": ["2026-10-01"],
        "currency": [bank_currency],
        "amount": [bank_amount],
        "status": ["SETTLED"],
    })

    return reconcile_transactions(internal_df, bank_df)

def test_floating_point_noise_is_not_a_mismatch():
    reconciled = make_pair(0.1 + 0.2, 0.3)

    assert len(find_amount_mismatches(reconciled)) == 0

def test_amount_tolerance():
    reconciled = make_pair(100.00, 100.01)

    assert len(find_amount_mismatches(reconciled)) == 1
    assert len(find_amount_mismatches(reconciled, tolerance=0.01)) == 0

def test_amount_mismatch_reports_difference():
    reconciled = make_pair(810.50, 800.50)

    amount_mismatches = find_amount_mismatches(reconciled)

    assert amount_mismatches.iloc[0]["difference"] == 10.0

FX_RATES = {"EUR": 1.0, "USD": 1.15}

def test_cross_currency_amounts_are_converted():
    reconciled = make_pair(100.00, 115.00, "EUR", "USD")

    assert len(find_amount_mismatches(reconciled, FX_RATES)) == 0

def test_cross_currency_mismatch_is_flagged():
    reconciled = make_pair(100.00, 150.00, "EUR", "USD")

    amount_mismatches = find_amount_mismatches(reconciled, FX_RATES)

    assert len(amount_mismatches) == 1
    assert amount_mismatches.iloc[0]["bank_amount_converted"] == 130.43
    assert amount_mismatches.iloc[0]["difference"] == -30.43

def test_cross_currency_within_fx_tolerance():
    reconciled = make_pair(100.00, 115.50, "EUR", "USD")

    assert len(find_amount_mismatches(reconciled, FX_RATES)) == 0

def test_cross_currency_without_rate_is_not_compared():
    reconciled = make_pair(100.00, 150.00, "EUR", "USD")

    assert len(find_amount_mismatches(reconciled)) == 0
    assert len(find_currency_mismatches(reconciled)) == 1

def test_invalid_amount_does_not_flag_other_rows():
    internal_df = pd.DataFrame({
        "transaction_id": ["TX001", "TX002", "TX003"],
        "date": ["2026-10-01", "2026-10-01", "2026-10-01"],
        "currency": ["EUR", "EUR", "EUR"],
        "amount": ["100.00", "200.00", "not-a-number"],
        "status": ["SETTLED", "SETTLED", "SETTLED"],
    })

    bank_df = pd.DataFrame({
        "transaction_id": ["TX001", "TX002", "TX003"],
        "date": ["2026-10-01", "2026-10-01", "2026-10-01"],
        "currency": ["EUR", "EUR", "EUR"],
        "amount": [100.0, 200.0, 300.0],
        "status": ["SETTLED", "SETTLED", "SETTLED"],
    })

    reconciled = reconcile_transactions(
        internal_df,
        bank_df
    )

    amount_mismatches = find_amount_mismatches(
        reconciled
    )

    assert len(amount_mismatches) == 0

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

def test_currency_normalization():
    df = pd.DataFrame({
        "currency": [" eur ", "usd", "GBP"],
    })

    result = normalize_currency(df)

    assert result["currency"].tolist() == [
        "EUR",
        "USD",
        "GBP",
    ]

def test_invalid_currency():
    df = pd.DataFrame({
        "currency": ["EUR", "XYZ"],
    })

    invalid = find_invalid_currencies(df)

    assert len(invalid) == 1
    assert invalid.iloc[0]["currency"] == "XYZ"

def test_currency_mismatch():
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
        "currency": ["USD"],
        "amount": [100.0],
        "status": ["SETTLED"],
    })

    reconciled = reconcile_transactions(
        internal_df,
        bank_df
    )

    currency_mismatches = find_currency_mismatches(
        reconciled
    )

    assert len(currency_mismatches) == 1
    assert (
        currency_mismatches.iloc[0]["transaction_id"]
        == "TX001"
    )