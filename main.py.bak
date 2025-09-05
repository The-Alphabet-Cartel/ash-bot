#!/usr/bin/env python3
"""
Ash-Bot: Crisis Detection Discord Bot for The Alphabet Cartel Discord Community
********************************************************************************
Ash-Bot Main Application Entry Point for Ash Bot Service
---
FILE VERSION: v3.1-1
LAST MODIFIED: 2025-09-4
CLEAN ARCHITECTURE: v3.1
Repository: https://github.com/the-alphabet-cartel/ash-thrash
Community: The Alphabet Cartel - https://discord.gg/alphabetcartel | https://alphabetcartel.org
"""

import asyncio
import logging
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# ============================================================================
# MANAGER IMPORTS - ALL USING FACTORY FUNCTIONS (Clean Architecture)
# ============================================================================
from managers.unified_config import create_unified_config_manager
from managers.logging_config import create_logging_config_manager
from core.config_manager import ConfigManager
# ============================================================================

# ============================================================================
# UNIFIED LOGGING SETUP
# ============================================================================
def setup_logging(unified_config):
    """
    Setup colorlog logging with unified configuration management
    """
    try:
        # Get logging configuration through unified config
        log_level = unified_config.get_config_section('logging_settings', 'global_settings.log_level', 'INFO')
        log_detailed = unified_config.get_config_section('logging_settings', 'detailed_logging.enable_detailed', True)
        enable_file_logging = unified_config.get_config_section('logging_settings', 'global_settings.enable_file_output', False)
        log_file = unified_config.get_config_section('logging_settings', 'global_settings.log_file', 'ash-thrash.log')
        
        # Configure colorlog formatter
        if log_detailed == False:
            log_format_string = '%(log_color)s%(levelname)s%(reset)s: %(message)s'
        else:  # detailed
            log_format_string = '%(log_color)s%(asctime)s - %(name)s - %(levelname)s%(reset)s: %(message)s'
        
        # Create colorlog formatter
        formatter = colorlog.ColoredFormatter(
            log_format_string,
            datefmt='%Y-%m-%d %H:%M:%S',
            reset=True,
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'red,bg_white',
            }
        )
        
        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
        
        # Clear existing handlers
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # Console handler
        console_handler = colorlog.StreamHandler()
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
        
        # Optional file handler
        if enable_file_logging:
            try:
                file_handler = logging.FileHandler(log_file)
                file_formatter = logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S'
                )
                file_handler.setFormatter(file_formatter)
                root_logger.addHandler(file_handler)
                logging.info(f"File logging enabled: {log_file}")
            except Exception as e:
                logging.warning(f"Could not setup file logging: {e}")
        
        logging.info("Unified colorlog logging configured successfully")
        logging.info(f"Log level: {log_level}")
        
    except Exception as e:
        # Fallback to basic logging
        logging.basicConfig(level=logging.INFO)
        logging.error(f"Failed to setup unified logging: {e}")
        logging.info("Using fallback basic logging configuration")
# ============================================================================

# ============================================================================
# UNIFIED MANAGER INITIALIZATION
# ============================================================================
def initialize_managers(unified_config):
    """
    Initialize all managers using factory functions (Clean Architecture v3.1) - Phase 3a Enhanced
    """
    logger = logging.getLogger(__name__)
    logger.info("=" * 70)
    logger.info("Initializing Ash-Thrash managers...")
    logger.info("=" * 70)
    
    try:
        # Core configuration managers
        logging_config = create_logging_config_manager(unified_config)
        
        managers = {
            'unified_config': unified_config,
            'logging_config': logging_config
        }
        
        logger.info(f"All managers initialized successfully: {len(managers)} total")
        return managers
        
    except Exception as e:
        logger.error(f"Manager initialization failed: {e}")
        raise
# ============================================================================

async def main():
    """Main entry point for Ash bot - CLEANED VERSION"""
    
    # Setup logging first
    try:
        # Initialize unified configuration manager first
        unified_config = create_unified_config_manager()
        
        # Setup unified logging
        setup_logging(unified_config)
        logger = logging.getLogger(__name__)

        logger.info("🚀 Starting Ash Bot v3.0...")
        logger.info("Serving The Alphabet Cartel LGBTQIA+ Community")
        logger.info("Repository: https://github.com/the-alphabet-cartel/ash-thrash")
        logger.info("Discord: https://discord.gg/alphabetcartel")
        logger.info("Website: https://alphabetcartel.org")
        logger.info("")
        logger.info("╔══════════════════════════════════════╗")
        logger.info("║           ASH BOT v3.0               ║")
        logger.info("║       The Alphabet Cartel's          ║")
        logger.info("║        Mental Health Sage            ║")
        logger.info("║        Modular Architecture          ║")
        logger.info("║                                      ║")
        logger.info("║  'Building chosen family,            ║")
        logger.info("║      one conversation at a time.'    ║")
        logger.info("╚══════════════════════════════════════╝")
        logger.info("=" * 70)
        logger.info("")
        logger.info("=" * 70)
        
        # Initialize all managers (including Phase 3a tuning manager)
        managers = initialize_managers()

        # Test configuration loading
        logger.info("🔧 Testing configuration...")
        bot_config = BotConfigManager()
        logger.info("✅ Configuration loaded successfully")
        
        # Initialize and start the bot
        from core.bot_manager import AshBot
        
        logger.info("🤖 Creating modular bot instance...")
        bot = AshBot(bot_config)
        
        logger.info("🚀 Starting modular bot...")
        
        # Add reaction event handlers AFTER creating the bot instance
        @bot.event
        async def on_reaction_add(reaction, user):
            """Handle reaction-based staff handoffs"""
            
            # Only process reactions in guilds (not DMs)
            if not reaction.message.guild:
                return
            
            # Let the message handler process the reaction
            if hasattr(bot, 'message_handler') and bot.message_handler:
                await bot.message_handler.handle_reaction_add(reaction, user)
        
        # Optional: Also handle reaction removal if needed
        @bot.event
        async def on_reaction_remove(reaction, user):
            """Handle reaction removal (optional - for undoing accidental handoffs)"""
            # Could implement undo functionality here if desired
            pass
        
        logger.info("🚀 Starting modular bot...")

        # Get Discord token
        token = bot_config.get('BOT_DISCORD_TOKEN')
        if not token:
            logger.error("❌ Discord token missing!")
            return
        
        # Start the bot directly (this is already async)
        await bot.start(token)
        
    except Exception as e:
        logger.error(f"💥 Configuration test failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("🛑 Startup interrupted by user")
    except Exception as e:
        print(f"💥 Critical startup error: {e}")
        sys.exit(1)