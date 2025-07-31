#!/usr/bin/env python3
"""
Message Handler - Enhanced for v3.0 NLP Integration - FIXED VERSION

Fixed to actually handle crisis responses instead of just detecting them.
"""

import logging
import time
from typing import Dict, Optional
from discord import Message

logger = logging.getLogger(__name__)

class MessageHandler:
    """Enhanced message handler for v3.0 NLP integration - FIXED"""
    
    def __init__(self, bot, claude_api=None, nlp_client=None, keyword_detector=None, crisis_handler=None, config=None, security_manager=None):
        """
        Enhanced initialization - SECURITY MANAGER IS NOW OPTIONAL
        """
        
        self.bot = bot
        self.claude_api = claude_api
        self.nlp_client = nlp_client
        self.keyword_detector = keyword_detector
        self.crisis_handler = crisis_handler
        self.config = config
        # SECURITY MANAGER IS NOW OPTIONAL AND IGNORED
        
        # Handle missing required components gracefully
        if not self.nlp_client:
            logger.warning("⚠️ NLP client not provided - NLP analysis will be skipped")
        
        if not self.keyword_detector:
            logger.warning("⚠️ Keyword detector not provided - keyword detection will be skipped")
        
        if not self.config:
            logger.warning("⚠️ Config not provided - using defaults")
            self.conversation_timeout = 300
            self.guild_id = None
        else:
            # Handle both config.get() and config.get_int() methods
            if hasattr(config, 'get_int'):
                self.conversation_timeout = config.get_int('BOT_CONVERSATION_TIMEOUT', 300)
                self.guild_id = config.get_int('BOT_GUILD_ID')
            else:
                self.conversation_timeout = config.get('BOT_CONVERSATION_TIMEOUT', 300)
                self.guild_id = config.get('BOT_GUILD_ID')
        
        # Enhanced statistics tracking
        self.message_stats = {
            'messages_processed': 0,
            'crisis_detected': 0,
            'crisis_responses_given': 0,
            'total_messages_processed': 0,
            'conversations_started': 0,
            'follow_ups_handled': 0,
            'rate_limits_hit': 0,
            'daily_limits_hit': 0,
            'ignored_follow_ups': 0,
            'intrusion_attempts_blocked': 0,
            'crisis_overrides_triggered': 0,
            'multiple_conversations_same_channel': 0,
            'detection_method_breakdown': {
                'keyword_only': 0,
                'nlp_primary': 0,
                'keyword_primary': 0,
                'hybrid_detection': 0
            },
            'v3_features': {
                'gaps_detected_count': 0,
                'staff_reviews_triggered': 0,
                'ensemble_analyses': 0
            }
        }
        
        # Conversation tracking
        self.active_conversations = {}
        
        # Rate limiting
        self.user_cooldowns = {}
        self.daily_call_count = 0
        self.max_daily_calls = 1000
        self.rate_limit_per_user = 10
        
        if self.config:
            if hasattr(config, 'get_int'):
                self.max_daily_calls = config.get_int('BOT_MAX_DAILY_CALLS', 1000)
                self.rate_limit_per_user = config.get_int('BOT_RATE_LIMIT_PER_USER', 10)
            else:
                self.max_daily_calls = config.get('BOT_MAX_DAILY_CALLS', 1000)
                self.rate_limit_per_user = config.get('BOT_RATE_LIMIT_PER_USER', 10)
        
        # Log initialization status
        logger.info("📨 Enhanced Message Handler initialized (FIXED VERSION)")
        logger.info(f"   🧠 NLP Client: {'✅ Available' if self.nlp_client else '❌ Missing'}")
        logger.info(f"   🔤 Keyword Detector: {'✅ Available' if self.keyword_detector else '❌ Missing'}")
        logger.info(f"   🚨 Crisis Handler: {'✅ Available' if self.crisis_handler else '❌ Missing'}")
        logger.info(f"   💬 Conversation timeout: {self.conversation_timeout}s")
        logger.info(f"   🎯 Guild ID: {self.guild_id}")

    async def handle_message(self, message: Message):
        """
        MAIN MESSAGE HANDLER - This is the method that should be called from bot_manager
        This method actually handles crisis responses, not just detection.
        """
        
        self.message_stats['total_messages_processed'] += 1
        
        logger.debug(f"📨 Handling message from {message.author}: '{message.content[:50]}...'")
        
        # Basic filtering
        if not self._should_process_message(message):
            return
        
        # Clean up expired conversations
        self.cleanup_expired_conversations()
        
        user_id = message.author.id
        
        # Check for active conversations (simplified logic)
        active_conversation = self.active_conversations.get(user_id)
        
        if active_conversation:
            # Handle conversation followup
            await self._handle_conversation_followup(message)
        else:
            # Handle potential new crisis
            await self._handle_potential_crisis(message)

    def _should_process_message(self, message: Message) -> bool:
        """Basic message filtering"""
        
        if message.author.bot:
            logger.debug(f"🤖 Ignored bot message from {message.author}")
            return False
        
        if not message.guild and self.guild_id:
            logger.debug(f"🚫 Ignored DM or wrong guild")
            return False
        
        if self.guild_id and message.guild.id != self.guild_id:
            logger.debug(f"🚫 Wrong guild: {message.guild.id} != {self.guild_id}")
            return False
        
        # Simple channel validation if config is available
        if self.config and hasattr(self.config, 'get_allowed_channels'):
            allowed_channels = self.config.get_allowed_channels()
            if allowed_channels and message.channel.id not in allowed_channels:
                logger.debug(f"🚫 Restricted channel: {message.channel.id}")
                return False
        
        logger.debug(f"✅ Processing message from {message.author}")
        return True

    async def _handle_potential_crisis(self, message: Message):
        """Handle potential crisis detection and response"""
        
        try:
            # Check rate limits
            if not await self.check_rate_limits(message.author.id):
                self.message_stats['rate_limits_hit'] += 1
                logger.debug(f"🚫 Rate limit hit for user {message.author.id}")
                return
            
            if self.daily_call_count >= self.max_daily_calls:
                self.message_stats['daily_limits_hit'] += 1
                logger.warning("🚫 Daily API call limit reached")
                return
            
            # Perform detection
            detection_result = await self._perform_hybrid_detection(message)
            
            logger.info(f"🔍 Detection result: needs_response={detection_result.get('needs_response', False)}, crisis_level={detection_result.get('crisis_level', 'none')}")
            
            if detection_result.get('needs_response', False):
                logger.info("✅ Crisis detected - triggering response")
                await self._handle_crisis_response(message, detection_result)
            else:
                logger.debug("ℹ️ No crisis detected")
        
        except Exception as e:
            logger.error(f"❌ Error handling potential crisis: {e}")
            logger.exception("Full traceback:")
            try:
                await message.add_reaction('❌')
            except:
                pass

    async def _handle_crisis_response(self, message: Message, detection_result: dict):
        """Handle the actual crisis response - this is where the actions happen"""
        
        try:
            crisis_level = detection_result['crisis_level']
            
            logger.info(f"🚨 HANDLING CRISIS RESPONSE:")
            logger.info(f"   👤 User: {message.author} ({message.author.id})")
            logger.info(f"   🚨 Level: {crisis_level}")
            logger.info(f"   🔍 Method: {detection_result.get('method', 'unknown')}")
            logger.info(f"   📊 Confidence: {detection_result.get('confidence', 0):.3f}")
            
            # Get response from Claude API (with fallback)
            response = "I'm here to support you through this difficult time. You're not alone, and reaching out shows real strength."
            
            if self.claude_api:
                try:
                    logger.debug("🧠 Getting Claude API response...")
                    response = await self.claude_api.get_ash_response(
                        message.content,
                        crisis_level,
                        message.author.display_name
                    )
                    logger.info("✅ Got Claude API response")
                except Exception as e:
                    logger.warning(f"⚠️ Claude API failed, using fallback: {e}")
            else:
                logger.info("ℹ️ No Claude API - using fallback response")
            
            # Call crisis handler to perform the actions
            if self.crisis_handler:
                logger.info("📞 Calling crisis handler for response and escalation...")
                await self.crisis_handler.handle_crisis_response_with_instructions(
                    message, crisis_level, response
                )
                logger.info("✅ Crisis handler completed")
            else:
                logger.error("❌ No crisis handler available - sending basic response")
                await message.reply(response)
            
            # Start conversation tracking
            self.start_conversation_tracking(message.author.id, crisis_level, message.channel.id)
            
            # Update counters
            self.daily_call_count += 1
            await self.record_api_call(message.author.id)
            self.message_stats['crisis_responses_given'] += 1
            
            logger.info(f"✅ Crisis response completed for {message.author}")
            
        except Exception as e:
            logger.error(f"❌ Error handling crisis response: {e}")
            logger.exception("Full traceback:")
            try:
                await message.add_reaction('❌')
            except:
                pass

    async def _perform_hybrid_detection(self, message: Message) -> Dict:
        """Perform hybrid crisis detection"""
        
        # Validate message content
        if not hasattr(message, 'content') or not message.content:
            logger.error(f"❌ Invalid message content")
            return {
                'needs_response': False,
                'crisis_level': 'none',
                'method': 'validation_error',
                'confidence': 0.0,
                'detected_categories': []
            }
        
        message_content = message.content.strip()
        if not message_content:
            logger.debug(f"📭 Empty message content")
            return {
                'needs_response': False,
                'crisis_level': 'none',
                'method': 'empty_message',
                'confidence': 0.0,
                'detected_categories': []
            }
        
        logger.debug(f"🔍 Analyzing message: '{message_content[:50]}...'")
        
        # Method 1: Keyword detection
        keyword_result = {'needs_response': False, 'crisis_level': 'none', 'detected_categories': []}
        
        if self.keyword_detector:
            try:
                keyword_result = self.keyword_detector.check_message(message_content)
                logger.info(f"🔤 Keyword detection: {keyword_result['crisis_level']} (needs_response: {keyword_result.get('needs_response', False)})")
            except Exception as e:
                logger.error(f"🔤 Keyword detector error: {e}")
        else:
            logger.warning("🔤 No keyword detector available")
        
        # Method 2: NLP analysis
        nlp_result = None
        if self.nlp_client:
            try:
                logger.debug(f"🧠 Calling NLP analysis...")
                nlp_result = await self.nlp_client.analyze_message(
                    message_content,
                    str(message.author.id),
                    str(message.channel.id)
                )
                if nlp_result:
                    logger.info(f"🧠 NLP v3.0 analysis: {nlp_result.get('crisis_level', 'none')} "
                               f"(confidence: {nlp_result.get('confidence_score', 0):.3f}) "
                               f"via {nlp_result.get('method', 'unknown')}")
                    
                    # Log v3.0 features
                    if nlp_result.get('gaps_detected'):
                        logger.warning(f"⚠️ Model disagreement detected")
                        self.message_stats['v3_features']['gaps_detected_count'] += 1
                    
                    if nlp_result.get('requires_staff_review'):
                        logger.info(f"👥 Staff review flagged")
                        self.message_stats['v3_features']['staff_reviews_triggered'] += 1
                    
                    self.message_stats['v3_features']['ensemble_analyses'] += 1
                else:
                    logger.info("🧠 NLP analysis returned None")
            except Exception as e:
                logger.warning(f"🧠 NLP analysis failed: {e}")
        else:
            logger.warning("🧠 No NLP client available")
        
        # Combine results
        final_result = self._combine_detection_results(keyword_result, nlp_result)
        
        logger.info(f"⚡ Final decision: {final_result.get('crisis_level', 'unknown')} "
                   f"via {final_result.get('method', 'unknown')} "
                   f"(confidence: {final_result.get('confidence', 0):.3f})")
        
        # Update statistics
        method = final_result.get('method', 'unknown')
        if method in self.message_stats['detection_method_breakdown']:
            self.message_stats['detection_method_breakdown'][method] += 1
        
        return final_result

    def _combine_detection_results(self, keyword_result: Dict, nlp_result: Optional[Dict]) -> Dict:
        """Combine keyword and NLP detection results"""
        
        # If NLP unavailable, use keywords only
        if not nlp_result:
            self.message_stats['detection_method_breakdown']['keyword_only'] += 1
            return {
                'needs_response': keyword_result.get('needs_response', False),
                'crisis_level': keyword_result.get('crisis_level', 'none'),
                'method': 'keyword_only',
                'confidence': 0.9 if keyword_result.get('needs_response', False) else 0.0,
                'detected_categories': keyword_result.get('detected_categories', [])
            }

        # Both methods available - hybrid logic
        keyword_level = keyword_result.get('crisis_level', 'none')
        nlp_level = nlp_result.get('crisis_level', 'none')
        
        # Crisis level hierarchy
        hierarchy = {'none': 0, 'low': 1, 'medium': 2, 'high': 3}
        
        # Use the higher of the two crisis levels (safety-first)
        if hierarchy[keyword_level] >= hierarchy[nlp_level]:
            final_level = keyword_level
            method = 'keyword_primary'
            confidence = 0.9 if keyword_result.get('needs_response', False) else 0.0
        else:
            final_level = nlp_level
            method = 'nlp_primary'
            confidence = nlp_result.get('confidence_score', 0.5)
        
        self.message_stats['detection_method_breakdown']['hybrid_detection'] += 1
        
        return {
            'needs_response': final_level != 'none',
            'crisis_level': final_level,
            'method': method,
            'confidence': confidence,
            'detected_categories': keyword_result.get('detected_categories', []) + nlp_result.get('detected_categories', []),
            'keyword_result': keyword_level,
            'nlp_result': nlp_level,
            'requires_staff_review': nlp_result.get('requires_staff_review', final_level == 'high'),
            'gaps_detected': nlp_result.get('gaps_detected', False)
        }

    # Rate limiting methods
    async def check_rate_limits(self, user_id: int) -> bool:
        """Check if user is within rate limits"""
        current_time = time.time()
        
        if user_id not in self.user_cooldowns:
            self.user_cooldowns[user_id] = []
        
        # Clean old entries (older than 1 hour)
        self.user_cooldowns[user_id] = [
            timestamp for timestamp in self.user_cooldowns[user_id]
            if current_time - timestamp < 3600
        ]
        
        # Check if under limit
        if len(self.user_cooldowns[user_id]) >= self.rate_limit_per_user:
            return False
        
        return True

    async def record_api_call(self, user_id: int):
        """Record an API call for rate limiting"""
        current_time = time.time()
        
        if user_id not in self.user_cooldowns:
            self.user_cooldowns[user_id] = []
        
        self.user_cooldowns[user_id].append(current_time)

    def cleanup_expired_conversations(self):
        """Clean up expired conversations"""
        current_time = time.time()
        expired_users = []
        
        for user_id, conv_data in self.active_conversations.items():
            if current_time - conv_data['start_time'] > self.conversation_timeout:
                expired_users.append(user_id)
        
        for user_id in expired_users:
            conv = self.active_conversations[user_id]
            duration = current_time - conv['start_time']
            
            logger.info(f"💬 Conversation expired for user {user_id} (duration: {duration:.1f}s)")
            del self.active_conversations[user_id]

    def start_conversation_tracking(self, user_id: int, crisis_level: str, channel_id: int):
        """Start tracking a conversation"""
        
        self.active_conversations[user_id] = {
            'start_time': time.time(),
            'crisis_level': crisis_level,
            'channel_id': channel_id,
            'follow_up_count': 0,
            'escalations': 0,
            'initial_crisis_level': crisis_level
        }
        
        self.message_stats['conversations_started'] += 1
        logger.info(f"💬 Started conversation tracking for user {user_id} (level: {crisis_level})")

    async def _handle_conversation_followup(self, message: Message):
        """Handle conversation follow-up"""
        
        user_id = message.author.id
        conversation = self.active_conversations[user_id]
        
        # Only respond in same channel
        if message.channel.id != conversation['channel_id']:
            return
        
        # Check if user properly triggered continuation (simplified)
        if not self._should_respond_in_conversation(message, user_id):
            logger.info(f"💬 Ignoring follow-up from {message.author} - no trigger")
            return
        
        self.message_stats['follow_ups_handled'] += 1
        
        try:
            logger.info(f"💬 Handling conversation follow-up from {message.author}")
            
            # Get response
            if self.claude_api:
                response = await self.claude_api.get_ash_response(
                    message.content,
                    conversation['crisis_level'],
                    message.author.display_name
                )
            else:
                response = "I'm still here with you. Thank you for continuing to share with me."
            
            await message.reply(response)
            
            # Update conversation stats
            conversation['follow_up_count'] += 1
            
            logger.info(f"✅ Follow-up handled (#{conversation['follow_up_count']})")
        
        except Exception as e:
            logger.error(f"❌ Error handling conversation follow-up: {e}")
            try:
                await message.add_reaction('❌')
            except:
                pass

    def _should_respond_in_conversation(self, message: Message, original_user_id: int) -> bool:
        """Check if should respond during conversation"""
        
        # Only respond to the original user
        if message.author.id != original_user_id:
            return False
        
        # Check for bot mention
        if self.bot.user in message.mentions:
            logger.debug(f"✅ Bot mentioned by user {message.author.id}")
            return True
        
        # Check for trigger phrases
        trigger_phrases = ['ash', 'hey ash', 'ash help']
        if self.config and hasattr(self.config, 'get'):
            trigger_phrases = self.config.get('BOT_CONVERSATION_TRIGGER_PHRASES', 'ash,hey ash,ash help').split(',')
        
        message_lower = message.content.lower().strip()
        
        for trigger in trigger_phrases:
            trigger = trigger.strip().lower()
            if trigger in message_lower:
                logger.debug(f"✅ Trigger phrase '{trigger}' found")
                return True
        
        return False

    # Keep the existing process_message method for backward compatibility
    async def process_message(self, message: Message) -> Optional[Dict]:
        """
        Backward compatibility method - just does detection, doesn't handle response
        """
        
        self.message_stats['messages_processed'] += 1
        
        # Perform detection only
        detection_result = await self._perform_hybrid_detection(message)
        
        if detection_result['needs_response']:
            self.message_stats['crisis_detected'] += 1
            logger.info(f"🚨 Crisis detected: {detection_result['crisis_level']}")
            return detection_result
        
        return None

    def get_message_handler_stats(self) -> Dict:
        """Get statistics for monitoring commands"""
        
        return {
            'message_processing': {
                'total_messages_processed': self.message_stats['total_messages_processed'],
                'crisis_responses_given': self.message_stats['crisis_responses_given'],
                'messages_processed_today': self.message_stats['messages_processed']
            },
            'conversation_tracking': {
                'conversations_started': self.message_stats['conversations_started'],
                'follow_ups_handled': self.message_stats['follow_ups_handled'],
                'active_conversations': len(self.active_conversations)
            },
            'detection_methods': self.message_stats['detection_method_breakdown'].copy(),
            'v3_ensemble_features': self.message_stats['v3_features'].copy()
        }

# Aliases for backward compatibility
EnhancedMessageHandler = MessageHandler