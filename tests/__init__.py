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
Ash-Bot Test Suite
---
FILE VERSION: v5.0
Repository: https://github.com/the-alphabet-cartel/ash-bot
Community: The Alphabet Cartel - https://discord.gg/alphabetcartel | https://alphabetcartel.org

Test suite for Ash-Bot v5.0 Crisis Detection Discord Bot.

USAGE:
    # Run all tests
    pytest tests/

    # Run with coverage
    pytest tests/ --cov=src --cov-report=html

    # Run specific test file
    pytest tests/test_api.py

    # Run specific test
    pytest tests/test_api.py::test_health_endpoint

    # Verbose output
    pytest tests/ -v
"""

__version__ = "v5.0"
