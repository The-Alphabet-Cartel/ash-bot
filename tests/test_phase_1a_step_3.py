#!/usr/bin/env python3
"""
Ash-Bot: Crisis Detection Bot for The Alphabet Cartel Discord Community
********************************************************************************
Phase 1a Step 3 Integration Test - Crisis Analysis Manager
---
FILE VERSION: v3.1-1a-3-2
LAST MODIFIED: 2025-09-05
PHASE: 1a Step 3 Test
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
from unittest.mock import AsyncMock, MagicMock

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import managers using factory functions (Rule #1)
from managers.unified_config import create_unified_config_manager
from managers.logging_config import create_logging_config_manager
from managers.crisis_analysis import create_crisis_analysis_manager, CrisisLevel

async def test_crisis_analysis_manager():
    """
    Test Phase 1a Step 3: CrisisAnalysisManager
    Following Rule #8: Real-world testing with actual methods
    """
    
    print("🧪 Starting Phase 1a Step 3 Integration Test")
    print("📋 Testing: CrisisAnalysisManager with Clean Architecture v3.1")
    print("🎯 Focus: NLP response mapping (NLP server does ALL analysis)")
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
        logger.info("🔬 Phase 1a Step 3 testing started")
        
        # Step 3: Test JSON configuration loading
        print("🔧 Step 3: Testing crisis_config.json loading...")
        crisis_config = config_manager.get_config_section('crisis_config')
        assert crisis_config is not None, "crisis_config.json not loaded"
        
        # Test configuration sections exist
        required_sections = ['response_mapping', 'staff_notification', 'integration']
        for section in required_sections:
            assert section in crisis_config, f"Required section '{section}' missing from crisis_config.json"
        
        print("✅ crisis_config.json loaded successfully")
        logger.info("📄 crisis_config.json validation successful")
        
        # Step 4: Create mock NLP manager for testing
        print("🔧 Step 4: Creating mock NLP manager for testing...")
        mock_nlp_manager = MagicMock()
        mock_nlp_manager.analyze_message = AsyncMock()
        
        print("✅ Mock NLP manager created")
        
        # Step 5: Test factory function (Rule #1)
        print("🔧 Step 5: Testing CrisisAnalysisManager factory function...")
        crisis_manager = create_crisis_analysis_manager(
            config_manager=config_manager,
            logging_manager=logging_manager,
            nlp_manager=mock_nlp_manager
        )
        assert crisis_manager is not None, "CrisisAnalysisManager factory failed"
        assert hasattr(crisis_manager, 'config_manager'), "CrisisAnalysisManager missing config_manager"
        assert hasattr(crisis_manager, 'logging_manager'), "CrisisAnalysisManager missing logging_manager"
        assert hasattr(crisis_manager, 'nlp_manager'), "CrisisAnalysisManager missing nlp_manager"
        
        print("✅ Factory function working correctly")
        logger.info("🏭 Factory function validation successful")
        
        # Step 6: Test get_config_section() method usage (critical requirement)
        print("🔧 Step 6: Testing configuration access patterns...")
        
        # Test staff notification settings
        crisis_channel_id = config_manager.get_config_section('crisis_config', 'staff_notification.crisis_response.channel_id', None)
        override_levels = config_manager.get_config_section('crisis_config', 'response_mapping.staff_notification_triggers.crisis_override_levels', 'medium,high')
        gap_notifications = config_manager.get_config_section('crisis_config', 'response_mapping.staff_notification_triggers.gaps_detected', True)
        
        # Verify manager uses correct configuration values
        assert isinstance(override_levels, str), f"Override levels should be string, got {type(override_levels)}"
        assert isinstance(gap_notifications, bool), f"Gap notifications should be bool, got {type(gap_notifications)}"
        
        # Test override levels parsing
        parsed_levels = set(level.strip().lower() for level in override_levels.split(',') if level.strip())
        assert 'medium' in parsed_levels or 'high' in parsed_levels, "Override levels should contain medium or high"
        
        print("✅ Configuration access patterns working")
        logger.info("⚙️ Configuration validation successful")
        
        # Step 7: Test Rule #7 compliance - Environment variable reuse
        print("🔧 Step 7: Testing Rule #7 environment variable mapping...")
        
        # Verify manager uses correct configuration values
        assert crisis_manager.override_levels == parsed_levels, f"Manager override levels mismatch"
        assert crisis_manager.gap_notifications_enabled == gap_notifications, f"Manager gap notifications mismatch"
        
        print("✅ Rule #7 environment variable mapping confirmed")
        logger.info("🔄 Environment variable reuse validation successful")
        
        # Step 8: Test NLP response mapping - NO CRISIS
        print("🔧 Step 8: Testing NLP response mapping - NO CRISIS...")
        
        # Mock NLP response: no crisis
        mock_nlp_response_none = {
            'needs_response': False,
            'crisis_level': 'none',
            'confidence_score': 0.1,
            'detected_categories': [],
            'requires_staff_review': False,
            'gaps_detected': False,
            'reasoning': 'No crisis indicators detected'
        }
        
        mock_nlp_manager.analyze_message.return_value = mock_nlp_response_none
        result = await crisis_manager.analyze_message("Hello, how are you?", 12345, 67890)
        
        assert result.crisis_level == CrisisLevel.NONE, "Should map to NONE crisis level"
        assert result.requires_response == False, "Should not require response"
        assert result.requires_staff_notification == False, "Should not require staff notification"
        assert result.gaps_detected == False, "Should not have gaps detected"
        
        print("✅ NO CRISIS mapping working correctly")
        logger.info("❌ No crisis mapping validation successful")
        
        # Step 9: Test NLP response mapping - LOW CRISIS
        print("🔧 Step 9: Testing NLP response mapping - LOW CRISIS...")
        
        mock_nlp_response_low = {
            'needs_response': True,
            'crisis_level': 'low',
            'confidence_score': 0.4,
            'detected_categories': ['anxiety'],
            'requires_staff_review': False,
            'gaps_detected': False,
            'reasoning': 'Low-level anxiety indicators detected'
        }
        
        mock_nlp_manager.analyze_message.return_value = mock_nlp_response_low
        result = await crisis_manager.analyze_message("I'm feeling anxious today", 12345, 67890)
        
        assert result.crisis_level == CrisisLevel.LOW, "Should map to LOW crisis level"
        assert result.requires_response == True, "Should require response"
        assert result.requires_staff_notification == False, "Low level should not notify staff by default"
        assert result.detected_categories == ['anxiety'], "Should preserve detected categories"
        
        print("✅ LOW CRISIS mapping working correctly")
        logger.info("🟡 Low crisis mapping validation successful")
        
        # Step 10: Test NLP response mapping - MEDIUM CRISIS with staff notification
        print("🔧 Step 10: Testing NLP response mapping - MEDIUM CRISIS...")
        
        mock_nlp_response_medium = {
            'needs_response': True,
            'crisis_level': 'medium',
            'confidence_score': 0.7,
            'detected_categories': ['depression', 'self_harm'],
            'requires_staff_review': False,
            'gaps_detected': False,
            'reasoning': 'Moderate depression and self-harm indicators'
        }
        
        mock_nlp_manager.analyze_message.return_value = mock_nlp_response_medium
        result = await crisis_manager.analyze_message("I feel hopeless and want to hurt myself", 12345, 67890)
        
        assert result.crisis_level == CrisisLevel.MEDIUM, "Should map to MEDIUM crisis level"
        assert result.requires_response == True, "Should require response"
        assert result.requires_staff_notification == True, "Medium is in override levels - should notify staff"
        assert 'depression' in result.detected_categories, "Should preserve detected categories"
        
        print("✅ MEDIUM CRISIS mapping working correctly")
        logger.info("🟠 Medium crisis mapping validation successful")
        
        # Step 11: Test NLP response mapping - HIGH CRISIS
        print("🔧 Step 11: Testing NLP response mapping - HIGH CRISIS...")
        
        mock_nlp_response_high = {
            'needs_response': True,
            'crisis_level': 'high',
            'confidence_score': 0.95,
            'detected_categories': ['suicidal_ideation'],
            'requires_staff_review': True,
            'gaps_detected': False,
            'reasoning': 'Explicit suicidal ideation detected'
        }
        
        mock_nlp_manager.analyze_message.return_value = mock_nlp_response_high
        result = await crisis_manager.analyze_message("I want to kill myself tonight", 12345, 67890)
        
        assert result.crisis_level == CrisisLevel.HIGH, "Should map to HIGH crisis level"
        assert result.requires_response == True, "Should require response"
        assert result.requires_staff_notification == True, "High crisis should always notify staff"
        assert result.requires_staff_review == True, "Should preserve staff review requirement"
        
        print("✅ HIGH CRISIS mapping working correctly")
        logger.info("🔴 High crisis mapping validation successful")
        
        # Step 12: Test gap detection and staff notification
        print("🔧 Step 12: Testing gap detection and staff notification...")
        
        mock_nlp_response_gaps = {
            'needs_response': True,
            'crisis_level': 'low',
            'confidence_score': 0.3,
            'detected_categories': ['anxiety'],
            'requires_staff_review': False,
            'gaps_detected': True,  # Models disagreed
            'reasoning': 'Model disagreement detected - low confidence'
        }
        
        mock_nlp_manager.analyze_message.return_value = mock_nlp_response_gaps
        result = await crisis_manager.analyze_message("I'm not sure how I feel", 12345, 67890)
        
        assert result.crisis_level == CrisisLevel.LOW, "Should map to LOW crisis level"
        assert result.gaps_detected == True, "Should preserve gaps detected"
        assert result.requires_staff_notification == True, "Gaps detected should trigger staff notification"
        
        print("✅ Gap detection and staff notification working")
        logger.info("🔍 Gap detection validation successful")
        
        # Step 13: Test staff review requirement
        print("🔧 Step 13: Testing staff review requirement...")
        
        mock_nlp_response_review = {
            'needs_response': True,
            'crisis_level': 'low',
            'confidence_score': 0.4,
            'detected_categories': ['anxiety'],
            'requires_staff_review': True,  # NLP server requests staff review
            'gaps_detected': False,
            'reasoning': 'Uncertain analysis - staff review recommended'
        }
        
        mock_nlp_manager.analyze_message.return_value = mock_nlp_response_review
        result = await crisis_manager.analyze_message("I'm struggling", 12345, 67890)
        
        assert result.requires_staff_review == True, "Should preserve staff review requirement"
        assert result.requires_staff_notification == True, "Staff review should trigger notification"
        
        print("✅ Staff review requirement working")
        logger.info("👥 Staff review validation successful")
        
        # Step 14: Test error handling - NLP manager returns None
        print("🔧 Step 14: Testing error handling...")
        
        mock_nlp_manager.analyze_message.return_value = None
        result = await crisis_manager.analyze_message("Test message", 12345, 67890)
        
        assert result.crisis_level == CrisisLevel.NONE, "Should default to NONE on NLP error"
        assert result.requires_response == False, "Should not require response on error"
        assert result.requires_staff_notification == False, "Should not notify staff on NLP error"
        assert "NLP analysis failed" in result.reasoning, "Should indicate NLP failure"
        
        print("✅ Error handling working correctly")
        logger.info("🛡️ Error handling validation successful")
        
        # Step 15: Test statistics tracking
        print("🔧 Step 15: Testing statistics tracking...")
        
        stats = crisis_manager.get_analysis_stats()
        assert isinstance(stats, dict), "Stats should be dictionary"
        assert 'manager_info' in stats, "Should have manager info"
        assert 'statistics' in stats, "Should have statistics"
        assert stats['statistics']['total_analyses'] > 0, "Should track total analyses"
        
        # Test health status
        health = crisis_manager.get_health_status()
        assert isinstance(health, dict), "Health should be dictionary"
        assert health['manager_healthy'] == True, "Manager should be healthy"
        assert health['nlp_integration'] == True, "Should show NLP integration"
        
        print("✅ Statistics and health tracking working")
        logger.info("📊 Statistics validation successful")
        
        # Step 16: Test manager integration points
        print("🔧 Step 16: Testing manager integration points...")
        
        # Test configuration manager integration
        assert crisis_manager.config_manager is config_manager, "Config manager reference should match"
        assert crisis_manager.logging_manager is logging_manager, "Logging manager reference should match"
        assert crisis_manager.nlp_manager is mock_nlp_manager, "NLP manager reference should match"
        
        # Test configuration loading
        assert len(crisis_manager.override_levels) > 0, "Should have override levels configured"
        assert isinstance(crisis_manager.gap_notifications_enabled, bool), "Gap notifications should be boolean"
        
        print("✅ Manager integration points working")
        logger.info("🔧 Manager integration validation successful")
        
        # Final validation
        print("")
        print("🎉 Phase 1a Step 3 Integration Test PASSED")
        print("✅ CrisisAnalysisManager fully functional")
        print("✅ Clean Architecture v3.1 compliance verified")
        print("✅ Rule #7 environment variable mapping confirmed")
        print("✅ Factory function pattern working")
        print("✅ JSON configuration loading successful")
        print("✅ NLP response mapping operational")
        print("✅ Staff notification logic functional")
        print("✅ Gap detection handling working")
        print("✅ Error handling resilient")
        print("✅ Simplified design: NLP server does ALL analysis")
        
        logger.info("🎉 Phase 1a Step 3 testing completed successfully")
        logger.info("📊 All integration tests passed")
        logger.info("🎯 Crisis analysis manager ready for Phase 1b integration")
        
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
    """Run the Phase 1a Step 3 integration test"""
    print("=" * 70)
    print("ASH-BOT PHASE 1a STEP 3 INTEGRATION TEST")
    print("Clean Architecture v3.1 - Crisis Analysis Manager")
    print("The Alphabet Cartel - https://discord.gg/alphabetcartel")
    print("=" * 70)
    print("")
    
    # Run the test
    success = asyncio.run(test_crisis_analysis_manager())
    
    if success:
        print("")
        print("=" * 70)
        print("🎉 PHASE 1a STEP 3 COMPLETE!")
        print("🏆 PHASE 1a FOUNDATION MANAGERS COMPLETE!")
        print("Ready to proceed to Phase 1b: Response Managers")
        print("=" * 70)
        sys.exit(0)
    else:
        print("")
        print("=" * 70)
        print("❌ PHASE 1a STEP 3 FAILED!")
        print("Please review errors and fix before proceeding")
        print("=" * 70)
        sys.exit(1)

if __name__ == "__main__":
    main()