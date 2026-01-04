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
Alert Dispatcher for Ash-Bot Service
---
FILE VERSION: v5.0-3-5.0-1
LAST MODIFIED: 2026-01-04
PHASE: Phase 3 - Alert Dispatching
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-bot
Community: The Alphabet Cartel - https://discord.gg/alphabetcartel | https://alphabetcartel.org
============================================================================
RESPONSIBILITIES:
- Determine if alert should be sent (severity + cooldown)
- Route alerts to appropriate channels by severity
- Build and send embeds with interactive buttons
- Ping CRT role for HIGH/CRITICAL alerts
- Track cooldowns to prevent spam

USAGE:
    from src.managers.alerting import create_alert_dispatcher

    dispatcher = create_alert_dispatcher(
        config_manager=config_manager,
        channel_config=channel_config,
        embed_builder=embed_builder,
        cooldown_manager=cooldown_manager,
        bot=bot,
    )

    alert_message = await dispatcher.dispatch_alert(message, result)
"""

import discord
from discord.ext import commands
from typing import Optional, Set, TYPE_CHECKING
import logging

if TYPE_CHECKING:
    from src.managers.config_manager import ConfigManager
    from src.managers.discord.channel_config_manager import ChannelConfigManager
    from src.managers.alerting.embed_builder import EmbedBuilder
    from src.managers.alerting.cooldown_manager import CooldownManager
    from src.models.nlp_models import CrisisAnalysisResult

from src.views.alert_buttons import AlertButtonView

# Module version
__version__ = "v5.0-3-5.0-1"

# Initialize logger
logger = logging.getLogger(__name__)


# =============================================================================
# Constants
# =============================================================================

# Severities that trigger alerts
ALERTABLE_SEVERITIES: Set[str] = {"medium", "high", "critical"}

# Severities that ping CRT role
PING_SEVERITIES: Set[str] = {"high", "critical"}


# =============================================================================
# Alert Dispatcher
# =============================================================================


class AlertDispatcher:
    """
    Dispatches crisis alerts to appropriate Discord channels.

    Handles the complete alert flow:
    1. Check if severity qualifies for alerting
    2. Check cooldown to prevent spam
    3. Build embed with crisis details
    4. Route to correct channel based on severity
    5. Add interactive buttons
    6. Ping CRT role if needed
    7. Set cooldown for user

    Attributes:
        config_manager: ConfigManager for settings
        channel_config: ChannelConfigManager for routing
        embed_builder: EmbedBuilder for embed creation
        cooldown_manager: CooldownManager for rate limiting
        bot: Discord bot instance for sending

    Example:
        >>> dispatcher = create_alert_dispatcher(...)
        >>> alert_msg = await dispatcher.dispatch_alert(message, result)
        >>> if alert_msg:
        ...     print(f"Alert sent: {alert_msg.id}")
    """

    def __init__(
        self,
        config_manager: "ConfigManager",
        channel_config: "ChannelConfigManager",
        embed_builder: "EmbedBuilder",
        cooldown_manager: "CooldownManager",
        bot: commands.Bot,
    ):
        """
        Initialize AlertDispatcher.

        Args:
            config_manager: Configuration manager
            channel_config: Channel routing configuration
            embed_builder: Embed builder instance
            cooldown_manager: Cooldown tracking instance
            bot: Discord bot instance

        Note:
            Use create_alert_dispatcher() factory function.
        """
        self._config = config_manager
        self._channel_config = channel_config
        self._embed_builder = embed_builder
        self._cooldown = cooldown_manager
        self._bot = bot

        # Load configuration
        self._enabled = self._config.get("alerting", "enabled", True)
        self._min_severity = self._config.get(
            "alerting", "min_severity_to_alert", "medium"
        )
        self._crt_role_id = self._channel_config.get_crt_role_id()

        # Statistics
        self._alerts_sent = 0
        self._alerts_skipped_cooldown = 0
        self._alerts_skipped_severity = 0

        logger.info(
            f"✅ AlertDispatcher initialized "
            f"(enabled={self._enabled}, min_severity={self._min_severity})"
        )

    # =========================================================================
    # Alert Qualification
    # =========================================================================

    def _should_alert(self, severity: str) -> bool:
        """
        Check if severity qualifies for alerting.

        Args:
            severity: Crisis severity level

        Returns:
            True if alert should be sent
        """
        if not self._enabled:
            return False

        return severity.lower() in ALERTABLE_SEVERITIES

    def _should_ping_crt(self, severity: str) -> bool:
        """
        Check if CRT should be pinged.

        Args:
            severity: Crisis severity level

        Returns:
            True if CRT should be pinged
        """
        if not self._crt_role_id:
            return False

        return severity.lower() in PING_SEVERITIES

    def _get_alert_channel(
        self,
        severity: str,
    ) -> Optional[discord.TextChannel]:
        """
        Get the alert channel for a severity level.

        Args:
            severity: Crisis severity level

        Returns:
            Discord TextChannel or None if not configured
        """
        channel_id = self._channel_config.get_alert_channel(severity)
        if channel_id is None:
            return None

        channel = self._bot.get_channel(channel_id)
        if channel is None:
            logger.warning(
                f"⚠️ Alert channel {channel_id} not found for severity {severity}"
            )
            return None

        if not isinstance(channel, discord.TextChannel):
            logger.warning(
                f"⚠️ Alert channel {channel_id} is not a text channel"
            )
            return None

        return channel

    # =========================================================================
    # Main Dispatch Method
    # =========================================================================

    async def dispatch_alert(
        self,
        message: discord.Message,
        result: "CrisisAnalysisResult",
        force: bool = False,
    ) -> Optional[discord.Message]:
        """
        Dispatch a crisis alert if appropriate.

        Args:
            message: Original Discord message
            result: NLP analysis result
            force: If True, bypass cooldown check

        Returns:
            Sent alert message, or None if not sent
        """
        severity = result.severity.lower()

        # Check if alerting is appropriate
        if not self._should_alert(severity):
            self._alerts_skipped_severity += 1
            logger.debug(
                f"Skipping alert: severity {severity} below threshold"
            )
            return None

        # Check cooldown (unless forced)
        if not force and self._cooldown.is_on_cooldown(message.author.id):
            self._alerts_skipped_cooldown += 1
            remaining = self._cooldown.get_remaining_cooldown(message.author.id)
            logger.debug(
                f"Skipping alert: user {message.author.id} on cooldown "
                f"({remaining}s remaining)"
            )
            return None

        # Get target channel
        channel = self._get_alert_channel(severity)
        if channel is None:
            logger.warning(
                f"⚠️ No alert channel configured for severity {severity}"
            )
            return None

        # Build embed
        embed = self._embed_builder.build_crisis_embed(
            message=message,
            result=result,
        )

        # Build button view
        view = AlertButtonView(
            user_id=message.author.id,
            message_id=message.id,
            severity=severity,
        )

        # Build content (CRT ping if needed)
        content = None
        if self._should_ping_crt(severity):
            content = f"<@&{self._crt_role_id}>"
            logger.debug(f"Will ping CRT role {self._crt_role_id}")

        # Send alert
        try:
            alert_message = await channel.send(
                content=content,
                embed=embed,
                view=view,
            )

            # Set cooldown
            self._cooldown.set_cooldown(message.author.id)

            # Update statistics
            self._alerts_sent += 1

            # Log success
            logger.info(
                f"🚨 Alert dispatched for user {message.author.id} "
                f"(severity: {severity}, channel: #{channel.name}, "
                f"ping_crt: {content is not None})"
            )

            return alert_message

        except discord.Forbidden:
            logger.error(
                f"❌ No permission to send to channel #{channel.name} "
                f"(ID: {channel.id})"
            )
            return None

        except discord.HTTPException as e:
            logger.error(f"❌ Failed to send alert: {e}")
            return None

    # =========================================================================
    # Escalation Alert
    # =========================================================================

    async def dispatch_escalation_alert(
        self,
        message: discord.Message,
        result: "CrisisAnalysisResult",
        history_count: int,
        trend: str,
    ) -> Optional[discord.Message]:
        """
        Dispatch an escalation alert (when pattern detected).

        Uses the escalation embed variant which highlights the pattern.

        Args:
            message: Original Discord message
            result: NLP analysis result
            history_count: Number of messages in history
            trend: Trend direction (escalating, stable, etc.)

        Returns:
            Sent alert message, or None if not sent
        """
        severity = result.severity.lower()

        # Check if alerting is appropriate
        if not self._should_alert(severity):
            return None

        # Escalation alerts bypass cooldown (they're more important)

        # Get target channel (use one level higher for escalations)
        channel = self._get_alert_channel(severity)
        if channel is None:
            return None

        # Build escalation embed
        embed = self._embed_builder.build_escalation_embed(
            message=message,
            result=result,
            history_count=history_count,
            trend=trend,
        )

        # Build button view
        view = AlertButtonView(
            user_id=message.author.id,
            message_id=message.id,
            severity=severity,
        )

        # Always ping CRT for escalations
        content = None
        if self._crt_role_id:
            content = f"📈 **ESCALATION** <@&{self._crt_role_id}>"

        # Send alert
        try:
            alert_message = await channel.send(
                content=content,
                embed=embed,
                view=view,
            )

            # Set cooldown
            self._cooldown.set_cooldown(message.author.id)

            # Update statistics
            self._alerts_sent += 1

            logger.warning(
                f"📈 Escalation alert dispatched for user {message.author.id} "
                f"(severity: {severity}, trend: {trend}, "
                f"history: {history_count} messages)"
            )

            return alert_message

        except discord.Forbidden:
            logger.error(f"❌ No permission to send escalation alert")
            return None

        except discord.HTTPException as e:
            logger.error(f"❌ Failed to send escalation alert: {e}")
            return None

    # =========================================================================
    # Properties
    # =========================================================================

    @property
    def is_enabled(self) -> bool:
        """Check if alerting is enabled."""
        return self._enabled

    @property
    def alerts_sent(self) -> int:
        """Get count of alerts sent."""
        return self._alerts_sent

    @property
    def alerts_skipped(self) -> int:
        """Get total count of skipped alerts."""
        return self._alerts_skipped_cooldown + self._alerts_skipped_severity

    # =========================================================================
    # Status Methods
    # =========================================================================

    def get_status(self) -> dict:
        """
        Get alert dispatcher status.

        Returns:
            Status dictionary for logging/debugging
        """
        return {
            "enabled": self._enabled,
            "min_severity": self._min_severity,
            "crt_role_configured": self._crt_role_id is not None,
            "alerts_sent": self._alerts_sent,
            "alerts_skipped_cooldown": self._alerts_skipped_cooldown,
            "alerts_skipped_severity": self._alerts_skipped_severity,
            "alert_channels": self._channel_config.get_all_alert_channels(),
        }

    def __repr__(self) -> str:
        """String representation for debugging."""
        return (
            f"AlertDispatcher("
            f"enabled={self._enabled}, "
            f"alerts_sent={self._alerts_sent})"
        )


# =============================================================================
# Factory Function
# =============================================================================


def create_alert_dispatcher(
    config_manager: "ConfigManager",
    channel_config: "ChannelConfigManager",
    embed_builder: "EmbedBuilder",
    cooldown_manager: "CooldownManager",
    bot: commands.Bot,
) -> AlertDispatcher:
    """
    Factory function for AlertDispatcher.

    Creates a configured AlertDispatcher instance with all dependencies.
    Following Clean Architecture v5.1 Rule #1: Factory Functions.

    Args:
        config_manager: Configuration manager instance
        channel_config: Channel routing configuration
        embed_builder: Embed builder instance
        cooldown_manager: Cooldown tracking instance
        bot: Discord bot instance

    Returns:
        Configured AlertDispatcher instance

    Example:
        >>> dispatcher = create_alert_dispatcher(
        ...     config_manager=config,
        ...     channel_config=channel_config,
        ...     embed_builder=embed_builder,
        ...     cooldown_manager=cooldown,
        ...     bot=bot,
        ... )
        >>> await dispatcher.dispatch_alert(message, result)
    """
    logger.info("🏭 Creating AlertDispatcher")

    return AlertDispatcher(
        config_manager=config_manager,
        channel_config=channel_config,
        embed_builder=embed_builder,
        cooldown_manager=cooldown_manager,
        bot=bot,
    )


# =============================================================================
# Export public interface
# =============================================================================

__all__ = [
    "AlertDispatcher",
    "create_alert_dispatcher",
    "ALERTABLE_SEVERITIES",
    "PING_SEVERITIES",
]
