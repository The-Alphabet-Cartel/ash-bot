"""
============================================================================
Ash-Bot: Crisis Detection Discord Bot
The Alphabet Cartel - https://discord.gg/alphabetcartel | alphabetcartel.org
============================================================================
Test Suite for Circuit Breaker
---
FILE VERSION: v5.0-5-5.1-1
LAST MODIFIED: 2026-01-04
PHASE: Phase 5 - Production Hardening
Repository: https://github.com/the-alphabet-cartel/ash-bot
============================================================================
Tests for CircuitBreaker utility class.
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.utils.circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerConfig,
    CircuitState,
    CircuitOpenError,
    create_circuit_breaker,
)


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def default_breaker() -> CircuitBreaker:
    """Create a circuit breaker with default config."""
    return CircuitBreaker(name="test_breaker")


@pytest.fixture
def fast_breaker() -> CircuitBreaker:
    """Create a circuit breaker with fast timeout for testing."""
    config = CircuitBreakerConfig(
        failure_threshold=3,
        success_threshold=2,
        timeout_seconds=0.1,  # 100ms for fast testing
    )
    return CircuitBreaker(name="fast_breaker", config=config)


@pytest.fixture
def successful_func() -> AsyncMock:
    """Create a mock function that succeeds."""
    mock = AsyncMock(return_value="success")
    return mock


@pytest.fixture
def failing_func() -> AsyncMock:
    """Create a mock function that always fails."""
    mock = AsyncMock(side_effect=RuntimeError("Test failure"))
    return mock


# =============================================================================
# Configuration Tests
# =============================================================================


class TestCircuitBreakerConfig:
    """Tests for CircuitBreakerConfig."""

    def test_default_config(self):
        """Test default configuration values."""
        config = CircuitBreakerConfig()
        
        assert config.failure_threshold == 5
        assert config.success_threshold == 2
        assert config.timeout_seconds == 30.0
        assert config.excluded_exceptions == ()

    def test_custom_config(self):
        """Test custom configuration values."""
        config = CircuitBreakerConfig(
            failure_threshold=10,
            success_threshold=3,
            timeout_seconds=60.0,
        )
        
        assert config.failure_threshold == 10
        assert config.success_threshold == 3
        assert config.timeout_seconds == 60.0

    def test_invalid_failure_threshold(self):
        """Test that failure_threshold < 1 raises error."""
        with pytest.raises(ValueError, match="failure_threshold must be at least 1"):
            CircuitBreakerConfig(failure_threshold=0)

    def test_invalid_success_threshold(self):
        """Test that success_threshold < 1 raises error."""
        with pytest.raises(ValueError, match="success_threshold must be at least 1"):
            CircuitBreakerConfig(success_threshold=0)

    def test_invalid_timeout(self):
        """Test that timeout_seconds <= 0 raises error."""
        with pytest.raises(ValueError, match="timeout_seconds must be positive"):
            CircuitBreakerConfig(timeout_seconds=0)


# =============================================================================
# Initialization Tests
# =============================================================================


class TestCircuitBreakerInit:
    """Tests for CircuitBreaker initialization."""

    def test_default_initialization(self, default_breaker):
        """Test default initialization."""
        assert default_breaker.name == "test_breaker"
        assert default_breaker.state == CircuitState.CLOSED
        assert default_breaker.is_closed
        assert not default_breaker.is_open
        assert not default_breaker.is_half_open
        assert default_breaker.failure_count == 0

    def test_factory_function(self):
        """Test factory function creates breaker correctly."""
        breaker = create_circuit_breaker(
            name="factory_test",
            failure_threshold=3,
            timeout_seconds=15.0,
        )
        
        assert breaker.name == "factory_test"
        assert breaker.config.failure_threshold == 3
        assert breaker.config.timeout_seconds == 15.0

    def test_repr(self, default_breaker):
        """Test string representation."""
        repr_str = repr(default_breaker)
        assert "test_breaker" in repr_str
        assert "closed" in repr_str


# =============================================================================
# Normal Operation Tests (Closed State)
# =============================================================================


class TestClosedState:
    """Tests for circuit breaker in closed state."""

    @pytest.mark.asyncio
    async def test_successful_call(self, default_breaker, successful_func):
        """Test successful call passes through."""
        result = await default_breaker.call(successful_func)
        
        assert result == "success"
        successful_func.assert_called_once()
        assert default_breaker.is_closed
        assert default_breaker.failure_count == 0

    @pytest.mark.asyncio
    async def test_multiple_successful_calls(self, default_breaker, successful_func):
        """Test multiple successful calls work."""
        for _ in range(5):
            result = await default_breaker.call(successful_func)
            assert result == "success"
        
        assert successful_func.call_count == 5
        assert default_breaker.is_closed

    @pytest.mark.asyncio
    async def test_single_failure_stays_closed(self, fast_breaker, failing_func):
        """Test single failure doesn't open circuit."""
        with pytest.raises(RuntimeError):
            await fast_breaker.call(failing_func)
        
        assert fast_breaker.is_closed
        assert fast_breaker.failure_count == 1

    @pytest.mark.asyncio
    async def test_failure_below_threshold_stays_closed(self, fast_breaker, failing_func):
        """Test failures below threshold don't open circuit."""
        # Fast breaker has threshold of 3
        for _ in range(2):
            with pytest.raises(RuntimeError):
                await fast_breaker.call(failing_func)
        
        assert fast_breaker.is_closed
        assert fast_breaker.failure_count == 2

    @pytest.mark.asyncio
    async def test_success_resets_failure_count(self, fast_breaker):
        """Test success resets failure count."""
        failing = AsyncMock(side_effect=RuntimeError("fail"))
        success = AsyncMock(return_value="ok")
        
        # Two failures
        for _ in range(2):
            with pytest.raises(RuntimeError):
                await fast_breaker.call(failing)
        
        assert fast_breaker.failure_count == 2
        
        # One success
        await fast_breaker.call(success)
        
        assert fast_breaker.failure_count == 0
        assert fast_breaker.is_closed


# =============================================================================
# Opening Circuit Tests
# =============================================================================


class TestCircuitOpening:
    """Tests for circuit breaker opening on failures."""

    @pytest.mark.asyncio
    async def test_opens_after_threshold_failures(self, fast_breaker, failing_func):
        """Test circuit opens after reaching failure threshold."""
        # Fast breaker has threshold of 3
        for i in range(3):
            with pytest.raises(RuntimeError):
                await fast_breaker.call(failing_func)
        
        assert fast_breaker.is_open
        assert fast_breaker.failure_count == 3

    @pytest.mark.asyncio
    async def test_open_circuit_rejects_calls(self, fast_breaker, failing_func):
        """Test open circuit rejects subsequent calls."""
        # Open the circuit
        for _ in range(3):
            with pytest.raises(RuntimeError):
                await fast_breaker.call(failing_func)
        
        assert fast_breaker.is_open
        
        # Try another call - should raise CircuitOpenError
        with pytest.raises(CircuitOpenError) as exc_info:
            await fast_breaker.call(failing_func)
        
        assert exc_info.value.breaker_name == "fast_breaker"
        # Function shouldn't have been called again (still 3 calls)
        assert failing_func.call_count == 3

    @pytest.mark.asyncio
    async def test_circuit_open_error_details(self, fast_breaker, failing_func):
        """Test CircuitOpenError contains correct details."""
        # Open the circuit
        for _ in range(3):
            with pytest.raises(RuntimeError):
                await fast_breaker.call(failing_func)
        
        with pytest.raises(CircuitOpenError) as exc_info:
            await fast_breaker.call(failing_func)
        
        error = exc_info.value
        assert error.breaker_name == "fast_breaker"
        assert error.time_until_retry is not None
        assert error.time_until_retry > 0


# =============================================================================
# Half-Open State Tests
# =============================================================================


class TestHalfOpenState:
    """Tests for circuit breaker in half-open state."""

    @pytest.mark.asyncio
    async def test_transitions_to_half_open_after_timeout(self, fast_breaker, failing_func):
        """Test circuit transitions to half-open after timeout."""
        # Open the circuit
        for _ in range(3):
            with pytest.raises(RuntimeError):
                await fast_breaker.call(failing_func)
        
        assert fast_breaker.is_open
        
        # Wait for timeout (100ms)
        await asyncio.sleep(0.15)
        
        # State check should trigger transition
        assert fast_breaker.is_half_open

    @pytest.mark.asyncio
    async def test_half_open_allows_calls(self, fast_breaker, failing_func):
        """Test half-open state allows calls through."""
        # Open the circuit
        for _ in range(3):
            with pytest.raises(RuntimeError):
                await fast_breaker.call(failing_func)
        
        # Wait for timeout
        await asyncio.sleep(0.15)
        
        success = AsyncMock(return_value="ok")
        result = await fast_breaker.call(success)
        
        assert result == "ok"
        success.assert_called_once()

    @pytest.mark.asyncio
    async def test_half_open_closes_on_success(self, fast_breaker, failing_func):
        """Test circuit closes after success_threshold successes in half-open."""
        # Open the circuit
        for _ in range(3):
            with pytest.raises(RuntimeError):
                await fast_breaker.call(failing_func)
        
        # Wait for timeout
        await asyncio.sleep(0.15)
        
        success = AsyncMock(return_value="ok")
        
        # Fast breaker needs 2 successes to close
        for _ in range(2):
            await fast_breaker.call(success)
        
        assert fast_breaker.is_closed

    @pytest.mark.asyncio
    async def test_half_open_reopens_on_failure(self, fast_breaker, failing_func):
        """Test circuit reopens immediately on failure in half-open."""
        # Open the circuit
        for _ in range(3):
            with pytest.raises(RuntimeError):
                await fast_breaker.call(failing_func)
        
        # Wait for timeout
        await asyncio.sleep(0.15)
        
        assert fast_breaker.is_half_open
        
        # Failure in half-open should reopen
        with pytest.raises(RuntimeError):
            await fast_breaker.call(failing_func)
        
        assert fast_breaker.is_open


# =============================================================================
# Excluded Exceptions Tests
# =============================================================================


class TestExcludedExceptions:
    """Tests for excluded exception handling."""

    @pytest.mark.asyncio
    async def test_excluded_exceptions_dont_count(self):
        """Test excluded exceptions don't count toward failures."""
        config = CircuitBreakerConfig(
            failure_threshold=3,
            excluded_exceptions=(ValueError,),
        )
        breaker = CircuitBreaker("exclude_test", config)
        
        # ValueError should not count
        failing = AsyncMock(side_effect=ValueError("not counted"))
        
        for _ in range(5):
            with pytest.raises(ValueError):
                await breaker.call(failing)
        
        # Should still be closed
        assert breaker.is_closed
        assert breaker.failure_count == 0

    @pytest.mark.asyncio
    async def test_non_excluded_exceptions_count(self):
        """Test non-excluded exceptions count toward failures."""
        config = CircuitBreakerConfig(
            failure_threshold=3,
            excluded_exceptions=(ValueError,),
        )
        breaker = CircuitBreaker("exclude_test", config)
        
        # RuntimeError should count
        failing = AsyncMock(side_effect=RuntimeError("counted"))
        
        for _ in range(3):
            with pytest.raises(RuntimeError):
                await breaker.call(failing)
        
        assert breaker.is_open


# =============================================================================
# Manual Control Tests
# =============================================================================


class TestManualControl:
    """Tests for manual circuit control."""

    @pytest.mark.asyncio
    async def test_manual_reset(self, fast_breaker, failing_func):
        """Test manual reset to closed state."""
        # Open the circuit
        for _ in range(3):
            with pytest.raises(RuntimeError):
                await fast_breaker.call(failing_func)
        
        assert fast_breaker.is_open
        
        await fast_breaker.reset()
        
        assert fast_breaker.is_closed

    @pytest.mark.asyncio
    async def test_manual_trip(self, default_breaker):
        """Test manual trip to open state."""
        assert default_breaker.is_closed
        
        await default_breaker.trip()
        
        assert default_breaker.is_open


# =============================================================================
# Metrics Tests
# =============================================================================


class TestMetrics:
    """Tests for circuit breaker metrics."""

    @pytest.mark.asyncio
    async def test_metrics_tracking(self, fast_breaker):
        """Test metrics are tracked correctly."""
        success = AsyncMock(return_value="ok")
        failure = AsyncMock(side_effect=RuntimeError("fail"))
        
        # 3 successes
        for _ in range(3):
            await fast_breaker.call(success)
        
        # 2 failures (not enough to open)
        for _ in range(2):
            with pytest.raises(RuntimeError):
                await fast_breaker.call(failure)
        
        metrics = fast_breaker.get_metrics()
        
        assert metrics["name"] == "fast_breaker"
        assert metrics["state"] == "closed"
        assert metrics["total_calls"] == 5
        assert metrics["total_successes"] == 3
        assert metrics["total_failures"] == 2

    def test_time_until_retry_when_closed(self, default_breaker):
        """Test time_until_retry is None when closed."""
        assert default_breaker.time_until_retry is None

    @pytest.mark.asyncio
    async def test_time_until_retry_when_open(self, fast_breaker, failing_func):
        """Test time_until_retry returns value when open."""
        # Open the circuit
        for _ in range(3):
            with pytest.raises(RuntimeError):
                await fast_breaker.call(failing_func)
        
        assert fast_breaker.time_until_retry is not None
        assert fast_breaker.time_until_retry > 0


# =============================================================================
# Sync Function Tests
# =============================================================================


class TestSyncFunctions:
    """Tests for handling synchronous functions."""

    @pytest.mark.asyncio
    async def test_sync_function_success(self, default_breaker):
        """Test calling sync function through breaker."""
        sync_func = MagicMock(return_value="sync_result")
        
        result = await default_breaker.call(sync_func)
        
        assert result == "sync_result"
        sync_func.assert_called_once()

    @pytest.mark.asyncio
    async def test_sync_function_failure(self, fast_breaker):
        """Test sync function failures are tracked."""
        sync_func = MagicMock(side_effect=RuntimeError("sync fail"))
        
        for _ in range(3):
            with pytest.raises(RuntimeError):
                await fast_breaker.call(sync_func)
        
        assert fast_breaker.is_open


# =============================================================================
# Concurrency Tests
# =============================================================================


class TestConcurrency:
    """Tests for concurrent access."""

    @pytest.mark.asyncio
    async def test_concurrent_calls(self, default_breaker):
        """Test concurrent calls are handled safely."""
        call_count = 0
        
        async def increment():
            nonlocal call_count
            await asyncio.sleep(0.01)
            call_count += 1
            return call_count
        
        # Make 10 concurrent calls
        tasks = [default_breaker.call(increment) for _ in range(10)]
        results = await asyncio.gather(*tasks)
        
        assert len(results) == 10
        assert call_count == 10

    @pytest.mark.asyncio
    async def test_concurrent_failures(self, fast_breaker):
        """Test concurrent failures don't over-increment."""
        async def fail():
            await asyncio.sleep(0.01)
            raise RuntimeError("concurrent fail")
        
        # Make concurrent failing calls
        tasks = [fast_breaker.call(fail) for _ in range(10)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # All should be errors
        errors = [r for r in results if isinstance(r, Exception)]
        assert len(errors) == 10
        
        # Some should be RuntimeError (before opening)
        # Some should be CircuitOpenError (after opening)
        runtime_errors = [e for e in errors if isinstance(e, RuntimeError)]
        circuit_errors = [e for e in errors if isinstance(e, CircuitOpenError)]
        
        assert len(runtime_errors) >= 3  # At least threshold amount
        assert fast_breaker.is_open
