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
FILE VERSION: v5.0-8-3.0-1
LAST MODIFIED: 2026-01-05
PHASE: Phase 8 - Metrics & Reporting (Step 8.3)
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
__version__ = "v5.0-8-3.0-1"


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
    logging.getLogger("anthropic").setLevel(logging.WARNING)
    logging.getLogger("aiohttp").setLevel(logging.WARNING)

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
    - Redis connection (warning only)
    - Alert channels configured (warning only, Phase 3)
    - Claude API token (warning only, Phase 4)

    Args:
        secrets_manager: Secrets manager instance
        nlp_client: NLP client instance
        channel_config: Channel config instance
        redis_manager: Redis manager instance
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
    if await nlp_client.check_health():
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

    # Phase 3: Check alert channels (warning only)
    alert_channels = channel_config.get_all_alert_channels()
    if alert_channels:
        logger.info(f"✅ {len(alert_channels)} alert channels configured (Phase 3)")
    else:
        logger.warning(
            "⚠️ No alert channels configured\n"
            "   Alerts will not be sent until channels are configured\n"
            "   Set BOT_ALERT_CHANNEL_* in .env"
        )

    # Phase 3: Check CRT role (warning only)
    if channel_config.has_crt_role():
        logger.info("✅ CRT role configured for pinging (Phase 3)")
    else:
        logger.warning(
            "⚠️ CRT role not configured\n"
            "   HIGH/CRITICAL alerts won't ping anyone\n"
            "   Set BOT_CRT_ROLE_ID in .env"
        )

    # Phase 4: Check Claude API token (warning only)
    claude_token = secrets_manager.get_claude_api_token()
    if claude_token:
        logger.info("✅ Claude API token found (Phase 4)")
    else:
        logger.warning(
            "⚠️ Claude API token not found\n"
            "   Ash AI will be disabled\n"
            "   Create secrets/claude_api_token to enable"
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
    logger.info("  Phase: 5 - Production Hardening")
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
        create_data_retention_manager,
    )
    from src.managers.alerting import (
        create_cooldown_manager,
        create_embed_builder,
        create_alert_dispatcher,
        create_auto_initiate_manager,
    )
    from src.managers.ash import (
        create_claude_client_manager,
        create_ash_session_manager,
        create_ash_personality_manager,
    )
    from src.managers.user import create_user_preferences_manager
    # Phase 5: Import health and metrics managers
    from src.managers.metrics import create_metrics_manager
    from src.managers.health import create_health_manager
    from src.api.health_routes import create_health_server
    # Phase 8: Import response metrics and reporting managers
    from src.managers.metrics import create_response_metrics_manager
    from src.managers.reporting import create_weekly_report_manager

    # Initialize managers
    logger.info("🔧 Initializing managers...")

    # Track managers for health checks
    discord_manager = None
    nlp_client = None
    redis_manager = None
    ash_session_manager = None
    health_server = None
    response_metrics_manager = None
    weekly_report_manager = None
    data_retention_manager = None

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

        # Phase 5: Create metrics manager first (used by other managers)
        metrics_manager = None
        metrics_enabled = config_manager.get("metrics", "enabled", True)
        if metrics_enabled:
            try:
                metrics_manager = create_metrics_manager()
                logger.info("✅ MetricsManager initialized (Phase 5)")
            except Exception as e:
                logger.warning(f"⚠️ Metrics initialization failed: {e}")

        # Create channel config manager
        channel_config = create_channel_config_manager(
            config_manager=config_manager,
        )

        # Create NLP client manager with metrics
        nlp_client = create_nlp_client_manager(
            config_manager=config_manager,
            metrics_manager=metrics_manager,
        )

        # Phase 2: Create Redis manager with metrics
        user_history = None
        try:
            redis_manager = create_redis_manager(
                config_manager=config_manager,
                secrets_manager=secrets_manager,
                metrics_manager=metrics_manager,
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

        # Phase 3: Create alerting managers
        alert_dispatcher = None
        cooldown_manager = None
        embed_builder = None
        try:
            # Create cooldown manager
            cooldown_manager = create_cooldown_manager(
                config_manager=config_manager,
            )

            # Create embed builder
            embed_builder = create_embed_builder()

            logger.info("✅ Alerting managers initialized (Phase 3)")

        except Exception as e:
            logger.warning(
                f"⚠️ Alerting initialization failed: {e}\n"
                "   Bot will start without alert dispatching"
            )
            cooldown_manager = None
            embed_builder = None

        # Phase 4: Prepare Claude client (session manager needs bot, created later)
        claude_client = None
        ash_personality_manager = None
        try:
            # Check for Claude API token first
            claude_token = secrets_manager.get_claude_api_token()
            if claude_token:
                # Create Claude client (no metrics_manager support yet)
                claude_client = create_claude_client_manager(
                    config_manager=config_manager,
                    secrets_manager=secrets_manager,
                )

                # Create personality manager (doesn't need bot)
                ash_personality_manager = create_ash_personality_manager(
                    config_manager=config_manager,
                    claude_client=claude_client,
                )

                logger.info("✅ Claude client and personality manager initialized (Phase 4)")
            else:
                logger.info("ℹ️ Ash AI disabled (no Claude API token)")

        except Exception as e:
            logger.warning(
                f"⚠️ Claude/personality initialization failed: {e}\n"
                "   Bot will start without Ash AI support"
            )
            claude_client = None
            ash_personality_manager = None

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

        # Create Discord manager (without Ash session manager - needs bot first)
        discord_manager = create_discord_manager(
            config_manager=config_manager,
            secrets_manager=secrets_manager,
            channel_config=channel_config,
            nlp_client=nlp_client,
            user_history=user_history,
            alert_dispatcher=None,  # Will set after creating alert_dispatcher
            ash_session_manager=None,  # Will set after creating with bot
            ash_personality_manager=ash_personality_manager,
            metrics_manager=metrics_manager,
        )

        # Phase 7: Create user preferences manager
        user_preferences_manager = None
        user_optout_enabled = config_manager.get("user_preferences", "optout_enabled", True)
        if user_optout_enabled and redis_manager:
            try:
                user_preferences_manager = create_user_preferences_manager(
                    config_manager=config_manager,
                    redis_manager=redis_manager,
                )
                logger.info("✅ UserPreferencesManager initialized (Phase 7)")
            except Exception as e:
                logger.warning(
                    f"⚠️ UserPreferencesManager initialization failed: {e}\n"
                    "   Bot will start without user opt-out feature"
                )
                user_preferences_manager = None

        # Phase 4: Now create Ash session manager with bot instance
        if claude_client and ash_personality_manager:
            try:
                ash_session_manager = create_ash_session_manager(
                    config_manager=config_manager,
                    bot=discord_manager.bot,
                )

                # Phase 7: Inject user preferences manager for opt-out support
                if user_preferences_manager:
                    ash_session_manager.set_user_preferences_manager(
                        user_preferences_manager
                    )
                    # Also inject into discord_manager for reaction handling
                    discord_manager.set_user_preferences_manager(
                        user_preferences_manager
                    )
                    logger.info("✅ User opt-out integration configured (Phase 7)")

                # Inject into discord_manager
                discord_manager.ash_session_manager = ash_session_manager
                discord_manager.bot.ash_session_manager = ash_session_manager
                logger.info("✅ AshSessionManager configured (Phase 4)")
            except Exception as e:
                logger.warning(f"⚠️ AshSessionManager creation failed: {e}")
                ash_session_manager = None

        # Phase 3: Now create alert_dispatcher with bot instance
        if cooldown_manager and embed_builder:
            try:
                alert_dispatcher = create_alert_dispatcher(
                    config_manager=config_manager,
                    channel_config=channel_config,
                    embed_builder=embed_builder,
                    cooldown_manager=cooldown_manager,
                    bot=discord_manager.bot,
                )
                # Inject alert_dispatcher into discord_manager
                discord_manager.alert_dispatcher = alert_dispatcher
                logger.info("✅ AlertDispatcher configured (Phase 3)")
            except Exception as e:
                logger.warning(f"⚠️ Failed to create AlertDispatcher: {e}")

        # Phase 8: Create response metrics manager
        try:
            if redis_manager:
                response_metrics_manager = create_response_metrics_manager(
                    config_manager=config_manager,
                    redis_manager=redis_manager,
                )
                logger.info("✅ ResponseMetricsManager initialized (Phase 8.1)")
        except Exception as e:
            logger.warning(
                f"⚠️ ResponseMetricsManager initialization failed: {e}\n"
                "   Bot will start without response time tracking"
            )
            response_metrics_manager = None

        # Phase 7: Create auto-initiate manager
        auto_initiate_manager = None
        auto_initiate_enabled = config_manager.get("auto_initiate", "enabled", True)
        if auto_initiate_enabled and alert_dispatcher:
            try:
                auto_initiate_manager = create_auto_initiate_manager(
                    config_manager=config_manager,
                    redis_manager=redis_manager,
                    bot=discord_manager.bot,
                )

                # Inject Ash managers if available
                if ash_session_manager and ash_personality_manager:
                    auto_initiate_manager.set_ash_managers(
                        ash_session_manager=ash_session_manager,
                        ash_personality_manager=ash_personality_manager,
                    )

                # Set on alert_dispatcher for integration
                alert_dispatcher.set_auto_initiate_manager(auto_initiate_manager)

                # Attach to bot instance for button access
                discord_manager.bot.auto_initiate_manager = auto_initiate_manager

                # Start the background check loop
                await auto_initiate_manager.start()

                logger.info("✅ AutoInitiateManager configured and started (Phase 7)")

            except Exception as e:
                logger.warning(
                    f"⚠️ AutoInitiateManager initialization failed: {e}\n"
                    "   Bot will start without auto-initiate feature"
                )
                auto_initiate_manager = None

        # Phase 5: Create health manager and server
        health_enabled = config_manager.get("health", "enabled", True)
        if health_enabled:
            try:
                health_manager = create_health_manager(
                    discord_manager=discord_manager,
                    nlp_client=nlp_client,
                    redis_manager=redis_manager,
                    ash_session_manager=ash_session_manager,
                    ash_personality_manager=ash_personality_manager,
                )

                # Create and start health server (need routes first)
                health_host = config_manager.get("health", "host", "0.0.0.0")
                health_port = config_manager.get("health", "port", 30881)

                # Import health routes factory
                from src.api.health_routes import create_health_routes

                # Create routes, then server
                health_routes = create_health_routes(
                    health_manager=health_manager,
                    metrics_manager=metrics_manager,
                )
                health_server = create_health_server(
                    routes=health_routes,
                    host=health_host,
                    port=health_port,
                )

                await health_server.start()
                logger.info(f"✅ Health server started on {health_host}:{health_port} (Phase 5)")

            except Exception as e:
                logger.warning(f"⚠️ Health server startup failed: {e}")
                health_server = None

        # Phase 8.3: Create and start data retention manager
        retention_enabled = config_manager.get("data_retention", "enabled", True)
        if retention_enabled and redis_manager:
            try:
                data_retention_manager = create_data_retention_manager(
                    config_manager=config_manager,
                    redis_manager=redis_manager,
                )

                # Start the retention scheduler
                await data_retention_manager.start()

                logger.info("✅ DataRetentionManager initialized (Phase 8.3)")

            except Exception as e:
                logger.warning(
                    f"⚠️ DataRetentionManager initialization failed: {e}\n"
                    "   Bot will start without automated data cleanup"
                )
                data_retention_manager = None

        # Phase 8.2: Create and start weekly report manager
        weekly_report_enabled = config_manager.get("weekly_report", "enabled", True)
        if weekly_report_enabled and response_metrics_manager:
            try:
                weekly_report_manager = create_weekly_report_manager(
                    config_manager=config_manager,
                    response_metrics_manager=response_metrics_manager,
                    bot=discord_manager.bot,
                )

                # Start the scheduler (will check channel config internally)
                await weekly_report_manager.start()

                logger.info("✅ WeeklyReportManager initialized (Phase 8.2)")

            except Exception as e:
                logger.warning(
                    f"⚠️ WeeklyReportManager initialization failed: {e}\n"
                    "   Bot will start without weekly reports"
                )
                weekly_report_manager = None

        # Setup signal handlers
        discord_manager.setup_signal_handlers()

        logger.info("✅ All managers initialized")
        logger.info("🚀 Starting Discord bot...")

        # Connect to Discord (blocks until shutdown)
        try:
            await discord_manager.connect()
        finally:
            # Phase 8.3: Stop data retention manager
            if data_retention_manager:
                await data_retention_manager.stop()
                logger.info("🔌 DataRetentionManager stopped")

            # Phase 8.2: Stop weekly report manager
            if weekly_report_manager:
                await weekly_report_manager.stop()
                logger.info("🔌 WeeklyReportManager stopped")

            # Phase 7: Stop auto-initiate manager
            if auto_initiate_manager:
                await auto_initiate_manager.stop()
                logger.info("🔌 AutoInitiateManager stopped")

            # Phase 5: Stop health server
            if health_server:
                await health_server.stop()
                logger.info("🔌 Health server stopped")

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
