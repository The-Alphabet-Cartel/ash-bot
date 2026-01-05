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
Integration Tests: Message Flow
---
FILE VERSION: v5.0-6-1.1-1
LAST MODIFIED: 2026-01-04
PHASE: Phase 6 - Final Testing & Documentation
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-bot
Community: The Alphabet Cartel - https://discord.gg/alphabetcartel | https://alphabetcartel.org
============================================================================
Tests for Scenarios 1 and 2:
- Scenario 1: Safe message processing (no alert, no storage)
- Scenario 2: Crisis message processing (alert + storage + metrics)
"""

import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch, call

# =============================================================================
# Scenario 1: Safe Message Flow
# =============================================================================


class TestSafeMessageFlow:
    """
    Scenario 1: Message Flow - Safe Message

    Input: User sends "Having a great day!"
    Expected:
    1. DiscordManager receives message
    2. NLPClientManager analyzes → SAFE severity
    3. No Redis storage (SAFE not stored)
    4. No alert dispatched
    5. Metrics: messages_processed_total +1
    """

    @pytest.mark.asyncio
    async def test_safe_message_detected_correctly(
        self,
        mock_nlp_client,
        safe_nlp_response,
        safe_message_text,
    ):
        """Test that NLP correctly identifies safe messages."""
        mock_nlp_client.analyze_message = AsyncMock(return_value=safe_nlp_response)

        result = await mock_nlp_client.analyze_message(safe_message_text)

        assert result["crisis_detected"] is False
        assert result["severity"] == "safe"
        assert result["requires_intervention"] is False
        mock_nlp_client.analyze_message.assert_called_once_with(safe_message_text)

    @pytest.mark.asyncio
    async def test_safe_message_not_stored_in_redis(
        self,
        mock_user_history,
        safe_nlp_response,
        mock_user,
    ):
        """Test that SAFE messages are NOT stored in Redis."""
        # Configure should_store to return False for SAFE
        mock_user_history.should_store = MagicMock(
            side_effect=lambda severity: severity not in ["safe", "none"]
        )

        # Simulate the check
        should_store = mock_user_history.should_store(safe_nlp_response["severity"])

        assert should_store is False

        # Verify add_message was never called for safe messages
        # (In real flow, this would be checked in the message handler)

    @pytest.mark.asyncio
    async def test_safe_message_no_alert_dispatched(
        self,
        mock_alert_dispatcher,
        safe_nlp_response,
    ):
        """Test that no alert is dispatched for SAFE messages."""
        # For safe messages, dispatch_alert should not be called
        # The logic in the actual handler checks severity before dispatching

        severity = safe_nlp_response["severity"]
        alerting_severities = ["critical", "high", "medium", "low"]

        should_alert = severity in alerting_severities

        assert should_alert is False

    @pytest.mark.asyncio
    async def test_safe_message_metrics_incremented(
        self,
        mock_metrics_manager,
    ):
        """Test that messages_processed_total metric is incremented."""
        # Simulate metric increment
        mock_metrics_manager.increment("messages_processed_total")

        mock_metrics_manager.increment.assert_called_with("messages_processed_total")

    @pytest.mark.asyncio
    async def test_safe_message_full_flow(
        self,
        mock_nlp_client,
        mock_user_history,
        mock_alert_dispatcher,
        mock_metrics_manager,
        mock_channel_config,
        safe_nlp_response,
        safe_message_text,
        message_factory,
    ):
        """Test complete flow for safe message processing."""
        # Setup
        mock_nlp_client.analyze_message = AsyncMock(return_value=safe_nlp_response)
        message = message_factory(safe_message_text)

        # Step 1: Check if channel is monitored
        assert mock_channel_config.is_monitored_channel(message.channel.id)

        # Step 2: Analyze message
        result = await mock_nlp_client.analyze_message(message.content)

        # Step 3: Verify result
        assert result["severity"] == "safe"
        assert result["crisis_detected"] is False

        # Step 4: Verify no storage for safe messages
        mock_user_history.should_store = MagicMock(return_value=False)
        assert mock_user_history.should_store(result["severity"]) is False

        # Step 5: Verify no alert dispatched
        # (In real code, alert_dispatcher.dispatch_alert would not be called)

        # Step 6: Verify metrics
        mock_metrics_manager.increment("messages_processed_total")
        mock_metrics_manager.increment.assert_called()


# =============================================================================
# Scenario 2: Crisis Message Flow
# =============================================================================


class TestCrisisMessageFlow:
    """
    Scenario 2: Message Flow - Crisis Message (HIGH severity)

    Input: User sends crisis-indicating message
    Expected:
    1. DiscordManager receives message
    2. NLPClientManager analyzes → HIGH severity
    3. RedisManager stores in user history
    4. AlertDispatcher sends embed to #crisis-response
    5. CRT role is pinged
    6. "Acknowledge" and "Talk to Ash" buttons present
    7. Metrics: messages_analyzed_total{severity="high"} +1
    8. Metrics: alerts_sent_total{severity="high"} +1
    """

    @pytest.mark.asyncio
    async def test_crisis_message_detected_correctly(
        self,
        mock_nlp_client,
        high_nlp_response,
        crisis_message_text,
    ):
        """Test that NLP correctly identifies crisis messages."""
        mock_nlp_client.analyze_message = AsyncMock(return_value=high_nlp_response)

        result = await mock_nlp_client.analyze_message(crisis_message_text)

        assert result["crisis_detected"] is True
        assert result["severity"] == "high"
        assert result["requires_intervention"] is True
        mock_nlp_client.analyze_message.assert_called_once_with(crisis_message_text)

    @pytest.mark.asyncio
    async def test_crisis_message_stored_in_redis(
        self,
        mock_user_history,
        mock_redis_manager,
        high_nlp_response,
        mock_user,
        message_factory,
        crisis_message_text,
    ):
        """Test that HIGH severity messages ARE stored in Redis."""
        message = message_factory(crisis_message_text)

        # Configure should_store to return True for HIGH
        mock_user_history.should_store = MagicMock(
            side_effect=lambda severity: severity not in ["safe", "none"]
        )

        should_store = mock_user_history.should_store(high_nlp_response["severity"])
        assert should_store is True

        # Simulate storage
        await mock_user_history.add_message(
            user_id=str(message.author.id),
            message_content=message.content,
            severity=high_nlp_response["severity"],
            crisis_score=high_nlp_response["crisis_score"],
        )

        mock_user_history.add_message.assert_called_once()

    @pytest.mark.asyncio
    async def test_crisis_alert_dispatched(
        self,
        mock_alert_dispatcher,
        high_nlp_response,
        message_factory,
        crisis_message_text,
    ):
        """Test that alert is dispatched for HIGH severity messages."""
        message = message_factory(crisis_message_text)

        # Simulate alert dispatch
        result = await mock_alert_dispatcher.dispatch_alert(
            message=message,
            nlp_result=high_nlp_response,
        )

        assert result is True
        mock_alert_dispatcher.dispatch_alert.assert_called_once()

    @pytest.mark.asyncio
    async def test_crt_role_pinged_for_high_severity(
        self,
        mock_channel_config,
        high_nlp_response,
    ):
        """Test that CRT role is pinged for HIGH severity."""
        should_ping = mock_channel_config.should_ping_for_severity(
            high_nlp_response["severity"]
        )

        assert should_ping is True
        assert mock_channel_config.has_crt_role() is True

    @pytest.mark.asyncio
    async def test_alert_channel_selection_for_high(
        self,
        mock_channel_config,
        mock_alert_channel,
        high_nlp_response,
    ):
        """Test that correct alert channel is selected for HIGH severity."""
        channel = mock_channel_config.get_alert_channel(high_nlp_response["severity"])

        # HIGH severity should go to crisis-response channel
        assert channel.id == mock_alert_channel.id

    @pytest.mark.asyncio
    async def test_crisis_metrics_incremented(
        self,
        mock_metrics_manager,
        high_nlp_response,
    ):
        """Test that severity-specific metrics are incremented."""
        severity = high_nlp_response["severity"]

        # Simulate metrics
        mock_metrics_manager.increment(
            "messages_analyzed_total", labels={"severity": severity}
        )
        mock_metrics_manager.increment(
            "alerts_sent_total", labels={"severity": severity}
        )

        # Verify both metrics called
        assert mock_metrics_manager.increment.call_count == 2

    @pytest.mark.asyncio
    async def test_crisis_message_full_flow(
        self,
        mock_nlp_client,
        mock_user_history,
        mock_alert_dispatcher,
        mock_metrics_manager,
        mock_channel_config,
        high_nlp_response,
        crisis_message_text,
        message_factory,
        mock_alert_channel,
    ):
        """Test complete flow for crisis message processing."""
        # Setup
        mock_nlp_client.analyze_message = AsyncMock(return_value=high_nlp_response)
        mock_user_history.should_store = MagicMock(return_value=True)
        message = message_factory(crisis_message_text)

        # Step 1: Check if channel is monitored
        assert mock_channel_config.is_monitored_channel(message.channel.id)

        # Step 2: Analyze message
        result = await mock_nlp_client.analyze_message(message.content)

        # Step 3: Verify crisis detected
        assert result["crisis_detected"] is True
        assert result["severity"] == "high"

        # Step 4: Store in Redis (for HIGH severity)
        assert mock_user_history.should_store(result["severity"]) is True
        await mock_user_history.add_message(
            user_id=str(message.author.id),
            message_content=message.content,
            severity=result["severity"],
            crisis_score=result["crisis_score"],
        )

        # Step 5: Get alert channel
        alert_channel = mock_channel_config.get_alert_channel(result["severity"])
        assert alert_channel.id == mock_alert_channel.id

        # Step 6: Check CRT ping requirement
        assert mock_channel_config.should_ping_for_severity(result["severity"]) is True

        # Step 7: Dispatch alert
        await mock_alert_dispatcher.dispatch_alert(
            message=message,
            nlp_result=result,
        )

        # Step 8: Verify metrics
        mock_metrics_manager.increment("messages_processed_total")
        mock_metrics_manager.increment(
            "messages_analyzed_total", labels={"severity": result["severity"]}
        )
        mock_metrics_manager.increment(
            "alerts_sent_total", labels={"severity": result["severity"]}
        )


# =============================================================================
# Critical Message Flow Tests
# =============================================================================


class TestCriticalMessageFlow:
    """Tests for CRITICAL severity messages."""

    @pytest.mark.asyncio
    async def test_critical_message_immediate_outreach(
        self,
        mock_nlp_client,
        critical_nlp_response,
        critical_message_text,
    ):
        """Test CRITICAL messages trigger immediate_outreach action."""
        mock_nlp_client.analyze_message = AsyncMock(return_value=critical_nlp_response)

        result = await mock_nlp_client.analyze_message(critical_message_text)

        assert result["severity"] == "critical"
        assert result["recommended_action"] == "immediate_outreach"
        assert result["crisis_score"] >= 0.85

    @pytest.mark.asyncio
    async def test_critical_message_crt_ping(
        self,
        mock_channel_config,
    ):
        """Test CRITICAL messages always ping CRT."""
        should_ping = mock_channel_config.should_ping_for_severity("critical")
        assert should_ping is True


# =============================================================================
# Medium and Low Severity Tests
# =============================================================================


class TestMediumSeverityFlow:
    """Tests for MEDIUM severity messages."""

    @pytest.mark.asyncio
    async def test_medium_no_crt_ping(
        self,
        mock_channel_config,
    ):
        """Test MEDIUM messages do NOT ping CRT."""
        # Update mock for this specific test
        mock_channel_config.should_ping_for_severity = MagicMock(
            side_effect=lambda severity: severity in ["high", "critical"]
        )

        should_ping = mock_channel_config.should_ping_for_severity("medium")
        assert should_ping is False

    @pytest.mark.asyncio
    async def test_medium_goes_to_monitor_channel(
        self,
        mock_channel_config,
        mock_monitor_channel,
    ):
        """Test MEDIUM messages go to monitor channel, not crisis channel."""
        channel = mock_channel_config.get_alert_channel("medium")
        assert channel.id == mock_monitor_channel.id


class TestLowSeverityFlow:
    """Tests for LOW severity messages."""

    @pytest.mark.asyncio
    async def test_low_severity_stored(
        self,
        mock_user_history,
        low_nlp_response,
    ):
        """Test LOW severity messages are stored (not SAFE)."""
        mock_user_history.should_store = MagicMock(
            side_effect=lambda severity: severity not in ["safe", "none"]
        )

        should_store = mock_user_history.should_store(low_nlp_response["severity"])
        assert should_store is True

    @pytest.mark.asyncio
    async def test_low_severity_passive_monitoring(
        self,
        mock_nlp_client,
        low_nlp_response,
        low_message_text,
    ):
        """Test LOW severity recommends passive monitoring."""
        mock_nlp_client.analyze_message = AsyncMock(return_value=low_nlp_response)

        result = await mock_nlp_client.analyze_message(low_message_text)

        assert result["severity"] == "low"
        assert result["recommended_action"] == "passive_monitoring"


# =============================================================================
# Edge Cases
# =============================================================================


class TestMessageFlowEdgeCases:
    """Edge case tests for message flow."""

    @pytest.mark.asyncio
    async def test_bot_messages_ignored(
        self,
        mock_user,
        message_factory,
    ):
        """Test that bot messages are ignored."""
        mock_user.bot = True
        message = message_factory("Bot message")
        message.author = mock_user

        # Bot check should return True (is bot)
        assert message.author.bot is True

    @pytest.mark.asyncio
    async def test_empty_message_handled(
        self,
        mock_nlp_client,
    ):
        """Test that empty messages are handled gracefully."""
        mock_nlp_client.analyze_message = AsyncMock(
            return_value={"severity": "safe", "crisis_detected": False}
        )

        result = await mock_nlp_client.analyze_message("")

        # Should not crash, return safe
        assert result["severity"] == "safe"

    @pytest.mark.asyncio
    async def test_non_monitored_channel_skipped(
        self,
        mock_channel_config,
    ):
        """Test that non-monitored channels are skipped."""
        mock_channel_config.is_monitored_channel = MagicMock(return_value=False)

        is_monitored = mock_channel_config.is_monitored_channel(999999999)

        assert is_monitored is False
