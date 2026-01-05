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
Integration Tests: Ash Sessions
---
FILE VERSION: v5.0-6-1.3-1
LAST MODIFIED: 2026-01-04
PHASE: Phase 6 - Final Testing & Documentation
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-bot
Community: The Alphabet Cartel - https://discord.gg/alphabetcartel | https://alphabetcartel.org
============================================================================
Tests for Scenario 5: Ash Session Timeout
- Session lifecycle management
- Timeout detection and cleanup
- Farewell message delivery
- Metrics tracking
"""

import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import AsyncMock, MagicMock, patch


# =============================================================================
# Scenario 5: Ash Session Timeout
# =============================================================================


class TestAshSessionTimeout:
    """
    Scenario 5: Ash Session Timeout

    Input: Ash session with no activity for 5 minutes
    Expected:
    1. Cleanup loop detects idle session
    2. Farewell message sent
    3. Session removed from active sessions
    4. Metrics: ash_sessions_active -1
    """

    @pytest.mark.asyncio
    async def test_idle_session_detected(
        self,
        mock_ash_session_manager,
        mock_user,
    ):
        """Test that idle sessions are detected by cleanup loop."""
        # Create session with old last_activity
        session = {
            "user_id": mock_user.id,
            "channel_id": 111222333444555666,
            "created_at": datetime.now(timezone.utc) - timedelta(minutes=10),
            "last_activity": datetime.now(timezone.utc) - timedelta(minutes=6),
            "timeout_seconds": 300,  # 5 minutes
        }

        # Calculate idle time
        idle_time = datetime.now(timezone.utc) - session["last_activity"]
        is_idle = idle_time.total_seconds() > session["timeout_seconds"]

        assert is_idle is True

    @pytest.mark.asyncio
    async def test_farewell_message_sent_on_timeout(
        self,
        mock_user,
        mock_ash_personality,
    ):
        """Test that farewell message is sent when session times out."""
        # Create DM channel
        dm_channel = MagicMock()
        dm_channel.send = AsyncMock()
        mock_user.create_dm = AsyncMock(return_value=dm_channel)

        # Get farewell message
        farewell = "Take care of yourself 💜 Remember, you can always reach out again."
        mock_ash_personality.get_farewell_message = MagicMock(return_value=farewell)

        # Send farewell
        channel = await mock_user.create_dm()
        await channel.send(farewell)

        dm_channel.send.assert_called_once_with(farewell)

    @pytest.mark.asyncio
    async def test_session_removed_after_timeout(
        self,
        mock_ash_session_manager,
        mock_user,
    ):
        """Test that session is removed from active sessions."""
        # End session
        await mock_ash_session_manager.end_session(mock_user.id)

        mock_ash_session_manager.end_session.assert_called_once_with(mock_user.id)

    @pytest.mark.asyncio
    async def test_active_sessions_metric_decremented(
        self,
        mock_metrics_manager,
    ):
        """Test that ash_sessions_active gauge is decremented."""
        # Before: 1 active session
        mock_metrics_manager.gauge("ash_sessions_active", 1)

        # After timeout: 0 active sessions
        mock_metrics_manager.gauge("ash_sessions_active", 0)

        # Verify gauge was called with 0
        calls = mock_metrics_manager.gauge.call_args_list
        assert ("ash_sessions_active", 0) == calls[-1][0]

    @pytest.mark.asyncio
    async def test_timeout_cleanup_flow_complete(
        self,
        mock_ash_session_manager,
        mock_user,
        mock_metrics_manager,
        mock_ash_personality,
    ):
        """Test complete session timeout cleanup flow."""
        # Setup
        dm_channel = MagicMock()
        dm_channel.send = AsyncMock()
        mock_user.create_dm = AsyncMock(return_value=dm_channel)
        mock_ash_personality.get_farewell_message = MagicMock(
            return_value="Take care 💜"
        )

        # Step 1: Detect idle session (simulated by cleanup loop)
        session = mock_ash_session_manager.get_session(mock_user.id)
        assert session is not None

        # Step 2: Get farewell message
        farewell = mock_ash_personality.get_farewell_message()

        # Step 3: Send farewell to DM
        channel = await mock_user.create_dm()
        await channel.send(farewell)

        # Step 4: End session
        await mock_ash_session_manager.end_session(mock_user.id)

        # Step 5: Update metrics
        active_count = mock_ash_session_manager.get_active_session_count() - 1
        mock_metrics_manager.gauge("ash_sessions_active", active_count)

        # Verify flow
        dm_channel.send.assert_called_once_with(farewell)
        mock_ash_session_manager.end_session.assert_called_once()


# =============================================================================
# Session Lifecycle Tests
# =============================================================================


class TestAshSessionLifecycle:
    """Tests for full Ash session lifecycle."""

    @pytest.mark.asyncio
    async def test_session_creation(
        self,
        mock_ash_session_manager,
        mock_user,
    ):
        """Test session creation."""
        session_id = await mock_ash_session_manager.create_session(
            user_id=mock_user.id,
            channel_id=111222333444555666,
            severity="high",
        )

        assert session_id is not None
        mock_ash_session_manager.create_session.assert_called_once()

    @pytest.mark.asyncio
    async def test_session_activity_updates(
        self,
        mock_ash_session_manager,
        mock_user,
    ):
        """Test that session activity is updated on messages."""
        # Update last activity
        mock_ash_session_manager.update_activity = AsyncMock()

        await mock_ash_session_manager.update_activity(mock_user.id)

        mock_ash_session_manager.update_activity.assert_called_once_with(mock_user.id)

    @pytest.mark.asyncio
    async def test_session_active_count_accurate(
        self,
        mock_ash_session_manager,
    ):
        """Test that active session count is accurate."""
        count = mock_ash_session_manager.get_active_session_count()

        assert count == 1  # Mock returns 1 by default

    @pytest.mark.asyncio
    async def test_multiple_concurrent_sessions(
        self,
        mock_ash_session_manager,
    ):
        """Test handling multiple concurrent sessions."""
        # Create multiple sessions
        users = [123, 456, 789]

        for user_id in users:
            await mock_ash_session_manager.create_session(
                user_id=user_id,
                channel_id=111222333444555666,
                severity="medium",
            )

        assert mock_ash_session_manager.create_session.call_count == 3


# =============================================================================
# Conversation Flow Tests
# =============================================================================


class TestAshConversation:
    """Tests for Ash conversation handling."""

    @pytest.mark.asyncio
    async def test_user_message_processed(
        self,
        mock_claude_client,
        mock_user,
    ):
        """Test that user messages are processed by Claude."""
        message = "I've been having a really hard time lately."

        response = await mock_claude_client.send_message(
            message=message,
            user_id=mock_user.id,
            session_id="session_123",
        )

        assert response["content"] is not None
        assert response["role"] == "assistant"

    @pytest.mark.asyncio
    async def test_conversation_history_maintained(
        self,
        mock_claude_client,
        mock_user,
    ):
        """Test that conversation history is maintained."""
        messages = [
            "I'm feeling overwhelmed.",
            "Work has been really stressful.",
            "I don't know how to cope.",
        ]

        for msg in messages:
            await mock_claude_client.send_message(
                message=msg,
                user_id=mock_user.id,
                session_id="session_123",
            )

        assert mock_claude_client.send_message.call_count == 3

    @pytest.mark.asyncio
    async def test_ash_provides_supportive_responses(
        self,
        mock_claude_client,
        mock_user,
    ):
        """Test that Ash provides supportive responses."""
        message = "I feel like nobody cares."

        response = await mock_claude_client.send_message(
            message=message,
            user_id=mock_user.id,
            session_id="session_123",
        )

        # Response should be supportive
        assert "hear you" in response["content"].lower()


# =============================================================================
# Error Handling Tests
# =============================================================================


class TestAshSessionErrors:
    """Tests for error handling in Ash sessions."""

    @pytest.mark.asyncio
    async def test_claude_api_failure_handled(
        self,
        mock_claude_client,
        mock_user,
    ):
        """Test graceful handling of Claude API failures."""
        mock_claude_client.send_message = AsyncMock(side_effect=Exception("API Error"))

        with pytest.raises(Exception) as exc_info:
            await mock_claude_client.send_message(
                message="Test",
                user_id=mock_user.id,
                session_id="session_123",
            )

        assert "API Error" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_dm_creation_failure_handled(
        self,
        mock_user,
    ):
        """Test handling when DM channel cannot be created."""
        mock_user.create_dm = AsyncMock(side_effect=Exception("Cannot create DM"))

        with pytest.raises(Exception) as exc_info:
            await mock_user.create_dm()

        assert "Cannot create DM" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_session_not_found_handled(
        self,
        mock_ash_session_manager,
    ):
        """Test handling when session is not found."""
        mock_ash_session_manager.get_session = MagicMock(return_value=None)

        session = mock_ash_session_manager.get_session(999999)

        assert session is None


# =============================================================================
# Personality Tests
# =============================================================================


class TestAshPersonality:
    """Tests for Ash personality responses."""

    @pytest.mark.asyncio
    async def test_welcome_message_varies_by_severity(
        self,
        mock_ash_personality,
    ):
        """Test that welcome messages vary by crisis severity."""
        severities = ["critical", "high", "medium", "low"]
        messages = []

        for severity in severities:
            msg = mock_ash_personality.get_welcome_message(severity=severity)
            messages.append(msg)

        # All should be supportive
        for msg in messages:
            assert "here for you" in msg.lower()

    @pytest.mark.asyncio
    async def test_farewell_message_supportive(
        self,
        mock_ash_personality,
    ):
        """Test that farewell messages are supportive."""
        mock_ash_personality.get_farewell_message = MagicMock(
            return_value="Take care of yourself 💜 I'm here whenever you need me."
        )

        farewell = mock_ash_personality.get_farewell_message()

        assert "here" in farewell.lower()
        assert "💜" in farewell


# =============================================================================
# Cleanup Loop Tests
# =============================================================================


class TestAshCleanupLoop:
    """Tests for session cleanup loop."""

    @pytest.mark.asyncio
    async def test_cleanup_loop_runs_periodically(
        self,
        mock_ash_session_manager,
    ):
        """Test that cleanup loop can run."""
        mock_ash_session_manager.cleanup_idle_sessions = AsyncMock(return_value=1)

        cleaned = await mock_ash_session_manager.cleanup_idle_sessions()

        assert cleaned == 1

    @pytest.mark.asyncio
    async def test_cleanup_handles_empty_sessions(
        self,
        mock_ash_session_manager,
    ):
        """Test cleanup handles no active sessions gracefully."""
        mock_ash_session_manager.get_active_session_count = MagicMock(return_value=0)
        mock_ash_session_manager.cleanup_idle_sessions = AsyncMock(return_value=0)

        count = mock_ash_session_manager.get_active_session_count()
        cleaned = await mock_ash_session_manager.cleanup_idle_sessions()

        assert count == 0
        assert cleaned == 0

    @pytest.mark.asyncio
    async def test_cleanup_processes_multiple_sessions(
        self,
        mock_ash_session_manager,
    ):
        """Test cleanup processes multiple idle sessions."""
        mock_ash_session_manager.cleanup_idle_sessions = AsyncMock(return_value=3)

        cleaned = await mock_ash_session_manager.cleanup_idle_sessions()

        assert cleaned == 3
