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
Slash Command Manager for Ash-Bot Service
----------------------------------------------------------------------------
FILE VERSION: v5.0-9-2.0-5
LAST MODIFIED: 2026-01-06
PHASE: Phase 9 - CRT Workflow Enhancements (Step 9.2)
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-bot
============================================================================

RESPONSIBILITIES:
- Register Discord slash commands on bot startup
- Handle permission checking for commands
- Route commands to appropriate handlers
- Provide CRT staff with operational tools

COMMANDS:
    /ash status              - Show bot status and health (CRT)
    /ash stats [days]        - Show statistics for period (CRT)
    /ash history @user       - Show user's crisis history (CRT)
    /ash config              - Show bot configuration (Admin)
    /ash notes <id> <text>   - Add note to session (CRT)
    /ash optout @user [clear]- Check/manage opt-out status (CRT)

USAGE:
    from src.managers.commands import create_slash_command_manager

    slash_commands = create_slash_command_manager(
        config_manager=config_manager,
        bot=discord_manager.bot,
        redis_manager=redis_manager,
        user_preferences_manager=user_preferences_manager,
        response_metrics_manager=response_metrics_manager,
    )
    
    await slash_commands.register_commands()
"""

import json
import logging
from typing import Optional, List, TYPE_CHECKING

import discord
from discord import app_commands
from discord.ext import commands

if TYPE_CHECKING:
    from src.managers.config_manager import ConfigManager
    from src.managers.storage.redis_manager import RedisManager
    from src.managers.user.user_preferences_manager import UserPreferencesManager
    from src.managers.metrics.response_metrics_manager import ResponseMetricsManager
    from src.managers.health.health_manager import HealthManager
    from src.managers.session.notes_manager import NotesManager

from src.managers.commands.command_handlers import (
    CommandHandlers,
    create_command_handlers,
)

# Module version
__version__ = "v5.0-9-2.0-5"

# Initialize logger
logger = logging.getLogger(__name__)


# =============================================================================
# Permission Levels
# =============================================================================

PERMISSION_LEVELS = {
    "admin": ["Admin", "Server Owner", "Administrator"],
    "crt": ["CRT", "Crisis Response Team", "Crisis Response"],
    "moderator": ["Moderator", "Mod"],
}

COMMAND_PERMISSIONS = {
    "status": "crt",
    "stats": "crt",
    "history": "crt",
    "config": "admin",
    "notes": "crt",
    "optout": "crt",
}


# =============================================================================
# Slash Command Manager
# =============================================================================


class SlashCommandManager:
    """
    Manages Discord slash commands for CRT operations.
    
    Handles command registration, permission checking, and routing
    to appropriate handlers for each command.
    
    Attributes:
        _config: ConfigManager instance
        _bot: Discord bot instance
        _handlers: CommandHandlers for building responses
        _redis: RedisManager for data access
        _preferences: UserPreferencesManager for opt-out
        _metrics: ResponseMetricsManager for statistics
        _allowed_role_ids: Parsed allowed role IDs
        _admin_role_ids: Parsed admin role IDs
        _is_enabled: Whether slash commands are enabled
        _commands_registered: Whether commands have been registered
    
    Example:
        >>> manager = create_slash_command_manager(config, bot, ...)
        >>> await manager.register_commands()
    """
    
    def __init__(
        self,
        config_manager: "ConfigManager",
        bot: commands.Bot,
        redis_manager: Optional["RedisManager"] = None,
        user_preferences_manager: Optional["UserPreferencesManager"] = None,
        response_metrics_manager: Optional["ResponseMetricsManager"] = None,
    ):
        """
        Initialize SlashCommandManager.
        
        Args:
            config_manager: Configuration manager instance
            bot: Discord bot instance
            redis_manager: Redis manager for data access
            user_preferences_manager: User preferences for opt-out
            response_metrics_manager: Response metrics for statistics
            
        Note:
            Use create_slash_command_manager() factory function.
        """
        self._config = config_manager
        self._bot = bot
        self._redis = redis_manager
        self._preferences = user_preferences_manager
        self._metrics = response_metrics_manager
        self._health_manager: Optional["HealthManager"] = None
        
        # Create command handlers
        self._handlers = create_command_handlers(
            config_manager=config_manager,
            redis_manager=redis_manager,
            user_preferences_manager=user_preferences_manager,
            response_metrics_manager=response_metrics_manager,
        )
        
        # Parse configuration
        self._is_enabled = config_manager.get("commands", "enabled", True)
        self._allowed_role_ids = self._parse_role_ids(
            config_manager.get("commands", "allowed_role_ids", "")
        )
        self._admin_role_ids = self._parse_role_ids(
            config_manager.get("commands", "admin_role_ids", "")
        )
        
        # Track registration state
        self._commands_registered = False
        
        logger.info("✅ SlashCommandManager initialized")
        logger.debug(f"   Enabled: {self._is_enabled}")
        logger.debug(f"   Allowed role IDs: {self._allowed_role_ids}")
        logger.debug(f"   Admin role IDs: {self._admin_role_ids}")
    
    def _parse_role_ids(self, role_ids_value) -> List[str]:
        """
        Parse role IDs from various formats into list.
        
        Supports:
        - List of strings: ["123", "456"]
        - JSON string: '["123", "456"]'
        - Legacy comma-separated: "123,456"
        - Single value: "123"
        - Empty/None: []
        
        Args:
            role_ids_value: Role IDs in any supported format
            
        Returns:
            List of role IDs as strings
        """
        if not role_ids_value:
            return []
        
        # If already a list, process each element
        if isinstance(role_ids_value, (list, tuple)):
            result = []
            for item in role_ids_value:
                if item:
                    result.append(str(item).strip())
            return result
        
        # Convert to string if needed
        if not isinstance(role_ids_value, str):
            return [str(role_ids_value).strip()]
        
        role_ids_str = role_ids_value.strip()
        if not role_ids_str:
            return []
        
        # Try JSON parsing first
        if role_ids_str.startswith('['):
            try:
                parsed = json.loads(role_ids_str)
                if isinstance(parsed, list):
                    return [str(item).strip() for item in parsed if item]
            except json.JSONDecodeError:
                pass
        
        # Fall back to comma-separated (legacy support)
        return [role_id.strip() for role_id in role_ids_str.split(",") if role_id.strip()]
    
    def set_health_manager(self, health_manager: "HealthManager") -> None:
        """
        Set the health manager for status checks.
        
        Args:
            health_manager: HealthManager instance
        """
        self._health_manager = health_manager
        self._handlers.set_health_manager(health_manager)
        logger.debug("Health manager set on SlashCommandManager")
    
    def set_notes_manager(self, notes_manager: "NotesManager") -> None:
        """
        Set the notes manager for session documentation.
        
        Phase 9.2: Required for enhanced notes functionality.
        
        Args:
            notes_manager: NotesManager instance
        """
        self._handlers.set_notes_manager(notes_manager)
        logger.debug("Notes manager set on SlashCommandManager")
    
    # =========================================================================
    # Permission Checking
    # =========================================================================
    
    def _check_permission(
        self,
        member: discord.Member,
        required_level: str,
    ) -> bool:
        """
        Check if member has required permission level.
        
        Uses role IDs for reliable permission checking (role names can change,
        but IDs are immutable).
        
        Args:
            member: Discord member to check
            required_level: Required permission level ('crt' or 'admin')
            
        Returns:
            True if member has permission
        """
        # Server owner always has permission
        if member.guild.owner_id == member.id:
            return True
        
        # Get required role IDs for this level
        if required_level == "admin":
            required_role_ids = self._admin_role_ids
        else:
            # CRT level includes both CRT and admin role IDs
            required_role_ids = self._allowed_role_ids
        
        # If no role IDs configured, deny access (fail-safe)
        if not required_role_ids:
            logger.warning(
                f"No role IDs configured for permission level '{required_level}'. "
                "Configure BOT_SLASH_COMMANDS_ALLOWED_ROLE_IDS or BOT_SLASH_COMMANDS_ADMIN_ROLE_IDS."
            )
            return False
        
        # Check if member has any required role by ID
        member_role_ids = [str(role.id) for role in member.roles]
        
        for role_id in required_role_ids:
            if role_id in member_role_ids:
                return True
        
        return False
    
    def _get_permission_level(self, command_name: str) -> str:
        """Get required permission level for a command."""
        return COMMAND_PERMISSIONS.get(command_name, "crt")
    
    # =========================================================================
    # Command Registration
    # =========================================================================
    
    async def register_commands(self) -> bool:
        """
        Register slash commands with Discord.
        
        Returns:
            True if registration successful
        """
        if not self._is_enabled:
            logger.info("⏭️ Slash commands disabled by configuration")
            return False
        
        if self._commands_registered:
            logger.warning("⚠️ Slash commands already registered")
            return True
        
        logger.info("📝 Registering slash commands...")
        
        try:
            # Create command group
            ash_group = app_commands.Group(
                name="ash",
                description="Ash-Bot CRT commands",
            )
            
            # Register individual commands
            self._register_status_command(ash_group)
            self._register_stats_command(ash_group)
            self._register_history_command(ash_group)
            self._register_config_command(ash_group)
            self._register_notes_command(ash_group)
            self._register_optout_command(ash_group)
            
            # Debug: Log registered commands in group
            group_commands = list(ash_group.commands)
            logger.info(f"📋 Commands registered in /ash group: {len(group_commands)}")
            for cmd in group_commands:
                logger.debug(f"   - /ash {cmd.name}: {cmd.description}")
            
            # Clear existing commands first (in case of re-registration)
            self._bot.tree.clear_commands(guild=None)
            
            # Add group to command tree
            self._bot.tree.add_command(ash_group)
            
            # Debug: Log commands in tree
            tree_commands = self._bot.tree.get_commands()
            logger.info(f"📋 Commands in tree before sync: {len(tree_commands)}")
            
            # Sync commands with Discord
            # Note: This syncs globally. For testing, use guild-specific sync
            guild_id = self._config.get("discord", "guild_id")
            if guild_id:
                # Sync to specific guild (faster for development)
                guild = discord.Object(id=int(guild_id))
                # Also clear guild-specific commands first
                self._bot.tree.clear_commands(guild=guild)
                # Copy global commands to guild
                self._bot.tree.copy_global_to(guild=guild)
                synced = await self._bot.tree.sync(guild=guild)
                logger.info(f"✅ Synced {len(synced)} commands to guild {guild_id}")
            else:
                # Global sync (takes up to 1 hour to propagate)
                synced = await self._bot.tree.sync()
                logger.info(f"✅ Synced {len(synced)} commands globally")
            
            self._commands_registered = True
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to register slash commands: {e}", exc_info=True)
            return False
    
    # =========================================================================
    # Individual Command Registration
    # =========================================================================
    
    def _register_status_command(self, group: app_commands.Group) -> None:
        """Register /ash status command."""
        
        @group.command(
            name="status",
            description="Show bot status and health information",
        )
        async def status_command(interaction: discord.Interaction):
            await self._handle_status(interaction)
        
        logger.debug("Registered /ash status command")
    
    def _register_stats_command(self, group: app_commands.Group) -> None:
        """Register /ash stats command."""
        
        @group.command(
            name="stats",
            description="Show crisis statistics for a period",
        )
        @app_commands.describe(
            days="Number of days to show statistics for (default: 7)",
        )
        async def stats_command(
            interaction: discord.Interaction,
            days: int = 7,
        ):
            await self._handle_stats(interaction, days)
        
        logger.debug("Registered /ash stats command")
    
    def _register_history_command(self, group: app_commands.Group) -> None:
        """Register /ash history command."""
        
        @group.command(
            name="history",
            description="Show a user's crisis alert history",
        )
        @app_commands.describe(
            user="User to get history for",
        )
        async def history_command(
            interaction: discord.Interaction,
            user: discord.Member,
        ):
            await self._handle_history(interaction, user)
        
        logger.debug("Registered /ash history command")
    
    def _register_config_command(self, group: app_commands.Group) -> None:
        """Register /ash config command."""
        
        @group.command(
            name="config",
            description="Show current bot configuration (Admin only)",
        )
        async def config_command(interaction: discord.Interaction):
            await self._handle_config(interaction)
        
        logger.debug("Registered /ash config command")
    
    def _register_notes_command(self, group: app_commands.Group) -> None:
        """Register /ash notes command."""
        
        @group.command(
            name="notes",
            description="Add a note to a crisis session",
        )
        @app_commands.describe(
            session_id="Session ID to add note to",
            note="Note text to add",
        )
        async def notes_command(
            interaction: discord.Interaction,
            session_id: str,
            note: str,
        ):
            await self._handle_notes(interaction, session_id, note)
        
        logger.debug("Registered /ash notes command")
    
    def _register_optout_command(self, group: app_commands.Group) -> None:
        """Register /ash optout command."""
        
        @group.command(
            name="optout",
            description="Check or manage user's opt-out status",
        )
        @app_commands.describe(
            user="User to check/manage opt-out for",
            clear="Set to True to clear the user's opt-out status",
        )
        async def optout_command(
            interaction: discord.Interaction,
            user: discord.Member,
            clear: bool = False,
        ):
            await self._handle_optout(interaction, user, clear)
        
        logger.debug("Registered /ash optout command")
    
    # =========================================================================
    # Command Handlers
    # =========================================================================
    
    async def _handle_status(
        self,
        interaction: discord.Interaction,
    ) -> None:
        """
        Handle /ash status command.
        
        Shows bot health and connection status.
        
        Args:
            interaction: Discord interaction
        """
        logger.info(f"📋 /ash status invoked by {interaction.user.display_name}")
        
        # Check permission
        if not self._check_permission(interaction.user, "crt"):
            await interaction.response.send_message(
                "⚠️ You don't have permission to use this command.\n"
                "Required role: CRT or Admin",
                ephemeral=True,
            )
            return
        
        # Defer response (may take a moment to gather status)
        await interaction.response.defer(ephemeral=True)
        
        try:
            embed = await self._handlers.build_status_embed(self._bot)
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Failed to handle /ash status: {e}")
            await interaction.followup.send(
                f"⚠️ Failed to get status: {e}",
                ephemeral=True,
            )
    
    async def _handle_stats(
        self,
        interaction: discord.Interaction,
        days: int = 7,
    ) -> None:
        """
        Handle /ash stats command.
        
        Shows statistics for the specified period.
        
        Args:
            interaction: Discord interaction
            days: Number of days to show stats for
        """
        logger.info(
            f"📊 /ash stats invoked by {interaction.user.display_name} "
            f"(days={days})"
        )
        
        # Check permission
        if not self._check_permission(interaction.user, "crt"):
            await interaction.response.send_message(
                "⚠️ You don't have permission to use this command.\n"
                "Required role: CRT or Admin",
                ephemeral=True,
            )
            return
        
        # Validate days range
        if days < 1 or days > 90:
            await interaction.response.send_message(
                "⚠️ Days must be between 1 and 90.",
                ephemeral=True,
            )
            return
        
        # Defer response
        await interaction.response.defer(ephemeral=True)
        
        try:
            embed = await self._handlers.build_stats_embed(days)
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Failed to handle /ash stats: {e}")
            await interaction.followup.send(
                f"⚠️ Failed to get statistics: {e}",
                ephemeral=True,
            )
    
    async def _handle_history(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
    ) -> None:
        """
        Handle /ash history command.
        
        Shows user's recent crisis alert history.
        
        Args:
            interaction: Discord interaction
            user: User to get history for
        """
        logger.info(
            f"📋 /ash history invoked by {interaction.user.display_name} "
            f"for user {user.display_name}"
        )
        
        # Check permission
        if not self._check_permission(interaction.user, "crt"):
            await interaction.response.send_message(
                "⚠️ You don't have permission to use this command.\n"
                "Required role: CRT or Admin",
                ephemeral=True,
            )
            return
        
        # Defer response
        await interaction.response.defer(ephemeral=True)
        
        try:
            embed = await self._handlers.build_history_embed(user)
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Failed to handle /ash history: {e}")
            await interaction.followup.send(
                f"⚠️ Failed to get history: {e}",
                ephemeral=True,
            )
    
    async def _handle_config(
        self,
        interaction: discord.Interaction,
    ) -> None:
        """
        Handle /ash config command.
        
        Shows current bot configuration (admin only).
        
        Args:
            interaction: Discord interaction
        """
        logger.info(f"⚙️ /ash config invoked by {interaction.user.display_name}")
        
        # Check permission (admin required)
        if not self._check_permission(interaction.user, "admin"):
            await interaction.response.send_message(
                "⚠️ You don't have permission to use this command.\n"
                "Required role: Admin",
                ephemeral=True,
            )
            return
        
        # Defer response
        await interaction.response.defer(ephemeral=True)
        
        try:
            embed = await self._handlers.build_config_embed()
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Failed to handle /ash config: {e}")
            await interaction.followup.send(
                f"⚠️ Failed to get configuration: {e}",
                ephemeral=True,
            )
    
    async def _handle_notes(
        self,
        interaction: discord.Interaction,
        session_id: str,
        note_text: str,
    ) -> None:
        """
        Handle /ash notes command.
        
        Adds a note to a crisis session.
        
        Args:
            interaction: Discord interaction
            session_id: Session ID to add note to
            note_text: Note content
        """
        logger.info(
            f"📝 /ash notes invoked by {interaction.user.display_name} "
            f"for session {session_id}"
        )
        
        # Check permission
        if not self._check_permission(interaction.user, "crt"):
            await interaction.response.send_message(
                "⚠️ You don't have permission to use this command.\n"
                "Required role: CRT or Admin",
                ephemeral=True,
            )
            return
        
        # Validate input
        if not session_id.strip():
            await interaction.response.send_message(
                "⚠️ Session ID cannot be empty.",
                ephemeral=True,
            )
            return
        
        if not note_text.strip():
            await interaction.response.send_message(
                "⚠️ Note text cannot be empty.",
                ephemeral=True,
            )
            return
        
        if len(note_text) > 2000:
            await interaction.response.send_message(
                "⚠️ Note text cannot exceed 2000 characters.",
                ephemeral=True,
            )
            return
        
        # Defer response
        await interaction.response.defer(ephemeral=True)
        
        try:
            success, message = await self._handlers.add_session_note(
                session_id=session_id.strip(),
                note_text=note_text.strip(),
                author_id=interaction.user.id,
                author_name=interaction.user.display_name,
            )
            
            if success:
                embed = self._handlers.build_note_success_embed(
                    session_id=session_id.strip(),
                    note_text=note_text.strip(),
                    author_name=interaction.user.display_name,
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
            else:
                await interaction.followup.send(
                    f"⚠️ {message}",
                    ephemeral=True,
                )
            
        except Exception as e:
            logger.error(f"Failed to handle /ash notes: {e}")
            await interaction.followup.send(
                f"⚠️ Failed to add note: {e}",
                ephemeral=True,
            )
    
    async def _handle_optout(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        clear: bool = False,
    ) -> None:
        """
        Handle /ash optout command.
        
        Checks or manages user's opt-out status.
        
        Args:
            interaction: Discord interaction
            user: User to check/manage
            clear: Whether to clear opt-out status
        """
        logger.info(
            f"👤 /ash optout invoked by {interaction.user.display_name} "
            f"for user {user.display_name} (clear={clear})"
        )
        
        # Check permission
        if not self._check_permission(interaction.user, "crt"):
            await interaction.response.send_message(
                "⚠️ You don't have permission to use this command.\n"
                "Required role: CRT or Admin",
                ephemeral=True,
            )
            return
        
        # Defer response
        await interaction.response.defer(ephemeral=True)
        
        try:
            if clear:
                # Clear opt-out with confirmation
                success, message = await self._handlers.clear_optout(user)
                
                if success:
                    await interaction.followup.send(
                        f"✅ {message}",
                        ephemeral=True,
                    )
                else:
                    await interaction.followup.send(
                        f"⚠️ {message}",
                        ephemeral=True,
                    )
            else:
                # Show opt-out status
                embed = await self._handlers.build_optout_embed(user)
                await interaction.followup.send(embed=embed, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Failed to handle /ash optout: {e}")
            await interaction.followup.send(
                f"⚠️ Failed to manage opt-out: {e}",
                ephemeral=True,
            )
    
    # =========================================================================
    # Properties
    # =========================================================================
    
    @property
    def is_enabled(self) -> bool:
        """Check if slash commands are enabled."""
        return self._is_enabled
    
    @property
    def is_registered(self) -> bool:
        """Check if commands have been registered."""
        return self._commands_registered
    
    @property
    def allowed_role_ids(self) -> List[str]:
        """Get list of allowed role IDs."""
        return self._allowed_role_ids.copy()
    
    @property
    def admin_role_ids(self) -> List[str]:
        """Get list of admin role IDs."""
        return self._admin_role_ids.copy()
    
    def __repr__(self) -> str:
        """String representation for debugging."""
        status = "enabled" if self._is_enabled else "disabled"
        registered = "registered" if self._commands_registered else "not registered"
        return f"SlashCommandManager(status={status}, {registered})"


# =============================================================================
# Factory Function
# =============================================================================


def create_slash_command_manager(
    config_manager: "ConfigManager",
    bot: commands.Bot,
    redis_manager: Optional["RedisManager"] = None,
    user_preferences_manager: Optional["UserPreferencesManager"] = None,
    response_metrics_manager: Optional["ResponseMetricsManager"] = None,
) -> SlashCommandManager:
    """
    Factory function for SlashCommandManager.
    
    Creates a configured SlashCommandManager instance with all dependencies.
    Following Clean Architecture v5.1 Rule #1: Factory Functions.
    
    Args:
        config_manager: Configuration manager instance
        bot: Discord bot instance
        redis_manager: Redis manager for data access
        user_preferences_manager: User preferences for opt-out
        response_metrics_manager: Response metrics for statistics
        
    Returns:
        Configured SlashCommandManager instance
        
    Example:
        >>> manager = create_slash_command_manager(
        ...     config_manager=config,
        ...     bot=discord_manager.bot,
        ...     redis_manager=redis,
        ...     user_preferences_manager=prefs,
        ...     response_metrics_manager=metrics,
        ... )
        >>> await manager.register_commands()
    """
    logger.info("🏭 Creating SlashCommandManager")
    
    if redis_manager:
        logger.info("📚 Redis integration enabled for commands")
    else:
        logger.info("⚠️ Redis not available (some commands may be limited)")
    
    if user_preferences_manager:
        logger.info("👤 User preferences integration enabled")
    else:
        logger.info("⚠️ User preferences not available")
    
    if response_metrics_manager:
        logger.info("📊 Response metrics integration enabled")
    else:
        logger.info("⚠️ Response metrics not available")
    
    return SlashCommandManager(
        config_manager=config_manager,
        bot=bot,
        redis_manager=redis_manager,
        user_preferences_manager=user_preferences_manager,
        response_metrics_manager=response_metrics_manager,
    )


# =============================================================================
# Export public interface
# =============================================================================

__all__ = [
    "SlashCommandManager",
    "create_slash_command_manager",
    "PERMISSION_LEVELS",
    "COMMAND_PERMISSIONS",
]
