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
Ash AI Managers Package for Ash-Bot Service
---
FILE VERSION: v5.0-4-5.0-1
LAST MODIFIED: 2026-01-04
PHASE: Phase 4 - Ash AI Integration
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-bot
Community: The Alphabet Cartel - https://discord.gg/alphabetcartel | https://alphabetcartel.org
============================================================================
This package contains managers for Ash AI personality and conversations:

MANAGERS:
- ClaudeClientManager: Claude API client for AI responses
- AshSessionManager: Conversation session lifecycle management
- AshPersonalityManager: Ash personality and response generation

USAGE:
    from src.managers.ash import (
        create_claude_client_manager,
        create_ash_session_manager,
        create_ash_personality_manager,
    )

    # Create Claude client
    claude_client = create_claude_client_manager(
        config_manager=config_manager,
        secrets_manager=secrets_manager,
    )

    # Create session manager
    session_manager = create_ash_session_manager(
        config_manager=config_manager,
        bot=bot,
    )

    # Create personality manager
    personality_manager = create_ash_personality_manager(
        config_manager=config_manager,
        claude_client=claude_client,
    )
"""

# Module version
__version__ = "v5.0-4-5.0-1"

# =============================================================================
# Claude Client Manager
# =============================================================================

from .claude_client_manager import (
    ClaudeClientManager,
    create_claude_client_manager,
    ClaudeAPIError,
    ClaudeConfigError,
)

# =============================================================================
# Ash Session Manager
# =============================================================================

from .ash_session_manager import (
    AshSession,
    AshSessionManager,
    create_ash_session_manager,
    SessionExistsError,
    SessionNotFoundError,
)

# =============================================================================
# Ash Personality Manager
# =============================================================================

from .ash_personality_manager import (
    AshPersonalityManager,
    create_ash_personality_manager,
)

# =============================================================================
# Public API
# =============================================================================

__all__ = [
    "__version__",
    # Claude Client
    "ClaudeClientManager",
    "create_claude_client_manager",
    "ClaudeAPIError",
    "ClaudeConfigError",
    # Session Manager
    "AshSession",
    "AshSessionManager",
    "create_ash_session_manager",
    "SessionExistsError",
    "SessionNotFoundError",
    # Personality Manager
    "AshPersonalityManager",
    "create_ash_personality_manager",
]
