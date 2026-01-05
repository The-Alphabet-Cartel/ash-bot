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
Circuit Breaker Pattern Implementation for Ash-Bot Service
---
FILE VERSION: v5.0-5-5.1-1
LAST MODIFIED: 2026-01-04
PHASE: Phase 5 - Production Hardening
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-bot
Community: The Alphabet Cartel - https://discord.gg/alphabetcartel | https://alphabetcartel.org
============================================================================
RESPONSIBILITIES:
- Prevent cascading failures by failing fast when a service is unavailable
- Track failure counts and switch states appropriately
- Allow recovery testing via half-open state
- Provide visibility into circuit health

STATES:
- CLOSED: Normal operation, requests pass through
- OPEN: Failing fast, all requests rejected immediately
- HALF_OPEN: Testing if service has recovered

USAGE:
    from src.utils import CircuitBreaker, CircuitOpenError

    breaker = CircuitBreaker("nlp_api")

    try:
        result = await breaker.call(async_function, arg1, arg2)
    except CircuitOpenError:
        # Handle circuit open (service unavailable)
        pass
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, TypeVar

# Module version
__version__ = "v5.0-5-5.1-1"

# Initialize logger
logger = logging.getLogger(__name__)

# Type variable for generic return types
T = TypeVar("T")


# =============================================================================
# Enums and Configuration
# =============================================================================


class CircuitState(Enum):
    """
    Circuit breaker states.

    Attributes:
        CLOSED: Normal operation, requests pass through
        OPEN: Failing fast, requests rejected
        HALF_OPEN: Testing recovery, limited requests allowed
    """

    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass
class CircuitBreakerConfig:
    """
    Configuration for circuit breaker behavior.

    Attributes:
        failure_threshold: Number of failures before opening circuit
        success_threshold: Number of successes to close from half-open
        timeout_seconds: Time before attempting half-open from open
        excluded_exceptions: Exception types that don't count as failures
    """

    failure_threshold: int = 5
    success_threshold: int = 2
    timeout_seconds: float = 30.0
    excluded_exceptions: tuple = field(default_factory=tuple)

    def __post_init__(self):
        """Validate configuration values."""
        if self.failure_threshold < 1:
            raise ValueError("failure_threshold must be at least 1")
        if self.success_threshold < 1:
            raise ValueError("success_threshold must be at least 1")
        if self.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")


@dataclass
class CircuitBreakerState:
    """
    Internal state tracking for circuit breaker.

    Attributes:
        state: Current circuit state
        failure_count: Consecutive failures in closed state
        success_count: Consecutive successes in half-open state
        last_failure_time: Timestamp of last failure
        last_state_change: Timestamp of last state transition
        total_calls: Total calls made through breaker
        total_failures: Total failures recorded
        total_successes: Total successful calls
    """

    state: CircuitState = CircuitState.CLOSED
    failure_count: int = 0
    success_count: int = 0
    last_failure_time: Optional[float] = None
    last_state_change: float = field(default_factory=time.time)
    total_calls: int = 0
    total_failures: int = 0
    total_successes: int = 0


# =============================================================================
# Exceptions
# =============================================================================


class CircuitOpenError(Exception):
    """
    Raised when circuit breaker is open and rejecting requests.

    Attributes:
        breaker_name: Name of the circuit breaker
        time_until_retry: Seconds until circuit will try half-open
    """

    def __init__(
        self,
        breaker_name: str,
        time_until_retry: Optional[float] = None,
    ):
        self.breaker_name = breaker_name
        self.time_until_retry = time_until_retry
        message = f"Circuit breaker '{breaker_name}' is OPEN"
        if time_until_retry is not None and time_until_retry > 0:
            message += f" (retry in {time_until_retry:.1f}s)"
        super().__init__(message)


# =============================================================================
# Circuit Breaker Implementation
# =============================================================================


class CircuitBreaker:
    """
    Circuit breaker for protecting against cascading failures.

    Implements the circuit breaker pattern to prevent cascading failures
    when an external service becomes unavailable. After a threshold of
    failures, the circuit opens and fails fast without calling the service.
    After a timeout, it enters half-open state to test if the service
    has recovered.

    Attributes:
        name: Identifier for this circuit breaker
        config: Configuration parameters
        _state: Internal state tracking

    Example:
        >>> breaker = CircuitBreaker("nlp_api")
        >>>
        >>> async def call_api():
        ...     try:
        ...         result = await breaker.call(api_function, arg1)
        ...         return result
        ...     except CircuitOpenError as e:
        ...         logger.warning(f"Circuit open: {e}")
        ...         return fallback_value
    """

    def __init__(
        self,
        name: str,
        config: Optional[CircuitBreakerConfig] = None,
    ):
        """
        Initialize circuit breaker.

        Args:
            name: Identifier for this circuit breaker
            config: Configuration parameters (uses defaults if not provided)
        """
        self.name = name
        self.config = config or CircuitBreakerConfig()
        self._state = CircuitBreakerState()
        self._lock = asyncio.Lock()

        logger.info(
            f"✅ CircuitBreaker '{name}' initialized "
            f"(failures={self.config.failure_threshold}, "
            f"timeout={self.config.timeout_seconds}s)"
        )

    # =========================================================================
    # Properties
    # =========================================================================

    @property
    def state(self) -> CircuitState:
        """
        Get current circuit state.

        May transition from OPEN to HALF_OPEN if timeout has elapsed.
        """
        self._check_state_transition()
        return self._state.state

    @property
    def is_closed(self) -> bool:
        """Check if circuit is closed (normal operation)."""
        return self.state == CircuitState.CLOSED

    @property
    def is_open(self) -> bool:
        """Check if circuit is open (failing fast)."""
        return self.state == CircuitState.OPEN

    @property
    def is_half_open(self) -> bool:
        """Check if circuit is half-open (testing recovery)."""
        return self.state == CircuitState.HALF_OPEN

    @property
    def failure_count(self) -> int:
        """Get current consecutive failure count."""
        return self._state.failure_count

    @property
    def time_until_retry(self) -> Optional[float]:
        """
        Get seconds until circuit will transition to half-open.

        Returns:
            Seconds until retry, or None if not in OPEN state
        """
        if self._state.state != CircuitState.OPEN:
            return None

        if self._state.last_failure_time is None:
            return None

        elapsed = time.time() - self._state.last_failure_time
        remaining = self.config.timeout_seconds - elapsed
        return max(0, remaining)

    # =========================================================================
    # Main Call Method
    # =========================================================================

    async def call(
        self,
        func: Callable[..., Any],
        *args: Any,
        **kwargs: Any,
    ) -> T:
        """
        Call function through circuit breaker.

        Tracks successes and failures, transitioning states as needed.
        Raises CircuitOpenError if circuit is open.

        Args:
            func: Async function to call
            *args: Positional arguments for function
            **kwargs: Keyword arguments for function

        Returns:
            Result from function call

        Raises:
            CircuitOpenError: If circuit is open and rejecting calls
            Exception: Any exception from the wrapped function
        """
        async with self._lock:
            # Check if we should allow this call
            if not self._should_allow_call():
                raise CircuitOpenError(
                    breaker_name=self.name,
                    time_until_retry=self.time_until_retry,
                )

            self._state.total_calls += 1

        # Make the actual call outside the lock
        try:
            # Handle both sync and async functions
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)

            # Record success
            async with self._lock:
                self._on_success()

            return result

        except Exception as e:
            # Check if this exception should be excluded
            if isinstance(e, self.config.excluded_exceptions):
                async with self._lock:
                    self._on_success()
                raise

            # Record failure
            async with self._lock:
                self._on_failure(e)
            raise

    # =========================================================================
    # State Management
    # =========================================================================

    def _check_state_transition(self) -> None:
        """
        Check if state should transition based on timeout.

        Transitions from OPEN to HALF_OPEN after timeout elapses.
        """
        if self._state.state != CircuitState.OPEN:
            return

        if self._state.last_failure_time is None:
            return

        elapsed = time.time() - self._state.last_failure_time
        if elapsed >= self.config.timeout_seconds:
            self._transition_to(CircuitState.HALF_OPEN)
            logger.info(
                f"🔄 CircuitBreaker '{self.name}' transitioning to HALF_OPEN "
                f"(timeout elapsed after {elapsed:.1f}s)"
            )

    def _should_allow_call(self) -> bool:
        """
        Determine if a call should be allowed.

        Returns:
            True if call should proceed, False if should be rejected
        """
        self._check_state_transition()

        if self._state.state == CircuitState.CLOSED:
            return True

        if self._state.state == CircuitState.HALF_OPEN:
            # Allow calls in half-open to test recovery
            return True

        # Circuit is OPEN
        return False

    def _on_success(self) -> None:
        """
        Handle successful call.

        Updates counters and transitions state if appropriate.
        """
        self._state.total_successes += 1
        self._state.failure_count = 0

        if self._state.state == CircuitState.HALF_OPEN:
            self._state.success_count += 1

            if self._state.success_count >= self.config.success_threshold:
                self._transition_to(CircuitState.CLOSED)
                logger.info(
                    f"✅ CircuitBreaker '{self.name}' CLOSED "
                    f"(recovery confirmed after {self._state.success_count} successes)"
                )

    def _on_failure(self, exception: Exception) -> None:
        """
        Handle failed call.

        Updates counters and transitions state if appropriate.

        Args:
            exception: The exception that occurred
        """
        self._state.total_failures += 1
        self._state.failure_count += 1
        self._state.last_failure_time = time.time()
        self._state.success_count = 0  # Reset success count

        if self._state.state == CircuitState.CLOSED:
            if self._state.failure_count >= self.config.failure_threshold:
                self._transition_to(CircuitState.OPEN)
                logger.warning(
                    f"🔴 CircuitBreaker '{self.name}' OPENED "
                    f"(threshold {self.config.failure_threshold} failures reached): "
                    f"{type(exception).__name__}: {exception}"
                )

        elif self._state.state == CircuitState.HALF_OPEN:
            # Any failure in half-open immediately opens the circuit
            self._transition_to(CircuitState.OPEN)
            logger.warning(
                f"🔴 CircuitBreaker '{self.name}' re-OPENED from HALF_OPEN "
                f"(recovery failed): {type(exception).__name__}: {exception}"
            )

    def _transition_to(self, new_state: CircuitState) -> None:
        """
        Transition to a new state.

        Args:
            new_state: The state to transition to
        """
        old_state = self._state.state
        self._state.state = new_state
        self._state.last_state_change = time.time()

        if new_state == CircuitState.CLOSED:
            self._state.failure_count = 0
            self._state.success_count = 0

        elif new_state == CircuitState.HALF_OPEN:
            self._state.success_count = 0

        logger.debug(
            f"CircuitBreaker '{self.name}' state: {old_state.value} → {new_state.value}"
        )

    # =========================================================================
    # Manual Control
    # =========================================================================

    async def reset(self) -> None:
        """
        Manually reset circuit to closed state.

        Use with caution - should only be done when you know
        the service has recovered.
        """
        async with self._lock:
            self._transition_to(CircuitState.CLOSED)
            logger.info(f"🔧 CircuitBreaker '{self.name}' manually reset to CLOSED")

    async def trip(self) -> None:
        """
        Manually trip circuit to open state.

        Can be used for maintenance or testing.
        """
        async with self._lock:
            self._state.last_failure_time = time.time()
            self._transition_to(CircuitState.OPEN)
            logger.info(f"🔧 CircuitBreaker '{self.name}' manually tripped to OPEN")

    # =========================================================================
    # Metrics and Status
    # =========================================================================

    def get_metrics(self) -> Dict[str, Any]:
        """
        Get circuit breaker metrics.

        Returns:
            Dictionary of metrics for monitoring
        """
        return {
            "name": self.name,
            "state": self._state.state.value,
            "failure_count": self._state.failure_count,
            "success_count": self._state.success_count,
            "total_calls": self._state.total_calls,
            "total_failures": self._state.total_failures,
            "total_successes": self._state.total_successes,
            "time_until_retry": self.time_until_retry,
            "config": {
                "failure_threshold": self.config.failure_threshold,
                "success_threshold": self.config.success_threshold,
                "timeout_seconds": self.config.timeout_seconds,
            },
        }

    def __repr__(self) -> str:
        """String representation for debugging."""
        return (
            f"CircuitBreaker("
            f"name='{self.name}', "
            f"state={self._state.state.value}, "
            f"failures={self._state.failure_count}/{self.config.failure_threshold})"
        )


# =============================================================================
# Factory Function
# =============================================================================


def create_circuit_breaker(
    name: str,
    failure_threshold: int = 5,
    success_threshold: int = 2,
    timeout_seconds: float = 30.0,
    excluded_exceptions: Optional[tuple] = None,
) -> CircuitBreaker:
    """
    Factory function for CircuitBreaker.

    Creates a configured CircuitBreaker instance.
    Following Clean Architecture v5.1 Rule #1: Factory Functions.

    Args:
        name: Identifier for this circuit breaker
        failure_threshold: Failures before opening circuit
        success_threshold: Successes to close from half-open
        timeout_seconds: Time before testing half-open
        excluded_exceptions: Exception types that don't count as failures

    Returns:
        Configured CircuitBreaker instance

    Example:
        >>> breaker = create_circuit_breaker(
        ...     name="nlp_api",
        ...     failure_threshold=5,
        ...     timeout_seconds=30.0
        ... )
    """
    config = CircuitBreakerConfig(
        failure_threshold=failure_threshold,
        success_threshold=success_threshold,
        timeout_seconds=timeout_seconds,
        excluded_exceptions=excluded_exceptions or tuple(),
    )
    return CircuitBreaker(name=name, config=config)


# =============================================================================
# Export public interface
# =============================================================================

__all__ = [
    "CircuitBreaker",
    "CircuitState",
    "CircuitBreakerConfig",
    "CircuitBreakerState",
    "CircuitOpenError",
    "create_circuit_breaker",
]
