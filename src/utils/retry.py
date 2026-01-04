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
Retry Utilities for Ash-Bot Service
---
FILE VERSION: v5.0-5-5.1-1
LAST MODIFIED: 2026-01-04
PHASE: Phase 5 - Production Hardening
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-bot
Community: The Alphabet Cartel - https://discord.gg/alphabetcartel | https://alphabetcartel.org
============================================================================
RESPONSIBILITIES:
- Provide configurable retry logic with exponential backoff
- Support both sync and async functions
- Allow customizable retry conditions
- Provide decorators for easy application

USAGE:
    from src.utils import retry_async, RetryConfig

    # Using retry_async function
    result = await retry_async(
        func=my_async_function,
        args=(arg1,),
        kwargs={"key": "value"},
        max_attempts=3,
        base_delay=1.0,
    )

    # Using decorator
    @with_retry(max_attempts=3, base_delay=1.0)
    async def my_function():
        ...
"""

import asyncio
import functools
import logging
import random
import time
from dataclasses import dataclass, field
from typing import Any, Callable, List, Optional, Tuple, Type, TypeVar, Union

# Module version
__version__ = "v5.0-5-5.1-1"

# Initialize logger
logger = logging.getLogger(__name__)

# Type variable for generic return types
T = TypeVar("T")


# =============================================================================
# Configuration
# =============================================================================


@dataclass
class RetryConfig:
    """
    Configuration for retry behavior.

    Attributes:
        max_attempts: Maximum number of attempts (including initial)
        base_delay: Initial delay between retries in seconds
        max_delay: Maximum delay cap in seconds
        exponential_base: Base for exponential backoff (e.g., 2 for doubling)
        jitter: Whether to add random jitter to delays
        jitter_factor: Maximum jitter as fraction of delay (0.0 to 1.0)
        retryable_exceptions: Exception types that should trigger retry
        non_retryable_exceptions: Exception types that should NOT retry
        on_retry: Callback function called before each retry
    """

    max_attempts: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0
    jitter: bool = True
    jitter_factor: float = 0.1
    retryable_exceptions: Tuple[Type[Exception], ...] = field(
        default_factory=lambda: (Exception,)
    )
    non_retryable_exceptions: Tuple[Type[Exception], ...] = field(
        default_factory=tuple
    )
    on_retry: Optional[Callable[[int, Exception, float], None]] = None

    def __post_init__(self):
        """Validate configuration values."""
        if self.max_attempts < 1:
            raise ValueError("max_attempts must be at least 1")
        if self.base_delay < 0:
            raise ValueError("base_delay must be non-negative")
        if self.max_delay < self.base_delay:
            raise ValueError("max_delay must be >= base_delay")
        if self.exponential_base < 1:
            raise ValueError("exponential_base must be at least 1")
        if not 0 <= self.jitter_factor <= 1:
            raise ValueError("jitter_factor must be between 0 and 1")


# =============================================================================
# Exceptions
# =============================================================================


class RetryError(Exception):
    """
    Raised when all retry attempts have been exhausted.

    Attributes:
        attempts: Number of attempts made
        last_exception: The last exception that occurred
        all_exceptions: List of all exceptions from each attempt
    """

    def __init__(
        self,
        message: str,
        attempts: int,
        last_exception: Exception,
        all_exceptions: Optional[List[Exception]] = None,
    ):
        super().__init__(message)
        self.attempts = attempts
        self.last_exception = last_exception
        self.all_exceptions = all_exceptions or [last_exception]

    def __str__(self) -> str:
        return (
            f"{self.args[0]} after {self.attempts} attempts. "
            f"Last error: {type(self.last_exception).__name__}: {self.last_exception}"
        )


# =============================================================================
# Retry Functions
# =============================================================================


def calculate_delay(
    attempt: int,
    config: RetryConfig,
) -> float:
    """
    Calculate delay before next retry attempt.

    Uses exponential backoff with optional jitter.

    Args:
        attempt: Current attempt number (0-indexed)
        config: Retry configuration

    Returns:
        Delay in seconds
    """
    # Calculate exponential delay
    delay = config.base_delay * (config.exponential_base ** attempt)

    # Cap at max delay
    delay = min(delay, config.max_delay)

    # Add jitter if enabled
    if config.jitter:
        jitter_range = delay * config.jitter_factor
        delay = delay + random.uniform(-jitter_range, jitter_range)

    # Ensure non-negative
    return max(0, delay)


def should_retry(
    exception: Exception,
    config: RetryConfig,
) -> bool:
    """
    Determine if an exception should trigger a retry.

    Args:
        exception: The exception that occurred
        config: Retry configuration

    Returns:
        True if should retry, False otherwise
    """
    # Check non-retryable first (takes precedence)
    if isinstance(exception, config.non_retryable_exceptions):
        return False

    # Check if it's a retryable exception
    return isinstance(exception, config.retryable_exceptions)


async def retry_async(
    func: Callable[..., Any],
    args: Optional[Tuple[Any, ...]] = None,
    kwargs: Optional[dict] = None,
    config: Optional[RetryConfig] = None,
    max_attempts: Optional[int] = None,
    base_delay: Optional[float] = None,
    max_delay: Optional[float] = None,
    retryable_exceptions: Optional[Tuple[Type[Exception], ...]] = None,
) -> T:
    """
    Execute an async function with retry logic.

    Implements exponential backoff with configurable parameters.
    Supports both explicit config and individual parameter overrides.

    Args:
        func: Async function to execute
        args: Positional arguments for function
        kwargs: Keyword arguments for function
        config: Full retry configuration (optional)
        max_attempts: Override max_attempts in config
        base_delay: Override base_delay in config
        max_delay: Override max_delay in config
        retryable_exceptions: Override retryable exceptions

    Returns:
        Result from function

    Raises:
        RetryError: If all attempts fail
        Exception: If a non-retryable exception occurs

    Example:
        >>> result = await retry_async(
        ...     fetch_data,
        ...     args=(url,),
        ...     max_attempts=3,
        ...     base_delay=1.0,
        ... )
    """
    args = args or ()
    kwargs = kwargs or {}

    # Build configuration
    if config is None:
        config = RetryConfig()

    # Apply overrides
    if max_attempts is not None:
        config = RetryConfig(
            max_attempts=max_attempts,
            base_delay=config.base_delay,
            max_delay=config.max_delay,
            exponential_base=config.exponential_base,
            jitter=config.jitter,
            jitter_factor=config.jitter_factor,
            retryable_exceptions=config.retryable_exceptions,
            non_retryable_exceptions=config.non_retryable_exceptions,
            on_retry=config.on_retry,
        )
    if base_delay is not None:
        config = RetryConfig(
            max_attempts=config.max_attempts,
            base_delay=base_delay,
            max_delay=config.max_delay,
            exponential_base=config.exponential_base,
            jitter=config.jitter,
            jitter_factor=config.jitter_factor,
            retryable_exceptions=config.retryable_exceptions,
            non_retryable_exceptions=config.non_retryable_exceptions,
            on_retry=config.on_retry,
        )
    if max_delay is not None:
        config = RetryConfig(
            max_attempts=config.max_attempts,
            base_delay=config.base_delay,
            max_delay=max_delay,
            exponential_base=config.exponential_base,
            jitter=config.jitter,
            jitter_factor=config.jitter_factor,
            retryable_exceptions=config.retryable_exceptions,
            non_retryable_exceptions=config.non_retryable_exceptions,
            on_retry=config.on_retry,
        )
    if retryable_exceptions is not None:
        config = RetryConfig(
            max_attempts=config.max_attempts,
            base_delay=config.base_delay,
            max_delay=config.max_delay,
            exponential_base=config.exponential_base,
            jitter=config.jitter,
            jitter_factor=config.jitter_factor,
            retryable_exceptions=retryable_exceptions,
            non_retryable_exceptions=config.non_retryable_exceptions,
            on_retry=config.on_retry,
        )

    all_exceptions: List[Exception] = []
    func_name = getattr(func, "__name__", str(func))

    for attempt in range(config.max_attempts):
        try:
            # Execute the function
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)

            # Success - log if there were previous failures
            if attempt > 0:
                logger.info(
                    f"✅ {func_name} succeeded on attempt {attempt + 1}"
                )

            return result

        except Exception as e:
            all_exceptions.append(e)

            # Check if we should retry
            if not should_retry(e, config):
                logger.warning(
                    f"⚠️ {func_name} failed with non-retryable exception: "
                    f"{type(e).__name__}: {e}"
                )
                raise

            # Check if we have more attempts
            if attempt + 1 >= config.max_attempts:
                logger.error(
                    f"❌ {func_name} failed after {config.max_attempts} attempts: "
                    f"{type(e).__name__}: {e}"
                )
                raise RetryError(
                    message=f"All {config.max_attempts} attempts failed for {func_name}",
                    attempts=config.max_attempts,
                    last_exception=e,
                    all_exceptions=all_exceptions,
                )

            # Calculate delay
            delay = calculate_delay(attempt, config)

            # Log retry
            logger.warning(
                f"⚠️ {func_name} attempt {attempt + 1}/{config.max_attempts} failed: "
                f"{type(e).__name__}: {e} | Retrying in {delay:.2f}s"
            )

            # Call retry callback if provided
            if config.on_retry:
                try:
                    config.on_retry(attempt + 1, e, delay)
                except Exception as callback_error:
                    logger.warning(f"Retry callback failed: {callback_error}")

            # Wait before retry
            await asyncio.sleep(delay)

    # This should never be reached, but just in case
    raise RetryError(
        message=f"Unexpected retry loop exit for {func_name}",
        attempts=len(all_exceptions),
        last_exception=all_exceptions[-1] if all_exceptions else Exception("Unknown"),
        all_exceptions=all_exceptions,
    )


# =============================================================================
# Decorators
# =============================================================================


def with_retry(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    retryable_exceptions: Tuple[Type[Exception], ...] = (Exception,),
    non_retryable_exceptions: Tuple[Type[Exception], ...] = (),
) -> Callable:
    """
    Decorator for adding retry logic to async functions.

    Args:
        max_attempts: Maximum number of attempts
        base_delay: Initial delay between retries
        max_delay: Maximum delay cap
        exponential_base: Base for exponential backoff
        jitter: Whether to add random jitter
        retryable_exceptions: Exceptions that trigger retry
        non_retryable_exceptions: Exceptions that don't retry

    Returns:
        Decorator function

    Example:
        >>> @with_retry(max_attempts=3, base_delay=1.0)
        ... async def fetch_data(url: str) -> dict:
        ...     async with httpx.AsyncClient() as client:
        ...         response = await client.get(url)
        ...         return response.json()
    """
    config = RetryConfig(
        max_attempts=max_attempts,
        base_delay=base_delay,
        max_delay=max_delay,
        exponential_base=exponential_base,
        jitter=jitter,
        retryable_exceptions=retryable_exceptions,
        non_retryable_exceptions=non_retryable_exceptions,
    )

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            return await retry_async(
                func=func,
                args=args,
                kwargs=kwargs,
                config=config,
            )

        return wrapper

    return decorator


# =============================================================================
# Synchronous Retry (for completeness)
# =============================================================================


def retry_sync(
    func: Callable[..., Any],
    args: Optional[Tuple[Any, ...]] = None,
    kwargs: Optional[dict] = None,
    config: Optional[RetryConfig] = None,
) -> T:
    """
    Execute a synchronous function with retry logic.

    Similar to retry_async but for synchronous functions.

    Args:
        func: Function to execute
        args: Positional arguments
        kwargs: Keyword arguments
        config: Retry configuration

    Returns:
        Result from function

    Raises:
        RetryError: If all attempts fail
    """
    args = args or ()
    kwargs = kwargs or {}
    config = config or RetryConfig()

    all_exceptions: List[Exception] = []
    func_name = getattr(func, "__name__", str(func))

    for attempt in range(config.max_attempts):
        try:
            result = func(*args, **kwargs)

            if attempt > 0:
                logger.info(f"✅ {func_name} succeeded on attempt {attempt + 1}")

            return result

        except Exception as e:
            all_exceptions.append(e)

            if not should_retry(e, config):
                raise

            if attempt + 1 >= config.max_attempts:
                raise RetryError(
                    message=f"All {config.max_attempts} attempts failed for {func_name}",
                    attempts=config.max_attempts,
                    last_exception=e,
                    all_exceptions=all_exceptions,
                )

            delay = calculate_delay(attempt, config)
            logger.warning(
                f"⚠️ {func_name} attempt {attempt + 1}/{config.max_attempts} failed: "
                f"{type(e).__name__}: {e} | Retrying in {delay:.2f}s"
            )

            time.sleep(delay)

    raise RetryError(
        message=f"Unexpected retry loop exit for {func_name}",
        attempts=len(all_exceptions),
        last_exception=all_exceptions[-1] if all_exceptions else Exception("Unknown"),
        all_exceptions=all_exceptions,
    )


# =============================================================================
# Export public interface
# =============================================================================

__all__ = [
    "RetryConfig",
    "RetryError",
    "retry_async",
    "retry_sync",
    "with_retry",
    "calculate_delay",
    "should_retry",
]
