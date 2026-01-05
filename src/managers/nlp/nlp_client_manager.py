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
FILE VERSION: v5.0-5-5.5-2
LAST MODIFIED: 2026-01-04
PHASE: Phase 5 - Production Hardening
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
- Circuit breaker integration (Phase 5)
- Metrics collection (Phase 5)

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
from src.utils.circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerConfig,
    CircuitOpenError,
)

if TYPE_CHECKING:
    from src.managers.config_manager import ConfigManager
    from src.managers.metrics.metrics_manager import MetricsManager

# Module version
__version__ = "v5.0-5-5.5-2"

# Initialize logger
logger = logging.getLogger(__name__)


# =============================================================================
# Exceptions
# =============================================================================


class NLPClientError(Exception):
    """Raised when NLP API communication fails."""

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


class NLPCircuitOpenError(NLPClientError):
    """Raised when circuit breaker is open."""
    pass


# =============================================================================
# NLP Client Manager
# =============================================================================


class NLPClientManager:
    """
    Async HTTP client for Ash-NLP API with circuit breaker protection.

    Handles all communication with the Ash-NLP crisis detection API
    including retries, timeouts, circuit breaker protection, and
    response parsing.
    """

    DEFAULT_BASE_URL = "http://10.20.30.253:30880"
    DEFAULT_TIMEOUT = 5.0
    DEFAULT_RETRY_ATTEMPTS = 2
    DEFAULT_RETRY_DELAY = 1.0
    DEFAULT_CB_FAILURE_THRESHOLD = 5
    DEFAULT_CB_SUCCESS_THRESHOLD = 2
    DEFAULT_CB_TIMEOUT = 30.0

    def __init__(
        self,
        config_manager: "ConfigManager",
        metrics_manager: Optional["MetricsManager"] = None,
    ):
        """Initialize NLPClientManager with circuit breaker."""
        self.config_manager = config_manager
        self._metrics = metrics_manager

        # Load configuration
        nlp_config = config_manager.get_section("nlp")
        self.base_url = nlp_config.get("base_url", self.DEFAULT_BASE_URL)
        self.timeout = float(nlp_config.get("timeout_seconds", self.DEFAULT_TIMEOUT))
        self.retry_attempts = int(nlp_config.get("retry_attempts", self.DEFAULT_RETRY_ATTEMPTS))
        self.retry_delay = float(nlp_config.get("retry_delay_seconds", self.DEFAULT_RETRY_DELAY))

        # Circuit breaker config
        cb_config = config_manager.get_section("circuit_breaker")
        cb_failure_threshold = int(cb_config.get("nlp_failure_threshold", self.DEFAULT_CB_FAILURE_THRESHOLD))
        cb_success_threshold = int(cb_config.get("nlp_success_threshold", self.DEFAULT_CB_SUCCESS_THRESHOLD))
        cb_timeout = float(cb_config.get("nlp_timeout_seconds", self.DEFAULT_CB_TIMEOUT))

        # Initialize circuit breaker
        self._circuit_breaker = CircuitBreaker(
            name="nlp_api",
            config=CircuitBreakerConfig(
                failure_threshold=cb_failure_threshold,
                success_threshold=cb_success_threshold,
                timeout_seconds=cb_timeout,
            ),
        )

        self._client: Optional[httpx.AsyncClient] = None
        self._closed = False
        self._consecutive_failures = 0

        logger.info(
            f"✅ NLPClientManager initialized (url={self.base_url}, "
            f"cb_failures={cb_failure_threshold})"
        )

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._closed:
            raise NLPClientError("NLP client has been closed")

        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=httpx.Timeout(self.timeout),
                headers={"Content-Type": "application/json", "Accept": "application/json"},
            )
        return self._client

    async def close(self) -> None:
        """Close the HTTP client connection pool."""
        if self._closed:
            return
        if self._client is not None:
            await self._client.aclose()
            self._client = None
        self._closed = True
        logger.debug("HTTP client closed")

    async def __aenter__(self) -> "NLPClientManager":
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.close()

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
        """Analyze a message for crisis signals with circuit breaker protection."""
        start_time = time.monotonic()

        # Check circuit breaker
        if not self._circuit_breaker.is_closed:
            if self._circuit_breaker.state.value == "open":
                if self._metrics:
                    self._metrics.inc_nlp_errors()
                logger.warning("⚡ Circuit breaker OPEN - returning error result")
                return CrisisAnalysisResult.create_error_result(
                    error_message="NLP API circuit breaker is open",
                    request_id="circuit_open",
                )

        # Build request
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
            request_body["message_history"] = [item.to_dict() for item in message_history]
        if user_timezone:
            request_body["user_timezone"] = user_timezone

        try:
            response_data = await self._circuit_breaker.call(
                self._make_request_with_retry,
                method="POST",
                endpoint="/analyze",
                json_data=request_body,
            )
            self._consecutive_failures = 0
            result = CrisisAnalysisResult.from_api_response(response_data)
            elapsed_ms = (time.monotonic() - start_time) * 1000

            if self._metrics:
                self._metrics.observe_nlp_duration(elapsed_ms / 1000.0)
                self._metrics.inc_messages_analyzed(result.severity)

            logger.info(f"📊 Analysis complete: {result.to_log_dict()} ({elapsed_ms:.1f}ms)")
            return result

        except CircuitOpenError:
            self._consecutive_failures += 1
            if self._metrics:
                self._metrics.inc_nlp_errors()
            logger.warning(f"⚡ Circuit breaker blocked call (failures={self._consecutive_failures})")
            return CrisisAnalysisResult.create_error_result(
                error_message="NLP API circuit breaker prevented call",
                request_id="circuit_blocked",
            )

        except NLPClientError as e:
            self._consecutive_failures += 1
            if self._metrics:
                self._metrics.inc_nlp_errors()
            elapsed_ms = (time.monotonic() - start_time) * 1000
            logger.error(f"❌ Analysis failed after {elapsed_ms:.1f}ms: {e}")
            return CrisisAnalysisResult.create_error_result(
                error_message=str(e),
                request_id=getattr(e, "request_id", "error"),
            )

    async def check_health(self) -> bool:
        """Check if Ash-NLP API is healthy (bypasses circuit breaker)."""
        try:
            client = await self._get_client()
            response = await client.get("/health", timeout=httpx.Timeout(2.0))

            if response.status_code == 200:
                data = response.json()
                is_healthy = data.get("ready", False)
                if is_healthy:
                    logger.debug("✅ Ash-NLP API is healthy")
                return is_healthy
            return False

        except Exception as e:
            logger.warning(f"⚠️ Ash-NLP health check failed: {e}")
            return False

    async def get_status(self) -> Optional[Dict[str, Any]]:
        """Get detailed status from Ash-NLP API."""
        try:
            client = await self._get_client()
            response = await client.get("/status", timeout=httpx.Timeout(5.0))
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.warning(f"Failed to get NLP status: {e}")
            return None

    async def _make_request_with_retry(
        self,
        method: str,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make HTTP request with exponential backoff retry."""
        client = await self._get_client()
        last_error: Optional[Exception] = None

        for attempt in range(self.retry_attempts + 1):
            try:
                if method.upper() == "POST":
                    response = await client.post(endpoint, json=json_data)
                else:
                    response = await client.get(endpoint)

                if response.status_code >= 400:
                    error_detail = self._extract_error_detail(response)
                    if 400 <= response.status_code < 500:
                        raise NLPValidationError(
                            message=f"Validation error: {error_detail}",
                            status_code=response.status_code,
                        )
                    raise NLPClientError(
                        message=f"Server error: {error_detail}",
                        status_code=response.status_code,
                    )
                return response.json()

            except httpx.TimeoutException as e:
                last_error = NLPTimeoutError(f"Request timed out: {e}")
                logger.warning(f"⚠️ NLP timeout (attempt {attempt + 1}/{self.retry_attempts + 1})")
            except httpx.ConnectError as e:
                last_error = NLPConnectionError(f"Connection failed: {e}")
                logger.warning(f"⚠️ NLP connection error (attempt {attempt + 1}): {e}")
            except NLPValidationError:
                raise
            except NLPClientError as e:
                last_error = e
                logger.warning(f"⚠️ NLP error (attempt {attempt + 1}): {e}")
            except Exception as e:
                last_error = NLPClientError(f"Unexpected error: {e}")
                logger.error(f"❌ Unexpected NLP error (attempt {attempt + 1}): {e}")

            if attempt < self.retry_attempts:
                delay = self.retry_delay * (2**attempt)
                await asyncio.sleep(delay)

        raise last_error or NLPClientError("Unknown error after retries")

    def _extract_error_detail(self, response: httpx.Response) -> str:
        """Extract error detail from response."""
        try:
            data = response.json()
            return data.get("message", data.get("detail", str(data)))
        except Exception:
            return response.text[:200] if response.text else f"HTTP {response.status_code}"

    async def health_check(self) -> bool:
        """
        Check if NLP API is healthy and responsive.

        Returns:
            True if API is healthy and ready, False otherwise.
        """
        try:
            client = await self._get_client()
            response = await client.get("/health")
            
            if response.status_code != 200:
                logger.warning(f"NLP health check returned status {response.status_code}")
                return False
            
            data = response.json()
            is_ready = data.get("ready", False)
            
            if not is_ready:
                logger.warning("NLP API is not ready")
                return False
            
            return True
            
        except httpx.TimeoutException:
            logger.warning("NLP health check timed out")
            return False
        except httpx.ConnectError as e:
            logger.warning(f"NLP health check connection error: {e}")
            return False
        except Exception as e:
            logger.warning(f"NLP health check failed: {e}")
            return False

    @property
    def circuit_state(self) -> str:
        return self._circuit_breaker.state.value

    @property
    def circuit_is_closed(self) -> bool:
        return self._circuit_breaker.is_closed

    def reset_circuit_breaker(self) -> None:
        """Manually reset circuit breaker."""
        self._circuit_breaker.reset()
        self._consecutive_failures = 0
        logger.info("🔄 Circuit breaker manually reset")

    @property
    def is_closed(self) -> bool:
        return self._closed

    @property
    def consecutive_failures(self) -> int:
        return self._consecutive_failures

    def get_stats(self) -> Dict[str, Any]:
        return {
            "base_url": self.base_url,
            "circuit_state": self.circuit_state,
            "consecutive_failures": self._consecutive_failures,
        }

    def __repr__(self) -> str:
        return f"NLPClientManager(url='{self.base_url}', circuit={self.circuit_state})"


def create_nlp_client_manager(
    config_manager: "ConfigManager",
    metrics_manager: Optional["MetricsManager"] = None,
) -> NLPClientManager:
    """Factory function for NLPClientManager."""
    logger.info("🏭 Creating NLPClientManager")
    return NLPClientManager(
        config_manager=config_manager,
        metrics_manager=metrics_manager,
    )


__all__ = [
    "NLPClientManager",
    "NLPClientError",
    "NLPConnectionError",
    "NLPTimeoutError",
    "NLPValidationError",
    "NLPCircuitOpenError",
    "create_nlp_client_manager",
]
