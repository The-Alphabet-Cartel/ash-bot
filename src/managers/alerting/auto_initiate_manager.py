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
Auto-Initiate Manager for Ash-Bot Service
---
Manages automatic Ash outreach when CRT staff doesn't respond to alerts
within a configurable timeout. Ensures no community member in crisis
is left without support during off-hours or when staff is unavailable.
----------------------------------------------------------------------------
FILE VERSION: v5.0-8-1.0-1
LAST MODIFIED: 2026-01-05
PHASE: Phase 8 - Metrics & Reporting
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-bot
============================================================================
"""

import asyncio
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from typing import Dict, Optional, Set, TYPE_CHECKING

import discord

if TYPE_CHECKING:
    from discord.ext import commands
    from src.managers.config_manager import ConfigManager
    from src.managers.storage.redis_manager import RedisManager
    from src.managers.ash.ash_session_manager import AshSessionManager
    from src.managers.ash.ash_personality_manager import AshPersonalityManager
    from src.managers.metrics.response_metrics_manager import ResponseMetricsManager

# Module version
__version__ = "v5.0-8-1.0-1"

# Initialize logger
logger = logging.getLogger(__name__)


# =============================================================================
# Constants
# =============================================================================

# Redis key prefix for pending alerts
REDIS_KEY_PREFIX = "ash:pending_alert:"

# Severities eligible for auto-initiate (configurable minimum)
SEVERITY_ORDER = ["low", "medium", "high", "critical"]

# Background check interval (seconds)
CHECK_INTERVAL_SECONDS = 30


# =============================================================================
# Data Classes
# =============================================================================


@dataclass
class PendingAlert:
    """
    Represents a pending alert awaiting CRT response.

    Tracks all information needed to auto-initiate Ash contact
    if the alert times out without acknowledgment.

    Attributes:
        alert_message_id: ID of the alert message in crisis channel
        alert_channel_id: ID of the channel containing the alert
        user_id: Discord ID of the user in crisis
        original_message_id: ID of the original crisis message
        original_channel_id: ID of the channel with original message
        severity: Crisis severity level
        created_at: When the alert was created (UTC)
        expires_at: When auto-initiate should trigger (UTC)
        auto_initiated: Whether auto-initiate has fired
        cancelled: Whether alert was acknowledged/cancelled
    """

    alert_message_id: int
    alert_channel_id: int
    user_id: int
    original_message_id: int
    original_channel_id: int
    severity: str
    created_at: datetime
    expires_at: datetime
    auto_initiated: bool = False
    cancelled: bool = False

    def is_expired(self) -> bool:
        """Check if the alert has expired (ready for auto-initiate)."""
        if self.cancelled or self.auto_initiated:
            return False
        return datetime.now(timezone.utc) >= self.expires_at

    def seconds_until_expiry(self) -> float:
        """Get seconds until expiration (negative if expired)."""
        delta = self.expires_at - datetime.now(timezone.utc)
        return delta.total_seconds()

    def to_dict(self) -> dict:
        """Convert to dictionary for Redis storage."""
        return {
            "alert_message_id": self.alert_message_id,
            "alert_channel_id": self.alert_channel_id,
            "user_id": self.user_id,
            "original_message_id": self.original_message_id,
            "original_channel_id": self.original_channel_id,
            "severity": self.severity,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat(),
            "auto_initiated": self.auto_initiated,
            "cancelled": self.cancelled,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "PendingAlert":
        """Create PendingAlert from dictionary (Redis retrieval)."""
        return cls(
            alert_message_id=int(data["alert_message_id"]),
            alert_channel_id=int(data["alert_channel_id"]),
            user_id=int(data["user_id"]),
            original_message_id=int(data["original_message_id"]),
            original_channel_id=int(data["original_channel_id"]),
            severity=data["severity"],
            created_at=datetime.fromisoformat(data["created_at"]),
            expires_at=datetime.fromisoformat(data["expires_at"]),
            auto_initiated=data.get("auto_initiated", False),
            cancelled=data.get("cancelled", False),
        )

    def __repr__(self) -> str:
        """String representation for debugging."""
        status = "cancelled" if self.cancelled else (
            "auto_initiated" if self.auto_initiated else "pending"
        )
        return (
            f"PendingAlert(alert={self.alert_message_id}, "
            f"user={self.user_id}, severity={self.severity}, "
            f"status={status}, expires_in={self.seconds_until_expiry():.0f}s)"
        )


# =============================================================================
# Auto-Initiate Manager
# =============================================================================


class AutoInitiateManager:
    """
    Manages automatic Ash initiation for unacknowledged alerts.

    When a crisis alert is dispatched, this manager tracks it. If no
    CRT member acknowledges or clicks "Talk to Ash" within the configured
    timeout, Ash automatically reaches out to the user.

    This ensures no community member in crisis is left without support,
    even during off-hours when staff may be unavailable.

    Attributes:
        config_manager: ConfigManager for settings
        redis_manager: RedisManager for persistent storage
        ash_session_manager: AshSessionManager for creating sessions
        ash_personality_manager: AshPersonalityManager for messages
        bot: Discord bot instance

    Example:
        >>> auto_initiate = create_auto_initiate_manager(...)
        >>> await auto_initiate.start()
        >>> await auto_initiate.track_alert(alert_msg, user, "high", orig_msg)
        >>> # Later, if no response...
        >>> # Auto-initiate fires automatically
    """

    def __init__(
        self,
        config_manager: "ConfigManager",
        redis_manager: Optional["RedisManager"],
        bot: "commands.Bot",
    ):
        """
        Initialize AutoInitiateManager.

        Args:
            config_manager: Configuration manager for settings
            redis_manager: Redis manager for persistent storage (optional)
            bot: Discord bot instance

        Note:
            Use create_auto_initiate_manager() factory function.
            AshSessionManager and AshPersonalityManager are injected later
            via set_ash_managers() to avoid circular dependencies.
        """
        self._config = config_manager
        self._redis = redis_manager
        self._bot = bot

        # Ash managers (set later to avoid circular deps)
        self._ash_sessions: Optional["AshSessionManager"] = None
        self._ash_personality: Optional["AshPersonalityManager"] = None

        # Response metrics manager (Phase 8)
        self._response_metrics: Optional["ResponseMetricsManager"] = None

        # In-memory tracking (primary)
        self._pending_alerts: Dict[int, PendingAlert] = {}

        # Background task
        self._check_task: Optional[asyncio.Task] = None
        self._running = False

        # Load configuration
        self._enabled = self._config.get("auto_initiate", "enabled", True)
        self._delay_minutes = self._config.get(
            "auto_initiate", "delay_minutes", 3
        )
        self._min_severity = self._config.get(
            "auto_initiate", "min_severity", "medium"
        ).lower()

        # Statistics
        self._total_tracked = 0
        self._total_cancelled = 0
        self._total_auto_initiated = 0
        self._total_failed = 0

        logger.info(
            f"✅ AutoInitiateManager initialized "
            f"(enabled={self._enabled}, delay={self._delay_minutes}min, "
            f"min_severity={self._min_severity})"
        )

    # =========================================================================
    # Ash Manager Injection
    # =========================================================================

    def set_ash_managers(
        self,
        ash_session_manager: "AshSessionManager",
        ash_personality_manager: "AshPersonalityManager",
    ) -> None:
        """
        Inject Ash managers after initialization.

        This is called from main.py after all managers are created
        to avoid circular dependency issues.

        Args:
            ash_session_manager: Session manager for creating Ash sessions
            ash_personality_manager: Personality manager for welcome messages
        """
        self._ash_sessions = ash_session_manager
        self._ash_personality = ash_personality_manager
        logger.debug("Ash managers injected into AutoInitiateManager")

    def set_response_metrics_manager(
        self,
        response_metrics_manager: "ResponseMetricsManager",
    ) -> None:
        """
        Inject response metrics manager after initialization (Phase 8).

        Args:
            response_metrics_manager: ResponseMetricsManager for tracking
        """
        self._response_metrics = response_metrics_manager
        logger.debug("ResponseMetricsManager injected into AutoInitiateManager")

    # =========================================================================
    # Lifecycle Methods
    # =========================================================================

    async def start(self) -> None:
        """
        Start the auto-initiate background task.

        Loads any pending alerts from Redis and starts the check loop.
        """
        if not self._enabled:
            logger.info("⏸️ AutoInitiateManager disabled by configuration")
            return

        if self._running:
            logger.warning("AutoInitiateManager already running")
            return

        # Load pending alerts from Redis (if available)
        await self._load_from_redis()

        # Start background check loop
        self._running = True
        self._check_task = asyncio.create_task(self._check_loop())

        logger.info(
            f"🚀 AutoInitiateManager started "
            f"(pending_alerts={len(self._pending_alerts)})"
        )

    async def stop(self) -> None:
        """
        Stop the auto-initiate background task.

        Saves pending alerts to Redis and cancels the check loop.
        """
        if not self._running:
            return

        self._running = False

        # Cancel background task
        if self._check_task:
            self._check_task.cancel()
            try:
                await self._check_task
            except asyncio.CancelledError:
                pass
            self._check_task = None

        # Save pending alerts to Redis
        await self._save_to_redis()

        logger.info("🛑 AutoInitiateManager stopped")

    # =========================================================================
    # Alert Tracking
    # =========================================================================

    def _meets_severity_threshold(self, severity: str) -> bool:
        """
        Check if severity meets minimum threshold for auto-initiate.

        Args:
            severity: Crisis severity level

        Returns:
            True if severity is at or above minimum threshold
        """
        severity_lower = severity.lower()
        min_index = SEVERITY_ORDER.index(self._min_severity) if self._min_severity in SEVERITY_ORDER else 1
        severity_index = SEVERITY_ORDER.index(severity_lower) if severity_lower in SEVERITY_ORDER else 0
        return severity_index >= min_index

    async def track_alert(
        self,
        alert_message: discord.Message,
        user_id: int,
        severity: str,
        original_message: discord.Message,
    ) -> bool:
        """
        Start tracking an alert for auto-initiation.

        Adds the alert to pending tracking with an expiration time.
        If no acknowledgment occurs before expiry, Ash will auto-initiate.

        Args:
            alert_message: The alert message sent to crisis channel
            user_id: Discord ID of the user in crisis
            severity: Crisis severity level
            original_message: The original message that triggered the alert

        Returns:
            True if alert is being tracked, False if not eligible
        """
        if not self._enabled:
            return False

        # Check severity threshold
        if not self._meets_severity_threshold(severity):
            logger.debug(
                f"Alert {alert_message.id} below severity threshold "
                f"({severity} < {self._min_severity})"
            )
            return False

        # Calculate expiration time
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(minutes=self._delay_minutes)

        # Create pending alert
        pending = PendingAlert(
            alert_message_id=alert_message.id,
            alert_channel_id=alert_message.channel.id,
            user_id=user_id,
            original_message_id=original_message.id,
            original_channel_id=original_message.channel.id,
            severity=severity.lower(),
            created_at=now,
            expires_at=expires_at,
        )

        # Store in memory
        self._pending_alerts[alert_message.id] = pending
        self._total_tracked += 1

        # Persist to Redis
        await self._save_alert_to_redis(pending)

        logger.info(
            f"⏱️ Tracking alert {alert_message.id} for user {user_id} "
            f"(severity: {severity}, auto-initiate in {self._delay_minutes}min)"
        )

        return True

    async def cancel_alert(
        self,
        alert_message_id: int,
        reason: str = "acknowledged",
    ) -> bool:
        """
        Cancel tracking for an alert (when acknowledged).

        Called when CRT clicks "Acknowledge" or "Talk to Ash" button.

        Args:
            alert_message_id: ID of the alert message
            reason: Reason for cancellation (for logging)

        Returns:
            True if alert was cancelled, False if not found
        """
        pending = self._pending_alerts.get(alert_message_id)

        if not pending:
            # Check if it's in Redis but not loaded
            pending = await self._load_alert_from_redis(alert_message_id)

        if not pending:
            logger.debug(f"Alert {alert_message_id} not found for cancellation")
            return False

        if pending.cancelled or pending.auto_initiated:
            logger.debug(f"Alert {alert_message_id} already handled")
            return False

        # Mark as cancelled
        pending.cancelled = True
        self._total_cancelled += 1

        # Update Redis
        await self._save_alert_to_redis(pending)

        # Remove from memory
        self._pending_alerts.pop(alert_message_id, None)

        logger.info(
            f"✅ Alert {alert_message_id} cancelled (reason: {reason})"
        )

        return True

    # =========================================================================
    # Background Check Loop
    # =========================================================================

    async def _check_loop(self) -> None:
        """
        Background loop checking for expired alerts.

        Runs every CHECK_INTERVAL_SECONDS and processes any alerts
        that have expired without acknowledgment.
        """
        logger.debug("AutoInitiate check loop started")

        while self._running:
            try:
                await self._process_expired_alerts()
                await asyncio.sleep(CHECK_INTERVAL_SECONDS)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in auto-initiate check loop: {e}")
                await asyncio.sleep(CHECK_INTERVAL_SECONDS)

        logger.debug("AutoInitiate check loop stopped")

    async def _process_expired_alerts(self) -> None:
        """Process all expired pending alerts."""
        expired: list[PendingAlert] = []

        # Find expired alerts
        for pending in list(self._pending_alerts.values()):
            if pending.is_expired():
                expired.append(pending)

        # Process each expired alert
        for pending in expired:
            await self._auto_initiate(pending)

    # =========================================================================
    # Auto-Initiation
    # =========================================================================

    async def _auto_initiate(self, pending: PendingAlert) -> None:
        """
        Execute auto-initiation for an expired alert.

        Creates an Ash session with the user and updates the alert embed.

        Args:
            pending: The pending alert to auto-initiate
        """
        logger.info(
            f"⏰ Auto-initiating for user {pending.user_id} "
            f"(alert: {pending.alert_message_id})"
        )

        # Mark as auto-initiated (prevent double-processing)
        pending.auto_initiated = True
        await self._save_alert_to_redis(pending)

        # Check if Ash managers are available
        if not self._ash_sessions or not self._ash_personality:
            logger.warning(
                "⚠️ Ash managers not available for auto-initiate. "
                "User will not receive automated outreach."
            )
            self._total_failed += 1
            return

        # Check if user already has an active session
        if self._ash_sessions.has_active_session(pending.user_id):
            logger.info(
                f"User {pending.user_id} already has active Ash session, "
                "skipping auto-initiate"
            )
            self._pending_alerts.pop(pending.alert_message_id, None)
            return

        try:
            # Fetch the user
            user = await self._bot.fetch_user(pending.user_id)

            # Start Ash session
            from src.managers.ash import SessionExistsError

            try:
                session = await self._ash_sessions.start_session(
                    user=user,
                    trigger_severity=pending.severity,
                )
            except SessionExistsError:
                logger.info(f"Session already exists for user {pending.user_id}")
                self._pending_alerts.pop(pending.alert_message_id, None)
                return

            # Get welcome message with auto-initiate context
            welcome_msg = self._ash_personality.get_welcome_message(
                severity=pending.severity,
                username=user.display_name,
            )

            # Send welcome message
            await session.dm_channel.send(welcome_msg)
            session.add_assistant_message(welcome_msg)

            # Phase 8: Record auto-initiation metrics
            await self._record_auto_initiate_metrics(pending)

            # Update the alert embed
            await self._update_alert_embed(pending)

            self._total_auto_initiated += 1

            logger.info(
                f"✅ Auto-initiated Ash session {session.session_id} "
                f"for user {pending.user_id}"
            )

        except discord.NotFound:
            logger.warning(
                f"User {pending.user_id} not found for auto-initiate"
            )
            self._total_failed += 1

        except discord.Forbidden:
            logger.warning(
                f"Cannot DM user {pending.user_id} for auto-initiate"
            )
            self._total_failed += 1

        except Exception as e:
            logger.error(
                f"❌ Auto-initiate failed for user {pending.user_id}: {e}"
            )
            self._total_failed += 1

        finally:
            # Remove from pending (whether success or failure)
            self._pending_alerts.pop(pending.alert_message_id, None)
            await self._delete_alert_from_redis(pending.alert_message_id)

    async def _record_auto_initiate_metrics(
        self,
        pending: PendingAlert,
    ) -> None:
        """
        Record auto-initiation metrics (Phase 8).

        Args:
            pending: The pending alert that was auto-initiated
        """
        try:
            if not self._response_metrics or not self._response_metrics.is_enabled:
                return

            await self._response_metrics.record_ash_contacted_by_message_id(
                alert_message_id=pending.alert_message_id,
                initiated_by="auto",
                was_auto_initiated=True,
            )

            logger.debug(
                f"📊 Auto-initiate metrics recorded for alert {pending.alert_message_id}"
            )

        except Exception as e:
            logger.warning(f"Failed to record auto-initiate metrics: {e}")

    async def _update_alert_embed(self, pending: PendingAlert) -> None:
        """
        Update the alert embed to show auto-initiation occurred.

        Args:
            pending: The pending alert that was auto-initiated
        """
        try:
            # Get the alert channel
            channel = self._bot.get_channel(pending.alert_channel_id)
            if not channel:
                logger.warning(
                    f"Could not find channel {pending.alert_channel_id} "
                    "to update alert embed"
                )
                return

            # Fetch the alert message
            try:
                message = await channel.fetch_message(pending.alert_message_id)
            except discord.NotFound:
                logger.warning(
                    f"Alert message {pending.alert_message_id} not found"
                )
                return

            if not message.embeds:
                return

            # Update the embed
            embed = message.embeds[0]

            # Change color to purple (auto-action indicator)
            embed.color = discord.Color.purple()

            # Add auto-initiate field
            embed.add_field(
                name="⏰ Auto-Initiated",
                value=(
                    f"Ash reached out automatically after {self._delay_minutes} "
                    f"minutes (no staff response)"
                ),
                inline=False,
            )

            # Update footer
            original_footer = embed.footer.text if embed.footer else ""
            embed.set_footer(
                text=f"⏰ Auto-initiated | {original_footer}"
            )

            # Disable buttons on the view
            view = discord.ui.View.from_message(message)
            if view:
                for item in view.children:
                    if isinstance(item, discord.ui.Button):
                        item.disabled = True

            await message.edit(embed=embed, view=view)

            logger.debug(
                f"Updated alert embed {pending.alert_message_id} "
                "with auto-initiate status"
            )

        except Exception as e:
            logger.warning(f"Failed to update alert embed: {e}")

    # =========================================================================
    # Redis Persistence
    # =========================================================================

    def _redis_key(self, alert_id: int) -> str:
        """Get Redis key for an alert."""
        return f"{REDIS_KEY_PREFIX}{alert_id}"

    async def _save_alert_to_redis(self, pending: PendingAlert) -> None:
        """Save a pending alert to Redis."""
        if not self._redis or not self._redis.is_connected:
            return

        try:
            key = self._redis_key(pending.alert_message_id)
            data = json.dumps(pending.to_dict())

            # Calculate TTL (expiry + 5 minutes buffer)
            ttl_seconds = int(pending.seconds_until_expiry()) + 300
            if ttl_seconds < 60:
                ttl_seconds = 60

            await self._redis.set(key, data, ttl=ttl_seconds)

        except Exception as e:
            logger.warning(f"Failed to save pending alert to Redis: {e}")

    async def _load_alert_from_redis(
        self,
        alert_id: int,
    ) -> Optional[PendingAlert]:
        """Load a pending alert from Redis."""
        if not self._redis or not self._redis.is_connected:
            return None

        try:
            key = self._redis_key(alert_id)
            data = await self._redis.get(key)

            if data:
                return PendingAlert.from_dict(json.loads(data))

        except Exception as e:
            logger.warning(f"Failed to load pending alert from Redis: {e}")

        return None

    async def _delete_alert_from_redis(self, alert_id: int) -> None:
        """Delete a pending alert from Redis."""
        if not self._redis or not self._redis.is_connected:
            return

        try:
            key = self._redis_key(alert_id)
            await self._redis.delete(key)

        except Exception as e:
            logger.warning(f"Failed to delete pending alert from Redis: {e}")

    async def _load_from_redis(self) -> None:
        """Load all pending alerts from Redis on startup."""
        if not self._redis or not self._redis.is_connected:
            return

        try:
            # Get all pending alert keys
            keys = await self._redis.keys(f"{REDIS_KEY_PREFIX}*")

            for key in keys:
                data = await self._redis.get(key)
                if data:
                    try:
                        pending = PendingAlert.from_dict(json.loads(data))

                        # Only load if not already handled
                        if not pending.cancelled and not pending.auto_initiated:
                            self._pending_alerts[pending.alert_message_id] = pending

                    except Exception as e:
                        logger.warning(f"Failed to parse pending alert: {e}")

            if self._pending_alerts:
                logger.info(
                    f"📥 Loaded {len(self._pending_alerts)} pending alerts from Redis"
                )

        except Exception as e:
            logger.warning(f"Failed to load pending alerts from Redis: {e}")

    async def _save_to_redis(self) -> None:
        """Save all pending alerts to Redis on shutdown."""
        if not self._redis or not self._redis.is_connected:
            return

        saved = 0
        for pending in self._pending_alerts.values():
            if not pending.cancelled and not pending.auto_initiated:
                await self._save_alert_to_redis(pending)
                saved += 1

        if saved:
            logger.info(f"📤 Saved {saved} pending alerts to Redis")

    # =========================================================================
    # Properties and Statistics
    # =========================================================================

    @property
    def is_enabled(self) -> bool:
        """Check if auto-initiate is enabled."""
        return self._enabled

    @property
    def is_running(self) -> bool:
        """Check if background task is running."""
        return self._running

    @property
    def pending_count(self) -> int:
        """Get count of pending alerts."""
        return len(self._pending_alerts)

    def get_stats(self) -> dict:
        """
        Get auto-initiate statistics.

        Returns:
            Dictionary with statistics
        """
        return {
            "enabled": self._enabled,
            "running": self._running,
            "delay_minutes": self._delay_minutes,
            "min_severity": self._min_severity,
            "pending_count": len(self._pending_alerts),
            "total_tracked": self._total_tracked,
            "total_cancelled": self._total_cancelled,
            "total_auto_initiated": self._total_auto_initiated,
            "total_failed": self._total_failed,
        }

    def get_pending_alerts(self) -> list[dict]:
        """
        Get list of pending alerts (for debugging).

        Returns:
            List of pending alert dictionaries
        """
        return [p.to_dict() for p in self._pending_alerts.values()]

    def __repr__(self) -> str:
        """String representation for debugging."""
        return (
            f"AutoInitiateManager("
            f"enabled={self._enabled}, "
            f"pending={len(self._pending_alerts)}, "
            f"auto_initiated={self._total_auto_initiated})"
        )


# =============================================================================
# Factory Function
# =============================================================================


def create_auto_initiate_manager(
    config_manager: "ConfigManager",
    redis_manager: Optional["RedisManager"],
    bot: "commands.Bot",
) -> AutoInitiateManager:
    """
    Factory function for AutoInitiateManager.

    Creates a configured AutoInitiateManager instance.
    Following Clean Architecture v5.1 Rule #1: Factory Functions.

    Note:
        After creation, call set_ash_managers() to inject the
        AshSessionManager and AshPersonalityManager dependencies.
        Then call start() to begin the background check loop.

    Args:
        config_manager: Configuration manager instance
        redis_manager: Redis manager for persistence (optional)
        bot: Discord bot instance

    Returns:
        Configured AutoInitiateManager instance

    Example:
        >>> auto_initiate = create_auto_initiate_manager(
        ...     config_manager=config,
        ...     redis_manager=redis,
        ...     bot=bot,
        ... )
        >>> auto_initiate.set_ash_managers(session_mgr, personality_mgr)
        >>> await auto_initiate.start()
    """
    logger.info("🏭 Creating AutoInitiateManager")

    return AutoInitiateManager(
        config_manager=config_manager,
        redis_manager=redis_manager,
        bot=bot,
    )


# =============================================================================
# Export public interface
# =============================================================================

__all__ = [
    "AutoInitiateManager",
    "create_auto_initiate_manager",
    "PendingAlert",
]
