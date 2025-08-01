#!/usr/bin/env python3
"""
Message Handler - ENHANCED VERSION WITH CRISIS CONVERSATION ISOLATION
"""

import logging
import time
from typing import Dict, Optional
from discord import Message

logger = logging.getLogger(__name__)

class MessageHandler:
    """Enhanced message handler with full conversation isolation"""
    
    def __init__(self, bot, claude_api=None, nlp_client=None, keyword_detector=None, crisis_handler=None, config=None):
        """
        Enhanced initialization with conversation isolation
        """
        
        self.bot = bot
        self.claude_api = claude_api
        self.nlp_client = nlp_client
        self.keyword_detector = keyword_detector
        self.crisis_handler = crisis_handler
        self.config = config
        
        # Handle missing required components gracefully
        if not self.nlp_client:
            raise ValueError("NLP client is required for v3.0")

        if not self.keyword_detector:
            raise ValueError("Keyword detector is required for v3.0")
        
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
        logger.info("📨 Enhanced Message Handler initialized with CONVERSATION ISOLATION")
        logger.info(f"   🧠 NLP Client: {'✅ Available' if self.nlp_client else '❌ Missing'}")
        logger.info(f"   🔤 Keyword Detector: {'✅ Available' if self.keyword_detector else '❌ Missing'}")
        logger.info(f"   🚨 Crisis Handler: {'✅ Available' if self.crisis_handler else '❌ Missing'}")
        logger.info(f"   💬 Conversation timeout: {self.conversation_timeout}s")
        logger.info(f"   🎯 Guild ID: {self.guild_id}")
        logger.info(f"   🛡️ Conversation isolation: ENABLED")

    async def handle_message(self, message: Message):
        """
        ENHANCED MESSAGE HANDLER WITH CHANNEL-LEVEL CONVERSATION ISOLATION
        """
        
        self.message_stats['total_messages_processed'] += 1
        
        logger.info(f"📨 DIAGNOSTIC: Handling message from {message.author}: '{message.content[:50]}...'")
        
        # Basic filtering
        if not self._should_process_message(message):
            return
        
        # Clean up expired conversations
        self.cleanup_expired_conversations()
        
        user_id = message.author.id
        
        # CRITICAL: Check if ANY user has an active conversation in this channel
        active_conversation_in_channel = self._get_active_conversation_in_channel(message.channel.id)
        
        if active_conversation_in_channel:
            conversation_owner_id, conversation_data = active_conversation_in_channel
            
            if user_id == conversation_owner_id:
                # This is the conversation owner - check if they properly triggered continuation
                should_respond = self._should_respond_in_conversation(message, user_id)
                if should_respond:
                    await self._handle_conversation_followup(message)
                else:
                    self._log_conversation_attempt(message, conversation_data, "no mention or trigger phrase")
            else:
                # SAFETY OVERRIDE: Check if this is a NEW CRISIS that needs immediate response
                crisis_override_needed = await self._check_crisis_override(message)
                
                if crisis_override_needed:
                    # This is a genuine crisis - respond immediately despite active conversation
                    logger.warning(f"🚨 CRISIS OVERRIDE: New crisis detected during active conversation")
                    logger.warning(f"   👤 Active conversation owner: {conversation_owner_id}")
                    logger.warning(f"   🆘 New crisis user: {user_id} ({message.author.display_name})")
                    await self._handle_potential_crisis(message)
                else:
                    # Not a crisis - STRICT BLOCK
                    self._log_conversation_intrusion_attempt(message, conversation_data, conversation_owner_id)
                    logger.info(f"🛡️ STRICT ISOLATION: Blocked non-crisis message from {message.author.display_name} during active conversation")
                    return
        else:
            # No active conversations in this channel - normal crisis detection
            await self._handle_potential_crisis(message)

    def _get_active_conversation_in_channel(self, channel_id: int) -> Optional[tuple]:
        """Get the active conversation in a specific channel (if any)"""
        
        for user_id, conversation_data in self.active_conversations.items():
            if conversation_data['channel_id'] == channel_id:
                return (user_id, conversation_data)
        
        return None

    async def _check_crisis_override(self, message: Message) -> bool:
        """Check if a message contains crisis indicators that override conversation isolation"""
        
        try:
            # Perform crisis detection without starting a conversation
            detection_result = await self._perform_enhanced_hybrid_detection(message)
            crisis_level = detection_result.get('crisis_level', 'none')
            
            # Only override for medium and high crises (configurable)
            override_levels = ['medium', 'high']  # Default since config might not have get method
            if self.config and hasattr(self.config, 'get'):
                override_levels = self.config.get('BOT_CRISIS_OVERRIDE_LEVELS', 'medium,high').split(',')
                override_levels = [level.strip().lower() for level in override_levels]
            
            should_override = crisis_level in override_levels
            
            if should_override:
                logger.warning(f"🚨 Crisis override triggered:")
                logger.warning(f"   📊 Crisis level: {crisis_level}")
                logger.warning(f"   🔍 Detection method: {detection_result.get('method', 'unknown')}")
                logger.warning(f"   📈 Confidence: {detection_result.get('confidence', 0):.2f}")
                logger.warning(f"   👤 User: {message.author} ({message.author.id})")
                
                # Track crisis overrides in stats
                self.message_stats['crisis_overrides_triggered'] += 1
            
            return should_override
            
        except Exception as e:
            logger.error(f"❌ Error in crisis override check: {e}")
            # If we can't check, err on the side of caution and allow override
            return True

    def _log_conversation_intrusion_attempt(self, message: Message, conversation_data: dict, conversation_owner_id: int):
        """Enhanced logging for blocked intrusion attempts"""
        
        logger.warning(f"🚨 CONVERSATION INTRUSION BLOCKED:")
        logger.warning(f"   👤 Conversation owner: {conversation_owner_id}")
        logger.warning(f"   🚫 Blocked user: {message.author.id} ({message.author.display_name})")
        logger.warning(f"   📍 Channel: {message.channel.id} ({message.channel.name})")
        logger.warning(f"   🚨 Crisis level: {conversation_data.get('crisis_level', 'unknown')}")
        logger.warning(f"   📝 Blocked message: '{message.content[:100]}...'")
        logger.warning(f"   ⏱️ Conversation time: {time.time() - conversation_data.get('start_time', 0):.1f}s")
        
        # Track intrusion attempts in stats
        self.message_stats['intrusion_attempts_blocked'] += 1
        
        # Optional: Add reaction to show the message was seen but ignored
        try:
            await message.add_reaction('🔒')  # Lock emoji to indicate conversation is locked
        except Exception as e:
            logger.debug(f"Could not add lock reaction: {e}")

    def _log_conversation_attempt(self, message: Message, conversation_data: dict, reason: str):
        """Log when users try to continue conversations without proper triggers"""
        
        logger.info(f"💬 Conversation attempt from user {message.author.id}:")
        logger.info(f"   📝 Message: '{message.content[:50]}...'")
        logger.info(f"   🚫 Reason ignored: {reason}")
        logger.info(f"   🚨 Conversation level: {conversation_data.get('crisis_level', 'unknown')}")
        
        # Track this in stats
        self.message_stats['ignored_follow_ups'] += 1

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
            detection_result = await self._perform_enhanced_hybrid_detection(message)
            
            logger.warning(f"🔍 DIAGNOSTIC: Detection result: needs_response={detection_result.get('needs_response', False)}, crisis_level={detection_result.get('crisis_level', 'none')}")
            
            if detection_result.get('needs_response', False):
                logger.warning("✅ DIAGNOSTIC: Crisis detected - triggering response")
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
            
            logger.warning(f"🚨 DIAGNOSTIC: HANDLING CRISIS RESPONSE:")
            logger.warning(f"   👤 User: {message.author} ({message.author.id})")
            logger.warning(f"   🚨 Level: {crisis_level}")
            logger.warning(f"   🔍 Method: {detection_result.get('method', 'unknown')}")
            logger.warning(f"   📊 Confidence: {detection_result.get('confidence', 0):.3f}")
            
            # Get response from Claude API (with fallback)
            response = "I'm here to support you through this difficult time. You're not alone, and reaching out shows real strength."
            
            if self.claude_api:
                try:
                    logger.warning("🧠 DIAGNOSTIC: Getting Claude API response...")
                    response = await self.claude_api.get_ash_response(
                        message.content,
                        crisis_level,
                        message.author.display_name
                    )
                    logger.warning("✅ DIAGNOSTIC: Got Claude API response")
                except Exception as e:
                    logger.warning(f"⚠️ DIAGNOSTIC: Claude API failed, using fallback: {e}")
            else:
                logger.warning("ℹ️ DIAGNOSTIC: No Claude API - using fallback response")
            
            # Call crisis handler to perform the actions
            if self.crisis_handler:
                logger.warning("📞 DIAGNOSTIC: Calling crisis handler for response and escalation...")
                await self.crisis_handler.handle_crisis_response_with_instructions(
                    message, crisis_level, response
                )
                logger.warning("✅ DIAGNOSTIC: Crisis handler completed")
            else:
                logger.error("❌ DIAGNOSTIC: No crisis handler available - sending basic response")
                await message.reply(response)
            
            # Start conversation tracking
            self.start_conversation_tracking(message.author.id, crisis_level, message.channel.id)
            
            # Update counters
            self.daily_call_count += 1
            await self.record_api_call(message.author.id)
            self.message_stats['crisis_responses_given'] += 1
            
            logger.warning(f"✅ DIAGNOSTIC: Crisis response completed for {message.author}")
            
        except Exception as e:
            logger.error(f"❌ DIAGNOSTIC: Error handling crisis response: {e}")
            logger.exception("Full traceback:")
            try:
                await message.add_reaction('❌')
            except:
                pass

    async def _perform_enhanced_hybrid_detection(self, message: Message) -> Dict:
        """Perform enhanced hybrid crisis detection with v3.0 NLP features"""
        
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
        
        logger.warning(f"🔍 DIAGNOSTIC: Analyzing message: '{message_content[:50]}...'")
        
        # Method 1: Keyword detection
        keyword_result = {'needs_response': False, 'crisis_level': 'none', 'detected_categories': []}
        
        if self.keyword_detector:
            try:
                keyword_result = self.keyword_detector.check_message(message_content)
                logger.warning(f"🔤 DIAGNOSTIC: Keyword detection: {keyword_result['crisis_level']} (needs_response: {keyword_result.get('needs_response', False)})")
            except Exception as e:
                logger.error(f"🔤 Keyword detector error: {e}")
        else:
            logger.warning("🔤 DIAGNOSTIC: No keyword detector available")
        
        # Method 2: Enhanced NLP analysis with v3.0 features
        nlp_result = None
        if self.nlp_client:
            try:
                logger.warning(f"🧠 DIAGNOSTIC: Calling enhanced NLP analysis...")
                nlp_result = await self.nlp_client.analyze_message(
                    message_content,
                    str(message.author.id),
                    str(message.channel.id)
                )
                if nlp_result:
                    logger.warning(f"🧠 DIAGNOSTIC: Enhanced NLP v3.0 analysis: {nlp_result.get('crisis_level', 'none')} "
                               f"(confidence: {nlp_result.get('confidence_score', 0):.3f}) "
                               f"via {nlp_result.get('method', 'unknown')}")
                    
                    # Log v3.0 features
                    if nlp_result.get('gaps_detected'):
                        logger.warning(f"⚠️ DIAGNOSTIC: Model disagreement detected")
                        self.message_stats['v3_features']['gaps_detected_count'] += 1
                    
                    if nlp_result.get('requires_staff_review'):
                        logger.warning(f"👥 DIAGNOSTIC: Staff review flagged")
                        self.message_stats['v3_features']['staff_reviews_triggered'] += 1
                    
                    self.message_stats['v3_features']['ensemble_analyses'] += 1
                else:
                    logger.warning("🧠 DIAGNOSTIC: Enhanced NLP analysis returned None")
            except Exception as e:
                logger.warning(f"🧠 DIAGNOSTIC: Enhanced NLP analysis failed: {e}")
        else:
            logger.warning("🧠 DIAGNOSTIC: No NLP client available")
        
        # Combine results with enhanced logic
        final_result = self._combine_detection_results(keyword_result, nlp_result)
        
        logger.warning(f"⚡ DIAGNOSTIC: Final decision: {final_result.get('crisis_level', 'unknown')} "
                   f"via {final_result.get('method', 'unknown')} "
                   f"(confidence: {final_result.get('confidence', 0):.3f})")
        
        # Update statistics
        method = final_result.get('method', 'unknown')
        if method in self.message_stats['detection_method_breakdown']:
            self.message_stats['detection_method_breakdown'][method] += 1
        
        return final_result

    def _combine_detection_results(self, keyword_result: Dict, nlp_result: Optional[Dict]) -> Dict:
        """Combine keyword and NLP detection results with enhanced v3.0 logic"""
        
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

        # Both methods available - enhanced hybrid logic
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
            'gaps_detected': nlp_result.get('gaps_detected', False),
            'ensemble_details': nlp_result.get('ensemble_details', {}),
            'processing_time_ms': nlp_result.get('processing_time_ms', 0)
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
        """Enhanced conversation tracking with multiple conversation support"""
        
        # Check if there's already a conversation in this channel
        existing_conversation = self._get_active_conversation_in_channel(channel_id)
        
        if existing_conversation:
            existing_user_id, existing_data = existing_conversation
            logger.warning(f"⚠️ Starting new conversation while another is active:")
            logger.warning(f"   📍 Channel: {channel_id}")
            logger.warning(f"   👤 Existing: User {existing_user_id} ({existing_data['crisis_level']} crisis)")
            logger.warning(f"   🆕 New: User {user_id} ({crisis_level} crisis)")
            
            # Track this situation in stats
            self.message_stats['multiple_conversations_same_channel'] += 1
        
        self.active_conversations[user_id] = {
            'start_time': time.time(),
            'crisis_level': crisis_level,
            'channel_id': channel_id,
            'follow_up_count': 0,
            'escalations': 0,
            'initial_crisis_level': crisis_level,
            'is_crisis_override': existing_conversation is not None  # Track if this overrode another conversation
        }
        
        self.message_stats['conversations_started'] += 1
        logger.info(f"💬 Started enhanced conversation tracking:")
        logger.info(f"   👤 User: {user_id}")
        logger.info(f"   🚨 Crisis level: {crisis_level}")
        logger.info(f"   📍 Channel: {channel_id}")
        logger.info(f"   🔄 Override situation: {'Yes' if existing_conversation else 'No'}")
        logger.info(f"   📊 Total conversations today: {self.message_stats['conversations_started']}")

    async def _handle_conversation_followup(self, message: Message):
        """Handle conversation follow-up with enhanced isolation logic"""
        
        user_id = message.author.id
        conversation = self.active_conversations[user_id]
        
        # Only respond in same channel
        if message.channel.id != conversation['channel_id']:
            logger.debug(f"💬 Wrong channel for follow-up from {message.author}")
            return
        
        # Check if user properly triggered continuation (enhanced)
        if not self._should_respond_in_conversation(message, user_id):
            logger.info(f"💬 Ignoring follow-up from {message.author} - no trigger")
            self.message_stats['ignored_follow_ups'] += 1
            return
        
        self.message_stats['follow_ups_handled'] += 1
        
        try:
            logger.info(f"💬 Handling conversation follow-up from {message.author}")
            
            # Check for escalation
            detection_result = await self._perform_enhanced_hybrid_detection(message)
            new_level = detection_result.get('crisis_level', 'none')
            current_level = conversation['crisis_level']
            
            # Check if this is an escalation
            is_escalation = self._is_escalation(current_level, new_level)
            
            if is_escalation:
                logger.warning(f"📈 Crisis escalation detected: {current_level} → {new_level}")
                conversation['crisis_level'] = new_level
                conversation['escalations'] += 1
            
            # Get response based on current/escalated level
            effective_level = new_level if is_escalation else current_level
            
            if self.claude_api:
                response = await self.claude_api.get_ash_response(
                    message.content,
                    effective_level,
                    message.author.display_name
                )
            else:
                response = "I'm still here with you. Thank you for continuing to share with me."
            
            await message.reply(response)
            
            # Update conversation stats
            conversation['follow_up_count'] += 1
            
            # If escalated, potentially re-trigger crisis alerts
            if is_escalation and self.crisis_handler:
                logger.warning(f"🚨 Re-triggering crisis alerts due to escalation to {new_level}")
                await self.crisis_handler.handle_escalation(message, current_level, new_level)
            
            logger.info(f"✅ Follow-up handled (#{conversation['follow_up_count']}, escalation: {is_escalation})")
        
        except Exception as e:
            logger.error(f"❌ Error handling conversation follow-up: {e}")
            try:
                await message.add_reaction('❌')
            except:
                pass

    def _should_respond_in_conversation(self, message: Message, original_user_id: int) -> bool:
        """
        ENHANCED: Stricter conversation isolation logic
        Only respond if ALL conditions are met:
        1. Message is from the original crisis user
        2. User properly mentioned Ash or used trigger phrase
        3. Channel matches the original conversation
        """
        
        # CRITICAL: Only respond to the original user
        if message.author.id != original_user_id:
            logger.debug(f"🚫 BLOCKED: Different user {message.author.id} vs conversation owner {original_user_id}")
            return False
        
        # Verify we're in the same channel as the original conversation
        conversation = self.active_conversations.get(original_user_id)
        if not conversation or message.channel.id != conversation['channel_id']:
            logger.debug(f"🚫 BLOCKED: Wrong channel for conversation with user {original_user_id}")
            return False
        
        # STRICT: Check for bot mention (@Ash) - highest priority
        if self.bot.user in message.mentions:
            logger.debug(f"✅ APPROVED: Bot mentioned by conversation owner {message.author.id}")
            return True
        
        # STRICT: Check for configurable trigger phrases (case-insensitive)
        trigger_phrases = ['ash', 'hey ash', 'ash help', '@ash']
        if self.config and hasattr(self.config, 'get'):
            trigger_phrases = self.config.get('BOT_CONVERSATION_TRIGGER_PHRASES', 'ash,hey ash,ash help,@ash').split(',')
        
        message_lower = message.content.lower().strip()
        
        for trigger in trigger_phrases:
            trigger = trigger.strip().lower()
            if trigger and trigger in message_lower:
                logger.debug(f"✅ APPROVED: Trigger phrase '{trigger}' found from conversation owner {message.author.id}")
                return True
        
        # ENHANCED: If conversation starters are enabled, check those too (but with strict config check)
        allow_starters = False
        if self.config:
            if hasattr(self.config, 'get_bool'):
                allow_starters = self.config.get_bool('BOT_CONVERSATION_ALLOW_STARTERS', False)
            elif hasattr(self.config, 'get'):
                allow_starters = self.config.get('BOT_CONVERSATION_ALLOW_STARTERS', 'false').lower() == 'true'
        
        if allow_starters:
            conversation_starters = [
                "i'm still", "i still", "but i", "what if", "can you", 
                "help me", "i need", "it's getting", "i feel", "this is"
            ]
            
            for starter in conversation_starters:
                if message_lower.startswith(starter):
                    logger.debug(f"✅ APPROVED: Conversation starter '{starter}' from owner {message.author.id}")
                    return True
        
        # DEFAULT: Block the message
        logger.debug(f"🚫 BLOCKED: No valid trigger found in message from user {message.author.id}: '{message.content[:30]}...'")
        return False

    def _is_escalation(self, current_level: str, new_level: str) -> bool:
        """Check if crisis level has escalated"""
        hierarchy = {'none': 0, 'low': 1, 'medium': 2, 'high': 3}
        return hierarchy.get(new_level, 0) > hierarchy.get(current_level, 0)

    def get_enhanced_stats(self) -> Dict:
        """
        Get enhanced statistics including v3.0 features AND all backward compatibility fields
        """
        
        # Calculate derived statistics
        total_processed = max(1, self.message_stats['total_messages_processed'])
        crisis_given = self.message_stats['crisis_responses_given']
        
        # V3.0 ensemble statistics
        v3_features = self.message_stats['v3_features']
        ensemble_analyses = v3_features['ensemble_analyses']
        gaps_detected = v3_features['gaps_detected_count']
        staff_reviews = v3_features['staff_reviews_triggered']
        
        # Calculate rates
        gap_detection_rate = (gaps_detected / max(1, ensemble_analyses)) if ensemble_analyses > 0 else 0.0
        staff_review_rate = (staff_reviews / max(1, ensemble_analyses)) if ensemble_analyses > 0 else 0.0
        
        # Detection method breakdown
        method_breakdown = self.message_stats['detection_method_breakdown']
        total_detections = sum(method_breakdown.values())
        
        # Calculate consensus statistics (for monitoring commands)
        unanimous_consensus_count = max(0, total_detections - gaps_detected)
        model_disagreement_count = gaps_detected
        unanimous_consensus_rate = (unanimous_consensus_count / max(1, total_detections)) if total_detections > 0 else 1.0
        
        return {
            # Core processing statistics
            'total_messages_processed': self.message_stats['total_messages_processed'],
            'crisis_responses_given': self.message_stats['crisis_responses_given'],
            
            # Conversation tracking
            'conversations_started': self.message_stats['conversations_started'],
            'follow_ups_handled': self.message_stats['follow_ups_handled'],
            'ignored_follow_ups': self.message_stats['ignored_follow_ups'],
            'intrusion_attempts_blocked': self.message_stats['intrusion_attempts_blocked'],
            'crisis_overrides_triggered': self.message_stats['crisis_overrides_triggered'],
            'multiple_conversations_same_channel': self.message_stats['multiple_conversations_same_channel'],
            
            # Rate limiting
            'rate_limits_hit': self.message_stats['rate_limits_hit'],
            'daily_limits_hit': self.message_stats['daily_limits_hit'],
            
            # Detection method breakdown
            'detection_method_breakdown': method_breakdown.copy(),
            
            # V3.0 Ensemble Features - formatted for monitoring commands
            'ensemble_analyses_performed': ensemble_analyses,
            'gaps_detected': gaps_detected,
            'staff_reviews_flagged': staff_reviews,
            'gap_detection_rate': gap_detection_rate,
            'staff_review_rate': staff_review_rate,
            
            # Consensus analysis (for ensemble_stats command)
            'unanimous_consensus_count': unanimous_consensus_count,
            'model_disagreement_count': model_disagreement_count,
            'unanimous_consensus_rate': unanimous_consensus_rate,
            
            # Active conversations
            'active_conversations': len(self.active_conversations),
            
            # Derived rates and percentages
            'detection_rate': (crisis_given / total_processed),
            'success_rate_percent': max(0.0, 100.0 - (
                (self.message_stats['rate_limits_hit'] + self.message_stats['daily_limits_hit']) * 100.0 / total_processed
            )),
            
            # V3.0 features grouped (for backward compatibility)
            'v3_ensemble_features': {
                'ensemble_analyses': ensemble_analyses,
                'gaps_detected_count': gaps_detected,
                'staff_reviews_triggered': staff_reviews,
                'gap_detection_rate': gap_detection_rate,
                'staff_review_rate': staff_review_rate
            }
        }