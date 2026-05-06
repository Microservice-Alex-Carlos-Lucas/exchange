from prometheus_client import Counter

cache_hits = Counter(
    "exchange_cache_hits_total",
    "Number of exchange-rate lookups served from Redis cache",
)

cache_misses = Counter(
    "exchange_cache_misses_total",
    "Number of exchange-rate lookups that bypassed cache and hit AwesomeAPI",
)
