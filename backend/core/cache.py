import time
from typing import Any, Dict, List, Optional, Tuple


class SWRCache:
    """
    A simple SWR (Stale-While-Revalidate) inspired cache implementation.
    Uses TTL for expiration and LRU for eviction when max_size is reached.
    """

    def __init__(self, ttl: int, max_size: int):
        self.ttl = ttl
        self.max_size = max_size
        self.cache: Dict[str, Tuple[Any, float]] = {}  # key -> (value, timestamp)
        self.order: List[str] = []  # for LRU eviction

    def get(self, key: str) -> Optional[Any]:
        if key in self.cache:
            value, timestamp = self.cache[key]
            if time.time() - timestamp < self.ttl:
                # Move to end for LRU
                self.order.remove(key)
                self.order.append(key)
                return value
            else:
                # Expired, remove
                del self.cache[key]
                self.order.remove(key)
        return None

    def set(self, key: str, value: Any) -> None:
        if key in self.cache:
            self.order.remove(key)
        elif len(self.cache) >= self.max_size:
            # Evict oldest
            oldest = self.order.pop(0)
            del self.cache[oldest]
        self.cache[key] = (value, time.time())
        self.order.append(key)