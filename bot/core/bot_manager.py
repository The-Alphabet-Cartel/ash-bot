#!/usr/bin/env python3
"""
Core Bot Manager - Final Fixed Version with Correct Imports
"""

import discord
from discord.ext import commands
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

class AshBot(commands.Bot):
    """Enhanced Ash Bot - Fixed Imports Version"""
    
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
        
        # Enhanced component references
        self.claude_api = None
        self.nlp_client = None
        self.keyword_detector = None
        self.crisis_handler = None
        self.message_handler = None
        
        # API Server components
        self.api_server = None
        self.start_time = datetime.now(timezone.utc)
        
        logger.info("🤖 AshBot initialized with fixed imports")
    
    async def setup_hook(self):
        """Setup hook - initialize components with fixed imports"""
        logger.info("🔄 Starting setup_hook with fixed imports...")
        
        try:
            # Initialize components
            await self._initialize_components_fixed()
            
            # Add command cogs
            await self._load_command_cogs()
            
            # Sync commands globally
            await self._sync_slash_commands()
            
            logger.info("✅ Setup completed successfully with fixed imports")
            return True
            
        except Exception as e:
            logger.error(f"❌ Setup hook failed: {e}")
            logger.exception("Full setup_hook traceback:")
            return False
    
    async def _initialize_components_fixed(self):
        """Initialize components with correct import names"""
        logger.info("🔧 Initializing components with fixed imports...")
        
        # Step 1: Initialize Claude API
        logger.info("🧠 Initializing Claude API...")
        try:
            from bot.integrations.claude_api import ClaudeAPI
            self.claude_api = ClaudeAPI(self.config)
            logger.info("✅ Claude API initialized")
        except Exception as e:
            logger.error(f"❌ Claude API initialization failed: {e}")
            self.claude_api = None
        
        # Step 2: Initialize keyword detector
        logger.info("🔍 Initializing keyword detector...")
        try:
            from bot.utils.keyword_detector import KeywordDetector
            self.keyword_detector = KeywordDetector()
            logger.info("✅ Keyword detector initialized")
        except Exception as e:
            logger.error(f"❌ Keyword detector initialization failed: {e}")
            # Create a dummy keyword detector to prevent crashes
            class DummyKeywordDetector:
                def check_message(self, content):
                    return {'needs_response': False, 'crisis_level': 'none', 'detected_categories': []}
            self.keyword_detector = DummyKeywordDetector()
            logger.warning("⚠️ Using dummy keyword detector")
        
        # Step 3: Initialize NLP client
        logger.info("🧠 Initializing NLP client...")
        try:
            from bot.integrations.nlp_integration import EnhancedNLPClient
            nlp_url = self.config.get('GLOBAL_NLP_API_URL', 'http://10.20.30.253:8881')
            self.nlp_client = EnhancedNLPClient(nlp_url)
            
            # Test connection
            health = await self.nlp_client.test_connection()
            if health:
                logger.info("✅ NLP client connected successfully")
            else:
                logger.warning("⚠️ NLP client initialized but health check failed")
                
        except Exception as e:
            logger.warning(f"⚠️ NLP client initialization failed: {e}")
            self.nlp_client = None
        
        # Step 4: Initialize crisis handler
        logger.info("🚨 Initializing crisis handler...")
        try:
            from bot.handlers.crisis_handler import CrisisHandler
            self.crisis_handler = CrisisHandler(self, self.config)
            logger.info("✅ Crisis handler initialized")
        except Exception as e:
            logger.error(f"❌ Crisis handler initialization failed: {e}")
            raise
        
        # Step 5: Initialize message handler
        logger.info("📨 Initializing message handler...")
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
            logger.info("✅ Message handler initialized")
        except Exception as e:
            logger.error(f"❌ Message handler initialization failed: {e}")
            raise
        
        logger.info("✅ All components initialized successfully")

    async def _load_command_cogs(self):
        """Load command cogs with fixed imports"""
        cog_errors = []
        
        # Load Crisis Commands
        try:
            from bot.commands.crisis_commands import CrisisKeywordCommands
            await self.add_cog(CrisisKeywordCommands(self))
            logger.info("✅ Loaded Crisis Commands cog")
        except Exception as e:
            logger.error(f"❌ Failed to load Crisis Commands: {e}")
            cog_errors.append(f"CrisisCommands: {e}")
        
        # Load Monitoring Commands
        try:
            from bot.commands.monitoring_commands import MonitoringCommands
            await self.add_cog(MonitoringCommands(self))
            logger.info("✅ Loaded Monitoring Commands cog")
        except Exception as e:
            logger.error(f"❌ Failed to load Monitoring Commands: {e}")
            cog_errors.append(f"MonitoringCommands: {e}")

        # Load Ensemble Commands (enhanced learning + v3.0 features)
        try:
            from bot.commands.ensemble_commands import EnsembleCommands
            await self.add_cog(EnsembleCommands(self))
            logger.info("✅ Loaded Ensemble Commands cog (enhanced learning + v3.0 features)")
        except ImportError as import_err:
            logger.error(f"❌ Failed to import Ensemble Commands: {import_err}")
            # Try alternative import method using setup function
            try:
                import bot.commands.ensemble_commands as ensemble_module
                if hasattr(ensemble_module, 'setup'):
                    await ensemble_module.setup(self)
                    logger.info("✅ Loaded Ensemble Commands via setup function")
                else:
                    cog_errors.append(f"EnsembleCommands: setup function not found")
            except Exception as setup_err:
                logger.error(f"❌ Failed to load via setup: {setup_err}")
                cog_errors.append(f"EnsembleCommands: {import_err}")
        except Exception as e:
            logger.error(f"❌ Failed to load Ensemble Commands: {e}")
            cog_errors.append(f"EnsembleCommands: {e}")

        # Log cog loading errors
        if cog_errors:
            logger.warning(f"⚠️ Cog loading errors: {cog_errors}")

    async def _sync_slash_commands(self):
        """Sync slash commands"""
        total_commands = len([cmd for cmd in self.tree.walk_commands()])
        logger.info(f"📋 Found {total_commands} commands in tree before sync")
        
        logger.info("🌍 Syncing slash commands globally...")
        try:
            synced = await self.tree.sync()
            logger.info(f"✅ Global sync successful: {len(synced)} commands")
            
            # Log each synced command
            for cmd in synced:
                logger.info(f"   📝 Synced: /{cmd.name} - {cmd.description[:50]}...")
            
            return True
            
        except Exception as sync_error:
            logger.error(f"❌ Command sync failed: {sync_error}")
            return False
    
    async def on_ready(self):
        """Bot ready event"""
        logger.info(f'✅ {self.user} has awakened in The Alphabet Cartel')
        
        # Log service status
        logger.info(f"🧠 NLP Server: {'Connected' if self.nlp_client else 'Not Connected'}")
        logger.info(f"🔍 Learning System: {'Enabled' if self.config.get_bool('GLOBAL_ENABLE_LEARNING_SYSTEM') else 'Disabled'}")
        
        # Log guild information
        guild = discord.utils.get(self.guilds, id=self.config.get_int('BOT_GUILD_ID'))
        if guild:
            logger.info(f'Connected to guild: {guild.name}')
            
            # Check bot permissions
            bot_member = guild.get_member(self.user.id)
            if bot_member:
                perms = bot_member.guild_permissions
                logger.info(f'Bot permissions: send_messages={perms.send_messages}, use_application_commands={perms.use_application_commands}')
        
        # Verify slash commands are registered
        try:
            app_commands = await self.tree.fetch_commands()
            logger.info(f"🔍 Verified {len(app_commands)} commands registered with Discord:")
            for cmd in app_commands:
                logger.info(f"   ✅ /{cmd.name}")
                
        except Exception as e:
            logger.error(f"❌ Failed to fetch registered commands: {e}")
        
        # Set bot status
        await self.change_presence(
            status=discord.Status.online,
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="for crisis patterns | /ash_help"
            )
        )
        
        logger.info("🎉 Ash Bot fully operational with fixed imports")
    
    async def on_message(self, message):
        """FIXED: Message handler with proper error handling"""
        
        # CRITICAL FIX #1: Never process the bot's own messages
        if message.author == self.user:
            logger.debug(f"🤖 Ignoring bot's own message")
            return
        
        # CRITICAL FIX #2: Never process any bot messages
        if message.author.bot:
            logger.debug(f"🤖 Ignoring bot message from {message.author}")
            return
        
        # CRITICAL FIX #3: Handle empty messages gracefully
        if not message.content or not message.content.strip():
            logger.debug(f"📭 Ignoring empty message from {message.author}")
            return
        
        # Basic guild validation
        if not message.guild or message.guild.id != self.config.get_int('BOT_GUILD_ID'):
            logger.debug(f"🚫 Wrong guild: {message.guild.id if message.guild else 'DM'}")
            return
        
        # SIMPLIFIED channel validation
        allowed_channels = self.config.get_allowed_channels()
        if allowed_channels and message.channel.id not in allowed_channels:
            logger.debug(f"🚫 Message from non-allowed channel: {message.channel.id}")
            return
        
        logger.debug(f"📨 Processing message from {message.author} in {message.channel}")
        
        # CRITICAL FIX: Call the message handler properly
        if self.message_handler:
            try:
                # Use the handle_message method from our fixed message handler
                await self.message_handler.handle_message(message)
                    
            except Exception as e:
                logger.error(f"❌ Error in message handler: {e}")
                logger.exception("Full traceback:")
                # Add error reaction to message
                try:
                    await message.add_reaction('❌')
                except:
                    pass  # Don't fail if we can't add reactions
        else:
            logger.warning("⚠️ Message handler not ready")
        
        # Process commands (in case any text commands are still used)
        await self.process_commands(message)

    async def on_command_error(self, ctx, error):
        """Handle command errors"""
        logger.error(f"Command error in {ctx.command}: {error}")
    
    async def close(self):
        """Enhanced cleanup"""
        logger.info("🛑 Starting shutdown...")
        
        try:
            # Close components if they have close methods
            if self.claude_api and hasattr(self.claude_api, 'close'):
                await self.claude_api.close()
            
            if self.nlp_client and hasattr(self.nlp_client, 'close'):
                await self.nlp_client.close()
        except Exception as e:
            logger.error(f"❌ Error during cleanup: {e}")
        
        # Close parent
        await super().close()
        
        logger.info("✅ Shutdown complete")

# Export for backwards compatibility
AshBotEnhanced = AshBot