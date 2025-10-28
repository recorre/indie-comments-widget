"""
Performance optimization utilities for the Comment Widget API
"""

import time
import asyncio
from functools import wraps
from typing import Dict, Any, Optional, Callable
import redis.asyncio as redis
from contextlib import asynccontextmanager
import json
import hashlib
from datetime import datetime, timedelta

from .config import settings


class CacheManager:
    """Redis-based caching manager"""

    def __init__(self, redis_url: Optional[str] = None):
        self.redis_url = redis_url or settings.redis_url
        self.redis_client: Optional[redis.Redis] = None
        self.enabled = bool(self.redis_url)

    async def connect(self):
        """Connect to Redis"""
        if self.enabled and not self.redis_client:
            self.redis_client = redis.from_url(self.redis_url, decode_responses=True)

    async def disconnect(self):
        """Disconnect from Redis"""
        if self.redis_client:
            await self.redis_client.close()
            self.redis_client = None

    async def get(self, key: str) -> Optional[str]:
        """Get value from cache"""
        if not self.enabled or not self.redis_client:
            return None
        try:
            return await self.redis_client.get(key)
        except Exception:
            return None

    async def set(self, key: str, value: str, ttl: int = 300) -> bool:
        """Set value in cache with TTL"""
        if not self.enabled or not self.redis_client:
            return False
        try:
            return await self.redis_client.setex(key, ttl, value)
        except Exception:
            return False

    async def delete(self, key: str) -> bool:
        """Delete key from cache"""
        if not self.enabled or not self.redis_client:
            return False
        try:
            return bool(await self.redis_client.delete(key))
        except Exception:
            return False

    def generate_key(self, *args, **kwargs) -> str:
        """Generate cache key from arguments"""
        key_data = json.dumps({"args": args, "kwargs": kwargs}, sort_keys=True)
        return f"comment_widget:{hashlib.md5(key_data.encode()).hexdigest()}"


class MetricsCollector:
    """Simple metrics collection for performance monitoring"""

    def __init__(self):
        self.metrics = {
            "requests_total": 0,
            "requests_duration": [],
            "errors_total": 0,
            "cache_hits": 0,
            "cache_misses": 0
        }

    def increment_requests(self):
        """Increment total requests counter"""
        self.metrics["requests_total"] += 1

    def add_request_duration(self, duration: float):
        """Add request duration for calculating averages"""
        self.metrics["requests_duration"].append(duration)
        # Keep only last 1000 measurements
        if len(self.metrics["requests_duration"]) > 1000:
            self.metrics["requests_duration"] = self.metrics["requests_duration"][-1000:]

    def increment_errors(self):
        """Increment error counter"""
        self.metrics["errors_total"] += 1

    def increment_cache_hit(self):
        """Increment cache hit counter"""
        self.metrics["cache_hits"] += 1

    def increment_cache_miss(self):
        """Increment cache miss counter"""
        self.metrics["cache_misses"] += 1

    def get_stats(self) -> Dict[str, Any]:
        """Get current metrics statistics"""
        durations = self.metrics["requests_duration"]
        return {
            "requests_total": self.metrics["requests_total"],
            "errors_total": self.metrics["errors_total"],
            "cache_hit_ratio": (
                self.metrics["cache_hits"] /
                (self.metrics["cache_hits"] + self.metrics["cache_misses"])
                if (self.metrics["cache_hits"] + self.metrics["cache_misses"]) > 0
                else 0
            ),
            "avg_response_time": sum(durations) / len(durations) if durations else 0,
            "min_response_time": min(durations) if durations else 0,
            "max_response_time": max(durations) if durations else 0
        }


# Global instances
cache_manager = CacheManager()
metrics_collector = MetricsCollector()


def cached(ttl: int = 300):
    """Decorator for caching function results"""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            if not cache_manager.enabled:
                return await func(*args, **kwargs)

            # Generate cache key
            cache_key = cache_manager.generate_key(func.__name__, *args, **kwargs)

            # Try to get from cache
            cached_result = await cache_manager.get(cache_key)
            if cached_result:
                metrics_collector.increment_cache_hit()
                try:
                    return json.loads(cached_result)
                except json.JSONDecodeError:
                    pass  # Fall through to function call

            # Cache miss - execute function
            metrics_collector.increment_cache_miss()
            result = await func(*args, **kwargs)

            # Cache the result
            try:
                await cache_manager.set(cache_key, json.dumps(result), ttl)
            except (TypeError, ValueError):
                # Skip caching if result is not JSON serializable
                pass

            return result

        return wrapper
    return decorator


def timed(func: Callable):
    """Decorator for timing function execution"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            duration = time.time() - start_time
            metrics_collector.add_request_duration(duration)
            return result
        except Exception as e:
            duration = time.time() - start_time
            metrics_collector.add_request_duration(duration)
            metrics_collector.increment_errors()
            raise e

    return wrapper


@asynccontextmanager
async def lifespan_manager():
    """Lifespan context manager for FastAPI app"""
    # Startup
    await cache_manager.connect()

    yield

    # Shutdown
    await cache_manager.disconnect()


class ConnectionPoolManager:
    """HTTP connection pool manager for external API calls"""

    def __init__(self, pool_size: int = 100, timeout: float = 30.0):
        self.pool_size = pool_size
        self.timeout = timeout
        self._semaphore = asyncio.Semaphore(pool_size)

    @asynccontextmanager
    async def acquire_connection(self):
        """Acquire a connection slot from the pool"""
        async with self._semaphore:
            yield


# Global connection pool
connection_pool = ConnectionPoolManager()


async def make_external_request(url: str, method: str = "GET", **kwargs) -> Dict[str, Any]:
    """Make external API request with connection pooling and error handling"""
    async with connection_pool.acquire_connection():
        async with httpx.AsyncClient(timeout=connection_pool.timeout) as client:
            try:
                response = await client.request(method, url, **kwargs)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                # Log error and re-raise
                logger.error(f"External API request failed: {e}")
                raise HTTPException(status_code=502, detail="External service unavailable")
            except Exception as e:
                logger.error(f"Unexpected error in external request: {e}")
                raise HTTPException(status_code=500, detail="Internal server error")


# Import here to avoid circular imports
from fastapi import HTTPException
import httpx
import logging
logger = logging.getLogger(__name__)