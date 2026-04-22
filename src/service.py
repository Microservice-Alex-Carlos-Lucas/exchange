from fastapi import HTTPException

from src.client import fetch_exchange_rate


class ExchangeService:
    def get_rate(self, from_currency: str, to_currency: str, id_account: str) -> dict:
        try:
            data = fetch_exchange_rate(from_currency.upper(), to_currency.upper())
            return {
                "sell": float(data["ask"]),
                "buy": float(data["bid"]),
                "date": data["create_date"],
                "id-account": id_account,
            }
        except HTTPException:
            raise
        except Exception as exc:
            raise HTTPException(status_code=502, detail=f"Exchange rate unavailable: {exc}") from exc
