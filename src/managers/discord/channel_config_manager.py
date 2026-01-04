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
Channel Configuration Manager for Ash-Bot Service
---
FILE VERSION: v5.0-1-1.4-1
LAST MODIFIED: 2026-01-03
PHASE: Phase 1 - Discord Connectivity
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-bot
Community: The Alphabet Cartel - https://discord.gg/alphabetcartel | https://alphabetcartel.org
============================================================================
RESPONSIBILITIES:
- Load and manage channel whitelist from configuration
- Determine if channels should be monitored
- Route alerts to appropriate channels by severity
- Provide CRT role ID for pinging

USAGE:
    from src.managers.discord import create_channel_config_manager

    channel_config = create_channel_config_manager(config_manager)

    if channel_config.is_monitored_channel(channel_id):
        # Process message
        alert_channel = channel_config.get_alert_channel("high")
"""

import json
import logging
from typing import List, Optional, Set, TYPE_CHECKING

if TYPE_CHECKING:
    from src.managers.config_manager import ConfigManager

# Module version
__version__ = "v5.0-1-1.4-1"

# Initialize logger
logger = logging.getLogger(__name__)


# =============================================================================
# Channel Config Manager
# =============================================================================


class ChannelConfigManager:
    """
    Manages channel whitelist and alert routing configuration.

    Handles which channels are monitored for messages and where
    alerts should be sent based on crisis severity.

    Attributes:
        config_manager: Configuration manager instance
        _monitored_channels: Set of monitored channel IDs
        _alert_channels: Dict mapping severity to channel ID
        _crt_role_id: Crisis Response Team role ID
        _guild_id: Target guild ID (optional)

    Example:
        >>> channel_config = create_channel_config_manager(config_manager)
        >>> channel_config.is_monitored_channel(123456789)
        True
        >>> channel_config.get_alert_channel("high")
        987654321
    """

    def __init__(self, config_manager: "ConfigManager"):
        """
        Initialize ChannelConfigManager.

        Args:
            config_manager: Configuration manager instance

        Note:
            Use create_channel_config_manager() factory function.
        """
        self.config_manager = config_manager

        # Internal storage
        self._monitored_channels: Set[int] = set()
        self._alert_channels: dict = {
            "medium": None,
            "high": None,
            "critical": None,
        }
        self._crt_role_id: Optional[int] = None
        self._guild_id: Optional[int] = None

        # Load configuration
        self._load_config()

        logger.info(
            f"✅ ChannelConfigManager initialized "
            f"(monitored={len(self._monitored_channels)} channels)"
        )

    # =========================================================================
    # Configuration Loading
    # =========================================================================

    def _load_config(self) -> None:
        """
        Load channel configuration from ConfigManager.

        Loads:
        - Monitored channel whitelist
        - Alert channel mappings
        - CRT role ID
        - Guild ID
        """
        # Load channels config
        channels_config = self.config_manager.get_section("channels")

        # Load monitored channels (supports JSON string or list)
        monitored_raw = channels_config.get("monitored_channels", [])
        self._monitored_channels = self._parse_channel_ids(monitored_raw)

        # Load alert channels
        self._alert_channels["medium"] = self._parse_single_id(
            channels_config.get("alert_channel_monitor")
        )
        self._alert_channels["high"] = self._parse_single_id(
            channels_config.get("alert_channel_crisis")
        )
        self._alert_channels["critical"] = self._parse_single_id(
            channels_config.get("alert_channel_critical")
        )

        # Load alerting config
        alerting_config = self.config_manager.get_section("alerting")
        self._crt_role_id = self._parse_single_id(alerting_config.get("crt_role_id"))

        # Load discord config
        discord_config = self.config_manager.get_section("discord")
        self._guild_id = self._parse_single_id(discord_config.get("guild_id"))

        # Log configuration
        logger.debug(f"  Monitored channels: {len(self._monitored_channels)}")
        logger.debug(f"  Alert channels: {self._alert_channels}")
        logger.debug(f"  CRT role ID: {self._crt_role_id}")
        logger.debug(f"  Guild ID: {self._guild_id}")

    def _parse_channel_ids(self, value) -> Set[int]:
        """
        Parse channel IDs from various formats.

        Supports:
        - List of integers: [123, 456]
        - List of strings: ["123", "456"]
        - JSON string: '["123", "456"]'
        - Empty/None: set()

        Args:
            value: Raw channel ID value(s)

        Returns:
            Set of integer channel IDs
        """
        if value is None:
            return set()

        # If it's a string, try to parse as JSON
        if isinstance(value, str):
            value = value.strip()
            if not value:
                return set()
            try:
                value = json.loads(value)
            except json.JSONDecodeError:
                # Maybe it's a single ID
                parsed = self._parse_single_id(value)
                return {parsed} if parsed else set()

        # If it's a list, parse each element
        if isinstance(value, (list, tuple)):
            result = set()
            for item in value:
                parsed = self._parse_single_id(item)
                if parsed:
                    result.add(parsed)
            return result

        # Single value
        parsed = self._parse_single_id(value)
        return {parsed} if parsed else set()

    def _parse_single_id(self, value) -> Optional[int]:
        """
        Parse a single ID value to integer.

        Args:
            value: Raw ID value (str, int, or None)

        Returns:
            Integer ID or None
        """
        if value is None:
            return None

        if isinstance(value, int):
            return value if value > 0 else None

        if isinstance(value, str):
            value = value.strip()
            if not value:
                return None
            try:
                parsed = int(value)
                return parsed if parsed > 0 else None
            except ValueError:
                return None

        return None

    def reload_config(self) -> None:
        """
        Reload configuration from ConfigManager.

        Call this if configuration changes at runtime.
        """
        logger.info("🔄 Reloading channel configuration...")
        self._load_config()

    # =========================================================================
    # Monitoring Methods
    # =========================================================================

    def is_monitored_channel(self, channel_id: int) -> bool:
        """
        Check if a channel should be monitored.

        Args:
            channel_id: Discord channel ID

        Returns:
            True if channel is in whitelist, False otherwise
        """
        # If no channels configured, monitor none
        if not self._monitored_channels:
            return False

        return channel_id in self._monitored_channels

    def add_monitored_channel(self, channel_id: int) -> bool:
        """
        Add a channel to the monitored list (runtime only).

        Note: This change is not persisted to configuration.

        Args:
            channel_id: Discord channel ID

        Returns:
            True if added, False if already present
        """
        if channel_id in self._monitored_channels:
            return False

        self._monitored_channels.add(channel_id)
        logger.info(f"➕ Added channel {channel_id} to monitoring")
        return True

    def remove_monitored_channel(self, channel_id: int) -> bool:
        """
        Remove a channel from the monitored list (runtime only).

        Note: This change is not persisted to configuration.

        Args:
            channel_id: Discord channel ID

        Returns:
            True if removed, False if not present
        """
        if channel_id not in self._monitored_channels:
            return False

        self._monitored_channels.discard(channel_id)
        logger.info(f"➖ Removed channel {channel_id} from monitoring")
        return True

    # =========================================================================
    # Alert Channel Methods
    # =========================================================================

    def get_alert_channel(self, severity: str) -> Optional[int]:
        """
        Get the alert channel for a given severity level.

        Severity mapping:
        - medium → alert_channel_monitor (#monitor-queue)
        - high → alert_channel_crisis (#crisis-response)
        - critical → alert_channel_critical (#critical-response)

        Args:
            severity: Crisis severity (medium, high, critical)

        Returns:
            Channel ID or None if not configured
        """
        severity_lower = severity.lower()

        # Map severity to channel
        channel_id = self._alert_channels.get(severity_lower)

        # Critical falls back to high if not configured
        if channel_id is None and severity_lower == "critical":
            channel_id = self._alert_channels.get("high")

        # High falls back to medium if not configured
        if channel_id is None and severity_lower in ("high", "critical"):
            channel_id = self._alert_channels.get("medium")

        return channel_id

    def get_all_alert_channels(self) -> dict:
        """
        Get all configured alert channels.

        Returns:
            Dictionary mapping severity to channel ID
        """
        return {
            severity: channel_id
            for severity, channel_id in self._alert_channels.items()
            if channel_id is not None
        }

    def has_alert_channel(self, severity: str) -> bool:
        """
        Check if an alert channel is configured for severity.

        Args:
            severity: Crisis severity level

        Returns:
            True if channel is configured
        """
        return self.get_alert_channel(severity) is not None

    # =========================================================================
    # Role Methods
    # =========================================================================

    def get_crt_role_id(self) -> Optional[int]:
        """
        Get the Crisis Response Team role ID.

        Returns:
            Role ID or None if not configured
        """
        return self._crt_role_id

    def has_crt_role(self) -> bool:
        """
        Check if CRT role is configured.

        Returns:
            True if role is configured
        """
        return self._crt_role_id is not None

    # =========================================================================
    # Guild Methods
    # =========================================================================

    def get_guild_id(self) -> Optional[int]:
        """
        Get the target guild ID.

        Returns:
            Guild ID or None if monitoring all guilds
        """
        return self._guild_id

    def is_target_guild(self, guild_id: int) -> bool:
        """
        Check if a guild is the target guild.

        Args:
            guild_id: Discord guild ID

        Returns:
            True if guild matches target (or no target configured)
        """
        if self._guild_id is None:
            return True  # No restriction, all guilds allowed
        return guild_id == self._guild_id

    # =========================================================================
    # Properties
    # =========================================================================

    @property
    def monitored_channel_count(self) -> int:
        """Get count of monitored channels."""
        return len(self._monitored_channels)

    @property
    def monitored_channels(self) -> List[int]:
        """Get list of monitored channel IDs."""
        return list(self._monitored_channels)

    @property
    def is_configured(self) -> bool:
        """Check if any channels are configured."""
        return len(self._monitored_channels) > 0

    # =========================================================================
    # Utility Methods
    # =========================================================================

    def get_status(self) -> dict:
        """
        Get channel configuration status.

        Returns:
            Status dictionary for logging/debugging
        """
        return {
            "monitored_channels": len(self._monitored_channels),
            "alert_channels": {
                k: v for k, v in self._alert_channels.items() if v is not None
            },
            "crt_role_configured": self._crt_role_id is not None,
            "guild_restriction": self._guild_id is not None,
        }

    def __repr__(self) -> str:
        """String representation for debugging."""
        return (
            f"ChannelConfigManager("
            f"monitored={len(self._monitored_channels)}, "
            f"alert_channels={len([v for v in self._alert_channels.values() if v])})"
        )


# =============================================================================
# Factory Function
# =============================================================================


def create_channel_config_manager(
    config_manager: "ConfigManager",
) -> ChannelConfigManager:
    """
    Factory function for ChannelConfigManager.

    Creates a configured ChannelConfigManager instance.
    Following Clean Architecture v5.1 Rule #1: Factory Functions.

    Args:
        config_manager: Configuration manager instance

    Returns:
        Configured ChannelConfigManager instance

    Example:
        >>> channel_config = create_channel_config_manager(config_manager)
        >>> if channel_config.is_monitored_channel(123456):
        ...     print("Channel is monitored")
    """
    logger.info("🏭 Creating ChannelConfigManager")
    return ChannelConfigManager(config_manager=config_manager)


# =============================================================================
# Export public interface
# =============================================================================

__all__ = [
    "ChannelConfigManager",
    "create_channel_config_manager",
]
