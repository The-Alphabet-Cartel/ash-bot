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
Session Package - Managers for session handoff, documentation, and follow-up
----------------------------------------------------------------------------
FILE VERSION: v5.0-9-3.0-1
LAST MODIFIED: 2026-01-05
PHASE: Phase 9 - CRT Workflow Enhancements (Step 9.3)
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-bot
============================================================================

This package contains managers for CRT session operations:

- NotesManager: Session notes storage and display
- HandoffManager: CRT handoff detection and coordination
- FollowUpManager: Automated follow-up check-ins after sessions

USAGE:
    from src.managers.session import (
        create_notes_manager,
        create_handoff_manager,
        create_followup_manager,
    )

    notes_manager = create_notes_manager(config_manager, redis_manager)
    handoff_manager = create_handoff_manager(config_manager, notes_manager)
    followup_manager = create_followup_manager(config_manager, redis_manager, user_prefs)
"""

from src.managers.session.notes_manager import (
    NotesManager,
    create_notes_manager,
    SessionNote,
    SessionSummary,
    SEVERITY_EMOJIS,
    SEVERITY_COLORS,
)
from src.managers.session.handoff_manager import (
    HandoffManager,
    create_handoff_manager,
    HANDOFF_MESSAGES,
)
from src.managers.session.followup_manager import (
    FollowUpManager,
    create_followup_manager,
    ScheduledFollowup,
    CHECKIN_MESSAGES,
    SEVERITY_ORDER,
)

# Module version
__version__ = "v5.0-9-3.0-1"

__all__ = [
    # Notes Manager
    "NotesManager",
    "create_notes_manager",
    "SessionNote",
    "SessionSummary",
    "SEVERITY_EMOJIS",
    "SEVERITY_COLORS",
    # Handoff Manager
    "HandoffManager",
    "create_handoff_manager",
    "HANDOFF_MESSAGES",
    # Follow-Up Manager
    "FollowUpManager",
    "create_followup_manager",
    "ScheduledFollowup",
    "CHECKIN_MESSAGES",
    "SEVERITY_ORDER",
]
