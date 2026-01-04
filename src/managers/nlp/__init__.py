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
NLP Managers Package for Ash-Bot Service
---
FILE VERSION: v5.0-1-1.1-1
LAST MODIFIED: 2026-01-03
PHASE: Phase 1 - Discord Connectivity
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-bot
Community: The Alphabet Cartel - https://discord.gg/alphabetcartel | https://alphabetcartel.org
============================================================================
This package contains NLP-related managers:
- NLPClientManager: Async HTTP client for Ash-NLP API

USAGE:
    from src.managers.nlp import create_nlp_client_manager

    nlp_client = create_nlp_client_manager(config_manager)
    result = await nlp_client.analyze_message("I'm feeling down today")
"""

# Module version
__version__ = "v5.0-1-1.1-1"

# =============================================================================
# NLP Client Manager
# =============================================================================
from .nlp_client_manager import (
    NLPClientManager,
    NLPClientError,
    create_nlp_client_manager,
)

# =============================================================================
# Public API
# =============================================================================
__all__ = [
    "__version__",
    # NLP Client Manager
    "NLPClientManager",
    "NLPClientError",
    "create_nlp_client_manager",
]
