import requests

_BASE_URL = "https://economia.awesomeapi.com.br/json/last"


def fetch_exchange_rate(from_currency: str, to_currency: str) -> dict:
    url = f"{_BASE_URL}/{from_currency}-{to_currency}"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    data = response.json()
    key = f"{from_currency}{to_currency}"
    return data[key]
