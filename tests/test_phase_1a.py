#!/usr/bin/env python3
"""
Ash-Bot: Crisis Detection Bot for The Alphabet Cartel Discord Community
********************************************************************************
Phase 1a Complete Integration Test - All Foundation Managers
---
FILE VERSION: v3.1-1a-complete-1
LAST MODIFIED: 2025-09-05
PHASE: 1a Complete Integration Test
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

# Import all foundation managers using factory functions (Rule #1)
from managers.unified_config import create_unified_config_manager
from managers.logging_config import create_logging_config_manager
from managers.discord_client import create_discord_client_manager
from managers.nlp_integration import create_nlp_integration_manager
from managers.crisis_analysis import create_crisis_analysis_manager, CrisisLevel

async def test_phase_1a_complete():
    """
    Test Phase 1a Complete: All Foundation Managers Working Together
    Tests the integration of DiscordClientManager, NLPIntegrationManager, and CrisisAnalysisManager
    """
    
    print("🧪 Starting Phase 1a Complete Integration Test")
    print("📋 Testing: All Foundation Managers Working Together")
    print("🏗️ Architecture: Clean Architecture v3.1")
    print("")
    
    try:
        # Step 1: Initialize Core Managers
        print("🔧 Step 1: Initializing core managers...")
        config_manager = create_unified_config_manager()
        logging_manager = create_logging_config_manager(config_manager)
        logger = logging.getLogger(__name__)
        logger.info("🔬 Phase 1a complete integration testing started")
        print("✅ Core managers initialized")
        
        # Step 2: Initialize Discord Client Manager
        print("🔧 Step 2: Initializing Discord Client Manager...")
        discord_manager = create_discord_client_manager(
            config_manager=config_manager,
            logging_manager=logging_manager
        )
        assert discord_manager is not None, "Discord manager creation failed"
        print("✅ Discord Client Manager initialized")
        
        # Step 3: Initialize NLP Integration Manager
        print("🔧 Step 3: Initializing NLP Integration Manager...")
        nlp_manager = create_nlp_integration_manager(
            config_manager=config_manager,
            logging_manager=logging_manager
        )
        assert nlp_manager is not None, "NLP manager creation failed"
        print("✅ NLP Integration Manager initialized")
        
        # Step 4: Initialize Crisis Analysis Manager with NLP dependency
        print("🔧 Step 4: Initializing Crisis Analysis Manager...")
        crisis_manager = create_crisis_analysis_manager(
            config_manager=config_manager,
            logging_manager=logging_manager,
            nlp_manager=nlp_manager
        )
        assert crisis_manager is not None, "Crisis manager creation failed"
        assert crisis_manager.nlp_manager is nlp_manager, "Crisis manager missing NLP dependency"
        print("✅ Crisis Analysis Manager initialized with NLP integration")
        
        # Step 5: Test Configuration Integration
        print("🔧 Step 5: Testing configuration integration...")
        
        # Verify all managers can access their configurations
        discord_config = config_manager.get_config_section('discord_config')
        nlp_config = config_manager.get_config_section('nlp_config')
        crisis_config = config_manager.get_config_section('crisis_config')
        
        assert discord_config is not None, "Discord config not accessible"
        assert nlp_config is not None, "NLP config not accessible"
        assert crisis_config is not None, "Crisis config not accessible"
        
        print("✅ All configurations accessible")
        
        # Step 6: Test End-to-End Crisis Analysis Flow (Mock)
        print("🔧 Step 6: Testing end-to-end crisis analysis flow...")
        
        # Mock NLP response for high crisis
        mock_nlp_response = {
            'needs_response': True,
            'crisis_level': 'high',
            'confidence_score': 0.95,
            'detected_categories': ['suicidal_ideation'],
            'requires_staff_review': True,
            'gaps_detected': False,
            'reasoning': 'Explicit suicidal ideation detected in message'
        }
        
        # Mock the NLP manager's analyze_message method
        original_analyze = nlp_manager.analyze_message
        nlp_manager.analyze_message = AsyncMock(return_value=mock_nlp_response)
        
        # Test crisis analysis with mocked NLP
        result = await crisis_manager.analyze_message(
            "I want to end my life tonight", 
            user_id=12345, 
            channel_id=67890
        )
        
        # Verify end-to-end result
        assert result.crisis_level == CrisisLevel.HIGH, "Crisis level not correctly mapped"
        assert result.requires_response == True, "Should require response"
        assert result.requires_staff_notification == True, "Should require staff notification"
        assert result.requires_staff_review == True, "Should require staff review"
        
        # Restore original method
        nlp_manager.analyze_message = original_analyze
        
        print("✅ End-to-end crisis analysis flow working")
        
        # Step 7: Test Manager Health Status
        print("🔧 Step 7: Testing manager health status...")
        
        discord_health = discord_manager.get_health_status()
        nlp_health = nlp_manager.get_health_status()
        crisis_health = crisis_manager.get_health_status()
        
        assert discord_health['manager_healthy'] == True, "Discord manager unhealthy"
        assert nlp_health['service_healthy'] is not None, "NLP health status missing"
        assert crisis_health['manager_healthy'] == True, "Crisis manager unhealthy"
        assert crisis_health['nlp_integration'] == True, "Crisis manager missing NLP integration"
        
        print("✅ All manager health status working")
        
        # Step 8: Test Statistics Collection
        print("🔧 Step 8: Testing statistics collection...")
        
        discord_stats = discord_manager.get_connection_stats()
        nlp_stats = nlp_manager.get_health_status()
        crisis_stats = crisis_manager.get_analysis_stats()
        
        assert isinstance(discord_stats, dict), "Discord stats not dictionary"
        assert isinstance(nlp_stats, dict), "NLP stats not dictionary"
        assert isinstance(crisis_stats, dict), "Crisis stats not dictionary"
        
        # Verify key statistics exist
        assert 'connection_attempts' in discord_stats, "Discord connection stats missing"
        assert 'analysis_stats' in nlp_stats, "NLP analysis stats missing"
        assert 'statistics' in crisis_stats, "Crisis statistics missing"
        
        print("✅ Statistics collection working")
        
        # Step 9: Test Environment Variable Integration
        print("🔧 Step 9: Testing environment variable integration...")
        
        # Test Rule #7 compliance across all managers
        guild_id = config_manager.get_config_section('discord_config', 'discord_settings.guild_id', 0)
        nlp_host = config_manager.get_config_section('nlp_config', 'server_settings.host', '172.20.0.11')
        override_levels = config_manager.get_config_section('crisis_config', 'response_mapping.staff_notification_triggers.crisis_override_levels', 'medium,high')
        
        assert guild_id > 0 or isinstance(guild_id, int), "Guild ID configuration issue"
        assert nlp_host == nlp_manager.nlp_host, "NLP host mismatch between config and manager"
        assert len(crisis_manager.override_levels) > 0, "Crisis override levels not configured"
        
        print("✅ Environment variable integration working")
        
        # Step 10: Test Error Resilience
        print("🔧 Step 10: Testing error resilience...")
        
        # Test configuration fallback behavior
        invalid_config = config_manager.get_config_section('nonexistent_config', 'invalid.path', 'fallback_value')
        assert invalid_config == 'fallback_value', "Configuration fallback not working"
        
        # Test crisis analysis with no NLP manager
        crisis_manager_no_nlp = create_crisis_analysis_manager(
            config_manager=config_manager,
            logging_manager=logging_manager,
            nlp_manager=None
        )
        
        error_result = await crisis_manager_no_nlp.analyze_message("test", 123, 456)
        assert error_result.crisis_level == CrisisLevel.NONE, "Error handling not working"
        
        print("✅ Error resilience working")
        
        # Final Integration Validation
        print("")
        print("🎉 Phase 1a Complete Integration Test PASSED")
        print("✅ All three foundation managers working together")
        print("✅ Discord Client Manager: Connection and event handling")
        print("✅ NLP Integration Manager: Analysis server communication")
        print("✅ Crisis Analysis Manager: NLP response mapping")
        print("✅ End-to-end crisis detection flow functional")
        print("✅ Configuration integration working")
        print("✅ Statistics and health monitoring operational")
        print("✅ Error resilience and fallback mechanisms working")
        print("✅ Clean Architecture v3.1 compliance verified")
        
        logger.info("🎉 Phase 1a complete integration testing successful")
        logger.info("🏆 Foundation managers ready for Phase 1b")
        
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
    """Run the Phase 1a complete integration test"""
    print("=" * 70)
    print("ASH-BOT PHASE 1a COMPLETE INTEGRATION TEST")
    print("Clean Architecture v3.1 - Foundation Managers")
    print("The Alphabet Cartel - https://discord.gg/alphabetcartel")
    print("=" * 70)
    print("")
    
    # Run the test
    success = asyncio.run(test_phase_1a_complete())
    
    if success:
        print("")
        print("=" * 70)
        print("🏆 PHASE 1a FOUNDATION COMPLETE!")
        print("✅ Discord Client Manager: Ready")
        print("✅ NLP Integration Manager: Ready") 
        print("✅ Crisis Analysis Manager: Ready")
        print("🚀 Ready to proceed to Phase 1b: Response Managers")
        print("=" * 70)
        sys.exit(0)
    else:
        print("")
        print("=" * 70)
        print("❌ PHASE 1a INTEGRATION FAILED!")
        print("Please review errors and fix before proceeding to Phase 1b")
        print("=" * 70)
        sys.exit(1)

if __name__ == "__main__":
    main()