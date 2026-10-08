from unittest.mock import Mock, patch

from src.exchange_rates import get_exchange_rate


def test_same_currency_returns_one():
    rate = get_exchange_rate("EUR", "EUR")

    assert rate == 1.0


@patch("src.exchange_rates.requests.get")
def test_get_exchange_rate(mock_get):
    mock_response = Mock()

    mock_response.json.return_value = {
        "date": "2026-10-08",
        "base": "EUR",
        "quote": "USD",
        "rate": 1.15,
    }

    mock_response.raise_for_status.return_value = None

    mock_get.return_value = mock_response

    rate = get_exchange_rate("EUR", "USD")

    assert rate == 1.15

@patch("src.exchange_rates.requests.get")
def test_exchange_rate_normalizes_currency_case(mock_get):
    mock_response = Mock()

    mock_response.json.return_value = {
        "date": "2026-10-08",
        "base": "EUR",
        "quote": "USD",
        "rate": 1.15,
    }

    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    rate = get_exchange_rate("eur", "usd")

    assert rate == 1.15