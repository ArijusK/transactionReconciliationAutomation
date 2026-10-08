import requests


BASE_URL = "https://api.frankfurter.dev/v2"


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

    response = requests.get(
        url,
        timeout=10
    )

    response.raise_for_status()

    data = response.json()

    return data["rate"]