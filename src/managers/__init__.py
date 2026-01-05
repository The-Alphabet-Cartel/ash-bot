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
FILE VERSION: v5.0-9-1.0-1
LAST MODIFIED: 2026-01-05
PHASE: Phase 9 - CRT Workflow Enhancements (Step 9.1)
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
- ClaudeClientManager: Claude API client (Phase 4)
- AshSessionManager: Conversation session management (Phase 4)
- AshPersonalityManager: Ash personality and responses (Phase 4)
- MetricsManager: Operational metrics collection (Phase 5)
- HealthManager: Component health monitoring (Phase 5)
- SlashCommandManager: CRT slash commands (Phase 9)

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
    from src.managers.ash import (
        create_claude_client_manager,
        create_ash_session_manager,
        create_ash_personality_manager,
    )
    from src.managers.metrics import create_metrics_manager
    from src.managers.health import create_health_manager
    from src.managers.commands import create_slash_command_manager
"""

# Module version
__version__ = "v5.0-9-1.0-1"

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
# Ash AI Managers (Phase 4)
# =============================================================================

from .ash import (
    ClaudeClientManager,
    create_claude_client_manager,
    ClaudeAPIError,
    ClaudeConfigError,
    AshSession,
    AshSessionManager,
    create_ash_session_manager,
    SessionExistsError,
    SessionNotFoundError,
    AshPersonalityManager,
    create_ash_personality_manager,
)

# =============================================================================
# Metrics Manager (Phase 5)
# =============================================================================

from .metrics import (
    MetricsManager,
    create_metrics_manager,
    Counter,
    Gauge,
    Histogram,
    LabeledCounter,
)

# =============================================================================
# Health Manager (Phase 5)
# =============================================================================

from .health import (
    HealthManager,
    HealthStatus,
    ComponentStatus,
    ComponentHealth,
    SystemHealth,
    create_health_manager,
)

# =============================================================================
# Commands Manager (Phase 9)
# =============================================================================

from .commands import (
    SlashCommandManager,
    create_slash_command_manager,
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
    # Ash AI (Phase 4)
    "ClaudeClientManager",
    "create_claude_client_manager",
    "ClaudeAPIError",
    "ClaudeConfigError",
    "AshSession",
    "AshSessionManager",
    "create_ash_session_manager",
    "SessionExistsError",
    "SessionNotFoundError",
    "AshPersonalityManager",
    "create_ash_personality_manager",
    # Metrics (Phase 5)
    "MetricsManager",
    "create_metrics_manager",
    "Counter",
    "Gauge",
    "Histogram",
    "LabeledCounter",
    # Health (Phase 5)
    "HealthManager",
    "HealthStatus",
    "ComponentStatus",
    "ComponentHealth",
    "SystemHealth",
    "create_health_manager",
    # Commands (Phase 9)
    "SlashCommandManager",
    "create_slash_command_manager",
]
