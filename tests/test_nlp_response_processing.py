#!/usr/bin/env python3
"""
Test NLP v3.0 Response Processing

Validates that ash-bot correctly processes the new v3.0 NLP response structure
with mock responses to ensure compatibility.

Location: ash/ash-bot/tests/test_nlp_response_processing.py
Repository: https://github.com/The-Alphabet-Cartel/ash-bot
"""

import unittest
import json
import sys
import os

# Add ash-bot root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bot.integrations.nlp_integration import EnhancedNLPClient

class TestNLPResponseProcessing(unittest.TestCase):
    """Test v3.0 NLP response processing"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.nlp_client = EnhancedNLPClient("http://test-server:8881", timeout=5)
    
    def test_v3_response_processing(self):
        """Test processing of v3.0 response structure"""
        
        # Sample v3.0 response (based on your provided example)
        v3_response = {
            "needs_response": True,
            "crisis_level": "high",
            "confidence_score": 0.6279780387878419,
            "detected_categories": [
                "depression_severe",
                "emotional_distress_medium distress"
            ],
            "method": "three_model_ensemble_most_severe_normalized_centralized",
            "processing_time_ms": 367.1274185180664,
            "model_info": "three_model_ensemble_centralized_thresholds",
            "reasoning": "Ensemble consensus: crisis (confidence: 0.628, method: most_severe_normalized)",
            "requires_staff_review": True,
            "gaps_detected": False,
            "analysis": {
                "ensemble_analysis": {
                    "individual_results": {
                        "depression": [
                            {
                                "label": "severe",
                                "score": 0.7849725484848022,
                                "model_type": "depression_specialist"
                            }
                        ],
                        "sentiment": [
                            {
                                "label": "Very Negative",
                                "score": 0.6535853743553162,
                                "model_type": "sentiment_specialist"
                            }
                        ],
                        "emotional_distress": [
                            {
                                "label": "Medium Distress",
                                "score": 0.599744975566864,
                                "model_type": "distress_specialist"
                            }
                        ]
                    },
                    "predictions": {
                        "depression": "severe",
                        "sentiment": "Very Negative",
                        "emotional_distress": "Medium Distress"
                    },
                    "consensus": {
                        "prediction": "crisis",
                        "confidence": 0.6279780387878419,
                        "method": "most_severe_normalized"
                    }
                }
            }
        }
        
        # Process the response
        processed = self.nlp_client._process_v3_response(v3_response)
        
        # Validate core fields are preserved
        self.assertEqual(processed['needs_response'], True)
        self.assertEqual(processed['crisis_level'], 'high')
        self.assertAlmostEqual(processed['confidence_score'], 0.628, places=2)
        self.assertEqual(processed['detected_categories'], [
            "depression_severe",
            "emotional_distress_medium distress"
        ])
        
        # Validate v3.0 specific fields
        self.assertEqual(processed['requires_staff_review'], True)
        self.assertEqual(processed['gaps_detected'], False)
        self.assertEqual(processed['method'], "three_model_ensemble_most_severe_normalized_centralized")
        self.assertAlmostEqual(processed['processing_time_ms'], 367.1, places=1)
        
        # Validate ensemble details
        self.assertIn('ensemble_details', processed)
        ensemble_details = processed['ensemble_details']
        self.assertIn('model_predictions', ensemble_details)
        self.assertIn('consensus_confidence', ensemble_details)
        
        predictions = ensemble_details['model_predictions']
        self.assertEqual(predictions['depression'], 'severe')
        self.assertEqual(predictions['sentiment'], 'Very Negative')
        self.assertEqual(predictions['emotional_distress'], 'Medium Distress')
    
    def test_backward_compatibility_v2_response(self):
        """Test that v2.x responses still work"""
        
        # Sample v2.x response format
        v2_response = {
            "needs_response": True,
            "crisis_level": "medium",
            "confidence_score": 0.75,
            "detected_categories": ["depression_moderate"],
            "processing_time_ms": 120.5
        }
        
        # Process the response
        processed = self.nlp_client._process_v3_response(v2_response)
        
        # Validate core fields work
        self.assertEqual(processed['needs_response'], True)
        self.assertEqual(processed['crisis_level'], 'medium')
        self.assertAlmostEqual(processed['confidence_score'], 0.75, places=2)
        
        # Validate v3.0 fields have defaults
        self.assertEqual(processed['requires_staff_review'], False)
        self.assertEqual(processed['gaps_detected'], False)
        self.assertEqual(processed['method'], 'three_model_ensemble')  # Default
    
    def test_gap_detection_response(self):
        """Test response with gap detection enabled"""
        
        gap_response = {
            "needs_response": True,
            "crisis_level": "medium",
            "confidence_score": 0.55,
            "detected_categories": ["emotional_distress_medium"],
            "method": "three_model_ensemble_gap_detected",
            "processing_time_ms": 420.3,
            "requires_staff_review": True,  # Forced due to gap
            "gaps_detected": True,
            "analysis": {
                "ensemble_analysis": {
                    "predictions": {
                        "depression": "safe",
                        "sentiment": "crisis", 
                        "emotional_distress": "crisis"
                    },
                    "consensus": {
                        "prediction": "mild_crisis",
                        "confidence": 0.55,
                        "method": "most_severe_normalized"
                    }
                },
                "gap_details": [
                    {
                        "type": "meaningful_disagreement",
                        "reason": "Models significantly disagree on crisis level"
                    }
                ]
            }
        }
        
        processed = self.nlp_client._process_v3_response(gap_response)
        
        # Validate gap detection fields
        self.assertEqual(processed['gaps_detected'], True)
        self.assertEqual(processed['requires_staff_review'], True)
        
        # Validate gap details are captured
        ensemble_details = processed['ensemble_details']
        gap_details = ensemble_details.get('gap_details', [])
        self.assertEqual(len(gap_details), 1)
        self.assertEqual(gap_details[0]['type'], 'meaningful_disagreement')
        
        # Validate conflicting predictions are captured
        predictions = ensemble_details['model_predictions']
        self.assertEqual(predictions['depression'], 'safe')
        self.assertEqual(predictions['sentiment'], 'crisis')
        self.assertEqual(predictions['emotional_distress'], 'crisis')
    
    def test_missing_fields_handling(self):
        """Test handling of responses with missing fields"""
        
        minimal_response = {
            "crisis_level": "low",
            "confidence_score": 0.3
            # Missing many fields
        }
        
        processed = self.nlp_client._process_v3_response(minimal_response)
        
        # Should have sensible defaults
        self.assertEqual(processed['needs_response'], False)  # Default
        self.assertEqual(processed['crisis_level'], 'low')
        self.assertEqual(processed['detected_categories'], [])  # Default
        self.assertEqual(processed['requires_staff_review'], False)  # Default
        self.assertEqual(processed['gaps_detected'], False)  # Default

if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2)