"""Redis cache service."""

import json
import logging
from typing import Any, Optional
import asyncio as redis

from app.config import settings

logger = logging.getLogger(__name__)


class CacheService:
    """Service for caching data with Redis and a simple SQLite fallback.

    For local development where Redis may not be available, this service
    provides a lightweight SQLite-backed cache with TTL support so endpoints
    keep working without requiring Redis.
    """

    def __init__(self):
        """Initialize SQLite fallback DB; Redis client is initialized lazily."""
        # Redis client will be created on first use to avoid network calls during import/startup
        self.redis = None
        self._redis_tried = False

        # SQLite DB file (persisted under data/ for local dev)
        from pathlib import Path
        import sqlite3
        import time

        self.default_ttl = settings.REDIS_CACHE_TTL
        self.data_dir = Path(__file__).resolve().parents[3] / "data"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = self.data_dir / "cache.sqlite"

        # Initialize SQLite connection
        self._sqlite_conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self._sqlite_conn.execute(
            """
            CREATE TABLE IF NOT EXISTS cache (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                expires_at INTEGER
            )
            """
        )
        self._sqlite_conn.commit()
        logger.info(f"Initialized SQLite cache at {self.db_path}")

    def _init_redis_if_needed(self):
        """Attempt to initialize Redis client the first time it's needed.

        Avoids making network calls at module import time and allows DB init to run
        first during application startup even if Redis is unreachable.
        """
        if self._redis_tried:
            return
        self._redis_tried = True

        if not settings.REDIS_URL or not settings.REDIS_URL.strip():
            logger.info("REDIS_URL not set; using SQLite fallback for cache")
            self.redis = None
            return

        try:
            self.redis = redis.from_url(settings.REDIS_URL, decode_responses=True)
            logger.info("Initialized Redis cache client")
        except Exception as e:
            logger.warning(f"Failed to initialize Redis client; will use SQLite fallback: {e}")
            self.redis = None

    # ------------------ Redis-first, SQLite-fallback helpers ------------------
    async def get(self, key: str) -> Optional[str]:
        try:
            # Initialize Redis lazily on first use
            self._init_redis_if_needed()

            if self.redis is not None:
                try:
                    import asyncio

                    value = await asyncio.wait_for(self.redis.get(key), timeout=settings.REDIS_OP_TIMEOUT)
                    if value:
                        logger.debug(f"Cache hit (Redis): {key}")
                        return value
                    logger.debug(f"Cache miss (Redis): {key}")
                except (asyncio.TimeoutError, asyncio.CancelledError) as e:
                    logger.warning(f"Redis get timed out for {key}, falling back to SQLite: {e}")
                    # disable redis client to avoid repeated slow calls
                    self.redis = None
                except Exception as e:
                    logger.warning(f"Redis get failed for {key}, falling back to SQLite: {e}")
                    self.redis = None

            # SQLite fallback
            return await self._sqlite_get(key)
        except Exception as e:
            logger.error(f"Error getting cache key {key}: {e}")
            return None

    async def set(self, key: str, value: str, ttl: Optional[int] = None) -> bool:
        try:
            ttl = ttl or self.default_ttl
            # Initialize Redis lazily on first use
            self._init_redis_if_needed()

            if self.redis is not None:
                try:
                    import asyncio

                    await asyncio.wait_for(self.redis.setex(key, ttl, value), timeout=settings.REDIS_OP_TIMEOUT)
                    logger.debug(f"Cache set (Redis): {key} (TTL: {ttl}s)")
                    return True
                except (asyncio.TimeoutError, asyncio.CancelledError) as e:
                    logger.warning(f"Redis set timed out for {key}, falling back to SQLite: {e}")
                    self.redis = None
                except Exception as e:
                    logger.warning(f"Redis set failed for {key}, falling back to SQLite: {e}")
                    self.redis = None

            # SQLite fallback
            return await self._sqlite_set(key, value, ttl)
        except Exception as e:
            logger.error(f"Error setting cache key {key}: {e}")
            return False

    async def delete(self, key: str) -> bool:
        try:
            # Initialize Redis lazily on first use
            self._init_redis_if_needed()

            if self.redis is not None:
                try:
                    import asyncio

                    await asyncio.wait_for(self.redis.delete(key), timeout=settings.REDIS_OP_TIMEOUT)
                    logger.debug(f"Cache deleted (Redis): {key}")
                    return True
                except (asyncio.TimeoutError, asyncio.CancelledError) as e:
                    logger.warning(f"Redis delete timed out for {key}, falling back to SQLite: {e}")
                    self.redis = None
                except Exception as e:
                    logger.warning(f"Redis delete failed for {key}, falling back to SQLite delete: {e}")
                    self.redis = None

            return await self._sqlite_delete(key)
        except Exception as e:
            logger.error(f"Error deleting cache key {key}: {e}")
            return False

    async def clear_pattern(self, pattern: str) -> int:
        """Clear keys matching a simple pattern (Redis glob style 'prefix:*')."""
        try:
            # Initialize Redis lazily on first use
            self._init_redis_if_needed()

            if self.redis is not None:
                try:
                    import asyncio

                    keys = await asyncio.wait_for(self.redis.keys(pattern), timeout=settings.REDIS_OP_TIMEOUT)
                    if keys:
                        # delete keys with timeout as well
                        try:
                            await asyncio.wait_for(self.redis.delete(*keys), timeout=settings.REDIS_OP_TIMEOUT)
                        except Exception:
                            logger.warning(f"Timed out deleting keys from Redis; continuing with SQLite fallback")
                        deleted = len(keys)
                        logger.info(f"Cleared {deleted} cache keys (Redis) matching pattern: {pattern}")
                        return deleted
                    return 0
                except (asyncio.TimeoutError, asyncio.CancelledError) as e:
                    logger.warning(f"Redis keys timed out for pattern {pattern}, falling back to SQLite: {e}")
                    self.redis = None
                except Exception as e:
                    logger.warning(f"Redis clear_pattern failed for {pattern}, falling back to SQLite: {e}")
                    self.redis = None

            # SQLite fallback: convert Redis glob '*' to SQL '%' and use LIKE on key
            sql_pattern = pattern.replace("*", "%")
            return await self._sqlite_clear_pattern(sql_pattern)
        except Exception as e:
            logger.error(f"Error clearing cache pattern {pattern}: {e}")
            return 0

    async def get_json(self, key: str) -> Optional[Any]:
        value = await self.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                logger.error(f"Error decoding JSON from cache key: {key}")
                return None
        return None

    async def set_json(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        try:
            json_value = json.dumps(value)
            return await self.set(key, json_value, ttl)
        except (TypeError, ValueError) as e:
            logger.error(f"Error encoding JSON for cache key {key}: {str(e)}")
            return False

    # ------------------ SQLite helpers (blocking — run in default executor) --
    async def _sqlite_get(self, key: str) -> Optional[str]:
        import time
        import asyncio

        def _get():
            cur = self._sqlite_conn.cursor()
            cur.execute("SELECT value, expires_at FROM cache WHERE key = ?", (key,))
            row = cur.fetchone()
            if not row:
                return None
            value, expires_at = row
            if expires_at and time.time() > expires_at:
                # expired; delete and return None
                cur.execute("DELETE FROM cache WHERE key = ?", (key,))
                self._sqlite_conn.commit()
                return None
            return value

        return await asyncio.get_running_loop().run_in_executor(None, _get)

    async def _sqlite_set(self, key: str, value: str, ttl: int) -> bool:
        import time
        import asyncio

        def _set():
            expires_at = int(time.time() + ttl) if ttl else None
            cur = self._sqlite_conn.cursor()
            cur.execute(
                "REPLACE INTO cache (key, value, expires_at) VALUES (?, ?, ?)",
                (key, value, expires_at),
            )
            self._sqlite_conn.commit()
            return True

        return await asyncio.get_running_loop().run_in_executor(None, _set)

    async def _sqlite_delete(self, key: str) -> bool:
        import asyncio

        def _delete():
            cur = self._sqlite_conn.cursor()
            cur.execute("DELETE FROM cache WHERE key = ?", (key,))
            self._sqlite_conn.commit()
            return cur.rowcount > 0

        return await asyncio.get_running_loop().run_in_executor(None, _delete)

    async def _sqlite_clear_pattern(self, sql_pattern: str) -> int:
        import asyncio

        def _clear():
            cur = self._sqlite_conn.cursor()
            cur.execute("SELECT key FROM cache WHERE key LIKE ?", (sql_pattern,))
            keys = [r[0] for r in cur.fetchall()]
            if not keys:
                return 0
            cur.execute("DELETE FROM cache WHERE key LIKE ?", (sql_pattern,))
            deleted = cur.rowcount
            self._sqlite_conn.commit()
            return deleted

        return await asyncio.get_running_loop().run_in_executor(None, _clear)


# Singleton instance
cache_service = CacheService()
