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
User History Manager for Ash-Bot Service
----------------------------------------------------------------------------
FILE VERSION: v5.0-2-4.0-1
LAST MODIFIED: 2026-01-03
PHASE: Phase 2 - Redis History Storage
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-bot
Community: The Alphabet Cartel - https://discord.gg/alphabetcartel | https://alphabetcartel.org
============================================================================

RESPONSIBILITIES:
- Store messages with crisis indicators (LOW+) to Redis
- Retrieve recent history for NLP context
- Enforce TTL-based expiration and max message limits
- Provide per-user, per-guild isolation

STORAGE RULES:
- SAFE severity: NOT stored (no crisis indicators)
- LOW severity: Stored (may indicate developing pattern)
- MEDIUM severity: Stored (confirmed concern)
- HIGH severity: Stored (significant crisis)
- CRITICAL severity: Stored (immediate crisis)

KEY FORMAT:
    ash:history:{guild_id}:{user_id}

DATA STRUCTURE:
    Redis Sorted Set with:
    - Score: Unix timestamp (for ordering)
    - Member: JSON string with message data
"""

import json
import logging
from datetime import datetime, timezone
from typing import List, Optional, TYPE_CHECKING

from src.models.history_models import StoredMessage
from src.models.nlp_models import MessageHistoryItem, CrisisAnalysisResult

if TYPE_CHECKING:
    from src.managers.config_manager import ConfigManager
    from src.managers.storage.redis_manager import RedisManager

# Module version
__version__ = "v5.0-2-4.0-1"

# Initialize logger
logger = logging.getLogger(__name__)


# =============================================================================
# Constants
# =============================================================================

# Severity levels that qualify for storage (LOW and higher)
STORABLE_SEVERITIES = frozenset({"low", "medium", "high", "critical"})

# Redis key prefix
KEY_PREFIX = "ash:history"


# =============================================================================
# User History Manager
# =============================================================================


class UserHistoryManager:
    """
    Manages user message history in Redis.

    Stores messages with crisis indicators (LOW+) and retrieves
    recent history for NLP context analysis. Enforces TTL-based
    expiration and maximum message limits per user.

    Attributes:
        _config: ConfigManager for history settings
        _redis: RedisManager for storage operations
        _ttl_days: Days to retain history
        _max_messages: Maximum messages per user
        _min_severity: Minimum severity to store

    Key Format:
        ash:history:{guild_id}:{user_id}

    Example:
        >>> history = create_user_history_manager(config, redis)
        >>> await history.add_message(guild_id, user_id, msg, result)
        >>> recent = await history.get_history(guild_id, user_id)
    """

    def __init__(
        self,
        config_manager: "ConfigManager",
        redis_manager: "RedisManager",
    ) -> None:
        """
        Initialize UserHistoryManager.

        Args:
            config_manager: Configuration manager for history settings
            redis_manager: RedisManager for storage operations

        Note:
            Use create_user_history_manager() factory function instead
            of direct instantiation.
        """
        self._config = config_manager
        self._redis = redis_manager

        # Load configuration
        self._ttl_days = self._config.get("history", "ttl_days", 14)
        self._max_messages = self._config.get("history", "max_messages", 100)
        self._min_severity = self._config.get(
            "history", "min_severity_to_store", "low"
        ).lower()

        # Calculate TTL in seconds
        self._ttl_seconds = self._ttl_days * 24 * 60 * 60

        logger.info(
            f"📚 UserHistoryManager initialized "
            f"(TTL: {self._ttl_days}d, max: {self._max_messages} msgs, "
            f"min_severity: {self._min_severity})"
        )

    # =========================================================================
    # Key Generation
    # =========================================================================

    def _make_key(self, guild_id: int, user_id: int) -> str:
        """
        Generate Redis key for user history.

        Args:
            guild_id: Discord guild ID
            user_id: Discord user ID

        Returns:
            Redis key string: ash:history:{guild_id}:{user_id}
        """
        return f"{KEY_PREFIX}:{guild_id}:{user_id}"

    @staticmethod
    def parse_key(key: str) -> tuple[Optional[int], Optional[int]]:
        """
        Parse guild_id and user_id from Redis key.

        Args:
            key: Redis key string

        Returns:
            Tuple of (guild_id, user_id) or (None, None) if invalid
        """
        try:
            parts = key.split(":")
            if len(parts) == 4 and parts[0] == "ash" and parts[1] == "history":
                return int(parts[2]), int(parts[3])
        except (ValueError, IndexError):
            pass
        return None, None

    # =========================================================================
    # Severity Checking
    # =========================================================================

    def _should_store(self, severity: str) -> bool:
        """
        Check if message severity qualifies for storage.

        Messages are stored if their severity is at or above
        the configured minimum severity threshold.

        Args:
            severity: Crisis severity level

        Returns:
            True if message should be stored
        """
        return severity.lower() in STORABLE_SEVERITIES

    # =========================================================================
    # Storage Operations
    # =========================================================================

    async def add_message(
        self,
        guild_id: int,
        user_id: int,
        message: str,
        analysis_result: CrisisAnalysisResult,
        message_id: Optional[str] = None,
    ) -> bool:
        """
        Add a message to user's history.

        Only stores if severity is LOW or higher.
        Automatically manages TTL and trims to max_messages.

        Args:
            guild_id: Discord guild ID
            user_id: Discord user ID
            message: Original message content
            analysis_result: NLP analysis result
            message_id: Optional Discord message ID

        Returns:
            True if message was stored, False if skipped

        Note:
            Messages with SAFE severity are not stored.
        """
        # Check severity threshold
        if not self._should_store(analysis_result.severity):
            logger.debug(
                f"⏭️ Skipping storage for user {user_id}: "
                f"severity {analysis_result.severity} below threshold"
            )
            return False

        key = self._make_key(guild_id, user_id)
        timestamp = datetime.now(timezone.utc)

        # Create stored message
        stored_msg = StoredMessage.create(
            message=message,
            timestamp=timestamp,
            crisis_score=analysis_result.crisis_score,
            severity=analysis_result.severity,
            message_id=message_id,
        )

        # Score = timestamp as float for chronological ordering
        score = timestamp.timestamp()

        try:
            # Add to sorted set
            await self._redis.zadd(key, score, json.dumps(stored_msg.to_dict()))

            # Set/refresh TTL
            await self._redis.expire(key, self._ttl_seconds)

            # Trim to max messages if needed
            await self._trim_history(key)

            logger.debug(
                f"📝 Stored message for user {user_id} "
                f"(severity: {analysis_result.severity}, "
                f"score: {analysis_result.crisis_score:.2f})"
            )

            return True

        except Exception as e:
            logger.error(f"❌ Failed to store message for user {user_id}: {e}")
            return False

    async def _trim_history(self, key: str) -> None:
        """
        Trim history to max_messages, removing oldest entries.

        Args:
            key: Redis key
        """
        count = await self._redis.zcard(key)

        if count > self._max_messages:
            # Remove oldest entries (lowest scores)
            to_remove = count - self._max_messages
            await self._redis.zremrangebyrank(key, 0, to_remove - 1)
            logger.debug(f"🔪 Trimmed {to_remove} old messages from {key}")

    # =========================================================================
    # Retrieval Operations
    # =========================================================================

    async def get_history(
        self,
        guild_id: int,
        user_id: int,
        limit: int = 20,
    ) -> List[MessageHistoryItem]:
        """
        Get recent message history for a user.

        Returns messages in newest-first order, suitable for
        inclusion in NLP context requests.

        Args:
            guild_id: Discord guild ID
            user_id: Discord user ID
            limit: Maximum messages to retrieve (default: 20)

        Returns:
            List of MessageHistoryItem (newest first)
        """
        key = self._make_key(guild_id, user_id)

        try:
            # Get most recent entries (highest scores = newest)
            entries = await self._redis.zrange(key, 0, limit - 1, desc=True)

            history: List[MessageHistoryItem] = []
            for entry_json in entries:
                try:
                    entry_data = json.loads(entry_json)
                    stored_msg = StoredMessage.from_dict(entry_data)
                    history.append(stored_msg.to_history_item())
                except (json.JSONDecodeError, KeyError, ValueError) as e:
                    logger.warning(f"⚠️ Invalid history entry: {e}")
                    continue

            logger.debug(
                f"📖 Retrieved {len(history)} history entries for user {user_id}"
            )
            return history

        except Exception as e:
            logger.error(f"❌ Failed to get history for user {user_id}: {e}")
            return []

    async def get_stored_messages(
        self,
        guild_id: int,
        user_id: int,
        limit: int = 20,
    ) -> List[StoredMessage]:
        """
        Get stored messages with full metadata.

        Unlike get_history(), this returns StoredMessage objects
        which include severity and other storage metadata.

        Args:
            guild_id: Discord guild ID
            user_id: Discord user ID
            limit: Maximum messages to retrieve

        Returns:
            List of StoredMessage (newest first)
        """
        key = self._make_key(guild_id, user_id)

        try:
            entries = await self._redis.zrange(key, 0, limit - 1, desc=True)

            messages: List[StoredMessage] = []
            for entry_json in entries:
                try:
                    entry_data = json.loads(entry_json)
                    messages.append(StoredMessage.from_dict(entry_data))
                except (json.JSONDecodeError, KeyError, ValueError) as e:
                    logger.warning(f"⚠️ Invalid stored message: {e}")
                    continue

            return messages

        except Exception as e:
            logger.error(f"❌ Failed to get stored messages for user {user_id}: {e}")
            return []

    async def get_history_count(self, guild_id: int, user_id: int) -> int:
        """
        Get count of stored messages for user.

        Args:
            guild_id: Discord guild ID
            user_id: Discord user ID

        Returns:
            Number of stored messages
        """
        key = self._make_key(guild_id, user_id)

        try:
            return await self._redis.zcard(key)
        except Exception as e:
            logger.error(f"❌ Failed to get history count for user {user_id}: {e}")
            return 0

    # =========================================================================
    # History Management
    # =========================================================================

    async def clear_history(self, guild_id: int, user_id: int) -> bool:
        """
        Clear all history for a user.

        Args:
            guild_id: Discord guild ID
            user_id: Discord user ID

        Returns:
            True if history was cleared
        """
        key = self._make_key(guild_id, user_id)

        try:
            result = await self._redis.delete(key)

            if result > 0:
                logger.info(f"🗑️ Cleared history for user {user_id} in guild {guild_id}")
                return True

            logger.debug(f"No history to clear for user {user_id}")
            return False

        except Exception as e:
            logger.error(f"❌ Failed to clear history for user {user_id}: {e}")
            return False

    async def has_history(self, guild_id: int, user_id: int) -> bool:
        """
        Check if user has any stored history.

        Args:
            guild_id: Discord guild ID
            user_id: Discord user ID

        Returns:
            True if user has stored history
        """
        key = self._make_key(guild_id, user_id)

        try:
            return await self._redis.exists(key)
        except Exception as e:
            logger.error(f"❌ Failed to check history for user {user_id}: {e}")
            return False

    async def get_history_ttl(self, guild_id: int, user_id: int) -> int:
        """
        Get remaining TTL for user's history.

        Args:
            guild_id: Discord guild ID
            user_id: Discord user ID

        Returns:
            TTL in seconds, -1 if no TTL, -2 if key doesn't exist
        """
        key = self._make_key(guild_id, user_id)

        try:
            return await self._redis.ttl(key)
        except Exception as e:
            logger.error(f"❌ Failed to get TTL for user {user_id}: {e}")
            return -2

    # =========================================================================
    # Statistics
    # =========================================================================

    async def get_user_stats(
        self,
        guild_id: int,
        user_id: int,
    ) -> dict:
        """
        Get statistics about user's history.

        Args:
            guild_id: Discord guild ID
            user_id: Discord user ID

        Returns:
            Dictionary with history statistics
        """
        key = self._make_key(guild_id, user_id)

        try:
            count = await self._redis.zcard(key)
            ttl = await self._redis.ttl(key)

            # Get severity distribution
            messages = await self.get_stored_messages(guild_id, user_id, limit=100)
            severity_counts = {"low": 0, "medium": 0, "high": 0, "critical": 0}

            for msg in messages:
                if msg.severity in severity_counts:
                    severity_counts[msg.severity] += 1

            return {
                "message_count": count,
                "ttl_seconds": ttl,
                "ttl_days": round(ttl / 86400, 1) if ttl > 0 else 0,
                "severity_distribution": severity_counts,
                "has_history": count > 0,
            }

        except Exception as e:
            logger.error(f"❌ Failed to get stats for user {user_id}: {e}")
            return {
                "message_count": 0,
                "ttl_seconds": -2,
                "ttl_days": 0,
                "severity_distribution": {},
                "has_history": False,
                "error": str(e),
            }

    # =========================================================================
    # Configuration Access
    # =========================================================================

    @property
    def ttl_days(self) -> int:
        """Get configured TTL in days."""
        return self._ttl_days

    @property
    def max_messages(self) -> int:
        """Get configured max messages per user."""
        return self._max_messages

    @property
    def min_severity(self) -> str:
        """Get configured minimum severity to store."""
        return self._min_severity

    def __repr__(self) -> str:
        """String representation for debugging."""
        return (
            f"UserHistoryManager("
            f"ttl={self._ttl_days}d, "
            f"max={self._max_messages}, "
            f"min_severity={self._min_severity})"
        )


# =============================================================================
# Factory Function
# =============================================================================


def create_user_history_manager(
    config_manager: "ConfigManager",
    redis_manager: "RedisManager",
) -> UserHistoryManager:
    """
    Factory function for UserHistoryManager.

    Creates a UserHistoryManager instance with proper dependency injection.
    Use this function instead of direct instantiation.

    Args:
        config_manager: Configuration manager for history settings
        redis_manager: RedisManager for storage operations

    Returns:
        UserHistoryManager instance

    Example:
        >>> redis = create_redis_manager(config, secrets)
        >>> await redis.connect()
        >>> history = create_user_history_manager(config, redis)
        >>> await history.add_message(guild_id, user_id, msg, result)
    """
    logger.debug("Creating UserHistoryManager via factory function")
    return UserHistoryManager(
        config_manager=config_manager,
        redis_manager=redis_manager,
    )


# =============================================================================
# Export public interface
# =============================================================================

__all__ = [
    "UserHistoryManager",
    "create_user_history_manager",
    "STORABLE_SEVERITIES",
    "KEY_PREFIX",
]
