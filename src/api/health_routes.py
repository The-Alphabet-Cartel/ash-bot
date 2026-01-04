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
Health Routes for Ash-Bot Service
---
FILE VERSION: v5.0-5-5.4-1
LAST MODIFIED: 2026-01-04
PHASE: Phase 5 - Production Hardening
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-bot
Community: The Alphabet Cartel - https://discord.gg/alphabetcartel | https://alphabetcartel.org
============================================================================
RESPONSIBILITIES:
- Provide HTTP endpoints for health checks
- Expose Prometheus metrics endpoint
- Enable Kubernetes liveness/readiness probes
- Return appropriate HTTP status codes

ENDPOINTS:
- GET /health          - Simple liveness (always 200 if running)
- GET /health/ready    - Readiness check (200/503)
- GET /health/detailed - Full status JSON (200/503)
- GET /metrics         - Prometheus metrics (200)

HTTP CODES:
- 200: Healthy/Ready
- 503: Unhealthy/Not Ready

USAGE:
    from src.api import create_health_routes, create_health_server

    routes = create_health_routes(health_manager, metrics_manager)
    server = create_health_server(routes, port=8080)
    
    await server.start()
    # ... later
    await server.stop()
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Any, Dict, Optional, TYPE_CHECKING

from aiohttp import web

# Module version
__version__ = "v5.0-5-5.4-1"

# Initialize logger
logger = logging.getLogger(__name__)

# Type checking imports
if TYPE_CHECKING:
    from src.managers.health import HealthManager
    from src.managers.metrics import MetricsManager


# =============================================================================
# Health Routes
# =============================================================================


class HealthRoutes:
    """
    HTTP routes for health checks and metrics.

    Provides endpoints for Kubernetes probes and monitoring systems.

    Endpoints:
        GET /health          - Liveness probe (always 200)
        GET /health/ready    - Readiness probe (200/503)
        GET /health/detailed - Full component status
        GET /metrics         - Prometheus format metrics

    Attributes:
        health_manager: Health check coordinator
        metrics_manager: Metrics collection manager

    Example:
        >>> routes = create_health_routes(health_mgr, metrics_mgr)
        >>> app = web.Application()
        >>> routes.setup_routes(app)
    """

    def __init__(
        self,
        health_manager: "HealthManager",
        metrics_manager: Optional["MetricsManager"] = None,
    ):
        """
        Initialize HealthRoutes with managers.

        Args:
            health_manager: Health check coordinator
            metrics_manager: Optional metrics manager for /metrics endpoint
        """
        self._health = health_manager
        self._metrics = metrics_manager

        logger.debug("HealthRoutes initialized")

    # =========================================================================
    # Route Setup
    # =========================================================================

    def setup_routes(self, app: web.Application) -> None:
        """
        Register routes with aiohttp application.

        Args:
            app: aiohttp Application instance
        """
        app.router.add_get("/health", self.liveness)
        app.router.add_get("/health/ready", self.readiness)
        app.router.add_get("/health/detailed", self.detailed)
        app.router.add_get("/metrics", self.metrics)

        # Also add /healthz for Kubernetes compatibility
        app.router.add_get("/healthz", self.liveness)
        app.router.add_get("/readyz", self.readiness)

        logger.info("✅ Health routes registered")

    # =========================================================================
    # Endpoint Handlers
    # =========================================================================

    async def liveness(self, request: web.Request) -> web.Response:
        """
        Simple liveness check endpoint.

        Returns 200 if the process is running.
        This is the most basic health check - if this returns,
        the process is alive.

        Args:
            request: aiohttp Request object

        Returns:
            JSON response with status and timestamp
        """
        is_alive = await self._health.check_liveness()

        body = {
            "status": "alive" if is_alive else "dead",
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }

        return web.json_response(body, status=200 if is_alive else 503)

    async def readiness(self, request: web.Request) -> web.Response:
        """
        Readiness check endpoint.

        Returns 200 if the bot is ready to serve traffic.
        Returns 503 if not ready (e.g., Discord not connected).

        This is used by load balancers and Kubernetes to determine
        if traffic should be routed to this instance.

        Args:
            request: aiohttp Request object

        Returns:
            JSON response with readiness status
        """
        is_ready = await self._health.check_readiness()

        body = {
            "ready": is_ready,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }

        if not is_ready:
            body["message"] = "Service not ready - Discord connection required"

        status_code = 200 if is_ready else 503
        return web.json_response(body, status=status_code)

    async def detailed(self, request: web.Request) -> web.Response:
        """
        Detailed health status endpoint.

        Returns comprehensive health information including:
        - Overall system status
        - Individual component statuses
        - Uptime and version info
        - Degradation reasons (if any)

        Args:
            request: aiohttp Request object

        Returns:
            JSON response with full health report
        """
        try:
            health = await self._health.check_health()
            body = health.to_dict()

            # Use 503 for unhealthy, 200 for healthy/degraded
            status_code = 503 if health.status.value == "unhealthy" else 200

            return web.json_response(body, status=status_code)

        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return web.json_response(
                {
                    "status": "error",
                    "message": str(e),
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                },
                status=500,
            )

    async def metrics(self, request: web.Request) -> web.Response:
        """
        Prometheus metrics endpoint.

        Returns metrics in Prometheus text format for scraping.
        If no metrics manager is configured, returns empty metrics.

        Args:
            request: aiohttp Request object

        Returns:
            Prometheus-formatted text response
        """
        if self._metrics is None:
            # Return empty metrics if no manager configured
            return web.Response(
                text="# No metrics configured\n",
                content_type="text/plain; version=0.0.4",
            )

        try:
            prometheus_text = self._metrics.export_prometheus()
            return web.Response(
                text=prometheus_text,
                content_type="text/plain; version=0.0.4",
            )

        except Exception as e:
            logger.error(f"Metrics export failed: {e}")
            return web.Response(
                text=f"# Error exporting metrics: {e}\n",
                content_type="text/plain; version=0.0.4",
                status=500,
            )

    # =========================================================================
    # Utility Methods
    # =========================================================================

    def __repr__(self) -> str:
        """String representation."""
        return f"HealthRoutes(has_metrics={self._metrics is not None})"


# =============================================================================
# Health Server
# =============================================================================


class HealthServer:
    """
    HTTP server for health endpoints.

    Manages the aiohttp server lifecycle for health checks and metrics.

    Attributes:
        routes: HealthRoutes instance
        host: Bind address
        port: Bind port

    Example:
        >>> server = create_health_server(routes, port=8080)
        >>> await server.start()
        >>> # ... server running ...
        >>> await server.stop()
    """

    def __init__(
        self,
        routes: HealthRoutes,
        host: str = "0.0.0.0",
        port: int = 8080,
    ):
        """
        Initialize HealthServer.

        Args:
            routes: HealthRoutes instance
            host: Host to bind to (default: 0.0.0.0)
            port: Port to bind to (default: 8080)
        """
        self._routes = routes
        self._host = host
        self._port = port
        self._app: Optional[web.Application] = None
        self._runner: Optional[web.AppRunner] = None
        self._site: Optional[web.TCPSite] = None
        self._running = False

        logger.debug(f"HealthServer initialized (port={port})")

    # =========================================================================
    # Properties
    # =========================================================================

    @property
    def is_running(self) -> bool:
        """Check if server is running."""
        return self._running

    @property
    def port(self) -> int:
        """Get configured port."""
        return self._port

    @property
    def host(self) -> str:
        """Get configured host."""
        return self._host

    @property
    def url(self) -> str:
        """Get server URL."""
        return f"http://{self._host}:{self._port}"

    # =========================================================================
    # Lifecycle
    # =========================================================================

    async def start(self) -> None:
        """
        Start the health server.

        Creates aiohttp application, sets up routes, and starts
        listening for connections.

        Raises:
            RuntimeError: If server is already running
        """
        if self._running:
            raise RuntimeError("Health server is already running")

        logger.info(f"🚀 Starting health server on {self._host}:{self._port}")

        # Create application
        self._app = web.Application()
        self._routes.setup_routes(self._app)

        # Setup runner
        self._runner = web.AppRunner(self._app)
        await self._runner.setup()

        # Create site
        self._site = web.TCPSite(
            self._runner,
            self._host,
            self._port,
        )
        await self._site.start()

        self._running = True
        logger.info(f"✅ Health server running at {self.url}")
        logger.info(f"   → Liveness:  {self.url}/health")
        logger.info(f"   → Readiness: {self.url}/health/ready")
        logger.info(f"   → Detailed:  {self.url}/health/detailed")
        logger.info(f"   → Metrics:   {self.url}/metrics")

    async def stop(self) -> None:
        """
        Stop the health server.

        Gracefully shuts down the server and cleans up resources.
        """
        if not self._running:
            logger.debug("Health server not running, nothing to stop")
            return

        logger.info("🛑 Stopping health server...")

        # Cleanup in reverse order
        if self._runner:
            await self._runner.cleanup()
            self._runner = None

        self._site = None
        self._app = None
        self._running = False

        logger.info("✅ Health server stopped")

    # =========================================================================
    # Utility Methods
    # =========================================================================

    def __repr__(self) -> str:
        """String representation."""
        status = "running" if self._running else "stopped"
        return f"HealthServer({self.url}, {status})"


# =============================================================================
# Factory Functions
# =============================================================================


def create_health_routes(
    health_manager: "HealthManager",
    metrics_manager: Optional["MetricsManager"] = None,
) -> HealthRoutes:
    """
    Factory function for HealthRoutes.

    Creates a HealthRoutes instance with manager references.
    Following Clean Architecture v5.1 Rule #1: Factory Functions.

    Args:
        health_manager: Health check coordinator
        metrics_manager: Optional metrics manager

    Returns:
        Configured HealthRoutes instance

    Example:
        >>> routes = create_health_routes(health_mgr)
        >>> routes = create_health_routes(health_mgr, metrics_mgr)
    """
    logger.info("🏭 Creating HealthRoutes")
    return HealthRoutes(
        health_manager=health_manager,
        metrics_manager=metrics_manager,
    )


def create_health_server(
    routes: HealthRoutes,
    host: str = "0.0.0.0",
    port: int = 8080,
) -> HealthServer:
    """
    Factory function for HealthServer.

    Creates a HealthServer instance with routes and configuration.
    Following Clean Architecture v5.1 Rule #1: Factory Functions.

    Args:
        routes: HealthRoutes instance
        host: Host to bind to (default: 0.0.0.0)
        port: Port to bind to (default: 8080)

    Returns:
        Configured HealthServer instance

    Example:
        >>> routes = create_health_routes(health_mgr)
        >>> server = create_health_server(routes, port=8080)
        >>> await server.start()
    """
    logger.info(f"🏭 Creating HealthServer (port={port})")
    return HealthServer(
        routes=routes,
        host=host,
        port=port,
    )


# =============================================================================
# Export public interface
# =============================================================================

__all__ = [
    "HealthRoutes",
    "HealthServer",
    "create_health_routes",
    "create_health_server",
]
