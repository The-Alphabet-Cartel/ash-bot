"""
============================================================================
Ash-Bot: Crisis Detection Discord Bot
The Alphabet Cartel - https://discord.gg/alphabetcartel | alphabetcartel.org
============================================================================
Test Suite for Health Manager
---
FILE VERSION: v5.0-5-5.3-1
LAST MODIFIED: 2026-01-04
PHASE: Phase 5 - Production Hardening
Repository: https://github.com/the-alphabet-cartel/ash-bot
============================================================================
Tests for HealthManager and related classes.
"""

import asyncio
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, PropertyMock

import pytest

from src.managers.health import (
    HealthManager,
    HealthStatus,
    ComponentStatus,
    ComponentHealth,
    SystemHealth,
    create_health_manager,
)


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def mock_discord_manager():
    """Create mock Discord manager that is connected and ready."""
    mock = MagicMock()
    mock.is_connected = MagicMock(return_value=True)
    mock.is_ready = MagicMock(return_value=True)
    mock.guild_count = MagicMock(return_value=3)
    return mock


@pytest.fixture
def mock_discord_disconnected():
    """Create mock Discord manager that is disconnected."""
    mock = MagicMock()
    mock.is_connected = MagicMock(return_value=False)
    mock.is_ready = MagicMock(return_value=False)
    return mock


@pytest.fixture
def mock_nlp_client():
    """Create mock NLP client that is healthy."""
    mock = MagicMock()
    mock.check_health = AsyncMock(return_value=True)
    mock._base_url = "http://ash-nlp:30880"
    return mock


@pytest.fixture
def mock_nlp_unhealthy():
    """Create mock NLP client that is unhealthy."""
    mock = MagicMock()
    mock.check_health = AsyncMock(return_value=False)
    return mock


@pytest.fixture
def mock_redis_manager():
    """Create mock Redis manager that is connected."""
    mock = MagicMock()
    mock.ping = AsyncMock(return_value=True)
    mock.is_connected = MagicMock(return_value=True)
    return mock


@pytest.fixture
def mock_redis_disconnected():
    """Create mock Redis manager that is disconnected."""
    mock = MagicMock()
    mock.ping = AsyncMock(return_value=False)
    mock.is_connected = MagicMock(return_value=False)
    return mock


@pytest.fixture
def mock_ash_manager():
    """Create mock Ash session manager."""
    mock = MagicMock()
    mock.active_session_count = MagicMock(return_value=2)
    mock._claude_client = MagicMock()
    return mock


@pytest.fixture
def health_manager_all_healthy(
    mock_discord_manager,
    mock_nlp_client,
    mock_redis_manager,
    mock_ash_manager,
):
    """Create health manager with all healthy components."""
    return create_health_manager(
        discord_manager=mock_discord_manager,
        nlp_client=mock_nlp_client,
        redis_manager=mock_redis_manager,
        ash_session_manager=mock_ash_manager,
        version="5.0.0-test",
    )


@pytest.fixture
def health_manager_no_components():
    """Create health manager with no components."""
    return create_health_manager(version="5.0.0-test")


# =============================================================================
# ComponentHealth Tests
# =============================================================================


class TestComponentHealth:
    """Tests for ComponentHealth dataclass."""

    def test_component_health_creation(self):
        """Test basic ComponentHealth creation."""
        health = ComponentHealth(
            name="test_component",
            status=ComponentStatus.UP,
            message="All good",
        )

        assert health.name == "test_component"
        assert health.status == ComponentStatus.UP
        assert health.message == "All good"
        assert health.latency_ms is None
        assert health.details == {}

    def test_component_health_to_dict(self):
        """Test ComponentHealth serialization."""
        now = datetime.utcnow()
        health = ComponentHealth(
            name="test",
            status=ComponentStatus.DOWN,
            message="Failed",
            last_check=now,
            latency_ms=15.5,
            details={"error_count": 3},
        )

        result = health.to_dict()

        assert result["name"] == "test"
        assert result["status"] == "down"
        assert result["message"] == "Failed"
        assert result["latency_ms"] == 15.5
        assert result["details"] == {"error_count": 3}


# =============================================================================
# SystemHealth Tests
# =============================================================================


class TestSystemHealth:
    """Tests for SystemHealth dataclass."""

    def test_system_health_creation(self):
        """Test basic SystemHealth creation."""
        health = SystemHealth(
            status=HealthStatus.HEALTHY,
            components={},
            uptime_seconds=100.5,
            version="5.0.0",
            timestamp=datetime.utcnow(),
        )

        assert health.status == HealthStatus.HEALTHY
        assert health.uptime_seconds == 100.5
        assert health.version == "5.0.0"
        assert health.degradation_reasons == []

    def test_system_health_to_dict(self):
        """Test SystemHealth serialization."""
        now = datetime.utcnow()
        components = {
            "discord": ComponentHealth(
                name="discord",
                status=ComponentStatus.UP,
            )
        }

        health = SystemHealth(
            status=HealthStatus.DEGRADED,
            components=components,
            uptime_seconds=3600.0,
            version="5.0.0",
            timestamp=now,
            degradation_reasons=["NLP unavailable"],
        )

        result = health.to_dict()

        assert result["status"] == "degraded"
        assert result["uptime_seconds"] == 3600.0
        assert result["version"] == "5.0.0"
        assert result["degradation_reasons"] == ["NLP unavailable"]
        assert result["is_healthy"] is False
        assert result["is_ready"] is True  # Degraded is still ready
        assert "discord" in result["components"]

    def test_system_health_unhealthy_not_ready(self):
        """Test unhealthy system is not ready."""
        health = SystemHealth(
            status=HealthStatus.UNHEALTHY,
            components={},
            uptime_seconds=0,
            version="5.0.0",
            timestamp=datetime.utcnow(),
        )

        result = health.to_dict()
        assert result["is_healthy"] is False
        assert result["is_ready"] is False


# =============================================================================
# HealthManager Initialization Tests
# =============================================================================


class TestHealthManagerInit:
    """Tests for HealthManager initialization."""

    def test_basic_initialization(self):
        """Test basic initialization without components."""
        manager = HealthManager(version="5.0.0")

        assert manager.version == "5.0.0"
        assert manager.uptime_seconds >= 0

    def test_initialization_with_components(
        self,
        mock_discord_manager,
        mock_nlp_client,
    ):
        """Test initialization with components."""
        manager = HealthManager(
            discord_manager=mock_discord_manager,
            nlp_client=mock_nlp_client,
            version="5.0.0",
        )

        assert manager._discord is mock_discord_manager
        assert manager._nlp is mock_nlp_client

    def test_factory_function(self):
        """Test factory function creates manager correctly."""
        manager = create_health_manager(version="test-version")

        assert isinstance(manager, HealthManager)
        assert manager.version == "test-version"

    def test_repr(self, health_manager_no_components):
        """Test string representation."""
        repr_str = repr(health_manager_no_components)
        assert "HealthManager" in repr_str
        assert "5.0.0-test" in repr_str


# =============================================================================
# Liveness Check Tests
# =============================================================================


class TestLivenessCheck:
    """Tests for liveness checks."""

    @pytest.mark.asyncio
    async def test_liveness_always_true(self, health_manager_no_components):
        """Test liveness check always returns True."""
        result = await health_manager_no_components.check_liveness()
        assert result is True


# =============================================================================
# Readiness Check Tests
# =============================================================================


class TestReadinessCheck:
    """Tests for readiness checks."""

    @pytest.mark.asyncio
    async def test_readiness_when_discord_connected(
        self,
        mock_discord_manager,
    ):
        """Test readiness is True when Discord is connected."""
        manager = create_health_manager(
            discord_manager=mock_discord_manager,
        )

        result = await manager.check_readiness()
        assert result is True

    @pytest.mark.asyncio
    async def test_readiness_when_discord_disconnected(
        self,
        mock_discord_disconnected,
    ):
        """Test readiness is False when Discord is disconnected."""
        manager = create_health_manager(
            discord_manager=mock_discord_disconnected,
        )

        result = await manager.check_readiness()
        assert result is False

    @pytest.mark.asyncio
    async def test_readiness_without_discord_manager(
        self,
        health_manager_no_components,
    ):
        """Test readiness when no Discord manager configured."""
        result = await health_manager_no_components.check_readiness()
        # Unknown status means not ready
        assert result is False


# =============================================================================
# Full Health Check Tests
# =============================================================================


class TestFullHealthCheck:
    """Tests for full health checks."""

    @pytest.mark.asyncio
    async def test_health_check_all_healthy(
        self,
        health_manager_all_healthy,
    ):
        """Test health check when all components healthy."""
        result = await health_manager_all_healthy.check_health()

        assert result.status == HealthStatus.HEALTHY
        assert len(result.degradation_reasons) == 0
        assert "discord" in result.components
        assert "nlp" in result.components
        assert "redis" in result.components
        assert "ash" in result.components
        assert result.components["discord"].status == ComponentStatus.UP

    @pytest.mark.asyncio
    async def test_health_check_discord_down_is_unhealthy(
        self,
        mock_discord_disconnected,
        mock_nlp_client,
        mock_redis_manager,
    ):
        """Test system is unhealthy when Discord is down."""
        manager = create_health_manager(
            discord_manager=mock_discord_disconnected,
            nlp_client=mock_nlp_client,
            redis_manager=mock_redis_manager,
        )

        result = await manager.check_health()

        assert result.status == HealthStatus.UNHEALTHY
        assert "Discord" in result.degradation_reasons[0]

    @pytest.mark.asyncio
    async def test_health_check_nlp_down_is_degraded(
        self,
        mock_discord_manager,
        mock_nlp_unhealthy,
        mock_redis_manager,
    ):
        """Test system is degraded when NLP is down."""
        manager = create_health_manager(
            discord_manager=mock_discord_manager,
            nlp_client=mock_nlp_unhealthy,
            redis_manager=mock_redis_manager,
        )

        result = await manager.check_health()

        assert result.status == HealthStatus.DEGRADED
        assert any("NLP" in reason for reason in result.degradation_reasons)

    @pytest.mark.asyncio
    async def test_health_check_redis_down_is_degraded(
        self,
        mock_discord_manager,
        mock_nlp_client,
        mock_redis_disconnected,
    ):
        """Test system is degraded when Redis is down."""
        manager = create_health_manager(
            discord_manager=mock_discord_manager,
            nlp_client=mock_nlp_client,
            redis_manager=mock_redis_disconnected,
        )

        result = await manager.check_health()

        assert result.status == HealthStatus.DEGRADED
        assert any("REDIS" in reason for reason in result.degradation_reasons)

    @pytest.mark.asyncio
    async def test_health_check_no_components_unknown(
        self,
        health_manager_no_components,
    ):
        """Test health check with no components returns unknown statuses."""
        result = await health_manager_no_components.check_health()

        # All components should be UNKNOWN (not configured)
        for name, health in result.components.items():
            assert health.status == ComponentStatus.UNKNOWN
            assert "not configured" in health.message.lower()

    @pytest.mark.asyncio
    async def test_health_check_includes_metadata(
        self,
        health_manager_all_healthy,
    ):
        """Test health check includes proper metadata."""
        result = await health_manager_all_healthy.check_health()

        assert result.version == "5.0.0-test"
        assert result.uptime_seconds >= 0
        assert result.timestamp is not None


# =============================================================================
# Individual Component Check Tests
# =============================================================================


class TestDiscordHealthCheck:
    """Tests for Discord health check."""

    @pytest.mark.asyncio
    async def test_discord_healthy(self, mock_discord_manager):
        """Test Discord health when connected and ready."""
        manager = create_health_manager(discord_manager=mock_discord_manager)

        health = await manager._check_discord_health()

        assert health.status == ComponentStatus.UP
        assert health.latency_ms is not None
        assert "guilds" in health.details

    @pytest.mark.asyncio
    async def test_discord_connected_not_ready(self):
        """Test Discord health when connected but not ready."""
        mock = MagicMock()
        mock.is_connected = MagicMock(return_value=True)
        mock.is_ready = MagicMock(return_value=False)

        manager = create_health_manager(discord_manager=mock)
        health = await manager._check_discord_health()

        assert health.status == ComponentStatus.DEGRADED
        assert "not ready" in health.message.lower()

    @pytest.mark.asyncio
    async def test_discord_disconnected(self, mock_discord_disconnected):
        """Test Discord health when disconnected."""
        manager = create_health_manager(discord_manager=mock_discord_disconnected)

        health = await manager._check_discord_health()

        assert health.status == ComponentStatus.DOWN
        assert "not connected" in health.message.lower()


class TestNLPHealthCheck:
    """Tests for NLP health check."""

    @pytest.mark.asyncio
    async def test_nlp_healthy(self, mock_nlp_client):
        """Test NLP health when API is responding."""
        manager = create_health_manager(nlp_client=mock_nlp_client)

        health = await manager._check_nlp_health()

        assert health.status == ComponentStatus.UP

    @pytest.mark.asyncio
    async def test_nlp_unhealthy(self, mock_nlp_unhealthy):
        """Test NLP health when API is not responding."""
        manager = create_health_manager(nlp_client=mock_nlp_unhealthy)

        health = await manager._check_nlp_health()

        assert health.status == ComponentStatus.DOWN

    @pytest.mark.asyncio
    async def test_nlp_check_error(self):
        """Test NLP health when check throws exception."""
        mock = MagicMock()
        mock.check_health = AsyncMock(side_effect=Exception("Connection refused"))

        manager = create_health_manager(nlp_client=mock)
        health = await manager._check_nlp_health()

        assert health.status == ComponentStatus.DOWN
        assert "error" in health.message.lower()


class TestRedisHealthCheck:
    """Tests for Redis health check."""

    @pytest.mark.asyncio
    async def test_redis_healthy(self, mock_redis_manager):
        """Test Redis health when connected."""
        manager = create_health_manager(redis_manager=mock_redis_manager)

        health = await manager._check_redis_health()

        assert health.status == ComponentStatus.UP

    @pytest.mark.asyncio
    async def test_redis_unhealthy(self, mock_redis_disconnected):
        """Test Redis health when disconnected."""
        manager = create_health_manager(redis_manager=mock_redis_disconnected)

        health = await manager._check_redis_health()

        assert health.status == ComponentStatus.DOWN

    @pytest.mark.asyncio
    async def test_redis_ping_error(self):
        """Test Redis health when ping throws exception."""
        mock = MagicMock()
        mock.ping = AsyncMock(side_effect=Exception("Connection refused"))

        manager = create_health_manager(redis_manager=mock)
        health = await manager._check_redis_health()

        assert health.status == ComponentStatus.DOWN


class TestAshHealthCheck:
    """Tests for Ash session manager health check."""

    @pytest.mark.asyncio
    async def test_ash_healthy_with_claude(self, mock_ash_manager):
        """Test Ash health when Claude client is available."""
        manager = create_health_manager(ash_session_manager=mock_ash_manager)

        health = await manager._check_ash_health()

        assert health.status == ComponentStatus.UP
        assert "active_sessions" in health.details

    @pytest.mark.asyncio
    async def test_ash_degraded_without_claude(self):
        """Test Ash health when Claude client is not available."""
        mock = MagicMock()
        mock.active_session_count = MagicMock(return_value=0)
        mock._claude_client = None

        manager = create_health_manager(ash_session_manager=mock)
        health = await manager._check_ash_health()

        assert health.status == ComponentStatus.DEGRADED


# =============================================================================
# Quick Status Tests
# =============================================================================


class TestQuickStatus:
    """Tests for quick status method."""

    def test_quick_status_returns_basic_info(self, health_manager_no_components):
        """Test quick status returns basic information."""
        result = health_manager_no_components.get_quick_status()

        assert result["status"] == "running"
        assert result["version"] == "5.0.0-test"
        assert "uptime_seconds" in result
        assert "timestamp" in result


# =============================================================================
# Status Determination Tests
# =============================================================================


class TestStatusDetermination:
    """Tests for overall status determination logic."""

    def test_all_up_is_healthy(self, health_manager_no_components):
        """Test all UP components results in HEALTHY."""
        components = {
            "discord": ComponentHealth("discord", ComponentStatus.UP),
            "nlp": ComponentHealth("nlp", ComponentStatus.UP),
            "redis": ComponentHealth("redis", ComponentStatus.UP),
        }

        status, reasons = health_manager_no_components._determine_overall_status(
            components
        )

        assert status == HealthStatus.HEALTHY
        assert len(reasons) == 0

    def test_discord_down_is_unhealthy(self, health_manager_no_components):
        """Test Discord DOWN results in UNHEALTHY."""
        components = {
            "discord": ComponentHealth("discord", ComponentStatus.DOWN),
            "nlp": ComponentHealth("nlp", ComponentStatus.UP),
        }

        status, reasons = health_manager_no_components._determine_overall_status(
            components
        )

        assert status == HealthStatus.UNHEALTHY
        assert "Discord" in reasons[0]

    def test_nlp_down_is_degraded(self, health_manager_no_components):
        """Test NLP DOWN results in DEGRADED."""
        components = {
            "discord": ComponentHealth("discord", ComponentStatus.UP),
            "nlp": ComponentHealth("nlp", ComponentStatus.DOWN),
        }

        status, reasons = health_manager_no_components._determine_overall_status(
            components
        )

        assert status == HealthStatus.DEGRADED
        assert any("NLP" in r for r in reasons)

    def test_multiple_degradations(self, health_manager_no_components):
        """Test multiple degraded components."""
        components = {
            "discord": ComponentHealth("discord", ComponentStatus.UP),
            "nlp": ComponentHealth("nlp", ComponentStatus.DOWN),
            "redis": ComponentHealth("redis", ComponentStatus.DOWN),
        }

        status, reasons = health_manager_no_components._determine_overall_status(
            components
        )

        assert status == HealthStatus.DEGRADED
        assert len(reasons) >= 2


# =============================================================================
# Timeout Tests
# =============================================================================


class TestHealthCheckTimeout:
    """Tests for health check timeout handling."""

    @pytest.mark.asyncio
    async def test_timeout_handling(self):
        """Test that slow health checks time out gracefully."""
        slow_mock = MagicMock()

        async def slow_health_check():
            await asyncio.sleep(10)  # Way longer than timeout
            return True

        slow_mock.check_health = slow_health_check
        slow_mock._base_url = None

        manager = create_health_manager(nlp_client=slow_mock)
        manager._check_timeout = 0.1  # 100ms timeout

        result = await manager.check_health()

        # Should complete without hanging
        nlp_health = result.components.get("nlp")
        assert nlp_health is not None
        # Should be UNKNOWN due to timeout
        assert nlp_health.status == ComponentStatus.UNKNOWN
