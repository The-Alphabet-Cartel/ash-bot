"""
Ash-Bot: Crisis Detection Discord Bot for The Alphabet Cartel Discord Community
CORE PRINCIPLE:
******************  CORE SYSTEM VISION (Never to be violated):  ****************
Ash-Bot is a CRISIS DETECTION DISCORD BOT that:
1. **PRIMARY**: Monitors all messages within our discord server and sends them to our NLP server for semantic classification.
2. **SECONDARY**: If the NLP server detects a crisis, the bot alerts the appropriate staff members within the Crisis Response Team (CRT) using "pings" (@crisis_response) to the CRT role within the crisis-response channel utilizing discord's embeds feature to show crisis details based on the NLP determined severity of the crisis.
3. **TERTIARY**: Tracks historical patterns and messages and sends them to our NLP server for semantic classification to determine if there is a pattern of escalation over time.
4. **PURPOSE**: To detect crisis messages in Discord community communications.
********************************************************************************
Ash-Bot Source Package
---
FILE VERSION: v5.0
LAST MODIFIED: 2025-01-03
PHASE: Phase 1
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-bot
Community: The Alphabet Cartel - https://discord.gg/alphabetcartel | https://alphabetcartel.org

This is the main source package for Ash-Bot containing:
- managers: Configuration and resource management

USAGE:
    from src.managers import create_config_manager
"""

__version__ = "5.0.0"
__author__ = "The Alphabet Cartel"
__email__ = "dev@alphabetcartel.org"
__url__ = "https://github.com/the-alphabet-cartel/ash-bot"

# Package metadata
__all__ = [
    "__version__",
    "__author__",
    "__email__",
    "__url__",
]
