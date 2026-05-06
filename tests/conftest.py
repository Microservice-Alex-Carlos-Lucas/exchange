import fakeredis
import pytest

from src import cache


@pytest.fixture(autouse=True)
def fake_redis(monkeypatch):
    fake = fakeredis.FakeRedis(decode_responses=True)
    monkeypatch.setattr(cache, "_client", fake)
    yield fake
    cache.reset_client_for_tests()
