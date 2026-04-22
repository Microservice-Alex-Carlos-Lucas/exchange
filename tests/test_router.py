import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from src.main import app

client = TestClient(app, raise_server_exceptions=False)

FAKE_RESPONSE = {
    "sell": 5.74,
    "buy": 5.73,
    "date": "2024-04-22 09:00:00",
    "id-account": "abc-123",
}


def test_health_check_returns_200():
    response = client.get("/exchanges/health-check")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_get_exchange_returns_rate():
    with patch("src.router.service.get_rate", return_value=FAKE_RESPONSE):
        response = client.get(
            "/exchanges/USD/EUR",
            headers={"id-account": "abc-123"},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["sell"] == FAKE_RESPONSE["sell"]
    assert data["buy"] == FAKE_RESPONSE["buy"]
    assert data["date"] == FAKE_RESPONSE["date"]
    assert data["id-account"] == FAKE_RESPONSE["id-account"]


def test_get_exchange_missing_id_account_returns_422():
    response = client.get("/exchanges/USD/EUR")
    assert response.status_code == 422


def test_get_exchange_upstream_failure_returns_502():
    from fastapi import HTTPException

    with patch(
        "src.router.service.get_rate",
        side_effect=HTTPException(status_code=502, detail="Exchange rate unavailable"),
    ):
        response = client.get(
            "/exchanges/USD/EUR",
            headers={"id-account": "abc-123"},
        )

    assert response.status_code == 502
