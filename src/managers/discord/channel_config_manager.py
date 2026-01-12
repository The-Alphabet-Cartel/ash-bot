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
FILE VERSION: v5.0-7-4.0-1
LAST MODIFIED: 2026-01-11
PHASE: Phase 7 - Core Safety & User Preferences
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-bot
Community: The Alphabet Cartel - https://discord.gg/alphabetcartel | https://alphabetcartel.org
============================================================================
RESPONSIBILITIES:
- Load and manage channel whitelist from configuration
- Determine if channels should be monitored
- Route alerts to appropriate channels by severity
- Provide CRT role ID for pinging
- Manage per-channel sensitivity settings (Phase 7)

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
__version__ = "v5.0-7-4.0-1"

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
        _alert_channels: Dict mapping severity to list of channel IDs
        _crt_role_ids: List of Crisis Response Team role IDs
        _guild_id: Target guild ID (optional)
        _channel_sensitivity: Dict mapping channel ID to sensitivity (Phase 7)
        _default_sensitivity: Default sensitivity for channels (Phase 7)

    Example:
        >>> channel_config = create_channel_config_manager(config_manager)
        >>> channel_config.is_monitored_channel(123456789)
        True
        >>> channel_config.get_alert_channels("high")
        [987654321]
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
            "medium": [],
            "high": [],
            "critical": [],
        }
        self._crt_role_ids: List[int] = []
        self._guild_id: Optional[int] = None

        # Phase 7: Channel sensitivity settings (Priority Class System)
        self._channel_sensitivity: dict[int, float] = {}
        self._channel_priority_class: dict[int, str] = {}  # Maps channel_id to class name
        self._default_sensitivity: float = 1.0
        self._sensitivity_ranges: dict[str, tuple[float, float]] = {
            "low": (0.3, 0.6),
            "medium": (0.6, 0.9),
            "high": (1.0, 1.5),
        }

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
        - Alert channel mappings (now supports multiple channels per severity)
        - CRT role IDs (now supports multiple roles)
        - Guild ID
        """
        # Load channels config
        channels_config = self.config_manager.get_section("channels")

        # Load monitored channels (supports JSON string or list)
        monitored_raw = channels_config.get("monitored_channels", [])
        self._monitored_channels = self._parse_channel_ids(monitored_raw)

        # Load alert channels (now arrays)
        self._alert_channels["medium"] = self._parse_ids_to_list(
            channels_config.get("alert_channel_monitor_ids", [])
        )
        self._alert_channels["high"] = self._parse_ids_to_list(
            channels_config.get("alert_channel_crisis_ids", [])
        )
        self._alert_channels["critical"] = self._parse_ids_to_list(
            channels_config.get("alert_channel_critical_ids", [])
        )

        # Load alerting config - CRT role IDs (now array)
        alerting_config = self.config_manager.get_section("alerting")
        self._crt_role_ids = self._parse_ids_to_list(
            alerting_config.get("crt_role_ids", [])
        )

        # Load discord config
        discord_config = self.config_manager.get_section("discord")
        self._guild_id = self._parse_single_id(discord_config.get("guild_id"))

        # Phase 7: Load channel sensitivity configuration (Priority Class System)
        sensitivity_config = self.config_manager.get_section("channel_sensitivity")
        
        # Load default sensitivity for unassigned channels
        self._default_sensitivity = float(
            sensitivity_config.get("default_sensitivity", 1.0)
        )
        if not 0.1 <= self._default_sensitivity <= 2.0:
            logger.warning(
                f"⚠️ Default sensitivity {self._default_sensitivity} out of range [0.1-2.0], "
                f"using 1.0"
            )
            self._default_sensitivity = 1.0

        # Load priority class ranges
        self._sensitivity_ranges = {
            "low": self._parse_range(sensitivity_config.get("range_low", "0.3-0.6")),
            "medium": self._parse_range(sensitivity_config.get("range_medium", "0.6-0.9")),
            "high": self._parse_range(sensitivity_config.get("range_high", "1.0-1.5")),
        }

        # Load and process priority channel assignments
        self._channel_sensitivity = {}
        self._channel_priority_class = {}
        
        priority_configs = [
            ("low", sensitivity_config.get("low_priority_channels", {})),
            ("medium", sensitivity_config.get("medium_priority_channels", {})),
            ("high", sensitivity_config.get("high_priority_channels", {})),
        ]
        
        for priority_class, channels_config in priority_configs:
            self._process_priority_channels(priority_class, channels_config)

        # Log configuration
        logger.debug(f"  Monitored channels: {len(self._monitored_channels)}")
        logger.debug(f"  Alert channels: {self._alert_channels}")
        logger.debug(f"  CRT role IDs: {self._crt_role_ids}")
        logger.debug(f"  Guild ID: {self._guild_id}")
        logger.debug(f"  Default sensitivity: {self._default_sensitivity}")
        logger.debug(f"  Sensitivity ranges: {self._sensitivity_ranges}")
        logger.debug(f"  Channel sensitivity overrides: {len(self._channel_sensitivity)}")
        for channel_id, sensitivity in self._channel_sensitivity.items():
            priority = self._channel_priority_class.get(channel_id, "unknown")
            logger.debug(f"    Channel {channel_id}: {sensitivity:.2f} ({priority})")

    def _parse_range(self, range_str: str) -> tuple[float, float]:
        """
        Parse a range string like "0.3-0.6" into a tuple of floats.

        Args:
            range_str: Range string in format "min-max"

        Returns:
            Tuple of (min, max) floats
        """
        try:
            if isinstance(range_str, str) and "-" in range_str:
                parts = range_str.split("-")
                if len(parts) == 2:
                    min_val = float(parts[0].strip())
                    max_val = float(parts[1].strip())
                    # Validate range values
                    if 0.1 <= min_val <= 2.0 and 0.1 <= max_val <= 2.0:
                        return (min_val, max_val)
            logger.warning(f"⚠️ Invalid range format '{range_str}', using (0.5, 1.0)")
        except (ValueError, AttributeError) as e:
            logger.warning(f"⚠️ Failed to parse range '{range_str}': {e}")
        return (0.5, 1.0)

    def _process_priority_channels(
        self, priority_class: str, channels_config
    ) -> None:
        """
        Process channel assignments for a priority class.

        Args:
            priority_class: Priority class name ("low", "medium", "high")
            channels_config: Dict of channel_id -> weight mappings
        """
        # Parse JSON string if needed
        if isinstance(channels_config, str):
            channels_config = channels_config.strip()
            if not channels_config:
                return
            try:
                channels_config = json.loads(channels_config)
            except json.JSONDecodeError as e:
                logger.warning(
                    f"⚠️ Invalid JSON for {priority_class}_priority_channels: {e}"
                )
                return
        
        if not isinstance(channels_config, dict):
            return

        range_min, range_max = self._sensitivity_ranges.get(
            priority_class, (0.5, 1.0)
        )
        
        for channel_id_str, weight in channels_config.items():
            channel_id = self._parse_single_id(channel_id_str)
            if not channel_id:
                continue
            
            # Check for duplicate assignment
            if channel_id in self._channel_sensitivity:
                existing_class = self._channel_priority_class.get(channel_id, "unknown")
                logger.warning(
                    f"⚠️ Channel {channel_id} assigned to multiple priority classes! "
                    f"Was '{existing_class}', now '{priority_class}'. Using default sensitivity."
                )
                # Remove from tracking, will use default
                del self._channel_sensitivity[channel_id]
                if channel_id in self._channel_priority_class:
                    del self._channel_priority_class[channel_id]
                continue
            
            # Validate and clamp weight to 0.0-1.0
            try:
                weight_val = float(weight)
                weight_val = max(0.0, min(1.0, weight_val))
            except (ValueError, TypeError):
                logger.warning(
                    f"⚠️ Invalid weight '{weight}' for channel {channel_id}, using 0.5"
                )
                weight_val = 0.5
            
            # Calculate final sensitivity: min + (weight × (max - min))
            sensitivity = range_min + (weight_val * (range_max - range_min))
            
            self._channel_sensitivity[channel_id] = sensitivity
            self._channel_priority_class[channel_id] = priority_class
            
            logger.debug(
                f"  📊 Channel {channel_id}: {priority_class.upper()} "
                f"(weight={weight_val:.1f}) → sensitivity={sensitivity:.2f}"
            )

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

    def _parse_ids_to_list(self, value) -> List[int]:
        """
        Parse IDs from various formats into a list.

        Supports:
        - List of integers: [123, 456]
        - List of strings: ["123", "456"]
        - JSON string: '["123", "456"]'
        - Single value: 123 or "123"
        - Empty/None: []

        Args:
            value: Raw ID value(s)

        Returns:
            List of integer IDs
        """
        if value is None:
            return []

        # If it's a string, try to parse as JSON
        if isinstance(value, str):
            value = value.strip()
            if not value:
                return []
            try:
                value = json.loads(value)
            except json.JSONDecodeError:
                # Maybe it's a single ID
                parsed = self._parse_single_id(value)
                return [parsed] if parsed else []

        # If it's a list, parse each element
        if isinstance(value, (list, tuple)):
            result = []
            for item in value:
                parsed = self._parse_single_id(item)
                if parsed:
                    result.append(parsed)
            return result

        # Single value
        parsed = self._parse_single_id(value)
        return [parsed] if parsed else []

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
        Get the first alert channel for a given severity level.

        This is a backward-compatible method that returns a single channel.
        Use get_alert_channels() to get all configured channels.

        Severity mapping:
        - medium → alert_channel_monitor (#monitor-queue)
        - high → alert_channel_crisis (#crisis-response)
        - critical → alert_channel_critical (#critical-response)

        Args:
            severity: Crisis severity (medium, high, critical)

        Returns:
            First channel ID or None if not configured
        """
        channels = self.get_alert_channels(severity)
        return channels[0] if channels else None

    def get_alert_channels(self, severity: str) -> List[int]:
        """
        Get all alert channels for a given severity level.

        Severity mapping:
        - medium → alert_channel_monitor_ids (#monitor-queue)
        - high → alert_channel_crisis_ids (#crisis-response)
        - critical → alert_channel_critical_ids (#critical-response)

        Args:
            severity: Crisis severity (medium, high, critical)

        Returns:
            List of channel IDs (may be empty)
        """
        severity_lower = severity.lower()

        # Map severity to channels
        channels = self._alert_channels.get(severity_lower, [])

        # Critical falls back to high if not configured
        if not channels and severity_lower == "critical":
            channels = self._alert_channels.get("high", [])

        # High falls back to medium if not configured
        if not channels and severity_lower in ("high", "critical"):
            channels = self._alert_channels.get("medium", [])

        return channels

    def get_all_alert_channels(self) -> dict:
        """
        Get all configured alert channels.

        Returns:
            Dictionary mapping severity to list of channel IDs
        """
        return {
            severity: channels
            for severity, channels in self._alert_channels.items()
            if channels
        }

    def has_alert_channel(self, severity: str) -> bool:
        """
        Check if any alert channel is configured for severity.

        Args:
            severity: Crisis severity level

        Returns:
            True if at least one channel is configured
        """
        return len(self.get_alert_channels(severity)) > 0

    # =========================================================================
    # Role Methods
    # =========================================================================

    def get_crt_role_id(self) -> Optional[int]:
        """
        Get the first Crisis Response Team role ID.

        This is a backward-compatible method that returns a single role.
        Use get_crt_role_ids() to get all configured roles.

        Returns:
            First role ID or None if not configured
        """
        return self._crt_role_ids[0] if self._crt_role_ids else None

    def get_crt_role_ids(self) -> List[int]:
        """
        Get all Crisis Response Team role IDs.

        Returns:
            List of role IDs (may be empty)
        """
        return self._crt_role_ids.copy()

    def has_crt_role(self) -> bool:
        """
        Check if any CRT role is configured.

        Returns:
            True if at least one role is configured
        """
        return len(self._crt_role_ids) > 0

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
    # Phase 7: Channel Sensitivity Methods (Priority Class System)
    # =========================================================================

    def get_channel_sensitivity(self, channel_id: int) -> float:
        """
        Get the sensitivity modifier for a channel.

        Channels are assigned to priority classes (LOW, MEDIUM, HIGH) with
        a weight that determines their position within that class's range.

        Formula: sensitivity = range_min + (weight × (range_max - range_min))

        Returns default_sensitivity for unassigned channels.

        Args:
            channel_id: Discord channel ID

        Returns:
            Calculated sensitivity value (typically 0.1-2.0)
        """
        return self._channel_sensitivity.get(channel_id, self._default_sensitivity)

    def get_channel_priority_class(self, channel_id: int) -> Optional[str]:
        """
        Get the priority class for a channel.

        Args:
            channel_id: Discord channel ID

        Returns:
            Priority class name ("low", "medium", "high") or None if unassigned
        """
        return self._channel_priority_class.get(channel_id)

    def get_channel_sensitivity_info(self, channel_id: int) -> dict:
        """
        Get detailed sensitivity information for a channel.

        Args:
            channel_id: Discord channel ID

        Returns:
            Dict with sensitivity, priority_class, and is_default
        """
        sensitivity = self._channel_sensitivity.get(channel_id)
        priority_class = self._channel_priority_class.get(channel_id)
        
        if sensitivity is None:
            return {
                "sensitivity": self._default_sensitivity,
                "priority_class": None,
                "is_default": True,
            }
        
        return {
            "sensitivity": sensitivity,
            "priority_class": priority_class,
            "is_default": False,
        }

    def set_channel_sensitivity(
        self,
        channel_id: int,
        sensitivity: float,
        priority_class: Optional[str] = None,
    ) -> bool:
        """
        Set the sensitivity modifier for a channel (runtime only).

        Note: This change is not persisted to configuration.
        For persistent changes, update .env file.

        Args:
            channel_id: Discord channel ID
            sensitivity: Sensitivity modifier (0.1-2.0)
            priority_class: Optional priority class label for tracking

        Returns:
            True if set successfully, False if out of range
        """
        if not 0.1 <= sensitivity <= 2.0:
            logger.warning(
                f"⚠️ Cannot set sensitivity {sensitivity} for channel {channel_id}: "
                f"out of range [0.1-2.0]"
            )
            return False

        old_sensitivity = self._channel_sensitivity.get(channel_id, self._default_sensitivity)
        self._channel_sensitivity[channel_id] = sensitivity
        
        if priority_class:
            self._channel_priority_class[channel_id] = priority_class

        logger.info(
            f"📊 Channel {channel_id} sensitivity updated: {old_sensitivity:.2f} → {sensitivity:.2f}"
            + (f" ({priority_class})" if priority_class else "")
        )
        return True

    def remove_channel_sensitivity(self, channel_id: int) -> bool:
        """
        Remove custom sensitivity for a channel (revert to default).

        Args:
            channel_id: Discord channel ID

        Returns:
            True if removed, False if no custom sensitivity was set
        """
        if channel_id not in self._channel_sensitivity:
            return False

        old_sensitivity = self._channel_sensitivity.pop(channel_id)
        old_class = self._channel_priority_class.pop(channel_id, None)
        
        logger.info(
            f"📊 Channel {channel_id} sensitivity removed: {old_sensitivity:.2f}"
            + (f" ({old_class})" if old_class else "")
            + f" → {self._default_sensitivity} (default)"
        )
        return True

    def get_all_channel_sensitivities(self) -> dict[int, float]:
        """
        Get all custom channel sensitivities.

        Returns:
            Dictionary mapping channel ID to calculated sensitivity
        """
        return dict(self._channel_sensitivity)

    def get_sensitivity_ranges(self) -> dict[str, tuple[float, float]]:
        """
        Get the configured sensitivity ranges for each priority class.

        Returns:
            Dict mapping class name to (min, max) tuple
        """
        return dict(self._sensitivity_ranges)

    def get_channels_by_priority_class(self, priority_class: str) -> dict[int, float]:
        """
        Get all channels assigned to a specific priority class.

        Args:
            priority_class: Priority class name ("low", "medium", "high")

        Returns:
            Dict mapping channel ID to sensitivity for that class
        """
        return {
            channel_id: sensitivity
            for channel_id, sensitivity in self._channel_sensitivity.items()
            if self._channel_priority_class.get(channel_id) == priority_class
        }

    @property
    def default_sensitivity(self) -> float:
        """Get the default channel sensitivity."""
        return self._default_sensitivity

    @property
    def sensitivity_override_count(self) -> int:
        """Get count of channels with custom sensitivity."""
        return len(self._channel_sensitivity)

    # =========================================================================
    # Utility Methods
    # =========================================================================

    def get_status(self) -> dict:
        """
        Get channel configuration status.

        Returns:
            Status dictionary for logging/debugging
        """
        # Count channels by priority class
        channels_by_class = {
            "low": len(self.get_channels_by_priority_class("low")),
            "medium": len(self.get_channels_by_priority_class("medium")),
            "high": len(self.get_channels_by_priority_class("high")),
        }
        
        return {
            "monitored_channels": len(self._monitored_channels),
            "alert_channels": {
                k: v for k, v in self._alert_channels.items() if v
            },
            "crt_roles_configured": len(self._crt_role_ids),
            "guild_restriction": self._guild_id is not None,
            # Phase 7: Sensitivity status (Priority Class System)
            "sensitivity": {
                "default": self._default_sensitivity,
                "ranges": self._sensitivity_ranges,
                "channels_configured": len(self._channel_sensitivity),
                "by_priority_class": channels_by_class,
            },
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
