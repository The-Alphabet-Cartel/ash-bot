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
Health Manager for Ash-Bot Service
---
FILE VERSION: v5.0-5-5.3-1
LAST MODIFIED: 2026-01-04
PHASE: Phase 5 - Production Hardening
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-bot
Community: The Alphabet Cartel - https://discord.gg/alphabetcartel | https://alphabetcartel.org
============================================================================
RESPONSIBILITIES:
- Coordinate health checks across all components
- Determine overall system health status
- Track degradation reasons and recovery
- Provide health check data for endpoints

HEALTH STATES:
- HEALTHY: All systems operational
- DEGRADED: Some non-critical systems unavailable
- UNHEALTHY: Critical systems (Discord) unavailable

USAGE:
    from src.managers.health import create_health_manager

    health = create_health_manager(
        discord_manager=discord_mgr,
        nlp_client=nlp_client,
        redis_manager=redis_mgr,
    )

    status = await health.check_health()
    print(f"Status: {status.status}")
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, TYPE_CHECKING

# Module version
__version__ = "v5.0-5-5.3-1"

# Initialize logger
logger = logging.getLogger(__name__)

# Type checking imports to avoid circular dependencies
if TYPE_CHECKING:
    from src.managers.discord import DiscordManager
    from src.managers.nlp import NLPClientManager
    from src.managers.storage import RedisManager
    from src.managers.ash import AshSessionManager
    from src.managers.metrics import MetricsManager


# =============================================================================
# Enums
# =============================================================================


class HealthStatus(Enum):
    """
    Overall health status for the system.

    Attributes:
        HEALTHY: All systems operational, full functionality
        DEGRADED: Some components unavailable, reduced functionality
        UNHEALTHY: Critical components down, service cannot operate
    """

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class ComponentStatus(Enum):
    """
    Health status for individual components.

    Attributes:
        UP: Component is fully operational
        DOWN: Component is not available
        DEGRADED: Component has reduced functionality
        UNKNOWN: Component status cannot be determined
    """

    UP = "up"
    DOWN = "down"
    DEGRADED = "degraded"
    UNKNOWN = "unknown"


# =============================================================================
# Data Classes
# =============================================================================


@dataclass
class ComponentHealth:
    """
    Health status for a single component.

    Attributes:
        name: Component identifier
        status: Current status
        message: Human-readable status message
        last_check: When this component was last checked
        latency_ms: Response time in milliseconds (if applicable)
        details: Additional component-specific details
    """

    name: str
    status: ComponentStatus
    message: Optional[str] = None
    last_check: Optional[datetime] = None
    latency_ms: Optional[float] = None
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "name": self.name,
            "status": self.status.value,
            "message": self.message,
            "last_check": self.last_check.isoformat() if self.last_check else None,
            "latency_ms": self.latency_ms,
            "details": self.details,
        }


@dataclass
class SystemHealth:
    """
    Overall system health report.

    Attributes:
        status: Overall health status
        components: Individual component health reports
        uptime_seconds: Time since system started
        version: Application version
        timestamp: When this report was generated
        degradation_reasons: List of reasons for degradation (if applicable)
    """

    status: HealthStatus
    components: Dict[str, ComponentHealth]
    uptime_seconds: float
    version: str
    timestamp: datetime
    degradation_reasons: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "status": self.status.value,
            "components": {
                name: comp.to_dict() for name, comp in self.components.items()
            },
            "uptime_seconds": self.uptime_seconds,
            "version": self.version,
            "timestamp": self.timestamp.isoformat() + "Z",
            "degradation_reasons": self.degradation_reasons,
            "is_healthy": self.status == HealthStatus.HEALTHY,
            "is_ready": self.status != HealthStatus.UNHEALTHY,
        }


# =============================================================================
# Health Manager
# =============================================================================


class HealthManager:
    """
    Coordinates health checks for all Ash-Bot components.

    Provides methods to check individual component health and
    determine overall system status based on component states.

    Attributes:
        version: Application version string
        start_time: When the manager was created

    Example:
        >>> health = create_health_manager(discord_manager=dm, nlp_client=nlp)
        >>> status = await health.check_health()
        >>> if status.status == HealthStatus.HEALTHY:
        ...     print("All systems go!")
    """

    def __init__(
        self,
        discord_manager: Optional["DiscordManager"] = None,
        nlp_client: Optional["NLPClientManager"] = None,
        redis_manager: Optional["RedisManager"] = None,
        ash_session_manager: Optional["AshSessionManager"] = None,
        metrics_manager: Optional["MetricsManager"] = None,
        version: str = "5.0.0",
    ):
        """
        Initialize HealthManager with component references.

        Args:
            discord_manager: Discord connection manager
            nlp_client: NLP API client manager
            redis_manager: Redis connection manager
            ash_session_manager: Ash personality session manager
            metrics_manager: Metrics collection manager
            version: Application version string
        """
        self._discord = discord_manager
        self._nlp = nlp_client
        self._redis = redis_manager
        self._ash = ash_session_manager
        self._metrics = metrics_manager
        self._version = version
        self._start_time = time.time()

        # Health check timeout
        self._check_timeout = 5.0  # seconds

        logger.info(f"✅ HealthManager v{__version__} initialized (version: {version})")

    # =========================================================================
    # Properties
    # =========================================================================

    @property
    def uptime_seconds(self) -> float:
        """Get system uptime in seconds."""
        return time.time() - self._start_time

    @property
    def version(self) -> str:
        """Get application version."""
        return self._version

    # =========================================================================
    # Main Health Check Methods
    # =========================================================================

    async def check_health(self) -> SystemHealth:
        """
        Perform full health check of all components.

        Checks each registered component and determines overall
        system health based on component statuses.

        Returns:
            SystemHealth with complete status report

        Note:
            This method never raises exceptions - it always returns
            a valid SystemHealth object.
        """
        components: Dict[str, ComponentHealth] = {}

        # Check each component with timeout protection
        check_tasks = [
            ("discord", self._check_discord_health()),
            ("nlp", self._check_nlp_health()),
            ("redis", self._check_redis_health()),
            ("ash", self._check_ash_health()),
        ]

        for name, coro in check_tasks:
            try:
                health = await asyncio.wait_for(coro, timeout=self._check_timeout)
                components[name] = health
            except asyncio.TimeoutError:
                components[name] = ComponentHealth(
                    name=name,
                    status=ComponentStatus.UNKNOWN,
                    message="Health check timed out",
                    last_check=datetime.utcnow(),
                )
            except Exception as e:
                logger.error(f"Error checking {name} health: {e}")
                components[name] = ComponentHealth(
                    name=name,
                    status=ComponentStatus.UNKNOWN,
                    message=f"Health check error: {str(e)}",
                    last_check=datetime.utcnow(),
                )

        # Determine overall status
        overall_status, degradation_reasons = self._determine_overall_status(components)

        return SystemHealth(
            status=overall_status,
            components=components,
            uptime_seconds=self.uptime_seconds,
            version=self._version,
            timestamp=datetime.utcnow(),
            degradation_reasons=degradation_reasons,
        )

    async def check_liveness(self) -> bool:
        """
        Simple liveness check.

        Returns True if the bot process is running.
        This is the most basic health check.

        Returns:
            True if alive (always, if this executes)
        """
        return True

    async def check_readiness(self) -> bool:
        """
        Check if bot is ready to serve.

        A bot is ready if Discord is connected, which is
        the minimum requirement for operation.

        Returns:
            True if ready to accept traffic
        """
        # Check Discord connection (minimum requirement)
        discord_health = await self._check_discord_health()
        return discord_health.status == ComponentStatus.UP

    # =========================================================================
    # Individual Component Health Checks
    # =========================================================================

    async def _check_discord_health(self) -> ComponentHealth:
        """
        Check Discord connection health.

        Discord is the CRITICAL component - if Discord is down,
        the bot cannot function.

        Returns:
            ComponentHealth for Discord
        """
        start_time = time.time()

        if self._discord is None:
            return ComponentHealth(
                name="discord",
                status=ComponentStatus.UNKNOWN,
                message="Discord manager not configured",
                last_check=datetime.utcnow(),
            )

        try:
            # Check if bot is connected and ready
            is_connected = getattr(self._discord, "is_connected", lambda: False)
            is_ready = getattr(self._discord, "is_ready", lambda: False)

            # Handle both method and property access
            connected = is_connected() if callable(is_connected) else is_connected
            ready = is_ready() if callable(is_ready) else is_ready

            latency_ms = (time.time() - start_time) * 1000

            if connected and ready:
                # Get guild count if available
                guilds = getattr(self._discord, "guild_count", 0)
                if callable(guilds):
                    guilds = guilds()

                return ComponentHealth(
                    name="discord",
                    status=ComponentStatus.UP,
                    message="Connected and ready",
                    last_check=datetime.utcnow(),
                    latency_ms=latency_ms,
                    details={"guilds": guilds},
                )
            elif connected:
                return ComponentHealth(
                    name="discord",
                    status=ComponentStatus.DEGRADED,
                    message="Connected but not ready",
                    last_check=datetime.utcnow(),
                    latency_ms=latency_ms,
                )
            else:
                return ComponentHealth(
                    name="discord",
                    status=ComponentStatus.DOWN,
                    message="Not connected to Discord gateway",
                    last_check=datetime.utcnow(),
                    latency_ms=latency_ms,
                )

        except Exception as e:
            logger.error(f"Discord health check failed: {e}")
            return ComponentHealth(
                name="discord",
                status=ComponentStatus.UNKNOWN,
                message=f"Health check error: {str(e)}",
                last_check=datetime.utcnow(),
            )

    async def _check_nlp_health(self) -> ComponentHealth:
        """
        Check NLP API health.

        NLP is important but the bot can continue without it
        in degraded mode.

        Returns:
            ComponentHealth for NLP API
        """
        start_time = time.time()

        if self._nlp is None:
            return ComponentHealth(
                name="nlp",
                status=ComponentStatus.UNKNOWN,
                message="NLP client not configured",
                last_check=datetime.utcnow(),
            )

        try:
            # Try to call health check if available
            health_check = getattr(self._nlp, "check_health", None)
            if health_check and callable(health_check):
                is_healthy = await health_check()
                latency_ms = (time.time() - start_time) * 1000

                if is_healthy:
                    return ComponentHealth(
                        name="nlp",
                        status=ComponentStatus.UP,
                        message="NLP API is responding",
                        last_check=datetime.utcnow(),
                        latency_ms=latency_ms,
                    )
                else:
                    return ComponentHealth(
                        name="nlp",
                        status=ComponentStatus.DOWN,
                        message="NLP API health check failed",
                        last_check=datetime.utcnow(),
                        latency_ms=latency_ms,
                    )

            # Fallback: check if client exists and has base URL
            base_url = getattr(self._nlp, "_base_url", None)
            latency_ms = (time.time() - start_time) * 1000

            if base_url:
                return ComponentHealth(
                    name="nlp",
                    status=ComponentStatus.UP,
                    message="NLP client configured",
                    last_check=datetime.utcnow(),
                    latency_ms=latency_ms,
                    details={"base_url": str(base_url)},
                )

            return ComponentHealth(
                name="nlp",
                status=ComponentStatus.UNKNOWN,
                message="Unable to determine NLP status",
                last_check=datetime.utcnow(),
                latency_ms=latency_ms,
            )

        except Exception as e:
            logger.error(f"NLP health check failed: {e}")
            return ComponentHealth(
                name="nlp",
                status=ComponentStatus.DOWN,
                message=f"Health check error: {str(e)}",
                last_check=datetime.utcnow(),
            )

    async def _check_redis_health(self) -> ComponentHealth:
        """
        Check Redis connection health.

        Redis is important for history tracking but the bot
        can continue without it in degraded mode.

        Returns:
            ComponentHealth for Redis
        """
        start_time = time.time()

        if self._redis is None:
            return ComponentHealth(
                name="redis",
                status=ComponentStatus.UNKNOWN,
                message="Redis manager not configured",
                last_check=datetime.utcnow(),
            )

        try:
            # Try to ping Redis
            ping = getattr(self._redis, "ping", None)
            if ping and callable(ping):
                result = await ping()
                latency_ms = (time.time() - start_time) * 1000

                if result:
                    return ComponentHealth(
                        name="redis",
                        status=ComponentStatus.UP,
                        message="Redis is responding",
                        last_check=datetime.utcnow(),
                        latency_ms=latency_ms,
                    )
                else:
                    return ComponentHealth(
                        name="redis",
                        status=ComponentStatus.DOWN,
                        message="Redis ping failed",
                        last_check=datetime.utcnow(),
                        latency_ms=latency_ms,
                    )

            # Fallback: check if connected property exists
            is_connected = getattr(self._redis, "is_connected", False)
            if callable(is_connected):
                is_connected = is_connected()

            latency_ms = (time.time() - start_time) * 1000

            if is_connected:
                return ComponentHealth(
                    name="redis",
                    status=ComponentStatus.UP,
                    message="Redis connected",
                    last_check=datetime.utcnow(),
                    latency_ms=latency_ms,
                )

            return ComponentHealth(
                name="redis",
                status=ComponentStatus.DOWN,
                message="Redis not connected",
                last_check=datetime.utcnow(),
                latency_ms=latency_ms,
            )

        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            return ComponentHealth(
                name="redis",
                status=ComponentStatus.DOWN,
                message=f"Health check error: {str(e)}",
                last_check=datetime.utcnow(),
            )

    async def _check_ash_health(self) -> ComponentHealth:
        """
        Check Ash personality session manager health.

        Ash is a nice-to-have feature - the bot operates
        fine without it.

        Returns:
            ComponentHealth for Ash sessions
        """
        start_time = time.time()

        if self._ash is None:
            return ComponentHealth(
                name="ash",
                status=ComponentStatus.UNKNOWN,
                message="Ash session manager not configured",
                last_check=datetime.utcnow(),
            )

        try:
            # Get active session count
            active_sessions = getattr(self._ash, "active_session_count", 0)
            if callable(active_sessions):
                active_sessions = active_sessions()

            # Check if Claude client is available
            has_claude = getattr(self._ash, "_claude_client", None) is not None

            latency_ms = (time.time() - start_time) * 1000

            if has_claude:
                return ComponentHealth(
                    name="ash",
                    status=ComponentStatus.UP,
                    message="Ash sessions available",
                    last_check=datetime.utcnow(),
                    latency_ms=latency_ms,
                    details={"active_sessions": active_sessions},
                )
            else:
                return ComponentHealth(
                    name="ash",
                    status=ComponentStatus.DEGRADED,
                    message="Ash available without Claude client",
                    last_check=datetime.utcnow(),
                    latency_ms=latency_ms,
                    details={"active_sessions": active_sessions},
                )

        except Exception as e:
            logger.error(f"Ash health check failed: {e}")
            return ComponentHealth(
                name="ash",
                status=ComponentStatus.DOWN,
                message=f"Health check error: {str(e)}",
                last_check=datetime.utcnow(),
            )

    # =========================================================================
    # Status Determination
    # =========================================================================

    def _determine_overall_status(
        self,
        components: Dict[str, ComponentHealth],
    ) -> tuple[HealthStatus, List[str]]:
        """
        Determine overall health from component statuses.

        Rules:
        - Discord DOWN/UNKNOWN = UNHEALTHY (critical)
        - Any other DOWN = DEGRADED
        - All UP = HEALTHY

        Args:
            components: Dictionary of component health reports

        Returns:
            Tuple of (overall_status, degradation_reasons)
        """
        degradation_reasons: List[str] = []

        # Discord is critical - if it's down, system is unhealthy
        discord_health = components.get("discord")
        if discord_health:
            if discord_health.status in (ComponentStatus.DOWN, ComponentStatus.UNKNOWN):
                return HealthStatus.UNHEALTHY, ["Discord connection unavailable"]

        # Check other components for degradation
        for name, health in components.items():
            if name == "discord":
                continue  # Already handled

            if health.status == ComponentStatus.DOWN:
                degradation_reasons.append(f"{name.upper()} unavailable")
            elif health.status == ComponentStatus.DEGRADED:
                degradation_reasons.append(f"{name.upper()} degraded")
            elif health.status == ComponentStatus.UNKNOWN:
                degradation_reasons.append(f"{name.upper()} status unknown")

        # Determine final status
        if degradation_reasons:
            return HealthStatus.DEGRADED, degradation_reasons

        return HealthStatus.HEALTHY, []

    # =========================================================================
    # Utility Methods
    # =========================================================================

    def get_quick_status(self) -> Dict[str, Any]:
        """
        Get quick status without async health checks.

        Returns cached/basic information only.

        Returns:
            Quick status dictionary
        """
        return {
            "status": "running",
            "version": self._version,
            "uptime_seconds": self.uptime_seconds,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }

    def __repr__(self) -> str:
        """String representation."""
        return f"HealthManager(version='{self._version}', uptime={self.uptime_seconds:.1f}s)"


# =============================================================================
# Factory Function
# =============================================================================


def create_health_manager(
    discord_manager: Optional["DiscordManager"] = None,
    nlp_client: Optional["NLPClientManager"] = None,
    redis_manager: Optional["RedisManager"] = None,
    ash_session_manager: Optional["AshSessionManager"] = None,
    metrics_manager: Optional["MetricsManager"] = None,
    version: str = "5.0.0",
) -> HealthManager:
    """
    Factory function for HealthManager.

    Creates a HealthManager instance with component references.
    Following Clean Architecture v5.1 Rule #1: Factory Functions.

    Args:
        discord_manager: Discord connection manager
        nlp_client: NLP API client manager
        redis_manager: Redis connection manager
        ash_session_manager: Ash personality session manager
        metrics_manager: Metrics collection manager
        version: Application version string

    Returns:
        Configured HealthManager instance

    Example:
        >>> health = create_health_manager(
        ...     discord_manager=discord_mgr,
        ...     nlp_client=nlp_client,
        ...     version="5.0.0",
        ... )
    """
    logger.info("🏭 Creating HealthManager")
    return HealthManager(
        discord_manager=discord_manager,
        nlp_client=nlp_client,
        redis_manager=redis_manager,
        ash_session_manager=ash_session_manager,
        metrics_manager=metrics_manager,
        version=version,
    )


# =============================================================================
# Export public interface
# =============================================================================

__all__ = [
    "HealthManager",
    "HealthStatus",
    "ComponentStatus",
    "ComponentHealth",
    "SystemHealth",
    "create_health_manager",
]
