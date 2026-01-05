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
User Package for Ash-Bot Service
---
FILE VERSION: v5.0-7-2.0-1
LAST MODIFIED: 2026-01-04
PHASE: Phase 7 - Core Safety & User Preferences
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-bot
Community: The Alphabet Cartel - https://discord.gg/alphabetcartel | https://alphabetcartel.org
============================================================================
This package contains user preference managers for Ash-Bot:

MANAGERS:
- UserPreferencesManager: Manages user opt-out and other preferences

USAGE:
    from src.managers.user import (
        create_user_preferences_manager,
        UserPreferencesManager,
    )

    preferences = create_user_preferences_manager(config, redis)
    is_opted_out = await preferences.is_opted_out(user_id)
"""

# Module version
__version__ = "v5.0-7-2.0-1"

# =============================================================================
# User Preferences Manager
# =============================================================================

from .user_preferences_manager import (
    UserPreferencesManager,
    create_user_preferences_manager,
    UserPreference,
)

# =============================================================================
# Public API
# =============================================================================

__all__ = [
    "__version__",
    # User Preferences
    "UserPreferencesManager",
    "create_user_preferences_manager",
    "UserPreference",
]
