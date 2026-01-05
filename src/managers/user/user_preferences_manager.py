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
User Preferences Manager for Ash-Bot Service
---
Manages user preferences including AI opt-out. Users can decline Ash AI
interaction while still receiving human CRT support. Preferences are
stored in Redis with configurable TTL expiration.
----------------------------------------------------------------------------
FILE VERSION: v5.0-7-2.0-1
LAST MODIFIED: 2026-01-04
PHASE: Phase 7 - Core Safety & User Preferences
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-bot
============================================================================
"""

import json
import logging
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from src.managers.config_manager import ConfigManager
    from src.managers.storage.redis_manager import RedisManager

# Module version
__version__ = "v5.0-7-2.0-1"

# Initialize logger
logger = logging.getLogger(__name__)


# =============================================================================
# Constants
# =============================================================================

# Redis key prefix for user preferences
REDIS_KEY_PREFIX = "ash:optout:"

# Default TTL for opt-out (days)
DEFAULT_TTL_DAYS = 30


# =============================================================================
# Data Classes
# =============================================================================


@dataclass
class UserPreference:
    """
    Represents a user's preferences.

    Attributes:
        user_id: Discord user ID
        opted_out: Whether user has opted out of Ash AI
        opted_out_at: When the opt-out was recorded (UTC)
        expires_at: When the opt-out expires (UTC)
    """

    user_id: int
    opted_out: bool
    opted_out_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None

    def is_expired(self) -> bool:
        """Check if the opt-out has expired."""
        if not self.opted_out or not self.expires_at:
            return False
        return datetime.now(timezone.utc) >= self.expires_at

    def days_until_expiry(self) -> Optional[int]:
        """Get days until opt-out expires."""
        if not self.opted_out or not self.expires_at:
            return None
        delta = self.expires_at - datetime.now(timezone.utc)
        return max(0, delta.days)

    def to_dict(self) -> dict:
        """Convert to dictionary for Redis storage."""
        return {
            "user_id": self.user_id,
            "opted_out": self.opted_out,
            "opted_out_at": self.opted_out_at.isoformat() if self.opted_out_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "UserPreference":
        """Create UserPreference from dictionary (Redis retrieval)."""
        return cls(
            user_id=int(data["user_id"]),
            opted_out=data.get("opted_out", False),
            opted_out_at=(
                datetime.fromisoformat(data["opted_out_at"])
                if data.get("opted_out_at")
                else None
            ),
            expires_at=(
                datetime.fromisoformat(data["expires_at"])
                if data.get("expires_at")
                else None
            ),
        )

    def __repr__(self) -> str:
        """String representation for debugging."""
        if not self.opted_out:
            return f"UserPreference(user={self.user_id}, opted_out=False)"
        days = self.days_until_expiry()
        return (
            f"UserPreference(user={self.user_id}, opted_out=True, "
            f"expires_in={days} days)"
        )


# =============================================================================
# User Preferences Manager
# =============================================================================


class UserPreferencesManager:
    """
    Manages user preferences including AI opt-out.

    Stores preferences in Redis with TTL-based expiration. Users who
    opt out of Ash AI interaction will not receive automated DMs but
    will still trigger CRT alerts.

    Attributes:
        config_manager: ConfigManager for settings
        redis_manager: RedisManager for persistent storage

    Example:
        >>> prefs = create_user_preferences_manager(config, redis)
        >>> if await prefs.is_opted_out(user_id):
        ...     # Skip Ash session, alert CRT only
        ...     pass
        >>> else:
        ...     # Normal Ash flow
        ...     await ash_session.start(user)
    """

    def __init__(
        self,
        config_manager: "ConfigManager",
        redis_manager: Optional["RedisManager"],
    ):
        """
        Initialize UserPreferencesManager.

        Args:
            config_manager: Configuration manager for settings
            redis_manager: Redis manager for persistent storage (optional)

        Note:
            Use create_user_preferences_manager() factory function.
        """
        self._config = config_manager
        self._redis = redis_manager

        # Load configuration
        self._enabled = self._config.get(
            "user_preferences", "optout_enabled", True
        )
        self._ttl_days = self._config.get(
            "user_preferences", "optout_ttl_days", DEFAULT_TTL_DAYS
        )

        # In-memory cache for quick lookups
        self._cache: dict[int, UserPreference] = {}

        # Statistics
        self._total_optouts = 0
        self._total_cleared = 0
        self._cache_hits = 0
        self._cache_misses = 0

        logger.info(
            f"✅ UserPreferencesManager initialized "
            f"(enabled={self._enabled}, ttl={self._ttl_days} days)"
        )

    # =========================================================================
    # Opt-Out Management
    # =========================================================================

    async def is_opted_out(self, user_id: int) -> bool:
        """
        Check if a user has opted out of Ash AI interaction.

        Args:
            user_id: Discord user ID

        Returns:
            True if user has opted out and opt-out hasn't expired
        """
        if not self._enabled:
            return False

        # Check cache first
        if user_id in self._cache:
            pref = self._cache[user_id]
            if pref.opted_out and not pref.is_expired():
                self._cache_hits += 1
                return True
            elif pref.is_expired():
                # Clean up expired entry
                del self._cache[user_id]

        self._cache_misses += 1

        # Check Redis
        pref = await self._load_from_redis(user_id)

        if pref and pref.opted_out:
            if pref.is_expired():
                # Clean up expired entry
                await self._delete_from_redis(user_id)
                return False
            else:
                # Cache and return
                self._cache[user_id] = pref
                return True

        return False

    async def set_opt_out(self, user_id: int) -> UserPreference:
        """
        Record a user's opt-out preference.

        Creates or updates the opt-out record with a new expiration.

        Args:
            user_id: Discord user ID

        Returns:
            The created/updated UserPreference
        """
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(days=self._ttl_days)

        pref = UserPreference(
            user_id=user_id,
            opted_out=True,
            opted_out_at=now,
            expires_at=expires_at,
        )

        # Update cache
        self._cache[user_id] = pref

        # Persist to Redis
        await self._save_to_redis(pref)

        # Update stats
        self._total_optouts += 1

        logger.info(
            f"📵 User {user_id} opted out of Ash AI "
            f"(expires in {self._ttl_days} days)"
        )

        return pref

    async def clear_opt_out(self, user_id: int) -> bool:
        """
        Clear a user's opt-out preference (re-enable Ash).

        Args:
            user_id: Discord user ID

        Returns:
            True if opt-out was cleared, False if not found
        """
        # Check if user has an opt-out
        if user_id in self._cache:
            del self._cache[user_id]

        # Delete from Redis
        deleted = await self._delete_from_redis(user_id)

        if deleted:
            self._total_cleared += 1
            logger.info(f"✅ User {user_id} opt-out cleared (Ash re-enabled)")

        return deleted

    async def get_preference(self, user_id: int) -> Optional[UserPreference]:
        """
        Get full preference record for a user.

        Args:
            user_id: Discord user ID

        Returns:
            UserPreference if found, None otherwise
        """
        # Check cache
        if user_id in self._cache:
            return self._cache[user_id]

        # Check Redis
        return await self._load_from_redis(user_id)

    # =========================================================================
    # Redis Operations
    # =========================================================================

    def _redis_key(self, user_id: int) -> str:
        """Get Redis key for a user's preferences."""
        return f"{REDIS_KEY_PREFIX}{user_id}"

    async def _save_to_redis(self, pref: UserPreference) -> None:
        """Save user preference to Redis."""
        if not self._redis or not self._redis.is_connected:
            logger.debug("Redis not available, opt-out stored in memory only")
            return

        try:
            key = self._redis_key(pref.user_id)
            data = json.dumps(pref.to_dict())

            # Calculate TTL in seconds
            ttl_seconds = self._ttl_days * 24 * 60 * 60

            await self._redis.set(key, data, ttl=ttl_seconds)

            logger.debug(f"Saved opt-out for user {pref.user_id} to Redis")

        except Exception as e:
            logger.warning(f"Failed to save opt-out to Redis: {e}")

    async def _load_from_redis(self, user_id: int) -> Optional[UserPreference]:
        """Load user preference from Redis."""
        if not self._redis or not self._redis.is_connected:
            return None

        try:
            key = self._redis_key(user_id)
            data = await self._redis.get(key)

            if data:
                return UserPreference.from_dict(json.loads(data))

        except Exception as e:
            logger.warning(f"Failed to load opt-out from Redis: {e}")

        return None

    async def _delete_from_redis(self, user_id: int) -> bool:
        """Delete user preference from Redis."""
        if not self._redis or not self._redis.is_connected:
            return False

        try:
            key = self._redis_key(user_id)
            result = await self._redis.delete(key)
            # Redis returns number of keys deleted (0 or 1)
            # Mock returns True/False - bool() handles both
            return bool(result)

        except Exception as e:
            logger.warning(f"Failed to delete opt-out from Redis: {e}")
            return False

    # =========================================================================
    # Properties and Statistics
    # =========================================================================

    @property
    def is_enabled(self) -> bool:
        """Check if opt-out feature is enabled."""
        return self._enabled

    @property
    def ttl_days(self) -> int:
        """Get opt-out TTL in days."""
        return self._ttl_days

    @property
    def cached_count(self) -> int:
        """Get count of cached preferences."""
        return len(self._cache)

    def get_stats(self) -> dict:
        """
        Get user preferences statistics.

        Returns:
            Dictionary with statistics
        """
        return {
            "enabled": self._enabled,
            "ttl_days": self._ttl_days,
            "cached_count": len(self._cache),
            "total_optouts": self._total_optouts,
            "total_cleared": self._total_cleared,
            "cache_hits": self._cache_hits,
            "cache_misses": self._cache_misses,
            "cache_hit_rate": (
                self._cache_hits / (self._cache_hits + self._cache_misses)
                if (self._cache_hits + self._cache_misses) > 0
                else 0.0
            ),
        }

    def __repr__(self) -> str:
        """String representation for debugging."""
        return (
            f"UserPreferencesManager("
            f"enabled={self._enabled}, "
            f"cached={len(self._cache)}, "
            f"optouts={self._total_optouts})"
        )


# =============================================================================
# Factory Function
# =============================================================================


def create_user_preferences_manager(
    config_manager: "ConfigManager",
    redis_manager: Optional["RedisManager"],
) -> UserPreferencesManager:
    """
    Factory function for UserPreferencesManager.

    Creates a configured UserPreferencesManager instance.
    Following Clean Architecture v5.1 Rule #1: Factory Functions.

    Args:
        config_manager: Configuration manager instance
        redis_manager: Redis manager for persistence (optional)

    Returns:
        Configured UserPreferencesManager instance

    Example:
        >>> prefs = create_user_preferences_manager(config, redis)
        >>> if await prefs.is_opted_out(user_id):
        ...     print("User prefers human support")
    """
    logger.info("🏭 Creating UserPreferencesManager")

    return UserPreferencesManager(
        config_manager=config_manager,
        redis_manager=redis_manager,
    )


# =============================================================================
# Export public interface
# =============================================================================

__all__ = [
    "UserPreferencesManager",
    "create_user_preferences_manager",
    "UserPreference",
]
