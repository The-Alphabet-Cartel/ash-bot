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
Test Package: Follow-Up Check-Ins (Phase 9.3)
----------------------------------------------------------------------------
FILE VERSION: v5.0-9-3.0-1
LAST MODIFIED: 2026-01-05
PHASE: Phase 9 - CRT Workflow Enhancements (Step 9.3)
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-bot
============================================================================

This package contains tests for the FollowUpManager and related functionality.

USAGE:
    # Run all follow-up tests
    docker exec ash-bot python -m pytest tests/test_followup/ -v

    # Run specific test class
    docker exec ash-bot python -m pytest tests/test_followup/test_followup.py::TestEligibilityChecking -v
"""

__version__ = "v5.0-9-3.0-1"
