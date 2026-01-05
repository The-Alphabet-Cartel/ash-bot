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
Ash-Bot Source Package
---
FILE VERSION: v5.0-5-5.4-1
LAST MODIFIED: 2026-01-04
PHASE: Phase 5 - Production Hardening
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-bot
Community: The Alphabet Cartel - https://discord.gg/alphabetcartel | https://alphabetcartel.org
============================================================================
This is the main source package for Ash-Bot containing:
- managers: Configuration and resource management
- models: Data classes and types
- prompts: AI system prompts
- views: Discord UI components
- utils: Utility functions (circuit breaker, retry logic)
- api: HTTP endpoints for health checks and metrics

USAGE:
    from src.managers import create_config_manager
    from src.models import CrisisAnalysisResult
    from src.utils import CircuitBreaker, retry_async
    from src.api import create_health_routes, create_health_server
"""

__version__ = "5.0.0"
__author__ = "The Alphabet Cartel"
__email__ = "dev@alphabetcartel.org"
__url__ = "https://github.com/the-alphabet-cartel/ash-bot"

# Package metadata
__all__ = [
    "__version__",
    "__author__",
    "__email__",
    "__url__",
]
