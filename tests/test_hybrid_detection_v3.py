#!/usr/bin/env python3
"""
Test Hybrid Detection with v3.0 Integration

Validates that the hybrid detection logic (keywords + NLP) works correctly
with the new v3.0 ensemble responses while maintaining safety-first approach.

Location: ash/ash-bot/tests/test_hybrid_detection_v3.py
Repository: https://github.com/The-Alphabet-Cartel/ash-bot
"""

import unittest
import asyncio
import sys
import os
from unittest.mock import Mock, AsyncMock, patch

# Add ash-bot root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bot.handlers.message_handler import MessageHandler

class TestHybridDetectionV3(unittest.TestCase):
    """Test hybrid detection with v3.0 NLP integration"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.mock_bot = Mock()
        self.mock_keyword_detector = Mock()
        self.mock_nlp_client = Mock()
        self.mock_config = {}
        
        self.handler = MessageHandler(
            self.mock_bot,
            self.mock_keyword_detector, 
            self.mock_nlp_client,
            self.mock_config
        )
    
    def test_keyword_primary_safety_first(self):
        """Test that keywords take priority when higher (safety-first)"""
        
        # Mock keyword detection: HIGH crisis
        keyword_result = {
            'needs_response': True,
            'crisis_level': 'high',
            'detected_categories': ['suicidal_ideation']
        }
        
        # Mock NLP detection: MEDIUM crisis (lower than keywords)
        nlp_result = {
            'needs_response': True,
            'crisis_level': 'medium',
            'confidence_score': 0.6,
            'detected_categories': ['depression_moderate'],
            'requires_staff_review': False,
            'gaps_detected': False,
            'processing_time_ms': 250.0,
            'method': 'three_model_ensemble',
            'reasoning': 'Ensemble detected moderate depression'
        }
        
        # Combine results
        result = self.handler._combine_detection_results_v3(keyword_result, nlp_result)
        
        # Should choose KEYWORDS (higher priority)
        self.assertEqual(result['crisis_level'], 'high')
        self.assertEqual(result['method'], 'keyword_primary')
        self.assertEqual(result['confidence'], 0.9)  # Keywords are high confidence
        self.assertEqual(result['requires_staff_review'], True)  # High crisis always needs review
        
        # Should combine detected categories
        categories = result['detected_categories']
        self.assertIn('suicidal_ideation', categories)
        self.assertIn('depression_moderate', categories)
    
    def test_nlp_primary_when_higher(self):
        """Test that NLP takes priority when higher (safety-first)"""
        
        # Mock keyword detection: LOW crisis
        keyword_result = {
            'needs_response': True,
            'crisis_level': 'low',
            'detected_categories': ['mild_distress']
        }
        
        # Mock NLP detection: HIGH crisis (higher than keywords)
        nlp_result = {
            'needs_response': True,
            'crisis_level': 'high',
            'confidence_score': 0.85,
            'detected_categories': ['depression_severe', 'suicidal_thoughts'],
            'requires_staff_review': True,
            'gaps_detected': False,
            'processing_time_ms': 380.5,
            'method': 'three_model_ensemble_high_confidence',
            'reasoning': 'Strong ensemble consensus for high crisis'
        }
        
        # Combine results
        result = self.handler._combine_detection_results_v3(keyword_result, nlp_result)
        
        # Should choose NLP (higher priority)
        self.assertEqual(result['crisis_level'], 'high')
        self.assertEqual(result['method'], 'nlp_primary')
        self.assertEqual(result['confidence'], 0.85)  # Use NLP confidence
        self.assertEqual(result['requires_staff_review'], True)  # From NLP recommendation
        
        # Should have v3.0 fields
        self.assertEqual(result['gaps_detected'], False)
        self.assertEqual(result['processing_time_ms'], 380.5)
        self.assertEqual(result['model_info'], 'unknown')  # Default when not provided
    
    def test_gap_detection_forces_staff_review(self):
        """Test that gap detection forces staff review regardless of level"""
        
        keyword_result = {
            'needs_response': True,
            'crisis_level': 'low',
            'detected_categories': ['mild_concern']
        }
        
        # NLP with gap detection (models disagreed)
        nlp_result = {
            'needs_response': True,
            'crisis_level': 'medium',
            'confidence_score': 0.45,  # Lower confidence due to disagreement
            'detected_categories': ['emotional_distress'],
            'requires_staff_review': False,  # Normally wouldn't require review
            'gaps_detected': True,  # But gap detected!
            'processing_time_ms': 450.0,
            'ensemble_details': {
                'model_predictions': {
                    'depression': 'safe',
                    'sentiment': 'crisis',
                    'emotional_distress': 'mild_crisis'
                },
                'gap_details': [
                    {
                        'type': 'meaningful_disagreement',
                        'reason': 'Models disagree on crisis severity'
                    }
                ]
            }
        }
        
        result = self.handler._combine_detection_results_v3(keyword_result, nlp_result)
        
        # Gap detection should force staff review
        self.assertEqual(result['requires_staff_review'], True)
        self.assertEqual(result['gaps_detected'], True)
        
        # Should choose NLP (higher level)
        self.assertEqual(result['crisis_level'], 'medium')
        self.assertEqual(result['method'], 'nlp_primary')
    
    def test_nlp_unavailable_fallback(self):
        """Test fallback to keywords when NLP is unavailable"""
        
        keyword_result = {
            'needs_response': True,
            'crisis_level': 'medium',
            'detected_categories': ['depression_keywords']
        }
        
        nlp_result = None  # NLP service unavailable
        
        result = self.handler._combine_detection_results_v3(keyword_result, nlp_result)
        
        # Should fall back to keywords
        self.assertEqual(result['crisis_level'], 'medium')
        self.assertEqual(result['method'], 'keyword_only')
        self.assertEqual(result['confidence'], 0.9)
        
        # v3.0 fields should have sensible defaults
        self.assertEqual(result['requires_staff_review'], False)  # Medium crisis, keywords only
        self.assertEqual(result['gaps_detected'], False)
        self.assertEqual(result['processing_time_ms'], 0)
    
    def test_no_crisis_detected(self):
        """Test when neither method detects crisis"""
        
        keyword_result = {
            'needs_response': False,
            'crisis_level': 'none',
            'detected_categories': []
        }
        
        nlp_result = {
            'needs_response': False,
            'crisis_level': 'none',
            'confidence_score': 0.1,
            'detected_categories': [],
            'requires_staff_review': False,
            'gaps_detected': False,
            'processing_time_ms': 200.0
        }
        
        result = self.handler._combine_detection_results_v3(keyword_result, nlp_result)
        
        # Should indicate no crisis
        self.assertEqual(result['needs_response'], False)
        self.assertEqual(result['crisis_level'], 'none')
        self.assertEqual(result['requires_staff_review'], False)
    
    def test_equal_crisis_levels_prefer_keywords(self):
        """Test that equal crisis levels prefer keywords (more reliable)"""
        
        keyword_result = {
            'needs_response': True,
            'crisis_level': 'medium',
            'detected_categories': ['depression_keywords']
        }
        
        nlp_result = {
            'needs_response': True,
            'crisis_level': 'medium',  # Same level
            'confidence_score': 0.7,
            'detected_categories': ['emotional_distress'],
            'requires_staff_review': True,
            'gaps_detected': False
        }
        
        result = self.handler._combine_detection_results_v3(keyword_result, nlp_result)
        
        # Should prefer keywords when equal (>= in hierarchy check)
        self.assertEqual(result['method'], 'keyword_primary')
        self.assertEqual(result['confidence'], 0.9)  # Keyword confidence
        self.assertEqual(result['requires_staff_review'], True)  # Medium crisis = no review normally, but keyword high confidence

class TestHybridDetectionAsync(unittest.IsolatedAsyncioTestCase):
    """Async tests for hybrid detection"""
    
    async def test_full_hybrid_detection_flow(self):
        """Test the full async hybrid detection flow"""
        
        # Set up mocks
        mock_bot = Mock()
        mock_keyword_detector = Mock()
        mock_nlp_client = AsyncMock()
        mock_config = {'BOT_CONVERSATION_TIMEOUT': 300}
        
        handler = MessageHandler(mock_bot, mock_keyword_detector, mock_nlp_client, mock_config)
        
        # Mock message
        mock_message = Mock()
        mock_message.content = "I want to end it all"
        mock_message.author.id = 12345
        mock_message.channel.id = 67890
        mock_message.id = 999
        
        # Mock keyword detection
        mock_keyword_detector.check_message.return_value = {
            'needs_response': True,
            'crisis_level': 'high',
            'detected_categories': ['suicidal_ideation']
        }
        
        # Mock NLP detection
        mock_nlp_client.analyze_message.return_value = {
            'needs_response': True,
            'crisis_level': 'high',
            'confidence_score': 0.92,
            'detected_categories': ['depression_severe'],
            'requires_staff_review': True,
            'gaps_detected': False,
            'processing_time_ms': 340.2,
            'method': 'three_model_ensemble_high_confidence'
        }
        
        # Run hybrid detection
        result = await handler._perform_hybrid_detection(mock_message)
        
        # Validate result
        self.assertEqual(result['crisis_level'], 'high')
        self.assertEqual(result['needs_response'], True)
        self.assertEqual(result['requires_staff_review'], True)
        
        # Should have called both detectors
        mock_keyword_detector.check_message.assert_called_once_with("I want to end it all")
        mock_nlp_client.analyze_message.assert_called_once_with(
            "I want to end it all", "12345", "67890"
        )

if __name__ == '__main__':
    unittest.main(verbosity=2)