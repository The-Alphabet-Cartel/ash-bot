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
Tests for FollowUpManager - Phase 9.3
----------------------------------------------------------------------------
FILE VERSION: v5.0-9-3.0-1
LAST MODIFIED: 2026-01-05
PHASE: Phase 9 - CRT Workflow Enhancements (Step 9.3)
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-bot
============================================================================

TESTS:
- Eligibility checking (opt-out, severity, duration, recent follow-ups)
- Follow-up scheduling
- Message generation with variations
- Follow-up sending
- Response handling
- Configuration validation
- Statistics tracking
"""

import asyncio
import json
import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

from src.managers.session.followup_manager import (
    FollowUpManager,
    create_followup_manager,
    ScheduledFollowup,
    CHECKIN_MESSAGES,
    SEVERITY_ORDER,
    REDIS_KEY_SCHEDULED,
    REDIS_KEY_USER_LAST,
    REDIS_KEY_PENDING_RESPONSE,
)


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def mock_config_manager():
    """Create a mock ConfigManager."""
    mock = MagicMock()
    mock.get = MagicMock(side_effect=lambda section, key, default=None: {
        ("followup", "enabled"): True,
        ("followup", "delay_hours"): 24,
        ("followup", "max_hours"): 48,
        ("followup", "min_severity"): "medium",
        ("followup", "min_session_minutes"): 5,
    }.get((section, key), default))
    return mock


@pytest.fixture
def mock_redis_manager():
    """Create a mock RedisManager."""
    mock = MagicMock()
    mock.get = AsyncMock(return_value=None)
    mock.set = AsyncMock(return_value=True)
    mock.delete = AsyncMock(return_value=True)
    mock.exists = AsyncMock(return_value=False)
    mock.keys = AsyncMock(return_value=[])
    mock.rpush = AsyncMock(return_value=True)
    mock.lrange = AsyncMock(return_value=[])
    mock.expire = AsyncMock(return_value=True)
    mock.is_connected = True
    return mock


@pytest.fixture
def mock_user_preferences():
    """Create a mock UserPreferencesManager."""
    mock = MagicMock()
    mock.is_opted_out = AsyncMock(return_value=False)
    return mock


@pytest.fixture
def mock_bot():
    """Create a mock Discord bot."""
    mock = MagicMock()
    mock_user = MagicMock()
    mock_user.id = 123456789
    mock_user.display_name = "TestUser"
    mock_dm = MagicMock()
    mock_dm.send = AsyncMock(return_value=MagicMock())
    mock_user.create_dm = AsyncMock(return_value=mock_dm)
    mock.fetch_user = AsyncMock(return_value=mock_user)
    return mock


@pytest.fixture
def followup_manager(mock_config_manager, mock_redis_manager, mock_user_preferences):
    """Create a FollowUpManager with mocked dependencies."""
    manager = create_followup_manager(
        config_manager=mock_config_manager,
        redis_manager=mock_redis_manager,
        user_preferences_manager=mock_user_preferences,
    )
    return manager


@pytest.fixture
def sample_followup():
    """Create a sample ScheduledFollowup."""
    now = datetime.now(timezone.utc)
    return ScheduledFollowup(
        followup_id="fu_test123",
        user_id=123456789,
        session_id="session_abc",
        session_severity="high",
        session_ended_at=now - timedelta(hours=1),
        scheduled_for=now + timedelta(hours=23),
    )


# =============================================================================
# Test: Factory Function
# =============================================================================


class TestFactoryFunction:
    """Tests for the create_followup_manager factory function."""

    def test_factory_creates_manager(self, mock_config_manager, mock_redis_manager, mock_user_preferences):
        """Factory function should create a FollowUpManager instance."""
        manager = create_followup_manager(
            config_manager=mock_config_manager,
            redis_manager=mock_redis_manager,
            user_preferences_manager=mock_user_preferences,
        )

        assert manager is not None
        assert isinstance(manager, FollowUpManager)

    def test_factory_without_redis(self, mock_config_manager, mock_user_preferences):
        """Factory should work without Redis (graceful degradation)."""
        manager = create_followup_manager(
            config_manager=mock_config_manager,
            redis_manager=None,
            user_preferences_manager=mock_user_preferences,
        )

        assert manager is not None
        assert isinstance(manager, FollowUpManager)

    def test_factory_without_user_preferences(self, mock_config_manager, mock_redis_manager):
        """Factory should work without UserPreferencesManager."""
        manager = create_followup_manager(
            config_manager=mock_config_manager,
            redis_manager=mock_redis_manager,
            user_preferences_manager=None,
        )

        assert manager is not None
        assert isinstance(manager, FollowUpManager)


# =============================================================================
# Test: Configuration
# =============================================================================


class TestConfiguration:
    """Tests for configuration loading."""

    def test_config_loaded_correctly(self, followup_manager):
        """Configuration values should be loaded correctly."""
        assert followup_manager.is_enabled is True
        assert followup_manager.delay_hours == 24
        assert followup_manager.max_hours == 48
        assert followup_manager.min_severity == "medium"

    def test_disabled_by_config(self, mock_redis_manager, mock_user_preferences):
        """Manager should respect enabled=false config."""
        mock_config = MagicMock()
        mock_config.get = MagicMock(side_effect=lambda section, key, default=None: {
            ("followup", "enabled"): False,
            ("followup", "delay_hours"): 24,
            ("followup", "max_hours"): 48,
            ("followup", "min_severity"): "medium",
            ("followup", "min_session_minutes"): 5,
        }.get((section, key), default))

        manager = create_followup_manager(
            config_manager=mock_config,
            redis_manager=mock_redis_manager,
            user_preferences_manager=mock_user_preferences,
        )

        assert manager.is_enabled is False


# =============================================================================
# Test: Eligibility Checking
# =============================================================================


class TestEligibilityChecking:
    """Tests for follow-up eligibility conditions."""

    @pytest.mark.asyncio
    async def test_eligible_session(self, followup_manager):
        """Eligible session should pass all checks."""
        eligible, reason = await followup_manager._check_eligibility(
            user_id=123456789,
            session_severity="high",
            session_duration_seconds=600,  # 10 minutes
        )

        assert eligible is True
        assert reason == "eligible"

    @pytest.mark.asyncio
    async def test_opted_out_user_not_eligible(self, followup_manager, mock_user_preferences):
        """Users who opted out should NOT be eligible."""
        mock_user_preferences.is_opted_out.return_value = True

        eligible, reason = await followup_manager._check_eligibility(
            user_id=123456789,
            session_severity="high",
            session_duration_seconds=600,
        )

        assert eligible is False
        assert "opted out" in reason

    @pytest.mark.asyncio
    async def test_low_severity_not_eligible(self, followup_manager):
        """Low severity sessions should NOT be eligible (min is medium)."""
        eligible, reason = await followup_manager._check_eligibility(
            user_id=123456789,
            session_severity="low",
            session_duration_seconds=600,
        )

        assert eligible is False
        assert "severity" in reason

    @pytest.mark.asyncio
    async def test_short_session_not_eligible(self, followup_manager):
        """Short sessions should NOT be eligible."""
        eligible, reason = await followup_manager._check_eligibility(
            user_id=123456789,
            session_severity="high",
            session_duration_seconds=120,  # 2 minutes (below 5 min minimum)
        )

        assert eligible is False
        assert "duration" in reason

    @pytest.mark.asyncio
    async def test_recent_followup_not_eligible(self, followup_manager, mock_redis_manager):
        """User with recent follow-up should NOT be eligible."""
        mock_redis_manager.exists.return_value = True  # User had recent follow-up

        eligible, reason = await followup_manager._check_eligibility(
            user_id=123456789,
            session_severity="high",
            session_duration_seconds=600,
        )

        assert eligible is False
        assert "24 hours" in reason


# =============================================================================
# Test: Scheduling
# =============================================================================


class TestScheduling:
    """Tests for follow-up scheduling."""

    @pytest.mark.asyncio
    async def test_schedule_followup_success(self, followup_manager, mock_redis_manager):
        """Successfully schedule a follow-up."""
        followup_id = await followup_manager.schedule_followup(
            session_id="session_123",
            user_id=123456789,
            session_severity="high",
            session_duration_seconds=600,
        )

        assert followup_id is not None
        assert followup_id.startswith("fu_")
        assert mock_redis_manager.set.called
        assert followup_manager._total_scheduled == 1

    @pytest.mark.asyncio
    async def test_schedule_skipped_for_opted_out(self, followup_manager, mock_user_preferences):
        """Scheduling should be skipped for opted-out users."""
        mock_user_preferences.is_opted_out.return_value = True

        followup_id = await followup_manager.schedule_followup(
            session_id="session_123",
            user_id=123456789,
            session_severity="high",
            session_duration_seconds=600,
        )

        assert followup_id is None
        assert followup_manager._total_skipped_optout == 1

    @pytest.mark.asyncio
    async def test_schedule_disabled(self, mock_config_manager, mock_redis_manager, mock_user_preferences):
        """Scheduling should return None when disabled."""
        mock_config_manager.get = MagicMock(side_effect=lambda section, key, default=None: {
            ("followup", "enabled"): False,
        }.get((section, key), default))

        manager = create_followup_manager(
            config_manager=mock_config_manager,
            redis_manager=mock_redis_manager,
            user_preferences_manager=mock_user_preferences,
        )

        followup_id = await manager.schedule_followup(
            session_id="session_123",
            user_id=123456789,
            session_severity="high",
            session_duration_seconds=600,
        )

        assert followup_id is None


# =============================================================================
# Test: Message Generation
# =============================================================================


class TestMessageGeneration:
    """Tests for follow-up message generation."""

    def test_message_generation_with_variations(self, followup_manager):
        """Message generation should use variations."""
        now = datetime.now(timezone.utc)
        session_ended_at = now - timedelta(hours=24)

        message1, idx1 = followup_manager._generate_message(
            user_name="TestUser",
            session_ended_at=session_ended_at,
        )

        # Message should contain expected elements
        assert "TestUser" in message1
        assert "💜" in message1
        assert "Ash" in message1
        assert idx1 >= 0 and idx1 < len(CHECKIN_MESSAGES)

    def test_message_time_ago_formatting(self, followup_manager):
        """Time ago should be formatted correctly."""
        now = datetime.now(timezone.utc)

        # Test "earlier today"
        message, _ = followup_manager._generate_message(
            user_name="User",
            session_ended_at=now - timedelta(hours=6),
        )
        assert "earlier" in message.lower()

        # Test "yesterday"
        message, _ = followup_manager._generate_message(
            user_name="User",
            session_ended_at=now - timedelta(hours=30),
        )
        assert "yesterday" in message.lower()

        # Test "X days ago"
        message, _ = followup_manager._generate_message(
            user_name="User",
            session_ended_at=now - timedelta(days=3),
        )
        assert "days ago" in message.lower()


# =============================================================================
# Test: Sending Follow-Ups
# =============================================================================


class TestSendingFollowups:
    """Tests for sending follow-up messages."""

    @pytest.mark.asyncio
    async def test_send_followup_success(self, followup_manager, mock_bot, mock_redis_manager, sample_followup):
        """Successfully send a follow-up DM."""
        followup_manager.set_bot(mock_bot)

        result = await followup_manager._send_followup(sample_followup)

        assert result is True
        assert mock_bot.fetch_user.called
        assert followup_manager._total_sent == 1

    @pytest.mark.asyncio
    async def test_send_skipped_if_opted_out_since_scheduling(self, followup_manager, mock_bot, mock_user_preferences, sample_followup):
        """Sending should be skipped if user opted out since scheduling."""
        followup_manager.set_bot(mock_bot)
        mock_user_preferences.is_opted_out.return_value = True

        result = await followup_manager._send_followup(sample_followup)

        assert result is False
        assert followup_manager._total_skipped_optout == 1

    @pytest.mark.asyncio
    async def test_send_without_bot(self, followup_manager, sample_followup):
        """Sending should fail gracefully without bot."""
        # Don't set bot

        result = await followup_manager._send_followup(sample_followup)

        assert result is False


# =============================================================================
# Test: Data Classes
# =============================================================================


class TestScheduledFollowup:
    """Tests for ScheduledFollowup dataclass."""

    def test_to_dict(self, sample_followup):
        """to_dict should serialize correctly."""
        data = sample_followup.to_dict()

        assert data["followup_id"] == sample_followup.followup_id
        assert data["user_id"] == sample_followup.user_id
        assert data["session_id"] == sample_followup.session_id
        assert data["session_severity"] == sample_followup.session_severity

    def test_from_dict(self, sample_followup):
        """from_dict should deserialize correctly."""
        data = sample_followup.to_dict()
        restored = ScheduledFollowup.from_dict(data)

        assert restored.followup_id == sample_followup.followup_id
        assert restored.user_id == sample_followup.user_id
        assert restored.session_id == sample_followup.session_id
        assert restored.session_severity == sample_followup.session_severity

    def test_is_sent_property(self, sample_followup):
        """is_sent should reflect sent_at status."""
        assert sample_followup.is_sent is False

        sample_followup.sent_at = datetime.now(timezone.utc)
        assert sample_followup.is_sent is True

    def test_is_responded_property(self, sample_followup):
        """is_responded should reflect responded_at status."""
        assert sample_followup.is_responded is False

        sample_followup.responded_at = datetime.now(timezone.utc)
        assert sample_followup.is_responded is True

    def test_hours_since_session(self, sample_followup):
        """hours_since_session should calculate correctly."""
        # Sample followup has session_ended_at 1 hour ago
        hours = sample_followup.hours_since_session

        assert hours >= 0.9 and hours <= 1.1  # Approximately 1 hour


# =============================================================================
# Test: Statistics
# =============================================================================


class TestStatistics:
    """Tests for statistics tracking."""

    @pytest.mark.asyncio
    async def test_stats_tracking(self, followup_manager, mock_redis_manager, mock_user_preferences):
        """Statistics should be tracked correctly."""
        # Schedule a follow-up
        await followup_manager.schedule_followup(
            session_id="session_1",
            user_id=111,
            session_severity="high",
            session_duration_seconds=600,
        )

        # Schedule another that will be skipped (opt-out)
        mock_user_preferences.is_opted_out.return_value = True
        await followup_manager.schedule_followup(
            session_id="session_2",
            user_id=222,
            session_severity="high",
            session_duration_seconds=600,
        )

        stats = followup_manager.get_stats()

        assert stats["total_scheduled"] == 1
        assert stats["total_skipped_optout"] == 1
        assert stats["enabled"] is True

    def test_stats_structure(self, followup_manager):
        """Stats should have expected structure."""
        stats = followup_manager.get_stats()

        assert "enabled" in stats
        assert "running" in stats
        assert "delay_hours" in stats
        assert "max_hours" in stats
        assert "min_severity" in stats
        assert "min_session_minutes" in stats
        assert "total_scheduled" in stats
        assert "total_sent" in stats
        assert "total_skipped_optout" in stats
        assert "total_skipped_conditions" in stats
        assert "total_responses" in stats
        assert "response_rate" in stats


# =============================================================================
# Test: Lifecycle
# =============================================================================


class TestLifecycle:
    """Tests for manager lifecycle."""

    @pytest.mark.asyncio
    async def test_start_stop(self, followup_manager):
        """Manager should start and stop cleanly."""
        await followup_manager.start()
        assert followup_manager.is_running is True

        await followup_manager.stop()
        assert followup_manager.is_running is False

    @pytest.mark.asyncio
    async def test_start_disabled(self, mock_config_manager, mock_redis_manager, mock_user_preferences):
        """Start should be no-op when disabled."""
        mock_config_manager.get = MagicMock(side_effect=lambda section, key, default=None: {
            ("followup", "enabled"): False,
        }.get((section, key), default))

        manager = create_followup_manager(
            config_manager=mock_config_manager,
            redis_manager=mock_redis_manager,
            user_preferences_manager=mock_user_preferences,
        )

        await manager.start()
        assert manager.is_running is False


# =============================================================================
# Test: Severity Ordering
# =============================================================================


class TestSeverityOrdering:
    """Tests for severity level ordering."""

    def test_severity_order_values(self):
        """Severity order should have correct relative values."""
        assert SEVERITY_ORDER["safe"] == 0
        assert SEVERITY_ORDER["low"] == 1
        assert SEVERITY_ORDER["medium"] == 2
        assert SEVERITY_ORDER["high"] == 3
        assert SEVERITY_ORDER["critical"] == 4

    def test_severity_comparison(self):
        """Severity comparisons should work correctly."""
        assert SEVERITY_ORDER["medium"] > SEVERITY_ORDER["low"]
        assert SEVERITY_ORDER["high"] > SEVERITY_ORDER["medium"]
        assert SEVERITY_ORDER["critical"] > SEVERITY_ORDER["high"]


# =============================================================================
# Test: Dependency Injection
# =============================================================================


class TestDependencyInjection:
    """Tests for dependency injection methods."""

    def test_set_bot(self, followup_manager, mock_bot):
        """set_bot should store bot reference."""
        followup_manager.set_bot(mock_bot)
        assert followup_manager._bot is mock_bot

    def test_set_ash_managers(self, followup_manager):
        """set_ash_managers should store manager references."""
        mock_session_manager = MagicMock()
        mock_personality_manager = MagicMock()

        followup_manager.set_ash_managers(
            ash_session_manager=mock_session_manager,
            ash_personality_manager=mock_personality_manager,
        )

        assert followup_manager._ash_session_manager is mock_session_manager
        assert followup_manager._ash_personality_manager is mock_personality_manager


# =============================================================================
# Test: CHECKIN_MESSAGES
# =============================================================================


class TestCheckinMessages:
    """Tests for check-in message templates."""

    def test_message_templates_have_required_keys(self):
        """All message templates should have required keys."""
        for template in CHECKIN_MESSAGES:
            assert "greeting" in template
            assert "body" in template
            assert "closing" in template

    def test_message_templates_have_placeholders(self):
        """Templates should have expected placeholders."""
        for template in CHECKIN_MESSAGES:
            # At least one should have {name}
            has_name = "{name}" in template["greeting"]
            # Body should have {time_ago}
            has_time = "{time_ago}" in template["body"]

            # Most templates should have these
            assert has_name or has_time

    def test_message_template_count(self):
        """Should have multiple message variations."""
        assert len(CHECKIN_MESSAGES) >= 3  # At least 3 variations


# =============================================================================
# Main
# =============================================================================


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
