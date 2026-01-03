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
Ash-Bot Test Suite
----------------------------------------------------------------------------
FILE VERSION: v5.0-0-1.0-1
LAST MODIFIED: 2026-01-03
PHASE: Phase 0 - Foundation
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-bot
============================================================================

Test suite for Ash-Bot v5.0 Crisis Detection Discord Bot.

USAGE:
    # Run all tests (inside Docker container)
    docker exec ash-bot python -m pytest tests/ -v

    # Run with coverage
    docker exec ash-bot python -m pytest tests/ --cov=src --cov-report=html

    # Run specific test file
    docker exec ash-bot python -m pytest tests/test_managers/test_config.py -v

    # Run specific test
    docker exec ash-bot python -m pytest tests/test_managers/test_config.py::test_specific -v
"""

__version__ = "v5.0-0-1.0-1"
