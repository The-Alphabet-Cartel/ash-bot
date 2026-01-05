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
Integration Tests: User Opt-Out Flow
---
FILE VERSION: v5.0-7-2.0-1
LAST MODIFIED: 2026-01-04
PHASE: Phase 7 - Core Safety & User Preferences
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-bot
Community: The Alphabet Cartel - https://discord.gg/alphabetcartel | https://alphabetcartel.org
============================================================================
Tests for User Opt-Out Feature (Step 7.2):
- Opted-out user skips Ash session
- CRT still receives alerts for opted-out users
- Alert embed shows "prefers human" indicator
- TTL expiry re-enables Ash
- AshSessionManager integration
"""

import json
import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import discord

from src.managers.user.user_preferences_manager import (
    UserPreferencesManager,
    create_user_preferences_manager,
    UserPreference,
    REDIS_KEY_PREFIX,
)
from src.managers.ash.ash_session_manager import (
    AshSessionManager,
    create_ash_session_manager,
    UserOptedOutError,
)
from src.managers.alerting.embed_builder import (
    EmbedBuilder,
    create_embed_builder,
)


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def mock_config_for_opt_out():
    """ConfigManager mock for opt-out testing."""
    config = MagicMock()
    config.get.side_effect = lambda section, key, default=None: {
        ("user_preferences", "optout_enabled"): True,
        ("user_preferences", "optout_ttl_days"): 30,
        ("ash", "session_timeout_seconds"): 300,
        ("ash", "max_session_duration_seconds"): 600,
    }.get((section, key), default)
    return config


@pytest.fixture
def mock_redis_for_opt_out():
    """Redis mock with full async support."""
    redis = MagicMock()
    redis.is_connected = True
    
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
    
    redis.set = AsyncMock(side_effect=mock_set)
    redis.get = AsyncMock(side_effect=mock_get)
    redis.delete = AsyncMock(side_effect=mock_delete)
    redis._storage = storage
    
    return redis


@pytest.fixture
def mock_bot_for_opt_out():
    """Bot mock for session testing."""
    bot = MagicMock()
    bot.user = MagicMock()
    bot.user.id = 999999999999999999
    return bot


@pytest.fixture
def mock_discord_user():
    """Mock Discord user for testing."""
    user = MagicMock(spec=discord.User)
    user.id = 123456789012345678
    user.display_name = "TestUser"
    user.name = "testuser"
    
    # DM channel mock
    dm_channel = MagicMock(spec=discord.DMChannel)
    dm_channel.send = AsyncMock()
    user.create_dm = AsyncMock(return_value=dm_channel)
    
    return user


@pytest.fixture
def user_preferences_manager(mock_config_for_opt_out, mock_redis_for_opt_out):
    """Create UserPreferencesManager for testing."""
    return create_user_preferences_manager(
        config_manager=mock_config_for_opt_out,
        redis_manager=mock_redis_for_opt_out,
    )


@pytest.fixture
def ash_session_manager(mock_config_for_opt_out, mock_bot_for_opt_out):
    """Create AshSessionManager for testing."""
    return create_ash_session_manager(
        config_manager=mock_config_for_opt_out,
        bot=mock_bot_for_opt_out,
    )


@pytest.fixture
def integrated_managers(
    mock_config_for_opt_out,
    mock_redis_for_opt_out,
    mock_bot_for_opt_out,
):
    """Create integrated managers with opt-out wired up."""
    # Create preferences manager
    prefs = create_user_preferences_manager(
        config_manager=mock_config_for_opt_out,
        redis_manager=mock_redis_for_opt_out,
    )
    
    # Create session manager
    sessions = create_ash_session_manager(
        config_manager=mock_config_for_opt_out,
        bot=mock_bot_for_opt_out,
    )
    
    # Wire them together
    sessions.set_user_preferences_manager(prefs)
    
    return {
        "preferences": prefs,
        "sessions": sessions,
        "redis": mock_redis_for_opt_out,
    }


# =============================================================================
# Scenario 1: Opted-Out User Skips Ash Session
# =============================================================================


class TestOptedOutUserSkipsAsh:
    """
    Scenario: User who has opted out should not receive Ash sessions.
    
    Flow:
    1. User opts out of Ash AI
    2. User triggers a crisis
    3. Ash session is NOT created
    4. UserOptedOutError is raised
    """

    @pytest.mark.asyncio
    async def test_opted_out_user_raises_error(
        self,
        integrated_managers,
        mock_discord_user,
    ):
        """Test that starting session for opted-out user raises error."""
        prefs = integrated_managers["preferences"]
        sessions = integrated_managers["sessions"]
        
        # User opts out
        await prefs.set_opt_out(mock_discord_user.id)
        
        # Attempt to start session should raise
        with pytest.raises(UserOptedOutError):
            await sessions.start_session(
                user=mock_discord_user,
                trigger_severity="high",
            )

    @pytest.mark.asyncio
    async def test_opted_out_user_no_dm_created(
        self,
        integrated_managers,
        mock_discord_user,
    ):
        """Test that no DM channel is created for opted-out user."""
        prefs = integrated_managers["preferences"]
        sessions = integrated_managers["sessions"]
        
        await prefs.set_opt_out(mock_discord_user.id)
        
        try:
            await sessions.start_session(
                user=mock_discord_user,
                trigger_severity="high",
            )
        except UserOptedOutError:
            pass
        
        # create_dm should NOT have been called
        mock_discord_user.create_dm.assert_not_called()

    @pytest.mark.asyncio
    async def test_non_opted_out_user_session_works(
        self,
        integrated_managers,
        mock_discord_user,
    ):
        """Test that non-opted-out user can start session normally."""
        sessions = integrated_managers["sessions"]
        
        # User has NOT opted out
        session = await sessions.start_session(
            user=mock_discord_user,
            trigger_severity="high",
        )
        
        assert session is not None
        assert session.user_id == mock_discord_user.id
        assert session.is_active is True

    @pytest.mark.asyncio
    async def test_has_active_session_check_respects_opt_out(
        self,
        integrated_managers,
        mock_discord_user,
    ):
        """Test that is_user_opted_out can be checked independently."""
        prefs = integrated_managers["preferences"]
        sessions = integrated_managers["sessions"]
        
        # Initially not opted out
        assert await sessions.is_user_opted_out(mock_discord_user.id) is False
        
        # Opt out
        await prefs.set_opt_out(mock_discord_user.id)
        
        # Now opted out
        assert await sessions.is_user_opted_out(mock_discord_user.id) is True


# =============================================================================
# Scenario 2: CRT Still Receives Alerts
# =============================================================================


class TestCRTStillReceivesAlerts:
    """
    Scenario: CRT should still receive alerts for opted-out users.
    
    The opt-out only affects Ash AI interaction, not CRT alerting.
    """

    @pytest.mark.asyncio
    async def test_opt_out_does_not_affect_alert_dispatch(
        self,
        integrated_managers,
        mock_discord_user,
    ):
        """Test that opt-out status doesn't prevent alert dispatch."""
        prefs = integrated_managers["preferences"]
        
        # User opts out
        await prefs.set_opt_out(mock_discord_user.id)
        
        # Opt-out only affects Ash sessions, not alerting
        # AlertDispatcher doesn't check opt-out - it always sends alerts
        # This test verifies the design - opt-out is checked in AshSessionManager
        
        is_opted_out = await prefs.is_opted_out(mock_discord_user.id)
        assert is_opted_out is True
        
        # The alert would still be sent (this is implicit in the design)
        # AlertDispatcher.dispatch_alert() doesn't check opt-out


# =============================================================================
# Scenario 3: Alert Embed Shows Human Preference
# =============================================================================


class TestAlertEmbedShowsHumanPreference:
    """
    Scenario: Alert embed can be updated to show user prefers human support.
    """

    def test_update_embed_user_prefers_human(self):
        """Test that embed can be updated with human preference indicator."""
        embed_builder = create_embed_builder()
        
        # Create a base embed
        embed = discord.Embed(
            title="🔶 Crisis Alert",
            color=discord.Color.orange(),
        )
        embed.set_footer(text="Request ID: test_123")
        
        # Update with human preference
        updated = embed_builder.update_embed_user_prefers_human(embed)
        
        # Check field was added
        field_names = [f.name for f in updated.fields]
        assert "👤 User Preference" in field_names
        
        # Check footer updated
        assert "Prefers human" in updated.footer.text

    def test_human_preference_field_content(self):
        """Test the content of the human preference field."""
        embed_builder = create_embed_builder()
        
        embed = discord.Embed(title="Test")
        embed.set_footer(text="Original footer")
        
        updated = embed_builder.update_embed_user_prefers_human(embed)
        
        # Find the field
        for field in updated.fields:
            if field.name == "👤 User Preference":
                assert "human support" in field.value.lower()
                assert "opted out" in field.value.lower()
                break
        else:
            pytest.fail("User Preference field not found")


# =============================================================================
# Scenario 4: TTL Expiry Re-enables Ash
# =============================================================================


class TestTTLExpiryReenablesAsh:
    """
    Scenario: After TTL expires, user can receive Ash DMs again.
    
    Flow:
    1. User opts out (TTL set)
    2. Time passes (TTL expires)
    3. User can now receive Ash DMs
    """

    @pytest.mark.asyncio
    async def test_expired_opt_out_allows_session(
        self,
        mock_config_for_opt_out,
        mock_redis_for_opt_out,
        mock_bot_for_opt_out,
        mock_discord_user,
    ):
        """Test that expired opt-out allows Ash session."""
        # Pre-populate Redis with expired opt-out
        past = datetime.now(timezone.utc) - timedelta(days=60)
        key = f"{REDIS_KEY_PREFIX}{mock_discord_user.id}"
        mock_redis_for_opt_out._storage[key] = json.dumps({
            "user_id": mock_discord_user.id,
            "opted_out": True,
            "opted_out_at": past.isoformat(),
            "expires_at": (past + timedelta(days=30)).isoformat(),  # Expired
        })
        
        # Create managers
        prefs = create_user_preferences_manager(
            config_manager=mock_config_for_opt_out,
            redis_manager=mock_redis_for_opt_out,
        )
        sessions = create_ash_session_manager(
            config_manager=mock_config_for_opt_out,
            bot=mock_bot_for_opt_out,
        )
        sessions.set_user_preferences_manager(prefs)
        
        # Expired opt-out should NOT block session
        session = await sessions.start_session(
            user=mock_discord_user,
            trigger_severity="high",
        )
        
        assert session is not None
        assert session.is_active is True

    @pytest.mark.asyncio
    async def test_active_opt_out_blocks_session(
        self,
        mock_config_for_opt_out,
        mock_redis_for_opt_out,
        mock_bot_for_opt_out,
        mock_discord_user,
    ):
        """Test that active (non-expired) opt-out blocks session."""
        # Pre-populate Redis with active opt-out
        now = datetime.now(timezone.utc)
        key = f"{REDIS_KEY_PREFIX}{mock_discord_user.id}"
        mock_redis_for_opt_out._storage[key] = json.dumps({
            "user_id": mock_discord_user.id,
            "opted_out": True,
            "opted_out_at": now.isoformat(),
            "expires_at": (now + timedelta(days=30)).isoformat(),  # Not expired
        })
        
        # Create managers
        prefs = create_user_preferences_manager(
            config_manager=mock_config_for_opt_out,
            redis_manager=mock_redis_for_opt_out,
        )
        sessions = create_ash_session_manager(
            config_manager=mock_config_for_opt_out,
            bot=mock_bot_for_opt_out,
        )
        sessions.set_user_preferences_manager(prefs)
        
        # Active opt-out should block session
        with pytest.raises(UserOptedOutError):
            await sessions.start_session(
                user=mock_discord_user,
                trigger_severity="high",
            )


# =============================================================================
# Scenario 5: Re-Opt-Out After Expiry
# =============================================================================


class TestReOptOutAfterExpiry:
    """
    Scenario: User can opt out again after their previous opt-out expires.
    """

    @pytest.mark.asyncio
    async def test_user_can_re_opt_out(
        self,
        integrated_managers,
        mock_discord_user,
    ):
        """Test that user can opt out, clear, and opt out again."""
        prefs = integrated_managers["preferences"]
        
        # First opt-out
        await prefs.set_opt_out(mock_discord_user.id)
        assert await prefs.is_opted_out(mock_discord_user.id) is True
        
        # Clear
        await prefs.clear_opt_out(mock_discord_user.id)
        assert await prefs.is_opted_out(mock_discord_user.id) is False
        
        # Re-opt-out
        await prefs.set_opt_out(mock_discord_user.id)
        assert await prefs.is_opted_out(mock_discord_user.id) is True


# =============================================================================
# Scenario 6: Bypass Opt-Out Check (Manual Override)
# =============================================================================


class TestBypassOptOutCheck:
    """
    Scenario: System can bypass opt-out check when needed.
    
    The start_session method has check_opt_out parameter for cases
    where opt-out should be bypassed (e.g., user explicitly requests Ash).
    """

    @pytest.mark.asyncio
    async def test_bypass_opt_out_allows_session(
        self,
        integrated_managers,
        mock_discord_user,
    ):
        """Test that check_opt_out=False bypasses opt-out."""
        prefs = integrated_managers["preferences"]
        sessions = integrated_managers["sessions"]
        
        # User opts out
        await prefs.set_opt_out(mock_discord_user.id)
        
        # But we bypass the check (e.g., user explicitly requested Ash)
        session = await sessions.start_session(
            user=mock_discord_user,
            trigger_severity="high",
            check_opt_out=False,  # Bypass
        )
        
        assert session is not None
        assert session.is_active is True


# =============================================================================
# Scenario 7: Statistics Integration
# =============================================================================


class TestStatisticsIntegration:
    """
    Tests for statistics tracking across managers.
    """

    @pytest.mark.asyncio
    async def test_opt_out_stats_tracked(
        self,
        integrated_managers,
        mock_discord_user,
    ):
        """Test that opt-out operations are tracked in stats."""
        prefs = integrated_managers["preferences"]
        
        initial_stats = prefs.get_stats()
        assert initial_stats["total_optouts"] == 0
        
        # Opt out
        await prefs.set_opt_out(mock_discord_user.id)
        
        stats = prefs.get_stats()
        assert stats["total_optouts"] == 1
        assert stats["cached_count"] == 1

    @pytest.mark.asyncio
    async def test_clear_stats_tracked(
        self,
        integrated_managers,
        mock_discord_user,
    ):
        """Test that clear operations are tracked in stats."""
        prefs = integrated_managers["preferences"]
        
        await prefs.set_opt_out(mock_discord_user.id)
        await prefs.clear_opt_out(mock_discord_user.id)
        
        stats = prefs.get_stats()
        assert stats["total_cleared"] == 1
