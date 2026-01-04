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
Claude Client Manager for Ash-Bot Service
---
FILE VERSION: v5.0-4-3.0-1
LAST MODIFIED: 2026-01-04
PHASE: Phase 4 - Ash AI Integration
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-bot
Community: The Alphabet Cartel - https://discord.gg/alphabetcartel | https://alphabetcartel.org
============================================================================
RESPONSIBILITIES:
- Initialize Anthropic client with API key from secrets
- Send messages to Claude API
- Handle streaming responses (optional)
- Implement error handling and retries
- Token counting and limiting

USAGE:
    from src.managers.ash import create_claude_client_manager

    claude_client = create_claude_client_manager(
        config_manager=config_manager,
        secrets_manager=secrets_manager,
    )

    response = await claude_client.create_message(
        system_prompt="You are Ash...",
        messages=[{"role": "user", "content": "Hello"}],
    )
"""

import asyncio
import logging
from typing import Any, AsyncGenerator, Dict, List, Optional, TYPE_CHECKING

import anthropic

if TYPE_CHECKING:
    from src.managers.config_manager import ConfigManager
    from src.managers.secrets_manager import SecretsManager

# Module version
__version__ = "v5.0-4-3.0-1"

# Initialize logger
logger = logging.getLogger(__name__)


# =============================================================================
# Exceptions
# =============================================================================


class ClaudeAPIError(Exception):
    """Raised when Claude API calls fail."""

    def __init__(self, message: str, original_error: Optional[Exception] = None):
        """
        Initialize ClaudeAPIError.

        Args:
            message: Error message
            original_error: Original exception that caused this error
        """
        super().__init__(message)
        self.original_error = original_error


class ClaudeConfigError(Exception):
    """Raised when Claude client configuration is invalid."""

    pass


# =============================================================================
# Claude Client Manager
# =============================================================================


class ClaudeClientManager:
    """
    Manages Claude API interactions for Ash responses.

    Handles all communication with the Anthropic Claude API,
    including message creation, streaming, and error handling.

    Attributes:
        config_manager: ConfigManager for settings
        secrets_manager: SecretsManager for API key
        model: Model identifier (e.g., claude-sonnet-4-20250514)
        max_tokens: Maximum response tokens

    Example:
        >>> claude = create_claude_client_manager(config, secrets)
        >>> response = await claude.create_message(
        ...     system_prompt="You are helpful.",
        ...     messages=[{"role": "user", "content": "Hi"}],
        ... )
    """

    # Default fallback response when API fails
    FALLBACK_RESPONSE = (
        "I'm here with you, though I'm having a bit of trouble right now. "
        "Would you like me to connect you with our Crisis Response Team?"
    )

    def __init__(
        self,
        config_manager: "ConfigManager",
        secrets_manager: "SecretsManager",
    ):
        """
        Initialize ClaudeClientManager.

        Args:
            config_manager: Configuration manager for settings
            secrets_manager: Secrets manager for API key

        Raises:
            ClaudeConfigError: If API key is not found
        """
        self._config = config_manager
        self._secrets = secrets_manager
        self._logger = logging.getLogger(__name__)

        # Load configuration
        self._model = self._config.get("ash", "model", "claude-sonnet-4-20250514")
        self._max_tokens = self._config.get("ash", "max_tokens", 500)

        # Get API key
        api_key = self._secrets.get_claude_api_token()
        if not api_key:
            raise ClaudeConfigError(
                "Claude API key not found in secrets.\n"
                "Please create: secrets/claude_api_token\n"
                "See secrets/README.md for instructions"
            )

        # Initialize async client
        self._client = anthropic.AsyncAnthropic(api_key=api_key)

        # Statistics
        self._request_count = 0
        self._error_count = 0
        self._total_tokens_used = 0

        self._logger.info(
            f"🤖 ClaudeClientManager initialized "
            f"(model: {self._model}, max_tokens: {self._max_tokens})"
        )

    # =========================================================================
    # Public API
    # =========================================================================

    async def create_message(
        self,
        system_prompt: str,
        messages: List[Dict[str, str]],
        max_tokens: Optional[int] = None,
    ) -> str:
        """
        Send a message to Claude and get response.

        Args:
            system_prompt: System prompt for Ash personality
            messages: Conversation history [{"role": "user/assistant", "content": "..."}]
            max_tokens: Override default max tokens (optional)

        Returns:
            Claude's response text

        Raises:
            ClaudeAPIError: If API call fails after retries
        """
        self._request_count += 1
        tokens = max_tokens or self._max_tokens

        self._logger.debug(
            f"📤 Sending message to Claude "
            f"(messages: {len(messages)}, max_tokens: {tokens})"
        )

        try:
            response = await self._client.messages.create(
                model=self._model,
                max_tokens=tokens,
                system=system_prompt,
                messages=messages,
            )

            # Extract text from response
            if response.content and len(response.content) > 0:
                text = response.content[0].text

                # Track token usage
                if hasattr(response, "usage"):
                    self._total_tokens_used += response.usage.output_tokens

                self._logger.debug(
                    f"📥 Received response from Claude "
                    f"(length: {len(text)} chars)"
                )

                return text

            # Empty response - return fallback
            self._logger.warning("Claude returned empty response")
            return self.FALLBACK_RESPONSE

        except anthropic.RateLimitError as e:
            self._error_count += 1
            self._logger.error(f"Claude rate limit exceeded: {e}")
            raise ClaudeAPIError("Rate limit exceeded. Please try again later.", e)

        except anthropic.AuthenticationError as e:
            self._error_count += 1
            self._logger.error(f"Claude authentication failed: {e}")
            raise ClaudeAPIError("Authentication failed. Check API key.", e)

        except anthropic.BadRequestError as e:
            self._error_count += 1
            self._logger.error(f"Claude bad request: {e}")
            raise ClaudeAPIError(f"Invalid request: {e}", e)

        except anthropic.APIError as e:
            self._error_count += 1
            self._logger.error(f"Claude API error: {e}")
            raise ClaudeAPIError(f"API call failed: {e}", e)

        except Exception as e:
            self._error_count += 1
            self._logger.exception(f"Unexpected error calling Claude: {e}")
            raise ClaudeAPIError(f"Unexpected error: {e}", e)

    async def create_message_safe(
        self,
        system_prompt: str,
        messages: List[Dict[str, str]],
        max_tokens: Optional[int] = None,
    ) -> str:
        """
        Send a message to Claude with fallback on error.

        Unlike create_message(), this method never raises exceptions.
        Returns a fallback response if the API call fails.

        Args:
            system_prompt: System prompt for Ash personality
            messages: Conversation history
            max_tokens: Override default max tokens (optional)

        Returns:
            Claude's response text or fallback message
        """
        try:
            return await self.create_message(
                system_prompt=system_prompt,
                messages=messages,
                max_tokens=max_tokens,
            )
        except ClaudeAPIError as e:
            self._logger.warning(f"Claude API failed, using fallback: {e}")
            return self.FALLBACK_RESPONSE

    async def stream_message(
        self,
        system_prompt: str,
        messages: List[Dict[str, str]],
        max_tokens: Optional[int] = None,
    ) -> AsyncGenerator[str, None]:
        """
        Stream a response from Claude.

        Yields response text in chunks as they arrive.
        Useful for showing typing indicators or progressive display.

        Args:
            system_prompt: System prompt
            messages: Conversation history
            max_tokens: Override default max tokens (optional)

        Yields:
            Response text chunks

        Raises:
            ClaudeAPIError: If streaming fails
        """
        self._request_count += 1
        tokens = max_tokens or self._max_tokens

        self._logger.debug(f"📤 Starting streaming response from Claude")

        try:
            async with self._client.messages.stream(
                model=self._model,
                max_tokens=tokens,
                system=system_prompt,
                messages=messages,
            ) as stream:
                async for text in stream.text_stream:
                    yield text

            self._logger.debug("📥 Streaming response complete")

        except anthropic.APIError as e:
            self._error_count += 1
            self._logger.error(f"Claude streaming error: {e}")
            raise ClaudeAPIError(f"Streaming failed: {e}", e)

    async def health_check(self) -> bool:
        """
        Check if Claude API is accessible.

        Sends a minimal request to verify connectivity.

        Returns:
            True if API is healthy, False otherwise
        """
        try:
            # Send a minimal test message
            response = await self._client.messages.create(
                model=self._model,
                max_tokens=10,
                messages=[{"role": "user", "content": "Hi"}],
            )
            return response.content is not None
        except Exception as e:
            self._logger.warning(f"Claude health check failed: {e}")
            return False

    async def close(self) -> None:
        """
        Close the client connection.

        Should be called when shutting down the bot.
        """
        if hasattr(self._client, "close"):
            await self._client.close()
        self._logger.info("🔌 Claude client closed")

    # =========================================================================
    # Properties
    # =========================================================================

    @property
    def model(self) -> str:
        """Get the model identifier."""
        return self._model

    @property
    def max_tokens(self) -> int:
        """Get the default max tokens."""
        return self._max_tokens

    @property
    def request_count(self) -> int:
        """Get total request count."""
        return self._request_count

    @property
    def error_count(self) -> int:
        """Get total error count."""
        return self._error_count

    @property
    def total_tokens_used(self) -> int:
        """Get total tokens used across all requests."""
        return self._total_tokens_used

    def get_stats(self) -> Dict[str, Any]:
        """
        Get client statistics.

        Returns:
            Dictionary with request count, error count, tokens used
        """
        return {
            "model": self._model,
            "max_tokens": self._max_tokens,
            "request_count": self._request_count,
            "error_count": self._error_count,
            "total_tokens_used": self._total_tokens_used,
            "error_rate": (
                self._error_count / self._request_count
                if self._request_count > 0
                else 0.0
            ),
        }

    def __repr__(self) -> str:
        """String representation for debugging."""
        return (
            f"ClaudeClientManager("
            f"model='{self._model}', "
            f"requests={self._request_count}, "
            f"errors={self._error_count})"
        )


# =============================================================================
# Factory Function
# =============================================================================


def create_claude_client_manager(
    config_manager: "ConfigManager",
    secrets_manager: "SecretsManager",
) -> ClaudeClientManager:
    """
    Factory function for ClaudeClientManager.

    Following Clean Architecture v5.1 Rule #1: Factory Functions.

    Args:
        config_manager: Configuration manager
        secrets_manager: Secrets manager for API key

    Returns:
        Configured ClaudeClientManager instance

    Raises:
        ClaudeConfigError: If API key is not found

    Example:
        >>> claude = create_claude_client_manager(config, secrets)
        >>> response = await claude.create_message(prompt, messages)
    """
    return ClaudeClientManager(
        config_manager=config_manager,
        secrets_manager=secrets_manager,
    )


# =============================================================================
# Export public interface
# =============================================================================

__all__ = [
    "ClaudeClientManager",
    "create_claude_client_manager",
    "ClaudeAPIError",
    "ClaudeConfigError",
]
