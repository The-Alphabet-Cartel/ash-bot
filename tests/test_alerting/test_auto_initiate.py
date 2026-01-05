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
Unit Tests for AutoInitiateManager
----------------------------------------------------------------------------
FILE VERSION: v5.0-7-1.0-1
LAST MODIFIED: 2026-01-04
PHASE: Phase 7 - Core Safety & User Preferences
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-bot
============================================================================
"""

import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

from src.managers.alerting.auto_initiate_manager import (
    AutoInitiateManager,
    create_auto_initiate_manager,
    PendingAlert,
    SEVERITY_ORDER,
)


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def mock_config_manager():
    """Create a mock config manager with auto-initiate settings."""
    config = MagicMock()
    config.get.side_effect = lambda section, key, default=None: {
        ("auto_initiate", "enabled"): True,
        ("auto_initiate", "delay_minutes"): 3,
        ("auto_initiate", "min_severity"): "medium",
    }.get((section, key), default)
    return config


@pytest.fixture
def mock_config_disabled():
    """Create a mock config manager with auto-initiate disabled."""
    config = MagicMock()
    config.get.side_effect = lambda section, key, default=None: {
        ("auto_initiate", "enabled"): False,
        ("auto_initiate", "delay_minutes"): 3,
        ("auto_initiate", "min_severity"): "medium",
    }.get((section, key), default)
    return config


@pytest.fixture
def mock_redis_manager():
    """Create a mock Redis manager."""
    redis = MagicMock()
    redis.is_connected = True
    redis.set = AsyncMock()
    redis.get = AsyncMock(return_value=None)
    redis.delete = AsyncMock()
    redis.keys = AsyncMock(return_value=[])
    return redis


@pytest.fixture
def mock_bot():
    """Create a mock Discord bot."""
    bot = MagicMock()
    bot.fetch_user = AsyncMock()
    bot.get_channel = MagicMock()
    return bot


@pytest.fixture
def mock_ash_session_manager():
    """Create a mock Ash session manager."""
    manager = MagicMock()
    manager.has_active_session = MagicMock(return_value=False)
    manager.start_session = AsyncMock()
    return manager


@pytest.fixture
def mock_ash_personality_manager():
    """Create a mock Ash personality manager."""
    manager = MagicMock()
    manager.get_welcome_message = MagicMock(return_value="Hello, I'm Ash.")
    return manager


@pytest.fixture
def auto_initiate_manager(mock_config_manager, mock_redis_manager, mock_bot):
    """Create an AutoInitiateManager for testing."""
    return create_auto_initiate_manager(
        config_manager=mock_config_manager,
        redis_manager=mock_redis_manager,
        bot=mock_bot,
    )


# =============================================================================
# PendingAlert Tests
# =============================================================================


class TestPendingAlert:
    """Tests for PendingAlert dataclass."""

    def test_create_pending_alert(self):
        """Test creating a pending alert."""
        now = datetime.now(timezone.utc)
        expires = now + timedelta(minutes=3)

        alert = PendingAlert(
            alert_message_id=123456,
            alert_channel_id=789012,
            user_id=111222,
            original_message_id=333444,
            original_channel_id=555666,
            severity="high",
            created_at=now,
            expires_at=expires,
        )

        assert alert.alert_message_id == 123456
        assert alert.user_id == 111222
        assert alert.severity == "high"
        assert alert.auto_initiated is False
        assert alert.cancelled is False

    def test_is_expired_not_expired(self):
        """Test is_expired when alert is not expired."""
        now = datetime.now(timezone.utc)
        expires = now + timedelta(minutes=3)

        alert = PendingAlert(
            alert_message_id=123456,
            alert_channel_id=789012,
            user_id=111222,
            original_message_id=333444,
            original_channel_id=555666,
            severity="high",
            created_at=now,
            expires_at=expires,
        )

        assert alert.is_expired() is False

    def test_is_expired_expired(self):
        """Test is_expired when alert has expired."""
        now = datetime.now(timezone.utc)
        expires = now - timedelta(minutes=1)  # Already expired

        alert = PendingAlert(
            alert_message_id=123456,
            alert_channel_id=789012,
            user_id=111222,
            original_message_id=333444,
            original_channel_id=555666,
            severity="high",
            created_at=now - timedelta(minutes=4),
            expires_at=expires,
        )

        assert alert.is_expired() is True

    def test_is_expired_cancelled(self):
        """Test is_expired returns False when cancelled."""
        now = datetime.now(timezone.utc)
        expires = now - timedelta(minutes=1)  # Would be expired

        alert = PendingAlert(
            alert_message_id=123456,
            alert_channel_id=789012,
            user_id=111222,
            original_message_id=333444,
            original_channel_id=555666,
            severity="high",
            created_at=now - timedelta(minutes=4),
            expires_at=expires,
            cancelled=True,
        )

        assert alert.is_expired() is False

    def test_is_expired_auto_initiated(self):
        """Test is_expired returns False when already auto-initiated."""
        now = datetime.now(timezone.utc)
        expires = now - timedelta(minutes=1)

        alert = PendingAlert(
            alert_message_id=123456,
            alert_channel_id=789012,
            user_id=111222,
            original_message_id=333444,
            original_channel_id=555666,
            severity="high",
            created_at=now - timedelta(minutes=4),
            expires_at=expires,
            auto_initiated=True,
        )

        assert alert.is_expired() is False

    def test_seconds_until_expiry(self):
        """Test seconds_until_expiry calculation."""
        now = datetime.now(timezone.utc)
        expires = now + timedelta(seconds=180)

        alert = PendingAlert(
            alert_message_id=123456,
            alert_channel_id=789012,
            user_id=111222,
            original_message_id=333444,
            original_channel_id=555666,
            severity="high",
            created_at=now,
            expires_at=expires,
        )

        # Should be close to 180 seconds (allow some time for test execution)
        assert 170 < alert.seconds_until_expiry() <= 180

    def test_to_dict_and_from_dict(self):
        """Test serialization and deserialization."""
        now = datetime.now(timezone.utc)
        expires = now + timedelta(minutes=3)

        original = PendingAlert(
            alert_message_id=123456,
            alert_channel_id=789012,
            user_id=111222,
            original_message_id=333444,
            original_channel_id=555666,
            severity="high",
            created_at=now,
            expires_at=expires,
            auto_initiated=False,
            cancelled=False,
        )

        # Serialize
        data = original.to_dict()

        # Deserialize
        restored = PendingAlert.from_dict(data)

        assert restored.alert_message_id == original.alert_message_id
        assert restored.user_id == original.user_id
        assert restored.severity == original.severity
        assert restored.auto_initiated == original.auto_initiated
        assert restored.cancelled == original.cancelled


# =============================================================================
# AutoInitiateManager Tests
# =============================================================================


class TestAutoInitiateManager:
    """Tests for AutoInitiateManager."""

    def test_create_manager(self, auto_initiate_manager):
        """Test factory function creates manager."""
        assert auto_initiate_manager is not None
        assert auto_initiate_manager.is_enabled is True
        assert auto_initiate_manager.pending_count == 0

    def test_create_manager_disabled(self, mock_config_disabled, mock_redis_manager, mock_bot):
        """Test manager when disabled by config."""
        manager = create_auto_initiate_manager(
            config_manager=mock_config_disabled,
            redis_manager=mock_redis_manager,
            bot=mock_bot,
        )

        assert manager.is_enabled is False

    def test_set_ash_managers(
        self,
        auto_initiate_manager,
        mock_ash_session_manager,
        mock_ash_personality_manager,
    ):
        """Test injecting Ash managers."""
        auto_initiate_manager.set_ash_managers(
            ash_session_manager=mock_ash_session_manager,
            ash_personality_manager=mock_ash_personality_manager,
        )

        assert auto_initiate_manager._ash_sessions is mock_ash_session_manager
        assert auto_initiate_manager._ash_personality is mock_ash_personality_manager

    @pytest.mark.asyncio
    async def test_track_alert(self, auto_initiate_manager):
        """Test tracking an alert."""
        # Create mock message objects
        alert_message = MagicMock()
        alert_message.id = 123456
        alert_message.channel.id = 789012

        original_message = MagicMock()
        original_message.id = 333444
        original_message.channel.id = 555666

        # Track the alert
        result = await auto_initiate_manager.track_alert(
            alert_message=alert_message,
            user_id=111222,
            severity="high",
            original_message=original_message,
        )

        assert result is True
        assert auto_initiate_manager.pending_count == 1
        assert 123456 in auto_initiate_manager._pending_alerts

    @pytest.mark.asyncio
    async def test_track_alert_below_threshold(self, auto_initiate_manager):
        """Test tracking alert below minimum severity threshold."""
        alert_message = MagicMock()
        alert_message.id = 123456
        alert_message.channel.id = 789012

        original_message = MagicMock()
        original_message.id = 333444
        original_message.channel.id = 555666

        # Track with "low" severity (below "medium" threshold)
        result = await auto_initiate_manager.track_alert(
            alert_message=alert_message,
            user_id=111222,
            severity="low",
            original_message=original_message,
        )

        assert result is False
        assert auto_initiate_manager.pending_count == 0

    @pytest.mark.asyncio
    async def test_track_alert_disabled(
        self,
        mock_config_disabled,
        mock_redis_manager,
        mock_bot,
    ):
        """Test tracking alert when feature is disabled."""
        manager = create_auto_initiate_manager(
            config_manager=mock_config_disabled,
            redis_manager=mock_redis_manager,
            bot=mock_bot,
        )

        alert_message = MagicMock()
        alert_message.id = 123456
        alert_message.channel.id = 789012

        original_message = MagicMock()
        original_message.id = 333444
        original_message.channel.id = 555666

        result = await manager.track_alert(
            alert_message=alert_message,
            user_id=111222,
            severity="high",
            original_message=original_message,
        )

        assert result is False

    @pytest.mark.asyncio
    async def test_cancel_alert(self, auto_initiate_manager):
        """Test cancelling a tracked alert."""
        # First track an alert
        alert_message = MagicMock()
        alert_message.id = 123456
        alert_message.channel.id = 789012

        original_message = MagicMock()
        original_message.id = 333444
        original_message.channel.id = 555666

        await auto_initiate_manager.track_alert(
            alert_message=alert_message,
            user_id=111222,
            severity="high",
            original_message=original_message,
        )

        assert auto_initiate_manager.pending_count == 1

        # Now cancel it
        result = await auto_initiate_manager.cancel_alert(
            alert_message_id=123456,
            reason="acknowledged",
        )

        assert result is True
        assert auto_initiate_manager.pending_count == 0
        assert auto_initiate_manager._total_cancelled == 1

    @pytest.mark.asyncio
    async def test_cancel_alert_not_found(self, auto_initiate_manager):
        """Test cancelling an alert that doesn't exist."""
        result = await auto_initiate_manager.cancel_alert(
            alert_message_id=999999,
            reason="acknowledged",
        )

        assert result is False

    @pytest.mark.asyncio
    async def test_cancel_alert_already_cancelled(self, auto_initiate_manager):
        """Test cancelling an already cancelled alert."""
        # Track and cancel
        alert_message = MagicMock()
        alert_message.id = 123456
        alert_message.channel.id = 789012

        original_message = MagicMock()
        original_message.id = 333444
        original_message.channel.id = 555666

        await auto_initiate_manager.track_alert(
            alert_message=alert_message,
            user_id=111222,
            severity="high",
            original_message=original_message,
        )

        await auto_initiate_manager.cancel_alert(123456, "first")

        # Try to cancel again
        result = await auto_initiate_manager.cancel_alert(123456, "second")

        assert result is False

    def test_meets_severity_threshold(self, auto_initiate_manager):
        """Test severity threshold checking."""
        # Min severity is "medium"
        assert auto_initiate_manager._meets_severity_threshold("low") is False
        assert auto_initiate_manager._meets_severity_threshold("medium") is True
        assert auto_initiate_manager._meets_severity_threshold("high") is True
        assert auto_initiate_manager._meets_severity_threshold("critical") is True

    def test_get_stats(self, auto_initiate_manager):
        """Test getting statistics."""
        stats = auto_initiate_manager.get_stats()

        assert stats["enabled"] is True
        assert stats["delay_minutes"] == 3
        assert stats["min_severity"] == "medium"
        assert stats["pending_count"] == 0
        assert stats["total_tracked"] == 0

    @pytest.mark.asyncio
    async def test_start_and_stop(self, auto_initiate_manager):
        """Test starting and stopping the manager."""
        await auto_initiate_manager.start()

        assert auto_initiate_manager.is_running is True
        assert auto_initiate_manager._check_task is not None

        await auto_initiate_manager.stop()

        assert auto_initiate_manager.is_running is False

    @pytest.mark.asyncio
    async def test_start_when_disabled(
        self,
        mock_config_disabled,
        mock_redis_manager,
        mock_bot,
    ):
        """Test starting manager when disabled."""
        manager = create_auto_initiate_manager(
            config_manager=mock_config_disabled,
            redis_manager=mock_redis_manager,
            bot=mock_bot,
        )

        await manager.start()

        assert manager.is_running is False


# =============================================================================
# Severity Order Tests
# =============================================================================


class TestSeverityOrder:
    """Tests for severity ordering constants."""

    def test_severity_order(self):
        """Test severity order is correct."""
        assert SEVERITY_ORDER == ["low", "medium", "high", "critical"]

    def test_severity_comparison(self):
        """Test severity index comparison."""
        assert SEVERITY_ORDER.index("low") < SEVERITY_ORDER.index("medium")
        assert SEVERITY_ORDER.index("medium") < SEVERITY_ORDER.index("high")
        assert SEVERITY_ORDER.index("high") < SEVERITY_ORDER.index("critical")
