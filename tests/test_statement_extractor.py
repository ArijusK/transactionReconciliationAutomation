import base64
import json

import anthropic
import httpx2
import pytest

from types import SimpleNamespace
from unittest.mock import Mock

from src.statement_extractor import (
    StatementExtractionError,
    extract_transactions,
)

STATEMENT_ROWS = [
    {
        "transaction_id": "TX001",
        "date": "2026-10-01",
        "currency": "EUR",
        "amount": 1250.0,
        "status": "SETTLED",
    },
    {
        "transaction_id": "TX003",
        "date": "2026-10-02",
        "currency": "eur",
        "amount": 800.5,
        "status": "PENDING",
    },
]


def make_response(rows=STATEMENT_ROWS, stop_reason="end_turn"):
    text = json.dumps({"transactions": rows})

    return SimpleNamespace(
        stop_reason=stop_reason,
        content=[SimpleNamespace(type="text", text=text)],
    )


def make_client(response=None, error=None):
    client = Mock()
    client.beta.messages.create.return_value = response
    client.beta.messages.create.side_effect = error

    return client


@pytest.fixture
def statement_pdf(tmp_path):
    pdf_path = tmp_path / "statement.pdf"
    pdf_path.write_bytes(b"%PDF-1.4 sample statement")

    return pdf_path


def test_extract_transactions_returns_statement_rows(statement_pdf):
    client = make_client(make_response())

    transactions = extract_transactions(statement_pdf, client)

    assert list(transactions.columns) == [
        "transaction_id",
        "date",
        "currency",
        "amount",
        "status",
    ]

    assert transactions.to_dict("records") == STATEMENT_ROWS


def test_extract_transactions_sends_pdf_and_schema(statement_pdf):
    client = make_client(make_response())

    extract_transactions(statement_pdf, client)

    request = client.beta.messages.create.call_args.kwargs
    document = request["messages"][0]["content"][0]

    assert document["type"] == "document"
    assert document["source"]["media_type"] == "application/pdf"
    assert base64.b64decode(document["source"]["data"]) == statement_pdf.read_bytes()
    assert request["output_config"]["format"]["type"] == "json_schema"


def test_statement_without_transactions_returns_empty_table(statement_pdf):
    client = make_client(make_response(rows=[]))

    transactions = extract_transactions(statement_pdf, client)

    assert transactions.empty
    assert "transaction_id" in transactions.columns


@pytest.mark.parametrize("stop_reason", ["max_tokens", "refusal"])
def test_incomplete_extraction_raises_error(statement_pdf, stop_reason):
    client = make_client(make_response(stop_reason=stop_reason))

    with pytest.raises(StatementExtractionError):
        extract_transactions(statement_pdf, client)


def test_api_failure_raises_error(statement_pdf):
    error = anthropic.APIConnectionError(
        request=httpx2.Request("POST", "https://api.anthropic.com/v1/messages")
    )

    client = make_client(error=error)

    with pytest.raises(StatementExtractionError):
        extract_transactions(statement_pdf, client)


def test_missing_statement_file_raises_error(tmp_path):
    client = make_client(make_response())

    with pytest.raises(FileNotFoundError):
        extract_transactions(tmp_path / "missing.pdf", client)


def test_missing_api_key_raises_error(statement_pdf, monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

    with pytest.raises(StatementExtractionError, match="ANTHROPIC_API_KEY"):
        extract_transactions(statement_pdf)
