"""
Ash-Bot: Crisis Detection Bot for The Alphabet Cartel Discord Community
********************************************************************************
Discord Client Manager for Ash-Bot
---
FILE VERSION: v3.1-1a-1-2
LAST MODIFIED: 2025-10-06
PHASE: 1a Step 1
CLEAN ARCHITECTURE: v3.1
Repository: https://github.com/the-alphabet-cartel/ash-bot
Community: The Alphabet Cartel - https://discord.gg/alphabetcartel | https://alphabetcartel.org
"""

import discord
from discord.ext import commands
import logging
import asyncio
from datetime import datetime, timezone
from typing import Dict, Any, Optional, Callable
from managers.unified_config import UnifiedConfigManager
from managers.logging_config import LoggingConfigManager

logger = logging.getLogger(__name__)

class DiscordClientManager(commands.Bot):
    """
    Discord Client Manager for Ash-Bot
    
    Responsibilities:
    - Discord bot initialization and connection
    - Guild management and validation
    - Event routing to appropriate managers
    - Health monitoring and reconnection logic
    - Discord intents and permissions management
    """
    
    # ========================================================================
    # INITIALIZE
    # ========================================================================
    def __init__(self, config_manager: UnifiedConfigManager, logging_manager: LoggingConfigManager, **kwargs):
        """
        Initialize DiscordClientManager
        
        Args:
            config_manager: UnifiedConfigManager instance (ALWAYS FIRST PARAMETER)
            logging_manager: LoggingConfigManager instance
            **kwargs: Additional manager dependencies
        """
        self.config_manager = config_manager
        self.logging_manager = logging_manager
        
        # Load configuration
        self.config = self.config_manager.get_config_section('discord_config')
        
        # Store additional manager references
        self.nlp_manager = kwargs.get('nlp_manager')
        self.crisis_manager = kwargs.get('crisis_manager')
        self.conversation_manager = kwargs.get('conversation_manager')
        self.crisis_response_manager = kwargs.get('crisis_response_manager')
        self.learning_manager = kwargs.get('learning_manager')
        self.api_manager = kwargs.get('api_manager')
        
        # Bot configuration from JSON config
        self.guild_id = self.config.get('discord_settings', {}).get('guild_id')

        # NOTE: command_prefix is required by discord.py but unused
        # We use slash commands exclusively via app_commands
        # Setting to dummy value to satisfy discord.py requirements
        self.command_prefix = '/'  # Dummy prefix - not used with slash commands
        
        # Setup Discord intents
        intents = self._setup_intents()
        
        # Initialize Discord Bot
        commands.Bot.__init__(
            self,
            command_prefix=self.command_prefix,
            intents=intents,
            help_command=None
        )
        
        # Bot state tracking
        self.start_time = datetime.now(timezone.utc)
        self.is_ready_complete = False
        self.connection_healthy = False
        
        # Event handler registry
        self.event_handlers = {}
        
        # Initialize manager state
        self._initialize_manager()
        
        logger.info(f"✅ DiscordClientManager initialized successfully")
    
    def _initialize_manager(self):
        """Initialize manager-specific state"""
        try:
            # Validate critical configuration
            self._validate_discord_config()
            
            # Register core event handlers
            self._register_core_events()
            
            logger.info("🤖 Discord client manager initialization complete")
            
        except Exception as e:
            logger.error(f"❌ Discord client manager initialization failed: {e}")
            # Implement resilient fallback per Rule #5
            self._apply_fallback_configuration()
    # ========================================================================
    
    # ========================================================================
    # SETUP
    # ========================================================================
    def _setup_intents(self) -> discord.Intents:
        """
        Setup Discord intents based on configuration
        
        Returns:
            Configured Discord intents
        """
        try:
            intents = discord.Intents.default()
            
            # Required intents for crisis detection
            intents.message_content = True
            intents.members = True
            intents.reactions = True
            
            # Optional intents based on configuration
            intent_config = self.config.get('discord_settings', {}).get('intents', {})
            
            if intent_config.get('guilds', True):
                intents.guilds = True
            if intent_config.get('guild_messages', True):
                intents.guild_messages = True
            if intent_config.get('direct_messages', False):
                intents.dm_messages = True
            
            logger.info("🔧 Discord intents configured successfully")
            return intents
            
        except Exception as e:
            logger.error(f"❌ Failed to setup Discord intents: {e}")
            # Fallback to safe default intents
            intents = discord.Intents.default()
            intents.message_content = True
            intents.members = True
            logger.warning("⚠️ Using fallback Discord intents")
            return intents
    
    def _validate_discord_config(self):
        """Validate Discord configuration with resilient fallbacks"""
        errors = []
        
        # Validate guild ID
        if not self.guild_id:
            errors.append("Guild ID not configured")
        else:
            try:
                self.guild_id = int(self.guild_id)
            except (ValueError, TypeError):
                errors.append(f"Invalid guild ID: {self.guild_id}")
        
        # NOTE: command_prefix validation removed - we use slash commands exclusively
        
        if errors:
            logger.warning(f"⚠️ Discord configuration issues: {', '.join(errors)}")
            logger.warning("⚠️ Attempting to continue with fallback configuration")
    
    def _apply_fallback_configuration(self):
        """Apply fallback configuration for resilient operation"""
        try:
            # Apply safe defaults from environment variables (Rule #7)
            self.guild_id = self.config_manager.get_env_int('BOT_GUILD_ID', 0)
            # NOTE: command_prefix not needed - we use slash commands exclusively
            
            logger.info("🛡️ Fallback configuration applied successfully")
            
        except Exception as e:
            logger.error(f"❌ Fallback configuration failed: {e}")
            # System can still function without guild restriction
            self.guild_id = None
    
    def _register_core_events(self):
        """Register core Discord event handlers"""
        # Register the actual event handlers
        self.add_listener(self._on_ready_handler, 'on_ready')
        self.add_listener(self._on_message_handler, 'on_message')
        self.add_listener(self._on_reaction_add_handler, 'on_reaction_add')
        self.add_listener(self._on_reaction_remove_handler, 'on_reaction_remove')
        self.add_listener(self._on_disconnect_handler, 'on_disconnect')
        self.add_listener(self._on_resumed_handler, 'on_resumed')
        
        logger.info("📡 Core Discord event handlers registered")
    
    async def _on_ready_handler(self):
        """Handle Discord on_ready event"""
        try:
            self.connection_healthy = True
            self.is_ready_complete = True
            
            logger.info(f'✅ {self.user} has awakened in The Alphabet Cartel (Clean Architecture v3.1)')
            
            # Validate guild connection
            await self._validate_guild_connection()
            
            # Set bot status
            await self._set_bot_status()
            
            # Initialize additional managers if needed
            await self._initialize_dependent_managers()
            
            logger.info("🎉 Discord client ready and operational")
            
        except Exception as e:
            logger.error(f"❌ Error in on_ready handler: {e}")
            self.connection_healthy = False
    
    async def _on_message_handler(self, message: discord.Message):
        """Route message events to appropriate managers"""
        try:
            # Ignore bot messages
            if message.author.bot:
                return
            
            # Guild restriction check
            if self.guild_id and message.guild and message.guild.id != self.guild_id:
                return
            
            # Route to conversation manager if available
            if self.conversation_manager:
                await self.conversation_manager.handle_message(message)
            else:
                logger.debug("📭 No conversation manager available for message routing")
                
        except Exception as e:
            logger.error(f"❌ Error in message handler: {e}")
            # Continue operation - don't crash on message handling errors
    
    async def _on_reaction_add_handler(self, reaction: discord.Reaction, user: discord.User):
        """Route reaction add events to appropriate managers"""
        try:
            # Ignore bot reactions
            if user.bot:
                return
            
            # Guild restriction check
            if self.guild_id and reaction.message.guild and reaction.message.guild.id != self.guild_id:
                return
            
            # Route to crisis response manager if available
            if self.crisis_response_manager:
                await self.crisis_response_manager.handle_reaction_add(reaction, user)
            else:
                logger.debug("📭 No crisis response manager available for reaction routing")
                
        except Exception as e:
            logger.error(f"❌ Error in reaction add handler: {e}")
    
    async def _on_reaction_remove_handler(self, reaction: discord.Reaction, user: discord.User):
        """Route reaction remove events to appropriate managers"""
        try:
            # Ignore bot reactions
            if user.bot:
                return
            
            # Route to crisis response manager if available
            if self.crisis_response_manager:
                await self.crisis_response_manager.handle_reaction_remove(reaction, user)
                
        except Exception as e:
            logger.error(f"❌ Error in reaction remove handler: {e}")
    
    async def _on_disconnect_handler(self):
        """Handle Discord disconnect events"""
        self.connection_healthy = False
        logger.warning("🔌 Discord connection lost")
    
    async def _on_resumed_handler(self):
        """Handle Discord connection resume events"""
        self.connection_healthy = True
        logger.info("🔌 Discord connection resumed")
    
    async def _validate_guild_connection(self):
        """Validate connection to configured guild"""
        if not self.guild_id:
            logger.warning("⚠️ No guild ID configured - bot will operate in all guilds")
            return
        
        guild = discord.utils.get(self.guilds, id=self.guild_id)
        if guild:
            logger.info(f'🏠 Connected to guild: {guild.name} (ID: {guild.id})')
            
            # Check bot permissions
            await self._check_bot_permissions(guild)
        else:
            logger.error(f"❌ Could not find configured guild ID: {self.guild_id}")
            # Continue operation but log the issue
    
    async def _check_bot_permissions(self, guild: discord.Guild):
        """Check and log bot permissions in guild"""
        try:
            bot_member = guild.get_member(self.user.id)
            if bot_member:
                perms = bot_member.guild_permissions
                
                # Check critical permissions
                critical_perms = {
                    'send_messages': perms.send_messages,
                    'read_messages': perms.read_messages,
                    'use_application_commands': perms.use_application_commands,
                    'add_reactions': perms.add_reactions,
                    'manage_messages': perms.manage_messages
                }
                
                logger.info("🔐 Bot permissions in guild:")
                for perm, has_perm in critical_perms.items():
                    status = "✅" if has_perm else "❌"
                    logger.info(f"   {status} {perm}: {has_perm}")
                
                # Warn about missing critical permissions
                missing_critical = [perm for perm, has_perm in critical_perms.items() if not has_perm]
                if missing_critical:
                    logger.warning(f"⚠️ Missing critical permissions: {', '.join(missing_critical)}")
                    
        except Exception as e:
            logger.error(f"❌ Error checking bot permissions: {e}")
    
    async def _set_bot_status(self):
        """Set Discord bot status and activity"""
        try:
            # Get status configuration using proper get_config_section method
            status_type_str = self.config_manager.get_config_section('discord_config', 'status.type', 'online')
            activity_name = self.config_manager.get_config_section('discord_config', 'status.activity.name', 'for crisis patterns | v3.1 clean arch')
            activity_type_str = self.config_manager.get_config_section('discord_config', 'status.activity.type', 'watching')
            
            # Convert strings to Discord enums
            status_type = getattr(discord.Status, status_type_str, discord.Status.online)
            activity_type = getattr(discord.ActivityType, activity_type_str, discord.ActivityType.watching)
            
            activity = discord.Activity(
                type=activity_type,
                name=activity_name
            )
            
            await self.change_presence(status=status_type, activity=activity)
            logger.info(f"🎭 Bot status set: {status_type.name} - {activity_type.name} {activity_name}")
            
        except Exception as e:
            logger.error(f"❌ Error setting bot status: {e}")
            # Continue without status - not critical
    
    async def _initialize_dependent_managers(self):
        """Initialize managers that depend on Discord client being ready"""
        try:
            # Initialize API manager if available
            if self.api_manager:
                await self.api_manager.initialize_after_discord_ready(self)
            
            # Load command cogs if available
            await self._load_command_cogs()
            
            # Sync slash commands
            await self._sync_slash_commands()
            
        except Exception as e:
            logger.error(f"❌ Error initializing dependent managers: {e}")
            # Continue operation - dependent managers are not critical for core functionality
    
    async def _load_command_cogs(self):
        """Load Discord command cogs"""
        try:
            # This will be implemented when we create the command managers
            # For now, log that we're ready for command loading
            logger.info("📋 Ready for command cog loading (to be implemented in later phases)")
            
        except Exception as e:
            logger.error(f"❌ Error loading command cogs: {e}")
    
    async def _sync_slash_commands(self):
        """Sync Discord slash commands"""
        try:
            total_commands = len([cmd for cmd in self.tree.walk_commands()])
            logger.info(f"📋 Found {total_commands} commands in tree before sync")
            
            if total_commands > 0:
                logger.info("🌍 Syncing slash commands globally...")
                synced = await self.tree.sync()
                logger.info(f"✅ Global sync successful: {len(synced)} commands")
                
                # Log each synced command
                for cmd in synced:
                    logger.info(f"   📝 Synced: /{cmd.name} - {cmd.description[:50]}...")
            else:
                logger.info("📋 No commands to sync")
                
        except Exception as e:
            logger.error(f"❌ Command sync failed: {e}")
            # Continue operation - slash commands are not critical for core functionality
    # ========================================================================
    
    # ========================================================================
    # HANDLERS
    # ========================================================================
    def register_event_handler(self, event_name: str, handler: Callable):
        """
        Register custom event handler
        
        Args:
            event_name: Name of Discord event
            handler: Handler function
        """
        if event_name not in self.event_handlers:
            self.event_handlers[event_name] = []
        
        self.event_handlers[event_name].append(handler)
        self.add_listener(handler, event_name)
        logger.info(f"📡 Registered custom event handler for {event_name}")
    
    def get_guild(self) -> Optional[discord.Guild]:
        """
        Get the configured guild
        
        Returns:
            Guild object if found, None otherwise
        """
        if not self.guild_id:
            return None
        return discord.utils.get(self.guilds, id=self.guild_id)
    
    def get_health_status(self) -> Dict[str, Any]:
        """
        Get Discord client health status
        
        Returns:
            Health status dictionary
        """
        guild = self.get_guild()
        
        return {
            'discord_ready': self.is_ready_complete,
            'connection_healthy': self.connection_healthy,
            'latency_ms': round(self.latency * 1000, 2),
            'guild_connected': guild is not None,
            'guild_name': guild.name if guild else None,
            'guild_member_count': guild.member_count if guild else None,
            'uptime_seconds': (datetime.now(timezone.utc) - self.start_time).total_seconds()
        }
    # ========================================================================

    # ========================================================================
    # CONNECTION MANAGEMENT
    # ========================================================================
    async def connect_to_discord(self) -> bool:
        """
        Connect to Discord and start the bot
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            logger.info("🔌 Connecting to Discord...")
            
            # Get bot token from configuration using get_config_section
            bot_token = self.config_manager.get_config_section(
                'discord_config', 
                'discord_settings.bot_token'
            )
            
            if not bot_token:
                logger.error("❌ Bot token not found in configuration")
                # Check environment variable as fallback (Rule #7)
                bot_token = self.config_manager.get_env('BOT_TOKEN')
                
                if not bot_token:
                    logger.error("❌ Bot token not found in environment variables")
                    return False
                
                logger.warning("⚠️ Using bot token from environment variable")
            
            # Validate token format
            if not self._validate_bot_token(bot_token):
                logger.error("❌ Invalid bot token format")
                return False
            
            # Start the bot connection
            # Note: self.start() is non-blocking and runs the bot in the background
            logger.info("🚀 Starting Discord bot connection...")
            asyncio.create_task(self.start(bot_token))
            
            # Wait for connection to be established
            max_wait = 30  # Maximum 30 seconds to connect
            wait_interval = 0.5
            total_waited = 0
            
            while not self.is_ready_complete and total_waited < max_wait:
                await asyncio.sleep(wait_interval)
                total_waited += wait_interval
            
            if self.is_ready_complete and self.connection_healthy:
                logger.info("✅ Successfully connected to Discord")
                return True
            else:
                logger.error(f"❌ Discord connection failed after {max_wait} seconds")
                return False
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to Discord: {e}")
            self.connection_healthy = False
            return False
    
    async def disconnect_from_discord(self) -> None:
        """
        Gracefully disconnect from Discord and cleanup resources
        """
        try:
            logger.info("🔌 Disconnecting from Discord...")
            
            # Mark connection as unhealthy
            self.connection_healthy = False
            
            # Update bot status before disconnecting
            try:
                await self.change_presence(
                    status=discord.Status.invisible,
                    activity=None
                )
                logger.info("👻 Bot status set to invisible")
            except Exception as e:
                logger.warning(f"⚠️ Could not update status before disconnect: {e}")
            
            # Close Discord connection
            if not self.is_closed():
                await self.close()
                logger.info("✅ Discord connection closed gracefully")
            else:
                logger.info("ℹ️ Discord connection already closed")
            
            # Cleanup event handlers
            self._cleanup_event_handlers()
            
            logger.info("✅ Successfully disconnected from Discord")
            
        except Exception as e:
            logger.error(f"❌ Error during Discord disconnect: {e}")
            # Continue with cleanup even if there were errors
            try:
                if not self.is_closed():
                    await self.close()
            except Exception as close_error:
                logger.error(f"❌ Final disconnect attempt failed: {close_error}")
    
    def _validate_bot_token(self, token: str) -> bool:
        """
        Validate Discord bot token format
        
        Args:
            token: Bot token to validate
            
        Returns:
            bool: True if token appears valid, False otherwise
        """
        if not token:
            return False
        
        # Discord bot tokens should be at least 50 characters
        if len(token) < 50:
            logger.warning("⚠️ Bot token appears too short")
            return False
        
        # Bot tokens typically contain dots
        if '.' not in token:
            logger.warning("⚠️ Bot token format appears invalid")
            return False
        
        return True
    
    def _cleanup_event_handlers(self) -> None:
        """
        Cleanup registered event handlers
        """
        try:
            # Remove custom event handlers
            for event_name, handlers in self.event_handlers.items():
                for handler in handlers:
                    try:
                        self.remove_listener(handler, event_name)
                    except Exception as e:
                        logger.debug(f"Could not remove handler for {event_name}: {e}")
            
            self.event_handlers.clear()
            logger.debug("🧹 Event handlers cleaned up")
            
        except Exception as e:
            logger.warning(f"⚠️ Error during event handler cleanup: {e}")
    # ========================================================================

# ========================================================================
# FACTORY FUNCTIONS
# ========================================================================
def create_discord_client_manager(config_manager: UnifiedConfigManager, logging_manager: LoggingConfigManager, **kwargs) -> DiscordClientManager:
    """
    Factory function for DiscordClientManager (MANDATORY per Rule #1)
    
    Args:
        config_manager: UnifiedConfigManager instance
        **kwargs: Additional dependencies (nlp_manager, crisis_manager, etc.)
        
    Returns:
        Initialized DiscordClientManager instance
    """
    try:
        # Get or create logging manager
        logging_manager = kwargs.get('logging_manager')
        if not logging_manager:
            from managers.logging_config import create_logging_config_manager
            logging_manager = create_logging_config_manager(config_manager)
        
        return DiscordClientManager(
            config_manager=config_manager,
            logging_manager=logging_manager,
            **kwargs
        )
    except Exception as e:
        logger.error(f"❌ Failed to create DiscordClientManager: {e}")
        # Implement resilient fallback per Rule #5
        raise

__all__ = [
    'DiscordClientManager',
    'create_discord_client_manager'
]