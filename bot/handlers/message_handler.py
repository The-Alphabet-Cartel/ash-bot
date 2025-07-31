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
    
    def __init__(self, bot, keyword_detector, nlp_client, config):
        self.bot = bot
        self.keyword_detector = keyword_detector
        self.nlp_client = nlp_client
        self.config = config
        
        # Enhanced statistics tracking
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
            }
        }
        
        # Conversation tracking (existing logic)
        self.active_conversations = {}
        self.conversation_timeout = config.get('BOT_CONVERSATION_TIMEOUT', 300)
        
        logger.info("📨 Enhanced Message Handler initialized for v3.0")
    
    async def _perform_hybrid_detection(self, message: Message) -> Dict:
        """
        Enhanced hybrid detection with v3.0 NLP support
        Maintains existing safety-first logic while leveraging new features
        """
        
        # Method 1: Keyword detection (always runs first)
        keyword_result = self.keyword_detector.check_message(message.content)
        logger.info(f"🔤 Keyword detection: {keyword_result['crisis_level']} (needs_response: {keyword_result['needs_response']})")
        
        # Method 2: NLP analysis with v3.0 ensemble (if available)
        nlp_result = None
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
        
        # Clean up expired conversations (existing logic)
        await self._cleanup_expired_conversations()
        
        # Perform hybrid crisis detection with v3.0 enhancements
        detection_result = await self._perform_hybrid_detection(message)
        
        # If crisis detected, update statistics and return result
        if detection_result['needs_response']:
            self.message_stats['crisis_detected'] += 1
            
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
        """Get enhanced statistics including v3.0 features"""
        
        base_stats = {
            'messages_processed': self.message_stats['messages_processed'],
            'crisis_detected': self.message_stats['crisis_detected'],
            'detection_rate': (
                self.message_stats['crisis_detected'] / max(1, self.message_stats['messages_processed'])
            ),
            'method_breakdown': self.message_stats['detection_method_breakdown'].copy()
        }
        
        # Add v3.0 specific statistics
        v3_stats = self.message_stats['v3_features'].copy()
        if v3_stats['ensemble_analyses'] > 0:
            v3_stats['gap_detection_rate'] = (
                v3_stats['gaps_detected_count'] / v3_stats['ensemble_analyses']
            )
            v3_stats['staff_review_rate'] = (
                v3_stats['staff_reviews_triggered'] / v3_stats['ensemble_analyses']
            )
        else:
            v3_stats['gap_detection_rate'] = 0.0
            v3_stats['staff_review_rate'] = 0.0
        
        base_stats['v3_ensemble_features'] = v3_stats
        
        return base_stats