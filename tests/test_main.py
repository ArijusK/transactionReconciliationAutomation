import pandas as pd
import requests

from unittest.mock import patch

import src.main
import src.report

from src.statement_extractor import StatementExtractionError


def test_run_fails_when_input_file_is_missing(tmp_path, monkeypatch):
    monkeypatch.setattr(src.main, "DATA_DIR", tmp_path)

    assert src.main.run() == 1


@patch("src.exchange_rates.requests.get")
def test_run_completes_without_fx_data(mock_get, tmp_path, monkeypatch):
    mock_get.side_effect = requests.ConnectionError()
    monkeypatch.setattr(src.report, "OUTPUT_DIR", tmp_path)

    assert src.main.run() == 0

    summary = pd.read_excel(
        tmp_path / "reconciliationReport.xlsx",
        sheet_name="Summary"
    ).set_index("Metric")["Count"]

    assert summary["Missing from bank"] == 1
    assert summary["Missing from internal"] == 1
    assert summary["Amount mismatches"] == 1
    assert summary["Status mismatches"] == 1
    assert summary["Currency mismatches"] == 1


@patch("src.exchange_rates.requests.get")
@patch("src.main.extract_transactions")
def test_run_reconciles_extracted_bank_statement(
    mock_extract, mock_get, tmp_path, monkeypatch
):
    mock_get.side_effect = requests.ConnectionError()
    mock_extract.return_value = pd.read_csv(
        src.main.DATA_DIR / "bankTransactions.csv"
    )
    monkeypatch.setattr(src.report, "OUTPUT_DIR", tmp_path)

    assert src.main.run(["--bank-statement", "statement.pdf"]) == 0

    mock_extract.assert_called_once()
    assert mock_extract.call_args.args[0].name == "statement.pdf"

    summary = pd.read_excel(
        tmp_path / "reconciliationReport.xlsx",
        sheet_name="Summary"
    ).set_index("Metric")["Count"]

    extracted = pd.read_csv(tmp_path / "extractedBankTransactions.csv")

    assert summary["Matched by ID"] == 5
    assert summary["Bank invalid currencies"] == 1
    assert len(extracted) == 6


@patch("src.main.extract_transactions")
def test_run_fails_when_statement_extraction_fails(mock_extract):
    mock_extract.side_effect = StatementExtractionError("API unavailable")

    assert src.main.run(["--bank-statement", "statement.pdf"]) == 1
