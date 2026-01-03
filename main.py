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
----------------------------------------------------------------------------
FILE VERSION: v5.0-0-1.0-1
LAST MODIFIED: 2026-01-03
PHASE: Phase 0 - Foundation
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-bot
============================================================================

USAGE:
    # Run with default settings (inside Docker container)
    docker exec ash-bot python main.py

    # Run with debug logging
    docker exec ash-bot python main.py --log-level DEBUG
"""

import argparse
import logging
import os
import sys

# Module version
__version__ = "v5.0-0-1.0-1"


def setup_logging(log_level: str = "INFO") -> None:
    """
    Configure logging for the application.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
    """
    # Convert string to logging level
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    # Configure root logger
    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        stream=sys.stdout,
    )

    # Reduce noise from third-party libraries
    logging.getLogger("discord").setLevel(logging.WARNING)
    logging.getLogger("discord.http").setLevel(logging.WARNING)

    logger = logging.getLogger(__name__)
    logger.info(f"Logging configured at {log_level} level")


def parse_args() -> argparse.Namespace:
    """
    Parse command-line arguments.

    Returns:
        Parsed arguments namespace
    """
    parser = argparse.ArgumentParser(
        description="Ash-Bot Crisis Detection Discord Bot",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--log-level",
        type=str,
        default=os.environ.get("BOT_LOG_LEVEL", "INFO"),
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Logging level (default: INFO or BOT_LOG_LEVEL env var)",
    )

    return parser.parse_args()


def main() -> None:
    """
    Main entry point for running the service.
    """
    # Parse command-line arguments
    args = parse_args()

    # Setup logging
    setup_logging(args.log_level)

    logger = logging.getLogger(__name__)

    # Print startup banner
    logger.info("=" * 60)
    logger.info("  Ash-Bot Crisis Detection Service")
    logger.info(f"  Version: {__version__}")
    logger.info("  Community: The Alphabet Cartel")
    logger.info("  https://discord.gg/alphabetcartel")
    logger.info("=" * 60)

    # TODO: Phase 1 - Initialize managers and start bot
    logger.info("🚧 Bot initialization not yet implemented (Phase 1)")
    logger.info("✅ Main entry point working correctly")


if __name__ == "__main__":
    main()
