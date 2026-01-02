#!/usr/bin/env python3
"""
Ash-Bot: Crisis Detection Discord Bot for The Alphabet Cartel Discord Community
CORE PRINCIPLE:
******************  CORE SYSTEM VISION (Never to be violated):  ****************
Ash-Bot is a CRISIS DETECTION DISCORD BOT that:
1. PRIMARY: Monitors all messages within our discord server and sends them to our NLP server for semantic classification.
2. CONTEXTUAL: If the NLP server detects a crisis, the bot alerts the appropriate staff members within the Crisis Response Team (CRT) using "pings" (@crisis_response) to the CRT role within the crisis-response channel utilizing discord's embeds feature to show crisis details based on the NLP determined severity of the crisis.
3. HISTORICAL: Tracks historical patterns and messages and sends them to our NLP server for semantic classification to determine if there is a pattern of escalation over time.
5. **PURPOSE**: To detect crisis messages in Discord community communications.
********************************************************************************
Main Entry Point for Ash-Bot Service
---
FILE VERSION: v5.0
LAST MODIFIED: 2026-1-22026-01-02
PHASE: Phase 1
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-bot
Community: The Alphabet Cartel - https://discord.gg/alphabetcartel | https://alphabetcartel.org

USAGE:
    # Run with default settings
    python main.py

ENVIRONMENT VARIABLES:
"""

import logging
import os
import sys

# Module version
__version__ = "v5.0"


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
    # logging.getLogger("uvicorn").setLevel(logging.WARNING)
    # logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

    logger = logging.getLogger(__name__)
    logger.info(f"Logging configured at {log_level} level")


def main() -> None:
    """
    Main entry point for running the service.
    """
    # Setup logging
    setup_logging(args.log_level)

    logger = logging.getLogger(__name__)

    # Print startup banner
    logger.info("=" * 60)
    logger.info("  Ash-Bot Crisis Detection Service")
    logger.info(f"  Version: {__version__}")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
