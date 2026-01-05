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
Storage Managers Package for Ash-Bot Service
----------------------------------------------------------------------------
FILE VERSION: v5.0-8-3.0-1
LAST MODIFIED: 2026-01-05
PHASE: Phase 8 - Metrics & Reporting (Step 8.3)
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-bot
Community: The Alphabet Cartel - https://discord.gg/alphabetcartel | https://alphabetcartel.org
============================================================================

This package contains storage managers for Ash-Bot:

MANAGERS:
- RedisManager: Redis connection and low-level operations
- UserHistoryManager: User message history storage and retrieval
- DataRetentionManager: Automated data cleanup and retention (Phase 8.3)

USAGE:
    from src.managers.storage import (
        create_redis_manager,
        create_user_history_manager,
        create_data_retention_manager,
    )

    # Initialize Redis connection
    redis = create_redis_manager(config_manager, secrets_manager)
    await redis.connect()

    # Initialize history manager
    history = create_user_history_manager(config_manager, redis)

    # Initialize data retention manager (Phase 8.3)
    retention = create_data_retention_manager(config_manager, redis)
    await retention.start()  # Start background cleanup scheduler

    # Store and retrieve user history
    await history.add_message(guild_id, user_id, message, analysis_result)
    recent = await history.get_history(guild_id, user_id, limit=20)
"""

# Module version
__version__ = "v5.0-8-3.0-1"

# =============================================================================
# Redis Manager
# =============================================================================

from .redis_manager import (
    RedisManager,
    create_redis_manager,
)

# =============================================================================
# User History Manager
# =============================================================================

from .user_history_manager import (
    UserHistoryManager,
    create_user_history_manager,
    STORABLE_SEVERITIES,
)

# =============================================================================
# Data Retention Manager (Phase 8.3)
# =============================================================================

from .data_retention_manager import (
    DataRetentionManager,
    create_data_retention_manager,
    CleanupStats,
    StorageStats,
    KEY_PREFIX_ALERT_METRICS,
    KEY_PREFIX_DAILY_AGGREGATE,
    KEY_PREFIX_ALERT_LOOKUP,
    KEY_PREFIX_USER_HISTORY,
    KEY_PREFIX_USER_OPTOUT,
    KEY_PREFIX_ASH_SESSION,
)

# =============================================================================
# Public API
# =============================================================================

__all__ = [
    "__version__",
    # Redis
    "RedisManager",
    "create_redis_manager",
    # User History
    "UserHistoryManager",
    "create_user_history_manager",
    "STORABLE_SEVERITIES",
    # Data Retention (Phase 8.3)
    "DataRetentionManager",
    "create_data_retention_manager",
    "CleanupStats",
    "StorageStats",
    "KEY_PREFIX_ALERT_METRICS",
    "KEY_PREFIX_DAILY_AGGREGATE",
    "KEY_PREFIX_ALERT_LOOKUP",
    "KEY_PREFIX_USER_HISTORY",
    "KEY_PREFIX_USER_OPTOUT",
    "KEY_PREFIX_ASH_SESSION",
]
