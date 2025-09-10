"""
Ash-Bot: Crisis Detection Bot for The Alphabet Cartel Discord Community
********************************************************************************
Conversation Handler Manager for Ash-Bot Service
---
FILE VERSION: v3.1-1b-1-1
LAST MODIFIED: 2025-09-09
PHASE: 1b Step 1
CLEAN ARCHITECTURE: v3.1
Repository: https://github.com/the-alphabet-cartel/ash-bot
Community: The Alphabet Cartel - https://discord.gg/alphabetcartel | https://alphabetcartel.org
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import discord

# Import existing managers using factory functions (Rule #1)
from managers.unified_config import UnifiedConfigManager
from managers.logging_config import LoggingConfigManager
from managers.crisis_analysis import CrisisAnalysisManager

logger = logging.getLogger(__name__)

# ============================================================================
# DATA STRUCTURES
# ============================================================================

class ConversationStatus(Enum):
    """Conversation status tracking"""
    ACTIVE = "active"
    ESCALATED = "escalated"
    HANDOFF_REQUESTED = "handoff_requested"
    COMPLETED = "completed"
    EXPIRED = "expired"

@dataclass
class ConversationSession:
    """Active conversation session data"""
    user_id: int
    channel_id: int
    start_time: float
    crisis_level: str
    initial_crisis_level: str
    status: ConversationStatus
    follow_up_count: int = 0
    escalations: int = 0
    last_interaction: float = None
    staff_notified: bool = False
    
    def __post_init__(self):
        if self.last_interaction is None:
            self.last_interaction = self.start_time

@dataclass
class ConversationStats:
    """Conversation statistics tracking"""
    total_conversations: int = 0
    active_conversations: int = 0
    completed_conversations: int = 0
    escalated_conversations: int = 0
    staff_handoffs: int = 0
    follow_ups_handled: int = 0
    expired_conversations: int = 0
    crisis_overrides: int = 0
    trigger_phrase_matches: int = 0
    mention_triggers: int = 0

# ============================================================================
# CONVERSATION HANDLER MANAGER
# ============================================================================

class ConversationHandlerManager:
    """
    Phase 1b Step 1: Discord conversation management and Claude integration
    
    Responsibilities:
    - Manage conversation sessions with isolation
    - Handle trigger phrase detection
    - Integrate with Claude API for responses
    - Coordinate with CrisisAnalysisManager
    - Track conversation statistics and health
    - Provide resilient error handling
    """
    
    def __init__(
        self,
        config_manager: UnifiedConfigManager,
        logging_manager: LoggingConfigManager,
        crisis_analysis_manager: CrisisAnalysisManager,
        discord_client_manager: Optional[Any] = None
    ):
        """
        Initialize ConversationHandlerManager with dependency injection (Rule #2)
        
        Args:
            config_manager: UnifiedConfigManager (first parameter - Rule #2)
            logging_manager: LoggingConfigManager for logging configuration
            crisis_analysis_manager: CrisisAnalysisManager for crisis detection
            discord_client_manager: DiscordClientManager for Discord integration (optional)
        """
        self.config_manager = config_manager
        self.logging_manager = logging_manager
        self.crisis_analysis_manager = crisis_analysis_manager
        self.discord_client_manager = discord_client_manager
        
        # Load configuration using get_config_section (Rule #4)
        try:
            self.config = self._load_configuration()
            logger.info("✅ ConversationHandlerManager configuration loaded")
        except Exception as e:
            logger.error(f"❌ Configuration loading failed: {e}")
            self.config = self._get_fallback_configuration()
            logger.warning("⚠️ Using fallback configuration for conversation handler")
        
        # Initialize conversation tracking
        self.active_conversations: Dict[int, ConversationSession] = {}
        self.stats = ConversationStats()
        
        # Initialize Claude API client (will be set later)
        self.claude_client = None
        
        # Initialize conversation settings from config
        self._initialize_conversation_settings()
        
        logger.info("🎯 ConversationHandlerManager initialized (Clean Architecture v3.1)")
        logger.info(f"   ⏱️ Conversation timeout: {self.conversation_timeout}s")
        logger.info(f"   🎯 Requires mention: {self.requires_mention}")
        logger.info(f"   📝 Trigger phrases: {len(self.trigger_phrases)} configured")
        logger.info(f"   🔄 Conversation starters: {'enabled' if self.allow_starters else 'disabled'}")
    
    def _load_configuration(self) -> Dict[str, Any]:
        """Load conversation configuration using UnifiedConfigManager"""
        try:
            # Load conversation configuration section
            config = self.config_manager.get_config_section('conversation_config')
            
            if not config:
                raise ValueError("conversation_config section not found")
            
            logger.debug("📋 Conversation configuration loaded successfully")
            return config
            
        except Exception as e:
            logger.error(f"❌ Failed to load conversation configuration: {e}")
            raise
    
    def _get_fallback_configuration(self) -> Dict[str, Any]:
        """Provide safe fallback configuration (Rule #5)"""
        fallback = {
            'conversation_settings': {
                'timeout': 300,
                'requires_mention': True,
                'allow_starters': False,
                'trigger_phrases': ['ash', 'hey ash', 'ash help'],
                'max_daily_conversations': 100,
                'rate_limit_per_user': 10
            },
            'claude_settings': {
                'model': 'claude-sonnet-4-20250514',
                'max_tokens': 1000,
                'temperature': 0.7,
                'timeout': 30
            },
            'response_settings': {
                'include_crisis_context': True,
                'personalize_responses': True,
                'response_format': 'supportive'
            }
        }
        
        logger.info("🔧 Using fallback conversation configuration")
        return fallback
    
    def _initialize_conversation_settings(self) -> None:
        """Initialize conversation settings from configuration"""
        try:
            conv_settings = self.config.get('conversation_settings', {})
            
            # Environment Variable Reuse (Rule #7) - mapping to existing variables
            self.conversation_timeout = conv_settings.get('timeout', 300)
            self.requires_mention = conv_settings.get('requires_mention', True)
            self.allow_starters = conv_settings.get('allow_starters', False)
            self.trigger_phrases = conv_settings.get('trigger_phrases', ['ash'])
            self.max_daily_conversations = conv_settings.get('max_daily_conversations', 100)
            self.rate_limit_per_user = conv_settings.get('rate_limit_per_user', 10)
            
            # Claude settings
            claude_settings = self.config.get('claude_settings', {})
            self.claude_model = claude_settings.get('model', 'claude-sonnet-4-20250514')
            self.claude_max_tokens = claude_settings.get('max_tokens', 1000)
            self.claude_temperature = claude_settings.get('temperature', 0.7)
            self.claude_timeout = claude_settings.get('timeout', 30)
            
            # Response settings
            response_settings = self.config.get('response_settings', {})
            self.include_crisis_context = response_settings.get('include_crisis_context', True)
            self.personalize_responses = response_settings.get('personalize_responses', True)
            self.response_format = response_settings.get('response_format', 'supportive')
            
            # Convert trigger phrases to lowercase for matching
            self.trigger_phrases = [phrase.lower().strip() for phrase in self.trigger_phrases]
            
            logger.debug("⚙️ Conversation settings initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Error initializing conversation settings: {e}")
            # Use safe defaults (Rule #5)
            self.conversation_timeout = 300
            self.requires_mention = True
            self.allow_starters = False
            self.trigger_phrases = ['ash']
            self.max_daily_conversations = 100
            self.rate_limit_per_user = 10
            self.claude_model = 'claude-sonnet-4-20250514'
            self.claude_max_tokens = 1000
            self.claude_temperature = 0.7
            self.claude_timeout = 30
            self.include_crisis_context = True
            self.personalize_responses = True
            self.response_format = 'supportive'
    
    async def handle_message(self, message: discord.Message) -> bool:
        """
        Handle incoming Discord message for conversation management
        
        Args:
            message: Discord message object
            
        Returns:
            bool: True if message was handled, False otherwise
        """
        try:
            # Basic message validation
            if not message or message.author.bot:
                return False
            
            user_id = message.author.id
            channel_id = message.channel.id
            
            logger.debug(f"📨 Processing message from user {user_id} in channel {channel_id}")
            
            # Check if user has active conversation
            if user_id in self.active_conversations:
                return await self._handle_conversation_followup(message)
            
            # Check if message should start new conversation
            if await self._should_start_conversation(message):
                return await self._start_new_conversation(message)
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Error handling message: {e}")
            # Resilient error handling (Rule #5) - don't crash the system
            return False
    
    async def _should_start_conversation(self, message: discord.Message) -> bool:
        """
        Determine if message should start a new conversation
        
        Args:
            message: Discord message object
            
        Returns:
            bool: True if conversation should start
        """
        try:
            content = message.content.lower().strip()
            
            # Check mention requirement
            if self.requires_mention:
                # Check if bot was mentioned
                if self.discord_client_manager and hasattr(self.discord_client_manager, 'user'):
                    bot_mentioned = self.discord_client_manager.user in message.mentions
                else:
                    # Fallback: check for common bot mention patterns
                    bot_mentioned = any(phrase in content for phrase in ['<@', 'ash'])
                
                if not bot_mentioned:
                    logger.debug(f"🚫 Message from {message.author.id} doesn't mention bot")
                    return False
            
            # Check trigger phrases
            trigger_matched = any(phrase in content for phrase in self.trigger_phrases)
            if trigger_matched:
                self.stats.trigger_phrase_matches += 1
                logger.debug(f"✅ Trigger phrase matched for user {message.author.id}")
                return True
            
            # Check conversation starters if enabled
            if self.allow_starters:
                starter_phrases = [
                    "i'm still", "i still", "but i", "what if", "can you",
                    "help me", "i need", "it's getting", "i feel", "this is"
                ]
                
                if any(content.startswith(starter) for starter in starter_phrases):
                    logger.debug(f"✅ Conversation starter detected for user {message.author.id}")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Error checking conversation trigger: {e}")
            return False
    
    async def _start_new_conversation(self, message: discord.Message) -> bool:
        """
        Start a new conversation session
        
        Args:
            message: Discord message that triggered the conversation
            
        Returns:
            bool: True if conversation started successfully
        """
        try:
            user_id = message.author.id
            channel_id = message.channel.id
            
            # Perform crisis analysis on the initial message
            crisis_result = await self.crisis_analysis_manager.analyze_message(
                message.content, user_id, channel_id
            )
            
            # Create conversation session
            session = ConversationSession(
                user_id=user_id,
                channel_id=channel_id,
                start_time=time.time(),
                crisis_level=crisis_result.crisis_level.value if hasattr(crisis_result.crisis_level, 'value') else str(crisis_result.crisis_level),
                initial_crisis_level=crisis_result.crisis_level.value if hasattr(crisis_result.crisis_level, 'value') else str(crisis_result.crisis_level),
                status=ConversationStatus.ACTIVE
            )
            
            # Check for existing conversation in same channel
            existing_conversation = self._get_conversation_in_channel(channel_id)
            if existing_conversation:
                self.stats.crisis_overrides += 1
                logger.warning(f"⚠️ Starting new conversation while another is active in channel {channel_id}")
            
            # Store conversation
            self.active_conversations[user_id] = session
            self.stats.total_conversations += 1
            self.stats.active_conversations += 1
            
            # Generate response using Claude
            response = await self._generate_claude_response(message, session)
            
            # Send response
            if response:
                await message.channel.send(response)
            
            logger.info(f"🎯 Started conversation for user {user_id} (crisis level: {session.crisis_level})")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error starting conversation: {e}")
            return False
    
    async def _handle_conversation_followup(self, message: discord.Message) -> bool:
        """
        Handle follow-up message in existing conversation
        
        Args:
            message: Follow-up message
            
        Returns:
            bool: True if handled successfully
        """
        try:
            user_id = message.author.id
            session = self.active_conversations[user_id]
            
            # Verify message is in same channel as conversation
            if message.channel.id != session.channel_id:
                logger.debug(f"💬 Follow-up from {user_id} in wrong channel, ignoring")
                return False
            
            # Update session
            session.last_interaction = time.time()
            session.follow_up_count += 1
            self.stats.follow_ups_handled += 1
            
            # Check for crisis escalation
            crisis_result = await self.crisis_analysis_manager.analyze_message(
                message.content, user_id, message.channel.id
            )
            
            new_level = crisis_result.crisis_level.value if hasattr(crisis_result.crisis_level, 'value') else str(crisis_result.crisis_level)
            
            if self._is_escalation(session.crisis_level, new_level):
                session.crisis_level = new_level
                session.escalations += 1
                session.status = ConversationStatus.ESCALATED
                self.stats.escalated_conversations += 1
                logger.warning(f"📈 Crisis escalation detected for user {user_id}: {session.initial_crisis_level} → {new_level}")
            
            # Generate response
            response = await self._generate_claude_response(message, session)
            
            # Send response
            if response:
                await message.channel.send(response)
            
            logger.debug(f"💬 Handled follow-up for user {user_id} (#{session.follow_up_count})")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error handling conversation follow-up: {e}")
            return False
    
    async def _generate_claude_response(self, message: discord.Message, session: ConversationSession) -> Optional[str]:
        """
        Generate Claude API response for conversation
        
        Args:
            message: Discord message
            session: Conversation session
            
        Returns:
            Optional[str]: Generated response or None if error
        """
        try:
            # If Claude client not available, provide fallback response
            if not self.claude_client:
                logger.warning("⚠️ Claude client not available, using fallback response")
                return self._get_fallback_response(session.crisis_level)
            
            # Prepare context for Claude
            context = {
                'user_name': message.author.display_name,
                'crisis_level': session.crisis_level,
                'follow_up_count': session.follow_up_count,
                'conversation_duration': time.time() - session.start_time,
                'escalations': session.escalations
            }
            
            # Generate response using Claude (placeholder - actual implementation depends on Claude client)
            response = await self._call_claude_api(message.content, context)
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Error generating Claude response: {e}")
            return self._get_fallback_response(session.crisis_level)
    
    async def _call_claude_api(self, message_content: str, context: Dict[str, Any]) -> str:
        """
        Call Claude API with proper error handling
        
        Args:
            message_content: User's message content
            context: Conversation context
            
        Returns:
            str: Claude's response
        """
        try:
            # Placeholder for actual Claude API integration
            # This will be implemented when Claude client is available
            
            crisis_level = context.get('crisis_level', 'none')
            user_name = context.get('user_name', 'friend')
            
            # Generate appropriate response based on crisis level
            if crisis_level in ['high', 'medium']:
                return f"I hear you, {user_name}. It sounds like you're going through something really difficult right now. You matter, and I'm here to listen. Would it help to talk about what's on your mind?"
            elif crisis_level == 'low':
                return f"Thank you for sharing with me, {user_name}. I can sense you might be dealing with some challenges. I'm here to support you through this. What's been weighing on you?"
            else:
                return f"Hi {user_name}, I'm here and ready to listen. What would you like to talk about today?"
            
        except Exception as e:
            logger.error(f"❌ Claude API call failed: {e}")
            return self._get_fallback_response(context.get('crisis_level', 'none'))
    
    def _get_fallback_response(self, crisis_level: str) -> str:
        """
        Get fallback response when Claude API is unavailable
        
        Args:
            crisis_level: Current crisis level
            
        Returns:
            str: Fallback response
        """
        fallback_responses = {
            'high': "I'm here with you. You matter, and you're not alone. Please consider reaching out to a trusted person or crisis resource if you need immediate support.",
            'medium': "Thank you for sharing with me. I can hear that things are difficult right now. I'm here to listen and support you.",
            'low': "I appreciate you opening up. I'm here to listen and help however I can.",
            'none': "Hi there! I'm here and ready to chat. What's on your mind today?"
        }
        
        return fallback_responses.get(crisis_level, fallback_responses['none'])
    
    def _is_escalation(self, current_level: str, new_level: str) -> bool:
        """Check if crisis level has escalated"""
        hierarchy = {'none': 0, 'low': 1, 'medium': 2, 'high': 3}
        return hierarchy.get(new_level, 0) > hierarchy.get(current_level, 0)
    
    def _get_conversation_in_channel(self, channel_id: int) -> Optional[Tuple[int, ConversationSession]]:
        """Find existing conversation in channel"""
        for user_id, session in self.active_conversations.items():
            if session.channel_id == channel_id:
                return (user_id, session)
        return None
    
    async def cleanup_expired_conversations(self) -> int:
        """
        Clean up expired conversations
        
        Returns:
            int: Number of conversations cleaned up
        """
        try:
            current_time = time.time()
            expired_users = []
            
            for user_id, session in self.active_conversations.items():
                # Check if conversation has expired
                time_since_last = current_time - session.last_interaction
                if time_since_last > self.conversation_timeout:
                    expired_users.append(user_id)
            
            # Remove expired conversations
            for user_id in expired_users:
                session = self.active_conversations.pop(user_id)
                session.status = ConversationStatus.EXPIRED
                self.stats.expired_conversations += 1
                self.stats.active_conversations -= 1
                
                duration = current_time - session.start_time
                logger.info(f"🕒 Conversation expired for user {user_id} (duration: {duration:.1f}s)")
            
            return len(expired_users)
            
        except Exception as e:
            logger.error(f"❌ Error cleaning up conversations: {e}")
            return 0
    
    def get_conversation_stats(self) -> Dict[str, Any]:
        """Get conversation statistics"""
        return {
            'total_conversations': self.stats.total_conversations,
            'active_conversations': self.stats.active_conversations,
            'completed_conversations': self.stats.completed_conversations,
            'escalated_conversations': self.stats.escalated_conversations,
            'staff_handoffs': self.stats.staff_handoffs,
            'follow_ups_handled': self.stats.follow_ups_handled,
            'expired_conversations': self.stats.expired_conversations,
            'crisis_overrides': self.stats.crisis_overrides,
            'trigger_phrase_matches': self.stats.trigger_phrase_matches,
            'mention_triggers': self.stats.mention_triggers,
            'current_active_sessions': len(self.active_conversations)
        }
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get manager health status"""
        try:
            return {
                'status': 'healthy',
                'configuration_loaded': self.config is not None,
                'active_conversations': len(self.active_conversations),
                'claude_client_available': self.claude_client is not None,
                'crisis_analysis_manager_available': self.crisis_analysis_manager is not None,
                'conversation_timeout': self.conversation_timeout,
                'trigger_phrases_count': len(self.trigger_phrases)
            }
        except Exception as e:
            logger.error(f"❌ Error getting health status: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }

# ============================================================================
# FACTORY FUNCTION (Rule #1)
# ============================================================================

def create_conversation_handler_manager(
    config_manager: UnifiedConfigManager,
    logging_manager: LoggingConfigManager,
    crisis_analysis_manager: CrisisAnalysisManager,
    discord_client_manager: Optional[Any] = None
) -> ConversationHandlerManager:
    """
    Factory function to create ConversationHandlerManager (Rule #1)
    
    Args:
        config_manager: UnifiedConfigManager instance
        logging_manager: LoggingConfigManager instance
        crisis_analysis_manager: CrisisAnalysisManager instance
        discord_client_manager: DiscordClientManager instance (optional)
        
    Returns:
        ConversationHandlerManager: Configured manager instance
        
    Raises:
        Exception: If manager creation fails
    """
    try:
        logger.info("🏭 Creating ConversationHandlerManager using factory function")
        
        manager = ConversationHandlerManager(
            config_manager=config_manager,
            logging_manager=logging_manager,
            crisis_analysis_manager=crisis_analysis_manager,
            discord_client_manager=discord_client_manager
        )
        
        logger.info("✅ ConversationHandlerManager created successfully")
        return manager
        
    except Exception as e:
        logger.error(f"❌ Failed to create ConversationHandlerManager: {e}")
        raise