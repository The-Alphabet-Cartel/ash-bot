"""
Enhanced Message Handler with Crisis Override System
"""

import logging
import asyncio
import time
from discord import Message
from typing import Dict, Optional
from handlers.crisis_handler import CrisisHandler
from integrations.claude_api import ClaudeAPI

logger = logging.getLogger(__name__)

class MessageHandler:
    """Enhanced message processing with crisis override system"""
    
    def __init__(self, bot, claude_api, nlp_client, keyword_detector, crisis_handler, config, security_manager=None):
        """Enhanced initialization with optional security manager"""
        
        self.bot = bot
        self.claude_api = claude_api
        self.nlp_client = nlp_client
        self.keyword_detector = keyword_detector
        self.crisis_handler = crisis_handler
        self.config = config
        
        # Security manager (optional for backwards compatibility)
        self.security_manager = security_manager
        if self.security_manager:
            logger.info("✅ Security manager integrated with message handler")
        else:
            logger.info("⚠️ Security manager not provided - running without security features")
        
        # Conversation tracking (enhanced)
        self.active_conversations = {}
        self.conversation_timeout = config.get_int('CONVERSATION_TIMEOUT', 300)
        
        # Rate limiting (enhanced)
        self.user_cooldowns = {}
        self.daily_call_count = 0
        self.max_daily_calls = config.get_int('MAX_DAILY_CALLS', 1000)
        self.rate_limit_per_user = config.get_int('RATE_LIMIT_PER_USER', 10)
        
        # Enhanced statistics
        self.message_stats = {
            'total_messages_processed': 0,
            'crisis_responses_given': 0,
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
                'hybrid_detection': 0
            }
        }
        
        self.guild_id = config.get_int('GUILD_ID')
        
        logger.info("📨 Enhanced message handler with crisis override initialized")
        logger.info(f"   🎯 Guild ID: {self.guild_id}")
        logger.info(f"   📊 Rate limits: {self.rate_limit_per_user}/hour per user, {self.max_daily_calls}/day total")
        logger.info(f"   💬 Conversation timeout: {self.conversation_timeout}s")
        logger.info(f"   🔐 Security manager: {'✅ Enabled' if self.security_manager else '❌ Disabled'}")
        logger.info(f"   🚨 Crisis override levels: {config.get('CRISIS_OVERRIDE_LEVELS', 'medium,high')}")

    async def handle_message(self, message: Message):
        """Enhanced message handling with crisis override and strict conversation isolation"""
        
        self.message_stats['total_messages_processed'] += 1
        
        if not self._should_process_message(message):
            return
        
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
                    # Not a crisis - block the intrusion attempt
                    self._log_conversation_intrusion_attempt(message, conversation_data, conversation_owner_id)
                    return
        else:
            # No active conversations in this channel - check for new crisis
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
            detection_result = await self._perform_hybrid_detection(message)
            crisis_level = detection_result.get('crisis_level', 'none')
            
            # Only override for medium and high crises (configurable)
            override_levels = self.config.get('CRISIS_OVERRIDE_LEVELS', 'medium,high').split(',')
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
        """Log attempts by other users to intrude on active conversations"""
        
        logger.warning(f"🚨 CONVERSATION INTRUSION BLOCKED:")
        logger.warning(f"   👤 Conversation owner: {conversation_owner_id}")
        logger.warning(f"   🚫 Blocked user: {message.author.id} ({message.author.display_name})")
        logger.warning(f"   📍 Channel: {message.channel.id} ({message.channel.name})")
        logger.warning(f"   🚨 Crisis level: {conversation_data.get('crisis_level', 'unknown')}")
        logger.warning(f"   📝 Blocked message: '{message.content[:100]}...'")
        
        # Track intrusion attempts in stats
        self.message_stats['intrusion_attempts_blocked'] += 1
        
        # Optional: Log to security manager if available
        if self.security_manager:
            self.security_manager.log_security_event(
                "conversation_intrusion_blocked",
                message.author.id,
                message.guild.id,
                message.channel.id,
                {
                    "conversation_owner_id": conversation_owner_id,
                    "intruder_user_id": message.author.id,
                    "intruder_display_name": message.author.display_name,
                    "conversation_crisis_level": conversation_data.get('crisis_level'),
                    "blocked_message_preview": message.content[:100],
                    "conversation_duration": time.time() - conversation_data.get('start_time', 0)
                },
                "warning"
            )

    def _should_respond_in_conversation(self, message: Message, original_user_id: int) -> bool:
        """Check if Ash should respond to this message during an active conversation"""
        
        # Only respond to the original user
        if message.author.id != original_user_id:
            logger.debug(f"🚫 Ignoring message from different user: {message.author.id} vs {original_user_id}")
            return False
        
        # Check for bot mention (@Ash)
        if self.bot.user in message.mentions:
            logger.debug(f"✅ Bot mentioned by user {message.author.id}")
            return True
        
        # Check for configurable trigger phrases (case-insensitive)
        trigger_phrases = self.config.get('CONVERSATION_TRIGGER_PHRASES', 'ash,hey ash,ash help,ash please').split(',')
        message_lower = message.content.lower().strip()
        
        for trigger in trigger_phrases:
            trigger = trigger.strip().lower()
            if trigger in message_lower:
                logger.debug(f"✅ Trigger phrase '{trigger}' found in message from user {message.author.id}")
                return True
        
        # Check if message starts with common conversation starters (if enabled in config)
        if self.config.get_bool('CONVERSATION_ALLOW_STARTERS', True):
            conversation_starters = [
                "i'm still", "i still", "but i", "what if", "can you", 
                "help me", "i need", "it's getting", "i feel", "this is"
            ]
            
            for starter in conversation_starters:
                if message_lower.startswith(starter):
                    logger.debug(f"✅ Conversation starter '{starter}' detected from user {message.author.id}")
                    return True
        
        logger.debug(f"🚫 No trigger found in message from user {message.author.id}: '{message.content[:30]}...'")
        return False

    def _log_conversation_attempt(self, message: Message, conversation_data: dict, reason: str):
        """Log when users try to continue conversations without proper triggers"""
        
        logger.info(f"💬 Conversation attempt from user {message.author.id}:")
        logger.info(f"   📝 Message: '{message.content[:50]}...'")
        logger.info(f"   🚫 Reason ignored: {reason}")
        logger.info(f"   🚨 Conversation level: {conversation_data.get('crisis_level', 'unknown')}")
        
        # Track this in stats
        self.message_stats['ignored_follow_ups'] += 1

    async def _handle_conversation_followup(self, message: Message):
        """Enhanced conversation follow-up with mention/ping requirement"""
        
        user_id = message.author.id
        conversation = self.active_conversations[user_id]
        
        # Only respond in same channel
        if message.channel.id != conversation['channel_id']:
            return
        
        self.message_stats['follow_ups_handled'] += 1
        
        try:
            # Check for escalation
            detection_result = await self._perform_hybrid_detection(message)
            new_level = detection_result.get('crisis_level', 'none')
            current_level = conversation['crisis_level']
            
            # Only escalate if the new level is actually HIGHER
            if self._is_escalation(current_level, new_level):
                conversation['crisis_level'] = new_level
                conversation['escalations'] = conversation.get('escalations', 0) + 1
                logger.warning(f"🚨 Crisis ESCALATED: {current_level} → {new_level} for user {user_id}")
                effective_level = new_level
                is_escalation = True
            else:
                # Continue with original crisis level for follow-ups
                effective_level = current_level
                is_escalation = False
                logger.debug(f"💬 Follow-up conversation: maintaining {current_level} level for user {user_id}")
            
            # Rate limiting for follow-ups
            if not await self.check_rate_limits(user_id):
                self.message_stats['rate_limits_hit'] += 1
                return
            
            if self.daily_call_count >= self.max_daily_calls:
                self.message_stats['daily_limits_hit'] += 1
                return
            
            # Generate response
            async with message.channel.typing():
                response = await self.claude_api.get_ash_response(
                    message.content,
                    effective_level,
                    message.author.display_name
                )
                
                # Only use crisis handler for escalations, simple reply for follow-ups
                if is_escalation:
                    # This is a real escalation - use full crisis handler
                    await self.crisis_handler.handle_crisis_response_with_instructions(message, effective_level, response)
                    logger.warning(f"🚨 Escalation handled with full crisis response")
                else:
                    # This is just a follow-up - simple reply, no alerts
                    await message.reply(response)
                    logger.info(f"💬 Follow-up response sent (no escalation)")
                
                self.daily_call_count += 1
                await self.record_api_call(user_id)
                
                # Update conversation stats
                conversation['follow_up_count'] = conversation.get('follow_up_count', 0) + 1
                
                logger.info(f"✅ Follow-up handled: {message.author} (level: {effective_level}, follow-up #{conversation['follow_up_count']}, escalation: {is_escalation})")
        
        except Exception as e:
            logger.error(f"❌ Error handling conversation follow-up: {e}")
            await message.add_reaction('❌')

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

    # [Include all your existing methods: _should_process_message, _handle_potential_crisis, 
    # _perform_hybrid_detection, _combine_detection_results, check_rate_limits, record_api_call,
    # cleanup_expired_conversations, _is_escalation, etc.]
    
    def _should_process_message(self, message: Message) -> bool:
        """Enhanced message filtering with detailed logging"""
        
        if message.author.bot:
            logger.debug(f"🤖 Ignored bot message from {message.author}")
            return False
        
        if not message.guild or message.guild.id != self.guild_id:
            logger.debug(f"🚫 Ignored message from wrong guild: {message.guild.id if message.guild else 'DM'}")
            return False
        
        if not self.config.is_channel_allowed(message.channel.id):
            logger.debug(f"🚫 Ignored message from restricted channel: {message.channel.id}")
            return False
        
        logger.debug(f"📨 Processing message from {message.author} in {message.channel}: {message.content[:50]}...")
        return True

    async def _handle_potential_crisis(self, message: Message):
        """Enhanced crisis detection with hybrid approach and comprehensive logging"""
        
        try:
            if not await self.check_rate_limits(message.author.id):
                self.message_stats['rate_limits_hit'] += 1
                logger.debug(f"🚫 Rate limit hit for user {message.author.id}")
                return
            
            if self.daily_call_count >= self.max_daily_calls:
                self.message_stats['daily_limits_hit'] += 1
                logger.warning("🚫 Daily API call limit reached")
                return
            
            detection_result = await self._perform_hybrid_detection(message)
            
            if detection_result['needs_response']:
                await self._handle_crisis_response(message, detection_result)
        
        except Exception as e:
            logger.error(f"❌ Error handling potential crisis: {e}")
            await message.add_reaction('❌')

    async def _handle_crisis_response(self, message: Message, detection_result: dict):
        """Enhanced crisis response with conversation setup"""
        
        try:
            async with message.channel.typing():
                crisis_level = detection_result['crisis_level']
                
                # Log crisis detection as security event
                self._log_security_event(
                    f"crisis_detected_{crisis_level}",
                    message.author.id,
                    message.guild.id,
                    message.channel.id,
                    {
                        "crisis_level": crisis_level,
                        "method": detection_result.get('method', 'unknown'),
                        "confidence": detection_result.get('confidence', 0),
                        "message_preview": message.content[:50] + "..." if len(message.content) > 50 else message.content
                    },
                    "warning" if crisis_level == "high" else "info"
                )
                
                # Get response using Claude API
                response = await self.claude_api.get_ash_response(
                    message.content,
                    crisis_level,
                    message.author.display_name
                )
                
                # Use enhanced crisis handler with conversation instructions
                await self.crisis_handler.handle_crisis_response_with_instructions(message, crisis_level, response)
                
                # Start conversation tracking
                self.start_conversation_tracking(message.author.id, crisis_level, message.channel.id)
                
                # Update counters
                self.daily_call_count += 1
                await self.record_api_call(message.author.id)
                self.message_stats['crisis_responses_given'] += 1
                
                logger.info(f"✅ Crisis response with conversation setup completed:")
                logger.info(f"   👤 User: {message.author} ({message.author.id})")
                logger.info(f"   🚨 Level: {crisis_level}")
                logger.info(f"   🔍 Method: {detection_result.get('method', 'unknown')}")
                logger.info(f"   📊 Confidence: {detection_result.get('confidence', 0):.2f}")
                logger.info(f"   💬 Mention requirement: ✅ Enabled")
                
        except Exception as e:
            logger.error(f"❌ Error handling crisis response: {e}")
            
            self._log_security_event(
                "crisis_response_error",
                message.author.id,
                message.guild.id,
                message.channel.id,
                {"error": str(e), "crisis_level": detection_result.get('crisis_level', 'unknown')},
                "error"
            )
            
            await message.add_reaction('❌')

    def _log_security_event(self, event_type: str, user_id: int, guild_id: int, channel_id: int, details: dict = None, severity: str = "info"):
        """Helper method to safely log security events"""
        if self.security_manager:
            self.security_manager.log_security_event(event_type, user_id, guild_id, channel_id, details, severity)
        else:
            logger.info(f"Security Event (no manager): {event_type} - User: {user_id} - Details: {details}")

    # Include all other existing methods from your current message_handler.py
    # (check_rate_limits, record_api_call, cleanup_expired_conversations, 
    # _perform_hybrid_detection, _combine_detection_results, _is_escalation, etc.)
    
    def _is_escalation(self, current_level: str, new_level: str) -> bool:
        """Check if crisis level has escalated"""
        hierarchy = {'none': 0, 'low': 1, 'medium': 2, 'high': 3}
        return hierarchy.get(new_level, 0) > hierarchy.get(current_level, 0)

    async def check_rate_limits(self, user_id: int) -> bool:
        """Enhanced rate limiting with better tracking"""
        current_time = asyncio.get_event_loop().time()
        
        if user_id not in self.user_cooldowns:
            self.user_cooldowns[user_id] = []
        
        # Remove old timestamps
        self.user_cooldowns[user_id] = [
            timestamp for timestamp in self.user_cooldowns[user_id]
            if current_time - timestamp < 3600
        ]
        
        if len(self.user_cooldowns[user_id]) >= self.rate_limit_per_user:
            logger.debug(f"🚫 Rate limit exceeded for user {user_id}: {len(self.user_cooldowns[user_id])}/{self.rate_limit_per_user}")
            return False
        
        return True

    async def record_api_call(self, user_id: int):
        """Enhanced API call recording"""
        current_time = asyncio.get_event_loop().time()
        if user_id not in self.user_cooldowns:
            self.user_cooldowns[user_id] = []
        self.user_cooldowns[user_id].append(current_time)
        
        logger.debug(f"📊 API call recorded: user {user_id} ({len(self.user_cooldowns[user_id])}/{self.rate_limit_per_user}) daily: {self.daily_call_count}/{self.max_daily_calls}")

    def cleanup_expired_conversations(self):
        """Enhanced conversation cleanup with detailed logging"""
        current_time = time.time()
        expired_users = []
        
        for user_id, conv_data in self.active_conversations.items():
            if current_time - conv_data['start_time'] > self.conversation_timeout:
                expired_users.append(user_id)
        
        for user_id in expired_users:
            conv = self.active_conversations[user_id]
            duration = current_time - conv['start_time']
            
            logger.info(f"💬 Conversation expired for user {user_id}:")
            logger.info(f"   ⏱️ Duration: {duration:.1f}s")
            logger.info(f"   💬 Follow-ups: {conv.get('follow_up_count', 0)}")
            logger.info(f"   🚨 Escalations: {conv.get('escalations', 0)}")
            logger.info(f"   📈 Level progression: {conv.get('initial_crisis_level', 'unknown')} → {conv['crisis_level']}")
            
            del self.active_conversations[user_id]

    # Add the rest of your existing methods here...
    async def _perform_hybrid_detection(self, message: Message) -> Dict:
        """Enhanced hybrid detection with your existing logic"""
        
        # Method 1: Keyword detection (always runs)
        keyword_result = self.keyword_detector.check_message(message.content)
        logger.info(f"🔤 Keyword detection result: {keyword_result['crisis_level']} (needs_response: {keyword_result['needs_response']})")
        
        # Method 2: NLP analysis (if available)
        nlp_result = None
        try:
            nlp_result = await self.nlp_client.analyze_message(
                message.content,
                str(message.author.id),
                str(message.channel.id)
            )
            if nlp_result:
                logger.info(f"🧠 NLP analysis result: {nlp_result.get('crisis_level', 'none')} (confidence: {nlp_result.get('confidence_score', 0):.2f})")
            else:
                logger.info("🧠 NLP analysis returned None")
        except Exception as e:
            logger.warning(f"🧠 NLP analysis failed: {e}")
        
        # Hybrid decision logic
        final_result = self._combine_detection_results(keyword_result, nlp_result)
        
        # Log the final decision
        logger.info(f"⚡ Final hybrid decision: {final_result.get('crisis_level', 'unknown')} via {final_result.get('method', 'unknown')} (confidence: {final_result.get('confidence', 0):.2f})")
        
        # Update statistics
        method = final_result.get('method', 'unknown')
        if method in self.message_stats['detection_method_breakdown']:
            self.message_stats['detection_method_breakdown'][method] += 1
        
        return final_result

    def _combine_detection_results(self, keyword_result: Dict, nlp_result: Optional[Dict]) -> Dict:
        """Hybrid decision logic with enhanced statistics"""
        
        # If NLP unavailable, use keywords only
        if not nlp_result:
            self.message_stats['detection_method_breakdown']['keyword_only'] += 1
            return {
                'needs_response': keyword_result['needs_response'],
                'crisis_level': keyword_result['crisis_level'],
                'method': 'keyword_only',
                'confidence': 0.9 if keyword_result['needs_response'] else 0.0,
                'detected_categories': keyword_result['detected_categories']
            }

        # Both methods available - hybrid logic
        keyword_level = keyword_result['crisis_level']
        nlp_level = nlp_result.get('crisis_level', 'none')
        
        # Crisis level hierarchy
        hierarchy = {'none': 0, 'low': 1, 'medium': 2, 'high': 3}
        
        # Use the higher of the two crisis levels (safety-first)
        if hierarchy[keyword_level] >= hierarchy[nlp_level]:
            final_level = keyword_level
            method = 'keyword_primary'
            confidence = 0.9 if keyword_result['needs_response'] else 0.0
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
            'detected_categories': keyword_result['detected_categories'] + nlp_result.get('detected_categories', []),
            'keyword_result': keyword_level,
            'nlp_result': nlp_level
        }