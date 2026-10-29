import pandas as pd
import requests

from unittest.mock import patch

import src.main
import src.report


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
