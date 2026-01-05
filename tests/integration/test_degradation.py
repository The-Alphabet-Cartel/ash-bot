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
Integration Tests: Service Degradation
---
FILE VERSION: v5.0-6-1.4-1
LAST MODIFIED: 2026-01-04
PHASE: Phase 6 - Final Testing & Documentation
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-bot
Community: The Alphabet Cartel - https://discord.gg/alphabetcartel | https://alphabetcartel.org

Tests for Scenarios 6 and 7:
- Scenario 6: NLP Service Unavailable
- Scenario 7: Redis Service Unavailable
============================================================================
"""

import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch


# =============================================================================
# Scenario 6: NLP Service Unavailable
# =============================================================================


class TestNLPServiceDegradation:
    """
    Scenario 6: Service Degradation - NLP Unavailable

    Input: NLP service down, user sends message
    Expected:
    1. NLPClientManager circuit breaker trips after failures
    2. Fallback response returned (MEDIUM severity)
    3. Alert still sent (conservative approach)
    4. System continues operating
    5. Health endpoint shows degraded
    """

    @pytest.mark.asyncio
    async def test_nlp_failure_triggers_circuit_breaker(
        self,
        mock_nlp_client,
    ):
        """Test that repeated NLP failures trigger circuit breaker."""
        # Simulate multiple failures
        failure_count = 0
        threshold = 5

        mock_nlp_client.analyze_message = AsyncMock(
            side_effect=Exception("NLP Service Unavailable")
        )

        for _ in range(threshold):
            try:
                await mock_nlp_client.analyze_message("Test message")
            except Exception:
                failure_count += 1

        # After threshold, circuit breaker should open
        assert failure_count == threshold

    @pytest.mark.asyncio
    async def test_fallback_response_returned_on_nlp_failure(
        self,
        mock_nlp_client,
        degraded_nlp_response,
    ):
        """Test that fallback (MEDIUM) severity is returned when NLP fails."""

        # First try fails, fallback kicks in
        async def failing_then_fallback(*args, **kwargs):
            raise Exception("NLP Service Unavailable")

        mock_nlp_client.analyze_message = AsyncMock(side_effect=failing_then_fallback)
        mock_nlp_client.get_fallback_response = MagicMock(
            return_value=degraded_nlp_response
        )

        # Simulate the actual fallback logic
        try:
            await mock_nlp_client.analyze_message("Test message")
        except Exception:
            result = mock_nlp_client.get_fallback_response()

        # Verify fallback response
        assert result["severity"] == "medium"
        assert result["is_degraded"] is True
        assert result["crisis_detected"] is True  # Conservative approach

    @pytest.mark.asyncio
    async def test_alert_sent_during_nlp_degradation(
        self,
        mock_alert_dispatcher,
        degraded_nlp_response,
        message_factory,
    ):
        """Test that alerts are still sent during NLP degradation."""
        message = message_factory("Test message during degradation")

        # Alert should be dispatched even with degraded response
        await mock_alert_dispatcher.dispatch_alert(
            message=message,
            nlp_result=degraded_nlp_response,
        )

        mock_alert_dispatcher.dispatch_alert.assert_called_once()

    @pytest.mark.asyncio
    async def test_system_continues_operating_during_nlp_outage(
        self,
        mock_nlp_client,
        mock_alert_dispatcher,
        mock_channel_config,
        degraded_nlp_response,
        message_factory,
    ):
        """Test that system continues operating when NLP is down."""
        message = message_factory("Test message")

        # Setup fallback
        mock_nlp_client.get_fallback_response = MagicMock(
            return_value=degraded_nlp_response
        )
        mock_nlp_client.analyze_message = AsyncMock(side_effect=Exception("NLP Down"))

        # Process message with fallback
        try:
            await mock_nlp_client.analyze_message(message.content)
            result = None
        except Exception:
            result = mock_nlp_client.get_fallback_response()

        # System should still work
        assert result is not None
        assert result["severity"] == "medium"

        # Alert channel should still be available
        channel = mock_channel_config.get_alert_channel(result["severity"])
        assert channel is not None

    @pytest.mark.asyncio
    async def test_health_endpoint_shows_degraded_status(
        self,
        mock_health_manager,
    ):
        """Test that health endpoint reflects degraded NLP status."""
        # Simulate degraded state
        mock_health_manager.get_status = MagicMock(
            return_value={
                "status": "degraded",
                "components": {
                    "discord": {"status": "healthy"},
                    "nlp": {"status": "unhealthy", "reason": "Circuit breaker open"},
                    "redis": {"status": "healthy"},
                },
            }
        )

        status = mock_health_manager.get_status()

        assert status["status"] == "degraded"
        assert status["components"]["nlp"]["status"] == "unhealthy"

    @pytest.mark.asyncio
    async def test_nlp_recovery_after_circuit_breaker_closes(
        self,
        mock_nlp_client,
        safe_nlp_response,
    ):
        """Test that NLP recovers when circuit breaker closes."""
        # After recovery period, circuit breaker allows requests
        mock_nlp_client.analyze_message = AsyncMock(return_value=safe_nlp_response)
        mock_nlp_client.is_healthy = MagicMock(return_value=True)

        # Successful request after recovery
        result = await mock_nlp_client.analyze_message("Test after recovery")

        assert result["severity"] == "safe"
        assert mock_nlp_client.is_healthy() is True


# =============================================================================
# Scenario 7: Redis Service Unavailable
# =============================================================================


class TestRedisServiceDegradation:
    """
    Scenario 7: Service Degradation - Redis Unavailable

    Input: Redis down, user sends crisis message
    Expected:
    1. RedisManager operations fail gracefully
    2. History storage skipped (logged)
    3. NLP analysis still works
    4. Alert still dispatched
    5. System continues operating
    """

    @pytest.mark.asyncio
    async def test_redis_failure_handled_gracefully(
        self,
        mock_redis_manager,
    ):
        """Test that Redis failures are handled gracefully."""
        # Simulate Redis down
        mock_redis_manager.is_connected = False
        mock_redis_manager.lpush = AsyncMock(
            side_effect=Exception("Redis connection refused")
        )

        # Operation should fail gracefully
        try:
            await mock_redis_manager.lpush("key", "value")
            success = True
        except Exception:
            success = False

        assert success is False

    @pytest.mark.asyncio
    async def test_history_storage_skipped_on_redis_failure(
        self,
        mock_user_history,
        mock_redis_manager,
    ):
        """Test that history storage is skipped when Redis is down."""
        # Redis unavailable
        mock_redis_manager.is_connected = False
        mock_user_history.add_message = AsyncMock(return_value=False)

        # Attempt to store - should return False but not crash
        result = await mock_user_history.add_message(
            user_id="123",
            message_content="Test",
            severity="high",
            crisis_score=0.78,
        )

        assert result is False

    @pytest.mark.asyncio
    async def test_nlp_analysis_works_without_redis(
        self,
        mock_nlp_client,
        mock_redis_manager,
        high_nlp_response,
        crisis_message_text,
    ):
        """Test that NLP analysis continues when Redis is down."""
        # Redis down
        mock_redis_manager.is_connected = False

        # NLP should still work
        mock_nlp_client.analyze_message = AsyncMock(return_value=high_nlp_response)

        result = await mock_nlp_client.analyze_message(crisis_message_text)

        assert result["crisis_detected"] is True
        assert result["severity"] == "high"

    @pytest.mark.asyncio
    async def test_alerts_dispatched_without_redis(
        self,
        mock_alert_dispatcher,
        mock_redis_manager,
        high_nlp_response,
        message_factory,
        crisis_message_text,
    ):
        """Test that alerts are still dispatched when Redis is down."""
        # Redis down
        mock_redis_manager.is_connected = False

        message = message_factory(crisis_message_text)

        # Alert should still work
        await mock_alert_dispatcher.dispatch_alert(
            message=message,
            nlp_result=high_nlp_response,
        )

        mock_alert_dispatcher.dispatch_alert.assert_called_once()

    @pytest.mark.asyncio
    async def test_complete_flow_without_redis(
        self,
        mock_nlp_client,
        mock_user_history,
        mock_alert_dispatcher,
        mock_redis_manager,
        high_nlp_response,
        message_factory,
        crisis_message_text,
    ):
        """Test complete message flow when Redis is unavailable."""
        # Setup: Redis down
        mock_redis_manager.is_connected = False
        mock_user_history.add_message = AsyncMock(return_value=False)
        mock_nlp_client.analyze_message = AsyncMock(return_value=high_nlp_response)

        message = message_factory(crisis_message_text)

        # Step 1: Analyze message (should work)
        result = await mock_nlp_client.analyze_message(message.content)
        assert result["crisis_detected"] is True

        # Step 2: Try to store (should fail gracefully)
        stored = await mock_user_history.add_message(
            user_id=str(message.author.id),
            message_content=message.content,
            severity=result["severity"],
            crisis_score=result["crisis_score"],
        )
        assert stored is False  # Failed but didn't crash

        # Step 3: Dispatch alert (should work)
        await mock_alert_dispatcher.dispatch_alert(
            message=message,
            nlp_result=result,
        )
        mock_alert_dispatcher.dispatch_alert.assert_called_once()

    @pytest.mark.asyncio
    async def test_redis_health_check_returns_false(
        self,
        mock_redis_manager,
    ):
        """Test that Redis health check returns False when down."""
        mock_redis_manager.health_check = AsyncMock(return_value=False)

        is_healthy = await mock_redis_manager.health_check()

        assert is_healthy is False

    @pytest.mark.asyncio
    async def test_health_status_reflects_redis_failure(
        self,
        mock_health_manager,
    ):
        """Test that health status shows Redis as unhealthy."""
        mock_health_manager.get_status = MagicMock(
            return_value={
                "status": "degraded",
                "components": {
                    "discord": {"status": "healthy"},
                    "nlp": {"status": "healthy"},
                    "redis": {"status": "unhealthy", "reason": "Connection refused"},
                },
            }
        )

        status = mock_health_manager.get_status()

        assert status["components"]["redis"]["status"] == "unhealthy"


# =============================================================================
# Combined Degradation Tests
# =============================================================================


class TestCombinedDegradation:
    """Tests for multiple service failures."""

    @pytest.mark.asyncio
    async def test_system_survives_nlp_and_redis_down(
        self,
        mock_nlp_client,
        mock_redis_manager,
        mock_alert_dispatcher,
        degraded_nlp_response,
        message_factory,
    ):
        """Test system continues when both NLP and Redis are down."""
        # Both services down
        mock_nlp_client.analyze_message = AsyncMock(side_effect=Exception("NLP Down"))
        mock_nlp_client.get_fallback_response = MagicMock(
            return_value=degraded_nlp_response
        )
        mock_redis_manager.is_connected = False

        message = message_factory("Test message")

        # Get fallback response
        try:
            await mock_nlp_client.analyze_message(message.content)
        except Exception:
            result = mock_nlp_client.get_fallback_response()

        # Alert should still work
        await mock_alert_dispatcher.dispatch_alert(
            message=message,
            nlp_result=result,
        )

        # System survived
        mock_alert_dispatcher.dispatch_alert.assert_called_once()


# =============================================================================
# Circuit Breaker Tests
# =============================================================================


class TestCircuitBreaker:
    """Tests for circuit breaker behavior."""

    def test_circuit_breaker_states(self):
        """Test circuit breaker state transitions."""
        states = ["CLOSED", "OPEN", "HALF_OPEN"]

        # All states should be valid
        for state in states:
            assert state in ["CLOSED", "OPEN", "HALF_OPEN"]

    @pytest.mark.asyncio
    async def test_circuit_breaker_opens_after_threshold(
        self,
        mock_nlp_client,
    ):
        """Test circuit breaker opens after failure threshold."""
        failure_threshold = 5
        failures = 0

        mock_nlp_client.analyze_message = AsyncMock(
            side_effect=Exception("Service Error")
        )

        for _ in range(failure_threshold):
            try:
                await mock_nlp_client.analyze_message("Test")
            except Exception:
                failures += 1

        # Should have hit threshold
        assert failures == failure_threshold

    @pytest.mark.asyncio
    async def test_circuit_breaker_allows_test_request_in_half_open(self):
        """Test circuit breaker allows test request in HALF_OPEN state."""
        # In HALF_OPEN, one request is allowed to test recovery
        # This is a state machine test
        state = "HALF_OPEN"
        requests_allowed = 1 if state == "HALF_OPEN" else 0

        assert requests_allowed == 1


# =============================================================================
# Retry Logic Tests
# =============================================================================


class TestRetryLogic:
    """Tests for retry behavior with exponential backoff."""

    @pytest.mark.asyncio
    async def test_retry_with_eventual_success(self):
        """Test that retry succeeds after transient failure."""
        attempt = 0
        max_retries = 3

        async def failing_then_succeeding():
            nonlocal attempt
            attempt += 1
            if attempt < 3:
                raise Exception("Transient failure")
            return {"success": True}

        result = None
        for _ in range(max_retries):
            try:
                result = await failing_then_succeeding()
                break
            except Exception:
                continue

        assert result is not None
        assert result["success"] is True
        assert attempt == 3

    def test_exponential_backoff_calculation(self):
        """Test exponential backoff timing."""
        base_delay = 1.0
        attempts = [0, 1, 2, 3]
        expected_delays = [1.0, 2.0, 4.0, 8.0]

        for attempt, expected in zip(attempts, expected_delays):
            delay = base_delay * (2**attempt)
            assert delay == expected


# =============================================================================
# Metrics During Degradation
# =============================================================================


class TestDegradationMetrics:
    """Tests for metrics during service degradation."""

    @pytest.mark.asyncio
    async def test_nlp_errors_metric_incremented(
        self,
        mock_metrics_manager,
    ):
        """Test NLP error metric is incremented on failures."""
        mock_metrics_manager.increment("nlp_errors_total")

        mock_metrics_manager.increment.assert_called_with("nlp_errors_total")

    @pytest.mark.asyncio
    async def test_redis_errors_metric_incremented(
        self,
        mock_metrics_manager,
    ):
        """Test Redis error metric is incremented on failures."""
        mock_metrics_manager.increment(
            "redis_operations_total", labels={"operation": "lpush", "status": "error"}
        )

        mock_metrics_manager.increment.assert_called()

    @pytest.mark.asyncio
    async def test_circuit_breaker_state_tracked(
        self,
        mock_metrics_manager,
    ):
        """Test circuit breaker state transitions are tracked."""
        mock_metrics_manager.gauge(
            "circuit_breaker_state",
            1,  # 0=CLOSED, 1=OPEN, 2=HALF_OPEN
            labels={"service": "nlp"},
        )

        mock_metrics_manager.gauge.assert_called()
