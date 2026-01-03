"""
Ash-Bot: Crisis Detection Discord Bot for The Alphabet Cartel Discord Community
CORE PRINCIPLE:
******************  CORE SYSTEM VISION (Never to be violated):  ****************
Ash-Bot is a CRISIS DETECTION DISCORD BOT that:
1. **PRIMARY**: Monitors all messages within our discord server and sends them to our NLP server for semantic classification.
2. **SECONDARY**: If the NLP server detects a crisis, the bot alerts the appropriate staff members within the Crisis Response Team (CRT) using "pings" (@crisis_response) to the CRT role within the crisis-response channel utilizing discord's embeds feature to show crisis details based on the NLP determined severity of the crisis.
3. **TERTIARY**: Tracks historical patterns and messages and sends them to our NLP server for semantic classification to determine if there is a pattern of escalation over time.
4. **PURPOSE**: To detect crisis messages in Discord community communications.
********************************************************************************
Managers Package for Ash-Bot Service
---
FILE VERSION: v5.0
LAST MODIFIED: 2026-01-03
PHASE: Phase 1
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-bot
Community: The Alphabet Cartel - https://discord.gg/alphabetcartel | https://alphabetcartel.org

This package contains resource managers for Ash-Bot:

MANAGERS:
- ConfigManager: Configuration loading and validation

USAGE:
    from src.managers import create_config_manager, create_secrets_manager

    config = create_config_manager(environment="production")
    secrets = create_secrets_manager(environment="production")
"""

# Module version
__version__ = "v5.0-6-3.0-1"

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
]
