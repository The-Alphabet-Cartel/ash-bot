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
Health Routes Tests
---
FILE VERSION: v5.0-5-5.4-1
LAST MODIFIED: 2026-01-04
PHASE: Phase 5 - Production Hardening
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-bot
Community: The Alphabet Cartel - https://discord.gg/alphabetcartel | https://alphabetcartel.org
============================================================================
TEST COVERAGE:
- HealthRoutes initialization
- Liveness endpoint (/health)
- Readiness endpoint (/health/ready)
- Detailed health endpoint (/health/detailed)
- Metrics endpoint (/metrics)
- HealthServer lifecycle
- Kubernetes aliases (/healthz, /readyz)
- Error handling

USAGE:
    pytest tests/test_api/test_health_routes.py -v
"""

import asyncio
from datetime import datetime
from typing import Dict, Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiohttp import web
from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop

# Import test targets
from src.api.health_routes import (
    HealthRoutes,
    HealthServer,
    create_health_routes,
    create_health_server,
)
from src.managers.health.health_manager import (
    HealthManager,
    HealthStatus,
    ComponentStatus,
    ComponentHealth,
    SystemHealth,
)


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def mock_health_manager():
    """Create mock HealthManager that returns healthy status."""
    manager = MagicMock(spec=HealthManager)
    manager.check_liveness = AsyncMock(return_value=True)
    manager.check_readiness = AsyncMock(return_value=True)
    
    # Create healthy system health
    healthy_system = SystemHealth(
        status=HealthStatus.HEALTHY,
        components={
            "discord": ComponentHealth(
                name="discord",
                status=ComponentStatus.UP,
                message="Connected and ready",
                last_check=datetime.utcnow(),
                latency_ms=5.0,
            ),
            "nlp": ComponentHealth(
                name="nlp",
                status=ComponentStatus.UP,
                message="NLP API responding",
                last_check=datetime.utcnow(),
                latency_ms=25.0,
            ),
        },
        uptime_seconds=3600.0,
        version="5.0.0",
        timestamp=datetime.utcnow(),
        degradation_reasons=[],
    )
    manager.check_health = AsyncMock(return_value=healthy_system)
    
    return manager


@pytest.fixture
def mock_health_manager_unhealthy():
    """Create mock HealthManager that returns unhealthy status."""
    manager = MagicMock(spec=HealthManager)
    manager.check_liveness = AsyncMock(return_value=True)
    manager.check_readiness = AsyncMock(return_value=False)
    
    # Create unhealthy system health
    unhealthy_system = SystemHealth(
        status=HealthStatus.UNHEALTHY,
        components={
            "discord": ComponentHealth(
                name="discord",
                status=ComponentStatus.DOWN,
                message="Discord disconnected",
                last_check=datetime.utcnow(),
            ),
        },
        uptime_seconds=100.0,
        version="5.0.0",
        timestamp=datetime.utcnow(),
        degradation_reasons=["Discord connection unavailable"],
    )
    manager.check_health = AsyncMock(return_value=unhealthy_system)
    
    return manager


@pytest.fixture
def mock_health_manager_degraded():
    """Create mock HealthManager that returns degraded status."""
    manager = MagicMock(spec=HealthManager)
    manager.check_liveness = AsyncMock(return_value=True)
    manager.check_readiness = AsyncMock(return_value=True)
    
    # Create degraded system health
    degraded_system = SystemHealth(
        status=HealthStatus.DEGRADED,
        components={
            "discord": ComponentHealth(
                name="discord",
                status=ComponentStatus.UP,
                message="Connected",
                last_check=datetime.utcnow(),
            ),
            "nlp": ComponentHealth(
                name="nlp",
                status=ComponentStatus.DOWN,
                message="NLP unavailable",
                last_check=datetime.utcnow(),
            ),
        },
        uptime_seconds=500.0,
        version="5.0.0",
        timestamp=datetime.utcnow(),
        degradation_reasons=["NLP unavailable"],
    )
    manager.check_health = AsyncMock(return_value=degraded_system)
    
    return manager


@pytest.fixture
def mock_metrics_manager():
    """Create mock MetricsManager."""
    manager = MagicMock()
    manager.export_prometheus = MagicMock(return_value="""# HELP messages_processed_total Total messages processed
# TYPE messages_processed_total counter
messages_processed_total 1000
""")
    manager.export_json = MagicMock(return_value={
        "counters": {"messages_processed": 1000},
        "gauges": {"active_sessions": 5},
    })
    return manager


@pytest.fixture
def health_routes(mock_health_manager, mock_metrics_manager):
    """Create HealthRoutes with mocks."""
    return create_health_routes(
        health_manager=mock_health_manager,
        metrics_manager=mock_metrics_manager,
    )


@pytest.fixture
def health_routes_no_metrics(mock_health_manager):
    """Create HealthRoutes without metrics manager."""
    return create_health_routes(
        health_manager=mock_health_manager,
        metrics_manager=None,
    )


# =============================================================================
# Test: HealthRoutes Initialization
# =============================================================================


class TestHealthRoutesInit:
    """Tests for HealthRoutes initialization."""

    def test_init_with_both_managers(self, mock_health_manager, mock_metrics_manager):
        """Test initialization with both managers."""
        routes = HealthRoutes(
            health_manager=mock_health_manager,
            metrics_manager=mock_metrics_manager,
        )
        
        assert routes._health is mock_health_manager
        assert routes._metrics is mock_metrics_manager

    def test_init_without_metrics(self, mock_health_manager):
        """Test initialization without metrics manager."""
        routes = HealthRoutes(
            health_manager=mock_health_manager,
            metrics_manager=None,
        )
        
        assert routes._health is mock_health_manager
        assert routes._metrics is None

    def test_factory_function(self, mock_health_manager, mock_metrics_manager):
        """Test factory function creates routes correctly."""
        routes = create_health_routes(
            health_manager=mock_health_manager,
            metrics_manager=mock_metrics_manager,
        )
        
        assert isinstance(routes, HealthRoutes)
        assert routes._health is mock_health_manager

    def test_repr(self, health_routes):
        """Test string representation."""
        repr_str = repr(health_routes)
        assert "HealthRoutes" in repr_str
        assert "has_metrics=True" in repr_str


# =============================================================================
# Test: Route Setup
# =============================================================================


class TestRouteSetup:
    """Tests for route registration."""

    def test_setup_routes_registers_all_endpoints(self, health_routes):
        """Test that all endpoints are registered."""
        app = web.Application()
        health_routes.setup_routes(app)
        
        # Get all registered routes
        routes = [r.resource.canonical for r in app.router.routes()]
        
        assert "/health" in routes
        assert "/health/ready" in routes
        assert "/health/detailed" in routes
        assert "/metrics" in routes
        assert "/healthz" in routes  # Kubernetes alias
        assert "/readyz" in routes   # Kubernetes alias


# =============================================================================
# Test: Liveness Endpoint
# =============================================================================


class TestLivenessEndpoint:
    """Tests for /health endpoint."""

    @pytest.mark.asyncio
    async def test_liveness_returns_200_when_alive(self, health_routes):
        """Test liveness returns 200 when service is alive."""
        app = web.Application()
        health_routes.setup_routes(app)
        
        from aiohttp.test_utils import TestClient, TestServer
        
        async with TestClient(TestServer(app)) as client:
            resp = await client.get("/health")
            assert resp.status == 200
            
            data = await resp.json()
            assert data["status"] == "alive"
            assert "timestamp" in data

    @pytest.mark.asyncio
    async def test_healthz_alias_works(self, health_routes):
        """Test /healthz Kubernetes alias."""
        app = web.Application()
        health_routes.setup_routes(app)
        
        from aiohttp.test_utils import TestClient, TestServer
        
        async with TestClient(TestServer(app)) as client:
            resp = await client.get("/healthz")
            assert resp.status == 200
            
            data = await resp.json()
            assert data["status"] == "alive"


# =============================================================================
# Test: Readiness Endpoint
# =============================================================================


class TestReadinessEndpoint:
    """Tests for /health/ready endpoint."""

    @pytest.mark.asyncio
    async def test_readiness_returns_200_when_ready(self, health_routes):
        """Test readiness returns 200 when service is ready."""
        app = web.Application()
        health_routes.setup_routes(app)
        
        from aiohttp.test_utils import TestClient, TestServer
        
        async with TestClient(TestServer(app)) as client:
            resp = await client.get("/health/ready")
            assert resp.status == 200
            
            data = await resp.json()
            assert data["ready"] is True
            assert "timestamp" in data

    @pytest.mark.asyncio
    async def test_readiness_returns_503_when_not_ready(
        self, mock_health_manager_unhealthy, mock_metrics_manager
    ):
        """Test readiness returns 503 when service is not ready."""
        routes = create_health_routes(
            health_manager=mock_health_manager_unhealthy,
            metrics_manager=mock_metrics_manager,
        )
        
        app = web.Application()
        routes.setup_routes(app)
        
        from aiohttp.test_utils import TestClient, TestServer
        
        async with TestClient(TestServer(app)) as client:
            resp = await client.get("/health/ready")
            assert resp.status == 503
            
            data = await resp.json()
            assert data["ready"] is False
            assert "message" in data

    @pytest.mark.asyncio
    async def test_readyz_alias_works(self, health_routes):
        """Test /readyz Kubernetes alias."""
        app = web.Application()
        health_routes.setup_routes(app)
        
        from aiohttp.test_utils import TestClient, TestServer
        
        async with TestClient(TestServer(app)) as client:
            resp = await client.get("/readyz")
            assert resp.status == 200


# =============================================================================
# Test: Detailed Health Endpoint
# =============================================================================


class TestDetailedHealthEndpoint:
    """Tests for /health/detailed endpoint."""

    @pytest.mark.asyncio
    async def test_detailed_returns_full_status(self, health_routes):
        """Test detailed endpoint returns full status."""
        app = web.Application()
        health_routes.setup_routes(app)
        
        from aiohttp.test_utils import TestClient, TestServer
        
        async with TestClient(TestServer(app)) as client:
            resp = await client.get("/health/detailed")
            assert resp.status == 200
            
            data = await resp.json()
            assert data["status"] == "healthy"
            assert "components" in data
            assert "uptime_seconds" in data
            assert "version" in data
            assert "timestamp" in data
            assert data["is_healthy"] is True
            assert data["is_ready"] is True

    @pytest.mark.asyncio
    async def test_detailed_returns_503_when_unhealthy(
        self, mock_health_manager_unhealthy, mock_metrics_manager
    ):
        """Test detailed returns 503 when unhealthy."""
        routes = create_health_routes(
            health_manager=mock_health_manager_unhealthy,
            metrics_manager=mock_metrics_manager,
        )
        
        app = web.Application()
        routes.setup_routes(app)
        
        from aiohttp.test_utils import TestClient, TestServer
        
        async with TestClient(TestServer(app)) as client:
            resp = await client.get("/health/detailed")
            assert resp.status == 503
            
            data = await resp.json()
            assert data["status"] == "unhealthy"
            assert data["is_healthy"] is False

    @pytest.mark.asyncio
    async def test_detailed_returns_200_when_degraded(
        self, mock_health_manager_degraded, mock_metrics_manager
    ):
        """Test detailed returns 200 when degraded (still operational)."""
        routes = create_health_routes(
            health_manager=mock_health_manager_degraded,
            metrics_manager=mock_metrics_manager,
        )
        
        app = web.Application()
        routes.setup_routes(app)
        
        from aiohttp.test_utils import TestClient, TestServer
        
        async with TestClient(TestServer(app)) as client:
            resp = await client.get("/health/detailed")
            assert resp.status == 200  # Degraded is still operational
            
            data = await resp.json()
            assert data["status"] == "degraded"
            assert len(data["degradation_reasons"]) > 0

    @pytest.mark.asyncio
    async def test_detailed_includes_component_info(self, health_routes):
        """Test detailed includes component information."""
        app = web.Application()
        health_routes.setup_routes(app)
        
        from aiohttp.test_utils import TestClient, TestServer
        
        async with TestClient(TestServer(app)) as client:
            resp = await client.get("/health/detailed")
            data = await resp.json()
            
            components = data["components"]
            assert "discord" in components
            assert components["discord"]["status"] == "up"
            assert "message" in components["discord"]


# =============================================================================
# Test: Metrics Endpoint
# =============================================================================


class TestMetricsEndpoint:
    """Tests for /metrics endpoint."""

    @pytest.mark.asyncio
    async def test_metrics_returns_prometheus_format(self, health_routes):
        """Test metrics returns Prometheus format."""
        app = web.Application()
        health_routes.setup_routes(app)
        
        from aiohttp.test_utils import TestClient, TestServer
        
        async with TestClient(TestServer(app)) as client:
            resp = await client.get("/metrics")
            assert resp.status == 200
            assert "text/plain" in resp.content_type
            
            text = await resp.text()
            assert "# HELP" in text
            assert "messages_processed_total" in text

    @pytest.mark.asyncio
    async def test_metrics_without_manager(self, health_routes_no_metrics):
        """Test metrics endpoint when no metrics manager configured."""
        app = web.Application()
        health_routes_no_metrics.setup_routes(app)
        
        from aiohttp.test_utils import TestClient, TestServer
        
        async with TestClient(TestServer(app)) as client:
            resp = await client.get("/metrics")
            assert resp.status == 200
            
            text = await resp.text()
            assert "No metrics configured" in text


# =============================================================================
# Test: Error Handling
# =============================================================================


class TestErrorHandling:
    """Tests for error handling in endpoints."""

    @pytest.mark.asyncio
    async def test_detailed_handles_exception(self, mock_health_manager, mock_metrics_manager):
        """Test detailed endpoint handles exceptions gracefully."""
        # Make health check raise an exception
        mock_health_manager.check_health = AsyncMock(
            side_effect=Exception("Database error")
        )
        
        routes = create_health_routes(
            health_manager=mock_health_manager,
            metrics_manager=mock_metrics_manager,
        )
        
        app = web.Application()
        routes.setup_routes(app)
        
        from aiohttp.test_utils import TestClient, TestServer
        
        async with TestClient(TestServer(app)) as client:
            resp = await client.get("/health/detailed")
            assert resp.status == 500
            
            data = await resp.json()
            assert data["status"] == "error"
            assert "Database error" in data["message"]

    @pytest.mark.asyncio
    async def test_metrics_handles_exception(self, mock_health_manager, mock_metrics_manager):
        """Test metrics endpoint handles exceptions gracefully."""
        # Make export raise an exception
        mock_metrics_manager.export_prometheus = MagicMock(
            side_effect=Exception("Export failed")
        )
        
        routes = create_health_routes(
            health_manager=mock_health_manager,
            metrics_manager=mock_metrics_manager,
        )
        
        app = web.Application()
        routes.setup_routes(app)
        
        from aiohttp.test_utils import TestClient, TestServer
        
        async with TestClient(TestServer(app)) as client:
            resp = await client.get("/metrics")
            assert resp.status == 500
            
            text = await resp.text()
            assert "Error exporting metrics" in text


# =============================================================================
# Test: HealthServer
# =============================================================================


class TestHealthServer:
    """Tests for HealthServer lifecycle."""

    def test_server_init(self, health_routes):
        """Test server initialization."""
        server = create_health_server(health_routes, port=9090)
        
        assert server.port == 9090
        assert server.host == "0.0.0.0"
        assert server.is_running is False
        assert server.url == "http://0.0.0.0:9090"

    def test_server_repr(self, health_routes):
        """Test server string representation."""
        server = create_health_server(health_routes, port=8080)
        repr_str = repr(server)
        
        assert "HealthServer" in repr_str
        assert "8080" in repr_str
        assert "stopped" in repr_str

    @pytest.mark.asyncio
    async def test_server_start_stop(self, health_routes):
        """Test server start and stop lifecycle."""
        server = create_health_server(health_routes, port=0)  # Port 0 = auto-assign
        
        assert server.is_running is False
        
        await server.start()
        assert server.is_running is True
        
        await server.stop()
        assert server.is_running is False

    @pytest.mark.asyncio
    async def test_server_double_start_raises(self, health_routes):
        """Test that starting twice raises error."""
        server = create_health_server(health_routes, port=0)
        
        await server.start()
        
        try:
            with pytest.raises(RuntimeError, match="already running"):
                await server.start()
        finally:
            await server.stop()

    @pytest.mark.asyncio
    async def test_server_stop_when_not_running(self, health_routes):
        """Test stopping when not running is safe."""
        server = create_health_server(health_routes, port=0)
        
        # Should not raise
        await server.stop()
        assert server.is_running is False


# =============================================================================
# Test: Factory Functions
# =============================================================================


class TestFactoryFunctions:
    """Tests for factory functions."""

    def test_create_health_routes(self, mock_health_manager):
        """Test create_health_routes factory."""
        routes = create_health_routes(mock_health_manager)
        assert isinstance(routes, HealthRoutes)

    def test_create_health_routes_with_metrics(
        self, mock_health_manager, mock_metrics_manager
    ):
        """Test create_health_routes with metrics."""
        routes = create_health_routes(mock_health_manager, mock_metrics_manager)
        assert routes._metrics is mock_metrics_manager

    def test_create_health_server(self, health_routes):
        """Test create_health_server factory."""
        server = create_health_server(health_routes)
        assert isinstance(server, HealthServer)
        assert server.port == 8080  # Default port

    def test_create_health_server_custom_port(self, health_routes):
        """Test create_health_server with custom port."""
        server = create_health_server(health_routes, port=9000)
        assert server.port == 9000
