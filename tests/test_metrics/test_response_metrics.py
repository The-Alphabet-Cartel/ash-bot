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
Unit Tests for Response Metrics Manager (Phase 8.1)
----------------------------------------------------------------------------
FILE VERSION: v5.0-8-1.0-2
LAST MODIFIED: 2026-01-05
PHASE: Phase 8 - Metrics & Reporting
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-bot
============================================================================

TESTS:
- AlertMetrics data model creation and serialization
- DailyAggregate aggregation and serialization
- WeeklySummary creation from aggregates
- ResponseMetricsManager recording methods
- ResponseMetricsManager query methods
- Configuration and enable/disable functionality

USAGE:
    docker exec ash-bot python -m pytest tests/test_response_metrics.py -v
"""

import pytest
import json
from datetime import datetime, date, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

# Import models
from src.managers.metrics.models import (
    AlertMetrics,
    DailyAggregate,
    WeeklySummary,
)

# Import manager
from src.managers.metrics.response_metrics_manager import (
    ResponseMetricsManager,
    create_response_metrics_manager,
    KEY_PREFIX_ALERT,
    KEY_PREFIX_DAILY,
    KEY_PREFIX_LOOKUP,
)


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def mock_config_manager():
    """Create mock configuration manager."""
    config = MagicMock()
    config.get.side_effect = lambda section, key, default=None: {
        ("response_metrics", "enabled"): True,
        ("response_metrics", "retention_days"): 90,
        ("response_metrics", "aggregate_retention_days"): 365,
    }.get((section, key), default)
    return config


@pytest.fixture
def mock_redis_manager():
    """Create mock Redis manager."""
    redis = MagicMock()
    redis.zadd = AsyncMock(return_value=1)
    redis.zrange = AsyncMock(return_value=[])
    redis.expire = AsyncMock(return_value=True)
    redis.is_connected = True
    return redis


@pytest.fixture
def response_metrics_manager(mock_config_manager, mock_redis_manager):
    """Create ResponseMetricsManager with mocks."""
    return create_response_metrics_manager(
        config_manager=mock_config_manager,
        redis_manager=mock_redis_manager,
    )


@pytest.fixture
def sample_alert_metrics():
    """Create sample AlertMetrics for testing."""
    return AlertMetrics(
        alert_id="alert_test123",
        alert_message_id=123456789,
        user_id=987654321,
        channel_id=111222333,
        severity="high",
        channel_sensitivity=1.0,
    )


@pytest.fixture
def sample_daily_aggregate():
    """Create sample DailyAggregate for testing."""
    return DailyAggregate(date="2026-01-05")


# =============================================================================
# AlertMetrics Model Tests
# =============================================================================


class TestAlertMetrics:
    """Tests for AlertMetrics data model."""

    def test_create_alert_metrics(self):
        """Test creating AlertMetrics with required fields."""
        metrics = AlertMetrics(
            alert_id="alert_abc123",
            alert_message_id=123456789,
            user_id=987654321,
            channel_id=111222333,
            severity="high",
        )

        assert metrics.alert_id == "alert_abc123"
        assert metrics.alert_message_id == 123456789
        assert metrics.user_id == 987654321
        assert metrics.severity == "high"
        assert metrics.alert_created_at is not None  # Auto-set

    def test_alert_metrics_default_values(self):
        """Test AlertMetrics default values."""
        metrics = AlertMetrics(
            alert_id="alert_test",
            alert_message_id=1,
            user_id=1,
            channel_id=1,
            severity="medium",
        )

        assert metrics.channel_sensitivity == 1.0
        assert metrics.acknowledged_at is None
        assert metrics.ash_contacted_at is None
        assert metrics.time_to_acknowledge_seconds is None
        assert metrics.was_auto_initiated is False
        assert metrics.user_opted_out is False

    def test_record_acknowledged(self, sample_alert_metrics):
        """Test recording acknowledgment."""
        sample_alert_metrics.record_acknowledged(acknowledged_by=555666777)

        assert sample_alert_metrics.acknowledged_at is not None
        assert sample_alert_metrics.acknowledged_by == 555666777
        assert sample_alert_metrics.time_to_acknowledge_seconds is not None
        assert sample_alert_metrics.time_to_acknowledge_seconds >= 0

    def test_record_ash_contacted_manual(self, sample_alert_metrics):
        """Test recording manual Ash contact."""
        sample_alert_metrics.record_ash_contacted(
            initiated_by=555666777,
            was_auto=False,
        )

        assert sample_alert_metrics.ash_contacted_at is not None
        assert sample_alert_metrics.ash_initiated_by == "555666777"
        assert sample_alert_metrics.was_auto_initiated is False
        assert sample_alert_metrics.time_to_ash_seconds is not None

    def test_record_ash_contacted_auto(self, sample_alert_metrics):
        """Test recording auto-initiated Ash contact."""
        sample_alert_metrics.record_ash_contacted(
            initiated_by="auto",
            was_auto=True,
        )

        assert sample_alert_metrics.ash_initiated_by == "auto"
        assert sample_alert_metrics.was_auto_initiated is True

    def test_record_first_response(self, sample_alert_metrics):
        """Test recording first human response."""
        sample_alert_metrics.record_first_response(responder_id=444555666)

        assert sample_alert_metrics.first_response_at is not None
        assert sample_alert_metrics.first_responder_id == 444555666
        assert sample_alert_metrics.time_to_response_seconds is not None

    def test_record_user_opted_out(self, sample_alert_metrics):
        """Test recording user opt-out."""
        sample_alert_metrics.record_user_opted_out()

        assert sample_alert_metrics.user_opted_out is True

    def test_properties(self, sample_alert_metrics):
        """Test AlertMetrics properties."""
        assert sample_alert_metrics.is_acknowledged is False
        assert sample_alert_metrics.is_ash_engaged is False
        assert sample_alert_metrics.is_resolved is False

        sample_alert_metrics.record_acknowledged(acknowledged_by=1)
        assert sample_alert_metrics.is_acknowledged is True

        sample_alert_metrics.record_ash_contacted(initiated_by=1)
        assert sample_alert_metrics.is_ash_engaged is True

        sample_alert_metrics.record_resolved()
        assert sample_alert_metrics.is_resolved is True

    def test_to_dict(self, sample_alert_metrics):
        """Test AlertMetrics to_dict serialization."""
        data = sample_alert_metrics.to_dict()

        assert isinstance(data, dict)
        assert data["alert_id"] == "alert_test123"
        assert data["alert_message_id"] == 123456789
        assert data["severity"] == "high"

    def test_to_json(self, sample_alert_metrics):
        """Test AlertMetrics to_json serialization."""
        json_str = sample_alert_metrics.to_json()

        assert isinstance(json_str, str)
        data = json.loads(json_str)
        assert data["alert_id"] == "alert_test123"

    def test_from_dict(self):
        """Test AlertMetrics from_dict deserialization."""
        data = {
            "alert_id": "alert_xyz",
            "alert_message_id": 999888777,
            "user_id": 111222333,
            "channel_id": 444555666,
            "severity": "critical",
            "channel_sensitivity": 1.5,
            "alert_created_at": "2026-01-05T12:00:00Z",
        }

        metrics = AlertMetrics.from_dict(data)

        assert metrics.alert_id == "alert_xyz"
        assert metrics.severity == "critical"
        assert metrics.channel_sensitivity == 1.5

    def test_from_json(self):
        """Test AlertMetrics from_json deserialization."""
        json_str = json.dumps({
            "alert_id": "alert_json",
            "alert_message_id": 123,
            "user_id": 456,
            "channel_id": 789,
            "severity": "medium",
            "alert_created_at": "2026-01-05T12:00:00Z",
        })

        metrics = AlertMetrics.from_json(json_str)

        assert metrics.alert_id == "alert_json"
        assert metrics.severity == "medium"

    def test_roundtrip_serialization(self, sample_alert_metrics):
        """Test AlertMetrics roundtrip serialization."""
        sample_alert_metrics.record_acknowledged(acknowledged_by=123)

        json_str = sample_alert_metrics.to_json()
        restored = AlertMetrics.from_json(json_str)

        assert restored.alert_id == sample_alert_metrics.alert_id
        assert restored.acknowledged_by == sample_alert_metrics.acknowledged_by
        assert restored.time_to_acknowledge_seconds == sample_alert_metrics.time_to_acknowledge_seconds


# =============================================================================
# DailyAggregate Model Tests
# =============================================================================


class TestDailyAggregate:
    """Tests for DailyAggregate data model."""

    def test_create_daily_aggregate(self):
        """Test creating DailyAggregate."""
        aggregate = DailyAggregate(date="2026-01-05")

        assert aggregate.date == "2026-01-05"
        assert aggregate.total_alerts == 0
        assert aggregate.acknowledged_count == 0
        assert aggregate.by_severity == {
            "low": 0, "medium": 0, "high": 0, "critical": 0
        }

    def test_add_alert_basic(self, sample_daily_aggregate):
        """Test adding basic alert."""
        sample_daily_aggregate.add_alert(severity="high")

        assert sample_daily_aggregate.total_alerts == 1
        assert sample_daily_aggregate.by_severity["high"] == 1

    def test_add_alert_with_ack_time(self, sample_daily_aggregate):
        """Test adding alert with acknowledgment time."""
        sample_daily_aggregate.add_alert(
            severity="high",
            ack_time=120,
            acknowledged_by=12345,
        )

        assert sample_daily_aggregate.acknowledged_count == 1
        assert sample_daily_aggregate.avg_acknowledge_seconds == 120.0
        assert sample_daily_aggregate.min_acknowledge_seconds == 120
        assert sample_daily_aggregate.max_acknowledge_seconds == 120
        assert "12345" in sample_daily_aggregate.top_responders

    def test_add_multiple_alerts(self, sample_daily_aggregate):
        """Test adding multiple alerts."""
        sample_daily_aggregate.add_alert(severity="high", ack_time=100)
        sample_daily_aggregate.add_alert(severity="medium", ack_time=200)
        sample_daily_aggregate.add_alert(severity="low")

        assert sample_daily_aggregate.total_alerts == 3
        assert sample_daily_aggregate.by_severity["high"] == 1
        assert sample_daily_aggregate.by_severity["medium"] == 1
        assert sample_daily_aggregate.by_severity["low"] == 1
        assert sample_daily_aggregate.acknowledged_count == 2
        assert sample_daily_aggregate.avg_acknowledge_seconds == 150.0
        assert sample_daily_aggregate.min_acknowledge_seconds == 100
        assert sample_daily_aggregate.max_acknowledge_seconds == 200

    def test_add_alert_with_ash_time(self, sample_daily_aggregate):
        """Test adding alert with Ash contact time."""
        sample_daily_aggregate.add_alert(
            severity="critical",
            ash_time=60,
            was_auto_initiated=True,
        )

        assert sample_daily_aggregate.ash_sessions_count == 1
        assert sample_daily_aggregate.auto_initiated_count == 1
        assert sample_daily_aggregate.avg_ash_contact_seconds == 60.0

    def test_add_alert_user_optout(self, sample_daily_aggregate):
        """Test adding alert with user opt-out."""
        sample_daily_aggregate.add_alert(
            severity="high",
            user_opted_out=True,
        )

        assert sample_daily_aggregate.user_optout_count == 1

    def test_to_dict(self, sample_daily_aggregate):
        """Test DailyAggregate to_dict serialization."""
        sample_daily_aggregate.add_alert(severity="high", ack_time=100)

        data = sample_daily_aggregate.to_dict()

        assert isinstance(data, dict)
        assert data["date"] == "2026-01-05"
        assert data["total_alerts"] == 1
        assert "_sum_acknowledge" in data  # Internal state preserved

    def test_from_dict(self):
        """Test DailyAggregate from_dict deserialization."""
        data = {
            "date": "2026-01-05",
            "total_alerts": 5,
            "by_severity": {"low": 1, "medium": 2, "high": 2, "critical": 0},
            "acknowledged_count": 4,
            "ash_sessions_count": 2,
            "auto_initiated_count": 1,
            "user_optout_count": 0,
            "avg_acknowledge_seconds": 150.0,
            "_sum_acknowledge": 600,
            "_count_acknowledge": 4,
        }

        aggregate = DailyAggregate.from_dict(data)

        assert aggregate.total_alerts == 5
        assert aggregate.avg_acknowledge_seconds == 150.0

    def test_roundtrip_serialization(self, sample_daily_aggregate):
        """Test DailyAggregate roundtrip serialization."""
        sample_daily_aggregate.add_alert(severity="high", ack_time=100)
        sample_daily_aggregate.add_alert(severity="medium", ack_time=200)

        json_str = sample_daily_aggregate.to_json()
        restored = DailyAggregate.from_json(json_str)

        assert restored.date == sample_daily_aggregate.date
        assert restored.total_alerts == sample_daily_aggregate.total_alerts
        assert restored.avg_acknowledge_seconds == sample_daily_aggregate.avg_acknowledge_seconds


# =============================================================================
# WeeklySummary Model Tests
# =============================================================================


class TestWeeklySummary:
    """Tests for WeeklySummary data model."""

    def test_create_from_empty_aggregates(self):
        """Test creating WeeklySummary from empty aggregates."""
        summary = WeeklySummary.from_aggregates(
            aggregates=[],
            start_date="2026-01-01",
            end_date="2026-01-07",
        )

        assert summary.start_date == "2026-01-01"
        assert summary.end_date == "2026-01-07"
        assert summary.total_alerts == 0

    def test_create_from_aggregates(self):
        """Test creating WeeklySummary from aggregates."""
        # Create sample aggregates
        agg1 = DailyAggregate(date="2026-01-05")
        agg1.add_alert(severity="high", ack_time=100, acknowledged_by=123)
        agg1.add_alert(severity="medium", ack_time=200, acknowledged_by=456)

        agg2 = DailyAggregate(date="2026-01-06")
        agg2.add_alert(severity="critical", ack_time=50, ash_time=30, acknowledged_by=123)

        summary = WeeklySummary.from_aggregates(
            aggregates=[agg1, agg2],
            start_date="2026-01-01",
            end_date="2026-01-07",
        )

        assert summary.total_alerts == 3
        assert summary.by_severity["high"] == 1
        assert summary.by_severity["medium"] == 1
        assert summary.by_severity["critical"] == 1
        assert summary.avg_acknowledge_seconds is not None
        assert len(summary.top_responders) > 0

    def test_peak_day_calculation(self):
        """Test peak day calculation."""
        agg1 = DailyAggregate(date="2026-01-05")
        agg1.add_alert(severity="high")
        agg1.add_alert(severity="high")

        agg2 = DailyAggregate(date="2026-01-06")
        agg2.add_alert(severity="medium")

        summary = WeeklySummary.from_aggregates(
            aggregates=[agg1, agg2],
            start_date="2026-01-01",
            end_date="2026-01-07",
        )

        assert summary.peak_day == "2026-01-05"

    def test_top_responders_sorted(self):
        """Test top responders are sorted by count."""
        agg = DailyAggregate(date="2026-01-05")
        agg.add_alert(severity="high", ack_time=100, acknowledged_by=111)
        agg.add_alert(severity="high", ack_time=100, acknowledged_by=222)
        agg.add_alert(severity="high", ack_time=100, acknowledged_by=111)
        agg.add_alert(severity="high", ack_time=100, acknowledged_by=111)

        summary = WeeklySummary.from_aggregates(
            aggregates=[agg],
            start_date="2026-01-01",
            end_date="2026-01-07",
        )

        # Top responder should be 111 with 3 acknowledgments
        assert summary.top_responders[0] == ("111", 3)

    def test_serialization(self):
        """Test WeeklySummary serialization."""
        summary = WeeklySummary(
            start_date="2026-01-01",
            end_date="2026-01-07",
            total_alerts=10,
            top_responders=[("123", 5), ("456", 3)],
        )

        json_str = summary.to_json()
        restored = WeeklySummary.from_json(json_str)

        assert restored.total_alerts == 10
        assert len(restored.top_responders) == 2


# =============================================================================
# ResponseMetricsManager Tests
# =============================================================================


class TestResponseMetricsManager:
    """Tests for ResponseMetricsManager."""

    def test_create_manager(self, response_metrics_manager):
        """Test creating ResponseMetricsManager."""
        assert response_metrics_manager is not None
        assert response_metrics_manager.is_enabled is True

    def test_generate_alert_id(self):
        """Test alert ID generation."""
        alert_id = ResponseMetricsManager.generate_alert_id()

        assert alert_id.startswith("alert_")
        assert len(alert_id) == 18  # "alert_" + 12 hex chars

    def test_generate_unique_ids(self):
        """Test that generated IDs are unique."""
        ids = {ResponseMetricsManager.generate_alert_id() for _ in range(100)}
        assert len(ids) == 100  # All unique

    @pytest.mark.asyncio
    async def test_record_alert_created(
        self,
        response_metrics_manager,
        mock_redis_manager,
    ):
        """Test recording alert creation."""
        metrics = await response_metrics_manager.record_alert_created(
            alert_id="alert_test123",
            alert_message_id=123456789,
            user_id=987654321,
            channel_id=111222333,
            severity="high",
            channel_sensitivity=1.2,
        )

        assert metrics is not None
        assert metrics.alert_id == "alert_test123"
        assert metrics.severity == "high"

        # Verify Redis was called
        mock_redis_manager.zadd.assert_called()
        mock_redis_manager.expire.assert_called()

    @pytest.mark.asyncio
    async def test_record_alert_created_disabled(
        self,
        mock_config_manager,
        mock_redis_manager,
    ):
        """Test recording alert when disabled."""
        mock_config_manager.get.side_effect = lambda section, key, default=None: {
            ("response_metrics", "enabled"): False,
        }.get((section, key), default)

        manager = create_response_metrics_manager(
            config_manager=mock_config_manager,
            redis_manager=mock_redis_manager,
        )

        metrics = await manager.record_alert_created(
            alert_id="alert_test",
            alert_message_id=123,
            user_id=456,
            channel_id=789,
            severity="high",
        )

        assert metrics is None
        mock_redis_manager.zadd.assert_not_called()

    @pytest.mark.asyncio
    async def test_record_acknowledged(
        self,
        response_metrics_manager,
        mock_redis_manager,
    ):
        """Test recording acknowledgment."""
        # Setup: Use dictionary to store data by key
        storage = {}

        async def mock_zadd(key, score, value):
            storage[key] = value
            return 1

        async def mock_zrange(key, start, stop, **kwargs):
            if key in storage:
                return [storage[key]]
            return []

        mock_redis_manager.zadd.side_effect = mock_zadd
        mock_redis_manager.zrange.side_effect = mock_zrange

        # Create alert
        await response_metrics_manager.record_alert_created(
            alert_id="alert_ack_test",
            alert_message_id=123,
            user_id=456,
            channel_id=789,
            severity="high",
        )

        # Record acknowledgment
        result = await response_metrics_manager.record_acknowledged(
            alert_id="alert_ack_test",
            acknowledged_by=999,
        )

        assert result is True

    @pytest.mark.asyncio
    async def test_record_ash_contacted(
        self,
        response_metrics_manager,
        mock_redis_manager,
    ):
        """Test recording Ash contact."""
        # Setup: Use dictionary to store data by key
        storage = {}

        async def mock_zadd(key, score, value):
            storage[key] = value
            return 1

        async def mock_zrange(key, start, stop, **kwargs):
            if key in storage:
                return [storage[key]]
            return []

        mock_redis_manager.zadd.side_effect = mock_zadd
        mock_redis_manager.zrange.side_effect = mock_zrange

        # Create alert
        await response_metrics_manager.record_alert_created(
            alert_id="alert_ash_test",
            alert_message_id=123,
            user_id=456,
            channel_id=789,
            severity="high",
        )

        # Record Ash contact
        result = await response_metrics_manager.record_ash_contacted(
            alert_id="alert_ash_test",
            initiated_by=999,
            was_auto_initiated=False,
        )

        assert result is True

    @pytest.mark.asyncio
    async def test_record_ash_auto_initiated(
        self,
        response_metrics_manager,
        mock_redis_manager,
    ):
        """Test recording auto-initiated Ash contact."""
        # Setup: Use dictionary to store data by key
        storage = {}

        async def mock_zadd(key, score, value):
            storage[key] = value
            return 1

        async def mock_zrange(key, start, stop, **kwargs):
            if key in storage:
                return [storage[key]]
            return []

        mock_redis_manager.zadd.side_effect = mock_zadd
        mock_redis_manager.zrange.side_effect = mock_zrange

        # Create alert
        await response_metrics_manager.record_alert_created(
            alert_id="alert_auto_test",
            alert_message_id=123,
            user_id=456,
            channel_id=789,
            severity="high",
        )

        # Record auto-initiate
        result = await response_metrics_manager.record_ash_contacted(
            alert_id="alert_auto_test",
            initiated_by="auto",
            was_auto_initiated=True,
        )

        assert result is True

    @pytest.mark.asyncio
    async def test_get_alert_metrics(
        self,
        response_metrics_manager,
        mock_redis_manager,
    ):
        """Test getting alert metrics."""
        # Setup mock to return stored data
        test_metrics = AlertMetrics(
            alert_id="alert_get_test",
            alert_message_id=123,
            user_id=456,
            channel_id=789,
            severity="high",
        )

        mock_redis_manager.zrange.return_value = [test_metrics.to_json()]

        # Get metrics
        result = await response_metrics_manager.get_alert_metrics("alert_get_test")

        assert result is not None
        assert result.alert_id == "alert_get_test"
        assert result.severity == "high"

    @pytest.mark.asyncio
    async def test_get_alert_metrics_not_found(
        self,
        response_metrics_manager,
        mock_redis_manager,
    ):
        """Test getting non-existent alert metrics."""
        mock_redis_manager.zrange.return_value = []

        result = await response_metrics_manager.get_alert_metrics("nonexistent")

        assert result is None

    @pytest.mark.asyncio
    async def test_get_weekly_summary(
        self,
        response_metrics_manager,
        mock_redis_manager,
    ):
        """Test getting weekly summary."""
        # Setup mock to return daily aggregates
        agg = DailyAggregate(date="2026-01-05")
        agg.add_alert(severity="high", ack_time=100)

        mock_redis_manager.zrange.return_value = [agg.to_json()]

        # Get summary
        summary = await response_metrics_manager.get_weekly_summary()

        assert summary is not None
        assert summary.start_date is not None
        assert summary.end_date is not None

    def test_get_status(self, response_metrics_manager):
        """Test getting manager status."""
        status = response_metrics_manager.get_status()

        assert "enabled" in status
        assert "alerts_tracked" in status
        assert "acknowledgments_recorded" in status
        assert "alert_retention_days" in status
        assert status["enabled"] is True

    def test_key_generation(self, response_metrics_manager):
        """Test Redis key generation."""
        alert_key = response_metrics_manager._alert_key("test123")
        daily_key = response_metrics_manager._daily_key("2026-01-05")
        lookup_key = response_metrics_manager._lookup_key(123456)

        assert alert_key == f"{KEY_PREFIX_ALERT}:test123"
        assert daily_key == f"{KEY_PREFIX_DAILY}:2026-01-05"
        assert lookup_key == f"{KEY_PREFIX_LOOKUP}:123456"


# =============================================================================
# Integration Tests
# =============================================================================


class TestIntegration:
    """Integration tests for response metrics system."""

    @pytest.mark.asyncio
    async def test_full_alert_lifecycle(
        self,
        response_metrics_manager,
        mock_redis_manager,
    ):
        """Test full alert lifecycle through metrics."""
        storage = {}

        async def mock_zadd(key, score, value):
            storage[key] = value
            return 1

        async def mock_zrange(key, start, stop, **kwargs):
            if key in storage:
                return [storage[key]]
            return []

        mock_redis_manager.zadd.side_effect = mock_zadd
        mock_redis_manager.zrange.side_effect = mock_zrange

        # 1. Create alert
        metrics = await response_metrics_manager.record_alert_created(
            alert_id="alert_lifecycle",
            alert_message_id=123456,
            user_id=789,
            channel_id=111,
            severity="high",
        )
        assert metrics is not None
        assert metrics.is_acknowledged is False

        # 2. Record acknowledgment
        result = await response_metrics_manager.record_acknowledged(
            alert_id="alert_lifecycle",
            acknowledged_by=999,
        )
        assert result is True

        # Verify acknowledgment recorded
        updated = await response_metrics_manager.get_alert_metrics("alert_lifecycle")
        assert updated.is_acknowledged is True
        assert updated.acknowledged_by == 999

        # 3. Record Ash contact
        result = await response_metrics_manager.record_ash_contacted(
            alert_id="alert_lifecycle",
            initiated_by=999,
        )
        assert result is True

        # Verify Ash contact recorded
        final = await response_metrics_manager.get_alert_metrics("alert_lifecycle")
        assert final.is_ash_engaged is True

    @pytest.mark.asyncio
    async def test_daily_aggregate_update(
        self,
        response_metrics_manager,
        mock_redis_manager,
    ):
        """Test daily aggregate updates."""
        storage = {}

        async def mock_zadd(key, score, value):
            storage[key] = value
            return 1

        async def mock_zrange(key, start, stop, **kwargs):
            if key in storage:
                return [storage[key]]
            return []

        mock_redis_manager.zadd.side_effect = mock_zadd
        mock_redis_manager.zrange.side_effect = mock_zrange

        # Create and acknowledge alert
        await response_metrics_manager.record_alert_created(
            alert_id="alert_agg_test",
            alert_message_id=123,
            user_id=456,
            channel_id=789,
            severity="high",
        )

        await response_metrics_manager.record_acknowledged(
            alert_id="alert_agg_test",
            acknowledged_by=999,
        )

        # Check that daily aggregate was updated
        today = date.today()
        daily_key = response_metrics_manager._daily_key(today.strftime("%Y-%m-%d"))

        # Aggregate should exist in storage
        assert daily_key in storage or any(KEY_PREFIX_DAILY in k for k in storage)


# =============================================================================
# Run Tests
# =============================================================================


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
