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
NLP Client Manager for Ash-Bot Service
---
FILE VERSION: v5.0-1-1.3-1
LAST MODIFIED: 2026-01-03
PHASE: Phase 1 - Discord Connectivity
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-bot
Community: The Alphabet Cartel - https://discord.gg/alphabetcartel | https://alphabetcartel.org
============================================================================
RESPONSIBILITIES:
- Async HTTP communication with Ash-NLP API
- Message analysis with retry logic
- Connection pooling and timeout management
- Health check functionality
- Response parsing and validation

USAGE:
    from src.managers.nlp import create_nlp_client_manager

    nlp_client = create_nlp_client_manager(config_manager)

    async with nlp_client:
        result = await nlp_client.analyze_message("I'm feeling down")
        if result.is_actionable:
            # Handle crisis
            pass
"""

import asyncio
import logging
import time
from typing import Any, Dict, List, Optional, TYPE_CHECKING

import httpx

from src.models.nlp_models import (
    CrisisAnalysisResult,
    MessageHistoryItem,
)

if TYPE_CHECKING:
    from src.managers.config_manager import ConfigManager

# Module version
__version__ = "v5.0-1-1.3-1"

# Initialize logger
logger = logging.getLogger(__name__)


# =============================================================================
# Exceptions
# =============================================================================


class NLPClientError(Exception):
    """
    Raised when NLP API communication fails.

    Attributes:
        message: Error description
        status_code: HTTP status code if available
        request_id: Request ID if available
    """

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        request_id: Optional[str] = None,
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.request_id = request_id

    def __str__(self) -> str:
        parts = [self.message]
        if self.status_code:
            parts.append(f"status={self.status_code}")
        if self.request_id:
            parts.append(f"request_id={self.request_id}")
        return " | ".join(parts)


class NLPConnectionError(NLPClientError):
    """Raised when connection to NLP API fails."""

    pass


class NLPTimeoutError(NLPClientError):
    """Raised when NLP API request times out."""

    pass


class NLPValidationError(NLPClientError):
    """Raised when NLP API returns validation error (4xx)."""

    pass


# =============================================================================
# NLP Client Manager
# =============================================================================


class NLPClientManager:
    """
    Async HTTP client for Ash-NLP API.

    Handles all communication with the Ash-NLP crisis detection API
    including retries, timeouts, and response parsing.

    Attributes:
        config_manager: Configuration manager instance
        base_url: Ash-NLP API base URL
        timeout: Request timeout in seconds
        retry_attempts: Number of retry attempts
        retry_delay: Initial delay between retries in seconds
        _client: httpx.AsyncClient instance
        _closed: Whether client has been closed

    Example:
        >>> nlp = create_nlp_client_manager(config_manager)
        >>> async with nlp:
        ...     result = await nlp.analyze_message("message text")
        ...     print(result.severity)
    """

    # Default configuration values (used if config fails)
    DEFAULT_BASE_URL = "http://ash-nlp:30880"
    DEFAULT_TIMEOUT = 5.0
    DEFAULT_RETRY_ATTEMPTS = 2
    DEFAULT_RETRY_DELAY = 1.0

    def __init__(self, config_manager: "ConfigManager"):
        """
        Initialize NLPClientManager.

        Args:
            config_manager: Configuration manager instance

        Note:
            Use create_nlp_client_manager() factory function.
        """
        self.config_manager = config_manager

        # Load configuration with safe defaults
        nlp_config = config_manager.get_section("nlp")

        self.base_url = nlp_config.get("base_url", self.DEFAULT_BASE_URL)
        self.timeout = float(nlp_config.get("timeout_seconds", self.DEFAULT_TIMEOUT))
        self.retry_attempts = int(
            nlp_config.get("retry_attempts", self.DEFAULT_RETRY_ATTEMPTS)
        )
        self.retry_delay = float(
            nlp_config.get("retry_delay_seconds", self.DEFAULT_RETRY_DELAY)
        )

        # Initialize HTTP client (lazy - created on first use)
        self._client: Optional[httpx.AsyncClient] = None
        self._closed = False

        logger.info(
            f"✅ NLPClientManager initialized "
            f"(url={self.base_url}, timeout={self.timeout}s, retries={self.retry_attempts})"
        )

    # =========================================================================
    # HTTP Client Management
    # =========================================================================

    async def _get_client(self) -> httpx.AsyncClient:
        """
        Get or create HTTP client.

        Uses lazy initialization for async compatibility.

        Returns:
            httpx.AsyncClient instance

        Raises:
            NLPClientError: If client is closed
        """
        if self._closed:
            raise NLPClientError("NLP client has been closed")

        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=httpx.Timeout(self.timeout),
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
            )
            logger.debug("HTTP client created")

        return self._client

    async def close(self) -> None:
        """
        Close the HTTP client connection pool.

        Should be called when done using the client.
        """
        if self._client is not None and not self._closed:
            await self._client.aclose()
            self._client = None
            self._closed = True
            logger.debug("HTTP client closed")

    async def __aenter__(self) -> "NLPClientManager":
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.close()

    # =========================================================================
    # API Methods
    # =========================================================================

    async def analyze_message(
        self,
        message: str,
        user_id: Optional[str] = None,
        channel_id: Optional[str] = None,
        message_history: Optional[List[MessageHistoryItem]] = None,
        user_timezone: Optional[str] = None,
        include_explanation: bool = True,
        verbosity: str = "standard",
    ) -> CrisisAnalysisResult:
        """
        Analyze a message for crisis signals.

        Sends the message to Ash-NLP API and returns the crisis analysis.
        Implements retry logic with exponential backoff.

        Args:
            message: Message content to analyze
            user_id: Discord user ID (optional, for tracking)
            channel_id: Discord channel ID (optional, for context)
            message_history: Previous messages for context (optional)
            user_timezone: User's timezone in IANA format (optional)
            include_explanation: Include human-readable explanation
            verbosity: Explanation detail level (minimal, standard, detailed)

        Returns:
            CrisisAnalysisResult with complete analysis

        Raises:
            NLPClientError: If API call fails after all retries
        """
        start_time = time.monotonic()

        # Build request body
        request_body: Dict[str, Any] = {
            "message": message,
            "include_explanation": include_explanation,
            "verbosity": verbosity,
        }

        if user_id:
            request_body["user_id"] = str(user_id)

        if channel_id:
            request_body["channel_id"] = str(channel_id)

        if message_history:
            request_body["message_history"] = [
                item.to_dict() for item in message_history
            ]

        if user_timezone:
            request_body["user_timezone"] = user_timezone

        # Make request with retry
        try:
            response_data = await self._make_request_with_retry(
                method="POST",
                endpoint="/analyze",
                json_data=request_body,
            )

            # Parse response
            result = CrisisAnalysisResult.from_api_response(response_data)

            elapsed_ms = (time.monotonic() - start_time) * 1000
            logger.info(
                f"📊 Analysis complete: {result.to_log_dict()} "
                f"(total_time={elapsed_ms:.1f}ms)"
            )

            return result

        except NLPClientError as e:
            elapsed_ms = (time.monotonic() - start_time) * 1000
            logger.error(f"❌ Analysis failed after {elapsed_ms:.1f}ms: {e}")
            # Return safe error result instead of crashing
            return CrisisAnalysisResult.create_error_result(
                error_message=str(e),
                request_id=getattr(e, "request_id", "error"),
            )

    async def health_check(self) -> bool:
        """
        Check if Ash-NLP API is healthy and ready.

        Returns:
            True if API is healthy, False otherwise
        """
        try:
            client = await self._get_client()
            response = await client.get(
                "/health",
                timeout=httpx.Timeout(2.0),  # Short timeout for health check
            )

            if response.status_code == 200:
                data = response.json()
                is_healthy = data.get("ready", False)
                is_degraded = data.get("degraded", False)

                if is_healthy:
                    if is_degraded:
                        logger.warning("⚠️ Ash-NLP API is healthy but degraded")
                    else:
                        logger.debug("✅ Ash-NLP API is healthy")
                    return True
                else:
                    logger.warning("⚠️ Ash-NLP API is not ready")
                    return False
            else:
                logger.warning(
                    f"⚠️ Ash-NLP health check returned {response.status_code}"
                )
                return False

        except httpx.TimeoutException:
            logger.warning("⚠️ Ash-NLP health check timed out")
            return False
        except httpx.ConnectError:
            logger.warning("⚠️ Cannot connect to Ash-NLP API")
            return False
        except Exception as e:
            logger.warning(f"⚠️ Ash-NLP health check failed: {e}")
            return False

    async def get_status(self) -> Optional[Dict[str, Any]]:
        """
        Get detailed status from Ash-NLP API.

        Returns:
            Status dictionary or None if unavailable
        """
        try:
            client = await self._get_client()
            response = await client.get(
                "/status",
                timeout=httpx.Timeout(5.0),
            )

            if response.status_code == 200:
                return response.json()
            return None

        except Exception as e:
            logger.warning(f"Failed to get NLP status: {e}")
            return None

    # =========================================================================
    # Internal Methods
    # =========================================================================

    async def _make_request_with_retry(
        self,
        method: str,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Make HTTP request with exponential backoff retry.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            json_data: JSON request body (optional)

        Returns:
            Response JSON as dictionary

        Raises:
            NLPClientError: On all errors after retries exhausted
            NLPValidationError: On 4xx errors (no retry)
        """
        client = await self._get_client()
        last_error: Optional[Exception] = None

        for attempt in range(self.retry_attempts + 1):
            try:
                if method.upper() == "POST":
                    response = await client.post(endpoint, json=json_data)
                elif method.upper() == "GET":
                    response = await client.get(endpoint)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")

                # Check for errors
                if response.status_code >= 400:
                    error_detail = self._extract_error_detail(response)

                    # Don't retry client errors (4xx)
                    if 400 <= response.status_code < 500:
                        raise NLPValidationError(
                            message=f"Validation error: {error_detail}",
                            status_code=response.status_code,
                        )

                    # Server errors (5xx) - retry
                    raise NLPClientError(
                        message=f"Server error: {error_detail}",
                        status_code=response.status_code,
                    )

                # Success
                return response.json()

            except httpx.TimeoutException as e:
                last_error = NLPTimeoutError(f"Request timed out: {e}")
                logger.warning(
                    f"⚠️ NLP request timeout (attempt {attempt + 1}/{self.retry_attempts + 1})"
                )

            except httpx.ConnectError as e:
                last_error = NLPConnectionError(f"Connection failed: {e}")
                logger.warning(
                    f"⚠️ NLP connection error (attempt {attempt + 1}/{self.retry_attempts + 1}): {e}"
                )

            except NLPValidationError:
                # Don't retry validation errors
                raise

            except NLPClientError as e:
                last_error = e
                logger.warning(
                    f"⚠️ NLP request error (attempt {attempt + 1}/{self.retry_attempts + 1}): {e}"
                )

            except Exception as e:
                last_error = NLPClientError(f"Unexpected error: {e}")
                logger.error(
                    f"❌ Unexpected NLP error (attempt {attempt + 1}/{self.retry_attempts + 1}): {e}"
                )

            # Wait before retry (exponential backoff)
            if attempt < self.retry_attempts:
                delay = self.retry_delay * (2**attempt)
                logger.debug(f"Waiting {delay}s before retry...")
                await asyncio.sleep(delay)

        # All retries exhausted
        raise last_error or NLPClientError("Unknown error after retries")

    def _extract_error_detail(self, response: httpx.Response) -> str:
        """
        Extract error detail from response.

        Args:
            response: HTTP response object

        Returns:
            Error detail string
        """
        try:
            data = response.json()
            return data.get("message", data.get("detail", str(data)))
        except Exception:
            return (
                response.text[:200] if response.text else f"HTTP {response.status_code}"
            )

    # =========================================================================
    # Properties
    # =========================================================================

    @property
    def is_closed(self) -> bool:
        """Check if client has been closed."""
        return self._closed

    def __repr__(self) -> str:
        """String representation for debugging."""
        return (
            f"NLPClientManager("
            f"base_url='{self.base_url}', "
            f"timeout={self.timeout}s, "
            f"retries={self.retry_attempts})"
        )


# =============================================================================
# Factory Function
# =============================================================================


def create_nlp_client_manager(
    config_manager: "ConfigManager",
) -> NLPClientManager:
    """
    Factory function for NLPClientManager.

    Creates a configured NLPClientManager instance.
    Following Clean Architecture v5.1 Rule #1: Factory Functions.

    Args:
        config_manager: Configuration manager instance

    Returns:
        Configured NLPClientManager instance

    Example:
        >>> nlp_client = create_nlp_client_manager(config_manager)
        >>> async with nlp_client:
        ...     result = await nlp_client.analyze_message("text")
    """
    logger.info("🏭 Creating NLPClientManager")
    return NLPClientManager(config_manager=config_manager)


# =============================================================================
# Export public interface
# =============================================================================

__all__ = [
    "NLPClientManager",
    "NLPClientError",
    "NLPConnectionError",
    "NLPTimeoutError",
    "NLPValidationError",
    "create_nlp_client_manager",
]
