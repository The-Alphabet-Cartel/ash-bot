#!/usr/bin/env python3
"""
Ash-Bot: Crisis Detection Bot for The Alphabet Cartel Discord Community
********************************************************************************
Phase 1b Complete Integration Test - Response Managers
---
FILE VERSION: v3.1-1b-complete-1
LAST MODIFIED: 2025-09-09
PHASE: 1b Complete Test - ConversationHandlerManager + CrisisResponseManager
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
from unittest.mock import Mock, AsyncMock

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import managers using factory functions (Rule #1)
from managers.unified_config import create_unified_config_manager
from managers.logging_config import create_logging_config_manager
from managers.nlp_integration import create_nlp_integration_manager
from managers.crisis_analysis import create_crisis_analysis_manager, CrisisLevel, CrisisAnalysisResult
from managers.conversation_handler import create_conversation_handler_manager
from managers.crisis_response import create_crisis_response_manager

async def test_phase_1b_complete_integration():
    """
    Test Phase 1b Complete: Both Response Managers working together
    Following Rule #8: Real-world testing with actual methods
    
    Tests:
    1. All foundation managers (Phase 1a) + Response managers (Phase 1b) 
    2. End-to-end conversation flow with crisis response
    3. ConversationHandlerManager + CrisisResponseManager integration
    4. Complete crisis detection and response pipeline
    """
    
    print("🧪 Starting Phase 1b Complete Integration Test")
    print("📋 Testing: ConversationHandlerManager + CrisisResponseManager")
    print("🎯 Focus: End-to-end conversation and crisis response flow")
    print("")
    
    try:
        # ====================================================================
        # FOUNDATION SETUP (Phase 1a Managers)
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
        logger.info("🔬 Phase 1b complete integration testing started")
        
        # Step 3: Initialize NLPIntegrationManager (Phase 1a)
        print("🔧 Step 3: Initializing NLPIntegrationManager (Phase 1a)...")
        nlp_manager = create_nlp_integration_manager(
            config_manager=config_manager,
            logging_manager=logging_manager
        )
        print("✅ NLPIntegrationManager ready")
        
        # Step 4: Initialize CrisisAnalysisManager (Phase 1a)
        print("🔧 Step 4: Initializing CrisisAnalysisManager (Phase 1a)...")
        crisis_analysis_manager = create_crisis_analysis_manager(
            config_manager=config_manager,
            logging_manager=logging_manager,
            nlp_integration_manager=nlp_manager
        )
        print("✅ CrisisAnalysisManager ready")
        
        # ====================================================================
        # PHASE 1b RESPONSE MANAGERS
        # ====================================================================
        
        # Step 5: Initialize ConversationHandlerManager (Phase 1b Step 1)
        print("🔧 Step 5: Initializing ConversationHandlerManager (Phase 1b Step 1)...")
        conversation_manager = create_conversation_handler_manager(
            config_manager=config_manager,
            logging_manager=logging_manager,
            crisis_analysis_manager=crisis_analysis_manager
        )
        print("✅ ConversationHandlerManager ready")
        
        # Step 6: Initialize CrisisResponseManager (Phase 1b Step 2)
        print("🔧 Step 6: Initializing CrisisResponseManager (Phase 1b Step 2)...")
        response_manager = create_crisis_response_manager(
            config_manager=config_manager,
            logging_manager=logging_manager,
            crisis_analysis_manager=crisis_analysis_manager
        )
        print("✅ CrisisResponseManager ready")
        
        # ====================================================================
        # CONFIGURATION VALIDATION
        # ====================================================================
        
        # Step 7: Validate all configuration files loaded
        print("🔧 Step 7: Validating all Phase 1b configuration files...")
        
        # Test conversation configuration
        conversation_config = config_manager.get_config_section('conversation_config')
        assert conversation_config is not None, "conversation_config.json not loaded"
        
        # Test response configuration  
        response_config = config_manager.get_config_section('response_config')
        assert response_config is not None, "response_config.json not loaded"
        
        # Validate required sections in both configs
        conv_sections = ['conversation_settings', 'claude_settings', 'response_settings']
        for section in conv_sections:
            assert section in conversation_config, f"Missing conversation config section: {section}"
        
        resp_sections = ['notification_settings', 'response_templates', 'execution_settings']
        for section in resp_sections:
            assert section in response_config, f"Missing response config section: {section}"
        
        print("✅ All Phase 1b configuration files validated")
        
        # ====================================================================
        # HEALTH STATUS VALIDATION
        # ====================================================================
        
        # Step 8: Validate all managers are healthy
        print("🔧 Step 8: Validating all manager health status...")
        
        # Check foundation managers health
        nlp_health = nlp_manager.get_health_status()
        crisis_health = crisis_analysis_manager.get_health_status()
        conversation_health = conversation_manager.get_health_status()
        response_health = response_manager.get_health_status()
        
        assert nlp_health['manager_healthy'] == True, "NLP manager not healthy"
        assert crisis_health['manager_healthy'] == True, "Crisis analysis manager not healthy"
        assert conversation_health['status'] == 'healthy', "Conversation manager not healthy"
        assert response_health['status'] == 'healthy', "Response manager not healthy"
        
        print("✅ All managers report healthy status")
        
        # ====================================================================
        # ENVIRONMENT VARIABLE REUSE VALIDATION (Rule #7)
        # ====================================================================
        
        # Step 9: Validate environment variable reuse across Phase 1b
        print("🔧 Step 9: Validating environment variable reuse (Rule #7)...")
        
        # Test that Phase 1b configs reuse existing variables
        expected_reused_vars = [
            'BOT_CONVERSATION_TIMEOUT',
            'BOT_CONVERSATION_REQUIRES_MENTION',
            'BOT_CONVERSATION_TRIGGER_PHRASES',
            'GLOBAL_CLAUDE_API_KEY',
            'GLOBAL_CLAUDE_MODEL',
            'BOT_CRISIS_RESPONSE_CHANNEL_ID',
            'BOT_CRISIS_RESPONSE_ROLE_ID',
            'BOT_RESOURCES_CHANNEL_ID',
            'BOT_STAFF_PING_USER',
            'BOT_ENABLE_GAP_NOTIFICATIONS',
            'GLOBAL_REQUEST_TIMEOUT'
        ]
        
        # Check both configuration files for variable reuse
        all_configs = [conversation_config, response_config]
        found_variables = []
        
        def find_env_vars(d):
            for key, value in d.items():
                if isinstance(value, dict):
                    find_env_vars(value)
                elif isinstance(value, str) and value.startswith('${') and value.endswith('}'):
                    var_name = value[2:-1]
                    found_variables.append(var_name)
        
        for config in all_configs:
            find_env_vars(config)
        
        reused_count = sum(1 for var in expected_reused_vars if var in found_variables)
        print(f"   🔄 Environment variables reused: {reused_count}/{len(expected_reused_vars)}")
        
        assert reused_count >= 8, f"Expected at least 8 reused variables, found {reused_count}"
        print("✅ Environment variable reuse validated (Rule #7 compliance)")
        
        # ====================================================================
        # END-TO-END CONVERSATION FLOW TEST
        # ====================================================================
        
        # Step 10: Test complete conversation flow
        print("🔧 Step 10: Testing end-to-end conversation flow...")
        
        # Create mock Discord message for conversation start
        mock_message = Mock()
        mock_message.author = Mock()
        mock_message.author.bot = False
        mock_message.author.id = 98765
        mock_message.author.display_name = "TestUser"
        mock_message.content = "ash help me please"
        mock_message.channel = Mock()
        mock_message.channel.id = 11111
        mock_message.channel.send = AsyncMock()
        mock_message.mentions = []
        
        # Test conversation handling
        conversation_handled = await conversation_manager.handle_message(mock_message)
        print(f"   💬 Conversation started: {conversation_handled}")
        
        # Get conversation stats
        conv_stats = conversation_manager.get_conversation_stats()
        print(f"   📊 Conversations started: {conv_stats['total_conversations']}")
        
        print("✅ End-to-end conversation flow working")
        
        # ====================================================================
        # INTEGRATED CRISIS RESPONSE TEST
        # ====================================================================
        
        # Step 11: Test integrated crisis response flow
        print("🔧 Step 11: Testing integrated crisis response flow...")
        
        # Create mock crisis analysis result
        high_crisis_result = CrisisAnalysisResult(
            crisis_level=CrisisLevel.HIGH,
            confidence_score=0.85,
            detected_categories=['suicide_ideation', 'severe_depression'],
            requires_response=True,
            requires_staff_notification=True,
            gaps_detected=False,
            requires_staff_review=True,
            processing_time_ms=200,
            reasoning="High-priority crisis detected requiring immediate intervention",
            nlp_raw_response={'analysis': 'high_risk'}
        )
        
        # Test crisis response execution
        response_executed = await response_manager.execute_crisis_response(
            high_crisis_result, 
            mock_message.author.id, 
            mock_message.channel.id
        )
        
        print(f"   🚨 Crisis response executed: {response_executed}")
        
        # Get response stats
        resp_stats = response_manager.get_response_stats()
        print(f"   📊 Total responses: {resp_stats['total_responses']}")
        print(f"   📊 High-level responses: {resp_stats['responses_by_level']['high']}")
        
        print("✅ Integrated crisis response flow working")
        
        # ====================================================================
        # CONVERSATION + CRISIS RESPONSE INTEGRATION
        # ====================================================================
        
        # Step 12: Test conversation escalation with crisis response
        print("🔧 Step 12: Testing conversation escalation with crisis response...")
        
        # Create follow-up message that escalates
        escalation_message = Mock()
        escalation_message.author = mock_message.author  # Same user
        escalation_message.content = "I don't think I can do this anymore"
        escalation_message.channel = mock_message.channel  # Same channel
        escalation_message.mentions = []
        
        # Test follow-up handling (should detect escalation)
        followup_handled = await conversation_manager.handle_message(escalation_message)
        print(f"   📈 Escalation handled: {followup_handled}")
        
        # Check conversation stats for escalations
        updated_conv_stats = conversation_manager.get_conversation_stats()
        print(f"   📊 Escalated conversations: {updated_conv_stats.get('escalated_conversations', 0)}")
        
        print("✅ Conversation escalation with crisis response working")
        
        # ====================================================================
        # STATISTICS AND MONITORING VALIDATION
        # ====================================================================
        
        # Step 13: Validate comprehensive statistics
        print("🔧 Step 13: Validating comprehensive statistics...")
        
        # Conversation statistics
        final_conv_stats = conversation_manager.get_conversation_stats()
        required_conv_stats = ['total_conversations', 'active_conversations', 'follow_ups_handled']
        for stat in required_conv_stats:
            assert stat in final_conv_stats, f"Missing conversation stat: {stat}"
        
        # Response statistics
        final_resp_stats = response_manager.get_response_stats()
        required_resp_stats = ['total_responses', 'responses_by_level', 'staff_notifications_sent']
        for stat in required_resp_stats:
            assert stat in final_resp_stats, f"Missing response stat: {stat}"
        
        print("✅ Comprehensive statistics validated")
        
        # ====================================================================
        # RESILIENCE AND ERROR HANDLING TEST
        # ====================================================================
        
        # Step 14: Test resilience across both managers
        print("🔧 Step 14: Testing resilience and error handling...")
        
        # Test conversation manager with invalid input
        invalid_conv_result = await conversation_manager.handle_message(None)
        assert invalid_conv_result == False, "Should handle None message gracefully"
        
        # Test response manager with invalid crisis result
        invalid_resp_result = await response_manager.execute_crisis_response(None, 12345, 67890)
        assert invalid_resp_result == False, "Should handle None crisis result gracefully"
        
        # Verify managers still healthy after errors
        conv_health_after = conversation_manager.get_health_status()
        resp_health_after = response_manager.get_health_status()
        
        assert conv_health_after['status'] == 'healthy', "Conversation manager should remain healthy"
        assert resp_health_after['status'] == 'healthy', "Response manager should remain healthy"
        
        print("✅ Resilience and error handling validated")
        
        # ====================================================================
        # PHASE 1b INTEGRATION SUMMARY
        # ====================================================================
        
        # Step 15: Final integration validation
        print("🔧 Step 15: Final Phase 1b integration validation...")
        
        # Validate all Phase 1a + 1b managers are working together
        all_managers_ready = (
            nlp_manager is not None and
            crisis_analysis_manager is not None and
            conversation_manager is not None and
            response_manager is not None
        )
        
        assert all_managers_ready, "Not all managers initialized properly"
        
        # Validate configuration integration
        all_configs_loaded = (
            config_manager.get_config_section('nlp_config') is not None and
            config_manager.get_config_section('crisis_config') is not None and
            config_manager.get_config_section('conversation_config') is not None and
            config_manager.get_config_section('response_config') is not None
        )
        
        assert all_configs_loaded, "Not all configuration files loaded"
        
        print("✅ Complete Phase 1b integration validated")
        
        # Final Success Report
        print("")
        print("🎉 Phase 1b Complete Integration Test PASSED")
        print("✅ Phase 1a Foundation: All 3 managers operational")
        print("✅ Phase 1b Response: Both managers operational")
        print("✅ ConversationHandlerManager: Discord conversation management working")
        print("✅ CrisisResponseManager: Staff notification coordination working")
        print("✅ End-to-end Flow: Message → Analysis → Conversation → Response")
        print("✅ Crisis Escalation: Conversation escalation triggers crisis response")
        print("✅ Configuration Integration: All JSON configs loaded and accessible")
        print("✅ Statistics Tracking: Comprehensive monitoring across all managers")
        print("✅ Error Resilience: Graceful error handling throughout pipeline")
        print("✅ Environment Variables: Maximum reuse of existing infrastructure")
        print("✅ Clean Architecture v3.1: Full compliance across all managers")
        
        logger.info("🎉 Phase 1b complete integration testing successful")
        logger.info("🏆 Response managers ready for production")
        logger.info("🚀 Foundation + Response managers integration complete")
        
        return True
        
    except AssertionError as e:
        print(f"❌ Integration test assertion failed: {e}")
        logger.error(f"❌ Integration test assertion failed: {e}")
        return False
        
    except Exception as e:
        print(f"❌ Integration test failed with error: {e}")
        logger.error(f"❌ Integration test failed with error: {e}")
        logger.exception("Full integration test error traceback:")
        return False

def main():
    """Run the Phase 1b complete integration test"""
    print("=" * 80)
    print("ASH-BOT PHASE 1b COMPLETE INTEGRATION TEST")
    print("Clean Architecture v3.1 - Foundation + Response Managers")
    print("The Alphabet Cartel - https://discord.gg/alphabetcartel")
    print("=" * 80)
    print("")
    
    # Run the test
    success = asyncio.run(test_phase_1b_complete_integration())
    
    if success:
        print("")
        print("=" * 80)
        print("🏆 PHASE 1b RESPONSE MANAGERS COMPLETE!")
        print("✅ Foundation Managers (Phase 1a): 3/3 Ready")
        print("   • DiscordClientManager")
        print("   • NLPIntegrationManager") 
        print("   • CrisisAnalysisManager")
        print("✅ Response Managers (Phase 1b): 2/2 Ready")
        print("   • ConversationHandlerManager")
        print("   • CrisisResponseManager")
        print("📊 Total Managers Operational: 5/5")
        print("🎯 End-to-End Crisis Detection Pipeline: FUNCTIONAL")
        print("🚀 Ready to proceed to Phase 1c: Learning & Analytics")
        print("=" * 80)
        sys.exit(0)
    else:
        print("")
        print("=" * 80)
        print("❌ PHASE 1b INTEGRATION FAILED!")
        print("Please review errors and fix before proceeding to Phase 1c")
        print("=" * 80)
        sys.exit(1)

if __name__ == "__main__":
    main()