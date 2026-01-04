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
Discord Managers Package for Ash-Bot Service
---
FILE VERSION: v5.0-1-1.1-1
LAST MODIFIED: 2026-01-03
PHASE: Phase 1 - Discord Connectivity
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-bot
Community: The Alphabet Cartel - https://discord.gg/alphabetcartel | https://alphabetcartel.org

This package contains Discord-related managers:
- DiscordManager: Gateway connection and event handling
- ChannelConfigManager: Channel whitelist and alert routing
============================================================================
USAGE:
    from src.managers.discord import (
        create_discord_manager,
        create_channel_config_manager,
    )
"""

# Module version
__version__ = "v5.0-1-1.1-1"

# =============================================================================
# Discord Manager
# =============================================================================
from .discord_manager import (
    DiscordManager,
    create_discord_manager,
)

# =============================================================================
# Channel Config Manager
# =============================================================================
from .channel_config_manager import (
    ChannelConfigManager,
    create_channel_config_manager,
)

# =============================================================================
# Public API
# =============================================================================
__all__ = [
    "__version__",
    # Discord Manager
    "DiscordManager",
    "create_discord_manager",
    # Channel Config Manager
    "ChannelConfigManager",
    "create_channel_config_manager",
]
