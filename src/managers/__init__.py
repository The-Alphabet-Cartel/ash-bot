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
----------------------------------------------------------------------------
FILE VERSION: v5.0-0-1.0-1
LAST MODIFIED: 2026-01-03
PHASE: Phase 0 - Foundation
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-bot
============================================================================

This package contains resource managers for Ash-Bot:

MANAGERS:
- ConfigManager: Configuration loading and validation
- SecretsManager: Docker secrets access

USAGE:
    from src.managers import create_config_manager, create_secrets_manager

    config = create_config_manager(environment="production")
    secrets = create_secrets_manager()
"""

# Module version
__version__ = "v5.0-0-1.0-1"

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
