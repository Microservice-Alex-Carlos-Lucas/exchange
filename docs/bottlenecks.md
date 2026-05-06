# Bottlenecks implementados

A página de exercícios pede **ao menos 2 bottlenecks por integrante**. No
Exchange API entreguei **dois**, ambos rodando localmente via
`docker compose up -d --build exchange redis`.

Ambos seguem a estrutura padrão do grupo: **Categoria → Problema → Solução
→ Verificação → O que isso desbloqueia → Arquivos relevantes**.

---

## Bottleneck 1 — Caching de taxas de câmbio com Redis

**Categoria:** Latência · *external-API throttling*

### Problema

Cada chamada a `/exchanges/{from}/{to}` faz um round-trip HTTP em tempo
real à [AwesomeAPI](https://docs.awesomeapi.com.br/). Isso adiciona
latência significativa a *todo* request — incluindo os que chegam via
`order-service` durante a criação de pedido em moeda alternativa — e
arrisca **rate-limiting** quando a aplicação escala. As cotações mudam de
forma não-trivial só a cada poucos segundos no provedor, então repetir
~85ms de chamada externa para *cada* request é desperdício puro.

### Solução

1. Adicionei o cliente **Redis** (`pyproject.toml`) e um módulo
   `src/cache.py` com TTL de **60s** e chave `exchange:rate:{FROM}:{TO}`.
   `setex` garante expiração automática; em produção o Redis é
   compartilhado entre réplicas (não há cache local por pod).
2. `ExchangeService.get_rate()` consulta o cache antes de chamar a
   AwesomeAPI; em cache miss faz a chamada e popula o cache.
3. Falhas do Redis (timeout, conexão recusada) não derrubam o serviço:
   `_get_client()` captura `RedisError`/`OSError`, loga warning e segue
   direto para a AwesomeAPI. Resiliência > eficiência quando Redis cai.
4. Contadores Prometheus customizados (`exchange_cache_hits_total` e
   `exchange_cache_misses_total`) tornam o efeito **observável**.

```python
# src/service.py — caminho crítico
cached = cache.get(from_currency, to_currency)
if cached is not None:
    return {**cached, "id-account": id_account}

data = fetch_exchange_rate(from_currency, to_currency)
payload = {"sell": float(data["ask"]), "buy": float(data["bid"]), "date": data["create_date"]}
cache.set(from_currency, to_currency, payload)
```

### Verificação

Rodando `docker compose up -d --build exchange redis` e disparando duas
chamadas consecutivas ao mesmo par de moedas:

```text
first call (cache miss):  86.0ms
second call (cache hit):   0.9ms
speedup: 91.2×
```

Métricas em `/metrics` confirmam o comportamento:

```text
$ curl http://localhost:8000/metrics | grep ^exchange_cache_
exchange_cache_hits_total 1.0
exchange_cache_misses_total 1.0
```

E os testes (`tests/test_service.py`) usando `fakeredis` provam que duas
chamadas a `get_rate("USD","BRL")` consecutivas executam **só uma**
chamada upstream:

```python
def test_cache_hit_skips_upstream_fetch(service):
    with patch("src.service.fetch_exchange_rate", return_value=FAKE_RATE) as mock_fetch:
        service.get_rate("USD", "BRL", "alex")
        service.get_rate("USD", "BRL", "carlos")
    assert mock_fetch.call_count == 1
```

### O que isso desbloqueia

- **Order Service consegue criar pedido em moeda alternativa em tempo
  comparável a pedido em moeda nativa**: a taxa fica quente por 60s, e
  picos de pedidos só pagam o overhead da AwesomeAPI uma vez por janela.
- **Defesa contra rate-limit**: a taxa de chamadas externas é limitada a
  ≤ 1/min/par-de-moedas, independentemente do volume.
- **HPA do Kubernetes pode escalar baseado em CPU sem aumentar carga
  externa proporcionalmente** — o cache absorve a maior parte do tráfego.

### Arquivos relevantes

- `pyproject.toml` (linhas com `redis` e `fakeredis`)
- `src/cache.py` (cliente Redis singleton + get/set com fallback gracioso)
- `src/metrics.py` (counters Prometheus)
- `src/service.py` (caminho do cache antes do fetch)
- `tests/test_service.py` (`test_cache_hit_skips_upstream_fetch`)
- `tests/conftest.py` (fakeredis fixture)

---

## Bottleneck 2 — Observabilidade com `prometheus-fastapi-instrumentator`

**Categoria:** Identificação de gargalos · *capacity planning*

### Problema

Sem métricas, é impossível saber quanto da latência percebida pelo
order-service vem da rede vs. da AwesomeAPI vs. do próprio FastAPI, e é
impossível justificar quantitativamente o ganho do cache (Bottleneck 1).
A observabilidade também é pré-requisito para alertas e para o **HPA**
do Kubernetes (peso de 15% no projeto via Load Testing).

### Solução

1. Adicionei `prometheus-fastapi-instrumentator` em `pyproject.toml`.
2. Em `src/main.py`, uma única linha instrumenta toda a aplicação e expõe
   `/metrics`:

```python
Instrumentator().instrument(app).expose(app, endpoint="/metrics", include_in_schema=False)
```

3. `src/metrics.py` declara contadores customizados consumidos pelo
   `cache.py`:

```python
cache_hits = Counter("exchange_cache_hits_total",
                     "Number of exchange-rate lookups served from Redis cache")
cache_misses = Counter("exchange_cache_misses_total",
                       "Number of exchange-rate lookups that bypassed cache and hit AwesomeAPI")
```

### Verificação

```text
$ curl http://localhost:8000/metrics | grep -E "^http_request|^exchange_cache"
http_request_duration_seconds_count{handler="/exchanges/{from_currency}/{to_currency}",method="GET",status="2xx"} 2.0
http_request_duration_seconds_sum{handler="/exchanges/{from_currency}/{to_currency}",method="GET",status="2xx"} 0.087
exchange_cache_hits_total 1.0
exchange_cache_misses_total 1.0
```

A query Prometheus `rate(exchange_cache_hits_total[1m]) / rate(exchange_cache_misses_total[1m])` dá
a **eficácia do cache** ao vivo em painéis Grafana.

### O que isso desbloqueia

- **Dashboards Grafana** com p95/p99 por rota, taxa de erro, eficácia do
  cache, e latência da AwesomeAPI isolada das demais.
- **Alertas Prometheus** (ex: `rate(exchange_cache_misses_total[5m]) > 1`
  significa que o cache está sendo invalidado mais rápido que esperado —
  possível bug ou TTL mal calibrado).
- **HPA com métricas customizadas** via `prometheus-adapter`: escalar
  pods quando `http_requests_in_progress` exceder X, sem depender só de
  CPU.

### Arquivos relevantes

- `pyproject.toml` (`prometheus-fastapi-instrumentator`)
- `src/main.py` (chamada do `Instrumentator`)
- `src/metrics.py` (contadores customizados)
