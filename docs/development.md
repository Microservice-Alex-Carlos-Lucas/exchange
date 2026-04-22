# Desenvolvimento

## Pré-requisitos

- [uv](https://docs.astral.sh/uv/) — gerenciador de pacotes Python
- Docker (para rodar integrado com a plataforma)
- Python 3.13+

## Setup local

```bash
git clone https://github.com/AlexChequer/exchange.git
cd exchange

# Instalar dependências (incluindo dev)
uv sync

# Rodar o servidor localmente
uv run uvicorn src.main:app --reload
```

O servidor sobe em `http://localhost:8000`.

!!! note
    Rodando localmente (fora do Docker), o gateway não estará presente — os endpoints autenticados precisarão do header `id-account` enviado manualmente para testes.

## Testes

```bash
# Rodar todos os testes
uv run pytest tests/ -v

# Com cobertura
uv run pytest tests/ -v --tb=short
```

### Estrutura dos testes

| Arquivo | Tipo | O que testa |
|---------|------|-------------|
| `tests/test_service.py` | Unitário | `ExchangeService` com cliente mockado |
| `tests/test_router.py` | Integração | Endpoints via `TestClient` do FastAPI |

Cobertura de cenários:

- Retorno correto com `sell`, `buy`, `date`, `id-account`
- Currencies são normalizadas para maiúsculas antes de chamar a API
- `502` quando a AwesomeAPI falha
- `422` quando o header `id-account` está ausente
- Health-check retorna `200` sem autenticação

## Docker

```bash
# Build da imagem
docker build -t exchange .

# Rodar o container isolado (porta 8000)
docker run -p 8000:8000 exchange
```

### Integrado com a plataforma

Adicione ao `compose.yaml` da plataforma:

```yaml
exchange:
  build:
    context: ./exchange
    dockerfile: Dockerfile
  hostname: exchange
  deploy:
    replicas: 1
```

E ao `gateway-service/application.yaml`:

```yaml
- id: exchanges
  uri: http://exchange:8000
  predicates:
    - Path=/exchanges/**
```

E ao `RouterValidator.java` (open routes):

```java
"/exchanges/health-check"
```

## Documentação local

```bash
# Servir MkDocs localmente
uv run mkdocs serve

# Build estático
uv run mkdocs build
```

A documentação fica disponível em `http://localhost:8001`.

## Variáveis de ambiente

Nenhuma variável é obrigatória — a AwesomeAPI é pública e não requer chave. Copie `.env.example` caso queira adicionar uma API de câmbio alternativa que exija autenticação:

```bash
cp .env.example .env
```
