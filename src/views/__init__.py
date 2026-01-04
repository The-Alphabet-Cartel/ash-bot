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
Views Package for Ash-Bot Service
---
FILE VERSION: v5.0-3-1.0-1
LAST MODIFIED: 2026-01-04
PHASE: Phase 3 - Alert Dispatching
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-bot
Community: The Alphabet Cartel - https://discord.gg/alphabetcartel | https://alphabetcartel.org
============================================================================
This package contains Discord UI components (Views) for Ash-Bot:

VIEWS:
- AlertButtonView: Buttons for crisis alert interactions

USAGE:
    from src.views import AlertButtonView

    view = AlertButtonView(user_id=123, message_id=456, severity="high")
    await channel.send(embed=embed, view=view)
"""

# Module version
__version__ = "v5.0-3-1.0-1"

# =============================================================================
# Alert Buttons
# =============================================================================

from .alert_buttons import (
    AlertButtonView,
    PersistentAlertView,
)

# =============================================================================
# Public API
# =============================================================================

__all__ = [
    "__version__",
    "AlertButtonView",
    "PersistentAlertView",
]
