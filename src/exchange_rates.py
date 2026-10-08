import requests


BASE_URL = "https://api.frankfurter.dev/v2"

class ExchangeRateError(Exception):
    pass


def get_exchange_rate(base_currency, quote_currency):
    base_currency = base_currency.upper()
    quote_currency = quote_currency.upper()

    if base_currency == quote_currency:
        return 1.0

    url = (
        f"{BASE_URL}/rate/"
        f"{base_currency.lower()}/"
        f"{quote_currency.lower()}"
    )

    try:
        response = requests.get(
            url,
            timeout=10
        )

        response.raise_for_status()

        data = response.json()

        return data["rate"]
    except requests.RequestException as error:
        raise ExchangeRateError(
            f"Failed to fetch {base_currency}/{quote_currency} rate"
        ) from error

def get_exchange_rates(currencies, base_currency="EUR"):
    rates = []

    for currency in sorted(currencies):
        rate = get_exchange_rate(
            base_currency,
            currency
        )

        rates.append({
            "base_currency": base_currency,
            "quote_currency": currency,
            "rate": rate,
        })

    return rates