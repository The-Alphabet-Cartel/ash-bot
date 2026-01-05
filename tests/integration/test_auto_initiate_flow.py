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
Integration Tests: Auto-Initiate Flow
---
FILE VERSION: v5.0-7-1.0-1
LAST MODIFIED: 2026-01-04
PHASE: Phase 7 - Core Safety & User Preferences
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-bot
Community: The Alphabet Cartel - https://discord.gg/alphabetcartel | https://alphabetcartel.org
============================================================================
Tests for Auto-Initiate Contact Feature (Step 7.1):
- Full timeout flow: alert → wait → auto-initiate
- Cancellation on acknowledge/Talk to Ash
- Severity filtering
- Multiple pending alerts
- Redis persistence across restarts
- Embed updates after auto-initiation
"""

import asyncio
import json
import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

from src.managers.alerting.auto_initiate_manager import (
    AutoInitiateManager,
    create_auto_initiate_manager,
    PendingAlert,
    REDIS_KEY_PREFIX,
)


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def auto_initiate_config():
    """Configuration for auto-initiate manager."""
    config = MagicMock()
    config.get.side_effect = lambda section, key, default=None: {
        ("auto_initiate", "enabled"): True,
        ("auto_initiate", "delay_minutes"): 3,
        ("auto_initiate", "min_severity"): "medium",
    }.get((section, key), default)
    return config


@pytest.fixture
def auto_initiate_config_low_delay():
    """Configuration with very short delay for testing."""
    config = MagicMock()
    config.get.side_effect = lambda section, key, default=None: {
        ("auto_initiate", "enabled"): True,
        ("auto_initiate", "delay_minutes"): 1,  # 1 minute for faster tests
        ("auto_initiate", "min_severity"): "medium",
    }.get((section, key), default)
    return config


@pytest.fixture
def mock_redis_for_auto_initiate():
    """Redis mock with full async support for auto-initiate."""
    redis = MagicMock()
    redis.is_connected = True
    
    # In-memory storage to simulate Redis
    storage = {}
    
    async def mock_set(key, value, ttl=None):
        storage[key] = value
        return True
    
    async def mock_get(key):
        return storage.get(key)
    
    async def mock_delete(key):
        if key in storage:
            del storage[key]
            return True
        return False
    
    async def mock_keys(pattern):
        prefix = pattern.rstrip("*")
        return [k for k in storage.keys() if k.startswith(prefix)]
    
    redis.set = AsyncMock(side_effect=mock_set)
    redis.get = AsyncMock(side_effect=mock_get)
    redis.delete = AsyncMock(side_effect=mock_delete)
    redis.keys = AsyncMock(side_effect=mock_keys)
    redis._storage = storage  # Expose for test assertions
    
    return redis


@pytest.fixture
def mock_bot_for_auto_initiate(mock_user, mock_alert_channel):
    """Bot mock configured for auto-initiate testing."""
    bot = MagicMock()
    
    # User fetching
    async def fetch_user(user_id):
        user = MagicMock()
        user.id = user_id
        user.display_name = f"User_{user_id}"
        user.dm_channel = MagicMock()
        user.dm_channel.send = AsyncMock()
        user.create_dm = AsyncMock(return_value=user.dm_channel)
        return user
    
    bot.fetch_user = AsyncMock(side_effect=fetch_user)
    bot.get_channel = MagicMock(return_value=mock_alert_channel)
    
    return bot


@pytest.fixture
def mock_ash_session_manager_for_auto():
    """Ash session manager mock for auto-initiate."""
    manager = MagicMock()
    manager.has_active_session = MagicMock(return_value=False)
    
    # Track created sessions
    sessions_created = []
    
    async def start_session(user, trigger_severity):
        session = MagicMock()
        session.session_id = f"session_{user.id}_{len(sessions_created)}"
        session.user_id = user.id
        session.dm_channel = user.dm_channel
        session.add_assistant_message = MagicMock()
        sessions_created.append(session)
        return session
    
    manager.start_session = AsyncMock(side_effect=start_session)
    manager._sessions_created = sessions_created
    
    return manager


@pytest.fixture
def mock_ash_personality_manager_for_auto():
    """Ash personality manager mock."""
    manager = MagicMock()
    manager.get_welcome_message = MagicMock(
        return_value="Hey there 💜 I'm Ash. I noticed you might be going through something difficult."
    )
    return manager


@pytest.fixture
def auto_initiate_manager_full(
    auto_initiate_config,
    mock_redis_for_auto_initiate,
    mock_bot_for_auto_initiate,
    mock_ash_session_manager_for_auto,
    mock_ash_personality_manager_for_auto,
):
    """Fully configured AutoInitiateManager for integration tests."""
    manager = create_auto_initiate_manager(
        config_manager=auto_initiate_config,
        redis_manager=mock_redis_for_auto_initiate,
        bot=mock_bot_for_auto_initiate,
    )
    
    # Inject Ash managers
    manager.set_ash_managers(
        ash_session_manager=mock_ash_session_manager_for_auto,
        ash_personality_manager=mock_ash_personality_manager_for_auto,
    )
    
    return manager


@pytest.fixture
def create_mock_alert_message():
    """Factory for creating mock alert messages."""
    counter = 0
    
    def _create(channel_id=555666777888999000):
        nonlocal counter
        counter += 1
        msg = MagicMock()
        msg.id = 100000000000000000 + counter
        msg.channel = MagicMock()
        msg.channel.id = channel_id
        msg.embeds = [MagicMock()]
        msg.embeds[0].footer = MagicMock()
        msg.embeds[0].footer.text = "Request ID: test_123"
        msg.edit = AsyncMock()
        return msg
    
    return _create


@pytest.fixture
def create_mock_original_message(mock_user, mock_channel):
    """Factory for creating mock original crisis messages."""
    counter = 0
    
    def _create(content="I'm feeling really down"):
        nonlocal counter
        counter += 1
        msg = MagicMock()
        msg.id = 200000000000000000 + counter
        msg.content = content
        msg.author = mock_user
        msg.channel = mock_channel
        msg.channel.id = mock_channel.id
        return msg
    
    return _create


# =============================================================================
# Scenario 1: Full Auto-Initiate Flow
# =============================================================================


class TestAutoInitiateFullFlow:
    """
    Scenario: Alert times out and Ash auto-initiates contact.
    
    Flow:
    1. Crisis alert dispatched
    2. Alert tracked by AutoInitiateManager
    3. Timer expires (no CRT response)
    4. Ash automatically initiates session
    5. Alert embed updated with auto-initiate indicator
    """

    @pytest.mark.asyncio
    async def test_alert_tracked_on_dispatch(
        self,
        auto_initiate_manager_full,
        create_mock_alert_message,
        create_mock_original_message,
        mock_user,
    ):
        """Test that alerts are tracked when dispatched."""
        manager = auto_initiate_manager_full
        alert_msg = create_mock_alert_message()
        original_msg = create_mock_original_message()
        
        # Track the alert
        result = await manager.track_alert(
            alert_message=alert_msg,
            user_id=mock_user.id,
            severity="high",
            original_message=original_msg,
        )
        
        assert result is True
        assert manager.pending_count == 1
        assert alert_msg.id in manager._pending_alerts
        
        pending = manager._pending_alerts[alert_msg.id]
        assert pending.user_id == mock_user.id
        assert pending.severity == "high"
        assert pending.auto_initiated is False
        assert pending.cancelled is False

    @pytest.mark.asyncio
    async def test_expired_alert_triggers_auto_initiate(
        self,
        auto_initiate_manager_full,
        create_mock_alert_message,
        create_mock_original_message,
        mock_user,
        mock_ash_session_manager_for_auto,
    ):
        """Test that expired alerts trigger auto-initiation."""
        manager = auto_initiate_manager_full
        alert_msg = create_mock_alert_message()
        original_msg = create_mock_original_message()
        
        # Track alert
        await manager.track_alert(
            alert_message=alert_msg,
            user_id=mock_user.id,
            severity="high",
            original_message=original_msg,
        )
        
        # Manually expire the alert (simulate time passing)
        pending = manager._pending_alerts[alert_msg.id]
        pending.expires_at = datetime.now(timezone.utc) - timedelta(seconds=10)
        
        # Process expired alerts
        await manager._process_expired_alerts()
        
        # Verify Ash session was started
        assert mock_ash_session_manager_for_auto.start_session.called
        assert len(mock_ash_session_manager_for_auto._sessions_created) == 1
        
        # Verify stats updated
        assert manager._total_auto_initiated == 1
        assert manager.pending_count == 0

    @pytest.mark.asyncio
    async def test_auto_initiate_sends_welcome_message(
        self,
        auto_initiate_manager_full,
        create_mock_alert_message,
        create_mock_original_message,
        mock_user,
        mock_bot_for_auto_initiate,
        mock_ash_personality_manager_for_auto,
    ):
        """Test that auto-initiation sends welcome message to user."""
        manager = auto_initiate_manager_full
        alert_msg = create_mock_alert_message()
        original_msg = create_mock_original_message()
        
        await manager.track_alert(
            alert_message=alert_msg,
            user_id=mock_user.id,
            severity="high",
            original_message=original_msg,
        )
        
        # Expire and process
        pending = manager._pending_alerts[alert_msg.id]
        pending.expires_at = datetime.now(timezone.utc) - timedelta(seconds=10)
        await manager._process_expired_alerts()
        
        # Verify welcome message was requested
        mock_ash_personality_manager_for_auto.get_welcome_message.assert_called_once()
        
        # Verify user was fetched
        mock_bot_for_auto_initiate.fetch_user.assert_called_with(mock_user.id)


# =============================================================================
# Scenario 2: Alert Acknowledged Before Timeout
# =============================================================================


class TestAlertAcknowledgement:
    """
    Scenario: CRT acknowledges alert before timeout.
    
    Flow:
    1. Crisis alert dispatched and tracked
    2. CRT clicks "Acknowledge" button
    3. Timer cancelled
    4. No auto-initiation occurs
    """

    @pytest.mark.asyncio
    async def test_acknowledge_cancels_timer(
        self,
        auto_initiate_manager_full,
        create_mock_alert_message,
        create_mock_original_message,
        mock_user,
    ):
        """Test that acknowledging an alert cancels the timer."""
        manager = auto_initiate_manager_full
        alert_msg = create_mock_alert_message()
        original_msg = create_mock_original_message()
        
        # Track alert
        await manager.track_alert(
            alert_message=alert_msg,
            user_id=mock_user.id,
            severity="high",
            original_message=original_msg,
        )
        
        assert manager.pending_count == 1
        
        # Cancel (simulate acknowledge button)
        result = await manager.cancel_alert(
            alert_message_id=alert_msg.id,
            reason="acknowledged",
        )
        
        assert result is True
        assert manager.pending_count == 0
        assert manager._total_cancelled == 1

    @pytest.mark.asyncio
    async def test_cancelled_alert_not_auto_initiated(
        self,
        auto_initiate_manager_full,
        create_mock_alert_message,
        create_mock_original_message,
        mock_user,
        mock_ash_session_manager_for_auto,
    ):
        """Test that cancelled alerts don't trigger auto-initiation."""
        manager = auto_initiate_manager_full
        alert_msg = create_mock_alert_message()
        original_msg = create_mock_original_message()
        
        # Track and cancel
        await manager.track_alert(
            alert_message=alert_msg,
            user_id=mock_user.id,
            severity="high",
            original_message=original_msg,
        )
        await manager.cancel_alert(alert_msg.id, "acknowledged")
        
        # Even if we try to process, nothing should happen
        await manager._process_expired_alerts()
        
        # No session should be created
        assert not mock_ash_session_manager_for_auto.start_session.called
        assert manager._total_auto_initiated == 0

    @pytest.mark.asyncio
    async def test_talk_to_ash_cancels_timer(
        self,
        auto_initiate_manager_full,
        create_mock_alert_message,
        create_mock_original_message,
        mock_user,
    ):
        """Test that 'Talk to Ash' button also cancels the timer."""
        manager = auto_initiate_manager_full
        alert_msg = create_mock_alert_message()
        original_msg = create_mock_original_message()
        
        await manager.track_alert(
            alert_message=alert_msg,
            user_id=mock_user.id,
            severity="critical",
            original_message=original_msg,
        )
        
        # Cancel with different reason
        result = await manager.cancel_alert(
            alert_message_id=alert_msg.id,
            reason="talk_to_ash_clicked",
        )
        
        assert result is True
        assert manager.pending_count == 0


# =============================================================================
# Scenario 3: Severity Filtering
# =============================================================================


class TestSeverityFiltering:
    """
    Scenario: Only alerts at or above minimum severity are tracked.
    
    Default minimum is "medium", so:
    - LOW: Not tracked
    - MEDIUM: Tracked
    - HIGH: Tracked
    - CRITICAL: Tracked
    """

    @pytest.mark.asyncio
    async def test_low_severity_not_tracked(
        self,
        auto_initiate_manager_full,
        create_mock_alert_message,
        create_mock_original_message,
        mock_user,
    ):
        """Test that LOW severity alerts are not tracked."""
        manager = auto_initiate_manager_full
        alert_msg = create_mock_alert_message()
        original_msg = create_mock_original_message()
        
        result = await manager.track_alert(
            alert_message=alert_msg,
            user_id=mock_user.id,
            severity="low",
            original_message=original_msg,
        )
        
        assert result is False
        assert manager.pending_count == 0

    @pytest.mark.asyncio
    async def test_medium_severity_tracked(
        self,
        auto_initiate_manager_full,
        create_mock_alert_message,
        create_mock_original_message,
        mock_user,
    ):
        """Test that MEDIUM severity alerts are tracked."""
        manager = auto_initiate_manager_full
        alert_msg = create_mock_alert_message()
        original_msg = create_mock_original_message()
        
        result = await manager.track_alert(
            alert_message=alert_msg,
            user_id=mock_user.id,
            severity="medium",
            original_message=original_msg,
        )
        
        assert result is True
        assert manager.pending_count == 1

    @pytest.mark.asyncio
    async def test_critical_severity_tracked(
        self,
        auto_initiate_manager_full,
        create_mock_alert_message,
        create_mock_original_message,
        mock_user,
    ):
        """Test that CRITICAL severity alerts are tracked."""
        manager = auto_initiate_manager_full
        alert_msg = create_mock_alert_message()
        original_msg = create_mock_original_message()
        
        result = await manager.track_alert(
            alert_message=alert_msg,
            user_id=mock_user.id,
            severity="critical",
            original_message=original_msg,
        )
        
        assert result is True
        assert manager.pending_count == 1


# =============================================================================
# Scenario 4: Multiple Pending Alerts
# =============================================================================


class TestMultiplePendingAlerts:
    """
    Scenario: Multiple alerts pending simultaneously.
    
    Each alert has its own independent timer.
    """

    @pytest.mark.asyncio
    async def test_multiple_alerts_tracked_independently(
        self,
        auto_initiate_manager_full,
        create_mock_alert_message,
        create_mock_original_message,
        mock_user,
    ):
        """Test that multiple alerts can be tracked simultaneously."""
        manager = auto_initiate_manager_full
        
        # Create 3 alerts
        alerts = []
        for i in range(3):
            alert_msg = create_mock_alert_message()
            original_msg = create_mock_original_message(f"Crisis message {i}")
            
            await manager.track_alert(
                alert_message=alert_msg,
                user_id=mock_user.id + i,  # Different users
                severity="high",
                original_message=original_msg,
            )
            alerts.append(alert_msg)
        
        assert manager.pending_count == 3
        
        # Cancel one
        await manager.cancel_alert(alerts[1].id, "acknowledged")
        
        assert manager.pending_count == 2

    @pytest.mark.asyncio
    async def test_only_expired_alerts_auto_initiate(
        self,
        auto_initiate_manager_full,
        create_mock_alert_message,
        create_mock_original_message,
        mock_user,
        mock_ash_session_manager_for_auto,
    ):
        """Test that only expired alerts trigger auto-initiation."""
        manager = auto_initiate_manager_full
        
        # Create 3 alerts
        alerts = []
        for i in range(3):
            alert_msg = create_mock_alert_message()
            original_msg = create_mock_original_message()
            
            await manager.track_alert(
                alert_message=alert_msg,
                user_id=mock_user.id + i,
                severity="high",
                original_message=original_msg,
            )
            alerts.append(alert_msg)
        
        # Expire only the first alert
        pending = manager._pending_alerts[alerts[0].id]
        pending.expires_at = datetime.now(timezone.utc) - timedelta(seconds=10)
        
        # Process
        await manager._process_expired_alerts()
        
        # Only 1 session should be created
        assert len(mock_ash_session_manager_for_auto._sessions_created) == 1
        assert manager._total_auto_initiated == 1
        assert manager.pending_count == 2  # 2 still pending


# =============================================================================
# Scenario 5: Redis Persistence
# =============================================================================


class TestRedisPersistence:
    """
    Scenario: Pending alerts persist across bot restarts via Redis.
    
    Flow:
    1. Alert tracked and saved to Redis
    2. Manager stopped (simulating restart)
    3. Manager started and loads from Redis
    4. Alert still pending
    """

    @pytest.mark.asyncio
    async def test_pending_alert_saved_to_redis(
        self,
        auto_initiate_manager_full,
        create_mock_alert_message,
        create_mock_original_message,
        mock_user,
        mock_redis_for_auto_initiate,
    ):
        """Test that pending alerts are saved to Redis."""
        manager = auto_initiate_manager_full
        alert_msg = create_mock_alert_message()
        original_msg = create_mock_original_message()
        
        await manager.track_alert(
            alert_message=alert_msg,
            user_id=mock_user.id,
            severity="high",
            original_message=original_msg,
        )
        
        # Verify Redis set was called
        assert mock_redis_for_auto_initiate.set.called
        
        # Check storage
        key = f"{REDIS_KEY_PREFIX}{alert_msg.id}"
        assert key in mock_redis_for_auto_initiate._storage

    @pytest.mark.asyncio
    async def test_pending_alerts_loaded_on_start(
        self,
        auto_initiate_config,
        mock_redis_for_auto_initiate,
        mock_bot_for_auto_initiate,
    ):
        """Test that pending alerts are loaded from Redis on start."""
        # Pre-populate Redis with a pending alert
        now = datetime.now(timezone.utc)
        pending_data = {
            "alert_message_id": 123456789,
            "alert_channel_id": 555666777,
            "user_id": 111222333,
            "original_message_id": 987654321,
            "original_channel_id": 444555666,
            "severity": "high",
            "created_at": now.isoformat(),
            "expires_at": (now + timedelta(minutes=2)).isoformat(),
            "auto_initiated": False,
            "cancelled": False,
        }
        
        key = f"{REDIS_KEY_PREFIX}123456789"
        mock_redis_for_auto_initiate._storage[key] = json.dumps(pending_data)
        
        # Create fresh manager
        manager = create_auto_initiate_manager(
            config_manager=auto_initiate_config,
            redis_manager=mock_redis_for_auto_initiate,
            bot=mock_bot_for_auto_initiate,
        )
        
        # Start (should load from Redis)
        await manager.start()
        
        try:
            assert manager.pending_count == 1
            assert 123456789 in manager._pending_alerts
        finally:
            await manager.stop()

    @pytest.mark.asyncio
    async def test_cancelled_alert_updated_in_redis(
        self,
        auto_initiate_manager_full,
        create_mock_alert_message,
        create_mock_original_message,
        mock_user,
        mock_redis_for_auto_initiate,
    ):
        """Test that cancelled alerts are updated in Redis with cancelled=True."""
        manager = auto_initiate_manager_full
        alert_msg = create_mock_alert_message()
        original_msg = create_mock_original_message()
        
        await manager.track_alert(
            alert_message=alert_msg,
            user_id=mock_user.id,
            severity="high",
            original_message=original_msg,
        )
        
        key = f"{REDIS_KEY_PREFIX}{alert_msg.id}"
        assert key in mock_redis_for_auto_initiate._storage
        
        # Get initial call count
        initial_set_count = mock_redis_for_auto_initiate.set.call_count
        
        # Cancel
        await manager.cancel_alert(alert_msg.id, "acknowledged")
        
        # Verify set was called again (to update cancelled state)
        assert mock_redis_for_auto_initiate.set.call_count > initial_set_count
        
        # Verify the stored data has cancelled=True
        stored_data = json.loads(mock_redis_for_auto_initiate._storage[key])
        assert stored_data["cancelled"] is True


# =============================================================================
# Scenario 6: Edge Cases
# =============================================================================


class TestEdgeCases:
    """
    Edge case handling for auto-initiate feature.
    """

    @pytest.mark.asyncio
    async def test_user_already_has_session(
        self,
        auto_initiate_manager_full,
        create_mock_alert_message,
        create_mock_original_message,
        mock_user,
        mock_ash_session_manager_for_auto,
    ):
        """Test that auto-initiate skips if user already has active session."""
        manager = auto_initiate_manager_full
        alert_msg = create_mock_alert_message()
        original_msg = create_mock_original_message()
        
        await manager.track_alert(
            alert_message=alert_msg,
            user_id=mock_user.id,
            severity="high",
            original_message=original_msg,
        )
        
        # Simulate user already has session
        mock_ash_session_manager_for_auto.has_active_session = MagicMock(return_value=True)
        
        # Expire and process
        pending = manager._pending_alerts[alert_msg.id]
        pending.expires_at = datetime.now(timezone.utc) - timedelta(seconds=10)
        await manager._process_expired_alerts()
        
        # Session should NOT be started
        assert not mock_ash_session_manager_for_auto.start_session.called

    @pytest.mark.asyncio
    async def test_cancel_nonexistent_alert(
        self,
        auto_initiate_manager_full,
    ):
        """Test cancelling an alert that doesn't exist."""
        manager = auto_initiate_manager_full
        
        result = await manager.cancel_alert(
            alert_message_id=999999999,
            reason="test",
        )
        
        assert result is False

    @pytest.mark.asyncio
    async def test_double_cancel_alert(
        self,
        auto_initiate_manager_full,
        create_mock_alert_message,
        create_mock_original_message,
        mock_user,
    ):
        """Test that cancelling twice doesn't cause issues."""
        manager = auto_initiate_manager_full
        alert_msg = create_mock_alert_message()
        original_msg = create_mock_original_message()
        
        await manager.track_alert(
            alert_message=alert_msg,
            user_id=mock_user.id,
            severity="high",
            original_message=original_msg,
        )
        
        # First cancel
        result1 = await manager.cancel_alert(alert_msg.id, "first")
        assert result1 is True
        
        # Second cancel
        result2 = await manager.cancel_alert(alert_msg.id, "second")
        assert result2 is False

    @pytest.mark.asyncio
    async def test_disabled_manager_does_not_track(
        self,
        mock_redis_for_auto_initiate,
        mock_bot_for_auto_initiate,
        create_mock_alert_message,
        create_mock_original_message,
        mock_user,
    ):
        """Test that disabled manager doesn't track alerts."""
        # Config with disabled auto-initiate
        config = MagicMock()
        config.get.side_effect = lambda section, key, default=None: {
            ("auto_initiate", "enabled"): False,
            ("auto_initiate", "delay_minutes"): 3,
            ("auto_initiate", "min_severity"): "medium",
        }.get((section, key), default)
        
        manager = create_auto_initiate_manager(
            config_manager=config,
            redis_manager=mock_redis_for_auto_initiate,
            bot=mock_bot_for_auto_initiate,
        )
        
        alert_msg = create_mock_alert_message()
        original_msg = create_mock_original_message()
        
        result = await manager.track_alert(
            alert_message=alert_msg,
            user_id=mock_user.id,
            severity="high",
            original_message=original_msg,
        )
        
        assert result is False
        assert manager.pending_count == 0


# =============================================================================
# Scenario 7: Statistics Tracking
# =============================================================================


class TestStatisticsTracking:
    """
    Test that auto-initiate statistics are properly tracked.
    """

    @pytest.mark.asyncio
    async def test_stats_updated_on_track(
        self,
        auto_initiate_manager_full,
        create_mock_alert_message,
        create_mock_original_message,
        mock_user,
    ):
        """Test that tracking increments total_tracked."""
        manager = auto_initiate_manager_full
        
        assert manager._total_tracked == 0
        
        alert_msg = create_mock_alert_message()
        original_msg = create_mock_original_message()
        
        await manager.track_alert(
            alert_message=alert_msg,
            user_id=mock_user.id,
            severity="high",
            original_message=original_msg,
        )
        
        assert manager._total_tracked == 1

    @pytest.mark.asyncio
    async def test_stats_updated_on_cancel(
        self,
        auto_initiate_manager_full,
        create_mock_alert_message,
        create_mock_original_message,
        mock_user,
    ):
        """Test that cancellation increments total_cancelled."""
        manager = auto_initiate_manager_full
        alert_msg = create_mock_alert_message()
        original_msg = create_mock_original_message()
        
        await manager.track_alert(
            alert_message=alert_msg,
            user_id=mock_user.id,
            severity="high",
            original_message=original_msg,
        )
        
        assert manager._total_cancelled == 0
        
        await manager.cancel_alert(alert_msg.id, "test")
        
        assert manager._total_cancelled == 1

    @pytest.mark.asyncio
    async def test_get_stats_returns_complete_info(
        self,
        auto_initiate_manager_full,
        create_mock_alert_message,
        create_mock_original_message,
        mock_user,
    ):
        """Test that get_stats returns complete information."""
        manager = auto_initiate_manager_full
        alert_msg = create_mock_alert_message()
        original_msg = create_mock_original_message()
        
        await manager.track_alert(
            alert_message=alert_msg,
            user_id=mock_user.id,
            severity="high",
            original_message=original_msg,
        )
        
        stats = manager.get_stats()
        
        assert "enabled" in stats
        assert "running" in stats
        assert "delay_minutes" in stats
        assert "min_severity" in stats
        assert "pending_count" in stats
        assert "total_tracked" in stats
        assert "total_cancelled" in stats
        assert "total_auto_initiated" in stats
        assert "total_failed" in stats
        
        assert stats["enabled"] is True
        assert stats["pending_count"] == 1
        assert stats["total_tracked"] == 1
