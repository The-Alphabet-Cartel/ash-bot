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
Ash-Bot Integration Test Suite
---
FILE VERSION: v5.0-6-1.0-1
LAST MODIFIED: 2026-01-04
PHASE: Phase 6 - Final Testing & Documentation
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-bot
Community: The Alphabet Cartel - https://discord.gg/alphabetcartel | https://alphabetcartel.org
============================================================================
Integration tests verify that all Ash-Bot components work together correctly
in realistic scenarios.

Test Modules:
- test_message_flow.py: Message processing scenarios (safe and crisis)
- test_alert_flow.py: Alert dispatching and acknowledgment
- test_ash_sessions.py: Ash AI conversation sessions
- test_degradation.py: Service degradation handling
- test_health_endpoints.py: HTTP health and metrics endpoints

USAGE:
    # Run all integration tests
    docker exec ash-bot python -m pytest tests/integration/ -v

    # Run specific test module
    docker exec ash-bot python -m pytest tests/integration/test_message_flow.py -v

    # Run with coverage
    docker exec ash-bot python -m pytest tests/integration/ -v --cov=src
"""

__version__ = "v5.0-6-1.0-1"
