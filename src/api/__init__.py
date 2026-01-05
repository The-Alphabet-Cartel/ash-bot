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
API Package for Ash-Bot Service
---
FILE VERSION: v5.0-5-5.4-1
LAST MODIFIED: 2026-01-04
PHASE: Phase 5 - Production Hardening
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-bot
Community: The Alphabet Cartel - https://discord.gg/alphabetcartel | https://alphabetcartel.org
============================================================================
COMPONENTS:
- HealthRoutes: HTTP endpoints for health checks and metrics
- HealthServer: aiohttp server management

ENDPOINTS:
- GET /health          - Simple liveness check
- GET /health/ready    - Readiness check
- GET /health/detailed - Full component status
- GET /metrics         - Prometheus metrics

USAGE:
    from src.api import create_health_routes, HealthServer

    routes = create_health_routes(health_manager, metrics_manager)
    server = HealthServer(routes, port=8080)
    await server.start()
"""

# Module version
__version__ = "v5.0-5-5.4-1"

# =============================================================================
# Health Routes
# =============================================================================

from .health_routes import (
    HealthRoutes,
    HealthServer,
    create_health_routes,
    create_health_server,
)

# =============================================================================
# Public API
# =============================================================================

__all__ = [
    "__version__",
    # Routes
    "HealthRoutes",
    "create_health_routes",
    # Server
    "HealthServer",
    "create_health_server",
]
