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
Response Metrics Manager for Alert Response Time Tracking
----------------------------------------------------------------------------
FILE VERSION: v5.0-8-1.0-1
LAST MODIFIED: 2026-01-05
PHASE: Phase 8 - Metrics & Reporting
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-bot
============================================================================

RESPONSIBILITIES:
- Track and store response time metrics for crisis alerts
- Record alert creation, acknowledgment, and Ash contact times
- Maintain daily aggregates for efficient reporting
- Provide query methods for weekly summaries
- Apply TTL to stored data for automatic cleanup

REDIS KEY PATTERNS:
- ash:metrics:alert:{alert_id}     → Individual alert metrics (TTL: 90 days)
- ash:metrics:daily:{YYYY-MM-DD}   → Daily aggregates (TTL: 365 days)
- ash:metrics:alert_lookup:{msg_id} → Message ID to Alert ID mapping

USAGE:
    from src.managers.metrics import create_response_metrics_manager

    metrics_mgr = create_response_metrics_manager(
        config_manager=config,
        redis_manager=redis,
    )

    # Record alert creation
    await metrics_mgr.record_alert_created(
        alert_id="alert_123",
        alert_message_id=123456789,
        user_id=987654321,
        channel_id=111222333,
        severity="high",
    )

    # Record acknowledgment
    await metrics_mgr.record_acknowledged(
        alert_id="alert_123",
        acknowledged_by=555666777,
    )
"""

import logging
import uuid
from datetime import datetime, timedelta, date
from typing import TYPE_CHECKING, Dict, List, Optional

from src.managers.metrics.models import AlertMetrics, DailyAggregate, WeeklySummary

if TYPE_CHECKING:
    from src.managers.config_manager import ConfigManager
    from src.managers.storage.redis_manager import RedisManager

# Module version
__version__ = "v5.0-8-1.0-1"

# Initialize logger
logger = logging.getLogger(__name__)


# =============================================================================
# Constants
# =============================================================================

# Redis key prefixes
KEY_PREFIX_ALERT = "ash:metrics:alert"
KEY_PREFIX_DAILY = "ash:metrics:daily"
KEY_PREFIX_LOOKUP = "ash:metrics:alert_lookup"

# Default retention periods (days)
DEFAULT_ALERT_RETENTION_DAYS = 90
DEFAULT_AGGREGATE_RETENTION_DAYS = 365

# TTL in seconds
SECONDS_PER_DAY = 86400


# =============================================================================
# Response Metrics Manager
# =============================================================================


class ResponseMetricsManager:
    """
    Tracks and stores response time metrics for crisis alerts.

    Provides methods to record alert lifecycle events and query
    historical metrics for reporting.

    Attributes:
        _config: ConfigManager for settings
        _redis: RedisManager for storage
        _enabled: Whether metrics tracking is enabled
        _alert_retention_days: Days to retain individual metrics
        _aggregate_retention_days: Days to retain daily aggregates

    Example:
        >>> metrics = create_response_metrics_manager(config, redis)
        >>> await metrics.record_alert_created(...)
        >>> await metrics.record_acknowledged(alert_id, user_id)
        >>> summary = await metrics.get_weekly_summary()
    """

    def __init__(
        self,
        config_manager: "ConfigManager",
        redis_manager: "RedisManager",
    ) -> None:
        """
        Initialize ResponseMetricsManager.

        Args:
            config_manager: Configuration manager
            redis_manager: Redis manager for storage

        Note:
            Use create_response_metrics_manager() factory function.
        """
        self._config = config_manager
        self._redis = redis_manager

        # Load configuration with defaults
        self._enabled = self._config.get(
            "response_metrics", "enabled", True
        )
        self._alert_retention_days = self._config.get(
            "response_metrics", "retention_days", DEFAULT_ALERT_RETENTION_DAYS
        )
        self._aggregate_retention_days = self._config.get(
            "response_metrics", "aggregate_retention_days", DEFAULT_AGGREGATE_RETENTION_DAYS
        )

        # Statistics
        self._alerts_tracked = 0
        self._acknowledgments_recorded = 0

        logger.info(
            f"✅ ResponseMetricsManager initialized "
            f"(enabled={self._enabled}, "
            f"alert_retention={self._alert_retention_days}d, "
            f"aggregate_retention={self._aggregate_retention_days}d)"
        )

    # =========================================================================
    # Key Generation
    # =========================================================================

    def _alert_key(self, alert_id: str) -> str:
        """Generate Redis key for alert metrics."""
        return f"{KEY_PREFIX_ALERT}:{alert_id}"

    def _daily_key(self, date_str: str) -> str:
        """Generate Redis key for daily aggregate."""
        return f"{KEY_PREFIX_DAILY}:{date_str}"

    def _lookup_key(self, message_id: int) -> str:
        """Generate Redis key for message ID to alert ID lookup."""
        return f"{KEY_PREFIX_LOOKUP}:{message_id}"

    @staticmethod
    def generate_alert_id() -> str:
        """
        Generate unique alert ID.

        Returns:
            Unique alert identifier string
        """
        return f"alert_{uuid.uuid4().hex[:12]}"

    # =========================================================================
    # Recording Methods
    # =========================================================================

    async def record_alert_created(
        self,
        alert_id: str,
        alert_message_id: int,
        user_id: int,
        channel_id: int,
        severity: str,
        channel_sensitivity: float = 1.0,
    ) -> Optional[AlertMetrics]:
        """
        Record when an alert is created.

        Creates a new AlertMetrics record and stores it in Redis.

        Args:
            alert_id: Unique alert identifier
            alert_message_id: Discord message ID of the alert
            user_id: User who triggered the alert
            channel_id: Source channel ID
            severity: Crisis severity level
            channel_sensitivity: Channel sensitivity modifier

        Returns:
            Created AlertMetrics object, or None if disabled/failed
        """
        if not self._enabled:
            logger.debug("Response metrics disabled, skipping alert creation")
            return None

        try:
            # Create metrics object
            metrics = AlertMetrics(
                alert_id=alert_id,
                alert_message_id=alert_message_id,
                user_id=user_id,
                channel_id=channel_id,
                severity=severity.lower(),
                channel_sensitivity=channel_sensitivity,
            )

            # Store in Redis with TTL
            key = self._alert_key(alert_id)
            ttl_seconds = self._alert_retention_days * SECONDS_PER_DAY

            # Use Redis SET with JSON (we'll add this as a simple string operation)
            await self._store_metrics(key, metrics.to_json(), ttl_seconds)

            # Create lookup from message ID to alert ID
            lookup_key = self._lookup_key(alert_message_id)
            await self._store_metrics(lookup_key, alert_id, ttl_seconds)

            self._alerts_tracked += 1

            logger.info(
                f"📊 Alert metrics created: {alert_id} "
                f"(severity={severity}, user={user_id})"
            )

            return metrics

        except Exception as e:
            logger.error(f"❌ Failed to record alert creation: {e}")
            return None

    async def record_acknowledged(
        self,
        alert_id: str,
        acknowledged_by: int,
    ) -> bool:
        """
        Record when alert is acknowledged.

        Args:
            alert_id: Alert identifier
            acknowledged_by: User ID of CRT member

        Returns:
            True if recorded successfully
        """
        if not self._enabled:
            return False

        try:
            # Load existing metrics
            metrics = await self.get_alert_metrics(alert_id)
            if metrics is None:
                logger.warning(f"Alert {alert_id} not found for acknowledgment")
                return False

            # Record acknowledgment
            metrics.record_acknowledged(acknowledged_by)

            # Update in Redis
            await self._store_metrics(
                self._alert_key(alert_id),
                metrics.to_json(),
                self._alert_retention_days * SECONDS_PER_DAY,
            )

            # Update daily aggregate
            await self._update_daily_aggregate(metrics)

            self._acknowledgments_recorded += 1

            logger.info(
                f"📊 Acknowledgment recorded: {alert_id} "
                f"by user {acknowledged_by} "
                f"in {metrics.time_to_acknowledge_seconds}s"
            )

            return True

        except Exception as e:
            logger.error(f"❌ Failed to record acknowledgment: {e}")
            return False

    async def record_acknowledged_by_message_id(
        self,
        alert_message_id: int,
        acknowledged_by: int,
    ) -> bool:
        """
        Record acknowledgment using alert message ID.

        Convenience method that looks up alert_id from message_id.

        Args:
            alert_message_id: Discord message ID of the alert
            acknowledged_by: User ID of CRT member

        Returns:
            True if recorded successfully
        """
        alert_id = await self._lookup_alert_id(alert_message_id)
        if alert_id is None:
            logger.debug(f"No alert found for message {alert_message_id}")
            return False

        return await self.record_acknowledged(alert_id, acknowledged_by)

    async def record_ash_contacted(
        self,
        alert_id: str,
        initiated_by: int | str,
        was_auto_initiated: bool = False,
    ) -> bool:
        """
        Record when Ash contact is initiated.

        Args:
            alert_id: Alert identifier
            initiated_by: User ID or "auto" for auto-initiate
            was_auto_initiated: Whether auto-initiated

        Returns:
            True if recorded successfully
        """
        if not self._enabled:
            return False

        try:
            metrics = await self.get_alert_metrics(alert_id)
            if metrics is None:
                logger.warning(f"Alert {alert_id} not found for Ash contact")
                return False

            metrics.record_ash_contacted(initiated_by, was_auto_initiated)

            await self._store_metrics(
                self._alert_key(alert_id),
                metrics.to_json(),
                self._alert_retention_days * SECONDS_PER_DAY,
            )

            # Update daily aggregate
            await self._update_daily_aggregate(metrics)

            logger.info(
                f"📊 Ash contact recorded: {alert_id} "
                f"by {initiated_by} (auto={was_auto_initiated}) "
                f"in {metrics.time_to_ash_seconds}s"
            )

            return True

        except Exception as e:
            logger.error(f"❌ Failed to record Ash contact: {e}")
            return False

    async def record_ash_contacted_by_message_id(
        self,
        alert_message_id: int,
        initiated_by: int | str,
        was_auto_initiated: bool = False,
    ) -> bool:
        """
        Record Ash contact using alert message ID.

        Args:
            alert_message_id: Discord message ID of the alert
            initiated_by: User ID or "auto"
            was_auto_initiated: Whether auto-initiated

        Returns:
            True if recorded successfully
        """
        alert_id = await self._lookup_alert_id(alert_message_id)
        if alert_id is None:
            logger.debug(f"No alert found for message {alert_message_id}")
            return False

        return await self.record_ash_contacted(alert_id, initiated_by, was_auto_initiated)

    async def record_user_opted_out(
        self,
        alert_id: str,
    ) -> bool:
        """
        Record when user opts out of Ash.

        Args:
            alert_id: Alert identifier

        Returns:
            True if recorded successfully
        """
        if not self._enabled:
            return False

        try:
            metrics = await self.get_alert_metrics(alert_id)
            if metrics is None:
                return False

            metrics.record_user_opted_out()

            await self._store_metrics(
                self._alert_key(alert_id),
                metrics.to_json(),
                self._alert_retention_days * SECONDS_PER_DAY,
            )

            # Update daily aggregate
            await self._update_daily_aggregate(metrics)

            logger.debug(f"📊 User opt-out recorded: {alert_id}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to record user opt-out: {e}")
            return False

    async def record_user_opted_out_by_message_id(
        self,
        alert_message_id: int,
    ) -> bool:
        """Record user opt-out using alert message ID."""
        alert_id = await self._lookup_alert_id(alert_message_id)
        if alert_id is None:
            return False
        return await self.record_user_opted_out(alert_id)

    async def record_first_response(
        self,
        alert_id: str,
        responder_id: int,
    ) -> bool:
        """
        Record first human response.

        Args:
            alert_id: Alert identifier
            responder_id: User ID of first responder

        Returns:
            True if recorded successfully
        """
        if not self._enabled:
            return False

        try:
            metrics = await self.get_alert_metrics(alert_id)
            if metrics is None:
                return False

            # Only record if not already recorded
            if metrics.first_response_at is not None:
                logger.debug(f"First response already recorded for {alert_id}")
                return True

            metrics.record_first_response(responder_id)

            await self._store_metrics(
                self._alert_key(alert_id),
                metrics.to_json(),
                self._alert_retention_days * SECONDS_PER_DAY,
            )

            logger.debug(
                f"📊 First response recorded: {alert_id} "
                f"by {responder_id} in {metrics.time_to_response_seconds}s"
            )

            return True

        except Exception as e:
            logger.error(f"❌ Failed to record first response: {e}")
            return False

    # =========================================================================
    # Query Methods
    # =========================================================================

    async def get_alert_metrics(
        self,
        alert_id: str,
    ) -> Optional[AlertMetrics]:
        """
        Get metrics for a specific alert.

        Args:
            alert_id: Alert identifier

        Returns:
            AlertMetrics object or None if not found
        """
        try:
            key = self._alert_key(alert_id)
            data = await self._get_metrics(key)

            if data is None:
                return None

            return AlertMetrics.from_json(data)

        except Exception as e:
            logger.error(f"❌ Failed to get alert metrics: {e}")
            return None

    async def get_daily_aggregate(
        self,
        target_date: date,
    ) -> Optional[DailyAggregate]:
        """
        Get aggregate metrics for a specific day.

        Args:
            target_date: Date to get aggregate for

        Returns:
            DailyAggregate object or None if not found
        """
        try:
            date_str = target_date.strftime("%Y-%m-%d")
            key = self._daily_key(date_str)
            data = await self._get_metrics(key)

            if data is None:
                return None

            return DailyAggregate.from_json(data)

        except Exception as e:
            logger.error(f"❌ Failed to get daily aggregate: {e}")
            return None

    async def get_weekly_summary(
        self,
        end_date: Optional[date] = None,
    ) -> WeeklySummary:
        """
        Get summary for past 7 days.

        Args:
            end_date: End date for the week (default: today)

        Returns:
            WeeklySummary object (may be empty if no data)
        """
        if end_date is None:
            end_date = date.today()

        start_date = end_date - timedelta(days=6)

        # Collect daily aggregates
        aggregates: List[DailyAggregate] = []

        current = start_date
        while current <= end_date:
            aggregate = await self.get_daily_aggregate(current)
            if aggregate is not None:
                aggregates.append(aggregate)
            current += timedelta(days=1)

        # Build summary
        return WeeklySummary.from_aggregates(
            aggregates=aggregates,
            start_date=start_date.strftime("%Y-%m-%d"),
            end_date=end_date.strftime("%Y-%m-%d"),
        )

    # =========================================================================
    # Internal Storage Methods
    # =========================================================================

    async def _store_metrics(
        self,
        key: str,
        value: str,
        ttl_seconds: int,
    ) -> bool:
        """
        Store metrics data in Redis with TTL.

        Args:
            key: Redis key
            value: JSON string to store
            ttl_seconds: TTL in seconds

        Returns:
            True if stored successfully
        """
        try:
            # Use zadd with score as timestamp for consistent storage
            # This allows us to use existing Redis methods
            score = datetime.utcnow().timestamp()
            await self._redis.zadd(key, score, value)
            await self._redis.expire(key, ttl_seconds)
            return True

        except Exception as e:
            logger.error(f"❌ Failed to store metrics at {key}: {e}")
            return False

    async def _get_metrics(self, key: str) -> Optional[str]:
        """
        Get metrics data from Redis.

        Args:
            key: Redis key

        Returns:
            JSON string or None if not found
        """
        try:
            # Get the most recent entry from the sorted set
            results = await self._redis.zrange(key, 0, 0, desc=True)

            if not results:
                return None

            return results[0]

        except Exception as e:
            logger.error(f"❌ Failed to get metrics from {key}: {e}")
            return None

    async def _lookup_alert_id(self, message_id: int) -> Optional[str]:
        """
        Look up alert ID from message ID.

        Args:
            message_id: Discord message ID

        Returns:
            Alert ID string or None if not found
        """
        key = self._lookup_key(message_id)
        return await self._get_metrics(key)

    async def _update_daily_aggregate(
        self,
        metrics: AlertMetrics,
    ) -> None:
        """
        Update daily aggregate with alert metrics.

        Args:
            metrics: AlertMetrics to aggregate
        """
        try:
            # Get date from alert creation
            if metrics.alert_created_at:
                alert_dt = datetime.fromisoformat(
                    metrics.alert_created_at.replace("Z", "+00:00")
                )
                date_str = alert_dt.strftime("%Y-%m-%d")
            else:
                date_str = date.today().strftime("%Y-%m-%d")

            # Load or create aggregate
            key = self._daily_key(date_str)
            existing_data = await self._get_metrics(key)

            if existing_data:
                aggregate = DailyAggregate.from_json(existing_data)
            else:
                aggregate = DailyAggregate(date=date_str)

            # Add this alert's data
            aggregate.add_alert(
                severity=metrics.severity,
                ack_time=metrics.time_to_acknowledge_seconds,
                ash_time=metrics.time_to_ash_seconds,
                response_time=metrics.time_to_response_seconds,
                was_auto_initiated=metrics.was_auto_initiated,
                user_opted_out=metrics.user_opted_out,
                acknowledged_by=metrics.acknowledged_by,
            )

            # Store updated aggregate
            ttl_seconds = self._aggregate_retention_days * SECONDS_PER_DAY
            await self._store_metrics(key, aggregate.to_json(), ttl_seconds)

            logger.debug(f"📊 Daily aggregate updated: {date_str}")

        except Exception as e:
            logger.error(f"❌ Failed to update daily aggregate: {e}")

    # =========================================================================
    # Properties and Status
    # =========================================================================

    @property
    def is_enabled(self) -> bool:
        """Check if response metrics tracking is enabled."""
        return self._enabled

    def get_status(self) -> Dict:
        """
        Get manager status for health checks.

        Returns:
            Status dictionary
        """
        return {
            "enabled": self._enabled,
            "alerts_tracked": self._alerts_tracked,
            "acknowledgments_recorded": self._acknowledgments_recorded,
            "alert_retention_days": self._alert_retention_days,
            "aggregate_retention_days": self._aggregate_retention_days,
        }

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"ResponseMetricsManager("
            f"enabled={self._enabled}, "
            f"tracked={self._alerts_tracked})"
        )


# =============================================================================
# Factory Function
# =============================================================================


def create_response_metrics_manager(
    config_manager: "ConfigManager",
    redis_manager: "RedisManager",
) -> ResponseMetricsManager:
    """
    Factory function for ResponseMetricsManager.

    Creates a ResponseMetricsManager instance with proper dependency injection.
    Following Clean Architecture v5.1 Rule #1: Factory Functions.

    Args:
        config_manager: Configuration manager instance
        redis_manager: Redis manager instance

    Returns:
        Configured ResponseMetricsManager instance

    Example:
        >>> metrics_mgr = create_response_metrics_manager(config, redis)
        >>> await metrics_mgr.record_alert_created(...)
    """
    logger.info("🏭 Creating ResponseMetricsManager")

    return ResponseMetricsManager(
        config_manager=config_manager,
        redis_manager=redis_manager,
    )


# =============================================================================
# Export public interface
# =============================================================================

__all__ = [
    "ResponseMetricsManager",
    "create_response_metrics_manager",
    "KEY_PREFIX_ALERT",
    "KEY_PREFIX_DAILY",
    "KEY_PREFIX_LOOKUP",
]
