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
Ash Personality Manager Tests for Ash-Bot Service
---
FILE VERSION: v5.0-4-5.0-1
LAST MODIFIED: 2026-01-04
PHASE: Phase 4 - Ash AI Integration
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-bot
Community: The Alphabet Cartel - https://discord.gg/alphabetcartel | https://alphabetcartel.org
============================================================================
Test suite for AshPersonalityManager.

USAGE:
    pytest tests/test_ash/test_ash_personality.py -v
"""

import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def mock_config_manager():
    """Create mock ConfigManager."""
    config = MagicMock()
    return config


@pytest.fixture
def mock_claude_client():
    """Create mock ClaudeClientManager."""
    client = MagicMock()
    client.create_message_safe = AsyncMock(
        return_value="I hear you. That sounds really difficult."
    )
    client.get_stats.return_value = {
        "model": "claude-sonnet-4-20250514",
        "request_count": 1,
        "error_count": 0,
    }
    return client


@pytest.fixture
def mock_session():
    """Create mock AshSession."""
    from src.managers.ash.ash_session_manager import AshSession

    dm_channel = MagicMock()
    dm_channel.send = AsyncMock()

    session = AshSession(
        session_id="test123",
        user_id=123456789,
        dm_channel=dm_channel,
        started_at=datetime.now(timezone.utc),
        last_activity=datetime.now(timezone.utc),
        trigger_severity="high",
    )

    return session


@pytest.fixture
def mock_message():
    """Create mock Discord message."""
    message = MagicMock()
    message.content = "I'm feeling really sad today."
    message.author = MagicMock()
    message.author.id = 123456789
    message.author.display_name = "TestUser"
    return message


# =============================================================================
# Initialization Tests
# =============================================================================


class TestAshPersonalityManagerInit:
    """Tests for AshPersonalityManager initialization."""

    def test_init_success(self, mock_config_manager, mock_claude_client):
        """Test successful initialization."""
        from src.managers.ash.ash_personality_manager import AshPersonalityManager

        manager = AshPersonalityManager(
            config_manager=mock_config_manager,
            claude_client=mock_claude_client,
        )

        assert manager.responses_generated == 0
        assert manager.safety_triggers_detected == 0

    def test_factory_function(self, mock_config_manager, mock_claude_client):
        """Test factory function creates manager."""
        from src.managers.ash.ash_personality_manager import (
            create_ash_personality_manager,
        )

        manager = create_ash_personality_manager(
            config_manager=mock_config_manager,
            claude_client=mock_claude_client,
        )

        assert manager is not None


# =============================================================================
# Response Generation Tests
# =============================================================================


class TestAshResponseGeneration:
    """Tests for response generation."""

    @pytest.mark.asyncio
    async def test_generate_response_success(
        self, mock_config_manager, mock_claude_client, mock_session, mock_message
    ):
        """Test successful response generation."""
        from src.managers.ash.ash_personality_manager import AshPersonalityManager

        manager = AshPersonalityManager(
            config_manager=mock_config_manager,
            claude_client=mock_claude_client,
        )

        response = await manager.generate_response(
            message=mock_message,
            session=mock_session,
        )

        assert response == "I hear you. That sounds really difficult."
        assert manager.responses_generated == 1
        assert len(mock_session.messages) == 2  # user + assistant
        mock_claude_client.create_message_safe.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_response_adds_to_history(
        self, mock_config_manager, mock_claude_client, mock_session, mock_message
    ):
        """Test response adds messages to session history."""
        from src.managers.ash.ash_personality_manager import AshPersonalityManager

        manager = AshPersonalityManager(
            config_manager=mock_config_manager,
            claude_client=mock_claude_client,
        )

        await manager.generate_response(
            message=mock_message,
            session=mock_session,
        )

        # Check history
        assert mock_session.messages[0]["role"] == "user"
        assert mock_session.messages[0]["content"] == mock_message.content
        assert mock_session.messages[1]["role"] == "assistant"

    @pytest.mark.asyncio
    async def test_generate_response_from_text(
        self, mock_config_manager, mock_claude_client, mock_session
    ):
        """Test response generation from raw text."""
        from src.managers.ash.ash_personality_manager import AshPersonalityManager

        manager = AshPersonalityManager(
            config_manager=mock_config_manager,
            claude_client=mock_claude_client,
        )

        response = await manager.generate_response_from_text(
            text="Test message",
            session=mock_session,
        )

        assert response is not None
        assert manager.responses_generated == 1


# =============================================================================
# Safety Trigger Tests
# =============================================================================


class TestAshSafetyTriggers:
    """Tests for safety trigger detection."""

    def test_check_safety_triggers_no_match(
        self, mock_config_manager, mock_claude_client
    ):
        """Test no safety triggers in normal message."""
        from src.managers.ash.ash_personality_manager import AshPersonalityManager

        manager = AshPersonalityManager(
            config_manager=mock_config_manager,
            claude_client=mock_claude_client,
        )

        has_triggers, matched = manager.check_safety_triggers(
            "I'm having a bad day at work."
        )

        assert has_triggers is False
        assert matched == []

    def test_check_safety_triggers_suicide(
        self, mock_config_manager, mock_claude_client
    ):
        """Test suicide trigger detection."""
        from src.managers.ash.ash_personality_manager import AshPersonalityManager

        manager = AshPersonalityManager(
            config_manager=mock_config_manager,
            claude_client=mock_claude_client,
        )

        has_triggers, matched = manager.check_safety_triggers(
            "I've been thinking about suicide."
        )

        assert has_triggers is True
        assert "suicide" in matched

    def test_check_safety_triggers_kill_myself(
        self, mock_config_manager, mock_claude_client
    ):
        """Test 'kill myself' trigger detection."""
        from src.managers.ash.ash_personality_manager import AshPersonalityManager

        manager = AshPersonalityManager(
            config_manager=mock_config_manager,
            claude_client=mock_claude_client,
        )

        has_triggers, matched = manager.check_safety_triggers(
            "I want to kill myself."
        )

        assert has_triggers is True
        assert "kill myself" in matched

    def test_check_safety_triggers_self_harm(
        self, mock_config_manager, mock_claude_client
    ):
        """Test self-harm trigger detection."""
        from src.managers.ash.ash_personality_manager import AshPersonalityManager

        manager = AshPersonalityManager(
            config_manager=mock_config_manager,
            claude_client=mock_claude_client,
        )

        has_triggers, matched = manager.check_safety_triggers(
            "I've been cutting again."
        )

        assert has_triggers is True
        assert "cutting" in matched

    def test_check_safety_triggers_case_insensitive(
        self, mock_config_manager, mock_claude_client
    ):
        """Test trigger detection is case insensitive."""
        from src.managers.ash.ash_personality_manager import AshPersonalityManager

        manager = AshPersonalityManager(
            config_manager=mock_config_manager,
            claude_client=mock_claude_client,
        )

        has_triggers, matched = manager.check_safety_triggers(
            "SUICIDE is something I think about."
        )

        assert has_triggers is True

    @pytest.mark.asyncio
    async def test_response_includes_resources_on_trigger(
        self, mock_config_manager, mock_claude_client, mock_session, mock_message
    ):
        """Test crisis resources are appended when trigger detected."""
        from src.managers.ash.ash_personality_manager import AshPersonalityManager

        manager = AshPersonalityManager(
            config_manager=mock_config_manager,
            claude_client=mock_claude_client,
        )

        # Set message with trigger
        mock_message.content = "I've been thinking about suicide."

        response = await manager.generate_response(
            message=mock_message,
            session=mock_session,
        )

        # Response should include crisis resources
        assert "988" in response
        assert "Trevor Project" in response
        assert manager.safety_triggers_detected == 1


# =============================================================================
# Welcome Message Tests
# =============================================================================


class TestAshWelcomeMessages:
    """Tests for welcome message generation."""

    def test_welcome_message_critical(self, mock_config_manager, mock_claude_client):
        """Test critical severity welcome message."""
        from src.managers.ash.ash_personality_manager import AshPersonalityManager

        manager = AshPersonalityManager(
            config_manager=mock_config_manager,
            claude_client=mock_claude_client,
        )

        message = manager.get_welcome_message("critical")

        assert "Ash" in message
        assert "hard right now" in message
        assert "💙" in message

    def test_welcome_message_high(self, mock_config_manager, mock_claude_client):
        """Test high severity welcome message."""
        from src.managers.ash.ash_personality_manager import AshPersonalityManager

        manager = AshPersonalityManager(
            config_manager=mock_config_manager,
            claude_client=mock_claude_client,
        )

        message = manager.get_welcome_message("high")

        assert "Ash" in message
        assert "Crisis Response Team" in message

    def test_welcome_message_with_username(
        self, mock_config_manager, mock_claude_client
    ):
        """Test welcome message with username."""
        from src.managers.ash.ash_personality_manager import AshPersonalityManager

        manager = AshPersonalityManager(
            config_manager=mock_config_manager,
            claude_client=mock_claude_client,
        )

        message = manager.get_welcome_message("high", username="Alex")

        assert "Alex" in message


# =============================================================================
# Closing Message Tests
# =============================================================================


class TestAshClosingMessages:
    """Tests for closing message generation."""

    def test_closing_message_ended(self, mock_config_manager, mock_claude_client):
        """Test 'ended' closing message."""
        from src.managers.ash.ash_personality_manager import AshPersonalityManager

        manager = AshPersonalityManager(
            config_manager=mock_config_manager,
            claude_client=mock_claude_client,
        )

        message = manager.get_closing_message("ended")

        assert "Take care" in message
        assert "💙" in message

    def test_closing_message_timeout(self, mock_config_manager, mock_claude_client):
        """Test timeout closing message."""
        from src.managers.ash.ash_personality_manager import AshPersonalityManager

        manager = AshPersonalityManager(
            config_manager=mock_config_manager,
            claude_client=mock_claude_client,
        )

        message = manager.get_closing_message("timeout")

        assert "haven't heard" in message

    def test_closing_message_transfer(self, mock_config_manager, mock_claude_client):
        """Test transfer closing message."""
        from src.managers.ash.ash_personality_manager import AshPersonalityManager

        manager = AshPersonalityManager(
            config_manager=mock_config_manager,
            claude_client=mock_claude_client,
        )

        message = manager.get_closing_message("transfer")

        assert "Crisis Response Team" in message


# =============================================================================
# Special Message Tests
# =============================================================================


class TestAshSpecialMessages:
    """Tests for special messages (handoff, CRT arrival)."""

    def test_handoff_message(self, mock_config_manager, mock_claude_client):
        """Test handoff message."""
        from src.managers.ash.ash_personality_manager import AshPersonalityManager

        manager = AshPersonalityManager(
            config_manager=mock_config_manager,
            claude_client=mock_claude_client,
        )

        message = manager.get_handoff_message()

        assert "Crisis Response Team" in message
        assert "real people" in message

    def test_crt_arrival_message(self, mock_config_manager, mock_claude_client):
        """Test CRT arrival message."""
        from src.managers.ash.ash_personality_manager import AshPersonalityManager

        manager = AshPersonalityManager(
            config_manager=mock_config_manager,
            claude_client=mock_claude_client,
        )

        message = manager.get_crt_arrival_message()

        assert "Crisis Response Team" in message
        assert "good hands" in message


# =============================================================================
# End Request Detection Tests
# =============================================================================


class TestAshEndRequestDetection:
    """Tests for end conversation request detection."""

    def test_detect_end_bye(self, mock_config_manager, mock_claude_client):
        """Test 'bye' detection."""
        from src.managers.ash.ash_personality_manager import AshPersonalityManager

        manager = AshPersonalityManager(
            config_manager=mock_config_manager,
            claude_client=mock_claude_client,
        )

        assert manager.detect_end_request("bye") is True
        assert manager.detect_end_request("Bye") is True
        assert manager.detect_end_request("goodbye") is True

    def test_detect_end_done(self, mock_config_manager, mock_claude_client):
        """Test 'done' variations detection."""
        from src.managers.ash.ash_personality_manager import AshPersonalityManager

        manager = AshPersonalityManager(
            config_manager=mock_config_manager,
            claude_client=mock_claude_client,
        )

        assert manager.detect_end_request("i'm done") is True
        assert manager.detect_end_request("im done") is True
        assert manager.detect_end_request("I am done") is True

    def test_detect_end_feeling_better(self, mock_config_manager, mock_claude_client):
        """Test feeling better detection."""
        from src.managers.ash.ash_personality_manager import AshPersonalityManager

        manager = AshPersonalityManager(
            config_manager=mock_config_manager,
            claude_client=mock_claude_client,
        )

        assert manager.detect_end_request("i feel better") is True
        assert manager.detect_end_request("feeling better now") is True

    def test_no_false_positive_end(self, mock_config_manager, mock_claude_client):
        """Test no false positive end detection."""
        from src.managers.ash.ash_personality_manager import AshPersonalityManager

        manager = AshPersonalityManager(
            config_manager=mock_config_manager,
            claude_client=mock_claude_client,
        )

        # These should NOT trigger end
        assert manager.detect_end_request("I said bye to my friend") is False
        assert manager.detect_end_request("I'm not done yet") is False


# =============================================================================
# CRT Request Detection Tests
# =============================================================================


class TestAshCRTRequestDetection:
    """Tests for CRT/human request detection."""

    def test_detect_crt_human(self, mock_config_manager, mock_claude_client):
        """Test human request detection."""
        from src.managers.ash.ash_personality_manager import AshPersonalityManager

        manager = AshPersonalityManager(
            config_manager=mock_config_manager,
            claude_client=mock_claude_client,
        )

        assert manager.detect_crt_request("Can I talk to a human?") is True
        assert manager.detect_crt_request("I want a real person") is True

    def test_detect_crt_team(self, mock_config_manager, mock_claude_client):
        """Test CRT team request detection."""
        from src.managers.ash.ash_personality_manager import AshPersonalityManager

        manager = AshPersonalityManager(
            config_manager=mock_config_manager,
            claude_client=mock_claude_client,
        )

        assert manager.detect_crt_request("Can the CRT help?") is True
        assert manager.detect_crt_request("crisis response team please") is True

    def test_detect_crt_bot_question(self, mock_config_manager, mock_claude_client):
        """Test bot question detection."""
        from src.managers.ash.ash_personality_manager import AshPersonalityManager

        manager = AshPersonalityManager(
            config_manager=mock_config_manager,
            claude_client=mock_claude_client,
        )

        assert manager.detect_crt_request("Are you a bot?") is True
        assert manager.detect_crt_request("are you real") is True

    def test_no_false_positive_crt(self, mock_config_manager, mock_claude_client):
        """Test no false positive CRT detection."""
        from src.managers.ash.ash_personality_manager import AshPersonalityManager

        manager = AshPersonalityManager(
            config_manager=mock_config_manager,
            claude_client=mock_claude_client,
        )

        # These should NOT trigger CRT
        assert manager.detect_crt_request("I talked to my friend") is False
        assert manager.detect_crt_request("Hello, how are you?") is False


# =============================================================================
# Statistics Tests
# =============================================================================


class TestAshPersonalityStatistics:
    """Tests for statistics tracking."""

    @pytest.mark.asyncio
    async def test_stats_increment(
        self, mock_config_manager, mock_claude_client, mock_session, mock_message
    ):
        """Test statistics increment on response."""
        from src.managers.ash.ash_personality_manager import AshPersonalityManager

        manager = AshPersonalityManager(
            config_manager=mock_config_manager,
            claude_client=mock_claude_client,
        )

        await manager.generate_response(mock_message, mock_session)
        await manager.generate_response(mock_message, mock_session)

        assert manager.responses_generated == 2

    def test_get_stats(self, mock_config_manager, mock_claude_client):
        """Test get_stats returns correct data."""
        from src.managers.ash.ash_personality_manager import AshPersonalityManager

        manager = AshPersonalityManager(
            config_manager=mock_config_manager,
            claude_client=mock_claude_client,
        )

        stats = manager.get_stats()

        assert "responses_generated" in stats
        assert "safety_triggers_detected" in stats
        assert "claude_stats" in stats

    def test_repr(self, mock_config_manager, mock_claude_client):
        """Test string representation."""
        from src.managers.ash.ash_personality_manager import AshPersonalityManager

        manager = AshPersonalityManager(
            config_manager=mock_config_manager,
            claude_client=mock_claude_client,
        )

        repr_str = repr(manager)

        assert "AshPersonalityManager" in repr_str
        assert "responses=0" in repr_str
