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
Managers Package for Ash-Bot Service
---
FILE VERSION: v5.0-3-1.0-1
LAST MODIFIED: 2026-01-04
PHASE: Phase 3 - Alert Dispatching
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-bot
Community: The Alphabet Cartel - https://discord.gg/alphabetcartel | https://alphabetcartel.org
============================================================================
This package contains resource managers for Ash-Bot:

MANAGERS:
- ConfigManager: Configuration loading and validation
- SecretsManager: Secure credential access
- DiscordManager: Discord gateway connection (Phase 1)
- ChannelConfigManager: Channel whitelist management (Phase 1)
- NLPClientManager: Ash-NLP API client (Phase 1)
- RedisManager: Redis connection management (Phase 2)
- UserHistoryManager: User message history storage (Phase 2)
- CooldownManager: Alert cooldown tracking (Phase 3)
- EmbedBuilder: Discord embed creation (Phase 3)
- AlertDispatcher: Crisis alert routing (Phase 3)

USAGE:
    from src.managers import (
        create_config_manager,
        create_secrets_manager,
    )
    from src.managers.discord import (
        create_discord_manager,
        create_channel_config_manager,
    )
    from src.managers.nlp import create_nlp_client_manager
    from src.managers.storage import (
        create_redis_manager,
        create_user_history_manager,
    )
    from src.managers.alerting import (
        create_cooldown_manager,
        create_embed_builder,
        create_alert_dispatcher,
    )
"""

# Module version
__version__ = "v5.0-3-1.0-1"

# =============================================================================
# Configuration Manager
# =============================================================================

from .config_manager import (
    ConfigManager,
    create_config_manager,
)

# =============================================================================
# Secrets Manager
# =============================================================================

from .secrets_manager import (
    SecretsManager,
    create_secrets_manager,
    get_secrets_manager,
    get_secret,
    SecretNotFoundError,
    KNOWN_SECRETS,
)

# =============================================================================
# Discord Managers (Phase 1)
# =============================================================================

from .discord import (
    DiscordManager,
    create_discord_manager,
    ChannelConfigManager,
    create_channel_config_manager,
)

# =============================================================================
# NLP Managers (Phase 1)
# =============================================================================

from .nlp import (
    NLPClientManager,
    NLPClientError,
    create_nlp_client_manager,
)

# =============================================================================
# Storage Managers (Phase 2)
# =============================================================================

from .storage import (
    RedisManager,
    create_redis_manager,
    UserHistoryManager,
    create_user_history_manager,
    STORABLE_SEVERITIES,
)

# =============================================================================
# Alerting Managers (Phase 3)
# =============================================================================

from .alerting import (
    CooldownManager,
    create_cooldown_manager,
    EmbedBuilder,
    create_embed_builder,
    AlertDispatcher,
    create_alert_dispatcher,
)

# =============================================================================
# Public API
# =============================================================================

__all__ = [
    "__version__",
    # Config
    "ConfigManager",
    "create_config_manager",
    # Secrets
    "SecretsManager",
    "create_secrets_manager",
    "get_secrets_manager",
    "get_secret",
    "SecretNotFoundError",
    "KNOWN_SECRETS",
    # Discord (Phase 1)
    "DiscordManager",
    "create_discord_manager",
    "ChannelConfigManager",
    "create_channel_config_manager",
    # NLP (Phase 1)
    "NLPClientManager",
    "NLPClientError",
    "create_nlp_client_manager",
    # Storage (Phase 2)
    "RedisManager",
    "create_redis_manager",
    "UserHistoryManager",
    "create_user_history_manager",
    "STORABLE_SEVERITIES",
    # Alerting (Phase 3)
    "CooldownManager",
    "create_cooldown_manager",
    "EmbedBuilder",
    "create_embed_builder",
    "AlertDispatcher",
    "create_alert_dispatcher",
]
