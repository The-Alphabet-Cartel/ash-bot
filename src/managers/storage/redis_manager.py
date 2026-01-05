"""
============================================================================
Ash-Bot: Crisis Detection Discord Bot
The Alphabet Cartel - https://discord.gg/alphabetcartel | alphabetcartel.org
============================================================================

MISSION - NEVER TO BE VIOLATED:
    Monitor  → Send messages to Ash-NLP for crisis classification
    Alert    → Notify Crisis Response Team via embeds when crisis detected
    Track    → Maintain user history for escalation pattern detection
    Protect  → Safeguard our LGBTQIA+ community through early intervention

============================================================================
Redis Manager for Ash-Bot Service
----------------------------------------------------------------------------
FILE VERSION: v5.0-5-5.5-1
LAST MODIFIED: 2026-01-04
PHASE: Phase 5 - Production Hardening
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-bot
Community: The Alphabet Cartel - https://discord.gg/alphabetcartel | https://alphabetcartel.org
============================================================================

RESPONSIBILITIES:
- Establish and manage authenticated Redis connection
- Provide async Redis operations for sorted sets
- Handle connection pooling and health checking
- Graceful error handling with reconnection support
- Auto-retry with exponential backoff (Phase 5)
- Metrics collection integration (Phase 5)

REDIS DATA STRUCTURES:
- Sorted Sets: Used for time-ordered message history
  - Key: ash:history:{guild_id}:{user_id}
  - Score: Unix timestamp (for ordering)
  - Member: JSON string with message data
"""

import asyncio
import logging
from typing import Any, Callable, List, Optional, TYPE_CHECKING

import redis.asyncio as redis
from redis.exceptions import ConnectionError, TimeoutError, AuthenticationError

if TYPE_CHECKING:
    from src.managers.config_manager import ConfigManager
    from src.managers.secrets_manager import SecretsManager
    from src.managers.metrics.metrics_manager import MetricsManager

# Module version
__version__ = "v5.0-5-5.5-1"

# Initialize logger
logger = logging.getLogger(__name__)


# =============================================================================
# Redis Manager
# =============================================================================


class RedisManager:
    """
    Manages Redis connection and low-level operations.

    Provides async Redis operations with connection pooling,
    health checking, graceful error handling, and automatic
    retry with exponential backoff.

    Attributes:
        _config: ConfigManager for Redis settings
        _secrets: SecretsManager for Redis password
        _metrics: Optional MetricsManager for operation tracking
        _client: redis.Redis async client instance
        _host: Redis server hostname
        _port: Redis server port
        _db: Redis database number

    Example:
        >>> redis_mgr = create_redis_manager(config, secrets, metrics)
        >>> await redis_mgr.connect()
        >>> await redis_mgr.zadd("key", 123.0, '{"data": "value"}')
        >>> await redis_mgr.disconnect()
    """

    # Default retry configuration
    DEFAULT_RETRY_ATTEMPTS = 3
    DEFAULT_RETRY_DELAY = 0.5  # seconds
    DEFAULT_RETRY_MAX_DELAY = 5.0  # seconds

    def __init__(
        self,
        config_manager: "ConfigManager",
        secrets_manager: "SecretsManager",
        metrics_manager: Optional["MetricsManager"] = None,
    ) -> None:
        """
        Initialize RedisManager.

        Args:
            config_manager: Configuration manager for Redis settings
            secrets_manager: Secrets manager for Redis password
            metrics_manager: Optional metrics manager for tracking operations

        Note:
            Use create_redis_manager() factory function instead of
            direct instantiation.
        """
        self._config = config_manager
        self._secrets = secrets_manager
        self._metrics = metrics_manager
        self._client: Optional[redis.Redis] = None

        # Load configuration
        self._host = self._config.get("redis", "host", "ash-redis")
        self._port = self._config.get("redis", "port", 6379)
        self._db = self._config.get("redis", "db", 0)

        # Retry configuration
        self._retry_attempts = self._config.get(
            "redis", "retry_attempts", self.DEFAULT_RETRY_ATTEMPTS
        )
        self._retry_delay = self._config.get(
            "redis", "retry_delay", self.DEFAULT_RETRY_DELAY
        )
        self._retry_max_delay = self._config.get(
            "redis", "retry_max_delay", self.DEFAULT_RETRY_MAX_DELAY
        )

        # Connection state tracking
        self._consecutive_failures = 0
        self._total_operations = 0
        self._failed_operations = 0

        logger.debug(
            f"RedisManager initialized (host: {self._host}, port: {self._port}, db: {self._db})"
        )

    # =========================================================================
    # Retry Logic
    # =========================================================================

    async def _with_retry(
        self,
        operation: Callable,
        operation_name: str,
        *args,
        **kwargs,
    ) -> Any:
        """
        Execute Redis operation with retry and exponential backoff.

        Args:
            operation: Async function to execute
            operation_name: Name for logging/metrics
            *args: Positional arguments for operation
            **kwargs: Keyword arguments for operation

        Returns:
            Operation result

        Raises:
            Last exception if all retries fail
        """
        last_error: Optional[Exception] = None
        delay = self._retry_delay

        for attempt in range(self._retry_attempts):
            try:
                self._total_operations += 1
                result = await operation(*args, **kwargs)

                # Success - reset failure counter
                self._consecutive_failures = 0

                # Record metric
                if self._metrics:
                    self._metrics.inc_redis_operations(operation_name, "success")

                return result

            except (ConnectionError, TimeoutError) as e:
                last_error = e
                self._consecutive_failures += 1
                self._failed_operations += 1

                logger.warning(
                    f"⚠️ Redis {operation_name} failed (attempt {attempt + 1}/{self._retry_attempts}): {e}"
                )

                # Record failure metric
                if self._metrics:
                    self._metrics.inc_redis_operations(operation_name, "failure")

                # Wait before retry with exponential backoff
                if attempt < self._retry_attempts - 1:
                    await asyncio.sleep(delay)
                    delay = min(delay * 2, self._retry_max_delay)

                    # Try to reconnect
                    if self._consecutive_failures >= 2:
                        try:
                            await self.reconnect()
                        except Exception as reconnect_error:
                            logger.warning(f"Reconnection failed: {reconnect_error}")

            except Exception as e:
                # Non-retryable error
                self._failed_operations += 1
                if self._metrics:
                    self._metrics.inc_redis_operations(operation_name, "error")
                raise

        # All retries exhausted
        raise last_error or RuntimeError(f"Redis {operation_name} failed after retries")

    # =========================================================================
    # Connection Management
    # =========================================================================

    async def connect(self) -> bool:
        """
        Establish Redis connection.

        Connects to Redis with authentication if password is configured.
        Tests connection with PING command.

        Returns:
            True if connection successful

        Raises:
            ConnectionError: If connection fails
            AuthenticationError: If authentication fails
        """
        if self._client is not None:
            logger.debug("Redis already connected, reusing existing connection")
            return True

        # Get password from secrets (may be None for unauthenticated)
        password = self._secrets.get_redis_token()

        try:
            logger.info(f"🔌 Connecting to Redis at {self._host}:{self._port}...")

            self._client = redis.Redis(
                host=self._host,
                port=self._port,
                db=self._db,
                password=password,
                decode_responses=True,
                socket_timeout=5.0,
                socket_connect_timeout=5.0,
                retry_on_timeout=True,
            )

            # Test connection
            await self._client.ping()

            self._consecutive_failures = 0
            logger.info(f"✅ Connected to Redis at {self._host}:{self._port}")
            return True

        except AuthenticationError as e:
            logger.error(f"❌ Redis authentication failed: {e}")
            self._client = None
            if self._metrics:
                self._metrics.inc_redis_operations("connect", "auth_failure")
            raise

        except (ConnectionError, TimeoutError) as e:
            logger.error(f"❌ Redis connection failed: {e}")
            self._client = None
            if self._metrics:
                self._metrics.inc_redis_operations("connect", "failure")
            raise ConnectionError(f"Failed to connect to Redis: {e}") from e

        except Exception as e:
            logger.error(f"❌ Unexpected Redis error: {e}")
            self._client = None
            raise

    async def disconnect(self) -> None:
        """
        Close Redis connection gracefully.

        Safe to call even if not connected.
        """
        if self._client is not None:
            try:
                await self._client.close()
                logger.info("🔌 Disconnected from Redis")
            except Exception as e:
                logger.warning(f"Error disconnecting from Redis: {e}")
            finally:
                self._client = None

    async def reconnect(self) -> bool:
        """
        Reconnect to Redis.

        Useful for recovering from connection failures.

        Returns:
            True if reconnection successful
        """
        logger.info("🔄 Attempting Redis reconnection...")
        await self.disconnect()
        return await self.connect()

    async def health_check(self) -> bool:
        """
        Check Redis connection health.

        Returns:
            True if Redis is responsive, False otherwise
        """
        try:
            if self._client is None:
                return False

            await self._client.ping()
            return True

        except Exception as e:
            logger.warning(f"Redis health check failed: {e}")
            return False

    async def ping(self) -> bool:
        """
        Ping Redis server.

        Alias for health_check() for compatibility.

        Returns:
            True if Redis is responsive
        """
        return await self.health_check()

    @property
    def is_connected(self) -> bool:
        """
        Check if client is connected (non-blocking check).

        Returns:
            True if client instance exists

        Note:
            This only checks if the client object exists.
            Use health_check() for actual connectivity test.
        """
        return self._client is not None

    # =========================================================================
    # Sorted Set Operations (for time-ordered history)
    # =========================================================================

    async def zadd(
        self,
        key: str,
        score: float,
        member: str,
    ) -> Optional[int]:
        """
        Add member to sorted set with score (timestamp).

        Args:
            key: Redis key
            score: Score (typically Unix timestamp as float)
            member: Value to store (typically JSON string)

        Returns:
            Number of elements added (0 if already exists, 1 if new)
            None if operation failed (graceful degradation)

        Note:
            Returns None on failure for graceful degradation.
        """
        if not self._ensure_connected_safe():
            return None

        try:
            result = await self._with_retry(
                self._client.zadd,
                "zadd",
                key,
                {member: score},
            )
            logger.debug(f"ZADD {key}: score={score:.2f}, added={result}")
            return result
        except Exception as e:
            logger.error(f"❌ ZADD failed for {key}: {e}")
            return None

    async def zrange(
        self,
        key: str,
        start: int,
        stop: int,
        desc: bool = True,
        withscores: bool = False,
    ) -> List[Any]:
        """
        Get range from sorted set.

        Args:
            key: Redis key
            start: Start index (0-based)
            stop: Stop index (-1 for all)
            desc: Reverse order (newest first) - default True
            withscores: Include scores in result

        Returns:
            List of members (or tuples if withscores=True)
            Empty list on failure (graceful degradation)
        """
        if not self._ensure_connected_safe():
            return []

        try:
            if desc:
                result = await self._with_retry(
                    self._client.zrevrange,
                    "zrevrange",
                    key,
                    start,
                    stop,
                    withscores=withscores,
                )
            else:
                result = await self._with_retry(
                    self._client.zrange,
                    "zrange",
                    key,
                    start,
                    stop,
                    withscores=withscores,
                )

            logger.debug(f"ZRANGE {key}: [{start}:{stop}] desc={desc}, count={len(result)}")
            return result
        except Exception as e:
            logger.error(f"❌ ZRANGE failed for {key}: {e}")
            return []

    async def zcard(self, key: str) -> int:
        """
        Get count of members in sorted set.

        Args:
            key: Redis key

        Returns:
            Number of members in the set (0 on failure)
        """
        if not self._ensure_connected_safe():
            return 0

        try:
            count = await self._with_retry(
                self._client.zcard,
                "zcard",
                key,
            )
            logger.debug(f"ZCARD {key}: {count}")
            return count
        except Exception as e:
            logger.error(f"❌ ZCARD failed for {key}: {e}")
            return 0

    async def zremrangebyrank(
        self,
        key: str,
        start: int,
        stop: int,
    ) -> int:
        """
        Remove members by rank (for trimming old entries).

        Ranks are 0-based, lowest score = rank 0.
        Use this to trim oldest entries from history.

        Args:
            key: Redis key
            start: Start rank (0 = oldest)
            stop: Stop rank (inclusive)

        Returns:
            Number of members removed (0 on failure)
        """
        if not self._ensure_connected_safe():
            return 0

        try:
            removed = await self._with_retry(
                self._client.zremrangebyrank,
                "zremrangebyrank",
                key,
                start,
                stop,
            )
            logger.debug(f"ZREMRANGEBYRANK {key}: [{start}:{stop}] removed={removed}")
            return removed
        except Exception as e:
            logger.error(f"❌ ZREMRANGEBYRANK failed for {key}: {e}")
            return 0

    async def zremrangebyscore(
        self,
        key: str,
        min_score: float,
        max_score: float,
    ) -> int:
        """
        Remove members by score range.

        Useful for removing entries older than a timestamp.

        Args:
            key: Redis key
            min_score: Minimum score (inclusive)
            max_score: Maximum score (inclusive)

        Returns:
            Number of members removed (0 on failure)
        """
        if not self._ensure_connected_safe():
            return 0

        try:
            removed = await self._with_retry(
                self._client.zremrangebyscore,
                "zremrangebyscore",
                key,
                min_score,
                max_score,
            )
            logger.debug(
                f"ZREMRANGEBYSCORE {key}: [{min_score}:{max_score}] removed={removed}"
            )
            return removed
        except Exception as e:
            logger.error(f"❌ ZREMRANGEBYSCORE failed for {key}: {e}")
            return 0

    # =========================================================================
    # Key Management
    # =========================================================================

    async def expire(self, key: str, seconds: int) -> bool:
        """
        Set TTL on a key.

        Args:
            key: Redis key
            seconds: TTL in seconds

        Returns:
            True if TTL was set successfully, False on failure
        """
        if not self._ensure_connected_safe():
            return False

        try:
            result = await self._with_retry(
                self._client.expire,
                "expire",
                key,
                seconds,
            )
            logger.debug(f"EXPIRE {key}: {seconds}s, result={result}")
            return result
        except Exception as e:
            logger.error(f"❌ EXPIRE failed for {key}: {e}")
            return False

    async def ttl(self, key: str) -> int:
        """
        Get remaining TTL of a key.

        Args:
            key: Redis key

        Returns:
            TTL in seconds, -1 if no TTL, -2 if key doesn't exist or error
        """
        if not self._ensure_connected_safe():
            return -2

        try:
            return await self._with_retry(
                self._client.ttl,
                "ttl",
                key,
            )
        except Exception as e:
            logger.error(f"❌ TTL failed for {key}: {e}")
            return -2

    async def delete(self, key: str) -> int:
        """
        Delete a key.

        Args:
            key: Redis key

        Returns:
            Number of keys deleted (0 or 1), 0 on failure
        """
        if not self._ensure_connected_safe():
            return 0

        try:
            result = await self._with_retry(
                self._client.delete,
                "delete",
                key,
            )
            logger.debug(f"DELETE {key}: result={result}")
            return result
        except Exception as e:
            logger.error(f"❌ DELETE failed for {key}: {e}")
            return 0

    async def exists(self, key: str) -> bool:
        """
        Check if key exists.

        Args:
            key: Redis key

        Returns:
            True if key exists, False otherwise or on error
        """
        if not self._ensure_connected_safe():
            return False

        try:
            result = await self._with_retry(
                self._client.exists,
                "exists",
                key,
            )
            return result > 0
        except Exception as e:
            logger.error(f"❌ EXISTS failed for {key}: {e}")
            return False

    # =========================================================================
    # Utility Methods
    # =========================================================================

    async def info(self, section: Optional[str] = None) -> Optional[dict]:
        """
        Get Redis server info.

        Args:
            section: Optional section to get (e.g., "memory", "stats")

        Returns:
            Redis INFO as dictionary, None on failure
        """
        if not self._ensure_connected_safe():
            return None

        try:
            if section:
                return await self._client.info(section)
            return await self._client.info()
        except Exception as e:
            logger.error(f"❌ INFO failed: {e}")
            return None

    async def dbsize(self) -> int:
        """
        Get number of keys in current database.

        Returns:
            Number of keys, 0 on failure
        """
        if not self._ensure_connected_safe():
            return 0

        try:
            return await self._client.dbsize()
        except Exception as e:
            logger.error(f"❌ DBSIZE failed: {e}")
            return 0

    def _ensure_connected_safe(self) -> bool:
        """
        Check if connected, log warning if not.

        Returns:
            True if connected, False otherwise
        """
        if self._client is None:
            logger.warning("⚠️ Redis not connected - operation skipped")
            return False
        return True

    def _ensure_connected(self) -> None:
        """
        Ensure Redis is connected.

        Raises:
            RuntimeError: If not connected to Redis
        """
        if self._client is None:
            raise RuntimeError(
                "Not connected to Redis. Call connect() first."
            )

    def get_connection_info(self) -> dict:
        """
        Get connection information (safe for logging).

        Returns:
            Dictionary with connection details (no password)
        """
        return {
            "host": self._host,
            "port": self._port,
            "db": self._db,
            "connected": self.is_connected,
        }

    def get_stats(self) -> dict:
        """
        Get operation statistics.

        Returns:
            Dictionary with operation stats
        """
        return {
            "connected": self.is_connected,
            "total_operations": self._total_operations,
            "failed_operations": self._failed_operations,
            "consecutive_failures": self._consecutive_failures,
            "success_rate": (
                (self._total_operations - self._failed_operations) / self._total_operations
                if self._total_operations > 0
                else 1.0
            ),
        }

    @property
    def consecutive_failures(self) -> int:
        """Get count of consecutive failures."""
        return self._consecutive_failures

    def __repr__(self) -> str:
        """String representation for debugging."""
        status = "connected" if self.is_connected else "disconnected"
        return f"RedisManager({self._host}:{self._port}/{self._db}, {status})"


# =============================================================================
# Factory Function
# =============================================================================


def create_redis_manager(
    config_manager: "ConfigManager",
    secrets_manager: "SecretsManager",
    metrics_manager: Optional["MetricsManager"] = None,
) -> RedisManager:
    """
    Factory function for RedisManager.

    Creates a RedisManager instance with proper dependency injection.
    Use this function instead of direct instantiation.

    Args:
        config_manager: Configuration manager for Redis settings
        secrets_manager: Secrets manager for Redis password
        metrics_manager: Optional metrics manager for operation tracking

    Returns:
        RedisManager instance (not yet connected - call connect())

    Example:
        >>> redis = create_redis_manager(config, secrets, metrics)
        >>> await redis.connect()
        >>> # Use Redis operations
        >>> await redis.disconnect()
    """
    logger.info("🏭 Creating RedisManager")
    return RedisManager(
        config_manager=config_manager,
        secrets_manager=secrets_manager,
        metrics_manager=metrics_manager,
    )


# =============================================================================
# Export public interface
# =============================================================================

__all__ = [
    "RedisManager",
    "create_redis_manager",
]
