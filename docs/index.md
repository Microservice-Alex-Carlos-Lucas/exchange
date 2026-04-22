# Exchange API

**Aluno:** Alex Chequer  
**Disciplina:** Plataformas, Microserviços, DevOps e APIs — Insper 2026.1

---

## Visão Geral

O Exchange API é um microserviço em Python (FastAPI) que permite a usuários autenticados consultar taxas de câmbio entre moedas em tempo real. As taxas são obtidas da [AwesomeAPI](https://docs.awesomeapi.com.br/api-de-moedas), uma API pública e gratuita sem necessidade de chave.

## Repositórios

| Serviço | Repositório |
|---------|-------------|
| Exchange API (este) | [AlexChequer/exchange](https://github.com/AlexChequer/exchange) |
| Plataforma (auth, account, gateway) | [insper/platform](https://github.com/insper/platform) |

## Endpoint

```
GET /exchanges/{from}/{to}
```

**Exemplo:**

```bash
curl -b "__store_jwt_token=<token>" \
  http://localhost:8080/exchanges/USD/BRL
```

**Resposta:**

```json
{
  "sell": 5.74,
  "buy": 5.73,
  "date": "2024-04-22 09:00:00",
  "id-account": "abc-123-def-456"
}
```

!!! warning "Autenticação obrigatória"
    O usuário deve estar autenticado. O gateway valida o JWT (`__store_jwt_token` cookie) e injeta o header `id-account` antes de encaminhar a requisição ao serviço.

## Stack

- **Linguagem:** Python 3.13  
- **Framework:** FastAPI  
- **Gerenciador de pacotes:** uv  
- **API de câmbio:** AwesomeAPI (pública, sem chave)  
- **Containerização:** Docker  
