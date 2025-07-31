"""
Detection Service - Coordinates crisis detection
"""

import logging
from typing import Dict, Optional
from discord import Message

from bot.utils.keyword_detector import KeywordDetector

logger = logging.getLogger(__name__)

class DetectionService:
    """Coordinates all crisis detection methods"""
    
    def __init__(self, claude_integration, nlp_integration, config):
        self.claude_integration = claude_integration
        self.nlp_integration = nlp_integration
        self.config = config
        
        # Initialize your existing keyword detector
        self.keyword_detector = KeywordDetector()
        
        logger.info("🔍 Detection service initialized with hybrid detection")
    
    async def detect_crisis(self, message: Message) -> Dict:
        """
        Main crisis detection using your existing hybrid approach
        """
        try:
            # Method 1: Your existing keyword detection (always runs)
            keyword_result = self.keyword_detector.check_message(message.content)
            
            # Method 2: Your existing NLP analysis (if available)
            nlp_result = await self.nlp_integration.analyze_message(
                message.content,
                str(message.author.id),
                str(message.channel.id)
            )
            
            # Use your existing hybrid decision logic
            final_result = self._combine_detection_results(keyword_result, nlp_result)
            
            # Log detection decision
            self._log_detection_decision(message, keyword_result, nlp_result, final_result)
            
            return final_result
            
        except Exception as e:
            logger.error(f"Error in crisis detection: {e}")
            # Fallback to keyword-only detection
            return self.keyword_detector.check_message(message.content)
    
    def _combine_detection_results(self, keyword_result: Dict, nlp_result: Optional[Dict]) -> Dict:
        """
        Your existing hybrid detection logic from main.py
        """
        # If NLP unavailable, use keywords only
        if not nlp_result:
            return {
                'needs_response': keyword_result['needs_response'],
                'crisis_level': keyword_result['crisis_level'],
                'method': 'keyword_only',
                'confidence': 0.9 if keyword_result['needs_response'] else 0.0,
                'detected_categories': keyword_result['detected_categories']
            }
        
        # Both methods available - use hybrid logic (your existing approach)
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
        
        return {
            'needs_response': final_level != 'none',
            'crisis_level': final_level,
            'method': method,
            'confidence': confidence,
            'detected_categories': keyword_result['detected_categories'] + nlp_result.get('detected_categories', []),
            'keyword_result': keyword_level,
            'nlp_result': nlp_level
        }
    
    async def get_crisis_response(self, message: Message, detection_result: Dict) -> str:
        """Get appropriate crisis response from Claude"""
        try:
            crisis_level = detection_result['crisis_level']
            username = message.author.display_name
            
            # Use your existing Claude integration
            response = await self.claude_integration.get_ash_response(
                message.content,
                crisis_level,
                username
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error getting crisis response: {e}")
            return self._get_fallback_response(detection_result['crisis_level'])
    
    def _get_fallback_response(self, crisis_level: str) -> str:
        """Get fallback response if Claude is unavailable"""
        resources_channel = self.config.get('BOT_RESOURCES_CHANNEL_NAME', 'resources')
        
        if crisis_level == 'high':
            return f"I hear you, and I want you to know that you matter. Please reach out to our crisis team or check #{resources_channel} for immediate support resources."
        elif crisis_level == 'medium':
            return f"It sounds like you're going through a really difficult time. You're not alone in this - our community is here for you."
        else:
            return f"I see you're struggling. That takes courage to share. We're here with you."
    
    def _log_detection_decision(self, message: Message, keyword_result: Dict, 
                              nlp_result: Optional[Dict], final_result: Dict):
        """Log the detection decision for monitoring"""
        message_preview = message.content[:30] + "..." if len(message.content) > 30 else message.content
        
        if nlp_result:
            logger.info(
                f"Hybrid Detection: '{message_preview}' -> "
                f"Keywords: {keyword_result['crisis_level']}, "
                f"NLP: {nlp_result.get('crisis_level', 'none')}, "
                f"Final: {final_result['crisis_level']} ({final_result['method']})"
            )
        else:
            logger.info(
                f"Keyword Detection: '{message_preview}' -> "
                f"{final_result['crisis_level']} (NLP unavailable)"
            )
    
    # Convenience methods for accessing your existing keyword detector
    def get_keyword_stats(self) -> Dict:
        return self.keyword_detector.get_keyword_stats()
    
    def reload_keywords(self):
        return self.keyword_detector.reload_keywords()