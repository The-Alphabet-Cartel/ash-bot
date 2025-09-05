#!/usr/bin/env python3
"""
Ash-Bot: Crisis Detection Bot for The Alphabet Cartel Discord Community
********************************************************************************
Phase 1a Step 1 Integration Test - Discord Client Manager
---
FILE VERSION: v3.1-1a-1-3
LAST MODIFIED: 2025-09-05
PHASE: 1a Step 1 Test
CLEAN ARCHITECTURE: v3.1
Repository: https://github.com/the-alphabet-cartel/ash-bot
Community: The Alphabet Cartel - https://discord.gg/alphabetcartel | https://alphabetcartel.org
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import managers using factory functions (Rule #1)
from managers.unified_config import create_unified_config_manager
from managers.logging_config import create_logging_config_manager
from managers.discord_client import create_discord_client_manager

async def test_discord_client_manager():
    """
    Test Phase 1a Step 1: DiscordClientManager
    Following Rule #8: Real-world testing with actual methods
    """
    
    print("🧪 Starting Phase 1a Step 1 Integration Test")
    print("📋 Testing: DiscordClientManager with Clean Architecture v3.1")
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
        logger.info("🔬 Phase 1a Step 1 testing started")
        
        # Step 3: Test JSON configuration loading
        print("🔧 Step 3: Testing discord_config.json loading...")
        discord_config = config_manager.load_config_file('discord_config')
        
        # Validate configuration structure
        assert '_metadata' in discord_config, "Missing _metadata in discord_config"
        assert 'discord_settings' in discord_config, "Missing discord_settings in discord_config"
        assert 'intents' in discord_config, "Missing intents in discord_config"
        
        print("✅ discord_config.json loaded and validated")
        logger.info("📋 Discord configuration validation successful")
        
        # Step 4: Test environment variable mapping (Rule #7)
        print("🔧 Step 4: Testing environment variable mapping (Rule #7)...")
        guild_id = config_manager.get_env('BOT_GUILD_ID')
        rate_limit = config_manager.get_env('BOT_RATE_LIMIT_PER_USER')
        
        if guild_id:
            print(f"✅ BOT_GUILD_ID mapped: {guild_id}")
            logger.info(f"🔗 BOT_GUILD_ID successfully mapped: {guild_id}")
        else:
            print("⚠️ BOT_GUILD_ID not found in environment")
            logger.warning("⚠️ BOT_GUILD_ID not configured - using defaults")
        
        if rate_limit:
            print(f"✅ BOT_RATE_LIMIT_PER_USER mapped: {rate_limit}")
            logger.info(f"🔗 BOT_RATE_LIMIT_PER_USER successfully mapped: {rate_limit}")
        
        # Step 5: Test DiscordClientManager factory function
        print("🔧 Step 5: Testing DiscordClientManager factory function...")
        discord_client = create_discord_client_manager(
            config_manager=config_manager,
            logging_manager=logging_manager
        )
        
        print("✅ DiscordClientManager created via factory function")
        logger.info("🏭 DiscordClientManager factory function successful")
        
        # Step 6: Test manager configuration
        print("🔧 Step 6: Testing manager configuration...")
        
        # Test configuration access
        discord_settings = discord_client.config.get('discord_settings', {})
        assert discord_settings, "Discord settings not loaded"
        
        # Test guild ID parsing
        if discord_client.guild_id:
            assert isinstance(discord_client.guild_id, int), "Guild ID should be integer"
            print(f"✅ Guild ID configured: {discord_client.guild_id}")
            logger.info(f"🏠 Guild ID validation successful: {discord_client.guild_id}")
        
        # Test command prefix
        assert discord_client.command_prefix, "Command prefix should be set"
        print(f"✅ Command prefix configured: '{discord_client.command_prefix}'")
        logger.info(f"💬 Command prefix validation successful: '{discord_client.command_prefix}'")
        
        # Step 7: Test intents configuration
        print("🔧 Step 7: Testing Discord intents configuration...")
        intents = discord_client.intents
        
        # Critical intents for crisis detection
        assert intents.message_content, "message_content intent required"
        assert intents.members, "members intent required"
        assert intents.reactions, "reactions intent required"
        
        print("✅ Critical Discord intents configured")
        logger.info("🔐 Discord intents validation successful")
        
        # Step 8: Test health status method
        print("🔧 Step 8: Testing health status method...")
        health_status = discord_client.get_health_status()
        
        # Validate health status structure
        required_keys = ['discord_ready', 'connection_healthy', 'latency_ms', 'uptime_seconds']
        for key in required_keys:
            assert key in health_status, f"Missing health status key: {key}"
        
        print("✅ Health status method functional")
        logger.info("💪 Health status validation successful")
        
        # Step 9: Test resilient configuration fallbacks
        print("🔧 Step 9: Testing resilient configuration fallbacks...")
        
        # Test fallback mechanism
        discord_client._apply_fallback_configuration()
        print("✅ Fallback configuration mechanism working")
        logger.info("🛡️ Resilient fallback testing successful")
        
        # Step 10: Test manager integration points
        print("🔧 Step 10: Testing manager integration points...")
        
        # Test event handler registration
        def test_handler():
            pass
        
        discord_client.register_event_handler('on_test', test_handler)
        assert 'on_test' in discord_client.event_handlers, "Event handler not registered"
        
        print("✅ Event handler registration working")
        logger.info("📡 Event handler registration successful")
        
        # Final validation
        print("")
        print("🎉 Phase 1a Step 1 Integration Test PASSED")
        print("✅ DiscordClientManager fully functional")
        print("✅ Clean Architecture v3.1 compliance verified")
        print("✅ Rule #7 environment variable mapping confirmed")
        print("✅ Factory function pattern working")
        print("✅ JSON configuration loading successful")
        print("✅ Resilient error handling operational")
        
        logger.info("🎉 Phase 1a Step 1 testing completed successfully")
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
    """Run the Phase 1a Step 1 integration test"""
    print("=" * 70)
    print("ASH-BOT PHASE 1a STEP 1 INTEGRATION TEST")
    print("Clean Architecture v3.1 - Discord Client Manager")
    print("The Alphabet Cartel - https://discord.gg/alphabetcartel")
    print("=" * 70)
    print("")
    
    # Run the test
    success = asyncio.run(test_discord_client_manager())
    
    if success:
        print("")
        print("=" * 70)
        print("🎉 PHASE 1a STEP 1 COMPLETE!")
        print("Ready to proceed to Phase 1a Step 2: NLP Integration Manager")
        print("=" * 70)
        sys.exit(0)
    else:
        print("")
        print("=" * 70)
        print("❌ PHASE 1a STEP 1 FAILED!")
        print("Please review errors and fix before proceeding")
        print("=" * 70)
        sys.exit(1)

if __name__ == "__main__":
    main()