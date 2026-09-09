"""Unit tests for the TTL Cache."""

import time
from micelio.core.cache import TTLCache

def test_ttl_cache_set_and_get():
    cache = TTLCache(ttl_seconds=1.0)
    cache.set("foo", "bar")
    assert cache.get("foo") == "bar"

def test_ttl_cache_expiration():
    cache = TTLCache(ttl_seconds=0.1)
    cache.set("temp", "data")
    assert cache.get("temp") == "data"
    
    # Wait for expiration
    time.sleep(0.15)
    assert cache.get("temp") is None

def test_ttl_cache_clear():
    cache = TTLCache()
    cache.set("a", 1)
    cache.clear()
    assert cache.get("a") is None
