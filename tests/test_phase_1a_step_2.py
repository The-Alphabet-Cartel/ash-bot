#!/usr/bin/env python3
"""
Ash-Bot: Crisis Detection Bot for The Alphabet Cartel Discord Community
********************************************************************************
Phase 1a Step 2 Integration Test - NLP Integration Manager
---
FILE VERSION: v3.1-1a-2-2
LAST MODIFIED: 2025-09-05
PHASE: 1a Step 2 Test
CLEAN ARCHITECTURE: v3.1
Repository: https://github.com/the-alphabet-cartel/ash-bot
Community: The Alphabet Cartel - https://discord.gg/alphabetcartel | https://alphabetcartel.org
"""

import asyncio
import logging
import os
import sys
import time
from pathlib import Path
from typing import Dict, Any

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import managers using factory functions (Rule #1)
from managers.unified_config import create_unified_config_manager
from managers.logging_config import create_logging_config_manager
from managers.nlp_integration import create_nlp_integration_manager

async def test_nlp_integration_manager():
    """
    Test Phase 1a Step 2: NLPIntegrationManager
    Following Rule #8: Real-world testing with actual methods
    """
    
    print("🧪 Starting Phase 1a Step 2 Integration Test")
    print("📋 Testing: NLPIntegrationManager with Clean Architecture v3.1")
    print("")
    
    try:
        # Step 1: Initialize UnifiedConfigManager (existing)
        print("🔧 Step 1: Initializing UnifiedConfigManager...")
        config_manager = create_unified_config_manager()
        print("✅ UnifiedConfigManager initialized")
        
        # Step 2: Initialize LoggingConfigManager (existing)  
        print("🔧 Step 2: Initializing LoggingConfigManager...")
        logging_manager = create_logging_config_manager(config_manager)
        print("✅ LoggingConfigManager initialized")
        
        # Get logger for actual testing (Rule #8)
        logger = logging.getLogger(__name__)
        logger.info("🔬 Phase 1a Step 2 testing started")
        
        # Step 3: Test JSON configuration loading
        print("🔧 Step 3: Testing nlp_config.json loading...")
        nlp_config = config_manager.get_config_section('nlp_config')
        assert nlp_config is not None, "nlp_config.json not loaded"
        
        # Test configuration sections exist
        required_sections = ['server_settings', 'connection_settings', 'endpoints', 'validation', 'analysis_settings']
        for section in required_sections:
            assert section in nlp_config, f"Required section '{section}' missing from nlp_config.json"
        
        print("✅ nlp_config.json loaded successfully")
        logger.info("📄 nlp_config.json validation successful")
        
        # Step 4: Test factory function (Rule #1)
        print("🔧 Step 4: Testing NLPIntegrationManager factory function...")
        nlp_manager = create_nlp_integration_manager(
            config_manager=config_manager,
            logging_manager=logging_manager
        )
        assert nlp_manager is not None, "NLPIntegrationManager factory failed"
        assert hasattr(nlp_manager, 'config_manager'), "NLPIntegrationManager missing config_manager"
        assert hasattr(nlp_manager, 'logging_manager'), "NLPIntegrationManager missing logging_manager"
        
        print("✅ Factory function working correctly")
        logger.info("🏭 Factory function validation successful")
        
        # Step 5: Test get_config_section() method usage (critical requirement)
        print("🔧 Step 5: Testing configuration access patterns...")
        
        # Test server settings access
        host = config_manager.get_config_section('nlp_config', 'server_settings.host', '172.20.0.11')
        port = config_manager.get_config_section('nlp_config', 'server_settings.port', 8881)
        assert isinstance(host, str), f"Host should be string, got {type(host)}"
        assert isinstance(port, int), f"Port should be int, got {type(port)}"
        assert 1 <= port <= 65535, f"Port {port} out of valid range"
        
        # Test connection settings
        timeout = config_manager.get_config_section('nlp_config', 'connection_settings.timeout', 30)
        retry_attempts = config_manager.get_config_section('nlp_config', 'connection_settings.retry_attempts', 3)
        assert isinstance(timeout, int), f"Timeout should be int, got {type(timeout)}"
        assert isinstance(retry_attempts, int), f"Retry attempts should be int, got {type(retry_attempts)}"
        assert 5 <= timeout <= 120, f"Timeout {timeout} out of valid range"
        assert 1 <= retry_attempts <= 10, f"Retry attempts {retry_attempts} out of valid range"
        
        print("✅ Configuration access patterns working")
        logger.info("⚙️ Configuration validation successful")
        
        # Step 6: Test Rule #7 compliance - Environment variable reuse
        print("🔧 Step 6: Testing Rule #7 environment variable mapping...")
        
        # Verify manager uses correct configuration values
        assert nlp_manager.nlp_host == host, f"Manager host mismatch: {nlp_manager.nlp_host} != {host}"
        assert nlp_manager.nlp_port == port, f"Manager port mismatch: {nlp_manager.nlp_port} != {port}"
        assert nlp_manager.timeout == timeout, f"Manager timeout mismatch: {nlp_manager.timeout} != {timeout}"
        assert nlp_manager.retry_attempts == retry_attempts, f"Manager retry attempts mismatch"
        
        # Verify URL construction
        expected_url = f"http://{host}:{port}"
        assert nlp_manager.nlp_url == expected_url, f"NLP URL mismatch: {nlp_manager.nlp_url} != {expected_url}"
        
        print("✅ Rule #7 environment variable mapping confirmed")
        logger.info("🔄 Environment variable reuse validation successful")
        
        # Step 7: Test NLP server endpoints configuration
        print("🔧 Step 7: Testing NLP endpoints configuration...")
        
        endpoints = config_manager.get_config_section('nlp_config', 'endpoints', {})
        required_endpoints = ['analyze', 'false_positive', 'false_negative', 'stats', 'health']
        
        for endpoint in required_endpoints:
            assert endpoint in endpoints, f"Required endpoint '{endpoint}' missing"
            endpoint_path = endpoints[endpoint]
            assert isinstance(endpoint_path, str), f"Endpoint {endpoint} should be string"
            assert endpoint_path.startswith('/'), f"Endpoint {endpoint} should start with '/'"
        
        print("✅ NLP endpoints configuration validated")
        logger.info("🔗 Endpoints configuration successful")
        
        # Step 8: Test message validation functionality
        print("🔧 Step 8: Testing message validation...")
        
        # Test valid message
        valid_message = "This is a test message for NLP analysis"
        assert nlp_manager._validate_message_content(valid_message), "Valid message failed validation"
        
        # Test empty message
        empty_message = ""
        assert not nlp_manager._validate_message_content(empty_message), "Empty message should fail validation"
        
        # Test None message
        assert not nlp_manager._validate_message_content(None), "None message should fail validation"
        
        # Test non-string message
        assert not nlp_manager._validate_message_content(123), "Non-string message should fail validation"
        
        # Test whitespace-only message
        whitespace_message = "   \n\t   "
        assert not nlp_manager._validate_message_content(whitespace_message), "Whitespace-only message should fail validation"
        
        print("✅ Message validation working correctly")
        logger.info("✔️ Message validation successful")
        
        # Step 9: Test health status functionality
        print("🔧 Step 9: Testing health status functionality...")
        
        health_status = nlp_manager.get_health_status()
        assert isinstance(health_status, dict), "Health status should be dictionary"
        
        required_health_fields = ['service_healthy', 'nlp_url', 'connection_attempts', 'analysis_stats', 'timeout_seconds', 'retry_attempts']
        for field in required_health_fields:
            assert field in health_status, f"Required health field '{field}' missing"
        
        # Verify health status structure
        assert isinstance(health_status['service_healthy'], bool), "service_healthy should be boolean"
        assert isinstance(health_status['nlp_url'], str), "nlp_url should be string"
        assert isinstance(health_status['connection_attempts'], int), "connection_attempts should be int"
        assert isinstance(health_status['analysis_stats'], dict), "analysis_stats should be dict"
        assert isinstance(health_status['timeout_seconds'], int), "timeout_seconds should be int"
        assert isinstance(health_status['retry_attempts'], int), "retry_attempts should be int"
        
        print("✅ Health status functionality working")
        logger.info("💚 Health status validation successful")
        
        # Step 10: Test response processing functionality
        print("🔧 Step 10: Testing response processing...")
        
        # Create sample response matching sample_response.json format
        sample_response = {
            'needs_response': True,
            'crisis_level': 'medium',
            'confidence_score': 0.85,
            'detected_categories': ['depression', 'anxiety'],
            'method': 'ensemble_analysis',
            'processing_time_ms': 145,
            'model_info': 'three_model_ensemble',
            'reasoning': 'User expressing suicidal ideation',
            'analysis': {
                'complete_analysis': {
                    'requires_staff_review': True,
                    'ai_model_details': {
                        'individual_results': [
                            {'model': 'model_1', 'crisis_level': 'high'},
                            {'model': 'model_2', 'crisis_level': 'medium'},
                            {'model': 'model_3', 'crisis_level': 'medium'}
                        ]
                    }
                }
            }
        }
        
        processed = nlp_manager._process_response(sample_response)
        assert processed is not None, "Response processing returned None"
        assert isinstance(processed, dict), "Processed response should be dictionary"
        
        # Verify core fields are processed correctly
        assert processed['needs_response'] == True, "needs_response not processed correctly"
        assert processed['crisis_level'] == 'medium', "crisis_level not processed correctly"
        assert processed['confidence_score'] == 0.85, "confidence_score not processed correctly"
        assert processed['method'] == 'ensemble_analysis', "method not processed correctly"
        
        # Verify v3.0 specific features
        assert 'gaps_detected' in processed, "gaps_detected field missing"
        assert 'requires_staff_review' in processed, "requires_staff_review field missing"
        assert processed['requires_staff_review'] == True, "requires_staff_review not set correctly"
        
        print("✅ Response processing working correctly")
        logger.info("📊 Response processing validation successful")
        
        # Step 11: Test resilient error handling (Rule #5)
        print("🔧 Step 11: Testing resilient error handling...")
        
        # Test invalid response processing
        invalid_response = {"invalid": "data"}
        processed_invalid = nlp_manager._process_response(invalid_response)
        assert processed_invalid is not None, "Should handle invalid response gracefully"
        assert processed_invalid['crisis_level'] == 'none', "Should default to 'none' crisis level"
        assert processed_invalid['confidence_score'] == 0.0, "Should default to 0.0 confidence"
        
        # Test empty response processing
        empty_response = {}
        processed_empty = nlp_manager._process_response(empty_response)
        assert processed_empty is not None, "Should handle empty response gracefully"
        
        print("✅ Resilient error handling working")
        logger.info("🛡️ Error handling validation successful")
        
        # Step 12: Test manager integration points
        print("🔧 Step 12: Testing manager integration points...")
        
        # Test that manager maintains proper state
        assert nlp_manager.connection_attempts >= 0, "Connection attempts should be non-negative"
        assert nlp_manager.analysis_stats is not None, "Analysis stats should be initialized"
        assert isinstance(nlp_manager.analysis_stats, dict), "Analysis stats should be dictionary"
        
        # Test configuration manager integration
        assert nlp_manager.config_manager is config_manager, "Config manager reference should match"
        assert nlp_manager.logging_manager is logging_manager, "Logging manager reference should match"
        
        print("✅ Manager integration points working")
        logger.info("🔧 Manager integration validation successful")
        
        # Final validation
        print("")
        print("🎉 Phase 1a Step 2 Integration Test PASSED")
        print("✅ NLPIntegrationManager fully functional")
        print("✅ Clean Architecture v3.1 compliance verified")
        print("✅ Rule #7 environment variable mapping confirmed")
        print("✅ Factory function pattern working")
        print("✅ JSON configuration loading successful")
        print("✅ Message validation operational")
        print("✅ Response processing functional")
        print("✅ Resilient error handling operational")
        
        logger.info("🎉 Phase 1a Step 2 testing completed successfully")
        logger.info("📊 All integration tests passed")
        
        return True
        
    except AssertionError as e:
        print(f"❌ Test assertion failed: {e}")
        logger.error(f"❌ Test assertion failed: {e}")
        return False
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        logger.error(f"❌ Test failed with error: {e}")
        logger.exception("Full test error traceback:")
        return False

def main():
    """Run the Phase 1a Step 2 integration test"""
    print("=" * 70)
    print("ASH-BOT PHASE 1a STEP 2 INTEGRATION TEST")
    print("Clean Architecture v3.1 - NLP Integration Manager")
    print("The Alphabet Cartel - https://discord.gg/alphabetcartel")
    print("=" * 70)
    print("")
    
    # Run the test
    success = asyncio.run(test_nlp_integration_manager())
    
    if success:
        print("")
        print("=" * 70)
        print("🎉 PHASE 1a STEP 2 COMPLETE!")
        print("Ready to proceed to Phase 1a Step 3: Crisis Analysis Manager")
        print("=" * 70)
        sys.exit(0)
    else:
        print("")
        print("=" * 70)
        print("❌ PHASE 1a STEP 2 FAILED!")
        print("Please review errors and fix before proceeding")
        print("=" * 70)
        sys.exit(1)

if __name__ == "__main__":
    main()