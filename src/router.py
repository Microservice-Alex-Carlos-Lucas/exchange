from fastapi import APIRouter, Header

from src.service import ExchangeService

router = APIRouter()
service = ExchangeService()


@router.get("/exchanges/health-check")
def health_check():
    return {"status": "ok"}


@router.get("/exchanges/{from_currency}/{to_currency}")
def get_exchange(
    from_currency: str,
    to_currency: str,
    id_account: str = Header(..., alias="id-account"),
):
    return service.get_rate(from_currency, to_currency, id_account)
