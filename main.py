#!/usr/bin/env python3
"""
Ash Discord Bot - Modular Entry Point - CLEANED VERSION
"""

import asyncio
import logging
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add the bot directory to Python path
bot_dir = Path(__file__).parent
sys.path.insert(0, str(bot_dir))

from bot.utils.logging_utils import setup_logging
from bot.core.config_manager import ConfigManager

# Load environment variables
load_dotenv()

def print_startup_banner():
    """Print Ash's startup banner"""
    banner = """
    ╔══════════════════════════════════════╗
    ║           ASH BOT v3.0               ║
    ║       The Alphabet Cartel's          ║
    ║        Mental Health Sage            ║
    ║        Modular Architecture          ║
    ║                                      ║
    ║  "Building chosen family,            ║
    ║      one conversation at a time."    ║
    ╚══════════════════════════════════════╝
    """
    print(banner)

async def main():
    """Main entry point for Ash bot - CLEANED VERSION"""
    print_startup_banner()
    
    # Setup logging first
    logger = setup_logging()
    logger.info("🚀 Starting Ash Bot v3.0 (Modular Architecture - CLEANED)...")
    
    try:
        # Test configuration loading
        logger.info("🔧 Testing configuration...")
        config = ConfigManager()
        logger.info("✅ Configuration loaded successfully")
        
        # Initialize and start the bot
        from bot.core.bot_manager import AshBot
        
        logger.info("🤖 Creating modular bot instance (CLEANED)...")
        bot = AshBot(config)
        
        logger.info("🚀 Starting modular bot (CLEANED)...")
        
        # Get Discord token
        token = config.get('BOT_DISCORD_TOKEN')
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