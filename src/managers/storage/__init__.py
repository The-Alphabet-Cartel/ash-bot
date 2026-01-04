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
FILE VERSION: v5.0-2-1.0-1
LAST MODIFIED: 2026-01-03
PHASE: Phase 2 - Redis History Storage
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-bot
Community: The Alphabet Cartel - https://discord.gg/alphabetcartel | https://alphabetcartel.org
============================================================================

This package contains storage managers for Ash-Bot:

MANAGERS:
- RedisManager: Redis connection and low-level operations
- UserHistoryManager: User message history storage and retrieval

USAGE:
    from src.managers.storage import (
        create_redis_manager,
        create_user_history_manager,
    )

    # Initialize Redis connection
    redis = create_redis_manager(config_manager, secrets_manager)
    await redis.connect()

    # Initialize history manager
    history = create_user_history_manager(config_manager, redis)

    # Store and retrieve user history
    await history.add_message(guild_id, user_id, message, analysis_result)
    recent = await history.get_history(guild_id, user_id, limit=20)
"""

# Module version
__version__ = "v5.0-2-1.0-1"

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
]
