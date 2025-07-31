#!/usr/bin/env python3
"""
Core Bot Manager - Simplified without Security Manager
"""

import discord
from discord.ext import commands
import logging
from datetime import datetime, timezone
from utils.resource_managers import ResourceCleanupMixin, graceful_shutdown

logger = logging.getLogger(__name__)

class AshBot(commands.Bot, ResourceCleanupMixin):
    """Enhanced Ash Bot with Resource Management - Security Manager Removed"""
    
    def __init__(self, config):
        self.config = config
        
        # Initialize resource management
        ResourceCleanupMixin.__init__(self)
        
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
        
        # NEW: API Server components
        self.api_server = None
        self.start_time = datetime.now(timezone.utc)
        
        # Register shutdown handler
        graceful_shutdown.register_shutdown_handler(self.cleanup_resources)
        
        logger.info("🤖 AshBot initialized with enhanced resource management (security manager removed)")
    
    async def setup_hook(self):
        """Setup hook - initialize components with resource management"""
        logger.info("🔄 Starting enhanced setup_hook...")
        
        try:
            # Initialize components (now without security manager)
            await self._initialize_components()
            
            # NEW: Initialize API Server
            await self._initialize_api_server()
            
            # Add command cogs
            await self._load_command_cogs()
            
            # Sync commands globally
            await self._sync_slash_commands()
            
            logger.info("✅ Enhanced setup completed successfully (no security manager)")
            return True
            
        except Exception as e:
            logger.error(f"❌ Setup failed: {e}")
            return False
    
    async def _initialize_components(self):
        """Initialize core components without security manager"""
        
        # Step 1: Initialize Claude API
        logger.info("🧠 Initializing Claude API...")
        try:
            from integrations.claude_api import ClaudeAPI
            self.claude_api = ClaudeAPI(self.config)
            logger.info("✅ Claude API initialized")
        except Exception as e:
            logger.error(f"❌ Claude API initialization failed: {e}")
            # Continue without Claude API - use fallback responses
            self.claude_api = None
        
        # Step 2: Initialize keyword detector
        logger.info("🔍 Initializing keyword detector...")
        try:
            from utils.keyword_detector import KeywordDetector
            self.keyword_detector = KeywordDetector()
            logger.info("✅ Keyword detector initialized")
        except Exception as e:
            logger.error(f"❌ Keyword detector initialization failed: {e}")
            raise
        
        # Step 3: Initialize NLP client
        logger.info("🧠 Initializing NLP client...")
        try:
            from integrations.nlp_integration import NLPClient
            nlp_url = self.config.get('GLOBAL_NLP_API_URL', 'http://10.20.30.253:8881')
            self.nlp_client = NLPClient(nlp_url)
            
            # Test connection
            health = await self.nlp_client.health_check()
            if health:
                logger.info("✅ NLP client connected successfully")
            else:
                logger.warning("⚠️ NLP client initialized but health check failed")
                
        except Exception as e:
            logger.warning(f"⚠️ NLP client initialization failed: {e}")
            # Continue without NLP client - will use keyword-only detection
            self.nlp_client = None
        
        # Step 2: Initialize enhanced handlers WITHOUT security
        logger.info("🚨 Initializing enhanced handlers...")
        from handlers.crisis_handler import CrisisHandler
        from handlers.message_handler import MessageHandler
        
        self.crisis_handler = CrisisHandler(self, self.config)
        
        self.message_handler = MessageHandler(
            self,
            self.claude_api,
            self.nlp_client, 
            self.keyword_detector,
            self.crisis_handler,
            self.config
            # REMOVED: security_manager parameter
        )
        
        logger.info("✅ All enhanced components initialized without security manager")

    async def _load_command_cogs(self):
        """Load command cogs"""
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

        # Load Enhanced Learning Commands (replaces false_positive_commands)
        try:
            from bot.commands.enhanced_learning_commands import EnhancedLearningCommands
            await self.add_cog(EnhancedLearningCommands(self))
            logger.info("✅ Loaded Enhanced Learning Commands cog")
        except Exception as e:
            logger.error(f"❌ Failed to load Enhanced Learning Commands: {e}")
            cog_errors.append(f"EnhancedLearningCommands: {e}")

        # Log cog loading errors
        if cog_errors:
            logger.warning(f"⚠️ Cog loading errors: {cog_errors}")

    async def _initialize_api_server(self):
        """Initialize API server if enabled"""
        # API server initialization code would go here
        # For now, just log that it's disabled
        logger.info("📡 API server initialization skipped (not implemented in this fix)")
        self.api_server = None

    async def _sync_slash_commands(self):
        """Sync slash commands with enhanced logging"""
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
        """Bot ready event with enhanced logging"""
        logger.info(f'✅ {self.user} has awakened in The Alphabet Cartel')
        
        # Log service status
        logger.info(f"📊 API Server: {'Running' if self.api_server else 'Not Available'}")
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
        
        logger.info("🎉 Ash Bot fully operational (security manager removed)")
    
    async def on_message(self, message):
        """FIXED: Simplified message routing without security validation"""
        
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
        
        # SIMPLIFIED channel validation (remove security manager dependency)
        allowed_channels = self.config.get_allowed_channels()
        if allowed_channels and message.channel.id not in allowed_channels:
            logger.debug(f"🚫 Message from non-allowed channel: {message.channel.id}")
            return
        
        logger.debug(f"📨 Processing message from {message.author} in {message.channel}")
        
        # CRITICAL FIX: Call the RIGHT method that actually handles crisis responses
        if self.message_handler:
            try:
                # Call the method that has all the crisis handling logic
                if hasattr(self.message_handler, 'handle_message'):
                    await self.message_handler.handle_message(message)
                elif hasattr(self.message_handler, 'process_message'):
                    # Fallback for your current structure
                    detection_result = await self.message_handler.process_message(message)
                    if detection_result and detection_result.get('needs_response'):
                        logger.info("🚨 Crisis detected - need to trigger response manually")
                        # Manually trigger crisis response if it wasn't handled
                        if self.crisis_handler:
                            crisis_level = detection_result['crisis_level']
                            if self.claude_api:
                                response = await self.claude_api.get_ash_response(
                                    message.content, crisis_level, message.author.display_name
                                )
                            else:
                                response = "I'm here to support you through this difficult time."
                            
                            await self.crisis_handler.handle_crisis_response_with_instructions(
                                message, crisis_level, response
                            )
                else:
                    logger.error("❌ Message handler has no handle_message or process_message method")
                    
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