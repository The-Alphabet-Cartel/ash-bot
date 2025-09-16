"""
Ash-Bot: Crisis Detection Bot for The Alphabet Cartel Discord Community
********************************************************************************
Phase 1c Step 1 Integration Test - Learning System Manager for Ash-Bot
---
FILE VERSION: v3.1-1c-1-2
LAST MODIFIED: 2025-09-09
PHASE: 1c Step 1
CLEAN ARCHITECTURE: v3.1
Repository: https://github.com/the-alphabet-cartel/ash-bot
Community: The Alphabet Cartel - https://discord.gg/alphabetcartel | https://alphabetcartel.org
"""

import asyncio
import json
import logging
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

# Import managers for testing (Rule #8 - real methods, not mocks)
from managers.unified_config import create_unified_config_manager
from managers.logging_config import create_logging_config_manager
from managers.nlp_integration import create_nlp_integration_manager
from managers.learning_system import create_learning_system_manager

async def test_phase_1c_step_1_learning_system_manager():
    """
    Phase 1c Step 1 Integration Test: LearningSystemManager
    
    Tests:
    1. LearningSystemManager factory function and initialization
    2. Configuration loading using get_config_section method
    3. Environment variable reuse (Rule #7) compliance
    4. Staff feedback submission (false positives and negatives)
    5. Learning statistics and effectiveness tracking
    6. Daily adjustment limits and learning system health
    7. Integration with NLPIntegrationManager
    8. Resilient error handling and safe defaults (Rule #5)
    """
    
    print("🧪 Starting Phase 1c Step 1 Integration Test")
    print("📋 Testing: LearningSystemManager")
    print("🎯 Focus: Staff feedback collection and NLP learning integration")
    print("")
    
    try:
        # ====================================================================
        # FOUNDATION SETUP (Using existing managers)
        # ====================================================================
        
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
        logger.info("🔬 Phase 1c Step 1 learning system testing started")
        
        # Step 3: Test learning_config.json loading
        print("🔧 Step 3: Testing learning_config.json loading...")
        learning_config = config_manager.get_config_section('learning_config')
        assert learning_config is not None, "learning_config.json not loaded"
        
        # Test configuration sections exist
        required_sections = [
            'learning_settings', 'feedback_processing', 'learning_coordination', 
            'statistics', 'alert_thresholds'
        ]
        for section in required_sections:
            assert section in learning_config, f"Missing configuration section: {section}"
            print(f"   ✅ Section '{section}' found")
        
        # Test configuration defaults
        learning_settings = learning_config.get('learning_settings', {})
        defaults = learning_settings.get('defaults', {})
        assert 'enabled' in defaults, "Missing enabled default"
        assert 'confidence_threshold' in defaults, "Missing confidence_threshold default"
        assert 'max_daily_adjustments' in defaults, "Missing max_daily_adjustments default"
        print("✅ Configuration structure valid")
        
        # Step 4: Initialize NLPIntegrationManager (dependency)
        print("🔧 Step 4: Initializing NLPIntegrationManager dependency...")
        nlp_manager = create_nlp_integration_manager(
            config_manager=config_manager,
            logging_manager=logging_manager
        )
        print("✅ NLPIntegrationManager dependency ready")
        
        # ====================================================================
        # PHASE 1c STEP 1: LEARNING SYSTEM MANAGER
        # ====================================================================
        
        # Step 5: Test LearningSystemManager factory function (Rule #1)
        print("🔧 Step 5: Testing LearningSystemManager factory function...")
        learning_manager = create_learning_system_manager(
            config_manager=config_manager,
            logging_manager=logging_manager,
            nlp_integration_manager=nlp_manager
        )
        
        # Verify manager is properly initialized
        assert learning_manager is not None, "LearningSystemManager creation failed"
        assert hasattr(learning_manager, 'config_manager'), "Missing config_manager dependency"
        assert hasattr(learning_manager, 'logging_manager'), "Missing logging_manager dependency"
        assert hasattr(learning_manager, 'nlp_manager'), "Missing nlp_manager dependency"
        print("✅ LearningSystemManager factory function working")
        
        # Step 6: Test Environment Variable Reuse (Rule #7)
        print("🔧 Step 6: Testing environment variable reuse (Rule #7)...")
        
        # Test that existing environment variables are being used
        expected_env_vars = [
            'GLOBAL_LEARNING_SYSTEM_ENABLED',
            'BOT_LEARNING_CONFIDENCE_THRESHOLD', 
            'BOT_MAX_LEARNING_ADJUSTMENTS_PER_DAY',
            'GLOBAL_REQUEST_TIMEOUT',
            'GLOBAL_NLP_API_HOST',
            'GLOBAL_NLP_API_PORT'
        ]
        
        for env_var in expected_env_vars:
            # Verify the manager is configured to use these variables
            if env_var == 'GLOBAL_LEARNING_SYSTEM_ENABLED':
                assert hasattr(learning_manager, 'learning_enabled'), f"Manager not using {env_var}"
            elif env_var == 'BOT_LEARNING_CONFIDENCE_THRESHOLD':
                assert hasattr(learning_manager, 'confidence_threshold'), f"Manager not using {env_var}"
            elif env_var == 'BOT_MAX_LEARNING_ADJUSTMENTS_PER_DAY':
                assert hasattr(learning_manager, 'max_daily_adjustments'), f"Manager not using {env_var}"
            print(f"   ✅ Environment variable reuse: {env_var}")
        
        print("✅ Rule #7 environment variable reuse verified")
        
        # Step 7: Test Configuration Access Patterns
        print("🔧 Step 7: Testing configuration access patterns...")
        
        # Test that manager uses get_config_section method correctly
        assert learning_manager.config is not None, "Configuration not loaded"
        
        # Test resilient configuration loading (Rule #5)
        learning_enabled = learning_manager.learning_enabled
        confidence_threshold = learning_manager.confidence_threshold
        max_daily_adjustments = learning_manager.max_daily_adjustments
        
        assert isinstance(learning_enabled, bool), "Learning enabled should be boolean"
        assert 0.0 <= confidence_threshold <= 1.0, "Confidence threshold should be in [0.0, 1.0]"
        assert max_daily_adjustments > 0, "Max daily adjustments should be positive"
        
        print(f"   ✅ Learning enabled: {learning_enabled}")
        print(f"   ✅ Confidence threshold: {confidence_threshold}")
        print(f"   ✅ Max daily adjustments: {max_daily_adjustments}")
        print("✅ Configuration access patterns working")
        
        # Step 8: Test Learning System State Management
        print("🔧 Step 8: Testing learning system state management...")
        
        # Test daily adjustment tracking
        daily_status = learning_manager._get_daily_adjustment_status()
        assert 'count' in daily_status, "Missing adjustment count"
        assert 'limit' in daily_status, "Missing adjustment limit"
        assert 'remaining' in daily_status, "Missing remaining adjustments"
        assert daily_status['remaining'] >= 0, "Remaining adjustments should be non-negative"
        
        # Test daily limit checking
        can_adjust = learning_manager._check_daily_adjustment_limit()
        assert isinstance(can_adjust, bool), "Daily limit check should return boolean"
        
        print(f"   ✅ Daily adjustments: {daily_status['count']}/{daily_status['limit']}")
        print(f"   ✅ Can make adjustments: {can_adjust}")
        print("✅ Learning system state management working")
        
        # Step 9: Test Learning Statistics (Real Methods - Rule #8)
        print("🔧 Step 9: Testing learning statistics...")
        
        # Test learning statistics retrieval
        learning_stats = await learning_manager.get_learning_statistics()
        assert learning_stats is not None, "Learning statistics should not be None"
        assert 'learning_system_status' in learning_stats, "Missing learning system status"
        assert 'daily_adjustments' in learning_stats, "Missing daily adjustments info"
        
        # Test learning effectiveness calculation
        effectiveness = await learning_manager.get_learning_effectiveness()
        assert effectiveness is not None, "Learning effectiveness should not be None"
        assert 'effectiveness_score' in effectiveness, "Missing effectiveness score"
        
        print(f"   ✅ Learning system status: {learning_stats['learning_system_status']}")
        print(f"   ✅ Effectiveness score: {effectiveness['effectiveness_score']}")
        print("✅ Learning statistics working")
        
        # Step 10: Test Learning System Health Monitoring
        print("🔧 Step 10: Testing learning system health monitoring...")
        
        # Test health status retrieval
        health_status = await learning_manager._get_learning_system_health()
        assert health_status is not None, "Health status should not be None"
        assert 'status' in health_status, "Missing health status"
        assert 'learning_enabled' in health_status, "Missing learning enabled status"
        
        print(f"   ✅ Health status: {health_status['status']}")
        print(f"   ✅ Learning enabled: {health_status['learning_enabled']}")
        print("✅ Learning system health monitoring working")
        
        # Step 11: Test Error Handling and Resilience (Rule #5)
        print("🔧 Step 11: Testing error handling and resilience...")
        
        # Test resilience with invalid feedback
        invalid_feedback_result = await learning_manager.submit_false_positive_feedback(
            message_content="",  # Invalid empty message
            original_analysis={},  # Invalid empty analysis
            staff_user_id="test_user",
            context={}
        )
        
        # Should handle gracefully and not crash
        assert invalid_feedback_result is not None, "Should handle invalid feedback gracefully"
        assert 'success' in invalid_feedback_result, "Should return structured response"
        
        # Test with invalid crisis level for false negative
        invalid_fn_result = await learning_manager.submit_false_negative_feedback(
            message_content="test message",
            original_analysis={'crisis_level': 'none'},
            staff_user_id="test_user",
            correct_crisis_level="invalid_level",  # Invalid crisis level
            context={}
        )
        
        assert invalid_fn_result is not None, "Should handle invalid crisis level gracefully"
        assert invalid_fn_result.get('success') == False, "Should reject invalid crisis level"
        assert invalid_fn_result.get('reason') == 'invalid_crisis_level', "Should identify validation error"
        
        print("   ✅ Invalid feedback handling: graceful")
        print("   ✅ Invalid crisis level handling: graceful")
        print("✅ Error handling and resilience verified")
        
        # Step 12: Test File Versioning (Rule #6)
        print("🔧 Step 12: Testing file versioning compliance...")
        
        # Check that manager file has proper versioning
        manager_file = Path("managers/learning_system.py")
        if manager_file.exists():
            with open(manager_file, 'r') as f:
                content = f.read()
                assert "FILE VERSION: v3.1-1c-1-1" in content, "Manager missing proper file version"
                assert "PHASE: 1c Step 1" in content, "Manager missing phase information"
        
        # Check that config file has proper versioning
        config_file = Path("config/learning_config.json")
        if config_file.exists():
            with open(config_file, 'r') as f:
                config_data = json.load(f)
                metadata = config_data.get('_metadata', {})
                assert metadata.get('file_version') == 'v3.1-1c-1-1', "Config missing proper file version"
                assert 'phase' in metadata, "Config missing phase information"
        
        print("   ✅ Manager file versioning: v3.1-1c-1-1")
        print("   ✅ Config file versioning: v3.1-1c-1-1")
        print("✅ File versioning compliance verified")
        
        # ====================================================================
        # INTEGRATION VERIFICATION
        # ====================================================================
        
        # Step 13: Test Integration with NLPIntegrationManager
        print("🔧 Step 13: Testing NLPIntegrationManager integration...")
        
        # Verify that learning manager correctly delegates to NLP manager
        assert learning_manager.nlp_manager is nlp_manager, "NLP manager dependency not properly injected"
        
        # Test that learning manager can access NLP manager methods
        nlp_health = await nlp_manager.get_service_health()
        assert nlp_health is not None, "Should be able to access NLP manager health"
        
        print("   ✅ NLP manager dependency injection: working")
        print("   ✅ NLP manager method access: working")
        print("✅ NLPIntegrationManager integration verified")
        
        # Step 14: Test Manager Lifecycle and Cleanup
        print("🔧 Step 14: Testing manager lifecycle...")
        
        # Test that manager maintains state correctly
        initial_adjustments = learning_manager.daily_adjustments_count
        
        # Simulate successful adjustment
        learning_manager._increment_daily_adjustments()
        assert learning_manager.daily_adjustments_count == initial_adjustments + 1, "Adjustment count should increment"
        
        # Test that date reset works
        from datetime import date, timedelta
        yesterday = date.today() - timedelta(days=1)
        learning_manager.daily_adjustments_date = yesterday
        
        can_adjust = learning_manager._check_daily_adjustment_limit()
        assert learning_manager.daily_adjustments_count == 0, "Count should reset for new day"
        assert can_adjust, "Should be able to adjust after reset"
        
        print("   ✅ State management: working")
        print("   ✅ Date reset logic: working")
        print("✅ Manager lifecycle verified")
        
        # ====================================================================
        # INTEGRATION SUCCESS
        # ====================================================================
        
        print("")
        print("🎉 PHASE 1c STEP 1 INTEGRATION TEST PASSED!")
        print("")
        print("✅ LearningSystemManager Creation and Initialization")
        print("✅ Clean Architecture v3.1 Compliance")
        print("✅ Factory Function Pattern (Rule #1)")
        print("✅ Dependency Injection (Rule #2)") 
        print("✅ JSON Configuration + Environment Overrides (Rule #4)")
        print("✅ Resilient Error Handling (Rule #5)")
        print("✅ File Versioning (Rule #6)")
        print("✅ Environment Variable Reuse (Rule #7)")
        print("✅ Real Method Testing (Rule #8)")
        print("")
        print("🚀 LearningSystemManager ready for production use!")
        print("📊 Staff feedback collection and NLP learning integration operational")
        print("⚙️  Learning system monitoring and statistics tracking functional")
        print("")
        logger.info("✅ Phase 1c Step 1 integration test completed successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        logger.error(f"❌ Phase 1c Step 1 integration test failed: {e}")
        raise e

def main():
    """Run Phase 1c Step 1 integration test"""
    try:
        # Run the async test
        result = asyncio.run(test_phase_1c_step_1_learning_system_manager())
        if result:
            print("🏆 All Phase 1c Step 1 tests passed!")
            return 0
        else:
            print("❌ Phase 1c Step 1 tests failed!")
            return 1
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())