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
Ash AI Test Suite for Ash-Bot Service
---
FILE VERSION: v5.0-4-1.0-1
LAST MODIFIED: 2026-01-04
PHASE: Phase 4 - Ash AI Integration
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-bot
Community: The Alphabet Cartel - https://discord.gg/alphabetcartel | https://alphabetcartel.org
============================================================================
Test suite for Ash AI managers.

TEST MODULES:
- test_claude_client.py: Claude API client tests
- test_ash_session.py: Session management tests
- test_ash_personality.py: Personality and response tests

USAGE:
    # Run all Ash tests
    pytest tests/test_ash/ -v

    # Run specific test file
    pytest tests/test_ash/test_claude_client.py -v

    # Run with coverage
    pytest tests/test_ash/ --cov=src.managers.ash
"""

# Module version
__version__ = "v5.0-4-1.0-1"
