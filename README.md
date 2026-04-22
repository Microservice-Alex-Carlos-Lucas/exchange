# Exchange API

Microserviço em Python (FastAPI) para consulta de taxas de câmbio em tempo real.  
Parte da plataforma de microserviços — Insper 2026.1.

**Aluno:** Alex Chequer

---

## Endpoint

```
GET /exchanges/{from}/{to}
```

Requer autenticação via cookie JWT (`__store_jwt_token`), validado pelo gateway.

**Resposta:**

```json
{
  "sell": 5.74,
  "buy":  5.73,
  "date": "2024-04-22 09:00:00",
  "id-account": "abc-123-def-456"
}
```

## Rodando localmente

```bash
uv sync
uv run uvicorn src.main:app --reload
```

## Testes

```bash
uv run pytest tests/ -v
```

## Documentação completa

```bash
uv run mkdocs serve
```

Ou acesse a documentação publicada em: `https://alexchequer.github.io/exchange`

## Stack

- Python 3.13 · FastAPI · uv · Docker
- Taxas de câmbio: [AwesomeAPI](https://docs.awesomeapi.com.br/api-de-moedas) (pública, sem chave)
