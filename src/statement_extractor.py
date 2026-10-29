import base64
import json
import os
from pathlib import Path

import anthropic
import pandas as pd

MODEL = "claude-opus-5-5"

COLUMNS = [
    "transaction_id",
    "date",
    "currency",
    "amount",
    "status",
]

TRANSACTIONS_SCHEMA = {
    "type": "object",
    "properties": {
        "transactions": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "transaction_id": {"type": "string"},
                    "date": {"type": "string"},
                    "currency": {"type": "string"},
                    "amount": {"type": "number"},
                    "status": {"type": "string", "enum": ["SETTLED", "PENDING"]},
                },
                "required": COLUMNS,
                "additionalProperties": False,
            },
        },
    },
    "required": ["transactions"],
    "additionalProperties": False,
}

INSTRUCTIONS = """Extract every transaction from this bank statement.

- transaction_id: the transaction reference exactly as printed.
- date: the value date in YYYY-MM-DD format.
- currency: the currency code exactly as printed, even if it looks invalid.
- amount: the amount as a number, without thousands separators.
- status: PENDING if the statement marks the transaction as pending, otherwise SETTLED.

Do not skip, merge or invent transactions. The output is validated and reconciled automatically, so copy values as printed rather than correcting them."""


class StatementExtractionError(Exception):
    pass


def extract_transactions(pdf_path, client=None):
    if client is None and not os.environ.get("ANTHROPIC_API_KEY"):
        raise StatementExtractionError(
            "ANTHROPIC_API_KEY is not set. It is needed to extract "
            "transactions from a PDF statement."
        )

    pdf_data = base64.standard_b64encode(
        Path(pdf_path).read_bytes()
    ).decode("utf-8")

    try:
        client = client or anthropic.Anthropic()

        response = client.beta.messages.create(
            model=MODEL,
            max_tokens=16000,
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
            output_config={
                "effort": "medium",
                "format": {
                    "type": "json_schema",
                    "schema": TRANSACTIONS_SCHEMA,
                },
            },
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "document",
                        "source": {
                            "type": "base64",
                            "media_type": "application/pdf",
                            "data": pdf_data,
                        },
                    },
                    {"type": "text", "text": INSTRUCTIONS},
                ],
            }],
        )

    except anthropic.AnthropicError as error:
        raise StatementExtractionError(
            f"Could not extract transactions from {pdf_path}: {error}"
        ) from error

    if response.stop_reason != "end_turn":
        raise StatementExtractionError(
            f"Extraction from {pdf_path} did not complete "
            f"(stop reason: {response.stop_reason})"
        )

    text = next(
        block.text for block in response.content if block.type == "text"
    )

    return pd.DataFrame(
        json.loads(text)["transactions"],
        columns=COLUMNS
    )
