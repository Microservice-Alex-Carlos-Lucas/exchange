from fastapi import HTTPException

from src import cache
from src.client import fetch_exchange_rate


class ExchangeService:
    def get_rate(self, from_currency: str, to_currency: str, id_account: str) -> dict:
        from_currency = from_currency.upper()
        to_currency = to_currency.upper()
        try:
            cached = cache.get(from_currency, to_currency)
            if cached is not None:
                return {**cached, "id-account": id_account}

            data = fetch_exchange_rate(from_currency, to_currency)
            payload = {
                "sell": float(data["ask"]),
                "buy": float(data["bid"]),
                "date": data["create_date"],
            }
            cache.set(from_currency, to_currency, payload)
            return {**payload, "id-account": id_account}
        except HTTPException:
            raise
        except Exception as exc:
            raise HTTPException(status_code=502, detail=f"Exchange rate unavailable: {exc}") from exc
