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
Health Package for Ash-Bot Service
---
FILE VERSION: v5.0-5-5.3-1
LAST MODIFIED: 2026-01-04
PHASE: Phase 5 - Production Hardening
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-bot
Community: The Alphabet Cartel - https://discord.gg/alphabetcartel | https://alphabetcartel.org
============================================================================
PACKAGE CONTENTS:
- HealthManager: Coordinates health checks across components
- HealthStatus: Overall system health status enum
- ComponentStatus: Individual component status enum
- ComponentHealth: Component health report dataclass
- SystemHealth: Full system health report dataclass

USAGE:
    from src.managers.health import create_health_manager

    health = create_health_manager(
        discord_manager=discord_mgr,
        nlp_client=nlp_client,
    )

    status = await health.check_health()
    print(f"Status: {status.status.value}")
"""

# Module version
__version__ = "v5.0-5-5.3-1"

from .health_manager import (
    HealthManager,
    HealthStatus,
    ComponentStatus,
    ComponentHealth,
    SystemHealth,
    create_health_manager,
)

__all__ = [
    "__version__",
    "HealthManager",
    "HealthStatus",
    "ComponentStatus",
    "ComponentHealth",
    "SystemHealth",
    "create_health_manager",
]
