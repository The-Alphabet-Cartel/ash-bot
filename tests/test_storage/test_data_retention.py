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
Unit Tests for Data Retention Manager
----------------------------------------------------------------------------
FILE VERSION: v5.0-8-3.0-1
LAST MODIFIED: 2026-01-05
PHASE: Phase 8 - Metrics & Reporting (Step 8.3)
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-bot
============================================================================

USAGE:
    # Run all data retention tests
    docker exec ash-bot python -m pytest tests/test_storage/test_data_retention.py -v

    # Run specific test class
    docker exec ash-bot python -m pytest tests/test_storage/test_data_retention.py::TestDataRetentionManagerInit -v
"""

import asyncio
import json
import pytest
from datetime import datetime, date, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

from src.managers.storage.data_retention_manager import (
    DataRetentionManager,
    create_data_retention_manager,
    CleanupStats,
    StorageStats,
    KEY_PREFIX_ALERT_METRICS,
    KEY_PREFIX_DAILY_AGGREGATE,
    KEY_PREFIX_ALERT_LOOKUP,
    KEY_PREFIX_USER_HISTORY,
    KEY_PREFIX_USER_OPTOUT,
    KEY_PREFIX_ASH_SESSION,
    DEFAULT_ALERT_METRICS_DAYS,
    DEFAULT_AGGREGATES_DAYS,
    DEFAULT_MESSAGE_HISTORY_DAYS,
    DEFAULT_SESSION_DATA_DAYS,
    DEFAULT_CLEANUP_HOUR,
)


# Module version
__version__ = "v5.0-8-3.0-1"


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def mock_config_manager():
    """Create mock ConfigManager with default settings."""
    config = MagicMock()
    config.get.side_effect = lambda section, key, default=None: {
        ("data_retention", "enabled"): True,
        ("data_retention", "cleanup_hour"): 3,
        ("data_retention", "alert_metrics_days"): 90,
        ("data_retention", "aggregates_days"): 365,
        ("data_retention", "message_history_days"): 7,
        ("data_retention", "session_data_days"): 30,
    }.get((section, key), default)
    return config


@pytest.fixture
def mock_config_disabled():
    """Create mock ConfigManager with retention disabled."""
    config = MagicMock()
    config.get.side_effect = lambda section, key, default=None: {
        ("data_retention", "enabled"): False,
        ("data_retention", "cleanup_hour"): 3,
        ("data_retention", "alert_metrics_days"): 90,
        ("data_retention", "aggregates_days"): 365,
        ("data_retention", "message_history_days"): 7,
        ("data_retention", "session_data_days"): 30,
    }.get((section, key), default)
    return config


@pytest.fixture
def mock_redis_manager():
    """Create mock RedisManager."""
    redis = MagicMock()
    redis.is_connected = True
    redis._client = MagicMock()

    # Mock async methods
    redis.zadd = AsyncMock(return_value=1)
    redis.zrange = AsyncMock(return_value=[])
    redis.zcard = AsyncMock(return_value=0)
    redis.zremrangebyscore = AsyncMock(return_value=0)
    redis.delete = AsyncMock(return_value=1)
    redis.expire = AsyncMock(return_value=True)
    redis.ttl = AsyncMock(return_value=3600)
    redis.dbsize = AsyncMock(return_value=100)
    redis.info = AsyncMock(return_value={"used_memory": 1024000, "used_memory_human": "1M"})

    # Mock scan
    async def mock_scan(*args, **kwargs):
        return (0, [])
    redis._client.scan = AsyncMock(side_effect=mock_scan)

    return redis


@pytest.fixture
def mock_redis_disconnected():
    """Create mock disconnected RedisManager."""
    redis = MagicMock()
    redis.is_connected = False
    redis._client = None
    return redis


@pytest.fixture
def retention_manager(mock_config_manager, mock_redis_manager):
    """Create DataRetentionManager with mocked dependencies."""
    return DataRetentionManager(
        config_manager=mock_config_manager,
        redis_manager=mock_redis_manager,
    )


@pytest.fixture
def disabled_retention_manager(mock_config_disabled, mock_redis_manager):
    """Create disabled DataRetentionManager."""
    return DataRetentionManager(
        config_manager=mock_config_disabled,
        redis_manager=mock_redis_manager,
    )


# =============================================================================
# Test: CleanupStats Model
# =============================================================================


class TestCleanupStats:
    """Tests for CleanupStats dataclass."""

    def test_default_values(self):
        """Test default values are set correctly."""
        stats = CleanupStats()

        assert stats.alert_metrics_removed == 0
        assert stats.daily_aggregates_removed == 0
        assert stats.alert_lookups_removed == 0
        assert stats.history_entries_removed == 0
        assert stats.optout_entries_removed == 0
        assert stats.session_entries_removed == 0
        assert stats.total_keys_removed == 0
        assert stats.success is True
        assert stats.errors == []
        assert stats.duration_seconds == 0.0
        assert stats.timestamp is not None

    def test_add_error_marks_failure(self):
        """Test adding error marks success as False."""
        stats = CleanupStats()
        assert stats.success is True

        stats.add_error("Test error")

        assert stats.success is False
        assert "Test error" in stats.errors

    def test_calculate_total(self):
        """Test total calculation."""
        stats = CleanupStats()
        stats.alert_metrics_removed = 10
        stats.daily_aggregates_removed = 5
        stats.alert_lookups_removed = 8
        stats.history_entries_removed = 20
        stats.optout_entries_removed = 3
        stats.session_entries_removed = 2

        stats.calculate_total()

        assert stats.total_keys_removed == 48

    def test_to_dict(self):
        """Test dictionary conversion."""
        stats = CleanupStats()
        stats.alert_metrics_removed = 10

        result = stats.to_dict()

        assert isinstance(result, dict)
        assert result["alert_metrics_removed"] == 10
        assert "timestamp" in result


# =============================================================================
# Test: StorageStats Model
# =============================================================================


class TestStorageStats:
    """Tests for StorageStats dataclass."""

    def test_default_values(self):
        """Test default values are set correctly."""
        stats = StorageStats()

        assert stats.total_keys == 0
        assert stats.alert_metrics_count == 0
        assert stats.daily_aggregates_count == 0
        assert stats.memory_used_bytes is None
        assert stats.last_cleanup is None

    def test_to_dict(self):
        """Test dictionary conversion."""
        stats = StorageStats()
        stats.total_keys = 100
        stats.memory_used_bytes = 1024000

        result = stats.to_dict()

        assert isinstance(result, dict)
        assert result["total_keys"] == 100
        assert result["memory_used_bytes"] == 1024000


# =============================================================================
# Test: DataRetentionManager Initialization
# =============================================================================


class TestDataRetentionManagerInit:
    """Tests for DataRetentionManager initialization."""

    def test_initialization_with_defaults(self, retention_manager):
        """Test manager initializes with correct defaults."""
        assert retention_manager._enabled is True
        assert retention_manager._cleanup_hour == 3
        assert retention_manager._retention_days["alert_metrics"] == 90
        assert retention_manager._retention_days["aggregates"] == 365
        assert retention_manager._retention_days["message_history"] == 7
        assert retention_manager._retention_days["session_data"] == 30

    def test_initialization_disabled(self, disabled_retention_manager):
        """Test manager can be initialized disabled."""
        assert disabled_retention_manager._enabled is False

    def test_initial_state(self, retention_manager):
        """Test initial state is correct."""
        assert retention_manager._running is False
        assert retention_manager._scheduler_task is None
        assert retention_manager._last_cleanup_stats is None
        assert retention_manager._total_cleanups == 0
        assert retention_manager._total_keys_removed == 0


# =============================================================================
# Test: Factory Function
# =============================================================================


class TestFactoryFunction:
    """Tests for create_data_retention_manager factory."""

    def test_factory_creates_manager(self, mock_config_manager, mock_redis_manager):
        """Test factory function creates manager correctly."""
        manager = create_data_retention_manager(
            config_manager=mock_config_manager,
            redis_manager=mock_redis_manager,
        )

        assert isinstance(manager, DataRetentionManager)
        assert manager._config is mock_config_manager
        assert manager._redis is mock_redis_manager


# =============================================================================
# Test: Properties
# =============================================================================


class TestProperties:
    """Tests for DataRetentionManager properties."""

    def test_is_enabled(self, retention_manager, disabled_retention_manager):
        """Test is_enabled property."""
        assert retention_manager.is_enabled is True
        assert disabled_retention_manager.is_enabled is False

    def test_is_running(self, retention_manager):
        """Test is_running property."""
        assert retention_manager.is_running is False

    def test_cleanup_hour(self, retention_manager):
        """Test cleanup_hour property."""
        assert retention_manager.cleanup_hour == 3

    def test_retention_days(self, retention_manager):
        """Test retention_days property returns copy."""
        days = retention_manager.retention_days

        assert days["alert_metrics"] == 90
        assert days["aggregates"] == 365

        # Verify it's a copy
        days["alert_metrics"] = 999
        assert retention_manager.retention_days["alert_metrics"] == 90

    def test_total_cleanups(self, retention_manager):
        """Test total_cleanups property."""
        assert retention_manager.total_cleanups == 0

    def test_total_keys_removed(self, retention_manager):
        """Test total_keys_removed property."""
        assert retention_manager.total_keys_removed == 0


# =============================================================================
# Test: Lifecycle Methods
# =============================================================================


class TestLifecycleMethods:
    """Tests for start/stop lifecycle methods."""

    @pytest.mark.asyncio
    async def test_start_creates_task(self, retention_manager):
        """Test start creates scheduler task."""
        await retention_manager.start()

        assert retention_manager._running is True
        assert retention_manager._scheduler_task is not None

        # Clean up
        await retention_manager.stop()

    @pytest.mark.asyncio
    async def test_start_disabled_does_nothing(self, disabled_retention_manager):
        """Test start does nothing when disabled."""
        await disabled_retention_manager.start()

        assert disabled_retention_manager._running is False
        assert disabled_retention_manager._scheduler_task is None

    @pytest.mark.asyncio
    async def test_stop_cancels_task(self, retention_manager):
        """Test stop cancels scheduler task."""
        await retention_manager.start()
        assert retention_manager._running is True

        await retention_manager.stop()

        assert retention_manager._running is False
        assert retention_manager._scheduler_task is None

    @pytest.mark.asyncio
    async def test_double_start_ignored(self, retention_manager):
        """Test starting twice doesn't create duplicate tasks."""
        await retention_manager.start()
        task1 = retention_manager._scheduler_task

        await retention_manager.start()
        task2 = retention_manager._scheduler_task

        assert task1 is task2

        # Clean up
        await retention_manager.stop()


# =============================================================================
# Test: Cleanup Operations
# =============================================================================


class TestCleanupOperations:
    """Tests for cleanup operations."""

    @pytest.mark.asyncio
    async def test_run_cleanup_returns_stats(self, retention_manager):
        """Test run_cleanup returns CleanupStats."""
        stats = await retention_manager.run_cleanup()

        assert isinstance(stats, CleanupStats)
        assert stats.success is True

    @pytest.mark.asyncio
    async def test_run_cleanup_updates_internal_state(self, retention_manager):
        """Test run_cleanup updates internal state."""
        assert retention_manager._total_cleanups == 0

        await retention_manager.run_cleanup()

        assert retention_manager._total_cleanups == 1
        assert retention_manager._last_cleanup_stats is not None
        assert retention_manager._last_cleanup_time is not None

    @pytest.mark.asyncio
    async def test_run_cleanup_disconnected_redis(
        self, mock_config_manager, mock_redis_disconnected
    ):
        """Test cleanup handles disconnected Redis gracefully."""
        manager = DataRetentionManager(
            config_manager=mock_config_manager,
            redis_manager=mock_redis_disconnected,
        )

        stats = await manager.run_cleanup()

        assert stats.success is False
        assert "Redis not connected" in stats.errors

    @pytest.mark.asyncio
    async def test_trigger_manual_cleanup(self, retention_manager):
        """Test manual cleanup trigger."""
        stats = await retention_manager.trigger_manual_cleanup()

        assert isinstance(stats, CleanupStats)
        assert retention_manager._total_cleanups == 1


# =============================================================================
# Test: Storage Statistics
# =============================================================================


class TestStorageStatistics:
    """Tests for storage statistics methods."""

    @pytest.mark.asyncio
    async def test_get_storage_stats(self, retention_manager, mock_redis_manager):
        """Test get_storage_stats returns stats."""
        stats = await retention_manager.get_storage_stats()

        assert isinstance(stats, StorageStats)
        assert stats.total_keys == 100  # From mock dbsize
        mock_redis_manager.dbsize.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_storage_stats_includes_memory(
        self, retention_manager, mock_redis_manager
    ):
        """Test storage stats includes memory info."""
        stats = await retention_manager.get_storage_stats()

        assert stats.memory_used_bytes == 1024000
        assert stats.memory_used_human == "1M"

    @pytest.mark.asyncio
    async def test_get_storage_stats_disconnected(
        self, mock_config_manager, mock_redis_disconnected
    ):
        """Test stats handles disconnected Redis."""
        manager = DataRetentionManager(
            config_manager=mock_config_manager,
            redis_manager=mock_redis_disconnected,
        )

        stats = await manager.get_storage_stats()

        assert stats.total_keys == 0


# =============================================================================
# Test: Status Methods
# =============================================================================


class TestStatusMethods:
    """Tests for status and health check methods."""

    def test_get_status(self, retention_manager):
        """Test get_status returns complete status."""
        status = retention_manager.get_status()

        assert isinstance(status, dict)
        assert status["enabled"] is True
        assert status["running"] is False
        assert status["cleanup_hour"] == "03:00 UTC"
        assert "retention_days" in status
        assert status["total_cleanups"] == 0
        assert status["total_keys_removed"] == 0

    def test_get_next_cleanup_time_not_running(self, retention_manager):
        """Test next cleanup time is None when not running."""
        assert retention_manager.get_next_cleanup_time() is None

    @pytest.mark.asyncio
    async def test_get_next_cleanup_time_running(self, retention_manager):
        """Test next cleanup time when running."""
        await retention_manager.start()

        next_time = retention_manager.get_next_cleanup_time()

        assert next_time is not None
        assert isinstance(next_time, datetime)
        assert next_time.hour == 3

        await retention_manager.stop()

    def test_repr(self, retention_manager):
        """Test string representation."""
        repr_str = repr(retention_manager)

        assert "DataRetentionManager" in repr_str
        assert "enabled=True" in repr_str
        assert "stopped" in repr_str


# =============================================================================
# Test: Key Prefix Constants
# =============================================================================


class TestConstants:
    """Tests for module constants."""

    def test_key_prefixes(self):
        """Test key prefixes are correct."""
        assert KEY_PREFIX_ALERT_METRICS == "ash:metrics:alert"
        assert KEY_PREFIX_DAILY_AGGREGATE == "ash:metrics:daily"
        assert KEY_PREFIX_ALERT_LOOKUP == "ash:metrics:alert_lookup"
        assert KEY_PREFIX_USER_HISTORY == "ash:history"
        assert KEY_PREFIX_USER_OPTOUT == "ash:optout"
        assert KEY_PREFIX_ASH_SESSION == "ash:session"

    def test_default_values(self):
        """Test default retention values."""
        assert DEFAULT_ALERT_METRICS_DAYS == 90
        assert DEFAULT_AGGREGATES_DAYS == 365
        assert DEFAULT_MESSAGE_HISTORY_DAYS == 7
        assert DEFAULT_SESSION_DATA_DAYS == 30
        assert DEFAULT_CLEANUP_HOUR == 3


# =============================================================================
# Test: Daily Aggregate Cleanup
# =============================================================================


class TestDailyAggregateCleanup:
    """Tests for daily aggregate cleanup logic."""

    @pytest.mark.asyncio
    async def test_cleanup_old_aggregates(
        self, mock_config_manager, mock_redis_manager
    ):
        """Test cleanup removes old daily aggregates."""
        # Setup mock to return keys with old dates
        old_date = (date.today() - timedelta(days=400)).strftime("%Y-%m-%d")
        recent_date = date.today().strftime("%Y-%m-%d")

        async def mock_scan(*args, **kwargs):
            pattern = kwargs.get("match", "")
            if "daily" in pattern:
                return (0, [
                    f"ash:metrics:daily:{old_date}",
                    f"ash:metrics:daily:{recent_date}",
                ])
            return (0, [])

        mock_redis_manager._client.scan = AsyncMock(side_effect=mock_scan)

        manager = DataRetentionManager(
            config_manager=mock_config_manager,
            redis_manager=mock_redis_manager,
        )

        stats = await manager.run_cleanup()

        # Should have attempted to delete the old key
        assert mock_redis_manager.delete.called


# =============================================================================
# Test: History Cleanup
# =============================================================================


class TestHistoryCleanup:
    """Tests for user history cleanup logic."""

    @pytest.mark.asyncio
    async def test_cleanup_old_history(
        self, mock_config_manager, mock_redis_manager
    ):
        """Test cleanup removes old history entries."""
        # Setup mock to return history keys
        async def mock_scan(*args, **kwargs):
            pattern = kwargs.get("match", "")
            if "history" in pattern:
                return (0, ["ash:history:123:456"])
            return (0, [])

        mock_redis_manager._client.scan = AsyncMock(side_effect=mock_scan)
        mock_redis_manager.zremrangebyscore = AsyncMock(return_value=5)
        mock_redis_manager.zcard = AsyncMock(return_value=10)

        manager = DataRetentionManager(
            config_manager=mock_config_manager,
            redis_manager=mock_redis_manager,
        )

        stats = await manager.run_cleanup()

        # Should have called zremrangebyscore
        mock_redis_manager.zremrangebyscore.assert_called()
        assert stats.history_entries_removed == 5


# =============================================================================
# Test: Error Handling
# =============================================================================


class TestErrorHandling:
    """Tests for error handling in cleanup operations."""

    @pytest.mark.asyncio
    async def test_cleanup_handles_scan_error(
        self, mock_config_manager, mock_redis_manager
    ):
        """Test cleanup handles scan errors gracefully."""
        mock_redis_manager._client.scan = AsyncMock(
            side_effect=Exception("Scan failed")
        )

        manager = DataRetentionManager(
            config_manager=mock_config_manager,
            redis_manager=mock_redis_manager,
        )

        stats = await manager.run_cleanup()

        # Should complete without crashing
        assert isinstance(stats, CleanupStats)

    @pytest.mark.asyncio
    async def test_cleanup_handles_delete_error(
        self, mock_config_manager, mock_redis_manager
    ):
        """Test cleanup handles delete errors gracefully."""
        async def mock_scan(*args, **kwargs):
            return (0, ["ash:metrics:daily:2025-01-01"])

        mock_redis_manager._client.scan = AsyncMock(side_effect=mock_scan)
        mock_redis_manager.delete = AsyncMock(side_effect=Exception("Delete failed"))

        manager = DataRetentionManager(
            config_manager=mock_config_manager,
            redis_manager=mock_redis_manager,
        )

        stats = await manager.run_cleanup()

        # Should complete without crashing
        assert isinstance(stats, CleanupStats)


# =============================================================================
# Export test list
# =============================================================================

__all__ = [
    "TestCleanupStats",
    "TestStorageStats",
    "TestDataRetentionManagerInit",
    "TestFactoryFunction",
    "TestProperties",
    "TestLifecycleMethods",
    "TestCleanupOperations",
    "TestStorageStatistics",
    "TestStatusMethods",
    "TestConstants",
    "TestDailyAggregateCleanup",
    "TestHistoryCleanup",
    "TestErrorHandling",
]
