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
FILE VERSION: v5.0-2-3.0-1
LAST MODIFIED: 2026-01-03
PHASE: Phase 2 - Redis History Storage
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-bot
Community: The Alphabet Cartel - https://discord.gg/alphabetcartel | https://alphabetcartel.org
============================================================================

RESPONSIBILITIES:
- Establish and manage authenticated Redis connection
- Provide async Redis operations for sorted sets
- Handle connection pooling and health checking
- Graceful error handling with reconnection support

REDIS DATA STRUCTURES:
- Sorted Sets: Used for time-ordered message history
  - Key: ash:history:{guild_id}:{user_id}
  - Score: Unix timestamp (for ordering)
  - Member: JSON string with message data
"""

import logging
from typing import Any, List, Optional, TYPE_CHECKING

import redis.asyncio as redis
from redis.exceptions import ConnectionError, TimeoutError, AuthenticationError

if TYPE_CHECKING:
    from src.managers.config_manager import ConfigManager
    from src.managers.secrets_manager import SecretsManager

# Module version
__version__ = "v5.0-2-3.0-1"

# Initialize logger
logger = logging.getLogger(__name__)


# =============================================================================
# Redis Manager
# =============================================================================


class RedisManager:
    """
    Manages Redis connection and low-level operations.

    Provides async Redis operations with connection pooling,
    health checking, and graceful error handling.

    Attributes:
        _config: ConfigManager for Redis settings
        _secrets: SecretsManager for Redis password
        _client: redis.Redis async client instance
        _host: Redis server hostname
        _port: Redis server port
        _db: Redis database number

    Example:
        >>> redis_mgr = create_redis_manager(config, secrets)
        >>> await redis_mgr.connect()
        >>> await redis_mgr.zadd("key", 123.0, '{"data": "value"}')
        >>> await redis_mgr.disconnect()
    """

    def __init__(
        self,
        config_manager: "ConfigManager",
        secrets_manager: "SecretsManager",
    ) -> None:
        """
        Initialize RedisManager.

        Args:
            config_manager: Configuration manager for Redis settings
            secrets_manager: Secrets manager for Redis password

        Note:
            Use create_redis_manager() factory function instead of
            direct instantiation.
        """
        self._config = config_manager
        self._secrets = secrets_manager
        self._client: Optional[redis.Redis] = None

        # Load configuration
        self._host = self._config.get("redis", "host", "ash-redis")
        self._port = self._config.get("redis", "port", 6379)
        self._db = self._config.get("redis", "db", 0)

        logger.debug(
            f"RedisManager initialized (host: {self._host}, port: {self._port}, db: {self._db})"
        )

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

            logger.info(f"✅ Connected to Redis at {self._host}:{self._port}")
            return True

        except AuthenticationError as e:
            logger.error(f"❌ Redis authentication failed: {e}")
            self._client = None
            raise

        except (ConnectionError, TimeoutError) as e:
            logger.error(f"❌ Redis connection failed: {e}")
            self._client = None
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
    ) -> int:
        """
        Add member to sorted set with score (timestamp).

        Args:
            key: Redis key
            score: Score (typically Unix timestamp as float)
            member: Value to store (typically JSON string)

        Returns:
            Number of elements added (0 if already exists, 1 if new)

        Raises:
            RuntimeError: If not connected to Redis
        """
        self._ensure_connected()

        result = await self._client.zadd(key, {member: score})
        logger.debug(f"ZADD {key}: score={score:.2f}, added={result}")
        return result

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

        Raises:
            RuntimeError: If not connected to Redis
        """
        self._ensure_connected()

        if desc:
            result = await self._client.zrevrange(
                key, start, stop, withscores=withscores
            )
        else:
            result = await self._client.zrange(
                key, start, stop, withscores=withscores
            )

        logger.debug(f"ZRANGE {key}: [{start}:{stop}] desc={desc}, count={len(result)}")
        return result

    async def zcard(self, key: str) -> int:
        """
        Get count of members in sorted set.

        Args:
            key: Redis key

        Returns:
            Number of members in the set
        """
        self._ensure_connected()

        count = await self._client.zcard(key)
        logger.debug(f"ZCARD {key}: {count}")
        return count

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
            Number of members removed
        """
        self._ensure_connected()

        removed = await self._client.zremrangebyrank(key, start, stop)
        logger.debug(f"ZREMRANGEBYRANK {key}: [{start}:{stop}] removed={removed}")
        return removed

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
            Number of members removed
        """
        self._ensure_connected()

        removed = await self._client.zremrangebyscore(key, min_score, max_score)
        logger.debug(
            f"ZREMRANGEBYSCORE {key}: [{min_score}:{max_score}] removed={removed}"
        )
        return removed

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
            True if TTL was set successfully
        """
        self._ensure_connected()

        result = await self._client.expire(key, seconds)
        logger.debug(f"EXPIRE {key}: {seconds}s, result={result}")
        return result

    async def ttl(self, key: str) -> int:
        """
        Get remaining TTL of a key.

        Args:
            key: Redis key

        Returns:
            TTL in seconds, -1 if no TTL, -2 if key doesn't exist
        """
        self._ensure_connected()

        return await self._client.ttl(key)

    async def delete(self, key: str) -> int:
        """
        Delete a key.

        Args:
            key: Redis key

        Returns:
            Number of keys deleted (0 or 1)
        """
        self._ensure_connected()

        result = await self._client.delete(key)
        logger.debug(f"DELETE {key}: result={result}")
        return result

    async def exists(self, key: str) -> bool:
        """
        Check if key exists.

        Args:
            key: Redis key

        Returns:
            True if key exists
        """
        self._ensure_connected()

        return await self._client.exists(key) > 0

    # =========================================================================
    # Utility Methods
    # =========================================================================

    async def info(self, section: Optional[str] = None) -> dict:
        """
        Get Redis server info.

        Args:
            section: Optional section to get (e.g., "memory", "stats")

        Returns:
            Redis INFO as dictionary
        """
        self._ensure_connected()

        if section:
            return await self._client.info(section)
        return await self._client.info()

    async def dbsize(self) -> int:
        """
        Get number of keys in current database.

        Returns:
            Number of keys
        """
        self._ensure_connected()

        return await self._client.dbsize()

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
) -> RedisManager:
    """
    Factory function for RedisManager.

    Creates a RedisManager instance with proper dependency injection.
    Use this function instead of direct instantiation.

    Args:
        config_manager: Configuration manager for Redis settings
        secrets_manager: Secrets manager for Redis password

    Returns:
        RedisManager instance (not yet connected - call connect())

    Example:
        >>> redis = create_redis_manager(config, secrets)
        >>> await redis.connect()
        >>> # Use Redis operations
        >>> await redis.disconnect()
    """
    logger.debug("Creating RedisManager via factory function")
    return RedisManager(
        config_manager=config_manager,
        secrets_manager=secrets_manager,
    )


# =============================================================================
# Export public interface
# =============================================================================

__all__ = [
    "RedisManager",
    "create_redis_manager",
]
