#!/usr/bin/env python3
"""
Message Handler - Enhanced for v3.0 NLP Integration

Updated to handle the new three-model ensemble response structure while
maintaining backward compatibility with existing logic.

Repository: https://github.com/The-Alphabet-Cartel/ash-bot
Location: ash/ash-bot/bot/handlers/message_handler.py
"""

import logging
import time
from typing import Dict, Optional
from discord import Message

logger = logging.getLogger(__name__)

class MessageHandler:
    """Enhanced message handler for v3.0 NLP integration"""
    
    def __init__(self, bot, claude_api=None, nlp_client=None, keyword_detector=None, crisis_handler=None, config=None, security_manager=None):
        """
        Enhanced initialization with flexible parameter support for backward compatibility
        
        Args:
            bot: Discord bot instance
            claude_api: Claude API integration (optional)
            nlp_client: NLP client instance (required)
            keyword_detector: Keyword detector instance (required)
            crisis_handler: Crisis handler instance (optional)
            config: Configuration manager (required)
            security_manager: Security manager (optional)
        """
        
        self.bot = bot
        self.claude_api = claude_api
        self.nlp_client = nlp_client
        self.keyword_detector = keyword_detector
        self.crisis_handler = crisis_handler
        self.config = config
        self.security_manager = security_manager
        
        # Handle missing required components gracefully
        if not self.nlp_client:
            logger.warning("⚠️ NLP client not provided - NLP analysis will be skipped")
        
        if not self.keyword_detector:
            logger.warning("⚠️ Keyword detector not provided - keyword detection will be skipped")
        
        if not self.config:
            logger.warning("⚠️ Config not provided - using defaults")
            self.conversation_timeout = 300
        else:
            # Handle both config.get() and config.get_int() methods
            if hasattr(config, 'get_int'):
                self.conversation_timeout = config.get_int('BOT_CONVERSATION_TIMEOUT', 300)
            else:
                self.conversation_timeout = config.get('BOT_CONVERSATION_TIMEOUT', 300)
        
        # Enhanced statistics tracking with backward compatibility
        self.message_stats = {
            'messages_processed': 0,
            'crisis_detected': 0,
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
            },
            # Backward compatibility fields for existing commands
            'conversations_started': 0,
            'follow_ups_handled': 0, 
            'crisis_responses_given': 0,
            'total_messages_processed': 0,
            'rate_limits_hit': 0,
            'daily_limits_hit': 0,
            'ignored_follow_ups': 0,
            'intrusion_attempts_blocked': 0,
            'crisis_overrides_triggered': 0,
            'multiple_conversations_same_channel': 0
        }
        
        # Conversation tracking (existing logic)
        self.active_conversations = {}
        
        # Log initialization status
        logger.info("📨 Enhanced Message Handler initialized for v3.0")
        logger.info(f"   🧠 NLP Client: {'✅ Available' if self.nlp_client else '❌ Missing'}")
        logger.info(f"   🔤 Keyword Detector: {'✅ Available' if self.keyword_detector else '❌ Missing'}")
        logger.info(f"   🚨 Crisis Handler: {'✅ Available' if self.crisis_handler else '❌ Missing'}")
        logger.info(f"   🔐 Security Manager: {'✅ Available' if self.security_manager else '❌ Missing'}")
        logger.info(f"   💬 Conversation timeout: {self.conversation_timeout}s")
    
    async def _perform_hybrid_detection(self, message: Message) -> Dict:
        """
        Enhanced hybrid detection with v3.0 NLP support
        Maintains existing safety-first logic while leveraging new features
        """
        
        # Method 1: Keyword detection (always runs first, if available)
        keyword_result = {'needs_response': False, 'crisis_level': 'none', 'detected_categories': []}
        
        if self.keyword_detector:
            keyword_result = self.keyword_detector.check_message(message.content)
            logger.info(f"🔤 Keyword detection: {keyword_result['crisis_level']} (needs_response: {keyword_result['needs_response']})")
        else:
            logger.warning("🔤 Keyword detector not available - skipping keyword analysis")
        
        # Method 2: NLP analysis with v3.0 ensemble (if available)
        nlp_result = None
        if self.nlp_client:
            try:
                nlp_result = await self.nlp_client.analyze_message(
                    message.content,
                    str(message.author.id),
                    str(message.channel.id)
                )
                if nlp_result:
                    logger.info(f"🧠 NLP v3.0 analysis: {nlp_result.get('crisis_level', 'none')} "
                               f"(confidence: {nlp_result.get('confidence_score', 0):.3f}) "
                               f"via {nlp_result.get('method', 'unknown')}")
                    
                    # Log v3.0 specific features
                    if nlp_result.get('gaps_detected'):
                        logger.warning(f"⚠️ Model disagreement detected - message: {message.id}")
                        self.message_stats['v3_features']['gaps_detected_count'] += 1
                        self._log_gap_details(message, nlp_result)
                    
                    if nlp_result.get('requires_staff_review'):
                        logger.info(f"👥 Staff review flagged by ensemble - message: {message.id}")
                        self.message_stats['v3_features']['staff_reviews_triggered'] += 1
                    
                    self.message_stats['v3_features']['ensemble_analyses'] += 1
                else:
                    logger.info("🧠 NLP analysis returned None")
            except Exception as e:
                logger.warning(f"🧠 NLP analysis failed: {e}")
        else:
            logger.warning("🧠 NLP client not available - skipping NLP analysis")
        
        # Combine results using existing hybrid logic with v3.0 enhancements
        final_result = self._combine_detection_results_v3(keyword_result, nlp_result)
        
        # Log the final decision with enhanced details
        logger.info(f"⚡ Final decision: {final_result.get('crisis_level', 'unknown')} "
                   f"via {final_result.get('method', 'unknown')} "
                   f"(confidence: {final_result.get('confidence', 0):.3f})")
        
        # Update statistics
        method = final_result.get('method', 'unknown')
        if method in self.message_stats['detection_method_breakdown']:
            self.message_stats['detection_method_breakdown'][method] += 1
        
        return final_result
    
    def _combine_detection_results_v3(self, keyword_result: Dict, nlp_result: Optional[Dict]) -> Dict:
        """
        Enhanced hybrid decision logic with v3.0 NLP features
        Maintains existing safety-first approach while leveraging ensemble insights
        """
        
        # If NLP unavailable, use keywords only (existing fallback)
        if not nlp_result:
            self.message_stats['detection_method_breakdown']['keyword_only'] += 1
            return {
                'needs_response': keyword_result['needs_response'],
                'crisis_level': keyword_result['crisis_level'],
                'method': 'keyword_only',
                'confidence': 0.9 if keyword_result['needs_response'] else 0.0,
                'detected_categories': keyword_result['detected_categories'],
                'requires_staff_review': keyword_result['crisis_level'] == 'high',  # v3.0 field
                'gaps_detected': False,  # v3.0 field
                'processing_time_ms': 0
            }

        # Both methods available - enhanced hybrid logic
        keyword_level = keyword_result['crisis_level']
        nlp_level = nlp_result.get('crisis_level', 'none')
        
        # Crisis level hierarchy (existing safety-first logic)
        hierarchy = {'none': 0, 'low': 1, 'medium': 2, 'high': 3}
        
        # Use the higher of the two crisis levels (safety-first approach)
        if hierarchy[keyword_level] >= hierarchy[nlp_level]:
            final_level = keyword_level
            method = 'keyword_primary'
            confidence = 0.9 if keyword_result['needs_response'] else 0.0
            staff_review = keyword_level == 'high'
        else:
            final_level = nlp_level
            method = 'nlp_primary'
            confidence = nlp_result.get('confidence_score', 0.5)
            # v3.0 enhancement: use ensemble's staff review recommendation
            staff_review = nlp_result.get('requires_staff_review', final_level == 'high')
        
        self.message_stats['detection_method_breakdown']['hybrid_detection'] += 1
        
        # Build enhanced result with v3.0 features
        result = {
            'needs_response': final_level != 'none',
            'crisis_level': final_level,
            'method': method,
            'confidence': confidence,
            'detected_categories': keyword_result['detected_categories'] + nlp_result.get('detected_categories', []),
            'keyword_result': keyword_level,
            'nlp_result': nlp_level
        }
        
        # Add v3.0 specific fields
        result.update({
            'requires_staff_review': staff_review,
            'gaps_detected': nlp_result.get('gaps_detected', False),
            'processing_time_ms': nlp_result.get('processing_time_ms', 0),
            'model_info': nlp_result.get('model_info', 'unknown'),
            'ensemble_details': nlp_result.get('ensemble_details', {}),
            'reasoning': nlp_result.get('reasoning', '')
        })
        
        # Special handling for gap situations
        if result['gaps_detected']:
            # When models disagree, be more conservative about staff review
            result['requires_staff_review'] = True
            logger.info(f"🔍 Gap detected - forcing staff review for safety")
        
        return result
    
    def _log_gap_details(self, message: Message, nlp_result: Dict):
        """Log detailed information about model disagreements"""
        
        ensemble_details = nlp_result.get('ensemble_details', {})
        predictions = ensemble_details.get('model_predictions', {})
        confidences = ensemble_details.get('individual_confidence_scores', {})
        gap_details = ensemble_details.get('gap_details', [])
        
        logger.info(f"🔍 Model Gap Analysis - Message ID: {message.id}")
        logger.info(f"   👤 User: {message.author.display_name} ({message.author.id})")
        logger.info(f"   💬 Content: {message.content[:100]}{'...' if len(message.content) > 100 else ''}")
        
        if predictions:
            logger.info(f"   📊 Model Predictions:")
            for model, prediction in predictions.items():
                confidence = confidences.get(model, 0.0)
                logger.info(f"      {model}: {prediction} (confidence: {confidence:.3f})")
        
        if gap_details:
            for gap in gap_details:
                gap_type = gap.get('type', 'unknown')
                gap_reason = gap.get('reason', 'no reason provided')
                logger.info(f"   ⚠️ Gap: {gap_type} - {gap_reason}")
    
    async def process_message(self, message: Message) -> Optional[Dict]:
        """
        Main message processing with enhanced v3.0 integration
        Maintains existing conversation flow while adding ensemble insights
        """
        
        self.message_stats['messages_processed'] += 1
        self.message_stats['total_messages_processed'] += 1  # Backward compatibility
        
        # Clean up expired conversations (existing logic)
        await self._cleanup_expired_conversations()
        
        # Perform hybrid crisis detection with v3.0 enhancements
        detection_result = await self._perform_hybrid_detection(message)
        
        # If crisis detected, update statistics and return result
        if detection_result['needs_response']:
            self.message_stats['crisis_detected'] += 1
            self.message_stats['crisis_responses_given'] += 1  # Backward compatibility
            
            # Enhanced logging for v3.0
            crisis_level = detection_result['crisis_level']
            method = detection_result['method']
            confidence = detection_result['confidence']
            
            logger.info(f"🚨 Crisis detected: {crisis_level} via {method} "
                       f"(confidence: {confidence:.1%})")
            
            # Log v3.0 specific insights
            if detection_result.get('gaps_detected'):
                logger.info(f"   ⚠️ Models disagreed - manual review recommended")
            
            if detection_result.get('requires_staff_review'):
                logger.info(f"   👥 Staff review required")
            
            processing_time = detection_result.get('processing_time_ms', 0)
            if processing_time > 0:
                logger.info(f"   ⏱️ Processing time: {processing_time:.1f}ms")
            
            return detection_result
        
        return None
    
    def get_message_handler_stats(self) -> Dict:
        """Get message handler statistics in expected format for commands"""
        
        # Build stats in the format expected by monitoring_commands
        return {
            'message_processing': {
                'total_messages_processed': self.message_stats['total_messages_processed'],
                'crisis_responses_given': self.message_stats['crisis_responses_given'],
                'messages_processed_today': self.message_stats['messages_processed']  # Alias
            },
            'conversation_tracking': {
                'conversations_started': self.message_stats['conversations_started'],
                'follow_ups_handled': self.message_stats['follow_ups_handled'],
                'active_conversations': len(self.active_conversations),
                'ignored_follow_ups': self.message_stats['ignored_follow_ups'],
                'crisis_overrides_triggered': self.message_stats['crisis_overrides_triggered']
            },
            'rate_limiting': {
                'rate_limits_hit': self.message_stats['rate_limits_hit'],
                'daily_limits_hit': self.message_stats['daily_limits_hit'],
                'success_rate_percent': 100.0 - (self.message_stats['rate_limits_hit'] * 100.0 / max(1, self.message_stats['total_messages_processed']))
            },
            'detection_methods': self.message_stats['detection_method_breakdown'].copy(),
            'v3_ensemble_features': self.message_stats['v3_features'].copy()
        }
    
    async def _cleanup_expired_conversations(self):
        """Enhanced conversation cleanup with v3.0 statistics"""
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
            
            # Log v3.0 insights if available
            if conv.get('ensemble_insights'):
                insights = conv['ensemble_insights']
                logger.info(f"   🧠 Ensemble insights: {len(insights)} analyses")
                gap_count = sum(1 for insight in insights if insight.get('gaps_detected'))
                if gap_count > 0:
                    logger.info(f"   🔍 Model disagreements: {gap_count}")
            
            del self.active_conversations[user_id]
    
    def get_enhanced_stats(self) -> Dict:
        """
        Get enhanced statistics including v3.0 features AND all backward compatibility fields
        This method ensures monitoring commands get all expected statistics fields
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
            'messages_processed': self.message_stats['messages_processed'],  # Alias
            'crisis_detected': self.message_stats['crisis_detected'],  # Alias
            
            # Conversation tracking (backward compatibility)
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

# Backward compatibility alias for bot_manager
EnhancedMessageHandler = MessageHandler