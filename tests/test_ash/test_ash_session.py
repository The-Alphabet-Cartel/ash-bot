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
Ash Session Manager Tests for Ash-Bot Service
---
FILE VERSION: v5.0-4-4.0-2
LAST MODIFIED: 2026-01-04
PHASE: Phase 4 - Ash AI Integration
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-bot
Community: The Alphabet Cartel - https://discord.gg/alphabetcartel | https://alphabetcartel.org
============================================================================
Test suite for AshSessionManager.

USAGE:
    pytest tests/test_ash/test_ash_session.py -v
"""

import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import AsyncMock, MagicMock, patch


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def mock_config_manager():
    """Create mock ConfigManager with session settings."""
    config = MagicMock()
    config.get.side_effect = lambda section, key, default=None: {
        ("ash", "session_timeout_seconds"): 300,
        ("ash", "max_session_duration_seconds"): 600,
    }.get((section, key), default)
    return config


@pytest.fixture
def mock_config_manager_short_timeout():
    """Create mock ConfigManager with short timeouts for testing."""
    config = MagicMock()
    config.get.side_effect = lambda section, key, default=None: {
        ("ash", "session_timeout_seconds"): 5,  # 5 seconds
        ("ash", "max_session_duration_seconds"): 10,  # 10 seconds
    }.get((section, key), default)
    return config


@pytest.fixture
def mock_bot():
    """Create mock Discord bot."""
    bot = MagicMock()
    return bot


@pytest.fixture
def mock_user():
    """Create mock Discord user."""
    user = MagicMock()
    user.id = 123456789
    user.display_name = "TestUser"

    # Mock DM channel creation
    dm_channel = MagicMock()
    dm_channel.send = AsyncMock()
    user.create_dm = AsyncMock(return_value=dm_channel)

    return user


@pytest.fixture
def mock_user_2():
    """Create second mock Discord user."""
    user = MagicMock()
    user.id = 987654321
    user.display_name = "TestUser2"

    dm_channel = MagicMock()
    dm_channel.send = AsyncMock()
    user.create_dm = AsyncMock(return_value=dm_channel)

    return user


# =============================================================================
# AshSession Tests
# =============================================================================


class TestAshSession:
    """Tests for AshSession dataclass."""

    def test_session_creation(self):
        """Test AshSession can be created with required fields."""
        from src.managers.ash.ash_session_manager import AshSession

        dm_channel = MagicMock()
        now = datetime.now(timezone.utc)

        session = AshSession(
            session_id="abc123",
            user_id=123456789,
            dm_channel=dm_channel,
            started_at=now,
            last_activity=now,
            trigger_severity="high",
        )

        assert session.session_id == "abc123"
        assert session.user_id == 123456789
        assert session.is_active is True
        assert session.messages == []

    def test_add_message(self):
        """Test adding messages to session."""
        from src.managers.ash.ash_session_manager import AshSession

        dm_channel = MagicMock()
        now = datetime.now(timezone.utc)

        session = AshSession(
            session_id="abc123",
            user_id=123456789,
            dm_channel=dm_channel,
            started_at=now,
            last_activity=now,
            trigger_severity="high",
        )

        session.add_message("user", "Hello")
        session.add_message("assistant", "Hi there!")

        assert len(session.messages) == 2
        assert session.messages[0] == {"role": "user", "content": "Hello"}
        assert session.messages[1] == {"role": "assistant", "content": "Hi there!"}

    def test_add_user_message(self):
        """Test adding user message shortcut."""
        from src.managers.ash.ash_session_manager import AshSession

        dm_channel = MagicMock()
        now = datetime.now(timezone.utc)

        session = AshSession(
            session_id="abc123",
            user_id=123456789,
            dm_channel=dm_channel,
            started_at=now,
            last_activity=now,
            trigger_severity="high",
        )

        session.add_user_message("Test message")

        assert session.messages[0]["role"] == "user"
        assert session.messages[0]["content"] == "Test message"

    def test_add_assistant_message(self):
        """Test adding assistant message shortcut."""
        from src.managers.ash.ash_session_manager import AshSession

        dm_channel = MagicMock()
        now = datetime.now(timezone.utc)

        session = AshSession(
            session_id="abc123",
            user_id=123456789,
            dm_channel=dm_channel,
            started_at=now,
            last_activity=now,
            trigger_severity="high",
        )

        session.add_assistant_message("Response")

        assert session.messages[0]["role"] == "assistant"

    def test_duration_seconds(self):
        """Test duration calculation."""
        from src.managers.ash.ash_session_manager import AshSession

        dm_channel = MagicMock()
        # Set started_at to 60 seconds ago
        started = datetime.now(timezone.utc) - timedelta(seconds=60)

        session = AshSession(
            session_id="abc123",
            user_id=123456789,
            dm_channel=dm_channel,
            started_at=started,
            last_activity=datetime.now(timezone.utc),
            trigger_severity="high",
        )

        # Duration should be approximately 60 seconds
        assert 59 <= session.duration_seconds <= 61

    def test_idle_seconds(self):
        """Test idle time calculation."""
        from src.managers.ash.ash_session_manager import AshSession

        dm_channel = MagicMock()
        now = datetime.now(timezone.utc)
        # Set last_activity to 30 seconds ago
        last_activity = now - timedelta(seconds=30)

        session = AshSession(
            session_id="abc123",
            user_id=123456789,
            dm_channel=dm_channel,
            started_at=now - timedelta(seconds=60),
            last_activity=last_activity,
            trigger_severity="high",
        )

        # Idle should be approximately 30 seconds
        assert 29 <= session.idle_seconds <= 31

    def test_message_count(self):
        """Test message count property."""
        from src.managers.ash.ash_session_manager import AshSession

        dm_channel = MagicMock()
        now = datetime.now(timezone.utc)

        session = AshSession(
            session_id="abc123",
            user_id=123456789,
            dm_channel=dm_channel,
            started_at=now,
            last_activity=now,
            trigger_severity="high",
        )

        assert session.message_count == 0

        session.add_message("user", "One")
        session.add_message("assistant", "Two")
        session.add_message("user", "Three")

        assert session.message_count == 3

    def test_to_dict(self):
        """Test session serialization to dict."""
        from src.managers.ash.ash_session_manager import AshSession

        dm_channel = MagicMock()
        now = datetime.now(timezone.utc)

        session = AshSession(
            session_id="abc123",
            user_id=123456789,
            dm_channel=dm_channel,
            started_at=now,
            last_activity=now,
            trigger_severity="high",
        )

        data = session.to_dict()

        assert data["session_id"] == "abc123"
        assert data["user_id"] == 123456789
        assert data["trigger_severity"] == "high"
        assert data["is_active"] is True
        assert "started_at" in data
        assert "duration_seconds" in data

    def test_repr(self):
        """Test string representation."""
        from src.managers.ash.ash_session_manager import AshSession

        dm_channel = MagicMock()
        now = datetime.now(timezone.utc)

        session = AshSession(
            session_id="abc123",
            user_id=123456789,
            dm_channel=dm_channel,
            started_at=now,
            last_activity=now,
            trigger_severity="high",
        )

        repr_str = repr(session)

        assert "AshSession" in repr_str
        assert "abc123" in repr_str
        assert "active" in repr_str


# =============================================================================
# AshSessionManager Initialization Tests
# =============================================================================


class TestAshSessionManagerInit:
    """Tests for AshSessionManager initialization."""

    def test_init_success(self, mock_config_manager, mock_bot):
        """Test successful initialization."""
        from src.managers.ash.ash_session_manager import AshSessionManager

        manager = AshSessionManager(
            config_manager=mock_config_manager,
            bot=mock_bot,
        )

        assert manager.active_session_count == 0
        assert manager._session_timeout == 300
        assert manager._max_duration == 600

    def test_factory_function(self, mock_config_manager, mock_bot):
        """Test factory function creates manager."""
        from src.managers.ash.ash_session_manager import create_ash_session_manager

        manager = create_ash_session_manager(
            config_manager=mock_config_manager,
            bot=mock_bot,
        )

        assert manager is not None
        assert manager.active_session_count == 0


# =============================================================================
# Session Lifecycle Tests
# =============================================================================


class TestAshSessionLifecycle:
    """Tests for session lifecycle management."""

    @pytest.mark.asyncio
    async def test_start_session(self, mock_config_manager, mock_bot, mock_user):
        """Test starting a new session."""
        from src.managers.ash.ash_session_manager import AshSessionManager

        manager = AshSessionManager(
            config_manager=mock_config_manager,
            bot=mock_bot,
        )

        session = await manager.start_session(
            user=mock_user,
            trigger_severity="high",
        )

        assert session is not None
        assert session.user_id == mock_user.id
        assert session.trigger_severity == "high"
        assert session.is_active is True
        assert manager.active_session_count == 1
        mock_user.create_dm.assert_called_once()

    @pytest.mark.asyncio
    async def test_start_session_critical(self, mock_config_manager, mock_bot, mock_user):
        """Test starting session with critical severity."""
        from src.managers.ash.ash_session_manager import AshSessionManager

        manager = AshSessionManager(
            config_manager=mock_config_manager,
            bot=mock_bot,
        )

        session = await manager.start_session(
            user=mock_user,
            trigger_severity="CRITICAL",  # Test case insensitivity
        )

        assert session.trigger_severity == "critical"

    @pytest.mark.asyncio
    async def test_start_duplicate_session_raises(
        self, mock_config_manager, mock_bot, mock_user
    ):
        """Test starting duplicate session raises error."""
        from src.managers.ash.ash_session_manager import (
            AshSessionManager,
            SessionExistsError,
        )

        manager = AshSessionManager(
            config_manager=mock_config_manager,
            bot=mock_bot,
        )

        # First session succeeds
        await manager.start_session(user=mock_user, trigger_severity="high")

        # Second session raises
        with pytest.raises(SessionExistsError):
            await manager.start_session(user=mock_user, trigger_severity="high")

    @pytest.mark.asyncio
    async def test_get_session(self, mock_config_manager, mock_bot, mock_user):
        """Test getting an active session."""
        from src.managers.ash.ash_session_manager import AshSessionManager

        manager = AshSessionManager(
            config_manager=mock_config_manager,
            bot=mock_bot,
        )

        await manager.start_session(user=mock_user, trigger_severity="high")

        session = manager.get_session(mock_user.id)

        assert session is not None
        assert session.user_id == mock_user.id

    def test_get_session_nonexistent(self, mock_config_manager, mock_bot):
        """Test getting nonexistent session returns None."""
        from src.managers.ash.ash_session_manager import AshSessionManager

        manager = AshSessionManager(
            config_manager=mock_config_manager,
            bot=mock_bot,
        )

        session = manager.get_session(999999)

        assert session is None

    @pytest.mark.asyncio
    async def test_has_active_session(self, mock_config_manager, mock_bot, mock_user):
        """Test checking for active session."""
        from src.managers.ash.ash_session_manager import AshSessionManager

        manager = AshSessionManager(
            config_manager=mock_config_manager,
            bot=mock_bot,
        )

        assert manager.has_active_session(mock_user.id) is False

        await manager.start_session(user=mock_user, trigger_severity="high")

        assert manager.has_active_session(mock_user.id) is True

    @pytest.mark.asyncio
    async def test_end_session(self, mock_config_manager, mock_bot, mock_user):
        """Test ending a session."""
        from src.managers.ash.ash_session_manager import AshSessionManager

        manager = AshSessionManager(
            config_manager=mock_config_manager,
            bot=mock_bot,
        )

        session = await manager.start_session(
            user=mock_user, trigger_severity="high"
        )

        # Patch at src.prompts where it's defined (imported inside method)
        with patch("src.prompts.get_closing_message") as mock_closing:
            mock_closing.return_value = "Take care!"

            result = await manager.end_session(mock_user.id, reason="ended")

        assert result is True
        assert session.is_active is False
        session.dm_channel.send.assert_called()

    @pytest.mark.asyncio
    async def test_end_session_no_closing_message(
        self, mock_config_manager, mock_bot, mock_user
    ):
        """Test ending session without closing message."""
        from src.managers.ash.ash_session_manager import AshSessionManager

        manager = AshSessionManager(
            config_manager=mock_config_manager,
            bot=mock_bot,
        )

        session = await manager.start_session(
            user=mock_user, trigger_severity="high"
        )

        result = await manager.end_session(
            mock_user.id, reason="ended", send_closing=False
        )

        assert result is True
        assert session.is_active is False
        # DM should not have been called for closing
        session.dm_channel.send.assert_not_called()

    @pytest.mark.asyncio
    async def test_end_nonexistent_session(self, mock_config_manager, mock_bot):
        """Test ending nonexistent session returns False."""
        from src.managers.ash.ash_session_manager import AshSessionManager

        manager = AshSessionManager(
            config_manager=mock_config_manager,
            bot=mock_bot,
        )

        result = await manager.end_session(999999, reason="ended")

        assert result is False


# =============================================================================
# Multiple Sessions Tests
# =============================================================================


class TestAshSessionMultiple:
    """Tests for multiple concurrent sessions."""

    @pytest.mark.asyncio
    async def test_multiple_users(
        self, mock_config_manager, mock_bot, mock_user, mock_user_2
    ):
        """Test multiple users can have sessions."""
        from src.managers.ash.ash_session_manager import AshSessionManager

        manager = AshSessionManager(
            config_manager=mock_config_manager,
            bot=mock_bot,
        )

        session1 = await manager.start_session(
            user=mock_user, trigger_severity="high"
        )
        session2 = await manager.start_session(
            user=mock_user_2, trigger_severity="critical"
        )

        assert manager.active_session_count == 2
        assert session1.session_id != session2.session_id

    @pytest.mark.asyncio
    async def test_get_all_active_sessions(
        self, mock_config_manager, mock_bot, mock_user, mock_user_2
    ):
        """Test getting all active sessions."""
        from src.managers.ash.ash_session_manager import AshSessionManager

        manager = AshSessionManager(
            config_manager=mock_config_manager,
            bot=mock_bot,
        )

        await manager.start_session(user=mock_user, trigger_severity="high")
        await manager.start_session(user=mock_user_2, trigger_severity="critical")

        sessions = manager.get_all_active_sessions()

        assert len(sessions) == 2


# =============================================================================
# Session Expiration Tests
# =============================================================================


class TestAshSessionExpiration:
    """Tests for session expiration handling."""

    @pytest.mark.asyncio
    async def test_session_idle_timeout(
        self, mock_config_manager_short_timeout, mock_bot, mock_user
    ):
        """Test session expires after idle timeout."""
        from src.managers.ash.ash_session_manager import AshSessionManager

        manager = AshSessionManager(
            config_manager=mock_config_manager_short_timeout,
            bot=mock_bot,
        )

        session = await manager.start_session(
            user=mock_user, trigger_severity="high"
        )

        # Artificially set last_activity to past
        session.last_activity = datetime.now(timezone.utc) - timedelta(seconds=10)

        # Session should now be expired
        retrieved = manager.get_session(mock_user.id)

        assert retrieved is None
        assert session.is_active is False

    @pytest.mark.asyncio
    async def test_session_max_duration(
        self, mock_config_manager_short_timeout, mock_bot, mock_user
    ):
        """Test session expires after max duration."""
        from src.managers.ash.ash_session_manager import AshSessionManager

        manager = AshSessionManager(
            config_manager=mock_config_manager_short_timeout,
            bot=mock_bot,
        )

        session = await manager.start_session(
            user=mock_user, trigger_severity="high"
        )

        # Artificially set started_at to past
        session.started_at = datetime.now(timezone.utc) - timedelta(seconds=15)

        # Session should now be expired
        retrieved = manager.get_session(mock_user.id)

        assert retrieved is None

    @pytest.mark.asyncio
    async def test_cleanup_expired_sessions(
        self, mock_config_manager_short_timeout, mock_bot, mock_user, mock_user_2
    ):
        """Test cleanup of expired sessions."""
        from src.managers.ash.ash_session_manager import AshSessionManager

        manager = AshSessionManager(
            config_manager=mock_config_manager_short_timeout,
            bot=mock_bot,
        )

        session1 = await manager.start_session(
            user=mock_user, trigger_severity="high"
        )
        session2 = await manager.start_session(
            user=mock_user_2, trigger_severity="high"
        )

        # Make session1 expired
        session1.last_activity = datetime.now(timezone.utc) - timedelta(seconds=10)

        with patch("src.prompts.get_closing_message") as mock_closing:
            mock_closing.return_value = "Take care!"

            cleaned = await manager.cleanup_expired_sessions()

        assert cleaned == 1
        assert session1.is_active is False
        assert session2.is_active is True


# =============================================================================
# Statistics Tests
# =============================================================================


class TestAshSessionStatistics:
    """Tests for session statistics."""

    @pytest.mark.asyncio
    async def test_get_stats(self, mock_config_manager, mock_bot, mock_user):
        """Test get_stats returns correct data."""
        from src.managers.ash.ash_session_manager import AshSessionManager

        manager = AshSessionManager(
            config_manager=mock_config_manager,
            bot=mock_bot,
        )

        await manager.start_session(user=mock_user, trigger_severity="high")

        stats = manager.get_stats()

        assert stats["active_sessions"] == 1
        assert stats["total_created"] == 1
        assert stats["session_timeout_seconds"] == 300
        assert stats["max_duration_seconds"] == 600
        assert len(stats["sessions"]) == 1

    @pytest.mark.asyncio
    async def test_stats_after_end(self, mock_config_manager, mock_bot, mock_user):
        """Test stats update after ending session."""
        from src.managers.ash.ash_session_manager import AshSessionManager

        manager = AshSessionManager(
            config_manager=mock_config_manager,
            bot=mock_bot,
        )

        await manager.start_session(user=mock_user, trigger_severity="high")

        with patch("src.prompts.get_closing_message") as mock_closing:
            mock_closing.return_value = "Take care!"
            await manager.end_session(mock_user.id)

        stats = manager.get_stats()

        assert stats["active_sessions"] == 0
        assert stats["total_created"] == 1
        assert stats["total_ended"] == 1

    def test_repr(self, mock_config_manager, mock_bot):
        """Test string representation."""
        from src.managers.ash.ash_session_manager import AshSessionManager

        manager = AshSessionManager(
            config_manager=mock_config_manager,
            bot=mock_bot,
        )

        repr_str = repr(manager)

        assert "AshSessionManager" in repr_str
        assert "active=0" in repr_str
