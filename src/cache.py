import json
import logging
import os

import redis

from src.metrics import cache_hits, cache_misses

logger = logging.getLogger(__name__)

_TTL_SECONDS = 60
_KEY_PREFIX = "exchange:rate"

_client: redis.Redis | None = None


def _get_client() -> redis.Redis | None:
    global _client
    if _client is not None:
        return _client
    try:
        _client = redis.Redis(
            host=os.environ.get("REDIS_HOST", "localhost"),
            port=int(os.environ.get("REDIS_PORT", "6379")),
            decode_responses=True,
            socket_timeout=1,
            socket_connect_timeout=1,
        )
        _client.ping()
        return _client
    except (redis.RedisError, OSError) as exc:
        logger.warning("Redis unavailable, falling back to direct fetch: %s", exc)
        _client = None
        return None


def _key(from_currency: str, to_currency: str) -> str:
    return f"{_KEY_PREFIX}:{from_currency}:{to_currency}"


def get(from_currency: str, to_currency: str) -> dict | None:
    client = _get_client()
    if client is None:
        cache_misses.inc()
        return None
    try:
        raw = client.get(_key(from_currency, to_currency))
    except redis.RedisError as exc:
        logger.warning("Redis GET failed: %s", exc)
        cache_misses.inc()
        return None
    if raw is None:
        cache_misses.inc()
        return None
    cache_hits.inc()
    return json.loads(raw)


def set(from_currency: str, to_currency: str, value: dict) -> None:
    client = _get_client()
    if client is None:
        return
    try:
        client.setex(_key(from_currency, to_currency), _TTL_SECONDS, json.dumps(value))
    except redis.RedisError as exc:
        logger.warning("Redis SETEX failed: %s", exc)


def reset_client_for_tests() -> None:
    global _client
    _client = None
