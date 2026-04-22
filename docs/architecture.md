# Arquitetura

## Visão da Plataforma

```
                          ┌─────────────────────────────┐
                          │        Trusted Layer         │
                          │                             │
  internet  ──request──▶  │  gateway ──▶  auth          │
                          │     │                       │
                          │     ├──▶  account ──▶  DB   │
                          │     │                       │
                          │     └──▶  exchange           │
                          │                             │
                          └─────────────────────────────┘
                                         │
                                         ▼
                                    3rd-party API
                                   (AwesomeAPI)
```

O Exchange API fica dentro da Trusted Layer. O gateway é o único ponto de entrada público — ele valida o JWT antes de encaminhar qualquer requisição ao serviço.

## Fluxo de uma requisição

```
Client
  │
  │  GET /exchanges/USD/BRL  (cookie: __store_jwt_token)
  ▼
Gateway (Spring Cloud Gateway)
  │
  ├─ AuthorizationFilter: extrai JWT do cookie
  │
  ├─ POST /auth/solve  ──▶  Auth Service
  │       ◀── { idAccount: "abc-123" }
  │
  ├─ Adiciona header  id-account: abc-123
  │
  ▼
Exchange Service (FastAPI, port 8000)
  │
  ├─ Lê header id-account
  │
  ├─ GET https://economia.awesomeapi.com.br/json/last/USD-BRL
  │       ◀── { bid, ask, create_date, … }
  │
  └─▶ { sell, buy, date, id-account }
```

## Estrutura de arquivos

```
exchange/
├── src/
│   ├── main.py       # FastAPI app factory
│   ├── router.py     # Rotas HTTP
│   ├── service.py    # Lógica de negócio
│   └── client.py     # Cliente HTTP para AwesomeAPI
├── tests/
│   ├── test_router.py   # Testes de integração (TestClient)
│   └── test_service.py  # Testes unitários (mocks)
├── Dockerfile
├── mkdocs.yml
└── pyproject.toml
```

## Decisões de design

### Por que AwesomeAPI?

- Gratuita e sem necessidade de cadastro ou chave de API
- Suporta ampla gama de pares de moedas, incluindo criptomoedas
- Resposta JSON simples com `bid` (compra) e `ask` (venda)

### Por que o serviço não valida o JWT diretamente?

A validação de JWT é responsabilidade exclusiva do gateway (`AuthorizationFilter.java`). O exchange service confia no header `id-account` injetado pelo gateway — isso mantém o serviço simples e sem dependência do segredo JWT.

### Por que FastAPI?

O exercício exige Python. FastAPI oferece validação automática de headers via type hints, documentação OpenAPI embutida (`/docs`) e excelente performance com uvicorn/uvloop.

### Tratamento de erros

| Situação | Comportamento |
|----------|---------------|
| AwesomeAPI timeout/erro | `502 Bad Gateway` com detalhe |
| Par de moedas inválido | `502 Bad Gateway` (AwesomeAPI retorna erro) |
| Header `id-account` ausente | `422 Unprocessable Entity` (FastAPI automático) |
| JWT inválido | `401 Unauthorized` (retornado pelo gateway, não chega ao serviço) |
