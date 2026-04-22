# API Reference

## Endpoints

### `GET /exchanges/health-check`

Verifica se o serviço está em execução. Rota aberta — não requer autenticação.

**Resposta:**

```json
{ "status": "ok" }
```

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `status` | string | Sempre `"ok"` quando o serviço está saudável |

---

### `GET /exchanges/{from}/{to}`

Retorna a taxa de câmbio atual entre duas moedas.

!!! info "Autenticação"
    Requer cookie `__store_jwt_token` válido. O gateway injeta o header `id-account` automaticamente após validar o JWT.

**Parâmetros de rota:**

| Parâmetro | Tipo | Exemplo | Descrição |
|-----------|------|---------|-----------|
| `from` | string | `USD` | Moeda de origem (case-insensitive) |
| `to` | string | `BRL` | Moeda de destino (case-insensitive) |

**Headers (injetados pelo gateway):**

| Header | Descrição |
|--------|-----------|
| `id-account` | UUID da conta autenticada |

**Resposta 200 — OK:**

```json
{
  "sell": 5.74,
  "buy":  5.73,
  "date": "2024-04-22 09:00:00",
  "id-account": "abc-123-def-456"
}
```

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `sell` | float | Preço de venda (ask) da moeda de origem |
| `buy` | float | Preço de compra (bid) da moeda de origem |
| `date` | string | Data/hora da cotação (`YYYY-MM-DD HH:MM:SS`) |
| `id-account` | string | UUID da conta que fez a requisição |

**Respostas de erro:**

| Código | Motivo |
|--------|--------|
| `401` | JWT ausente ou inválido (retornado pelo gateway) |
| `422` | Header `id-account` ausente (requisição não passou pelo gateway) |
| `502` | AwesomeAPI indisponível ou par de moedas inválido |

## Exemplos

=== "cURL"

    ```bash
    # Login para obter o cookie
    curl -c cookies.txt -X POST http://localhost:8080/auth/login \
      -H "Content-Type: application/json" \
      -d '{"email":"user@example.com","password":"secret"}'

    # Consultar câmbio USD → BRL
    curl -b cookies.txt http://localhost:8080/exchanges/USD/BRL
    ```

=== "Python"

    ```python
    import requests

    session = requests.Session()
    session.post("http://localhost:8080/auth/login", json={
        "email": "user@example.com",
        "password": "secret"
    })

    response = session.get("http://localhost:8080/exchanges/USD/BRL")
    print(response.json())
    ```

## Pares de moedas suportados

Qualquer par suportado pela [AwesomeAPI](https://docs.awesomeapi.com.br/api-de-moedas). Exemplos comuns:

| Par | Descrição |
|-----|-----------|
| `USD/BRL` | Dólar americano → Real brasileiro |
| `EUR/BRL` | Euro → Real brasileiro |
| `USD/EUR` | Dólar americano → Euro |
| `BTC/BRL` | Bitcoin → Real brasileiro |
