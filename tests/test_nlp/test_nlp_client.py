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
NLP Client Manager Tests for Ash-Bot Service
---
FILE VERSION: v5.0-1-1.7-1
LAST MODIFIED: 2026-01-03
PHASE: Phase 1 - Discord Connectivity
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-bot
Community: The Alphabet Cartel - https://discord.gg/alphabetcartel | https://alphabetcartel.org
============================================================================
Tests for NLPClientManager including:
- Factory function creation
- Message analysis with various responses
- Retry logic
- Error handling
- Context manager usage
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

import httpx

__version__ = "v5.0-1-1.7-1"


# =============================================================================
# Factory Function Tests
# =============================================================================


class TestNLPClientManagerFactory:
    """Tests for NLPClientManager factory function."""

    def test_create_nlp_client_manager(self, test_config_manager):
        """Test factory function creates manager correctly."""
        from src.managers.nlp import create_nlp_client_manager

        client = create_nlp_client_manager(test_config_manager)

        assert client is not None
        assert client.base_url == "http://test-nlp:30880"
        assert client.timeout == 2.0
        assert client.retry_attempts == 1

    def test_create_with_defaults(self, test_config_manager):
        """Test factory function uses default values correctly."""
        from src.managers.nlp import create_nlp_client_manager

        client = create_nlp_client_manager(test_config_manager)

        assert not client.is_closed


# =============================================================================
# Message Analysis Tests
# =============================================================================


class TestAnalyzeMessage:
    """Tests for analyze_message method."""

    @pytest.mark.asyncio
    async def test_analyze_message_success(self, test_nlp_client, mock_nlp_response):
        """Test successful message analysis."""
        from src.models import CrisisAnalysisResult

        with patch.object(
            test_nlp_client,
            "_make_request_with_retry",
            new_callable=AsyncMock,
            return_value=mock_nlp_response,
        ):
            result = await test_nlp_client.analyze_message(
                message="I'm feeling really down today", user_id="123", channel_id="456"
            )

            assert isinstance(result, CrisisAnalysisResult)
            assert result.crisis_detected is True
            assert result.severity == "high"
            assert result.crisis_score == 0.78

    @pytest.mark.asyncio
    async def test_analyze_message_safe(self, test_nlp_client, mock_safe_response):
        """Test safe message analysis."""
        with patch.object(
            test_nlp_client,
            "_make_request_with_retry",
            new_callable=AsyncMock,
            return_value=mock_safe_response,
        ):
            result = await test_nlp_client.analyze_message(
                message="Having a great day!"
            )

            assert result.crisis_detected is False
            assert result.severity == "safe"
            assert result.is_actionable is False

    @pytest.mark.asyncio
    async def test_analyze_message_with_history(
        self, test_nlp_client, mock_nlp_response
    ):
        """Test message analysis with history context."""
        from src.models import MessageHistoryItem

        history = [
            MessageHistoryItem(
                message="Previous message",
                timestamp="2026-01-03T10:00:00Z",
                crisis_score=0.3,
            )
        ]

        with patch.object(
            test_nlp_client,
            "_make_request_with_retry",
            new_callable=AsyncMock,
            return_value=mock_nlp_response,
        ) as mock_request:
            await test_nlp_client.analyze_message(
                message="Current message", message_history=history
            )

            # Verify history was included in request
            call_args = mock_request.call_args
            json_data = call_args.kwargs.get("json_data", call_args[1].get("json_data"))
            assert "message_history" in json_data
            assert len(json_data["message_history"]) == 1

    @pytest.mark.asyncio
    async def test_analyze_message_error_returns_safe(self, test_nlp_client):
        """Test that errors return safe result instead of crashing."""
        from src.managers.nlp import NLPClientError

        with patch.object(
            test_nlp_client,
            "_make_request_with_retry",
            new_callable=AsyncMock,
            side_effect=NLPClientError("API unavailable"),
        ):
            result = await test_nlp_client.analyze_message(message="Test message")

            # Should return safe error result
            assert result.crisis_detected is False
            assert result.severity == "safe"
            assert result.is_degraded is True


# =============================================================================
# Health Check Tests
# =============================================================================


class TestHealthCheck:
    """Tests for health_check method."""

    @pytest.mark.asyncio
    async def test_health_check_healthy(self, test_nlp_client):
        """Test health check returns True when healthy."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"ready": True, "degraded": False}

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)

        test_nlp_client._client = mock_client

        result = await test_nlp_client.health_check()
        assert result is True

    @pytest.mark.asyncio
    async def test_health_check_unhealthy(self, test_nlp_client):
        """Test health check returns False when unhealthy."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"ready": False}

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)

        test_nlp_client._client = mock_client

        result = await test_nlp_client.health_check()
        assert result is False

    @pytest.mark.asyncio
    async def test_health_check_timeout(self, test_nlp_client):
        """Test health check returns False on timeout."""
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(side_effect=httpx.TimeoutException("timeout"))

        test_nlp_client._client = mock_client

        result = await test_nlp_client.health_check()
        assert result is False

    @pytest.mark.asyncio
    async def test_health_check_connection_error(self, test_nlp_client):
        """Test health check returns False on connection error."""
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(
            side_effect=httpx.ConnectError("connection refused")
        )

        test_nlp_client._client = mock_client

        result = await test_nlp_client.health_check()
        assert result is False


# =============================================================================
# Retry Logic Tests
# =============================================================================


class TestRetryLogic:
    """Tests for retry logic."""

    @pytest.mark.asyncio
    async def test_retry_on_timeout(self, test_nlp_client, mock_nlp_response):
        """Test retry on timeout."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_nlp_response

        mock_client = AsyncMock()
        # First call times out, second succeeds
        mock_client.post = AsyncMock(
            side_effect=[httpx.TimeoutException("timeout"), mock_response]
        )

        test_nlp_client._client = mock_client

        response = await test_nlp_client._make_request_with_retry(
            method="POST", endpoint="/analyze", json_data={"message": "test"}
        )

        assert response == mock_nlp_response
        assert mock_client.post.call_count == 2

    @pytest.mark.asyncio
    async def test_no_retry_on_validation_error(self, test_nlp_client):
        """Test no retry on 4xx validation errors."""
        from src.managers.nlp import NLPValidationError

        mock_response = MagicMock()
        mock_response.status_code = 422
        mock_response.json.return_value = {"detail": "Invalid message"}
        mock_response.text = "Invalid message"

        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)

        test_nlp_client._client = mock_client

        with pytest.raises(NLPValidationError):
            await test_nlp_client._make_request_with_retry(
                method="POST", endpoint="/analyze", json_data={"message": ""}
            )

        # Should only be called once (no retry)
        assert mock_client.post.call_count == 1


# =============================================================================
# Context Manager Tests
# =============================================================================


class TestContextManager:
    """Tests for async context manager."""

    @pytest.mark.asyncio
    async def test_context_manager_enter_exit(self, test_config_manager):
        """Test async context manager."""
        from src.managers.nlp import create_nlp_client_manager

        client = create_nlp_client_manager(test_config_manager)

        async with client as nlp:
            assert nlp is client
            assert not nlp.is_closed

        assert client.is_closed

    @pytest.mark.asyncio
    async def test_close_method(self, test_nlp_client):
        """Test explicit close method."""
        # Initialize client
        await test_nlp_client._get_client()
        assert test_nlp_client._client is not None

        # Close
        await test_nlp_client.close()
        assert test_nlp_client.is_closed


# =============================================================================
# Model Data Tests
# =============================================================================


class TestCrisisAnalysisResult:
    """Tests for CrisisAnalysisResult model."""

    def test_from_api_response(self, mock_nlp_response):
        """Test creating result from API response."""
        from src.models import CrisisAnalysisResult

        result = CrisisAnalysisResult.from_api_response(mock_nlp_response)

        assert result.crisis_detected is True
        assert result.severity == "high"
        assert result.confidence == 0.87
        assert len(result.signals) == 4
        assert "bart" in result.signals

    def test_convenience_properties(self, sample_crisis_result):
        """Test convenience properties."""
        assert sample_crisis_result.is_crisis is True
        assert sample_crisis_result.is_actionable is True
        assert sample_crisis_result.requires_alert is True
        assert sample_crisis_result.requires_ash_response is True

    def test_safe_result_properties(self, sample_safe_result):
        """Test safe result properties."""
        assert sample_safe_result.is_crisis is False
        assert sample_safe_result.is_actionable is False
        assert sample_safe_result.requires_alert is False
        assert sample_safe_result.requires_ash_response is False

    def test_to_dict(self, sample_crisis_result):
        """Test serialization to dictionary."""
        data = sample_crisis_result.to_dict()

        assert isinstance(data, dict)
        assert data["crisis_detected"] is True
        assert data["severity"] == "high"
        assert "signals" in data

    def test_to_log_dict(self, sample_crisis_result):
        """Test compact log dictionary."""
        data = sample_crisis_result.to_log_dict()

        assert "crisis" in data
        assert "severity" in data
        assert "score" in data
        # Should not include full signals
        assert "signals" not in data

    def test_create_error_result(self):
        """Test error result creation."""
        from src.models import CrisisAnalysisResult

        result = CrisisAnalysisResult.create_error_result(
            error_message="API timeout", request_id="error_123"
        )

        assert result.crisis_detected is False
        assert result.severity == "safe"
        assert result.is_degraded is True
        assert "API timeout" in result.explanation_summary


# =============================================================================
# Message History Item Tests
# =============================================================================


class TestMessageHistoryItem:
    """Tests for MessageHistoryItem model."""

    def test_to_dict(self):
        """Test conversion to dictionary."""
        from src.models import MessageHistoryItem

        item = MessageHistoryItem(
            message="Test message",
            timestamp="2026-01-03T10:00:00Z",
            crisis_score=0.5,
            message_id="msg_123",
        )

        data = item.to_dict()

        assert data["message"] == "Test message"
        assert data["timestamp"] == "2026-01-03T10:00:00Z"
        assert data["crisis_score"] == 0.5
        assert data["message_id"] == "msg_123"

    def test_to_dict_optional_fields(self):
        """Test that optional fields are omitted when None."""
        from src.models import MessageHistoryItem

        item = MessageHistoryItem(message="Test", timestamp="2026-01-03T10:00:00Z")

        data = item.to_dict()

        assert "message" in data
        assert "timestamp" in data
        assert "crisis_score" not in data
        assert "message_id" not in data

    def test_from_dict(self):
        """Test creation from dictionary."""
        from src.models import MessageHistoryItem

        data = {
            "message": "Test",
            "timestamp": "2026-01-03T10:00:00Z",
            "crisis_score": 0.3,
        }

        item = MessageHistoryItem.from_dict(data)

        assert item.message == "Test"
        assert item.crisis_score == 0.3


# =============================================================================
# Severity Level Tests
# =============================================================================


class TestSeverityLevel:
    """Tests for SeverityLevel constants."""

    def test_is_valid(self):
        """Test severity validation."""
        from src.models.nlp_models import SeverityLevel

        assert SeverityLevel.is_valid("safe") is True
        assert SeverityLevel.is_valid("high") is True
        assert SeverityLevel.is_valid("CRITICAL") is True
        assert SeverityLevel.is_valid("invalid") is False

    def test_is_actionable(self):
        """Test actionable severity check."""
        from src.models.nlp_models import SeverityLevel

        assert SeverityLevel.is_actionable("safe") is False
        assert SeverityLevel.is_actionable("low") is False
        assert SeverityLevel.is_actionable("medium") is True
        assert SeverityLevel.is_actionable("high") is True
        assert SeverityLevel.is_actionable("critical") is True

    def test_requires_ash_response(self):
        """Test Ash response requirement check."""
        from src.models.nlp_models import SeverityLevel

        assert SeverityLevel.requires_ash_response("safe") is False
        assert SeverityLevel.requires_ash_response("medium") is False
        assert SeverityLevel.requires_ash_response("high") is True
        assert SeverityLevel.requires_ash_response("critical") is True

    def test_get_level_index(self):
        """Test severity level indexing."""
        from src.models.nlp_models import SeverityLevel

        assert SeverityLevel.get_level_index("safe") == 0
        assert SeverityLevel.get_level_index("critical") == 4
        assert SeverityLevel.get_level_index("invalid") == -1
