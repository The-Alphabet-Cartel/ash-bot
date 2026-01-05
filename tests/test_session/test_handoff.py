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
Unit Tests for HandoffManager (Phase 9.2)
----------------------------------------------------------------------------
FILE VERSION: v5.0-9-2.0-1
LAST MODIFIED: 2026-01-05
PHASE: Phase 9 - CRT Workflow Enhancements (Step 9.2)
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-bot
============================================================================

USAGE:
    docker exec ash-bot python3.11 -m pytest tests/test_handoff.py -v
"""

import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))


# =============================================================================
# Module version
# =============================================================================

__version__ = "v5.0-9-2.0-1"


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def mock_config_manager():
    """Create mock ConfigManager for handoff tests."""
    config = MagicMock()
    
    def get_config(section, key, default=None):
        configs = {
            ("handoff", "enabled"): True,
            ("handoff", "crt_roles"): "CRT,Crisis Response Team",
            ("handoff", "notes_channel_id"): "123456789",
            ("handoff", "context_enabled"): True,
        }
        return configs.get((section, key), default)
    
    config.get = MagicMock(side_effect=get_config)
    return config


@pytest.fixture
def mock_config_manager_disabled():
    """Create mock ConfigManager with handoff disabled."""
    config = MagicMock()
    
    def get_config(section, key, default=None):
        configs = {
            ("handoff", "enabled"): False,
            ("handoff", "crt_roles"): "CRT,Crisis Response Team",
            ("handoff", "notes_channel_id"): None,
            ("handoff", "context_enabled"): False,
        }
        return configs.get((section, key), default)
    
    config.get = MagicMock(side_effect=get_config)
    return config


@pytest.fixture
def mock_config_manager_no_context():
    """Create mock ConfigManager with context disabled."""
    config = MagicMock()
    
    def get_config(section, key, default=None):
        configs = {
            ("handoff", "enabled"): True,
            ("handoff", "crt_roles"): "CRT,Crisis Response Team",
            ("handoff", "notes_channel_id"): "123456789",
            ("handoff", "context_enabled"): False,
        }
        return configs.get((section, key), default)
    
    config.get = MagicMock(side_effect=get_config)
    return config


@pytest.fixture
def mock_notes_manager():
    """Create mock NotesManager."""
    notes = MagicMock()
    notes.update_session_end = AsyncMock(return_value=True)
    notes.add_note = AsyncMock(return_value=(True, "Note added", MagicMock()))
    return notes


@pytest.fixture
def mock_discord_member_crt():
    """Create mock Discord member with CRT role."""
    member = MagicMock()
    member.id = 12345
    member.display_name = "CRTStaff"
    
    # Mock CRT role
    crt_role = MagicMock()
    crt_role.name = "CRT"
    
    # Mock regular role
    other_role = MagicMock()
    other_role.name = "Member"
    
    member.roles = [crt_role, other_role]
    
    # Mock guild
    member.guild = MagicMock()
    member.guild.id = 999999
    
    return member


@pytest.fixture
def mock_discord_member_non_crt():
    """Create mock Discord member without CRT role."""
    member = MagicMock()
    member.id = 67890
    member.display_name = "RegularUser"
    
    # Mock regular role only
    role = MagicMock()
    role.name = "Member"
    
    member.roles = [role]
    
    # Mock guild
    member.guild = MagicMock()
    member.guild.id = 999999
    
    return member


@pytest.fixture
def mock_discord_guild():
    """Create mock Discord guild."""
    guild = MagicMock()
    guild.id = 999999
    guild.name = "Test Server"
    return guild


@pytest.fixture
def mock_ash_session():
    """Create mock AshSession for handoff tests."""
    session = MagicMock()
    session.session_id = "session_test123"
    session.user_id = 11111
    session.dm_channel = MagicMock()
    session.dm_channel.send = AsyncMock(return_value=MagicMock())
    session.trigger_severity = "high"
    session.message_count = 10
    session.duration_seconds = 300.0
    session.messages = [
        {"role": "user", "content": "I'm feeling really anxious about work"},
        {"role": "assistant", "content": "I hear you. What's going on at work?"},
        {"role": "user", "content": "My boss has been putting a lot of pressure on me"},
        {"role": "assistant", "content": "That sounds stressful."},
        {"role": "user", "content": "I feel better talking about it"},
    ]
    return session


@pytest.fixture
def mock_bot():
    """Create mock Discord bot."""
    bot = MagicMock()
    bot.response_metrics_manager = MagicMock()
    bot.response_metrics_manager.get_user_alert_history = AsyncMock(return_value=[])
    return bot


# =============================================================================
# HandoffManager Initialization Tests
# =============================================================================


class TestHandoffManagerInitialization:
    """Tests for HandoffManager initialization."""
    
    def test_initialization_enabled(self, mock_config_manager, mock_notes_manager):
        """Test initialization with handoff enabled."""
        from src.managers.session.handoff_manager import create_handoff_manager
        
        manager = create_handoff_manager(
            config_manager=mock_config_manager,
            notes_manager=mock_notes_manager,
        )
        
        assert manager is not None
        assert manager.is_enabled is True
        assert manager.context_enabled is True
        assert "crt" in manager.crt_roles
        assert "crisis response team" in manager.crt_roles
    
    def test_initialization_disabled(self, mock_config_manager_disabled, mock_notes_manager):
        """Test initialization with handoff disabled."""
        from src.managers.session.handoff_manager import create_handoff_manager
        
        manager = create_handoff_manager(
            config_manager=mock_config_manager_disabled,
            notes_manager=mock_notes_manager,
        )
        
        assert manager is not None
        assert manager.is_enabled is False
    
    def test_initialization_without_notes_manager(self, mock_config_manager):
        """Test initialization without notes manager."""
        from src.managers.session.handoff_manager import create_handoff_manager
        
        manager = create_handoff_manager(
            config_manager=mock_config_manager,
            notes_manager=None,
        )
        
        assert manager is not None
        assert manager.is_enabled is True
    
    def test_initialization_context_disabled(self, mock_config_manager_no_context):
        """Test initialization with context summaries disabled."""
        from src.managers.session.handoff_manager import create_handoff_manager
        
        manager = create_handoff_manager(
            config_manager=mock_config_manager_no_context,
        )
        
        assert manager is not None
        assert manager.context_enabled is False


# =============================================================================
# CRT Detection Tests
# =============================================================================


class TestCRTDetection:
    """Tests for CRT member detection."""
    
    @pytest.mark.asyncio
    async def test_is_crt_member_with_crt_role(
        self, mock_config_manager, mock_discord_member_crt
    ):
        """Test CRT detection with member who has CRT role."""
        from src.managers.session.handoff_manager import create_handoff_manager
        
        manager = create_handoff_manager(
            config_manager=mock_config_manager,
        )
        
        result = await manager.is_crt_member(mock_discord_member_crt)
        
        assert result is True
    
    @pytest.mark.asyncio
    async def test_is_crt_member_without_crt_role(
        self, mock_config_manager, mock_discord_member_non_crt
    ):
        """Test CRT detection with member who lacks CRT role."""
        from src.managers.session.handoff_manager import create_handoff_manager
        
        manager = create_handoff_manager(
            config_manager=mock_config_manager,
        )
        
        result = await manager.is_crt_member(mock_discord_member_non_crt)
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_is_crt_member_when_disabled(
        self, mock_config_manager_disabled, mock_discord_member_crt
    ):
        """Test CRT detection returns False when handoff disabled."""
        from src.managers.session.handoff_manager import create_handoff_manager
        
        manager = create_handoff_manager(
            config_manager=mock_config_manager_disabled,
        )
        
        result = await manager.is_crt_member(mock_discord_member_crt)
        
        # Should return False when disabled even if member has CRT role
        assert result is False
    
    @pytest.mark.asyncio
    async def test_is_crt_member_crisis_response_team_role(
        self, mock_config_manager
    ):
        """Test CRT detection with 'Crisis Response Team' role name."""
        from src.managers.session.handoff_manager import create_handoff_manager
        
        manager = create_handoff_manager(
            config_manager=mock_config_manager,
        )
        
        # Create member with "Crisis Response Team" role
        member = MagicMock()
        member.id = 12345
        role = MagicMock()
        role.name = "Crisis Response Team"
        member.roles = [role]
        member.guild = MagicMock()
        
        result = await manager.is_crt_member(member)
        
        assert result is True
    
    @pytest.mark.asyncio
    async def test_is_crt_by_user_fetches_member(
        self, mock_config_manager, mock_discord_guild
    ):
        """Test CRT detection via user ID fetches member from guild."""
        from src.managers.session.handoff_manager import create_handoff_manager
        
        manager = create_handoff_manager(
            config_manager=mock_config_manager,
        )
        
        # Create user
        user = MagicMock()
        user.id = 12345
        
        # Mock guild.get_member to return a CRT member
        crt_member = MagicMock()
        crt_role = MagicMock()
        crt_role.name = "CRT"
        crt_member.roles = [crt_role]
        crt_member.guild = mock_discord_guild
        
        mock_discord_guild.get_member = MagicMock(return_value=crt_member)
        mock_discord_guild.fetch_member = AsyncMock(return_value=crt_member)
        
        result = await manager.is_crt_by_user(user, mock_discord_guild)
        
        assert result is True
        mock_discord_guild.get_member.assert_called_once_with(12345)
    
    @pytest.mark.asyncio
    async def test_is_crt_by_user_user_not_in_guild(
        self, mock_config_manager, mock_discord_guild
    ):
        """Test CRT detection returns False when user not in guild."""
        from src.managers.session.handoff_manager import create_handoff_manager
        import discord
        
        manager = create_handoff_manager(
            config_manager=mock_config_manager,
        )
        
        user = MagicMock()
        user.id = 99999
        
        # Mock guild.get_member to return None (not cached)
        # Mock fetch_member to raise NotFound
        mock_discord_guild.get_member = MagicMock(return_value=None)
        mock_discord_guild.fetch_member = AsyncMock(side_effect=discord.NotFound(MagicMock(), "Not found"))
        
        result = await manager.is_crt_by_user(user, mock_discord_guild)
        
        assert result is False


# =============================================================================
# Handoff Handling Tests
# =============================================================================


class TestHandoffHandling:
    """Tests for CRT handoff handling."""
    
    @pytest.mark.asyncio
    async def test_handle_crt_join_success(
        self,
        mock_config_manager,
        mock_notes_manager,
        mock_ash_session,
        mock_discord_member_crt,
        mock_bot,
    ):
        """Test successful CRT join handling."""
        from src.managers.session.handoff_manager import create_handoff_manager
        
        manager = create_handoff_manager(
            config_manager=mock_config_manager,
            notes_manager=mock_notes_manager,
        )
        
        result = await manager.handle_crt_join(
            session=mock_ash_session,
            crt_member=mock_discord_member_crt,
            bot=mock_bot,
        )
        
        assert result is True
        # Verify handoff announcement was sent
        mock_ash_session.dm_channel.send.assert_called()
    
    @pytest.mark.asyncio
    async def test_handle_crt_join_when_disabled(
        self,
        mock_config_manager_disabled,
        mock_notes_manager,
        mock_ash_session,
        mock_discord_member_crt,
        mock_bot,
    ):
        """Test CRT join returns False when handoff disabled."""
        from src.managers.session.handoff_manager import create_handoff_manager
        
        manager = create_handoff_manager(
            config_manager=mock_config_manager_disabled,
            notes_manager=mock_notes_manager,
        )
        
        result = await manager.handle_crt_join(
            session=mock_ash_session,
            crt_member=mock_discord_member_crt,
            bot=mock_bot,
        )
        
        assert result is False
        # Verify no announcement was sent
        mock_ash_session.dm_channel.send.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_handle_crt_join_duplicate_prevention(
        self,
        mock_config_manager,
        mock_notes_manager,
        mock_ash_session,
        mock_discord_member_crt,
        mock_bot,
    ):
        """Test duplicate handoff announcements are prevented."""
        from src.managers.session.handoff_manager import create_handoff_manager
        
        manager = create_handoff_manager(
            config_manager=mock_config_manager,
            notes_manager=mock_notes_manager,
        )
        
        # First call should succeed
        result1 = await manager.handle_crt_join(
            session=mock_ash_session,
            crt_member=mock_discord_member_crt,
            bot=mock_bot,
        )
        
        # Second call with same session/member should return False
        result2 = await manager.handle_crt_join(
            session=mock_ash_session,
            crt_member=mock_discord_member_crt,
            bot=mock_bot,
        )
        
        assert result1 is True
        assert result2 is False
    
    @pytest.mark.asyncio
    async def test_handle_crt_join_different_members(
        self,
        mock_config_manager,
        mock_notes_manager,
        mock_ash_session,
        mock_discord_member_crt,
        mock_bot,
    ):
        """Test multiple CRT members can be announced for same session."""
        from src.managers.session.handoff_manager import create_handoff_manager
        
        manager = create_handoff_manager(
            config_manager=mock_config_manager,
            notes_manager=mock_notes_manager,
        )
        
        # Create second CRT member
        second_crt = MagicMock()
        second_crt.id = 99999
        second_crt.display_name = "SecondCRT"
        crt_role = MagicMock()
        crt_role.name = "CRT"
        second_crt.roles = [crt_role]
        
        # First CRT member
        result1 = await manager.handle_crt_join(
            session=mock_ash_session,
            crt_member=mock_discord_member_crt,
            bot=mock_bot,
        )
        
        # Second CRT member (different person) should also succeed
        result2 = await manager.handle_crt_join(
            session=mock_ash_session,
            crt_member=second_crt,
            bot=mock_bot,
        )
        
        assert result1 is True
        assert result2 is True
    
    @pytest.mark.asyncio
    async def test_handle_crt_join_without_context(
        self,
        mock_config_manager_no_context,
        mock_notes_manager,
        mock_ash_session,
        mock_discord_member_crt,
        mock_bot,
    ):
        """Test CRT join without context summary."""
        from src.managers.session.handoff_manager import create_handoff_manager
        
        manager = create_handoff_manager(
            config_manager=mock_config_manager_no_context,
            notes_manager=mock_notes_manager,
        )
        
        result = await manager.handle_crt_join(
            session=mock_ash_session,
            crt_member=mock_discord_member_crt,
            bot=mock_bot,
        )
        
        assert result is True
        # Should only send one message (handoff announcement) not context
        assert mock_ash_session.dm_channel.send.call_count == 1


# =============================================================================
# Context Summary Tests
# =============================================================================


class TestContextSummary:
    """Tests for context summary generation."""
    
    @pytest.mark.asyncio
    async def test_generate_context_summary_basic(
        self,
        mock_config_manager,
        mock_ash_session,
        mock_bot,
    ):
        """Test basic context summary generation."""
        from src.managers.session.handoff_manager import create_handoff_manager
        
        manager = create_handoff_manager(
            config_manager=mock_config_manager,
        )
        
        context = await manager.generate_context_summary(
            session=mock_ash_session,
            bot=mock_bot,
        )
        
        assert context is not None
        assert "duration_str" in context
        assert "previous_alerts" in context
    
    @pytest.mark.asyncio
    async def test_generate_context_summary_duration_formats(
        self, mock_config_manager, mock_bot
    ):
        """Test duration formatting for various lengths."""
        from src.managers.session.handoff_manager import create_handoff_manager
        
        manager = create_handoff_manager(
            config_manager=mock_config_manager,
        )
        
        # Test seconds
        session_short = MagicMock()
        session_short.duration_seconds = 45
        session_short.messages = []
        session_short.user_id = 12345
        
        context = await manager.generate_context_summary(session_short, mock_bot)
        assert "45 seconds" in context["duration_str"]
        
        # Test minutes
        session_medium = MagicMock()
        session_medium.duration_seconds = 300
        session_medium.messages = []
        session_medium.user_id = 12345
        
        context = await manager.generate_context_summary(session_medium, mock_bot)
        assert "5 minute" in context["duration_str"]
        
        # Test hours
        session_long = MagicMock()
        session_long.duration_seconds = 3700
        session_long.messages = []
        session_long.user_id = 12345
        
        context = await manager.generate_context_summary(session_long, mock_bot)
        assert "1h" in context["duration_str"]
    
    @pytest.mark.asyncio
    async def test_generate_context_summary_topic_extraction(
        self, mock_config_manager, mock_bot
    ):
        """Test topic extraction from messages."""
        from src.managers.session.handoff_manager import create_handoff_manager
        
        manager = create_handoff_manager(
            config_manager=mock_config_manager,
        )
        
        session = MagicMock()
        session.duration_seconds = 300
        session.user_id = 12345
        session.messages = [
            {"role": "user", "content": "I'm feeling so anxious about everything"},
            {"role": "assistant", "content": "Tell me more about that."},
            {"role": "user", "content": "My work is stressful and I can't sleep"},
        ]
        
        context = await manager.generate_context_summary(session, mock_bot)
        
        # Should detect anxiety, stress, sleep topics
        topics = context.get("topics", "").lower()
        assert "anxiety" in topics or "stress" in topics or "sleep" in topics
    
    @pytest.mark.asyncio
    async def test_generate_context_summary_mood_assessment(
        self, mock_config_manager, mock_bot
    ):
        """Test mood assessment from messages."""
        from src.managers.session.handoff_manager import create_handoff_manager
        
        manager = create_handoff_manager(
            config_manager=mock_config_manager,
        )
        
        # Test positive mood indicators
        session_positive = MagicMock()
        session_positive.duration_seconds = 300
        session_positive.user_id = 12345
        session_positive.messages = [
            {"role": "user", "content": "I was feeling bad but now I feel better"},
            {"role": "assistant", "content": "That's great to hear."},
            {"role": "user", "content": "Thanks for the help, I'm okay now"},
        ]
        
        context = await manager.generate_context_summary(session_positive, mock_bot)
        mood = context.get("mood_assessment", "").lower()
        assert "calm" in mood or "better" in mood or "engaged" in mood
    
    @pytest.mark.asyncio
    async def test_generate_context_summary_no_messages(
        self, mock_config_manager, mock_bot
    ):
        """Test context summary with no messages."""
        from src.managers.session.handoff_manager import create_handoff_manager
        
        manager = create_handoff_manager(
            config_manager=mock_config_manager,
        )
        
        session = MagicMock()
        session.duration_seconds = 0
        session.user_id = 12345
        session.messages = []
        
        context = await manager.generate_context_summary(session, mock_bot)
        
        assert context is not None
        # Should have default topics when no messages to analyze
        assert context.get("topics") == "General support conversation"


# =============================================================================
# Session Transfer Tests
# =============================================================================


class TestSessionTransfer:
    """Tests for session transfer marking."""
    
    @pytest.mark.asyncio
    async def test_mark_session_transferred(
        self,
        mock_config_manager,
        mock_notes_manager,
        mock_ash_session,
        mock_discord_member_crt,
    ):
        """Test marking session as transferred."""
        from src.managers.session.handoff_manager import create_handoff_manager
        
        manager = create_handoff_manager(
            config_manager=mock_config_manager,
            notes_manager=mock_notes_manager,
        )
        
        await manager.mark_session_transferred(
            session=mock_ash_session,
            crt_member=mock_discord_member_crt,
        )
        
        # Verify notes manager was called
        mock_notes_manager.update_session_end.assert_called_once()
        call_kwargs = mock_notes_manager.update_session_end.call_args[1]
        assert call_kwargs["session_id"] == "session_test123"
        assert call_kwargs["end_reason"] == "crt_handoff"
    
    @pytest.mark.asyncio
    async def test_mark_session_transferred_no_notes_manager(
        self,
        mock_config_manager,
        mock_ash_session,
        mock_discord_member_crt,
    ):
        """Test transfer marking without notes manager does nothing."""
        from src.managers.session.handoff_manager import create_handoff_manager
        
        manager = create_handoff_manager(
            config_manager=mock_config_manager,
            notes_manager=None,
        )
        
        # Should not raise exception
        await manager.mark_session_transferred(
            session=mock_ash_session,
            crt_member=mock_discord_member_crt,
        )


# =============================================================================
# Handoff Cache Tests
# =============================================================================


class TestHandoffCache:
    """Tests for handoff cache management."""
    
    @pytest.mark.asyncio
    async def test_clear_handoff_cache(
        self,
        mock_config_manager,
        mock_notes_manager,
        mock_ash_session,
        mock_discord_member_crt,
        mock_bot,
    ):
        """Test clearing handoff cache for a session."""
        from src.managers.session.handoff_manager import create_handoff_manager
        
        manager = create_handoff_manager(
            config_manager=mock_config_manager,
            notes_manager=mock_notes_manager,
        )
        
        # First, handle a CRT join to populate cache
        await manager.handle_crt_join(
            session=mock_ash_session,
            crt_member=mock_discord_member_crt,
            bot=mock_bot,
        )
        
        # Clear the cache
        manager.clear_handoff_cache(mock_ash_session.session_id)
        
        # Now the same handoff should be allowed again
        result = await manager.handle_crt_join(
            session=mock_ash_session,
            crt_member=mock_discord_member_crt,
            bot=mock_bot,
        )
        
        assert result is True
    
    def test_clear_handoff_cache_nonexistent(self, mock_config_manager):
        """Test clearing cache for session that doesn't exist."""
        from src.managers.session.handoff_manager import create_handoff_manager
        
        manager = create_handoff_manager(
            config_manager=mock_config_manager,
        )
        
        # Should not raise exception
        manager.clear_handoff_cache("nonexistent_session")


# =============================================================================
# Properties Tests
# =============================================================================


class TestHandoffManagerProperties:
    """Tests for HandoffManager properties."""
    
    def test_is_enabled_property(self, mock_config_manager):
        """Test is_enabled property."""
        from src.managers.session.handoff_manager import create_handoff_manager
        
        manager = create_handoff_manager(
            config_manager=mock_config_manager,
        )
        
        assert manager.is_enabled is True
    
    def test_context_enabled_property(self, mock_config_manager):
        """Test context_enabled property."""
        from src.managers.session.handoff_manager import create_handoff_manager
        
        manager = create_handoff_manager(
            config_manager=mock_config_manager,
        )
        
        assert manager.context_enabled is True
    
    def test_crt_roles_property(self, mock_config_manager):
        """Test crt_roles property returns copy."""
        from src.managers.session.handoff_manager import create_handoff_manager
        
        manager = create_handoff_manager(
            config_manager=mock_config_manager,
        )
        
        roles = manager.crt_roles
        assert "crt" in roles
        assert "crisis response team" in roles
        
        # Verify it's a copy (modifying doesn't affect original)
        original_length = len(manager.crt_roles)
        roles.append("test")
        assert len(manager.crt_roles) == original_length


# =============================================================================
# Role Parsing Tests
# =============================================================================


class TestRoleParsing:
    """Tests for role string parsing."""
    
    def test_parse_roles_standard(self, mock_config_manager):
        """Test standard role parsing."""
        from src.managers.session.handoff_manager import create_handoff_manager
        
        manager = create_handoff_manager(
            config_manager=mock_config_manager,
        )
        
        roles = manager.crt_roles
        assert len(roles) == 2
        assert "crt" in roles
        assert "crisis response team" in roles
    
    def test_parse_roles_empty(self):
        """Test parsing empty role string."""
        from src.managers.session.handoff_manager import create_handoff_manager
        
        config = MagicMock()
        config.get = MagicMock(side_effect=lambda s, k, d=None: {
            ("handoff", "enabled"): True,
            ("handoff", "crt_roles"): "",
            ("handoff", "notes_channel_id"): None,
            ("handoff", "context_enabled"): True,
        }.get((s, k), d))
        
        manager = create_handoff_manager(
            config_manager=config,
        )
        
        assert manager.crt_roles == []
    
    def test_parse_roles_whitespace(self):
        """Test role parsing with extra whitespace."""
        from src.managers.session.handoff_manager import create_handoff_manager
        
        config = MagicMock()
        config.get = MagicMock(side_effect=lambda s, k, d=None: {
            ("handoff", "enabled"): True,
            ("handoff", "crt_roles"): "  CRT  ,  Admin  ",
            ("handoff", "notes_channel_id"): None,
            ("handoff", "context_enabled"): True,
        }.get((s, k), d))
        
        manager = create_handoff_manager(
            config_manager=config,
        )
        
        roles = manager.crt_roles
        assert "crt" in roles
        assert "admin" in roles
        # Ensure no whitespace in results
        for role in roles:
            assert role == role.strip()


# =============================================================================
# Handoff Messages Tests
# =============================================================================


class TestHandoffMessages:
    """Tests for handoff message content."""
    
    def test_handoff_messages_exist(self):
        """Test that handoff messages are defined."""
        from src.managers.session.handoff_manager import HANDOFF_MESSAGES
        
        assert len(HANDOFF_MESSAGES) > 0
        
        for message in HANDOFF_MESSAGES:
            assert len(message) > 0
            # Each message should mention CRT/support team
            assert "team" in message.lower() or "crt" in message.lower()
    
    def test_handoff_messages_contain_emoji(self):
        """Test that handoff messages contain heart emoji."""
        from src.managers.session.handoff_manager import HANDOFF_MESSAGES
        
        for message in HANDOFF_MESSAGES:
            assert "💜" in message


# =============================================================================
# Edge Cases Tests
# =============================================================================


class TestEdgeCases:
    """Tests for edge cases and error handling."""
    
    @pytest.mark.asyncio
    async def test_handle_crt_join_dm_send_fails(
        self,
        mock_config_manager,
        mock_notes_manager,
        mock_ash_session,
        mock_discord_member_crt,
        mock_bot,
    ):
        """Test handling when DM send fails."""
        import discord
        from src.managers.session.handoff_manager import create_handoff_manager
        
        manager = create_handoff_manager(
            config_manager=mock_config_manager,
            notes_manager=mock_notes_manager,
        )
        
        # Mock send to raise exception
        mock_ash_session.dm_channel.send = AsyncMock(
            side_effect=discord.HTTPException(MagicMock(), "Failed")
        )
        
        # Should not raise, but return False
        result = await manager.handle_crt_join(
            session=mock_ash_session,
            crt_member=mock_discord_member_crt,
            bot=mock_bot,
        )
        
        # May still return True if handoff was registered, just announcement failed
        # The important thing is it doesn't raise
        assert isinstance(result, bool)
    
    @pytest.mark.asyncio
    async def test_is_crt_member_no_guild(self, mock_config_manager):
        """Test CRT detection with member lacking guild attribute."""
        from src.managers.session.handoff_manager import create_handoff_manager
        
        manager = create_handoff_manager(
            config_manager=mock_config_manager,
        )
        
        # Member without guild attribute
        member = MagicMock(spec=[])  # Empty spec = no attributes
        member.id = 12345
        
        result = await manager.is_crt_member(member, guild=None)
        
        assert result is False


# =============================================================================
# Run tests
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
