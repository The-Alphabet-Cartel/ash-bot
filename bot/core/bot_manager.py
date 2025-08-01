#!/usr/bin/env python3
"""
Core Bot Manager - v3.0 CLEANED VERSION
Removed all backward compatibility aliases and legacy code
"""

import discord
from discord.ext import commands
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

class AshBot(commands.Bot):
    """Ash Bot v3.0 - Three-Model Ensemble Architecture"""
    
    def __init__(self, config):
        self.config = config
        
        # Setup Discord intents
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        
        commands.Bot.__init__(
            self,
            command_prefix='!ash ',
            intents=intents,
            help_command=None
        )
        
        # v3.0 Component references
        self.claude_api = None
        self.nlp_client = None
        self.keyword_detector = None
        self.crisis_handler = None
        self.message_handler = None
        
        # API Server components
        self.api_server = None
        self.start_time = datetime.now(timezone.utc)
        
        logger.info("🤖 AshBot v3.0 initialized - Three-Model Ensemble Architecture")
    
    async def setup_hook(self):
        """Setup hook - initialize v3.0 components"""
        logger.info("🔄 Starting v3.0 setup_hook...")
        
        try:
            # Initialize v3.0 components
            await self._initialize_v3_components()
            
            # Initialize API Server
            await self._initialize_api_server()
            
            # Add command cogs
            await self._load_command_cogs()
            
            # Sync commands globally
            await self._sync_slash_commands()
            
            logger.info("✅ v3.0 Setup completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ v3.0 Setup hook failed: {e}")
            logger.exception("Full setup_hook traceback:")
            return False
    
    async def _initialize_v3_components(self):
        """Initialize v3.0 components - no legacy compatibility"""
        logger.info("🔧 Initializing v3.0 components...")
        
        # Step 1: Initialize Claude API
        logger.info("🧠 Initializing Claude API...")
        try:
            from bot.integrations.claude_api import ClaudeAPI
            self.claude_api = ClaudeAPI(self.config)
            logger.info("✅ Claude API initialized")
        except Exception as e:
            logger.error(f"❌ Claude API initialization failed: {e}")
            raise  # Fail fast in v3.0
        
        # Step 2: Initialize keyword detector
        logger.info("🔍 Initializing keyword detector...")
        try:
            from bot.utils.keyword_detector import KeywordDetector
            self.keyword_detector = KeywordDetector()
            logger.info("✅ Keyword detector initialized")
        except Exception as e:
            logger.error(f"❌ Keyword detector initialization failed: {e}")
            raise  # Fail fast in v3.0
        
        # Step 3: Initialize NLP client
        logger.info("🧠 Initializing v3.0 NLP client...")
        try:
            from bot.integrations.nlp_integration import EnhancedNLPClient
            nlp_host = self.config.get('GLOBAL_NLP_API_HOST', '10.20.30.253')
            nlp_port = self.config.get('GLOBAL_NLP_API_PORT', '8881')
            nlp_url = f"http://{nlp_host}:{nlp_port}"
            self.nlp_client = EnhancedNLPClient(nlp_url)
            
            # Test connection
            health = await self.nlp_client.test_connection()
            if health:
                logger.info("✅ v3.0 NLP client connected successfully")
            else:
                logger.error("❌ v3.0 NLP client health check failed")
                raise ConnectionError("NLP service unavailable")
                
        except Exception as e:
            logger.error(f"❌ v3.0 NLP client initialization failed: {e}")
            raise  # Fail fast in v3.0
        
        # Step 4: Initialize crisis handler
        logger.info("🚨 Initializing v3.0 crisis handler...")
        try:
            from bot.handlers.crisis_handler import CrisisHandler
            self.crisis_handler = CrisisHandler(self, self.config)
            logger.info("✅ v3.0 Crisis handler initialized")
        except Exception as e:
            logger.error(f"❌ v3.0 Crisis handler initialization failed: {e}")
            raise
        
        # Step 5: Initialize message handler
        logger.info("📨 Initializing v3.0 message handler...")
        try:
            from bot.handlers.message_handler import MessageHandler
            self.message_handler = MessageHandler(
                self,
                self.claude_api,
                self.nlp_client, 
                self.keyword_detector,
                self.crisis_handler,
                self.config
            )
            logger.info("✅ v3.0 Message handler initialized")
        except Exception as e:
            logger.error(f"❌ v3.0 Message handler initialization failed: {e}")
            raise
        
        logger.info("✅ All v3.0 components initialized successfully")

    async def _initialize_api_server(self):
        """Initialize v3.0 API Server"""
        logger.info("🌐 Initializing v3.0 API Server...")
        try:
            from bot.api.api_server import setup_api_server
            
            api_host = self.config.get('GLOBAL_BOT_API_HOST', '0.0.0.0')
            api_port = self.config.get_int('GLOBAL_BOT_API_PORT', 8882)
            
            self.api_server = setup_api_server(self, api_host, api_port)
            
            # Start the API server
            api_started = await self.api_server.start_server()
            if api_started:
                logger.info("✅ v3.0 API Server started successfully")
            else:
                raise RuntimeError("API Server failed to start")
                
        except Exception as e:
            logger.error(f"❌ v3.0 API Server initialization failed: {e}")
            raise  # Fail fast in v3.0

    async def _load_command_cogs(self):
        """Load v3.0 command cogs"""
        
        # Load Crisis Commands
        try:
            from bot.commands.crisis_commands import CrisisKeywordCommands
            await self.add_cog(CrisisKeywordCommands(self))
            logger.info("✅ Loaded v3.0 Crisis Commands cog")
        except Exception as e:
            logger.error(f"❌ Failed to load Crisis Commands: {e}")
            raise
        
        # Load Monitoring Commands
        try:
            from bot.commands.monitoring_commands import MonitoringCommands
            await self.add_cog(MonitoringCommands(self))
            logger.info("✅ Loaded v3.0 Monitoring Commands cog")
        except Exception as e:
            logger.error(f"❌ Failed to load Monitoring Commands: {e}")
            raise

        # Load Ensemble Commands (v3.0 feature)
        try:
            from bot.commands.ensemble_commands import EnsembleCommands
            await self.add_cog(EnsembleCommands(self))
            logger.info("✅ Loaded v3.0 Ensemble Commands cog")
        except Exception as e:
            logger.error(f"❌ Failed to load v3.0 Ensemble Commands: {e}")
            raise

    async def _sync_slash_commands(self):
        """Sync v3.0 slash commands"""
        total_commands = len([cmd for cmd in self.tree.walk_commands()])
        logger.info(f"📋 Found {total_commands} v3.0 commands in tree before sync")
        
        logger.info("🌍 Syncing v3.0 slash commands globally...")
        try:
            synced = await self.tree.sync()
            logger.info(f"✅ v3.0 Global sync successful: {len(synced)} commands")
            
            # Log each synced command
            for cmd in synced:
                logger.info(f"   📝 Synced: /{cmd.name} - {cmd.description[:50]}...")
            
            return True
            
        except Exception as sync_error:
            logger.error(f"❌ v3.0 Command sync failed: {sync_error}")
            raise
    
    async def on_ready(self):
        """Bot ready event - v3.0"""
        logger.info(f'✅ {self.user} has awakened in The Alphabet Cartel (v3.0)')
        
        # Log v3.0 service status
        logger.info(f"🧠 v3.0 NLP Server: {'Connected' if self.nlp_client else 'Not Connected'}")
        logger.info(f"🔍 v3.0 Learning System: {'Enabled' if self.config.get_bool('GLOBAL_ENABLE_LEARNING_SYSTEM') else 'Disabled'}")
        
        # Log guild information
        guild = discord.utils.get(self.guilds, id=self.config.get_int('BOT_GUILD_ID'))
        if guild:
            logger.info(f'Connected to guild: {guild.name}')
            
            # Check bot permissions
            bot_member = guild.get_member(self.user.id)
            if bot_member:
                perms = bot_member.guild_permissions
                logger.info(f'Bot permissions: send_messages={perms.send_messages}, use_application_commands={perms.use_application_commands}')
        
        # Set bot status
        await self.change_presence(
            status=discord.Status.online,
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="for crisis patterns | v3.0 ensemble"
            )
        )
        
        logger.info("🎉 Ash Bot v3.0 fully operational (Three-Model Ensemble)")
    
    async def on_message(self, message):
        """v3.0 Message handler with strict validation"""
        
        # CRITICAL: Never process the bot's own messages
        if message.author == self.user:
            return
        
        # CRITICAL: Never process any bot messages
        if message.author.bot:
            return
        
        # CRITICAL: Handle empty messages gracefully
        if not message.content or not message.content.strip():
            return
        
        # Basic guild validation
        if not message.guild or message.guild.id != self.config.get_int('BOT_GUILD_ID'):
            return
        
        # Channel validation
        allowed_channels = self.config.get_allowed_channels()
        if allowed_channels and message.channel.id not in allowed_channels:
            return
        
        logger.debug(f"📨 Processing v3.0 message from {message.author} in {message.channel}")
        
        # v3.0 Message handling
        try:
            await self.message_handler.handle_message(message)
        except Exception as e:
            logger.error(f"❌ Error in v3.0 message handler: {e}")
            logger.exception("Full traceback:")
            try:
                await message.add_reaction('❌')
            except:
                pass
        
        # Process commands
        await self.process_commands(message)

    async def on_command_error(self, ctx, error):
        """Handle command errors - v3.0"""
        logger.error(f"v3.0 Command error in {ctx.command}: {error}")
    
    async def close(self):
        """v3.0 Enhanced cleanup"""
        logger.info("🛑 Starting v3.0 shutdown...")
        
        try:
            # Stop API server
            if self.api_server and hasattr(self.api_server, 'stop_server'):
                await self.api_server.stop_server()
            
            # Close components if they have close methods
            if self.claude_api and hasattr(self.claude_api, 'close'):
                await self.claude_api.close()
            
            if self.nlp_client and hasattr(self.nlp_client, 'close'):
                await self.nlp_client.close()
        except Exception as e:
            logger.error(f"❌ Error during v3.0 cleanup: {e}")
        
        # Close parent
        await super().close()
        
        logger.info("✅ v3.0 Shutdown complete")