"""
Enhanced Message Handler with Three-Model Ensemble Support
Includes gap detection, staff review flagging, and learning integration
"""

import logging
import asyncio
import time
from discord import Message
from typing import Dict, Optional
from handlers.crisis_handler import CrisisHandler
from integrations.claude_api import ClaudeAPI

logger = logging.getLogger(__name__)

class EnhancedMessageHandler:
    """Enhanced message processing with three-model ensemble and gap detection"""
    
    def __init__(self, bot, claude_api, nlp_client, keyword_detector, crisis_handler, config, security_manager=None):
        """Enhanced initialization with three-model ensemble support"""
        
        self.bot = bot
        self.claude_api = claude_api
        self.nlp_client = nlp_client  # Should be EnhancedNLPClient
        self.keyword_detector = keyword_detector
        self.crisis_handler = crisis_handler
        self.config = config
        self.security_manager = security_manager
        
        # Conversation tracking (enhanced)
        self.active_conversations = {}
        self.conversation_timeout = config.get_int('BOT_CONVERSATION_TIMEOUT', 300)
        
        # Rate limiting (enhanced)
        self.user_cooldowns = {}
        self.daily_call_count = 0
        self.max_daily_calls = config.get_int('BOT_MAX_DAILY_CALLS', 1000)
        self.rate_limit_per_user = config.get_int('BOT_RATE_LIMIT_PER_USER', 10)
        
        # Enhanced statistics for three-model ensemble
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
            
            # Three-model ensemble specific stats
            'ensemble_analyses_performed': 0,
            'gaps_detected': 0,
            'staff_reviews_flagged': 0,
            'unanimous_consensus_count': 0,
            'model_disagreement_count': 0,
            
            'detection_method_breakdown': {
                'keyword_only': 0,
                'ensemble_primary': 0,
                'ensemble_unanimous_consensus': 0,
                'ensemble_best_of_disagreeing': 0,
                'ensemble_majority_vote': 0,
                'ensemble_weighted': 0,
                'hybrid_detection': 0
            }
        }
        
        self.guild_id = config.get_int('BOT_GUILD_ID')
        
        # Gap detection settings
        self.enable_gap_notifications = config.get_bool('BOT_ENABLE_GAP_NOTIFICATIONS', True)
        self.gap_notification_channel = config.get_int('BOT_GAP_NOTIFICATION_CHANNEL_ID', None)
        
        logger.info("📨 Enhanced message handler with three-model ensemble initialized")
        logger.info(f"🔍 Gap detection: {'enabled' if self.enable_gap_notifications else 'disabled'}")
    
    async def process_message(self, message: Message):
        """Enhanced message processing with three-model ensemble"""
        
        # Standard filtering
        if not self._should_process_message(message):
            return
        
        # Rate limiting
        if not await self.check_rate_limits(message.author.id):
            self.message_stats['rate_limits_hit'] += 1
            return
        
        # Daily limit check
        if self.daily_call_count >= self.max_daily_calls:
            self.message_stats['daily_limits_hit'] += 1
            logger.warning(f"⚠️ Daily API call limit reached: {self.daily_call_count}/{self.max_daily_calls}")
            return
        
        # Security check
        if self.security_manager:
            if not await self.security_manager.validate_message_security(message):
                self.message_stats['intrusion_attempts_blocked'] += 1
                return
        
        self.message_stats['total_messages_processed'] += 1
        
        try:
            # Perform enhanced hybrid detection with three-model ensemble
            detection_result = await self._perform_enhanced_hybrid_detection(message)
            
            # Handle gap detection and staff notifications
            if detection_result.get('gap_detected'):
                await self._handle_gap_detection(message, detection_result)
            
            # Crisis response handling
            if detection_result.get('needs_response'):
                await self._handle_crisis_response(message, detection_result)
            
            # Conversation handling
            await self._handle_conversation_logic(message, detection_result)
            
        except Exception as e:
            logger.error(f"❌ Error processing message from {message.author}: {e}")
            logger.exception("Full traceback:")
    
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

    async def check_rate_limits(self, user_id: int) -> bool:
        """Check if user is within rate limits"""
        current_time = time.time()
        
        # Clean old entries
        if user_id in self.user_cooldowns:
            self.user_cooldowns[user_id] = [
                timestamp for timestamp in self.user_cooldowns[user_id]
                if current_time - timestamp < 3600  # 1 hour
            ]
        else:
            self.user_cooldowns[user_id] = []
        
        # Check rate limit
        if len(self.user_cooldowns[user_id]) >= self.rate_limit_per_user:
            return False
        
        # Add current timestamp
        self.user_cooldowns[user_id].append(current_time)
        return True

    async def record_api_call(self, user_id: int):
        """Record an API call for rate limiting"""
        self.daily_call_count += 1
        current_time = time.time()
        
        if user_id not in self.user_cooldowns:
            self.user_cooldowns[user_id] = []
        
        self.user_cooldowns[user_id].append(current_time)

    async def _handle_conversation_logic(self, message: Message, detection_result: Dict):
        """Handle conversation setup and management"""
        # For now, just log that conversation logic would happen here
        # You can implement your full conversation logic later
        if detection_result.get('needs_response'):
            logger.info(f"💬 Would start conversation for {message.author.display_name}")
            # Add your conversation management logic here if needed

    def cleanup_expired_conversations(self):
        """Clean up expired conversations"""
        current_time = time.time()
        expired_users = []
        
        for user_id, conv_data in self.active_conversations.items():
            if current_time - conv_data.get('start_time', current_time) > self.conversation_timeout:
                expired_users.append(user_id)
        
        for user_id in expired_users:
            del self.active_conversations[user_id]
            
        if expired_users:
            logger.info(f"💬 Cleaned up {len(expired_users)} expired conversations")

    async def validate_message_security(self, message: Message) -> bool:
        """Basic message security validation"""
        # Basic security checks
        if len(message.content) > 2000:  # Discord's limit
            return False
        
        # Add more security checks as needed
        return True

    async def _perform_enhanced_hybrid_detection(self, message: Message) -> Dict:
        """Enhanced hybrid detection using three-model ensemble with gap detection"""
        
        # Method 1: Keyword detection (always runs - instant)
        keyword_result = self.keyword_detector.check_message(message.content)
        logger.info(f"🔑 Keyword detection: {keyword_result.get('crisis_level', 'none')} "
                   f"(confidence: {keyword_result.get('confidence', 0):.2f})")
        
        # Method 2: Three-model ensemble analysis (if available)
        nlp_result = None
        try:
            nlp_result = await self.nlp_client.analyze_message(
                message.content,
                str(message.author.id),
                str(message.channel.id)
            )
            
            if nlp_result:
                self.message_stats['ensemble_analyses_performed'] += 1
                
                # Track ensemble method used
                method = nlp_result.get('method', 'unknown')
                if method.startswith('ensemble_'):
                    method_key = method.replace('ensemble_', '').replace('ensemble', 'ensemble_primary')
                    if method_key in self.message_stats['detection_method_breakdown']:
                        self.message_stats['detection_method_breakdown'][method_key] += 1
                
                # Track gap detection
                if nlp_result.get('gap_detected'):
                    self.message_stats['gaps_detected'] += 1
                if nlp_result.get('requires_staff_review'):
                    self.message_stats['staff_reviews_flagged'] += 1
                
                # Track consensus types
                consensus_method = nlp_result.get('method', '')
                if 'unanimous_consensus' in consensus_method:
                    self.message_stats['unanimous_consensus_count'] += 1
                elif 'best_of_disagreeing' in consensus_method:
                    self.message_stats['model_disagreement_count'] += 1
                
                logger.info(f"🎯 Ensemble analysis: {nlp_result.get('crisis_level', 'none')} "
                          f"(confidence: {nlp_result.get('confidence_score', 0):.2f}, "
                          f"method: {nlp_result.get('method', 'unknown')})")
                
                if nlp_result.get('gap_detected'):
                    logger.info(f"🔍 Gap detected: {len(nlp_result.get('gap_details', []))} model disagreements")
                
            else:
                logger.info("🎯 Ensemble analysis returned None")
                
        except Exception as e:
            logger.warning(f"🎯 Ensemble analysis failed: {e}")
        
        # Enhanced hybrid decision logic
        final_result = self._combine_enhanced_detection_results(keyword_result, nlp_result)
        
        # Log the final decision with more detail
        logger.info(f"⚡ Final enhanced decision: {final_result.get('crisis_level', 'unknown')} "
                   f"via {final_result.get('method', 'unknown')} "
                   f"(confidence: {final_result.get('confidence', 0):.2f})")
        
        if final_result.get('gap_detected'):
            logger.info(f"🚨 Staff review required due to model disagreement")
        
        return final_result
    
    def _combine_enhanced_detection_results(self, keyword_result: Dict, nlp_result: Optional[Dict]) -> Dict:
        """Enhanced hybrid decision logic with three-model ensemble support"""
        
        # If NLP unavailable, use keywords only
        if not nlp_result:
            self.message_stats['detection_method_breakdown']['keyword_only'] += 1
            return {
                'needs_response': keyword_result.get('needs_response', False),
                'crisis_level': keyword_result.get('crisis_level', 'none'),
                'confidence': keyword_result.get('confidence', 0.0),
                'method': 'keyword_only',
                'processing_time_ms': 0,
                'keyword_result': keyword_result.get('crisis_level'),
                'nlp_result': None,
                'gap_detected': False,
                'requires_staff_review': False
            }
        
        # Extract key information
        keyword_level = keyword_result.get('crisis_level', 'none')
        nlp_level = nlp_result.get('crisis_level', 'none')
        keyword_confidence = keyword_result.get('confidence', 0.0)
        nlp_confidence = nlp_result.get('confidence_score', 0.0)
        
        # Priority levels for decision making
        priority_levels = {'none': 0, 'low': 1, 'medium': 2, 'high': 3}
        keyword_priority = priority_levels.get(keyword_level, 0)
        nlp_priority = priority_levels.get(nlp_level, 0)
        
        # Enhanced decision logic:
        # 1. If ensemble detected gaps, use ensemble but flag for review
        # 2. If both detect crisis, use higher priority
        # 3. If only one detects crisis, use that one
        # 4. If neither detects crisis, use the more confident one
        
        result = {
            'keyword_result': keyword_level,
            'nlp_result': nlp_level,
            'gap_detected': nlp_result.get('gap_detected', False),
            'requires_staff_review': nlp_result.get('requires_staff_review', False),
            'ensemble_details': nlp_result.get('ensemble_details', {}),
            'model_breakdown': nlp_result.get('model_breakdown', {}),
            'processing_time_ms': nlp_result.get('processing_time_ms', 0)
        }
        
        # Decision logic
        if nlp_result.get('gap_detected'):
            # Gap detected - use ensemble result but flag for staff review
            result.update({
                'needs_response': nlp_result.get('needs_response', False),
                'crisis_level': nlp_level,
                'confidence': nlp_confidence,
                'method': f"ensemble_with_gaps_{nlp_result.get('method', 'unknown')}"
            })
            self.message_stats['detection_method_breakdown']['hybrid_detection'] += 1
            
        elif max(keyword_priority, nlp_priority) >= 2:  # medium or high
            # High priority crisis detected by either system
            if nlp_priority >= keyword_priority:
                # Ensemble detected higher or equal priority
                result.update({
                    'needs_response': True,
                    'crisis_level': nlp_level,
                    'confidence': nlp_confidence,
                    'method': f"ensemble_primary_{nlp_result.get('method', 'unknown')}"
                })
                self.message_stats['detection_method_breakdown']['ensemble_primary'] += 1
            else:
                # Keywords detected higher priority
                result.update({
                    'needs_response': True,
                    'crisis_level': keyword_level,
                    'confidence': keyword_confidence,
                    'method': 'keyword_override'
                })
                self.message_stats['detection_method_breakdown']['keyword_only'] += 1
                
        elif max(keyword_priority, nlp_priority) > 0:
            # Low priority crisis detected
            if nlp_confidence > keyword_confidence:
                result.update({
                    'needs_response': nlp_result.get('needs_response', False),
                    'crisis_level': nlp_level,
                    'confidence': nlp_confidence,
                    'method': f"ensemble_low_confidence_{nlp_result.get('method', 'unknown')}"
                })
            else:
                result.update({
                    'needs_response': keyword_result.get('needs_response', False),
                    'crisis_level': keyword_level,
                    'confidence': keyword_confidence,
                    'method': 'keyword_low_confidence'
                })
            self.message_stats['detection_method_breakdown']['hybrid_detection'] += 1
            
        else:
            # No crisis detected by either system
            result.update({
                'needs_response': False,
                'crisis_level': 'none',
                'confidence': max(keyword_confidence, nlp_confidence),
                'method': 'no_crisis_detected'
            })
        
        return result
    
    async def _handle_gap_detection(self, message: Message, detection_result: Dict):
        """Handle gap detection - notify staff about model disagreements"""
        
        if not self.enable_gap_notifications:
            return
        
        gap_details = detection_result.get('gap_details', [])
        model_breakdown = detection_result.get('model_breakdown', {})
        
        # Log detailed gap information
        logger.info(f"🔍 Gap Detection Details:")
        logger.info(f"   Message: '{message.content[:100]}...'")
        logger.info(f"   User: {message.author.display_name}")
        logger.info(f"   Channel: #{message.channel.name}")
        
        for i, gap in enumerate(gap_details):
            gap_type = gap.get('type', 'unknown')
            logger.info(f"   Gap {i+1}: {gap_type}")
            
            if gap_type == 'meaningful_disagreement':
                crisis_models = gap.get('crisis_models', [])
                safe_models = gap.get('safe_models', [])
                logger.info(f"     Crisis models: {crisis_models}")
                logger.info(f"     Safe models: {safe_models}")
        
        # Log individual model results
        for model_name, model_data in model_breakdown.items():
            prediction = model_data.get('prediction', 'unknown')
            confidence = model_data.get('confidence', 0)
            logger.info(f"   {model_name}: {prediction} ({confidence:.2f})")
        
        # Send notification to gap notification channel if configured
        if self.gap_notification_channel:
            try:
                channel = self.bot.get_channel(self.gap_notification_channel)
                if channel:
                    embed = self._create_gap_notification_embed(message, detection_result)
                    await channel.send(embed=embed)
            except Exception as e:
                logger.error(f"❌ Failed to send gap notification: {e}")
    
    def _create_gap_notification_embed(self, message: Message, detection_result: Dict):
        """Create Discord embed for gap notifications"""
        import discord
        
        embed = discord.Embed(
            title="🔍 Model Disagreement Detected",
            description="The three-model ensemble detected disagreement and flagged this message for staff review.",
            color=discord.Color.orange()
        )
        
        # Message info
        embed.add_field(
            name="📝 Message",
            value=f"```{message.content[:500]}{'...' if len(message.content) > 500 else ''}```",
            inline=False
        )
        
        embed.add_field(
            name="👤 User",
            value=f"{message.author.mention} ({message.author.display_name})",
            inline=True
        )
        
        embed.add_field(
            name="📍 Channel",
            value=f"#{message.channel.name}",
            inline=True
        )
        
        # Final decision
        embed.add_field(
            name="⚡ Final Decision",
            value=f"**Level:** {detection_result.get('crisis_level', 'unknown')}\n"
                  f"**Confidence:** {detection_result.get('confidence', 0):.2%}\n"
                  f"**Method:** {detection_result.get('method', 'unknown')}",
            inline=False
        )
        
        # Model breakdown
        model_breakdown = detection_result.get('model_breakdown', {})
        if model_breakdown:
            breakdown_text = ""
            for model_name, model_data in model_breakdown.items():
                prediction = model_data.get('prediction', 'unknown')
                confidence = model_data.get('confidence', 0)
                breakdown_text += f"**{model_name.title()}:** {prediction} ({confidence:.2%})\n"
            
            embed.add_field(
                name="🎯 Model Breakdown",
                value=breakdown_text,
                inline=False
            )
        
        # Gap details
        gap_details = detection_result.get('gap_details', [])
        if gap_details:
            gap_text = ""
            for i, gap in enumerate(gap_details):
                gap_type = gap.get('type', 'unknown')
                gap_text += f"{i+1}. {gap_type.replace('_', ' ').title()}\n"
            
            embed.add_field(
                name="🚨 Gap Details",
                value=gap_text,
                inline=False
            )
        
        embed.add_field(
            name="🎓 Learning Opportunity",
            value="Use `/fp_correction` or `/fn_correction` commands to provide feedback and improve detection.",
            inline=False
        )
        
        embed.set_footer(text="Three-Model Ensemble • Gap Detection System")
        embed.timestamp = message.created_at
        
        return embed
    
    async def _handle_crisis_response(self, message: Message, detection_result: Dict):
        """Enhanced crisis response handling with ensemble details"""
        
        try:
            self.message_stats['crisis_responses_given'] += 1
            
            # Enhanced crisis response that includes ensemble information
            await self.crisis_handler.handle_crisis(message, detection_result)
            
            logger.info(f"🚨 Crisis response sent for {message.author.display_name}: "
                       f"{detection_result.get('crisis_level', 'unknown')} "
                       f"(method: {detection_result.get('method', 'unknown')})")
            
        except Exception as e:
            logger.error(f"❌ Failed to handle crisis response: {e}")
    
    # ... (rest of the existing methods like _should_process_message, check_rate_limits, etc.)
    # These remain largely the same as your current implementation
    
    def get_enhanced_stats(self) -> Dict:
        """Get comprehensive statistics including ensemble performance"""
        base_stats = self.message_stats.copy()
        
        # Add ensemble-specific metrics
        if base_stats['ensemble_analyses_performed'] > 0:
            base_stats['gap_detection_rate'] = base_stats['gaps_detected'] / base_stats['ensemble_analyses_performed']
            base_stats['staff_review_rate'] = base_stats['staff_reviews_flagged'] / base_stats['ensemble_analyses_performed']
            base_stats['unanimous_consensus_rate'] = base_stats['unanimous_consensus_count'] / base_stats['ensemble_analyses_performed']
        else:
            base_stats.update({
                'gap_detection_rate': 0.0,
                'staff_review_rate': 0.0,
                'unanimous_consensus_rate': 0.0
            })
        
        return base_stats

# For backwards compatibility
MessageHandler = EnhancedMessageHandler