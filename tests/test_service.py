import pytest
from fastapi import HTTPException
from unittest.mock import patch

from src.service import ExchangeService


FAKE_RATE = {
    "bid": "5.73",
    "ask": "5.74",
    "create_date": "2024-04-22 09:00:00",
}

ACCOUNT_ID = "abc-123"


@pytest.fixture
def service():
    return ExchangeService()


def test_get_rate_returns_correct_shape(service):
    with patch("src.service.fetch_exchange_rate", return_value=FAKE_RATE):
        result = service.get_rate("USD", "BRL", ACCOUNT_ID)

    assert result["sell"] == float(FAKE_RATE["ask"])
    assert result["buy"] == float(FAKE_RATE["bid"])
    assert result["date"] == FAKE_RATE["create_date"]
    assert result["id-account"] == ACCOUNT_ID


def test_get_rate_uppercases_currencies(service):
    with patch("src.service.fetch_exchange_rate", return_value=FAKE_RATE) as mock_fetch:
        service.get_rate("usd", "brl", ACCOUNT_ID)

    mock_fetch.assert_called_once_with("USD", "BRL")


def test_get_rate_raises_502_on_client_error(service):
    with patch("src.service.fetch_exchange_rate", side_effect=Exception("timeout")):
        with pytest.raises(HTTPException) as exc_info:
            service.get_rate("USD", "BRL", ACCOUNT_ID)

    assert exc_info.value.status_code == 502
