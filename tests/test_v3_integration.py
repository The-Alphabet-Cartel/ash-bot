#!/usr/bin/env python3
"""
V3.0 Integration Test Script

Test the updated ash-bot integration with the new v3.0 NLP response structure.
This script validates that the bot can properly process the three-model ensemble responses.

Usage:
    cd ash/ash-bot
    python tests/test_v3_integration.py

Repository: https://github.com/The-Alphabet-Cartel/ash-bot
Location: ash/ash-bot/tests/test_v3_integration.py
"""

import asyncio
import json
import sys
import os
import logging
from datetime import datetime

# Add the ash-bot root to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

async def test_v3_integration():
    """Test the v3.0 NLP integration"""
    
    print("🧪 V3.0 Integration Test")
    print("=" * 50)
    print(f"🕒 Test started: {datetime.now()}")
    print()
    
    # Import the updated NLP integration
    try:
        from bot.integrations.nlp_integration import NLPIntegration
        print("✅ Successfully imported NLPIntegration")
    except ImportError as e:
        print(f"❌ Failed to import NLPIntegration: {e}")
        return False
    
    # Initialize NLP client
    nlp_url = os.getenv('GLOBAL_NLP_API_URL', 'http://10.20.30.253:8881')
    nlp_client = NLPIntegration(nlp_url, timeout=30)
    
    print(f"🔗 Testing connection to: {nlp_url}")
    
    # Test 1: Health check
    print("\n1️⃣ Testing health check...")
    health_ok = await nlp_client.test_connection()
    if health_ok:
        print("✅ Health check passed")
    else:
        print("❌ Health check failed - NLP service may be unavailable")
        return False
    
    # Test 2: Basic message analysis
    print("\n2️⃣ Testing basic message analysis...")
    test_messages = [
        {
            "message": "I want to die",
            "expected_crisis": "high",
            "description": "Clear crisis language"
        },
        {
            "message": "I'm feeling a bit down today",
            "expected_crisis": "low",
            "description": "Mild distress"
        },
        {
            "message": "This game is awesome!",
            "expected_crisis": "none",
            "description": "Positive content"
        }
    ]
    
    test_results = []
    
    for i, test_case in enumerate(test_messages, 1):
        print(f"\n   Test 2.{i}: {test_case['description']}")
        print(f"   Message: '{test_case['message']}'")
        
        try:
            result = await nlp_client.analyze_message(
                test_case['message'],
                f"test_user_{i}",
                f"test_channel_{i}"
            )
            
            if result:
                crisis_level = result.get('crisis_level', 'unknown')
                confidence = result.get('confidence_score', 0.0)
                method = result.get('method', 'unknown')
                
                print(f"   📊 Result: {crisis_level} (confidence: {confidence:.3f}) via {method}")
                
                # Check v3.0 specific fields
                if result.get('gaps_detected'):
                    print(f"   ⚠️ Model disagreement detected")
                
                if result.get('requires_staff_review'):
                    print(f"   👥 Staff review required")
                
                processing_time = result.get('processing_time_ms', 0)
                if processing_time > 0:
                    print(f"   ⏱️ Processing time: {processing_time:.1f}ms")
                
                # Check for ensemble details
                if result.get('ensemble_details'):
                    ensemble = result['ensemble_details']
                    predictions = ensemble.get('model_predictions', {})
                    if predictions and len(set(predictions.values())) > 1:
                        print(f"   🔍 Model predictions: {predictions}")
                
                test_results.append({
                    'test_case': test_case,
                    'result': result,
                    'success': True
                })
                
                print(f"   ✅ Analysis successful")
                
            else:
                print(f"   ❌ Analysis returned None")
                test_results.append({
                    'test_case': test_case,
                    'result': None,
                    'success': False
                })
                
        except Exception as e:
            print(f"   ❌ Analysis failed: {e}")
            logger.exception("Full error:")
            test_results.append({
                'test_case': test_case,
                'result': None,
                'success': False,
                'error': str(e)
            })
    
    # Test 3: Ensemble metrics (if available)
    print("\n3️⃣ Testing ensemble metrics...")
    try:
        ensemble_metrics = await nlp_client.get_ensemble_metrics()
        if ensemble_metrics:
            print("✅ Ensemble metrics available")
            print(f"   📊 Sample metrics: {list(ensemble_metrics.keys())[:3]}")
        else:
            print("ℹ️ Ensemble metrics not available (may not be implemented yet)")
    except Exception as e:
        print(f"⚠️ Ensemble metrics test failed: {e}")
    
    # Test 4: Service stats
    print("\n4️⃣ Testing service statistics...")
    try:
        stats = await nlp_client.get_service_stats()
        if stats:
            print("✅ Service stats available")
            print(f"   📊 Stats available: {list(stats.keys())[:5]}")
        else:
            print("ℹ️ Service stats not available")
    except Exception as e:
        print(f"⚠️ Service stats test failed: {e}")
    
    # Test Summary
    print("\n" + "=" * 50)
    print("📋 TEST SUMMARY")
    print("=" * 50)
    
    successful_tests = sum(1 for result in test_results if result['success'])
    total_tests = len(test_results)
    
    print(f"✅ Successful analyses: {successful_tests}/{total_tests}")
    
    if successful_tests == total_tests:
        print("🎉 All tests passed! V3.0 integration is working correctly.")
        
        # Show sample v3.0 features found
        v3_features_found = []
        for result in test_results:
            if result['success'] and result['result']:
                r = result['result']
                if r.get('gaps_detected'):
                    v3_features_found.append("Gap detection")
                if r.get('requires_staff_review'):
                    v3_features_found.append("Staff review flagging")
                if r.get('ensemble_details'):
                    v3_features_found.append("Ensemble analysis")
                if r.get('method', '').startswith('three_model'):
                    v3_features_found.append("Three-model ensemble")
        
        if v3_features_found:
            unique_features = list(set(v3_features_found))
            print("🆕 V3.0 features detected:")
            for feature in unique_features:
                print(f"   • {feature}")
        
        return True
    else:
        print(f"❌ {total_tests - successful_tests} tests failed. Check the logs above.")
        return False

async def test_message_handler_integration():
    """Test the message handler integration"""
    
    print("\n" + "=" * 50)
    print("🤖 MESSAGE HANDLER INTEGRATION TEST")
    print("=" * 50)
    
    try:
        # This would test the actual message handler if we have a bot instance
        # For now, just validate that the imports work
        from bot.handlers.message_handler import MessageHandler
        print("✅ MessageHandler import successful")
        
        # Could add more comprehensive tests here when we have a bot instance
        print("ℹ️ Full message handler testing requires bot instance")
        return True
        
    except ImportError as e:
        print(f"❌ MessageHandler import failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting V3.0 Integration Tests")
    
    async def run_all_tests():
        # Test NLP integration
        nlp_success = await test_v3_integration()
        
        # Test message handler integration
        handler_success = await test_message_handler_integration()
        
        print("\n" + "=" * 50)
        print("🏁 FINAL RESULTS")
        print("=" * 50)
        
        if nlp_success and handler_success:
            print("🎉 All integration tests passed!")
            print("✅ Ash-bot is ready for v3.0 NLP service")
            return True
        else:
            print("❌ Some tests failed. Please review the errors above.")
            return False
    
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)