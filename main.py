#!/usr/bin/env python3
"""
============================================================================
Ash-Bot: Crisis Detection Discord Bot
The Alphabet Cartel - https://discord.gg/alphabetcartel | alphabetcartel.org
============================================================================

MISSION - NEVER TO BE VIOLATED:
    Monitor  → Send messages to Ash-NLP for crisis classification
    Alert    → Notify Crisis Response Team via embeds when crisis detected
    Track    → Maintain user history for escalation pattern detection
    Protect  → Safeguard our LGBTQIA+ community through early intervention

============================================================================
Main Entry Point for Ash-Bot Service
---
FILE VERSION: v5.0-2-7.0-1
LAST MODIFIED: 2026-01-04
PHASE: Phase 2 - Redis History Storage
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-bot
Community: The Alphabet Cartel - https://discord.gg/alphabetcartel | https://alphabetcartel.org
============================================================================
USAGE:
    # Run with default settings
    python main.py

    # Run with debug logging
    python main.py --log-level DEBUG

    # Run in testing environment
    python main.py --environment testing

ENVIRONMENT VARIABLES:
    BOT_ENVIRONMENT: production, testing (default: production)
    BOT_LOG_LEVEL: DEBUG, INFO, WARNING, ERROR (default: INFO)
"""

import argparse
import asyncio
import logging
import os
import signal
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Module version
__version__ = "v5.0-2-7.0-1"


# =============================================================================
# Logging Setup
# =============================================================================


def setup_logging(log_level: str = "INFO", log_format: str = "text") -> None:
    """
    Configure logging for the application.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_format: Log format (json, text)
    """
    # Convert string to logging level
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    # Choose format
    if log_format.lower() == "json":
        # JSON format for production
        format_str = '{"time":"%(asctime)s","level":"%(levelname)s","logger":"%(name)s","message":"%(message)s"}'
    else:
        # Human-readable format for development
        format_str = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"

    # Configure root logger
    logging.basicConfig(
        level=numeric_level,
        format=format_str,
        datefmt="%Y-%m-%d %H:%M:%S",
        stream=sys.stdout,
    )

    # Reduce noise from third-party libraries
    logging.getLogger("discord").setLevel(logging.WARNING)
    logging.getLogger("discord.http").setLevel(logging.WARNING)
    logging.getLogger("discord.gateway").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)

    logger = logging.getLogger(__name__)
    logger.info(f"Logging configured at {log_level} level ({log_format} format)")


def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments.

    Returns:
        Parsed arguments namespace
    """
    parser = argparse.ArgumentParser(
        description="Ash-Bot Crisis Detection Discord Bot",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python main.py                          # Run with defaults
    python main.py --log-level DEBUG        # Enable debug logging
    python main.py --environment testing    # Use testing config

For more information, visit:
    https://github.com/the-alphabet-cartel/ash-bot
    https://discord.gg/alphabetcartel
        """,
    )

    parser.add_argument(
        "--log-level",
        default=os.environ.get("BOT_LOG_LEVEL", "INFO"),
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Logging level (default: INFO)",
    )

    parser.add_argument(
        "--log-format",
        default=os.environ.get("BOT_LOG_FORMAT", "text"),
        choices=["json", "text"],
        help="Log format (default: text for dev, json for prod)",
    )

    parser.add_argument(
        "--environment",
        default=os.environ.get("BOT_ENVIRONMENT", "production"),
        choices=["production", "testing", "development"],
        help="Environment name (default: production)",
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"Ash-Bot {__version__}",
    )

    return parser.parse_args()


# =============================================================================
# Startup Validation
# =============================================================================


async def validate_startup(
    secrets_manager,
    nlp_client,
    channel_config,
    redis_manager,
    logger: logging.Logger,
) -> bool:
    """
    Validate startup requirements.

    Checks:
    - Discord bot token exists
    - Ash-NLP API is reachable (warning only)
    - At least one channel is configured (warning only)
    - Redis connection (warning only - Phase 2)

    Args:
        secrets_manager: Secrets manager instance
        nlp_client: NLP client instance
        channel_config: Channel config instance
        redis_manager: Redis manager instance (Phase 2)
        logger: Logger instance

    Returns:
        True if validation passes, False otherwise
    """
    validation_passed = True

    # Check Discord bot token (required)
    token = secrets_manager.get_discord_bot_token()
    if not token:
        logger.error(
            "❌ FATAL: Discord bot token not found!\n"
            "   Please create: secrets/discord_bot_token\n"
            "   See secrets/README.md for instructions"
        )
        return False
    else:
        logger.info("✅ Discord bot token found")

    # Check NLP API (warning only)
    if await nlp_client.health_check():
        logger.info("✅ Ash-NLP API is healthy")
    else:
        logger.warning(
            "⚠️ Ash-NLP API is not responding\n"
            "   Bot will start, but crisis detection may fail\n"
            "   Make sure ash-nlp container is running"
        )

    # Check monitored channels (warning only)
    if channel_config.monitored_channel_count > 0:
        logger.info(
            f"✅ {channel_config.monitored_channel_count} channels configured for monitoring"
        )
    else:
        logger.warning(
            "⚠️ No channels configured for monitoring\n"
            "   Bot will connect but won't process any messages\n"
            "   Set BOT_MONITORED_CHANNELS in .env"
        )

    # Phase 2: Check Redis connection (warning only)
    if redis_manager:
        if await redis_manager.health_check():
            logger.info("✅ Redis connection is healthy (Phase 2)")
        else:
            logger.warning(
                "⚠️ Redis is not responding\n"
                "   Bot will start, but history tracking will be disabled\n"
                "   Make sure ash-redis container is running"
            )

    return validation_passed


# =============================================================================
# Main Entry Point
# =============================================================================


async def main_async(args: argparse.Namespace) -> int:
    """
    Async main entry point.

    Initializes all managers and starts the bot.

    Args:
        args: Parsed command-line arguments

    Returns:
        Exit code (0 = success, 1 = error)
    """
    logger = logging.getLogger(__name__)

    # Print startup banner
    logger.info("=" * 60)
    logger.info("  🤖 Ash-Bot Crisis Detection Service")
    logger.info(f"  Version: {__version__}")
    logger.info(f"  Environment: {args.environment}")
    logger.info("  Community: The Alphabet Cartel")
    logger.info("  https://discord.gg/alphabetcartel")
    logger.info("=" * 60)

    # Import managers (after path setup)
    from src.managers import create_config_manager, create_secrets_manager
    from src.managers.discord import (
        create_channel_config_manager,
        create_discord_manager,
    )
    from src.managers.nlp import create_nlp_client_manager
    from src.managers.storage import (
        create_redis_manager,
        create_user_history_manager,
    )

    # Initialize managers
    logger.info("🔧 Initializing managers...")

    try:
        # Set environment for config manager
        os.environ["BOT_ENVIRONMENT"] = args.environment

        # Create configuration manager
        config_manager = create_config_manager(
            config_dir=Path(__file__).parent / "src" / "config",
            environment=args.environment,
        )

        # Create secrets manager
        secrets_manager = create_secrets_manager()

        # Create channel config manager
        channel_config = create_channel_config_manager(
            config_manager=config_manager,
        )

        # Create NLP client manager
        nlp_client = create_nlp_client_manager(
            config_manager=config_manager,
        )

        # Phase 2: Create Redis manager
        redis_manager = None
        user_history = None
        try:
            redis_manager = create_redis_manager(
                config_manager=config_manager,
                secrets_manager=secrets_manager,
            )
            await redis_manager.connect()
            logger.info("✅ Redis connected (Phase 2)")

            # Create user history manager
            user_history = create_user_history_manager(
                config_manager=config_manager,
                redis_manager=redis_manager,
            )
            logger.info("✅ UserHistoryManager initialized (Phase 2)")

        except Exception as e:
            logger.warning(
                f"⚠️ Redis initialization failed: {e}\n"
                "   Bot will start without history tracking\n"
                "   Make sure ash-redis container is running"
            )
            redis_manager = None
            user_history = None

        # Validate startup
        logger.info("🔍 Validating startup requirements...")
        if not await validate_startup(
            secrets_manager=secrets_manager,
            nlp_client=nlp_client,
            channel_config=channel_config,
            redis_manager=redis_manager,
            logger=logger,
        ):
            logger.error("❌ Startup validation failed")
            return 1

        # Create Discord manager (with history if available)
        discord_manager = create_discord_manager(
            config_manager=config_manager,
            secrets_manager=secrets_manager,
            channel_config=channel_config,
            nlp_client=nlp_client,
            user_history=user_history,
        )

        # Setup signal handlers
        discord_manager.setup_signal_handlers()

        logger.info("✅ All managers initialized")
        logger.info("🚀 Starting Discord bot...")

        # Connect to Discord (blocks until shutdown)
        try:
            await discord_manager.connect()
        finally:
            # Phase 2: Disconnect Redis on shutdown
            if redis_manager and redis_manager.is_connected:
                await redis_manager.disconnect()
                logger.info("🔌 Redis disconnected")

        logger.info("👋 Ash-Bot shutdown complete")
        return 0

    except KeyboardInterrupt:
        logger.info("👋 Shutdown requested via keyboard")
        return 0

    except ValueError as e:
        logger.error(f"❌ Configuration error: {e}")
        return 1

    except ConnectionError as e:
        logger.error(f"❌ Connection error: {e}")
        return 1

    except Exception as e:
        logger.exception(f"❌ Unexpected error: {e}")
        return 1


def main() -> None:
    """
    Main entry point for running the service.

    Parses arguments, sets up logging, and runs the async main.
    """
    # Parse arguments
    args = parse_arguments()

    # Setup logging
    setup_logging(
        log_level=args.log_level,
        log_format=args.log_format,
    )

    # Run async main
    try:
        exit_code = asyncio.run(main_async(args))
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n👋 Shutdown requested")
        sys.exit(0)


if __name__ == "__main__":
    main()
