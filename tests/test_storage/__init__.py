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
Storage Manager Tests Package for Ash-Bot Service
----------------------------------------------------------------------------
FILE VERSION: v5.0-2-1.0-1
LAST MODIFIED: 2026-01-03
PHASE: Phase 2 - Redis History Storage
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-bot
Community: The Alphabet Cartel - https://discord.gg/alphabetcartel | https://alphabetcartel.org
============================================================================

Test suite for storage managers:
- test_redis_manager.py: RedisManager unit tests
- test_user_history_manager.py: UserHistoryManager unit tests

USAGE:
    # Run all storage tests
    pytest tests/test_storage/ -v

    # Run specific test file
    pytest tests/test_storage/test_redis_manager.py -v
"""

__version__ = "v5.0-2-1.0-1"
