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
Claude Client Manager Tests for Ash-Bot Service
---
FILE VERSION: v5.0-4-3.0-1
LAST MODIFIED: 2026-01-04
PHASE: Phase 4 - Ash AI Integration
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-bot
Community: The Alphabet Cartel - https://discord.gg/alphabetcartel | https://alphabetcartel.org
============================================================================
Test suite for ClaudeClientManager.

USAGE:
    pytest tests/test_ash/test_claude_client.py -v
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, Any

import anthropic


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def mock_config_manager():
    """Create mock ConfigManager with Ash settings."""
    config = MagicMock()
    config.get.side_effect = lambda section, key, default=None: {
        ("ash", "model"): "claude-sonnet-4-20250514",
        ("ash", "max_tokens"): 500,
    }.get((section, key), default)
    return config


@pytest.fixture
def mock_secrets_manager():
    """Create mock SecretsManager with API key."""
    secrets = MagicMock()
    secrets.get_claude_api_token.return_value = "test-api-key-12345"
    return secrets


@pytest.fixture
def mock_secrets_manager_no_key():
    """Create mock SecretsManager without API key."""
    secrets = MagicMock()
    secrets.get_claude_api_token.return_value = None
    return secrets


@pytest.fixture
def mock_anthropic_response():
    """Create mock Anthropic API response."""
    response = MagicMock()
    response.content = [MagicMock(text="I hear you. That sounds really difficult.")]
    response.usage = MagicMock(output_tokens=15)
    return response


@pytest.fixture
def mock_anthropic_empty_response():
    """Create mock empty Anthropic API response."""
    response = MagicMock()
    response.content = []
    return response


# =============================================================================
# Initialization Tests
# =============================================================================


class TestClaudeClientManagerInit:
    """Tests for ClaudeClientManager initialization."""

    def test_init_success(self, mock_config_manager, mock_secrets_manager):
        """Test successful initialization with valid API key."""
        with patch("anthropic.AsyncAnthropic") as mock_client:
            from src.managers.ash.claude_client_manager import ClaudeClientManager

            manager = ClaudeClientManager(
                config_manager=mock_config_manager,
                secrets_manager=mock_secrets_manager,
            )

            assert manager.model == "claude-sonnet-4-20250514"
            assert manager.max_tokens == 500
            assert manager.request_count == 0
            assert manager.error_count == 0
            mock_client.assert_called_once_with(api_key="test-api-key-12345")

    def test_init_missing_api_key(self, mock_config_manager, mock_secrets_manager_no_key):
        """Test initialization fails without API key."""
        from src.managers.ash.claude_client_manager import (
            ClaudeClientManager,
            ClaudeConfigError,
        )

        with pytest.raises(ClaudeConfigError) as exc_info:
            ClaudeClientManager(
                config_manager=mock_config_manager,
                secrets_manager=mock_secrets_manager_no_key,
            )

        assert "Claude API key not found" in str(exc_info.value)

    def test_factory_function(self, mock_config_manager, mock_secrets_manager):
        """Test factory function creates manager correctly."""
        with patch("anthropic.AsyncAnthropic"):
            from src.managers.ash.claude_client_manager import (
                create_claude_client_manager,
            )

            manager = create_claude_client_manager(
                config_manager=mock_config_manager,
                secrets_manager=mock_secrets_manager,
            )

            assert manager is not None
            assert manager.model == "claude-sonnet-4-20250514"


# =============================================================================
# Message Creation Tests
# =============================================================================


class TestClaudeClientMessageCreation:
    """Tests for create_message functionality."""

    @pytest.mark.asyncio
    async def test_create_message_success(
        self, mock_config_manager, mock_secrets_manager, mock_anthropic_response
    ):
        """Test successful message creation."""
        with patch("anthropic.AsyncAnthropic") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.messages.create = AsyncMock(return_value=mock_anthropic_response)
            mock_client_class.return_value = mock_client

            from src.managers.ash.claude_client_manager import ClaudeClientManager

            manager = ClaudeClientManager(
                config_manager=mock_config_manager,
                secrets_manager=mock_secrets_manager,
            )

            response = await manager.create_message(
                system_prompt="You are Ash.",
                messages=[{"role": "user", "content": "I'm feeling sad."}],
            )

            assert response == "I hear you. That sounds really difficult."
            assert manager.request_count == 1
            assert manager.error_count == 0
            mock_client.messages.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_message_empty_response(
        self, mock_config_manager, mock_secrets_manager, mock_anthropic_empty_response
    ):
        """Test fallback on empty response."""
        with patch("anthropic.AsyncAnthropic") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.messages.create = AsyncMock(
                return_value=mock_anthropic_empty_response
            )
            mock_client_class.return_value = mock_client

            from src.managers.ash.claude_client_manager import ClaudeClientManager

            manager = ClaudeClientManager(
                config_manager=mock_config_manager,
                secrets_manager=mock_secrets_manager,
            )

            response = await manager.create_message(
                system_prompt="You are Ash.",
                messages=[{"role": "user", "content": "Hello"}],
            )

            assert "I'm here with you" in response
            assert "Crisis Response Team" in response

    @pytest.mark.asyncio
    async def test_create_message_with_custom_max_tokens(
        self, mock_config_manager, mock_secrets_manager, mock_anthropic_response
    ):
        """Test message creation with custom max tokens."""
        with patch("anthropic.AsyncAnthropic") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.messages.create = AsyncMock(return_value=mock_anthropic_response)
            mock_client_class.return_value = mock_client

            from src.managers.ash.claude_client_manager import ClaudeClientManager

            manager = ClaudeClientManager(
                config_manager=mock_config_manager,
                secrets_manager=mock_secrets_manager,
            )

            await manager.create_message(
                system_prompt="You are Ash.",
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=200,
            )

            call_kwargs = mock_client.messages.create.call_args.kwargs
            assert call_kwargs["max_tokens"] == 200

    @pytest.mark.asyncio
    async def test_create_message_rate_limit_error(
        self, mock_config_manager, mock_secrets_manager
    ):
        """Test rate limit error handling."""
        with patch("anthropic.AsyncAnthropic") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.messages.create = AsyncMock(
                side_effect=anthropic.RateLimitError(
                    message="Rate limited",
                    response=MagicMock(status_code=429),
                    body=None,
                )
            )
            mock_client_class.return_value = mock_client

            from src.managers.ash.claude_client_manager import (
                ClaudeClientManager,
                ClaudeAPIError,
            )

            manager = ClaudeClientManager(
                config_manager=mock_config_manager,
                secrets_manager=mock_secrets_manager,
            )

            with pytest.raises(ClaudeAPIError) as exc_info:
                await manager.create_message(
                    system_prompt="You are Ash.",
                    messages=[{"role": "user", "content": "Hello"}],
                )

            assert "Rate limit exceeded" in str(exc_info.value)
            assert manager.error_count == 1

    @pytest.mark.asyncio
    async def test_create_message_auth_error(
        self, mock_config_manager, mock_secrets_manager
    ):
        """Test authentication error handling."""
        with patch("anthropic.AsyncAnthropic") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.messages.create = AsyncMock(
                side_effect=anthropic.AuthenticationError(
                    message="Invalid API key",
                    response=MagicMock(status_code=401),
                    body=None,
                )
            )
            mock_client_class.return_value = mock_client

            from src.managers.ash.claude_client_manager import (
                ClaudeClientManager,
                ClaudeAPIError,
            )

            manager = ClaudeClientManager(
                config_manager=mock_config_manager,
                secrets_manager=mock_secrets_manager,
            )

            with pytest.raises(ClaudeAPIError) as exc_info:
                await manager.create_message(
                    system_prompt="You are Ash.",
                    messages=[{"role": "user", "content": "Hello"}],
                )

            assert "Authentication failed" in str(exc_info.value)


# =============================================================================
# Safe Message Creation Tests
# =============================================================================


class TestClaudeClientSafeMessage:
    """Tests for create_message_safe functionality."""

    @pytest.mark.asyncio
    async def test_create_message_safe_success(
        self, mock_config_manager, mock_secrets_manager, mock_anthropic_response
    ):
        """Test safe message creation on success."""
        with patch("anthropic.AsyncAnthropic") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.messages.create = AsyncMock(return_value=mock_anthropic_response)
            mock_client_class.return_value = mock_client

            from src.managers.ash.claude_client_manager import ClaudeClientManager

            manager = ClaudeClientManager(
                config_manager=mock_config_manager,
                secrets_manager=mock_secrets_manager,
            )

            response = await manager.create_message_safe(
                system_prompt="You are Ash.",
                messages=[{"role": "user", "content": "Hello"}],
            )

            assert response == "I hear you. That sounds really difficult."

    @pytest.mark.asyncio
    async def test_create_message_safe_fallback(
        self, mock_config_manager, mock_secrets_manager
    ):
        """Test safe message creation returns fallback on error."""
        with patch("anthropic.AsyncAnthropic") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.messages.create = AsyncMock(
                side_effect=anthropic.APIError(
                    message="Server error",
                    request=MagicMock(),
                    body=None,
                )
            )
            mock_client_class.return_value = mock_client

            from src.managers.ash.claude_client_manager import ClaudeClientManager

            manager = ClaudeClientManager(
                config_manager=mock_config_manager,
                secrets_manager=mock_secrets_manager,
            )

            # Should NOT raise exception
            response = await manager.create_message_safe(
                system_prompt="You are Ash.",
                messages=[{"role": "user", "content": "Hello"}],
            )

            assert "I'm here with you" in response
            assert "Crisis Response Team" in response


# =============================================================================
# Health Check Tests
# =============================================================================


class TestClaudeClientHealthCheck:
    """Tests for health check functionality."""

    @pytest.mark.asyncio
    async def test_health_check_success(
        self, mock_config_manager, mock_secrets_manager, mock_anthropic_response
    ):
        """Test successful health check."""
        with patch("anthropic.AsyncAnthropic") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.messages.create = AsyncMock(return_value=mock_anthropic_response)
            mock_client_class.return_value = mock_client

            from src.managers.ash.claude_client_manager import ClaudeClientManager

            manager = ClaudeClientManager(
                config_manager=mock_config_manager,
                secrets_manager=mock_secrets_manager,
            )

            result = await manager.health_check()

            assert result is True

    @pytest.mark.asyncio
    async def test_health_check_failure(
        self, mock_config_manager, mock_secrets_manager
    ):
        """Test health check returns False on failure."""
        with patch("anthropic.AsyncAnthropic") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.messages.create = AsyncMock(
                side_effect=Exception("Connection failed")
            )
            mock_client_class.return_value = mock_client

            from src.managers.ash.claude_client_manager import ClaudeClientManager

            manager = ClaudeClientManager(
                config_manager=mock_config_manager,
                secrets_manager=mock_secrets_manager,
            )

            result = await manager.health_check()

            assert result is False


# =============================================================================
# Statistics Tests
# =============================================================================


class TestClaudeClientStatistics:
    """Tests for statistics tracking."""

    @pytest.mark.asyncio
    async def test_request_count_increments(
        self, mock_config_manager, mock_secrets_manager, mock_anthropic_response
    ):
        """Test request count increments on each call."""
        with patch("anthropic.AsyncAnthropic") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.messages.create = AsyncMock(return_value=mock_anthropic_response)
            mock_client_class.return_value = mock_client

            from src.managers.ash.claude_client_manager import ClaudeClientManager

            manager = ClaudeClientManager(
                config_manager=mock_config_manager,
                secrets_manager=mock_secrets_manager,
            )

            assert manager.request_count == 0

            await manager.create_message("Test", [{"role": "user", "content": "Hi"}])
            assert manager.request_count == 1

            await manager.create_message("Test", [{"role": "user", "content": "Hi"}])
            assert manager.request_count == 2

    @pytest.mark.asyncio
    async def test_error_count_increments(
        self, mock_config_manager, mock_secrets_manager
    ):
        """Test error count increments on failures."""
        with patch("anthropic.AsyncAnthropic") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.messages.create = AsyncMock(
                side_effect=anthropic.APIError(
                    message="Error",
                    request=MagicMock(),
                    body=None,
                )
            )
            mock_client_class.return_value = mock_client

            from src.managers.ash.claude_client_manager import (
                ClaudeClientManager,
                ClaudeAPIError,
            )

            manager = ClaudeClientManager(
                config_manager=mock_config_manager,
                secrets_manager=mock_secrets_manager,
            )

            assert manager.error_count == 0

            with pytest.raises(ClaudeAPIError):
                await manager.create_message("Test", [{"role": "user", "content": "Hi"}])

            assert manager.error_count == 1

    def test_get_stats(self, mock_config_manager, mock_secrets_manager):
        """Test get_stats returns correct data."""
        with patch("anthropic.AsyncAnthropic"):
            from src.managers.ash.claude_client_manager import ClaudeClientManager

            manager = ClaudeClientManager(
                config_manager=mock_config_manager,
                secrets_manager=mock_secrets_manager,
            )

            stats = manager.get_stats()

            assert stats["model"] == "claude-sonnet-4-20250514"
            assert stats["max_tokens"] == 500
            assert stats["request_count"] == 0
            assert stats["error_count"] == 0
            assert stats["error_rate"] == 0.0


# =============================================================================
# Repr Tests
# =============================================================================


class TestClaudeClientRepr:
    """Tests for string representation."""

    def test_repr(self, mock_config_manager, mock_secrets_manager):
        """Test __repr__ returns useful info."""
        with patch("anthropic.AsyncAnthropic"):
            from src.managers.ash.claude_client_manager import ClaudeClientManager

            manager = ClaudeClientManager(
                config_manager=mock_config_manager,
                secrets_manager=mock_secrets_manager,
            )

            repr_str = repr(manager)

            assert "ClaudeClientManager" in repr_str
            assert "claude-sonnet-4-20250514" in repr_str
            assert "requests=0" in repr_str
