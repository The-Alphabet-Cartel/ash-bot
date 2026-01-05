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
Cooldown Manager for Ash-Bot Service
---
FILE VERSION: v5.0-3-2.0-1
LAST MODIFIED: 2026-01-04
PHASE: Phase 3 - Alert Dispatching
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-bot
Community: The Alphabet Cartel - https://discord.gg/alphabetcartel | https://alphabetcartel.org
============================================================================
RESPONSIBILITIES:
- Track alert cooldowns per user to prevent spam
- Provide configurable cooldown duration
- Auto-expire cooldowns after duration
- Support manual cooldown clearing

USAGE:
    from src.managers.alerting import create_cooldown_manager

    cooldown = create_cooldown_manager(config_manager)

    if not cooldown.is_on_cooldown(user_id):
        # Send alert
        cooldown.set_cooldown(user_id)
"""

from datetime import datetime, timezone, timedelta
from typing import Dict, Optional, TYPE_CHECKING
import logging

if TYPE_CHECKING:
    from src.managers.config_manager import ConfigManager

# Module version
__version__ = "v5.0-3-2.0-1"

# Initialize logger
logger = logging.getLogger(__name__)


# =============================================================================
# Cooldown Manager
# =============================================================================


class CooldownManager:
    """
    Manages alert cooldowns to prevent spam.

    Prevents multiple alerts for the same user within a cooldown period.
    Uses in-memory storage (resets on restart).

    Attributes:
        config_manager: ConfigManager for cooldown duration
        cooldowns: Dict mapping user_id to cooldown expiry time

    Example:
        >>> cooldown = create_cooldown_manager(config_manager)
        >>> if not cooldown.is_on_cooldown(user_id):
        ...     await dispatch_alert(message, result)
        ...     cooldown.set_cooldown(user_id)
    """

    def __init__(self, config_manager: "ConfigManager"):
        """
        Initialize CooldownManager.

        Args:
            config_manager: Configuration manager

        Note:
            Use create_cooldown_manager() factory function.
        """
        self._config = config_manager
        self._cooldowns: Dict[int, datetime] = {}

        # Load cooldown duration (seconds)
        self._cooldown_seconds = self._config.get(
            "alerting", "cooldown_seconds", 300  # 5 minutes default
        )

        logger.info(
            f"✅ CooldownManager initialized ({self._cooldown_seconds}s cooldown)"
        )

    # =========================================================================
    # Cooldown Check Methods
    # =========================================================================

    def is_on_cooldown(self, user_id: int) -> bool:
        """
        Check if a user is on alert cooldown.

        Args:
            user_id: Discord user ID

        Returns:
            True if user is on cooldown
        """
        if user_id not in self._cooldowns:
            return False

        expiry = self._cooldowns[user_id]
        now = datetime.now(timezone.utc)

        if now >= expiry:
            # Cooldown expired, clean up
            del self._cooldowns[user_id]
            return False

        return True

    def set_cooldown(self, user_id: int, duration_seconds: Optional[int] = None) -> None:
        """
        Set cooldown for a user.

        Args:
            user_id: Discord user ID
            duration_seconds: Optional custom duration (uses default if None)
        """
        duration = duration_seconds or self._cooldown_seconds
        expiry = datetime.now(timezone.utc) + timedelta(seconds=duration)
        self._cooldowns[user_id] = expiry

        logger.debug(
            f"⏱️ Cooldown set for user {user_id} until {expiry.isoformat()}"
        )

    def clear_cooldown(self, user_id: int) -> bool:
        """
        Clear cooldown for a user (manual override).

        Args:
            user_id: Discord user ID

        Returns:
            True if cooldown was cleared
        """
        if user_id in self._cooldowns:
            del self._cooldowns[user_id]
            logger.info(f"⏱️ Cooldown cleared for user {user_id}")
            return True
        return False

    def get_remaining_cooldown(self, user_id: int) -> int:
        """
        Get remaining cooldown time in seconds.

        Args:
            user_id: Discord user ID

        Returns:
            Remaining seconds, or 0 if not on cooldown
        """
        if user_id not in self._cooldowns:
            return 0

        expiry = self._cooldowns[user_id]
        now = datetime.now(timezone.utc)

        if now >= expiry:
            # Cleanup expired
            del self._cooldowns[user_id]
            return 0

        return int((expiry - now).total_seconds())

    def get_expiry_time(self, user_id: int) -> Optional[datetime]:
        """
        Get the cooldown expiry time for a user.

        Args:
            user_id: Discord user ID

        Returns:
            Expiry datetime or None if not on cooldown
        """
        if user_id not in self._cooldowns:
            return None

        expiry = self._cooldowns[user_id]
        now = datetime.now(timezone.utc)

        if now >= expiry:
            del self._cooldowns[user_id]
            return None

        return expiry

    # =========================================================================
    # Cleanup Methods
    # =========================================================================

    def cleanup_expired(self) -> int:
        """
        Remove all expired cooldowns.

        Returns:
            Number of cooldowns cleaned up
        """
        now = datetime.now(timezone.utc)
        expired = [
            user_id for user_id, expiry in self._cooldowns.items()
            if now >= expiry
        ]

        for user_id in expired:
            del self._cooldowns[user_id]

        if expired:
            logger.debug(f"🧹 Cleaned up {len(expired)} expired cooldowns")

        return len(expired)

    def clear_all(self) -> int:
        """
        Clear all cooldowns (admin function).

        Returns:
            Number of cooldowns cleared
        """
        count = len(self._cooldowns)
        self._cooldowns.clear()

        if count > 0:
            logger.info(f"🧹 Cleared all {count} cooldowns")

        return count

    # =========================================================================
    # Properties
    # =========================================================================

    @property
    def active_cooldown_count(self) -> int:
        """Get count of active (non-expired) cooldowns."""
        # Cleanup expired first
        self.cleanup_expired()
        return len(self._cooldowns)

    @property
    def cooldown_duration(self) -> int:
        """Get configured cooldown duration in seconds."""
        return self._cooldown_seconds

    @property
    def all_cooldowns(self) -> Dict[int, datetime]:
        """Get copy of all active cooldowns (for debugging)."""
        # Cleanup expired first
        self.cleanup_expired()
        return self._cooldowns.copy()

    # =========================================================================
    # Status Methods
    # =========================================================================

    def get_status(self) -> dict:
        """
        Get cooldown manager status.

        Returns:
            Status dictionary for logging/debugging
        """
        self.cleanup_expired()
        return {
            "active_cooldowns": len(self._cooldowns),
            "cooldown_duration_seconds": self._cooldown_seconds,
            "cooldown_duration_minutes": self._cooldown_seconds / 60,
        }

    def __repr__(self) -> str:
        """String representation for debugging."""
        return (
            f"CooldownManager("
            f"active={self.active_cooldown_count}, "
            f"duration={self._cooldown_seconds}s)"
        )


# =============================================================================
# Factory Function
# =============================================================================


def create_cooldown_manager(
    config_manager: "ConfigManager",
) -> CooldownManager:
    """
    Factory function for CooldownManager.

    Creates a CooldownManager instance with configuration.
    Following Clean Architecture v5.1 Rule #1: Factory Functions.

    Args:
        config_manager: Configuration manager instance

    Returns:
        Configured CooldownManager instance

    Example:
        >>> cooldown = create_cooldown_manager(config_manager)
        >>> if not cooldown.is_on_cooldown(user_id):
        ...     cooldown.set_cooldown(user_id)
    """
    logger.info("🏭 Creating CooldownManager")
    return CooldownManager(config_manager=config_manager)


# =============================================================================
# Export public interface
# =============================================================================

__all__ = [
    "CooldownManager",
    "create_cooldown_manager",
]
