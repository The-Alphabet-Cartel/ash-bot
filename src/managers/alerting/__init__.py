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
Alerting Package for Ash-Bot Service
---
FILE VERSION: v5.0-3-1.0-1
LAST MODIFIED: 2026-01-04
PHASE: Phase 3 - Alert Dispatching
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-bot
Community: The Alphabet Cartel - https://discord.gg/alphabetcartel | https://alphabetcartel.org
============================================================================
This package contains alert system managers for Ash-Bot:

MANAGERS:
- CooldownManager: Prevents alert spam per user
- EmbedBuilder: Creates Discord embeds for alerts
- AlertDispatcher: Routes alerts to appropriate channels

USAGE:
    from src.managers.alerting import (
        create_cooldown_manager,
        create_embed_builder,
        create_alert_dispatcher,
    )

    cooldown = create_cooldown_manager(config_manager)
    embed_builder = create_embed_builder()
    dispatcher = create_alert_dispatcher(...)
"""

# Module version
__version__ = "v5.0-3-1.0-1"

# =============================================================================
# Cooldown Manager
# =============================================================================

from .cooldown_manager import (
    CooldownManager,
    create_cooldown_manager,
)

# =============================================================================
# Embed Builder
# =============================================================================

from .embed_builder import (
    EmbedBuilder,
    create_embed_builder,
)

# =============================================================================
# Alert Dispatcher
# =============================================================================

from .alert_dispatcher import (
    AlertDispatcher,
    create_alert_dispatcher,
)

# =============================================================================
# Public API
# =============================================================================

__all__ = [
    "__version__",
    # Cooldown
    "CooldownManager",
    "create_cooldown_manager",
    # Embed Builder
    "EmbedBuilder",
    "create_embed_builder",
    # Alert Dispatcher
    "AlertDispatcher",
    "create_alert_dispatcher",
]
