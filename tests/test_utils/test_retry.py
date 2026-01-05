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
Test Suite for Retry Utilities
---
FILE VERSION: v5.0-5-5.1-1
LAST MODIFIED: 2026-01-04
PHASE: Phase 5 - Production Hardening
Repository: https://github.com/the-alphabet-cartel/ash-bot
============================================================================
Tests for retry utility functions and decorators.
"""

import asyncio
import time
from unittest.mock import AsyncMock, MagicMock, call

import pytest

from src.utils.retry import (
    RetryConfig,
    RetryError,
    calculate_delay,
    retry_async,
    retry_sync,
    should_retry,
    with_retry,
)


# =============================================================================
# Configuration Tests
# =============================================================================


class TestRetryConfig:
    """Tests for RetryConfig."""

    def test_default_config(self):
        """Test default configuration values."""
        config = RetryConfig()

        assert config.max_attempts == 3
        assert config.base_delay == 1.0
        assert config.max_delay == 60.0
        assert config.exponential_base == 2.0
        assert config.jitter is True
        assert config.jitter_factor == 0.1
        assert config.retryable_exceptions == (Exception,)
        assert config.non_retryable_exceptions == ()

    def test_custom_config(self):
        """Test custom configuration values."""
        config = RetryConfig(
            max_attempts=5,
            base_delay=0.5,
            max_delay=30.0,
            exponential_base=3.0,
            jitter=False,
        )

        assert config.max_attempts == 5
        assert config.base_delay == 0.5
        assert config.max_delay == 30.0
        assert config.exponential_base == 3.0
        assert config.jitter is False

    def test_invalid_max_attempts(self):
        """Test that max_attempts < 1 raises error."""
        with pytest.raises(ValueError, match="max_attempts must be at least 1"):
            RetryConfig(max_attempts=0)

    def test_invalid_base_delay(self):
        """Test that negative base_delay raises error."""
        with pytest.raises(ValueError, match="base_delay must be non-negative"):
            RetryConfig(base_delay=-1)

    def test_invalid_max_delay(self):
        """Test that max_delay < base_delay raises error."""
        with pytest.raises(ValueError, match="max_delay must be >= base_delay"):
            RetryConfig(base_delay=10.0, max_delay=5.0)

    def test_invalid_exponential_base(self):
        """Test that exponential_base < 1 raises error."""
        with pytest.raises(ValueError, match="exponential_base must be at least 1"):
            RetryConfig(exponential_base=0.5)

    def test_invalid_jitter_factor(self):
        """Test that jitter_factor outside [0, 1] raises error."""
        with pytest.raises(ValueError, match="jitter_factor must be between 0 and 1"):
            RetryConfig(jitter_factor=1.5)


# =============================================================================
# Calculate Delay Tests
# =============================================================================


class TestCalculateDelay:
    """Tests for calculate_delay function."""

    def test_first_attempt_delay(self):
        """Test delay for first attempt (attempt 0)."""
        config = RetryConfig(base_delay=1.0, jitter=False)
        delay = calculate_delay(0, config)
        assert delay == 1.0

    def test_exponential_backoff(self):
        """Test exponential increase in delays."""
        config = RetryConfig(base_delay=1.0, exponential_base=2.0, jitter=False)

        assert calculate_delay(0, config) == 1.0
        assert calculate_delay(1, config) == 2.0
        assert calculate_delay(2, config) == 4.0
        assert calculate_delay(3, config) == 8.0

    def test_max_delay_cap(self):
        """Test delay is capped at max_delay."""
        config = RetryConfig(
            base_delay=1.0,
            max_delay=5.0,
            exponential_base=2.0,
            jitter=False,
        )

        # 8.0 would exceed max_delay of 5.0
        assert calculate_delay(3, config) == 5.0
        assert calculate_delay(4, config) == 5.0

    def test_jitter_adds_variation(self):
        """Test jitter adds variation to delays."""
        config = RetryConfig(base_delay=10.0, jitter=True, jitter_factor=0.1)

        # Get multiple delays and check they vary
        delays = [calculate_delay(0, config) for _ in range(100)]

        # Should have some variation
        assert min(delays) < 10.0
        assert max(delays) > 10.0
        # But within jitter bounds
        assert min(delays) >= 9.0
        assert max(delays) <= 11.0


# =============================================================================
# Should Retry Tests
# =============================================================================


class TestShouldRetry:
    """Tests for should_retry function."""

    def test_default_retries_all_exceptions(self):
        """Test default config retries all exceptions."""
        config = RetryConfig()

        assert should_retry(ValueError("test"), config) is True
        assert should_retry(RuntimeError("test"), config) is True
        assert should_retry(Exception("test"), config) is True

    def test_specific_retryable_exceptions(self):
        """Test only specified exceptions are retried."""
        config = RetryConfig(retryable_exceptions=(ValueError, TypeError))

        assert should_retry(ValueError("test"), config) is True
        assert should_retry(TypeError("test"), config) is True
        assert should_retry(RuntimeError("test"), config) is False

    def test_non_retryable_exceptions(self):
        """Test non-retryable exceptions are not retried."""
        config = RetryConfig(non_retryable_exceptions=(KeyboardInterrupt,))

        assert should_retry(ValueError("test"), config) is True
        assert should_retry(KeyboardInterrupt(), config) is False

    def test_non_retryable_takes_precedence(self):
        """Test non-retryable takes precedence over retryable."""
        config = RetryConfig(
            retryable_exceptions=(Exception,),
            non_retryable_exceptions=(ValueError,),
        )

        # ValueError is both Exception and in non_retryable
        assert should_retry(ValueError("test"), config) is False
        assert should_retry(RuntimeError("test"), config) is True


# =============================================================================
# Retry Async Tests
# =============================================================================


class TestRetryAsync:
    """Tests for retry_async function."""

    @pytest.mark.asyncio
    async def test_success_no_retry(self):
        """Test successful call doesn't retry."""
        func = AsyncMock(return_value="success")

        result = await retry_async(func)

        assert result == "success"
        func.assert_called_once()

    @pytest.mark.asyncio
    async def test_retry_on_failure(self):
        """Test function is retried on failure."""
        func = AsyncMock(
            side_effect=[RuntimeError("fail1"), RuntimeError("fail2"), "success"]
        )

        result = await retry_async(func, max_attempts=3, base_delay=0.01)

        assert result == "success"
        assert func.call_count == 3

    @pytest.mark.asyncio
    async def test_raises_after_max_attempts(self):
        """Test RetryError raised after max attempts."""
        func = AsyncMock(side_effect=RuntimeError("always fails"))

        with pytest.raises(RetryError) as exc_info:
            await retry_async(func, max_attempts=3, base_delay=0.01)

        error = exc_info.value
        assert error.attempts == 3
        assert isinstance(error.last_exception, RuntimeError)
        assert len(error.all_exceptions) == 3

    @pytest.mark.asyncio
    async def test_passes_args_and_kwargs(self):
        """Test arguments are passed correctly."""
        func = AsyncMock(return_value="result")

        await retry_async(func, args=("arg1",), kwargs={"key": "value"})

        func.assert_called_once_with("arg1", key="value")

    @pytest.mark.asyncio
    async def test_non_retryable_exception_not_retried(self):
        """Test non-retryable exceptions are not retried."""
        config = RetryConfig(
            max_attempts=3,
            non_retryable_exceptions=(ValueError,),
        )
        func = AsyncMock(side_effect=ValueError("not retryable"))

        with pytest.raises(ValueError):
            await retry_async(func, config=config)

        # Should only be called once
        func.assert_called_once()

    @pytest.mark.asyncio
    async def test_retryable_exception_filter(self):
        """Test only retryable exceptions trigger retry."""
        config = RetryConfig(
            max_attempts=3,
            base_delay=0.01,
            retryable_exceptions=(ConnectionError,),
        )
        func = AsyncMock(side_effect=RuntimeError("not retryable"))

        with pytest.raises(RuntimeError):
            await retry_async(func, config=config)

        func.assert_called_once()

    @pytest.mark.asyncio
    async def test_on_retry_callback(self):
        """Test on_retry callback is called."""
        callback = MagicMock()
        config = RetryConfig(
            max_attempts=3,
            base_delay=0.01,
            on_retry=callback,
        )
        func = AsyncMock(side_effect=[RuntimeError("fail"), "success"])

        await retry_async(func, config=config)

        # Callback should be called once (before retry)
        callback.assert_called_once()
        call_args = callback.call_args[0]
        assert call_args[0] == 1  # attempt number
        assert isinstance(call_args[1], RuntimeError)  # exception
        assert call_args[2] >= 0  # delay

    @pytest.mark.asyncio
    async def test_sync_function_handling(self):
        """Test retry_async handles sync functions."""
        sync_func = MagicMock(return_value="sync_result")

        result = await retry_async(sync_func)

        assert result == "sync_result"
        sync_func.assert_called_once()


# =============================================================================
# Retry Sync Tests
# =============================================================================


class TestRetrySync:
    """Tests for retry_sync function."""

    def test_success_no_retry(self):
        """Test successful call doesn't retry."""
        func = MagicMock(return_value="success")

        result = retry_sync(func)

        assert result == "success"
        func.assert_called_once()

    def test_retry_on_failure(self):
        """Test function is retried on failure."""
        func = MagicMock(side_effect=[RuntimeError("fail"), "success"])
        config = RetryConfig(max_attempts=3, base_delay=0.01)

        result = retry_sync(func, config=config)

        assert result == "success"
        assert func.call_count == 2

    def test_raises_after_max_attempts(self):
        """Test RetryError raised after max attempts."""
        func = MagicMock(side_effect=RuntimeError("always fails"))
        config = RetryConfig(max_attempts=3, base_delay=0.01)

        with pytest.raises(RetryError) as exc_info:
            retry_sync(func, config=config)

        error = exc_info.value
        assert error.attempts == 3


# =============================================================================
# Decorator Tests
# =============================================================================


class TestWithRetryDecorator:
    """Tests for @with_retry decorator."""

    @pytest.mark.asyncio
    async def test_decorator_success(self):
        """Test decorator on successful function."""

        @with_retry(max_attempts=3, base_delay=0.01)
        async def success_func():
            return "decorated success"

        result = await success_func()
        assert result == "decorated success"

    @pytest.mark.asyncio
    async def test_decorator_retry(self):
        """Test decorator retries on failure."""
        call_count = 0

        @with_retry(max_attempts=3, base_delay=0.01)
        async def flaky_func():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise RuntimeError("not yet")
            return "finally success"

        result = await flaky_func()

        assert result == "finally success"
        assert call_count == 3

    @pytest.mark.asyncio
    async def test_decorator_preserves_function_name(self):
        """Test decorator preserves function metadata."""

        @with_retry()
        async def named_function():
            """Function docstring."""
            return "result"

        assert named_function.__name__ == "named_function"
        assert named_function.__doc__ == "Function docstring."

    @pytest.mark.asyncio
    async def test_decorator_with_arguments(self):
        """Test decorated function receives arguments."""

        @with_retry(max_attempts=2, base_delay=0.01)
        async def func_with_args(a, b, key=None):
            return f"{a}-{b}-{key}"

        result = await func_with_args("x", "y", key="z")
        assert result == "x-y-z"

    @pytest.mark.asyncio
    async def test_decorator_exhausts_retries(self):
        """Test decorator raises RetryError after max attempts."""

        @with_retry(max_attempts=3, base_delay=0.01)
        async def always_fails():
            raise RuntimeError("permanent failure")

        with pytest.raises(RetryError) as exc_info:
            await always_fails()

        assert exc_info.value.attempts == 3


# =============================================================================
# RetryError Tests
# =============================================================================


class TestRetryError:
    """Tests for RetryError exception."""

    def test_error_message(self):
        """Test error message format."""
        last_exc = RuntimeError("last error")
        error = RetryError(
            message="Operation failed",
            attempts=3,
            last_exception=last_exc,
        )

        error_str = str(error)
        assert "Operation failed" in error_str
        assert "3 attempts" in error_str
        assert "RuntimeError" in error_str
        assert "last error" in error_str

    def test_all_exceptions_stored(self):
        """Test all exceptions are stored."""
        exceptions = [
            RuntimeError("first"),
            RuntimeError("second"),
            RuntimeError("third"),
        ]
        error = RetryError(
            message="Failed",
            attempts=3,
            last_exception=exceptions[-1],
            all_exceptions=exceptions,
        )

        assert len(error.all_exceptions) == 3
        assert error.last_exception == exceptions[-1]


# =============================================================================
# Timing Tests
# =============================================================================


class TestTimingBehavior:
    """Tests for timing and delay behavior."""

    @pytest.mark.asyncio
    async def test_delay_between_retries(self):
        """Test actual delay happens between retries."""
        func = AsyncMock(side_effect=[RuntimeError("fail"), "success"])

        start = time.monotonic()
        await retry_async(func, base_delay=0.1, max_attempts=2)
        elapsed = time.monotonic() - start

        # Should have waited at least 0.1 seconds
        assert elapsed >= 0.09  # Allow small timing variance

    @pytest.mark.asyncio
    async def test_no_delay_on_success(self):
        """Test no delay when first attempt succeeds."""
        func = AsyncMock(return_value="success")

        start = time.monotonic()
        await retry_async(func)
        elapsed = time.monotonic() - start

        # Should be nearly instant
        assert elapsed < 0.1


# =============================================================================
# Edge Cases
# =============================================================================


class TestEdgeCases:
    """Tests for edge cases."""

    @pytest.mark.asyncio
    async def test_single_attempt(self):
        """Test behavior with max_attempts=1 (no retries)."""
        func = AsyncMock(side_effect=RuntimeError("fail"))

        with pytest.raises(RetryError) as exc_info:
            await retry_async(func, max_attempts=1)

        assert exc_info.value.attempts == 1
        func.assert_called_once()

    @pytest.mark.asyncio
    async def test_zero_delay(self):
        """Test behavior with zero delay."""
        call_times = []

        async def track_time():
            call_times.append(time.monotonic())
            if len(call_times) < 3:
                raise RuntimeError("fail")
            return "success"

        await retry_async(track_time, base_delay=0, max_attempts=3)

        # All calls should happen almost instantly
        total_time = call_times[-1] - call_times[0]
        assert total_time < 0.1

    @pytest.mark.asyncio
    async def test_callback_exception_ignored(self):
        """Test callback exceptions don't break retry."""

        def bad_callback(attempt, exc, delay):
            raise ValueError("callback error")

        config = RetryConfig(
            max_attempts=2,
            base_delay=0.01,
            on_retry=bad_callback,
        )
        func = AsyncMock(side_effect=[RuntimeError("fail"), "success"])

        # Should complete despite callback error
        result = await retry_async(func, config=config)
        assert result == "success"
