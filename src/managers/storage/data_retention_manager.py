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
Data Retention Manager for Automated Data Cleanup
----------------------------------------------------------------------------
FILE VERSION: v5.0-8-3.0-1
LAST MODIFIED: 2026-01-05
PHASE: Phase 8 - Metrics & Reporting (Step 8.3)
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-bot
============================================================================

RESPONSIBILITIES:
- Automatically purge old data based on configurable retention periods
- Run daily cleanup at configurable hour (default: 3 AM UTC)
- Track cleanup statistics and provide storage reports
- Graceful degradation if Redis unavailable
- Log cleanup operations for auditing

DATA CATEGORIES:
- Alert metrics (individual): 90 days default
- Daily aggregates: 365 days default  
- Message history: 7 days default
- Session data: 30 days default

REDIS KEY PATTERNS CLEANED:
- ash:metrics:alert:*       → Individual alert metrics
- ash:metrics:daily:*       → Daily aggregates
- ash:metrics:alert_lookup:* → Message ID to alert ID lookups
- ash:history:*             → User message history
- ash:optout:*              → User opt-out preferences

USAGE:
    from src.managers.storage import create_data_retention_manager

    retention_mgr = create_data_retention_manager(
        config_manager=config,
        redis_manager=redis,
    )

    # Start the background cleanup scheduler
    await retention_mgr.start()

    # Manual cleanup (for testing)
    stats = await retention_mgr.run_cleanup()

    # Get storage statistics
    stats = await retention_mgr.get_storage_stats()

    # Stop scheduler on shutdown
    await retention_mgr.stop()
"""

import asyncio
import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta, date, timezone
from typing import TYPE_CHECKING, Dict, List, Optional, Any

if TYPE_CHECKING:
    from src.managers.config_manager import ConfigManager
    from src.managers.storage.redis_manager import RedisManager

# Module version
__version__ = "v5.0-8-3.0-1"

# Initialize logger
logger = logging.getLogger(__name__)


# =============================================================================
# Constants
# =============================================================================

# Redis key prefixes for cleanup
KEY_PREFIX_ALERT_METRICS = "ash:metrics:alert"
KEY_PREFIX_DAILY_AGGREGATE = "ash:metrics:daily"
KEY_PREFIX_ALERT_LOOKUP = "ash:metrics:alert_lookup"
KEY_PREFIX_USER_HISTORY = "ash:history"
KEY_PREFIX_USER_OPTOUT = "ash:optout"
KEY_PREFIX_ASH_SESSION = "ash:session"

# Default retention periods (days)
DEFAULT_ALERT_METRICS_DAYS = 90
DEFAULT_AGGREGATES_DAYS = 365
DEFAULT_MESSAGE_HISTORY_DAYS = 7
DEFAULT_SESSION_DATA_DAYS = 30

# Default cleanup hour (UTC)
DEFAULT_CLEANUP_HOUR = 3

# Seconds per day for TTL calculations
SECONDS_PER_DAY = 86400


# =============================================================================
# Data Classes
# =============================================================================


@dataclass
class CleanupStats:
    """
    Statistics from a cleanup operation.

    Attributes:
        timestamp: When cleanup ran
        duration_seconds: How long cleanup took
        alert_metrics_removed: Individual alert metrics removed
        daily_aggregates_removed: Daily aggregates removed
        alert_lookups_removed: Alert lookups removed
        history_entries_removed: User history entries removed
        optout_entries_removed: Opt-out entries removed
        session_entries_removed: Session entries removed
        total_keys_removed: Total keys removed across all categories
        errors: List of error messages encountered
        success: Whether cleanup completed successfully
    """

    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    duration_seconds: float = 0.0

    # Removal counts by category
    alert_metrics_removed: int = 0
    daily_aggregates_removed: int = 0
    alert_lookups_removed: int = 0
    history_entries_removed: int = 0
    optout_entries_removed: int = 0
    session_entries_removed: int = 0

    # Summary
    total_keys_removed: int = 0
    errors: List[str] = field(default_factory=list)
    success: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging/reporting."""
        return asdict(self)

    def add_error(self, error: str) -> None:
        """Add an error message."""
        self.errors.append(error)
        self.success = False

    def calculate_total(self) -> None:
        """Calculate total keys removed."""
        self.total_keys_removed = (
            self.alert_metrics_removed +
            self.daily_aggregates_removed +
            self.alert_lookups_removed +
            self.history_entries_removed +
            self.optout_entries_removed +
            self.session_entries_removed
        )


@dataclass
class StorageStats:
    """
    Current storage statistics.

    Attributes:
        timestamp: When stats were gathered
        total_keys: Total keys in Redis database
        alert_metrics_count: Number of alert metric keys
        daily_aggregates_count: Number of daily aggregate keys
        history_keys_count: Number of user history keys
        optout_keys_count: Number of opt-out keys
        session_keys_count: Number of session keys
        memory_used_bytes: Redis memory usage (if available)
        last_cleanup: Timestamp of last cleanup
        last_cleanup_stats: Stats from last cleanup
    """

    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    total_keys: int = 0

    # Key counts by category
    alert_metrics_count: int = 0
    daily_aggregates_count: int = 0
    alert_lookups_count: int = 0
    history_keys_count: int = 0
    optout_keys_count: int = 0
    session_keys_count: int = 0

    # Memory (if available)
    memory_used_bytes: Optional[int] = None
    memory_used_human: Optional[str] = None

    # Last cleanup info
    last_cleanup: Optional[str] = None
    last_cleanup_stats: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for reporting."""
        return asdict(self)


# =============================================================================
# Data Retention Manager
# =============================================================================


class DataRetentionManager:
    """
    Manages automated data retention and cleanup.

    Runs a background task that performs daily cleanup at a
    configurable hour. Removes expired data across all data
    categories based on configurable retention periods.

    Attributes:
        _config: ConfigManager for settings
        _redis: RedisManager for storage operations
        _enabled: Whether retention is enabled
        _cleanup_hour: Hour (0-23 UTC) to run cleanup
        _retention_days: Dict of category -> retention days

    Example:
        >>> retention = create_data_retention_manager(config, redis)
        >>> await retention.start()
        >>> # ... bot runs ...
        >>> await retention.stop()
    """

    def __init__(
        self,
        config_manager: "ConfigManager",
        redis_manager: "RedisManager",
    ) -> None:
        """
        Initialize DataRetentionManager.

        Args:
            config_manager: Configuration manager
            redis_manager: Redis manager for storage operations

        Note:
            Use create_data_retention_manager() factory function.
        """
        self._config = config_manager
        self._redis = redis_manager

        # Load configuration with safe defaults
        self._enabled = self._config.get(
            "data_retention", "enabled", True
        )
        self._cleanup_hour = self._config.get(
            "data_retention", "cleanup_hour", DEFAULT_CLEANUP_HOUR
        )

        # Retention periods (days)
        self._retention_days = {
            "alert_metrics": self._config.get(
                "data_retention", "alert_metrics_days", DEFAULT_ALERT_METRICS_DAYS
            ),
            "aggregates": self._config.get(
                "data_retention", "aggregates_days", DEFAULT_AGGREGATES_DAYS
            ),
            "message_history": self._config.get(
                "data_retention", "message_history_days", DEFAULT_MESSAGE_HISTORY_DAYS
            ),
            "session_data": self._config.get(
                "data_retention", "session_data_days", DEFAULT_SESSION_DATA_DAYS
            ),
        }

        # Background task state
        self._scheduler_task: Optional[asyncio.Task] = None
        self._running = False
        self._last_cleanup_stats: Optional[CleanupStats] = None
        self._last_cleanup_time: Optional[datetime] = None

        # Statistics
        self._total_cleanups = 0
        self._total_keys_removed = 0

        logger.info(
            f"✅ DataRetentionManager initialized "
            f"(enabled={self._enabled}, "
            f"cleanup_hour={self._cleanup_hour:02d}:00 UTC, "
            f"alert_metrics={self._retention_days['alert_metrics']}d, "
            f"aggregates={self._retention_days['aggregates']}d, "
            f"history={self._retention_days['message_history']}d, "
            f"sessions={self._retention_days['session_data']}d)"
        )

    # =========================================================================
    # Lifecycle Methods
    # =========================================================================

    async def start(self) -> None:
        """
        Start the background cleanup scheduler.

        Creates an asyncio task that checks hourly and runs
        cleanup when the configured hour is reached.
        """
        if not self._enabled:
            logger.info("ℹ️ Data retention disabled, scheduler not started")
            return

        if self._running:
            logger.warning("⚠️ DataRetentionManager already running")
            return

        self._running = True
        self._scheduler_task = asyncio.create_task(
            self._scheduler_loop(),
            name="data-retention-scheduler",
        )

        logger.info(
            f"🕐 Data retention scheduler started "
            f"(cleanup at {self._cleanup_hour:02d}:00 UTC daily)"
        )

    async def stop(self) -> None:
        """
        Stop the background cleanup scheduler.

        Cancels the scheduler task gracefully.
        """
        self._running = False

        if self._scheduler_task is not None:
            self._scheduler_task.cancel()
            try:
                await self._scheduler_task
            except asyncio.CancelledError:
                pass
            self._scheduler_task = None

        logger.info("🛑 Data retention scheduler stopped")

    async def _scheduler_loop(self) -> None:
        """
        Background scheduler loop.

        Checks every minute if it's time to run cleanup.
        Runs cleanup once at the configured hour each day.
        """
        last_cleanup_date: Optional[date] = None

        while self._running:
            try:
                now = datetime.now(timezone.utc)
                current_date = now.date()
                current_hour = now.hour

                # Check if it's cleanup time
                should_cleanup = (
                    current_hour == self._cleanup_hour and
                    last_cleanup_date != current_date
                )

                if should_cleanup:
                    logger.info("🧹 Starting scheduled data cleanup...")
                    stats = await self.run_cleanup()

                    if stats.success:
                        logger.info(
                            f"✅ Scheduled cleanup complete: "
                            f"{stats.total_keys_removed} keys removed "
                            f"in {stats.duration_seconds:.2f}s"
                        )
                    else:
                        logger.warning(
                            f"⚠️ Scheduled cleanup completed with errors: "
                            f"{', '.join(stats.errors)}"
                        )

                    last_cleanup_date = current_date

                # Sleep for 1 minute before next check
                await asyncio.sleep(60)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Error in retention scheduler: {e}")
                # Continue running despite errors
                await asyncio.sleep(60)

    # =========================================================================
    # Cleanup Operations
    # =========================================================================

    async def run_cleanup(self) -> CleanupStats:
        """
        Run data cleanup across all categories.

        Removes expired data based on configured retention periods.
        This can be called manually or is called by the scheduler.

        Returns:
            CleanupStats with details about what was cleaned
        """
        start_time = datetime.now(timezone.utc)
        stats = CleanupStats()

        if not self._redis or not self._redis.is_connected:
            stats.add_error("Redis not connected")
            logger.warning("⚠️ Cannot run cleanup - Redis not connected")
            return stats

        try:
            # Clean each category
            stats.alert_metrics_removed = await self._cleanup_by_date_pattern(
                prefix=KEY_PREFIX_ALERT_METRICS,
                retention_days=self._retention_days["alert_metrics"],
                category="alert metrics",
            )

            stats.daily_aggregates_removed = await self._cleanup_daily_aggregates(
                retention_days=self._retention_days["aggregates"],
            )

            stats.alert_lookups_removed = await self._cleanup_by_date_pattern(
                prefix=KEY_PREFIX_ALERT_LOOKUP,
                retention_days=self._retention_days["alert_metrics"],
                category="alert lookups",
            )

            stats.history_entries_removed = await self._cleanup_history(
                retention_days=self._retention_days["message_history"],
            )

            stats.optout_entries_removed = await self._cleanup_by_ttl(
                prefix=KEY_PREFIX_USER_OPTOUT,
                category="opt-out entries",
            )

            stats.session_entries_removed = await self._cleanup_by_ttl(
                prefix=KEY_PREFIX_ASH_SESSION,
                category="session entries",
            )

            # Calculate totals
            stats.calculate_total()

        except Exception as e:
            stats.add_error(f"Cleanup failed: {str(e)}")
            logger.error(f"❌ Cleanup operation failed: {e}")

        # Record timing
        end_time = datetime.now(timezone.utc)
        stats.duration_seconds = (end_time - start_time).total_seconds()

        # Update internal state
        self._last_cleanup_stats = stats
        self._last_cleanup_time = start_time
        self._total_cleanups += 1
        self._total_keys_removed += stats.total_keys_removed

        # Log cleanup report
        self._log_cleanup_report(stats)

        return stats

    async def _cleanup_by_date_pattern(
        self,
        prefix: str,
        retention_days: int,
        category: str,
    ) -> int:
        """
        Clean up keys by scanning and checking TTL/dates.

        Args:
            prefix: Redis key prefix to scan
            retention_days: Days to retain data
            category: Category name for logging

        Returns:
            Number of keys removed
        """
        removed = 0

        try:
            # Calculate cutoff timestamp
            cutoff = datetime.now(timezone.utc) - timedelta(days=retention_days)
            cutoff_timestamp = cutoff.timestamp()

            # Scan for keys with this prefix
            pattern = f"{prefix}:*"
            keys = await self._scan_keys(pattern)

            for key in keys:
                try:
                    # Check if key has expired based on score (timestamp)
                    # Get the data and check timestamp
                    result = await self._redis.zrange(key, 0, 0, desc=True, withscores=True)

                    if result:
                        _, score = result[0]
                        if score < cutoff_timestamp:
                            # Delete expired key
                            deleted = await self._redis.delete(key)
                            if deleted:
                                removed += 1
                except Exception as e:
                    logger.debug(f"Error checking key {key}: {e}")
                    continue

            logger.debug(f"🧹 Cleaned {removed} {category}")

        except Exception as e:
            logger.error(f"❌ Error cleaning {category}: {e}")

        return removed

    async def _cleanup_daily_aggregates(
        self,
        retention_days: int,
    ) -> int:
        """
        Clean up daily aggregate keys by date in key name.

        Daily aggregates have date in the key: ash:metrics:daily:YYYY-MM-DD

        Args:
            retention_days: Days to retain aggregates

        Returns:
            Number of keys removed
        """
        removed = 0

        try:
            cutoff_date = date.today() - timedelta(days=retention_days)

            # Scan for daily aggregate keys
            pattern = f"{KEY_PREFIX_DAILY_AGGREGATE}:*"
            keys = await self._scan_keys(pattern)

            for key in keys:
                try:
                    # Extract date from key: ash:metrics:daily:YYYY-MM-DD
                    parts = key.split(":")
                    if len(parts) >= 4:
                        date_str = parts[-1]
                        try:
                            key_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                            if key_date < cutoff_date:
                                deleted = await self._redis.delete(key)
                                if deleted:
                                    removed += 1
                        except ValueError:
                            # Invalid date format, skip
                            continue
                except Exception as e:
                    logger.debug(f"Error checking aggregate key {key}: {e}")
                    continue

            logger.debug(f"🧹 Cleaned {removed} daily aggregates")

        except Exception as e:
            logger.error(f"❌ Error cleaning daily aggregates: {e}")

        return removed

    async def _cleanup_history(
        self,
        retention_days: int,
    ) -> int:
        """
        Clean up user history entries older than retention period.

        History is stored as sorted sets with timestamp scores.
        Uses ZREMRANGEBYSCORE to efficiently remove old entries.

        Args:
            retention_days: Days to retain history

        Returns:
            Number of entries removed
        """
        removed = 0

        try:
            cutoff = datetime.now(timezone.utc) - timedelta(days=retention_days)
            cutoff_timestamp = cutoff.timestamp()

            # Scan for history keys
            pattern = f"{KEY_PREFIX_USER_HISTORY}:*"
            keys = await self._scan_keys(pattern)

            for key in keys:
                try:
                    # Remove entries with score (timestamp) before cutoff
                    count = await self._redis.zremrangebyscore(
                        key,
                        min_score=0,
                        max_score=cutoff_timestamp,
                    )
                    removed += count

                    # Check if key is now empty and delete if so
                    remaining = await self._redis.zcard(key)
                    if remaining == 0:
                        await self._redis.delete(key)

                except Exception as e:
                    logger.debug(f"Error cleaning history key {key}: {e}")
                    continue

            logger.debug(f"🧹 Cleaned {removed} history entries")

        except Exception as e:
            logger.error(f"❌ Error cleaning history: {e}")

        return removed

    async def _cleanup_by_ttl(
        self,
        prefix: str,
        category: str,
    ) -> int:
        """
        Clean up keys that have already expired (no TTL remaining).

        Redis should auto-expire these, but this catches any stragglers.

        Args:
            prefix: Redis key prefix
            category: Category name for logging

        Returns:
            Number of keys removed
        """
        removed = 0

        try:
            pattern = f"{prefix}:*"
            keys = await self._scan_keys(pattern)

            for key in keys:
                try:
                    # Check TTL - if -2, key doesn't exist; if -1, no expiry set
                    ttl = await self._redis.ttl(key)

                    # Remove keys with no TTL set (shouldn't happen, but clean up)
                    if ttl == -1:
                        # Key exists but has no TTL - this shouldn't happen
                        # but we'll leave it for now as it may be intentional
                        logger.debug(f"Key {key} has no TTL set")

                except Exception as e:
                    logger.debug(f"Error checking TTL for {key}: {e}")
                    continue

            logger.debug(f"🧹 Cleaned {removed} {category}")

        except Exception as e:
            logger.error(f"❌ Error cleaning {category}: {e}")

        return removed

    async def _scan_keys(self, pattern: str) -> List[str]:
        """
        Scan Redis for keys matching pattern.

        Args:
            pattern: Key pattern (e.g., "ash:metrics:*")

        Returns:
            List of matching keys
        """
        keys = []

        try:
            if not self._redis._client:
                return keys

            cursor = 0
            while True:
                cursor, batch = await self._redis._client.scan(
                    cursor=cursor,
                    match=pattern,
                    count=100,
                )
                keys.extend(batch)

                if cursor == 0:
                    break

        except Exception as e:
            logger.error(f"❌ Error scanning keys with pattern {pattern}: {e}")

        return keys

    def _log_cleanup_report(self, stats: CleanupStats) -> None:
        """
        Log a formatted cleanup report.

        Args:
            stats: CleanupStats from cleanup operation
        """
        report_lines = [
            "",
            "═" * 60,
            "📊 DATA RETENTION CLEANUP REPORT",
            "═" * 60,
            f"Timestamp:        {stats.timestamp}",
            f"Duration:         {stats.duration_seconds:.2f} seconds",
            f"Status:           {'✅ Success' if stats.success else '⚠️ Completed with errors'}",
            "─" * 60,
            "REMOVED BY CATEGORY:",
            f"  Alert Metrics:    {stats.alert_metrics_removed:,}",
            f"  Daily Aggregates: {stats.daily_aggregates_removed:,}",
            f"  Alert Lookups:    {stats.alert_lookups_removed:,}",
            f"  History Entries:  {stats.history_entries_removed:,}",
            f"  Opt-out Entries:  {stats.optout_entries_removed:,}",
            f"  Session Entries:  {stats.session_entries_removed:,}",
            "─" * 60,
            f"TOTAL REMOVED:      {stats.total_keys_removed:,}",
        ]

        if stats.errors:
            report_lines.extend([
                "─" * 60,
                "ERRORS:",
                *[f"  • {error}" for error in stats.errors],
            ])

        report_lines.append("═" * 60)

        logger.info("\n".join(report_lines))

    # =========================================================================
    # Statistics Methods
    # =========================================================================

    async def get_storage_stats(self) -> StorageStats:
        """
        Get current storage statistics.

        Returns:
            StorageStats with current key counts and memory usage
        """
        stats = StorageStats()

        if not self._redis or not self._redis.is_connected:
            return stats

        try:
            # Get total key count
            stats.total_keys = await self._redis.dbsize()

            # Count keys by category
            stats.alert_metrics_count = len(
                await self._scan_keys(f"{KEY_PREFIX_ALERT_METRICS}:*")
            )
            stats.daily_aggregates_count = len(
                await self._scan_keys(f"{KEY_PREFIX_DAILY_AGGREGATE}:*")
            )
            stats.alert_lookups_count = len(
                await self._scan_keys(f"{KEY_PREFIX_ALERT_LOOKUP}:*")
            )
            stats.history_keys_count = len(
                await self._scan_keys(f"{KEY_PREFIX_USER_HISTORY}:*")
            )
            stats.optout_keys_count = len(
                await self._scan_keys(f"{KEY_PREFIX_USER_OPTOUT}:*")
            )
            stats.session_keys_count = len(
                await self._scan_keys(f"{KEY_PREFIX_ASH_SESSION}:*")
            )

            # Get memory usage
            info = await self._redis.info("memory")
            if info:
                stats.memory_used_bytes = info.get("used_memory", 0)
                stats.memory_used_human = info.get("used_memory_human", "N/A")

            # Add last cleanup info
            if self._last_cleanup_time:
                stats.last_cleanup = self._last_cleanup_time.isoformat()
            if self._last_cleanup_stats:
                stats.last_cleanup_stats = self._last_cleanup_stats.to_dict()

        except Exception as e:
            logger.error(f"❌ Error getting storage stats: {e}")

        return stats

    async def trigger_manual_cleanup(self) -> CleanupStats:
        """
        Manually trigger a cleanup (alias for run_cleanup).

        Useful for testing or administrative cleanup.

        Returns:
            CleanupStats from the cleanup operation
        """
        logger.info("🧹 Manual cleanup triggered")
        return await self.run_cleanup()

    # =========================================================================
    # Properties and Status
    # =========================================================================

    @property
    def is_enabled(self) -> bool:
        """Check if data retention is enabled."""
        return self._enabled

    @property
    def is_running(self) -> bool:
        """Check if scheduler is running."""
        return self._running

    @property
    def cleanup_hour(self) -> int:
        """Get configured cleanup hour (0-23 UTC)."""
        return self._cleanup_hour

    @property
    def retention_days(self) -> Dict[str, int]:
        """Get configured retention periods."""
        return self._retention_days.copy()

    @property
    def total_cleanups(self) -> int:
        """Get total number of cleanups performed."""
        return self._total_cleanups

    @property
    def total_keys_removed(self) -> int:
        """Get total keys removed across all cleanups."""
        return self._total_keys_removed

    def get_next_cleanup_time(self) -> Optional[datetime]:
        """
        Get next scheduled cleanup time.

        Returns:
            Datetime of next cleanup, or None if not running
        """
        if not self._running:
            return None

        now = datetime.now(timezone.utc)
        next_cleanup = now.replace(
            hour=self._cleanup_hour,
            minute=0,
            second=0,
            microsecond=0,
        )

        # If we've passed today's cleanup hour, schedule for tomorrow
        if now.hour >= self._cleanup_hour:
            next_cleanup += timedelta(days=1)

        return next_cleanup

    def get_status(self) -> Dict[str, Any]:
        """
        Get manager status for health checks.

        Returns:
            Status dictionary with configuration and stats
        """
        return {
            "enabled": self._enabled,
            "running": self._running,
            "cleanup_hour": f"{self._cleanup_hour:02d}:00 UTC",
            "retention_days": self._retention_days,
            "total_cleanups": self._total_cleanups,
            "total_keys_removed": self._total_keys_removed,
            "last_cleanup": (
                self._last_cleanup_time.isoformat()
                if self._last_cleanup_time else None
            ),
            "next_cleanup": (
                self.get_next_cleanup_time().isoformat()
                if self.get_next_cleanup_time() else None
            ),
        }

    def __repr__(self) -> str:
        """String representation for debugging."""
        status = "running" if self._running else "stopped"
        return (
            f"DataRetentionManager("
            f"enabled={self._enabled}, "
            f"status={status}, "
            f"cleanups={self._total_cleanups})"
        )


# =============================================================================
# Factory Function
# =============================================================================


def create_data_retention_manager(
    config_manager: "ConfigManager",
    redis_manager: "RedisManager",
) -> DataRetentionManager:
    """
    Factory function for DataRetentionManager.

    Creates a DataRetentionManager instance with proper dependency injection.
    Following Clean Architecture v5.1 Rule #1: Factory Functions.

    Args:
        config_manager: Configuration manager instance
        redis_manager: Redis manager instance

    Returns:
        Configured DataRetentionManager instance

    Example:
        >>> retention = create_data_retention_manager(config, redis)
        >>> await retention.start()
        >>> # ... bot runs ...
        >>> await retention.stop()
    """
    logger.info("🏭 Creating DataRetentionManager")

    return DataRetentionManager(
        config_manager=config_manager,
        redis_manager=redis_manager,
    )


# =============================================================================
# Export public interface
# =============================================================================

__all__ = [
    "DataRetentionManager",
    "create_data_retention_manager",
    "CleanupStats",
    "StorageStats",
    "KEY_PREFIX_ALERT_METRICS",
    "KEY_PREFIX_DAILY_AGGREGATE",
    "KEY_PREFIX_ALERT_LOOKUP",
    "KEY_PREFIX_USER_HISTORY",
    "KEY_PREFIX_USER_OPTOUT",
    "KEY_PREFIX_ASH_SESSION",
]
