"""Minimalist in-memory TTL Cache."""

import time
import threading
from typing import Any

class TTLCache:
    """Thread-safe, simple in-memory cache with Time-To-Live."""
    
    def __init__(self, ttl_seconds: float = 5.0):
        self._cache: dict[str, tuple[float, Any]] = {}
        self.ttl_seconds = ttl_seconds
        self._lock = threading.Lock()

    def get(self, key: str) -> Any | None:
        """Retrieve an item from the cache if it hasn't expired."""
        with self._lock:
            if key in self._cache:
                timestamp, value = self._cache[key]
                if time.time() - timestamp <= self.ttl_seconds:
                    return value
                else:
                    # Expired
                    del self._cache[key]
            return None

    def set(self, key: str, value: Any) -> None:
        """Store an item in the cache."""
        with self._lock:
            self._cache[key] = (time.time(), value)

    def clear(self) -> None:
        """Clear all entries."""
        with self._lock:
            self._cache.clear()
