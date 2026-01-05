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
Utilities Package for Ash-Bot Service
---
FILE VERSION: v5.0-5-5.1-1
LAST MODIFIED: 2026-01-04
PHASE: Phase 5 - Production Hardening
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-bot
Community: The Alphabet Cartel - https://discord.gg/alphabetcartel | https://alphabetcartel.org
============================================================================
PACKAGE CONTENTS:
- circuit_breaker: Circuit breaker pattern for preventing cascading failures
- retry: Retry utilities with exponential backoff

USAGE:
    from src.utils import CircuitBreaker, CircuitOpenError
    from src.utils import retry_async, RetryConfig
"""

# Module version
__version__ = "v5.0-5-5.1-1"

# =============================================================================
# Circuit Breaker
# =============================================================================

from .circuit_breaker import (
    CircuitBreaker,
    CircuitState,
    CircuitBreakerConfig,
    CircuitOpenError,
    create_circuit_breaker,
)

# =============================================================================
# Retry Utilities
# =============================================================================

from .retry import (
    RetryConfig,
    RetryError,
    retry_async,
    with_retry,
)

# =============================================================================
# Public API
# =============================================================================

__all__ = [
    "__version__",
    # Circuit Breaker
    "CircuitBreaker",
    "CircuitState",
    "CircuitBreakerConfig",
    "CircuitOpenError",
    "create_circuit_breaker",
    # Retry
    "RetryConfig",
    "RetryError",
    "retry_async",
    "with_retry",
]
