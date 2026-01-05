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
Phase 4 Integration Tests - Ash AI Flow
---
FILE VERSION: v5.0-4-9.0-3
LAST MODIFIED: 2026-01-04
PHASE: Phase 4 - Ash AI Integration
Repository: https://github.com/the-alphabet-cartel/ash-bot
Community: The Alphabet Cartel - https://discord.gg/alphabetcartel | https://alphabetcartel.org
============================================================================
Integration tests for complete Ash AI conversation flow:
- Session creation from alert button
- DM message routing
- Response generation
- Safety trigger detection
- Session lifecycle (timeout, end, transfer)
"""

import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

__version__ = "v5.0-4-9.0-3"


# =============================================================================
# Full Flow Integration Tests
# =============================================================================


class TestAshConversationFlow:
    """Tests for complete Ash conversation flow."""

    @pytest.mark.asyncio
    async def test_full_conversation_flow(self):
        """Test complete conversation from button click to response."""
        from src.managers.ash import (
            create_ash_session_manager,
            create_ash_personality_manager,
        )

        # Create mock config manager
        mock_config = MagicMock()
        mock_config.get.side_effect = lambda section, key, default=None: {
            ("ash", "idle_timeout_seconds"): 300,
            ("ash", "max_session_seconds"): 600,
            ("ash", "model"): "claude-sonnet-4-20250514",
            ("ash", "max_tokens"): 500,
        }.get((section, key), default)

        # Create mock Claude client
        mock_claude_client = MagicMock()
        mock_claude_client.create_message_safe = AsyncMock(
            return_value="I hear you. That sounds really difficult. Would you like to tell me more?"
        )

        # Create mock bot
        mock_bot = MagicMock()

        # Create session manager
        session_manager = create_ash_session_manager(
            config_manager=mock_config,
            bot=mock_bot,
        )

        # Create personality manager
        personality_manager = create_ash_personality_manager(
            config_manager=mock_config,
            claude_client=mock_claude_client,
        )

        # Step 1: Create mock user and start session
        mock_user = MagicMock()
        mock_user.id = 123456789
        mock_user.display_name = "TestUser"
        mock_user.create_dm = AsyncMock()
        mock_dm_channel = MagicMock()
        mock_dm_channel.send = AsyncMock()
        mock_user.create_dm.return_value = mock_dm_channel

        session = await session_manager.start_session(
            user=mock_user,
            trigger_severity="high",
        )

        assert session is not None
        assert session.user_id == 123456789
        assert session.is_active is True
        assert session.trigger_severity == "high"

        # Step 2: Get welcome message
        welcome = personality_manager.get_welcome_message(
            severity="high",
            username="TestUser",
        )

        assert "Ash" in welcome
        assert len(welcome) > 0

        # Step 3: Simulate user message
        mock_message = MagicMock()
        mock_message.content = "I'm feeling really sad today"
        mock_message.author.id = 123456789
        mock_message.author.display_name = "TestUser"

        response = await personality_manager.generate_response(
            message=mock_message,
            session=session,
        )

        assert response is not None
        assert len(response) > 0

        # Step 4: Verify Claude was called
        mock_claude_client.create_message_safe.assert_called_once()

        # Step 5: Verify session has messages
        assert len(session.messages) == 2  # User + Assistant
        assert session.messages[0]["role"] == "user"
        assert session.messages[1]["role"] == "assistant"

    @pytest.mark.asyncio
    async def test_safety_trigger_adds_resources(self):
        """Test that safety triggers add crisis resources to response."""
        from src.managers.ash import (
            create_ash_session_manager,
            create_ash_personality_manager,
        )
        from src.managers.ash.ash_session_manager import AshSession

        mock_config = MagicMock()
        mock_config.get.return_value = None

        mock_claude_client = MagicMock()
        mock_claude_client.create_message = AsyncMock(
            return_value="I'm really glad you reached out. That took courage."
        )

        personality_manager = create_ash_personality_manager(
            config_manager=mock_config,
            claude_client=mock_claude_client,
        )

        # Create mock session
        mock_session = MagicMock(spec=AshSession)
        mock_session.messages = []
        mock_session.session_id = "test_123"

        def add_message(role, content):
            mock_session.messages.append({"role": role, "content": content})

        mock_session.add_message = add_message

        # Simulate message with safety trigger
        mock_message = MagicMock()
        mock_message.content = "I don't want to live anymore"
        mock_message.author.id = 123456789
        mock_message.author.display_name = "TestUser"

        response = await personality_manager.generate_response(
            message=mock_message,
            session=mock_session,
        )

        # Response should include crisis resources
        assert "988" in response or "Crisis" in response or "Trevor" in response

    @pytest.mark.asyncio
    async def test_session_timeout_detection(self):
        """Test that idle sessions are detected as expired."""
        from src.managers.ash import create_ash_session_manager
        from src.managers.ash.ash_session_manager import AshSession

        mock_config = MagicMock()
        mock_config.get.side_effect = lambda section, key, default=None: {
            ("ash", "idle_timeout_seconds"): 300,
            ("ash", "max_session_seconds"): 600,
        }.get((section, key), default)

        mock_bot = MagicMock()

        session_manager = create_ash_session_manager(
            config_manager=mock_config,
            bot=mock_bot,
        )

        # Create mock user
        mock_user = MagicMock()
        mock_user.id = 123456789
        mock_user.create_dm = AsyncMock(return_value=MagicMock())

        session = await session_manager.start_session(
            user=mock_user,
            trigger_severity="high",
        )

        # Session should be active initially
        assert session_manager.has_active_session(123456789) is True

        # Manually set last_activity to past (simulating timeout)
        session.last_activity = datetime.now(timezone.utc) - timedelta(seconds=400)

        # Now session should be expired
        assert session_manager.has_active_session(123456789) is False

    @pytest.mark.asyncio
    async def test_max_duration_detection(self):
        """Test that sessions exceeding max duration are detected."""
        from src.managers.ash import create_ash_session_manager

        mock_config = MagicMock()
        mock_config.get.side_effect = lambda section, key, default=None: {
            ("ash", "idle_timeout_seconds"): 300,
            ("ash", "max_session_seconds"): 600,
        }.get((section, key), default)

        mock_bot = MagicMock()

        session_manager = create_ash_session_manager(
            config_manager=mock_config,
            bot=mock_bot,
        )

        mock_user = MagicMock()
        mock_user.id = 123456789
        mock_user.create_dm = AsyncMock(return_value=MagicMock())

        session = await session_manager.start_session(
            user=mock_user,
            trigger_severity="high",
        )

        # Manually set started_at to past (simulating max duration)
        session.started_at = datetime.now(timezone.utc) - timedelta(seconds=700)
        # Keep activity recent
        session.last_activity = datetime.now(timezone.utc)

        # Session should be expired due to max duration
        assert session_manager.has_active_session(123456789) is False

    @pytest.mark.asyncio
    async def test_duplicate_session_prevention(self):
        """Test that duplicate sessions are prevented."""
        from src.managers.ash import (
            create_ash_session_manager,
            SessionExistsError,
        )

        mock_config = MagicMock()
        mock_config.get.return_value = 300

        mock_bot = MagicMock()

        session_manager = create_ash_session_manager(
            config_manager=mock_config,
            bot=mock_bot,
        )

        mock_user = MagicMock()
        mock_user.id = 123456789
        mock_user.create_dm = AsyncMock(return_value=MagicMock())

        # First session should succeed
        await session_manager.start_session(
            user=mock_user,
            trigger_severity="high",
        )

        # Second session should raise
        with pytest.raises(SessionExistsError):
            await session_manager.start_session(
                user=mock_user,
                trigger_severity="high",
            )


class TestEndRequestDetection:
    """Tests for conversation end request detection."""

    def test_detect_goodbye(self):
        """Test detection of goodbye phrases."""
        from src.managers.ash import create_ash_personality_manager

        mock_config = MagicMock()
        mock_config.get.return_value = None

        mock_claude = MagicMock()

        personality_manager = create_ash_personality_manager(
            config_manager=mock_config,
            claude_client=mock_claude,
        )

        # Should detect end requests
        assert personality_manager.detect_end_request("goodbye") is True
        assert personality_manager.detect_end_request("bye ash") is True
        assert personality_manager.detect_end_request("I'm done talking") is True
        assert personality_manager.detect_end_request("end conversation") is True

        # Should not detect false positives
        assert personality_manager.detect_end_request("hello") is False
        assert personality_manager.detect_end_request("I feel sad") is False

    def test_detect_crt_request(self):
        """Test detection of CRT transfer requests."""
        from src.managers.ash import create_ash_personality_manager

        mock_config = MagicMock()
        mock_config.get.return_value = None

        mock_claude = MagicMock()

        personality_manager = create_ash_personality_manager(
            config_manager=mock_config,
            claude_client=mock_claude,
        )

        # Should detect CRT requests
        assert personality_manager.detect_crt_request("can I talk to a real person") is True
        assert personality_manager.detect_crt_request("I want a human") is True
        assert personality_manager.detect_crt_request("connect me to CRT") is True

        # Should not detect false positives
        assert personality_manager.detect_crt_request("I feel lonely") is False
        assert personality_manager.detect_crt_request("hello") is False


class TestSafetyTriggerDetection:
    """Tests for safety trigger detection."""

    def test_detect_safety_triggers(self):
        """Test detection of various safety trigger phrases."""
        from src.managers.ash import create_ash_personality_manager

        mock_config = MagicMock()
        mock_config.get.return_value = None

        mock_claude = MagicMock()

        personality_manager = create_ash_personality_manager(
            config_manager=mock_config,
            claude_client=mock_claude,
        )

        # Should detect safety triggers
        safety_phrases = [
            "I want to kill myself",
            "I don't want to live anymore",
            "I'm going to end my life",
            "I'd be better off dead",
            "I have a plan to hurt myself",
        ]

        for phrase in safety_phrases:
            assert personality_manager._check_safety_triggers(phrase) is True, f"Should detect: {phrase}"

        # Should not trigger on normal phrases
        safe_phrases = [
            "I feel sad today",
            "I'm having a hard time",
            "Work is killing me (metaphorically)",
            "I'm stressed out",
        ]

        for phrase in safe_phrases:
            assert personality_manager._check_safety_triggers(phrase) is False, f"Should not trigger: {phrase}"


class TestSessionCleanup:
    """Tests for session cleanup functionality."""

    @pytest.mark.asyncio
    async def test_cleanup_expired_sessions(self):
        """Test batch cleanup of expired sessions."""
        from src.managers.ash import create_ash_session_manager

        mock_config = MagicMock()
        mock_config.get.side_effect = lambda section, key, default=None: {
            ("ash", "idle_timeout_seconds"): 300,
            ("ash", "max_session_seconds"): 600,
        }.get((section, key), default)

        mock_bot = MagicMock()

        session_manager = create_ash_session_manager(
            config_manager=mock_config,
            bot=mock_bot,
        )

        # Create multiple sessions
        for user_id in [111, 222, 333]:
            mock_user = MagicMock()
            mock_user.id = user_id
            mock_dm = MagicMock()
            mock_dm.send = AsyncMock()
            mock_user.create_dm = AsyncMock(return_value=mock_dm)

            await session_manager.start_session(
                user=mock_user,
                trigger_severity="high",
            )

        # Make some sessions expired
        session_manager._sessions[111].last_activity = (
            datetime.now(timezone.utc) - timedelta(seconds=400)
        )
        session_manager._sessions[222].started_at = (
            datetime.now(timezone.utc) - timedelta(seconds=700)
        )
        # Session 333 stays active

        # Run cleanup
        cleaned = await session_manager.cleanup_expired_sessions()

        # Two sessions should be cleaned
        assert cleaned == 2

        # Only session 333 should remain active
        assert session_manager.has_active_session(333) is True
        assert session_manager.active_session_count == 1


class TestWelcomeMessages:
    """Tests for welcome message generation."""

    def test_critical_welcome_message(self):
        """Test welcome message for CRITICAL severity."""
        from src.managers.ash import create_ash_personality_manager

        mock_config = MagicMock()
        mock_claude = MagicMock()

        personality_manager = create_ash_personality_manager(
            config_manager=mock_config,
            claude_client=mock_claude,
        )

        welcome = personality_manager.get_welcome_message(
            severity="critical",
            username="Alex",
        )

        assert "Ash" in welcome
        assert "Alex" in welcome
        # Critical should mention things being hard
        assert "hard" in welcome.lower() or "difficult" in welcome.lower()

    def test_high_welcome_message(self):
        """Test welcome message for HIGH severity."""
        from src.managers.ash import create_ash_personality_manager

        mock_config = MagicMock()
        mock_claude = MagicMock()

        personality_manager = create_ash_personality_manager(
            config_manager=mock_config,
            claude_client=mock_claude,
        )

        welcome = personality_manager.get_welcome_message(
            severity="high",
            username="Jordan",
        )

        assert "Ash" in welcome
        assert "Jordan" in welcome


class TestHandoffMessages:
    """Tests for CRT handoff messages."""

    def test_handoff_message(self):
        """Test CRT handoff message."""
        from src.managers.ash import create_ash_personality_manager

        mock_config = MagicMock()
        mock_claude = MagicMock()

        personality_manager = create_ash_personality_manager(
            config_manager=mock_config,
            claude_client=mock_claude,
        )

        handoff = personality_manager.get_handoff_message()

        assert "Crisis Response Team" in handoff or "CRT" in handoff
        assert "human" in handoff.lower() or "people" in handoff.lower()


class TestClaudeClientErrors:
    """Tests for Claude API error handling."""

    @pytest.mark.asyncio
    async def test_api_error_returns_fallback(self):
        """Test that API errors return fallback response."""
        from src.managers.ash import create_ash_personality_manager
        from src.managers.ash.ash_session_manager import AshSession

        mock_config = MagicMock()
        mock_config.get.return_value = None

        mock_claude_client = MagicMock()
        mock_claude_client.create_message = AsyncMock(
            side_effect=Exception("API Error")
        )

        personality_manager = create_ash_personality_manager(
            config_manager=mock_config,
            claude_client=mock_claude_client,
        )

        mock_session = MagicMock(spec=AshSession)
        mock_session.messages = []
        mock_session.session_id = "test_123"
        mock_session.add_message = lambda role, content: mock_session.messages.append(
            {"role": role, "content": content}
        )

        mock_message = MagicMock()
        mock_message.content = "hello"
        mock_message.author.id = 123
        mock_message.author.display_name = "Test"

        # Should not raise, should return fallback
        response = await personality_manager.generate_response(
            message=mock_message,
            session=mock_session,
        )

        assert response is not None
        assert len(response) > 0
        # Fallback should mention being here or CRT
        assert "here" in response.lower() or "CRT" in response or "Crisis" in response
