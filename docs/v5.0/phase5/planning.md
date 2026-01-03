# Phase 5: Production Hardening - Planning Document

============================================================================
**Ash-Bot**: Crisis Detection Discord Bot for The Alphabet Cartel  
**The Alphabet Cartel** - https://discord.gg/alphabetcartel | alphabetcartel.org
============================================================================

**Document Version**: v1.0.0  
**Created**: 2026-01-03  
**Phase**: 5 - Production Hardening  
**Status**: 🔲 Not Started  
**Estimated Time**: 1 week  
**Dependencies**: Phases 1-4 Complete

---

## Table of Contents

1. [Overview](#overview)
2. [Goals](#goals)
3. [Architecture](#architecture)
4. [File Structure](#file-structure)
5. [Implementation Details](#implementation-details)
6. [Configuration](#configuration)
7. [Testing Requirements](#testing-requirements)
8. [Step-by-Step Implementation](#step-by-step-implementation)
9. [Acceptance Criteria](#acceptance-criteria)

---

## Overview

Phase 5 hardens Ash-Bot for production deployment. This includes comprehensive error handling, metrics collection, graceful degradation, health monitoring, and operational tooling.

### Key Deliverables

1. Comprehensive error handling and recovery
2. Metrics and monitoring integration
3. Graceful degradation when services unavailable
4. Health check endpoints
5. Operational documentation
6. Production deployment scripts

---

## Goals

### Primary Goals

| Goal | Description |
|------|-------------|
| Error Resilience | Handle all error conditions gracefully |
| Metrics | Collect and expose operational metrics |
| Health Checks | Provide health endpoints for monitoring |
| Graceful Degradation | Continue operating with reduced functionality |
| Documentation | Complete operational runbooks |

### Non-Goals

- New features (feature complete after Phase 4)
- Major architectural changes
- Performance optimization (beyond baseline)

---

## Architecture

### Error Handling Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Error Handling Layers                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Layer 1: Method-Level Try/Catch                                │
│  ├── Log error with context                                     │
│  ├── Return safe default or raise                               │
│  └── Preserve original exception chain                          │
│                                                                  │
│  Layer 2: Manager-Level Recovery                                │
│  ├── Retry with exponential backoff                             │
│  ├── Circuit breaker pattern                                    │
│  └── Fallback to degraded mode                                  │
│                                                                  │
│  Layer 3: Global Exception Handlers                             │
│  ├── Catch unhandled exceptions                                 │
│  ├── Log full stack traces                                      │
│  ├── Send alerts for critical failures                          │
│  └── Prevent crash, continue operation                          │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Metrics Collection Flow

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Bot Events  │────▶│   Metrics    │────▶│   Export     │
│              │     │   Manager    │     │   Endpoint   │
└──────────────┘     └──────────────┘     └──────────────┘
       │                    │                    │
       │                    │                    ▼
       │                    │            ┌──────────────┐
       │                    │            │  Prometheus  │
       │                    │            │  /metrics    │
       │                    │            └──────────────┘
       │                    ▼
       │             ┌──────────────┐
       │             │   Counter    │
       │             │   Gauges     │
       │             │   Histograms │
       │             └──────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────┐
│ Metrics Collected:                                    │
│ • messages_processed_total                           │
│ • messages_analyzed_total (by severity)              │
│ • alerts_sent_total (by severity, channel)           │
│ • ash_sessions_total                                 │
│ • nlp_request_duration_seconds                       │
│ • nlp_errors_total                                   │
│ • redis_operations_total                             │
│ • discord_reconnects_total                           │
└──────────────────────────────────────────────────────┘
```

### Health Check Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      Health Check System                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  GET /health (Simple Liveness)                                  │
│  └── Returns: {"status": "healthy", "timestamp": "..."}         │
│                                                                  │
│  GET /health/ready (Readiness Check)                            │
│  └── Checks:                                                    │
│      ├── Discord connected                                      │
│      ├── NLP API reachable                                      │
│      ├── Redis connected                                        │
│      └── All managers initialized                               │
│                                                                  │
│  GET /health/detailed (Full Status)                             │
│  └── Returns:                                                   │
│      ├── Component status (each manager)                        │
│      ├── Uptime                                                 │
│      ├── Version info                                           │
│      ├── Recent errors                                          │
│      └── Performance metrics                                    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Graceful Degradation States

```
┌─────────────────────────────────────────────────────────────────┐
│                    Degradation States                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  🟢 HEALTHY - All systems operational                           │
│  └── Full functionality                                         │
│                                                                  │
│  🟡 DEGRADED_NLP - NLP API unavailable                          │
│  └── Log all messages, skip analysis                            │
│  └── Queue messages for retry when recovered                    │
│                                                                  │
│  🟡 DEGRADED_REDIS - Redis unavailable                          │
│  └── Skip history storage                                       │
│  └── Continue with analysis and alerts                          │
│  └── Use in-memory cache temporarily                            │
│                                                                  │
│  🟡 DEGRADED_ASH - Claude API unavailable                       │
│  └── Skip personality responses                                 │
│  └── Send alerts without Ash engagement                         │
│                                                                  │
│  🔴 UNHEALTHY - Discord disconnected                            │
│  └── Attempt reconnection                                       │
│  └── Alert via webhook if persistent                            │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## File Structure

### New Files to Create

```
src/
├── managers/
│   ├── health/
│   │   ├── __init__.py
│   │   └── health_manager.py          # Health check coordination
│   └── metrics/
│       ├── __init__.py
│       └── metrics_manager.py         # Metrics collection
├── api/
│   ├── __init__.py
│   └── health_routes.py               # HTTP health endpoints
└── utils/
    ├── __init__.py
    ├── circuit_breaker.py             # Circuit breaker pattern
    └── retry.py                       # Retry utilities

docs/
├── operations/
│   ├── runbook.md                     # Operational runbook
│   ├── troubleshooting.md             # Troubleshooting guide
│   └── deployment.md                  # Deployment procedures

tests/
├── test_health/
│   ├── __init__.py
│   └── test_health_manager.py
└── test_metrics/
    ├── __init__.py
    └── test_metrics_manager.py
```

### Files to Update

```
src/
├── managers/
│   ├── __init__.py                    # Add health, metrics exports
│   ├── discord/discord_manager.py     # Add error recovery
│   ├── nlp/nlp_client_manager.py      # Add circuit breaker
│   ├── redis/redis_manager.py         # Add connection recovery
│   └── ash/ash_manager.py             # Add graceful degradation
└── main.py                            # Add health server, metrics
```

---

## Implementation Details

### 1. Health Manager (`src/managers/health/health_manager.py`)

```python
"""
Health Manager for Ash-Bot Service
---
Coordinates health checks across all components.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import asyncio


class HealthStatus(Enum):
    """Overall health status."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class ComponentStatus(Enum):
    """Individual component status."""
    UP = "up"
    DOWN = "down"
    DEGRADED = "degraded"
    UNKNOWN = "unknown"


@dataclass
class ComponentHealth:
    """Health status for a single component."""
    name: str
    status: ComponentStatus
    message: Optional[str] = None
    last_check: Optional[datetime] = None
    latency_ms: Optional[float] = None
    details: Optional[Dict[str, Any]] = None


@dataclass
class SystemHealth:
    """Overall system health."""
    status: HealthStatus
    components: Dict[str, ComponentHealth]
    uptime_seconds: float
    version: str
    timestamp: datetime
    degradation_reasons: List[str]


class HealthManager:
    """
    Coordinates health checks for all Ash-Bot components.
    
    Responsibilities:
    - Check health of all components
    - Determine overall system health
    - Track degradation reasons
    - Provide health check endpoints
    """
    
    def __init__(
        self,
        discord_manager: "DiscordManager",
        nlp_client: "NLPClientManager",
        redis_manager: "RedisManager",
        ash_manager: "AshManager",
        config_manager: "ConfigManager",
    ):
        """Initialize with all managed components."""
        self._discord = discord_manager
        self._nlp = nlp_client
        self._redis = redis_manager
        self._ash = ash_manager
        self._config = config_manager
        self._start_time = datetime.utcnow()
        self._version = "5.0.0"
    
    async def check_health(self) -> SystemHealth:
        """
        Perform full health check of all components.
        
        Returns:
            SystemHealth with status of all components
        """
        pass
    
    async def check_liveness(self) -> bool:
        """
        Simple liveness check.
        
        Returns:
            True if bot process is running
        """
        return True
    
    async def check_readiness(self) -> bool:
        """
        Check if bot is ready to serve.
        
        Returns:
            True if all required components are healthy
        """
        pass
    
    async def _check_discord_health(self) -> ComponentHealth:
        """Check Discord connection health."""
        pass
    
    async def _check_nlp_health(self) -> ComponentHealth:
        """Check NLP API health."""
        pass
    
    async def _check_redis_health(self) -> ComponentHealth:
        """Check Redis connection health."""
        pass
    
    async def _check_ash_health(self) -> ComponentHealth:
        """Check Ash/Claude API health."""
        pass
    
    def _determine_overall_status(
        self,
        components: Dict[str, ComponentHealth]
    ) -> tuple[HealthStatus, List[str]]:
        """
        Determine overall health from component statuses.
        
        Rules:
        - Discord DOWN = UNHEALTHY
        - Any other DOWN = DEGRADED
        - All UP = HEALTHY
        
        Returns:
            Tuple of (status, degradation_reasons)
        """
        pass


def create_health_manager(...) -> HealthManager:
    """Factory function for HealthManager."""
    pass
```

### 2. Metrics Manager (`src/managers/metrics/metrics_manager.py`)

```python
"""
Metrics Manager for Ash-Bot Service
---
Collects and exports operational metrics.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from datetime import datetime
import asyncio
import time


@dataclass
class Counter:
    """Simple counter metric."""
    name: str
    value: int = 0
    labels: Dict[str, str] = field(default_factory=dict)
    
    def inc(self, amount: int = 1) -> None:
        """Increment counter."""
        self.value += amount


@dataclass
class Gauge:
    """Gauge metric (can go up or down)."""
    name: str
    value: float = 0.0
    labels: Dict[str, str] = field(default_factory=dict)
    
    def set(self, value: float) -> None:
        """Set gauge value."""
        self.value = value
    
    def inc(self, amount: float = 1.0) -> None:
        """Increment gauge."""
        self.value += amount
    
    def dec(self, amount: float = 1.0) -> None:
        """Decrement gauge."""
        self.value -= amount


@dataclass
class Histogram:
    """Histogram for tracking distributions."""
    name: str
    buckets: tuple = (0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0)
    counts: Dict[float, int] = field(default_factory=dict)
    sum: float = 0.0
    count: int = 0
    
    def observe(self, value: float) -> None:
        """Record an observation."""
        self.sum += value
        self.count += 1
        for bucket in self.buckets:
            if value <= bucket:
                self.counts[bucket] = self.counts.get(bucket, 0) + 1


class MetricsManager:
    """
    Collects and manages operational metrics.
    
    Metrics collected:
    - messages_processed_total: Counter
    - messages_analyzed_total: Counter (by severity)
    - alerts_sent_total: Counter (by severity, channel)
    - ash_sessions_total: Counter
    - nlp_request_duration_seconds: Histogram
    - nlp_errors_total: Counter
    - redis_operations_total: Counter
    - discord_reconnects_total: Counter
    - active_ash_sessions: Gauge
    """
    
    def __init__(self):
        """Initialize metrics."""
        self._counters: Dict[str, Counter] = {}
        self._gauges: Dict[str, Gauge] = {}
        self._histograms: Dict[str, Histogram] = {}
        self._setup_metrics()
    
    def _setup_metrics(self) -> None:
        """Initialize all metrics."""
        # Counters
        self._counters["messages_processed_total"] = Counter("messages_processed_total")
        self._counters["messages_analyzed_total"] = Counter("messages_analyzed_total")
        self._counters["alerts_sent_total"] = Counter("alerts_sent_total")
        self._counters["ash_sessions_total"] = Counter("ash_sessions_total")
        self._counters["nlp_errors_total"] = Counter("nlp_errors_total")
        self._counters["redis_operations_total"] = Counter("redis_operations_total")
        self._counters["discord_reconnects_total"] = Counter("discord_reconnects_total")
        
        # Gauges
        self._gauges["active_ash_sessions"] = Gauge("active_ash_sessions")
        self._gauges["connected_guilds"] = Gauge("connected_guilds")
        
        # Histograms
        self._histograms["nlp_request_duration_seconds"] = Histogram(
            "nlp_request_duration_seconds"
        )
    
    def inc_messages_processed(self) -> None:
        """Increment messages processed counter."""
        self._counters["messages_processed_total"].inc()
    
    def inc_messages_analyzed(self, severity: str) -> None:
        """Increment messages analyzed counter with severity label."""
        self._counters["messages_analyzed_total"].inc()
    
    def inc_alerts_sent(self, severity: str, channel_type: str) -> None:
        """Increment alerts sent counter."""
        self._counters["alerts_sent_total"].inc()
    
    def observe_nlp_duration(self, duration_seconds: float) -> None:
        """Record NLP request duration."""
        self._histograms["nlp_request_duration_seconds"].observe(duration_seconds)
    
    def inc_nlp_errors(self) -> None:
        """Increment NLP error counter."""
        self._counters["nlp_errors_total"].inc()
    
    def set_active_ash_sessions(self, count: int) -> None:
        """Set active Ash sessions gauge."""
        self._gauges["active_ash_sessions"].set(count)
    
    def export_prometheus(self) -> str:
        """
        Export metrics in Prometheus format.
        
        Returns:
            Prometheus-formatted metrics string
        """
        pass
    
    def export_json(self) -> Dict[str, Any]:
        """
        Export metrics as JSON.
        
        Returns:
            Dictionary of all metrics
        """
        pass


def create_metrics_manager() -> MetricsManager:
    """Factory function for MetricsManager."""
    return MetricsManager()
```

### 3. Circuit Breaker (`src/utils/circuit_breaker.py`)

```python
"""
Circuit Breaker Pattern Implementation
---
Prevents cascading failures by failing fast when a service is unavailable.
"""

from enum import Enum
from dataclasses import dataclass
from typing import Callable, Any, Optional
from datetime import datetime, timedelta
import asyncio
import logging

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing fast
    HALF_OPEN = "half_open"  # Testing recovery


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker."""
    failure_threshold: int = 5       # Failures before opening
    success_threshold: int = 2       # Successes to close from half-open
    timeout_seconds: float = 30.0    # Time before trying half-open
    

class CircuitBreaker:
    """
    Circuit breaker for protecting against cascading failures.
    
    States:
    - CLOSED: Normal operation, requests pass through
    - OPEN: Failing fast, all requests rejected
    - HALF_OPEN: Testing if service recovered
    
    Usage:
        breaker = CircuitBreaker("nlp_api")
        
        try:
            result = await breaker.call(async_function, arg1, arg2)
        except CircuitOpenError:
            # Handle circuit open (service unavailable)
            pass
    """
    
    def __init__(
        self,
        name: str,
        config: Optional[CircuitBreakerConfig] = None,
    ):
        """Initialize circuit breaker."""
        self.name = name
        self.config = config or CircuitBreakerConfig()
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time: Optional[datetime] = None
    
    @property
    def state(self) -> CircuitState:
        """Get current circuit state."""
        return self._state
    
    @property
    def is_closed(self) -> bool:
        """Check if circuit is closed (normal operation)."""
        return self._state == CircuitState.CLOSED
    
    async def call(
        self,
        func: Callable,
        *args,
        **kwargs
    ) -> Any:
        """
        Call function through circuit breaker.
        
        Args:
            func: Async function to call
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            Result from function
            
        Raises:
            CircuitOpenError: If circuit is open
        """
        pass
    
    def _should_attempt(self) -> bool:
        """Check if we should attempt the call."""
        pass
    
    def _on_success(self) -> None:
        """Handle successful call."""
        pass
    
    def _on_failure(self) -> None:
        """Handle failed call."""
        pass
    
    def reset(self) -> None:
        """Manually reset circuit to closed state."""
        pass


class CircuitOpenError(Exception):
    """Raised when circuit breaker is open."""
    pass
```

### 4. Health Routes (`src/api/health_routes.py`)

```python
"""
Health Check HTTP Endpoints
---
Provides /health endpoints for monitoring.
"""

from aiohttp import web
from typing import Optional
import json


class HealthRoutes:
    """
    HTTP routes for health checks.
    
    Endpoints:
    - GET /health - Simple liveness
    - GET /health/ready - Readiness check
    - GET /health/detailed - Full status
    - GET /metrics - Prometheus metrics
    """
    
    def __init__(
        self,
        health_manager: "HealthManager",
        metrics_manager: "MetricsManager",
    ):
        """Initialize with managers."""
        self._health = health_manager
        self._metrics = metrics_manager
    
    def setup_routes(self, app: web.Application) -> None:
        """Register routes with aiohttp app."""
        app.router.add_get("/health", self.liveness)
        app.router.add_get("/health/ready", self.readiness)
        app.router.add_get("/health/detailed", self.detailed)
        app.router.add_get("/metrics", self.metrics)
    
    async def liveness(self, request: web.Request) -> web.Response:
        """
        Simple liveness check.
        
        Returns 200 if process is running.
        """
        pass
    
    async def readiness(self, request: web.Request) -> web.Response:
        """
        Readiness check.
        
        Returns 200 if ready to serve, 503 if not ready.
        """
        pass
    
    async def detailed(self, request: web.Request) -> web.Response:
        """
        Detailed health status.
        
        Returns full component status.
        """
        pass
    
    async def metrics(self, request: web.Request) -> web.Response:
        """
        Prometheus metrics endpoint.
        
        Returns metrics in Prometheus format.
        """
        pass


def create_health_routes(...) -> HealthRoutes:
    """Factory function for HealthRoutes."""
    pass
```

---

## Configuration

### New Configuration

```json
{
    "health": {
        "description": "Health check configuration",
        "enabled": "${BOT_HEALTH_ENABLED}",
        "port": "${BOT_HEALTH_PORT}",
        "defaults": {
            "enabled": true,
            "port": 8080
        }
    },
    "metrics": {
        "description": "Metrics collection configuration",
        "enabled": "${BOT_METRICS_ENABLED}",
        "defaults": {
            "enabled": true
        }
    },
    "circuit_breaker": {
        "description": "Circuit breaker configuration",
        "nlp_failure_threshold": "${BOT_CB_NLP_FAILURES}",
        "nlp_timeout_seconds": "${BOT_CB_NLP_TIMEOUT}",
        "defaults": {
            "nlp_failure_threshold": 5,
            "nlp_timeout_seconds": 30
        }
    }
}
```

### Environment Variables to Add

```bash
# Health Check Configuration
BOT_HEALTH_ENABLED=true
BOT_HEALTH_PORT=8080

# Metrics Configuration
BOT_METRICS_ENABLED=true

# Circuit Breaker Configuration
BOT_CB_NLP_FAILURES=5
BOT_CB_NLP_TIMEOUT=30
```

---

## Testing Requirements

### Unit Tests

```python
"""Tests for Phase 5 components."""

class TestHealthManager:
    """Test suite for HealthManager."""
    
    @pytest.mark.asyncio
    async def test_check_health_all_healthy(self):
        """Test health check when all components healthy."""
        pass
    
    @pytest.mark.asyncio
    async def test_check_health_nlp_down(self):
        """Test degraded status when NLP is down."""
        pass
    
    @pytest.mark.asyncio
    async def test_check_health_discord_down(self):
        """Test unhealthy status when Discord is down."""
        pass


class TestMetricsManager:
    """Test suite for MetricsManager."""
    
    def test_counter_increment(self):
        """Test counter increments correctly."""
        pass
    
    def test_histogram_observe(self):
        """Test histogram records observations."""
        pass
    
    def test_export_prometheus_format(self):
        """Test Prometheus export format."""
        pass


class TestCircuitBreaker:
    """Test suite for CircuitBreaker."""
    
    @pytest.mark.asyncio
    async def test_closed_state_passes_through(self):
        """Test calls pass through when closed."""
        pass
    
    @pytest.mark.asyncio
    async def test_opens_after_failures(self):
        """Test circuit opens after threshold failures."""
        pass
    
    @pytest.mark.asyncio
    async def test_half_open_after_timeout(self):
        """Test circuit goes half-open after timeout."""
        pass
```

---

## Step-by-Step Implementation

### Step 5.1: Create Utility Classes

1. Create `src/utils/__init__.py`
2. Implement `src/utils/circuit_breaker.py`
3. Implement `src/utils/retry.py`
4. Write unit tests

### Step 5.2: Implement Metrics Manager

1. Create `src/managers/metrics/__init__.py`
2. Implement `MetricsManager` class
3. Add metric recording calls to existing managers
4. Write unit tests

### Step 5.3: Implement Health Manager

1. Create `src/managers/health/__init__.py`
2. Implement `HealthManager` class
3. Implement component health checks
4. Write unit tests

### Step 5.4: Implement Health HTTP Endpoints

1. Create `src/api/__init__.py`
2. Implement `HealthRoutes` class
3. Add aiohttp to requirements.txt
4. Integrate with main.py
5. Write tests

### Step 5.5: Add Error Recovery to Managers

1. Add circuit breaker to NLPClientManager
2. Add connection recovery to RedisManager
3. Add reconnection handling to DiscordManager
4. Update error logging throughout

### Step 5.6: Create Operational Documentation

1. Create `docs/operations/runbook.md`
2. Create `docs/operations/troubleshooting.md`
3. Create `docs/operations/deployment.md`
4. Update README.md with operations section

### Step 5.7: Update Configuration

1. Add health/metrics/circuit_breaker sections to default.json
2. Add environment variables to .env.template
3. Update docker-compose.yml with health check

### Step 5.8: Integration Testing

1. Test full startup sequence
2. Test graceful degradation scenarios
3. Test health endpoints
4. Test metrics collection
5. Load testing (optional)

---

## Acceptance Criteria

### Must Have

- [ ] Health check endpoints respond correctly
- [ ] Circuit breaker prevents cascading NLP failures
- [ ] Bot continues operating when Redis unavailable
- [ ] Bot continues operating when Claude API unavailable
- [ ] Metrics are collected for all operations
- [ ] Graceful shutdown handles cleanup
- [ ] Operational runbook is complete
- [ ] All unit tests passing

### Should Have

- [ ] Prometheus metrics endpoint
- [ ] Detailed health status with component breakdown
- [ ] Automatic recovery from transient failures
- [ ] Error rate alerting via webhook

### Nice to Have

- [ ] Dashboard configuration (Grafana)
- [ ] Performance benchmarks documented
- [ ] Chaos testing scenarios

---

## Operational Documentation Outline

### runbook.md

1. **Startup Procedures**
   - Pre-flight checks
   - Starting the bot
   - Verifying healthy startup

2. **Monitoring**
   - Health check URLs
   - Key metrics to watch
   - Alert thresholds

3. **Common Operations**
   - Restarting the bot
   - Rotating secrets
   - Updating configuration

4. **Incident Response**
   - Escalation procedures
   - Communication templates
   - Post-incident review

### troubleshooting.md

1. **Discord Connection Issues**
2. **NLP API Failures**
3. **Redis Connection Issues**
4. **Claude API Failures**
5. **High Memory Usage**
6. **High Latency**

### deployment.md

1. **Prerequisites**
2. **Environment Setup**
3. **Secret Management**
4. **Deployment Steps**
5. **Rollback Procedures**
6. **Blue-Green Deployment**

---

## Notes

```
Implementation notes will be added here as we progress...
```

---

**Built with care for chosen family** 🏳️‍🌈
