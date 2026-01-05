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
Unit Tests for Slash Command Manager (Phase 9.1)
----------------------------------------------------------------------------
FILE VERSION: v5.0-9-1.0-1
LAST MODIFIED: 2026-01-05
PHASE: Phase 9 - CRT Workflow Enhancements (Step 9.1)
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-bot
============================================================================

TESTS COVERED:
- SlashCommandManager initialization
- Permission checking (CRT vs Admin roles)
- Command handler building
- Configuration parsing
- Factory function creation
"""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from datetime import datetime

# Import test subjects
from src.managers.commands.slash_command_manager import (
    SlashCommandManager,
    create_slash_command_manager,
    PERMISSION_LEVELS,
    COMMAND_PERMISSIONS,
)
from src.managers.commands.command_handlers import (
    CommandHandlers,
    create_command_handlers,
    SEVERITY_EMOJIS,
    SEVERITY_COLORS,
)

# Module version
__version__ = "v5.0-9-1.0-1"


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def mock_config_manager():
    """Create mock ConfigManager."""
    config = MagicMock()
    config.get = MagicMock(side_effect=lambda section, key, default=None: {
        ("commands", "enabled"): True,
        ("commands", "allowed_roles"): "CRT,Admin,Moderator",
        ("commands", "admin_roles"): "Admin",
        ("alerting", "enabled"): True,
        ("alerting", "min_severity_to_alert"): "medium",
        ("auto_initiate", "enabled"): True,
        ("auto_initiate", "delay_minutes"): 3,
        ("auto_initiate", "min_severity"): "medium",
        ("weekly_report", "enabled"): True,
        ("weekly_report", "report_day"): "monday",
        ("weekly_report", "report_hour"): 9,
        ("data_retention", "enabled"): True,
        ("data_retention", "alert_metrics_days"): 90,
        ("data_retention", "session_data_days"): 30,
        ("data_retention", "message_history_days"): 7,
        ("discord", "guild_id"): "123456789",
    }.get((section, key), default))
    return config


@pytest.fixture
def mock_bot():
    """Create mock Discord bot."""
    bot = MagicMock()
    bot.tree = MagicMock()
    bot.tree.add_command = MagicMock()
    bot.tree.sync = AsyncMock(return_value=[])
    bot.is_ready = MagicMock(return_value=True)
    bot.latency = 0.045  # 45ms
    bot.ash_session_manager = None
    bot.ash_personality_manager = None
    return bot


@pytest.fixture
def mock_redis_manager():
    """Create mock RedisManager."""
    redis = MagicMock()
    redis.health_check = AsyncMock(return_value=True)
    redis.rpush = AsyncMock()
    redis.expire = AsyncMock()
    return redis


@pytest.fixture
def mock_user_preferences_manager():
    """Create mock UserPreferencesManager."""
    prefs = MagicMock()
    prefs.is_opted_out = AsyncMock(return_value=False)
    prefs.get_opt_out_info = AsyncMock(return_value=None)
    prefs.clear_opt_out = AsyncMock()
    return prefs


@pytest.fixture
def mock_response_metrics_manager():
    """Create mock ResponseMetricsManager."""
    metrics = MagicMock()
    metrics.is_enabled = True
    metrics.get_daily_stats = AsyncMock(return_value={"total_alerts": 5})
    metrics.get_period_stats = AsyncMock(return_value={
        "total_alerts": 12,
        "critical_count": 0,
        "high_count": 3,
        "medium_count": 6,
        "low_count": 3,
        "avg_acknowledge_seconds": 165,
        "avg_ash_contact_seconds": 72,
        "avg_human_response_seconds": 510,
        "ash_sessions": 8,
        "auto_initiated": 2,
        "user_optouts": 1,
    })
    metrics.get_user_alert_history = AsyncMock(return_value=[])
    return metrics


@pytest.fixture
def mock_discord_member():
    """Create mock Discord member."""
    member = MagicMock()
    member.id = 123456789
    member.display_name = "TestUser"
    member.roles = []
    member.guild = MagicMock()
    member.guild.owner_id = 999999999
    return member


@pytest.fixture
def mock_discord_interaction():
    """Create mock Discord interaction."""
    interaction = MagicMock()
    interaction.user = MagicMock()
    interaction.user.id = 123456789
    interaction.user.display_name = "TestCRT"
    interaction.response = MagicMock()
    interaction.response.send_message = AsyncMock()
    interaction.response.defer = AsyncMock()
    interaction.followup = MagicMock()
    interaction.followup.send = AsyncMock()
    return interaction


# =============================================================================
# SlashCommandManager Tests
# =============================================================================


class TestSlashCommandManagerInit:
    """Tests for SlashCommandManager initialization."""
    
    def test_init_with_defaults(self, mock_config_manager, mock_bot):
        """Test initialization with default configuration."""
        manager = SlashCommandManager(
            config_manager=mock_config_manager,
            bot=mock_bot,
        )
        
        assert manager.is_enabled is True
        assert "CRT" in manager.allowed_roles
        assert "Admin" in manager.allowed_roles
        assert "Admin" in manager.admin_roles
        assert manager.is_registered is False
    
    def test_init_with_all_dependencies(
        self,
        mock_config_manager,
        mock_bot,
        mock_redis_manager,
        mock_user_preferences_manager,
        mock_response_metrics_manager,
    ):
        """Test initialization with all dependencies."""
        manager = SlashCommandManager(
            config_manager=mock_config_manager,
            bot=mock_bot,
            redis_manager=mock_redis_manager,
            user_preferences_manager=mock_user_preferences_manager,
            response_metrics_manager=mock_response_metrics_manager,
        )
        
        assert manager._redis is mock_redis_manager
        assert manager._preferences is mock_user_preferences_manager
        assert manager._metrics is mock_response_metrics_manager
    
    def test_init_disabled(self, mock_config_manager, mock_bot):
        """Test initialization when disabled by config."""
        mock_config_manager.get = MagicMock(side_effect=lambda section, key, default=None: {
            ("commands", "enabled"): False,
            ("commands", "allowed_roles"): "CRT,Admin",
            ("commands", "admin_roles"): "Admin",
        }.get((section, key), default))
        
        manager = SlashCommandManager(
            config_manager=mock_config_manager,
            bot=mock_bot,
        )
        
        assert manager.is_enabled is False


class TestSlashCommandManagerPermissions:
    """Tests for permission checking."""
    
    def test_permission_check_server_owner(
        self,
        mock_config_manager,
        mock_bot,
        mock_discord_member,
    ):
        """Test that server owner always has permission."""
        manager = SlashCommandManager(
            config_manager=mock_config_manager,
            bot=mock_bot,
        )
        
        # Make member the guild owner
        mock_discord_member.guild.owner_id = mock_discord_member.id
        
        assert manager._check_permission(mock_discord_member, "admin") is True
        assert manager._check_permission(mock_discord_member, "crt") is True
    
    def test_permission_check_crt_role(
        self,
        mock_config_manager,
        mock_bot,
        mock_discord_member,
    ):
        """Test CRT role permission check."""
        manager = SlashCommandManager(
            config_manager=mock_config_manager,
            bot=mock_bot,
        )
        
        # Add CRT role to member
        crt_role = MagicMock()
        crt_role.name = "CRT"
        mock_discord_member.roles = [crt_role]
        
        assert manager._check_permission(mock_discord_member, "crt") is True
        assert manager._check_permission(mock_discord_member, "admin") is False
    
    def test_permission_check_admin_role(
        self,
        mock_config_manager,
        mock_bot,
        mock_discord_member,
    ):
        """Test Admin role permission check."""
        manager = SlashCommandManager(
            config_manager=mock_config_manager,
            bot=mock_bot,
        )
        
        # Add Admin role to member
        admin_role = MagicMock()
        admin_role.name = "Admin"
        mock_discord_member.roles = [admin_role]
        
        assert manager._check_permission(mock_discord_member, "crt") is True
        assert manager._check_permission(mock_discord_member, "admin") is True
    
    def test_permission_check_no_role(
        self,
        mock_config_manager,
        mock_bot,
        mock_discord_member,
    ):
        """Test permission check with no matching roles."""
        manager = SlashCommandManager(
            config_manager=mock_config_manager,
            bot=mock_bot,
        )
        
        # No roles
        mock_discord_member.roles = []
        
        assert manager._check_permission(mock_discord_member, "crt") is False
        assert manager._check_permission(mock_discord_member, "admin") is False


class TestSlashCommandManagerRegistration:
    """Tests for command registration."""
    
    @pytest.mark.asyncio
    async def test_register_commands_success(
        self,
        mock_config_manager,
        mock_bot,
    ):
        """Test successful command registration."""
        manager = SlashCommandManager(
            config_manager=mock_config_manager,
            bot=mock_bot,
        )
        
        result = await manager.register_commands()
        
        assert result is True
        assert manager.is_registered is True
        mock_bot.tree.add_command.assert_called_once()
        mock_bot.tree.sync.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_register_commands_disabled(
        self,
        mock_config_manager,
        mock_bot,
    ):
        """Test registration when disabled."""
        mock_config_manager.get = MagicMock(side_effect=lambda section, key, default=None: {
            ("commands", "enabled"): False,
            ("commands", "allowed_roles"): "CRT,Admin",
            ("commands", "admin_roles"): "Admin",
        }.get((section, key), default))
        
        manager = SlashCommandManager(
            config_manager=mock_config_manager,
            bot=mock_bot,
        )
        
        result = await manager.register_commands()
        
        assert result is False
        assert manager.is_registered is False
    
    @pytest.mark.asyncio
    async def test_register_commands_already_registered(
        self,
        mock_config_manager,
        mock_bot,
    ):
        """Test registration when already registered."""
        manager = SlashCommandManager(
            config_manager=mock_config_manager,
            bot=mock_bot,
        )
        
        # First registration
        await manager.register_commands()
        
        # Second registration should return True but not re-register
        result = await manager.register_commands()
        
        assert result is True
        # Should only be called once
        assert mock_bot.tree.add_command.call_count == 1


# =============================================================================
# CommandHandlers Tests
# =============================================================================


class TestCommandHandlersInit:
    """Tests for CommandHandlers initialization."""
    
    def test_init_minimal(self, mock_config_manager):
        """Test initialization with minimal dependencies."""
        handlers = CommandHandlers(
            config_manager=mock_config_manager,
        )
        
        assert handlers._config is mock_config_manager
        assert handlers._redis is None
        assert handlers._preferences is None
        assert handlers._metrics is None
    
    def test_init_full(
        self,
        mock_config_manager,
        mock_redis_manager,
        mock_user_preferences_manager,
        mock_response_metrics_manager,
    ):
        """Test initialization with all dependencies."""
        handlers = CommandHandlers(
            config_manager=mock_config_manager,
            redis_manager=mock_redis_manager,
            user_preferences_manager=mock_user_preferences_manager,
            response_metrics_manager=mock_response_metrics_manager,
        )
        
        assert handlers._redis is mock_redis_manager
        assert handlers._preferences is mock_user_preferences_manager
        assert handlers._metrics is mock_response_metrics_manager


class TestCommandHandlersStatus:
    """Tests for status command handler."""
    
    @pytest.mark.asyncio
    async def test_build_status_embed(
        self,
        mock_config_manager,
        mock_bot,
    ):
        """Test building status embed."""
        handlers = CommandHandlers(
            config_manager=mock_config_manager,
        )
        
        embed = await handlers.build_status_embed(mock_bot)
        
        assert embed.title == "🤖 Ash-Bot Status"
        assert len(embed.fields) > 0
        # Check Discord field is present
        field_names = [f.name for f in embed.fields]
        assert "📡 Discord" in field_names


class TestCommandHandlersStats:
    """Tests for stats command handler."""
    
    @pytest.mark.asyncio
    async def test_build_stats_embed_no_metrics(self, mock_config_manager):
        """Test building stats embed without metrics manager."""
        handlers = CommandHandlers(
            config_manager=mock_config_manager,
        )
        
        embed = await handlers.build_stats_embed(days=7)
        
        assert "not available" in embed.description.lower()
    
    @pytest.mark.asyncio
    async def test_build_stats_embed_with_metrics(
        self,
        mock_config_manager,
        mock_response_metrics_manager,
    ):
        """Test building stats embed with metrics."""
        handlers = CommandHandlers(
            config_manager=mock_config_manager,
            response_metrics_manager=mock_response_metrics_manager,
        )
        
        embed = await handlers.build_stats_embed(days=7)
        
        assert embed.title == "📊 Ash-Bot Statistics (Last 7 Days)"
        field_names = [f.name for f in embed.fields]
        assert "📈 Alerts" in field_names


class TestCommandHandlersHistory:
    """Tests for history command handler."""
    
    @pytest.mark.asyncio
    async def test_build_history_embed_no_redis(
        self,
        mock_config_manager,
        mock_discord_member,
    ):
        """Test building history embed without Redis."""
        handlers = CommandHandlers(
            config_manager=mock_config_manager,
        )
        
        embed = await handlers.build_history_embed(mock_discord_member)
        
        assert "not available" in embed.description.lower()


class TestCommandHandlersConfig:
    """Tests for config command handler."""
    
    @pytest.mark.asyncio
    async def test_build_config_embed(self, mock_config_manager):
        """Test building config embed."""
        handlers = CommandHandlers(
            config_manager=mock_config_manager,
        )
        
        embed = await handlers.build_config_embed()
        
        assert embed.title == "⚙️ Ash-Bot Configuration"
        field_names = [f.name for f in embed.fields]
        assert "🔔 Alerting" in field_names
        assert "⏰ Auto-Initiate" in field_names
        assert "📊 Reporting" in field_names
        assert "🗄️ Retention" in field_names


class TestCommandHandlersNotes:
    """Tests for notes command handler."""
    
    @pytest.mark.asyncio
    async def test_add_session_note_no_redis(self, mock_config_manager):
        """Test adding note without Redis."""
        handlers = CommandHandlers(
            config_manager=mock_config_manager,
        )
        
        success, message = await handlers.add_session_note(
            session_id="test_session",
            note_text="Test note",
            author_id=123,
            author_name="Tester",
        )
        
        assert success is False
        assert "not available" in message.lower()
    
    @pytest.mark.asyncio
    async def test_add_session_note_success(
        self,
        mock_config_manager,
        mock_redis_manager,
    ):
        """Test adding note with Redis."""
        handlers = CommandHandlers(
            config_manager=mock_config_manager,
            redis_manager=mock_redis_manager,
        )
        
        success, message = await handlers.add_session_note(
            session_id="test_session",
            note_text="Test note",
            author_id=123,
            author_name="Tester",
        )
        
        assert success is True
        assert "test_session" in message
        mock_redis_manager.rpush.assert_called_once()


class TestCommandHandlersOptout:
    """Tests for optout command handler."""
    
    @pytest.mark.asyncio
    async def test_build_optout_embed_no_preferences(
        self,
        mock_config_manager,
        mock_discord_member,
    ):
        """Test building optout embed without preferences manager."""
        handlers = CommandHandlers(
            config_manager=mock_config_manager,
        )
        
        embed = await handlers.build_optout_embed(mock_discord_member)
        
        assert "not available" in embed.description.lower()
    
    @pytest.mark.asyncio
    async def test_build_optout_embed_not_opted_out(
        self,
        mock_config_manager,
        mock_user_preferences_manager,
        mock_discord_member,
    ):
        """Test building optout embed for non-opted-out user."""
        handlers = CommandHandlers(
            config_manager=mock_config_manager,
            user_preferences_manager=mock_user_preferences_manager,
        )
        
        embed = await handlers.build_optout_embed(mock_discord_member)
        
        field_values = [f.value for f in embed.fields]
        assert any("Not opted out" in v for v in field_values)
    
    @pytest.mark.asyncio
    async def test_clear_optout_success(
        self,
        mock_config_manager,
        mock_user_preferences_manager,
        mock_discord_member,
    ):
        """Test clearing optout status."""
        mock_user_preferences_manager.is_opted_out = AsyncMock(return_value=True)
        
        handlers = CommandHandlers(
            config_manager=mock_config_manager,
            user_preferences_manager=mock_user_preferences_manager,
        )
        
        success, message = await handlers.clear_optout(mock_discord_member)
        
        assert success is True
        mock_user_preferences_manager.clear_opt_out.assert_called_once()


# =============================================================================
# Factory Function Tests
# =============================================================================


class TestFactoryFunctions:
    """Tests for factory functions."""
    
    def test_create_slash_command_manager(
        self,
        mock_config_manager,
        mock_bot,
    ):
        """Test SlashCommandManager factory function."""
        manager = create_slash_command_manager(
            config_manager=mock_config_manager,
            bot=mock_bot,
        )
        
        assert isinstance(manager, SlashCommandManager)
        assert manager._config is mock_config_manager
        assert manager._bot is mock_bot
    
    def test_create_command_handlers(self, mock_config_manager):
        """Test CommandHandlers factory function."""
        handlers = create_command_handlers(
            config_manager=mock_config_manager,
        )
        
        assert isinstance(handlers, CommandHandlers)
        assert handlers._config is mock_config_manager


# =============================================================================
# Constants Tests
# =============================================================================


class TestConstants:
    """Tests for module constants."""
    
    def test_permission_levels(self):
        """Test PERMISSION_LEVELS constant."""
        assert "admin" in PERMISSION_LEVELS
        assert "crt" in PERMISSION_LEVELS
        assert "Admin" in PERMISSION_LEVELS["admin"]
        assert "CRT" in PERMISSION_LEVELS["crt"]
    
    def test_command_permissions(self):
        """Test COMMAND_PERMISSIONS constant."""
        assert COMMAND_PERMISSIONS["status"] == "crt"
        assert COMMAND_PERMISSIONS["config"] == "admin"
        assert COMMAND_PERMISSIONS["notes"] == "crt"
        assert COMMAND_PERMISSIONS["optout"] == "crt"
    
    def test_severity_emojis(self):
        """Test SEVERITY_EMOJIS constant."""
        assert "critical" in SEVERITY_EMOJIS
        assert "high" in SEVERITY_EMOJIS
        assert "medium" in SEVERITY_EMOJIS
        assert "low" in SEVERITY_EMOJIS
        assert "safe" in SEVERITY_EMOJIS
    
    def test_severity_colors(self):
        """Test SEVERITY_COLORS constant."""
        assert "critical" in SEVERITY_COLORS
        assert "high" in SEVERITY_COLORS
        assert "medium" in SEVERITY_COLORS
        assert "low" in SEVERITY_COLORS
        assert "safe" in SEVERITY_COLORS


# =============================================================================
# Integration Tests
# =============================================================================


class TestIntegration:
    """Integration tests for slash command system."""
    
    @pytest.mark.asyncio
    async def test_full_status_flow(
        self,
        mock_config_manager,
        mock_bot,
        mock_redis_manager,
        mock_discord_interaction,
    ):
        """Test full status command flow."""
        # Setup CRT role on interaction user
        crt_role = MagicMock()
        crt_role.name = "CRT"
        mock_discord_interaction.user.roles = [crt_role]
        mock_discord_interaction.user.guild = MagicMock()
        mock_discord_interaction.user.guild.owner_id = 999999999
        
        manager = SlashCommandManager(
            config_manager=mock_config_manager,
            bot=mock_bot,
            redis_manager=mock_redis_manager,
        )
        
        # Call the handler directly (simulating command invocation)
        await manager._handle_status(mock_discord_interaction)
        
        # Verify deferred and followup was sent
        mock_discord_interaction.response.defer.assert_called_once_with(ephemeral=True)
        mock_discord_interaction.followup.send.assert_called_once()


# =============================================================================
# Main Test Runner
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
