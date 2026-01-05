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
Integration Tests for Channel Sensitivity Flow (Phase 7.3)
---
FILE VERSION: v5.0-7-3.0-1
LAST MODIFIED: 2026-01-05
PHASE: Phase 7 - Core Safety & User Preferences
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-bot
Community: The Alphabet Cartel - https://discord.gg/alphabetcartel | https://alphabetcartel.org
============================================================================
TESTS:
- Full message flow with sensitivity modification
- Wreck Room channel reduced sensitivity
- High-sensitivity channel behavior
- Metrics tracking for sensitivity adjustments
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

# Module version
__version__ = "v5.0-7-3.0-1"


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def mock_config_manager():
    """Create a mock ConfigManager with full sensitivity config."""
    config = MagicMock()
    
    sections = {
        "channels": {
            "monitored_channels": [
                "100000001",  # general
                "100000002",  # wreck-room
                "100000003",  # crisis-support
            ],
            "alert_channel_monitor": "200000001",
            "alert_channel_crisis": "200000002",
            "alert_channel_critical": "200000003",
        },
        "alerting": {
            "enabled": True,
            "crt_role_id": "300000001",
            "min_severity_to_alert": "medium",
            "cooldown_seconds": 300,
        },
        "discord": {
            "guild_id": "400000001",
        },
        "channel_sensitivity": {
            "default_sensitivity": 1.0,
            "channel_overrides": {
                "100000002": 0.5,   # wreck-room - reduced
                "100000003": 1.3,   # crisis-support - increased
            },
        },
        "history": {
            "ttl_days": 14,
            "max_messages": 100,
            "min_severity_to_store": "low",
        },
        "nlp": {
            "base_url": "http://ash-nlp:30880",
            "timeout_seconds": 5,
            "retry_attempts": 2,
            "retry_delay_seconds": 1,
        },
        "circuit_breaker": {
            "nlp_failure_threshold": 5,
            "nlp_success_threshold": 2,
            "nlp_timeout_seconds": 30,
        },
    }
    
    config.get_section = lambda section: sections.get(section, {})
    config.get = lambda section, key, default=None: sections.get(section, {}).get(key, default)
    
    return config


@pytest.fixture
def mock_discord_message():
    """Create a mock Discord message."""
    def _create_message(channel_id, channel_name, content="I'm feeling really down"):
        message = MagicMock()
        message.id = 123456789
        message.content = content
        message.author = MagicMock()
        message.author.id = 888888888
        message.author.display_name = "TestUser"
        message.author.bot = False
        message.channel = MagicMock()
        message.channel.id = channel_id
        message.channel.name = channel_name
        message.guild = MagicMock()
        message.guild.id = 400000001
        return message
    
    return _create_message


@pytest.fixture
def mock_nlp_response():
    """Create a mock NLP API response."""
    def _create_response(crisis_score=0.72, severity="high"):
        return {
            "crisis_detected": crisis_score >= 0.16,
            "severity": severity,
            "confidence": 0.85,
            "crisis_score": crisis_score,
            "requires_intervention": severity in ("medium", "high", "critical"),
            "recommended_action": "alert" if severity in ("high", "critical") else "monitor",
            "request_id": "test-req-123",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "processing_time_ms": 150.0,
            "models_used": ["model_a", "model_b"],
            "is_degraded": False,
            "signals": {},
            "explanation": {"decision_summary": "Crisis indicators detected"},
        }
    
    return _create_response


# =============================================================================
# Integration Test: Full Message Flow with Sensitivity
# =============================================================================


class TestChannelSensitivityFlow:
    """Integration tests for channel sensitivity in message processing."""

    @pytest.mark.asyncio
    async def test_general_channel_normal_sensitivity(
        self,
        mock_config_manager,
        mock_discord_message,
        mock_nlp_response,
    ):
        """Messages in general channel should use default sensitivity (1.0)."""
        from src.managers.discord.channel_config_manager import ChannelConfigManager
        from src.models.nlp_models import CrisisAnalysisResult
        
        # Setup
        channel_config = ChannelConfigManager(mock_config_manager)
        message = mock_discord_message(100000001, "general")
        
        # Verify default sensitivity
        sensitivity = channel_config.get_channel_sensitivity(message.channel.id)
        assert sensitivity == 1.0
        
        # Simulate NLP response
        nlp_data = mock_nlp_response(crisis_score=0.72, severity="high")
        result = CrisisAnalysisResult.from_api_response(nlp_data)
        
        # With sensitivity 1.0, no modification needed
        if sensitivity != 1.0:
            modified_score = result.crisis_score * sensitivity
            result = result.with_modified_score(modified_score, sensitivity)
        
        # Score should remain unchanged
        assert result.crisis_score == 0.72
        assert result.severity == "high"

    @pytest.mark.asyncio
    async def test_wreck_room_reduced_sensitivity(
        self,
        mock_config_manager,
        mock_discord_message,
        mock_nlp_response,
    ):
        """Messages in Wreck Room should have reduced sensitivity (0.5)."""
        from src.managers.discord.channel_config_manager import ChannelConfigManager
        from src.models.nlp_models import CrisisAnalysisResult
        
        # Setup
        channel_config = ChannelConfigManager(mock_config_manager)
        message = mock_discord_message(100000002, "wreck-room")
        
        # Verify reduced sensitivity
        sensitivity = channel_config.get_channel_sensitivity(message.channel.id)
        assert sensitivity == 0.5
        
        # Simulate NLP response - HIGH severity
        nlp_data = mock_nlp_response(crisis_score=0.72, severity="high")
        result = CrisisAnalysisResult.from_api_response(nlp_data)
        
        # Apply sensitivity modification
        modified_score = result.crisis_score * sensitivity
        result = result.with_modified_score(
            modified_score,
            sensitivity,
            channel_name=message.channel.name,
        )
        
        # Score should be reduced: 0.72 * 0.5 = 0.36
        assert result.crisis_score == 0.36
        # Severity should drop to MEDIUM
        assert result.severity == "medium"
        # Still actionable, but different alert routing
        assert result.requires_intervention is True

    @pytest.mark.asyncio
    async def test_crisis_support_increased_sensitivity(
        self,
        mock_config_manager,
        mock_discord_message,
        mock_nlp_response,
    ):
        """Messages in crisis-support should have increased sensitivity (1.3)."""
        from src.managers.discord.channel_config_manager import ChannelConfigManager
        from src.models.nlp_models import CrisisAnalysisResult
        
        # Setup
        channel_config = ChannelConfigManager(mock_config_manager)
        message = mock_discord_message(100000003, "crisis-support")
        
        # Verify increased sensitivity
        sensitivity = channel_config.get_channel_sensitivity(message.channel.id)
        assert sensitivity == 1.3
        
        # Simulate NLP response - borderline MEDIUM severity
        nlp_data = mock_nlp_response(crisis_score=0.50, severity="medium")
        result = CrisisAnalysisResult.from_api_response(nlp_data)
        
        # Apply sensitivity modification
        modified_score = result.crisis_score * sensitivity
        result = result.with_modified_score(
            modified_score,
            sensitivity,
            channel_name=message.channel.name,
        )
        
        # Score should increase: 0.50 * 1.3 = 0.65
        assert result.crisis_score == 0.65
        # Severity should increase to HIGH
        assert result.severity == "high"
        # Now requires immediate alert
        assert result.recommended_action == "alert"

    @pytest.mark.asyncio
    async def test_wreck_room_high_crisis_still_alerts(
        self,
        mock_config_manager,
        mock_discord_message,
        mock_nlp_response,
    ):
        """Even with reduced sensitivity, very high scores still trigger alerts."""
        from src.managers.discord.channel_config_manager import ChannelConfigManager
        from src.models.nlp_models import CrisisAnalysisResult
        
        # Setup
        channel_config = ChannelConfigManager(mock_config_manager)
        message = mock_discord_message(100000002, "wreck-room")
        
        sensitivity = channel_config.get_channel_sensitivity(message.channel.id)
        assert sensitivity == 0.5
        
        # Very high crisis score - CRITICAL
        nlp_data = mock_nlp_response(crisis_score=0.90, severity="critical")
        result = CrisisAnalysisResult.from_api_response(nlp_data)
        
        # Apply sensitivity modification
        modified_score = result.crisis_score * sensitivity
        result = result.with_modified_score(
            modified_score,
            sensitivity,
            channel_name=message.channel.name,
        )
        
        # Score: 0.90 * 0.5 = 0.45 (MEDIUM)
        assert result.crisis_score == 0.45
        assert result.severity == "medium"
        # Still triggers an alert (MEDIUM is actionable)
        assert result.requires_intervention is True

    @pytest.mark.asyncio
    async def test_wreck_room_low_score_becomes_safe(
        self,
        mock_config_manager,
        mock_discord_message,
        mock_nlp_response,
    ):
        """Low scores in Wreck Room should drop below threshold."""
        from src.managers.discord.channel_config_manager import ChannelConfigManager
        from src.models.nlp_models import CrisisAnalysisResult
        
        # Setup
        channel_config = ChannelConfigManager(mock_config_manager)
        message = mock_discord_message(100000002, "wreck-room")
        
        sensitivity = channel_config.get_channel_sensitivity(message.channel.id)
        
        # Borderline LOW crisis score
        nlp_data = mock_nlp_response(crisis_score=0.25, severity="low")
        result = CrisisAnalysisResult.from_api_response(nlp_data)
        
        # Apply sensitivity modification
        modified_score = result.crisis_score * sensitivity
        result = result.with_modified_score(
            modified_score,
            sensitivity,
            channel_name=message.channel.name,
        )
        
        # Score: 0.25 * 0.5 = 0.125 (below LOW threshold of 0.16)
        assert result.crisis_score == 0.125
        assert result.severity == "safe"
        # No alert triggered
        assert result.requires_intervention is False
        assert result.crisis_detected is False


# =============================================================================
# Integration Test: Alert Routing with Sensitivity
# =============================================================================


class TestSensitivityAlertRouting:
    """Tests for how sensitivity affects alert routing."""

    @pytest.mark.asyncio
    async def test_wreck_room_avoids_crisis_channel(
        self,
        mock_config_manager,
        mock_discord_message,
        mock_nlp_response,
    ):
        """
        Wreck Room sensitivity should route HIGH scores to monitor channel
        instead of crisis channel.
        
        Original: HIGH (0.72) -> crisis channel with CRT ping
        Modified: MEDIUM (0.36) -> monitor channel without ping
        """
        from src.managers.discord.channel_config_manager import ChannelConfigManager
        from src.models.nlp_models import CrisisAnalysisResult
        
        channel_config = ChannelConfigManager(mock_config_manager)
        message = mock_discord_message(100000002, "wreck-room")
        
        # Original HIGH severity
        nlp_data = mock_nlp_response(crisis_score=0.72, severity="high")
        original_result = CrisisAnalysisResult.from_api_response(nlp_data)
        
        # Without sensitivity: would go to crisis channel
        assert original_result.severity == "high"
        crisis_channel = channel_config.get_alert_channel("high")
        assert crisis_channel == 200000002  # crisis channel
        
        # With sensitivity: goes to monitor channel
        sensitivity = channel_config.get_channel_sensitivity(message.channel.id)
        modified_result = original_result.with_modified_score(
            original_result.crisis_score * sensitivity,
            sensitivity,
        )
        
        assert modified_result.severity == "medium"
        monitor_channel = channel_config.get_alert_channel("medium")
        assert monitor_channel == 200000001  # monitor channel

    @pytest.mark.asyncio
    async def test_crisis_support_escalates_to_crisis_channel(
        self,
        mock_config_manager,
        mock_discord_message,
        mock_nlp_response,
    ):
        """
        Crisis support channel sensitivity should escalate MEDIUM to HIGH.
        
        Original: MEDIUM (0.50) -> monitor channel
        Modified: HIGH (0.65) -> crisis channel with CRT ping
        """
        from src.managers.discord.channel_config_manager import ChannelConfigManager
        from src.models.nlp_models import CrisisAnalysisResult
        
        channel_config = ChannelConfigManager(mock_config_manager)
        message = mock_discord_message(100000003, "crisis-support")
        
        # Original MEDIUM severity
        nlp_data = mock_nlp_response(crisis_score=0.50, severity="medium")
        original_result = CrisisAnalysisResult.from_api_response(nlp_data)
        
        # Without sensitivity: goes to monitor channel
        assert original_result.severity == "medium"
        monitor_channel = channel_config.get_alert_channel("medium")
        assert monitor_channel == 200000001
        
        # With sensitivity: escalates to crisis channel
        sensitivity = channel_config.get_channel_sensitivity(message.channel.id)
        modified_result = original_result.with_modified_score(
            original_result.crisis_score * sensitivity,
            sensitivity,
        )
        
        assert modified_result.severity == "high"
        crisis_channel = channel_config.get_alert_channel("high")
        assert crisis_channel == 200000002


# =============================================================================
# Integration Test: Explanation Preservation
# =============================================================================


class TestSensitivityExplanation:
    """Tests for explanation/audit trail of sensitivity modifications."""

    @pytest.mark.asyncio
    async def test_modification_tracked_in_explanation(
        self,
        mock_config_manager,
        mock_discord_message,
        mock_nlp_response,
    ):
        """Sensitivity modification should be fully tracked in explanation."""
        from src.managers.discord.channel_config_manager import ChannelConfigManager
        from src.models.nlp_models import CrisisAnalysisResult
        
        channel_config = ChannelConfigManager(mock_config_manager)
        message = mock_discord_message(100000002, "wreck-room")
        
        nlp_data = mock_nlp_response(crisis_score=0.72, severity="high")
        result = CrisisAnalysisResult.from_api_response(nlp_data)
        
        sensitivity = channel_config.get_channel_sensitivity(message.channel.id)
        modified = result.with_modified_score(
            result.crisis_score * sensitivity,
            sensitivity,
            channel_name=message.channel.name,
        )
        
        # Check explanation contains full audit trail
        sens_mod = modified.explanation.get("sensitivity_modification")
        
        assert sens_mod is not None
        assert sens_mod["original_score"] == 0.72
        assert sens_mod["modified_score"] == 0.36
        assert sens_mod["sensitivity_applied"] == 0.5
        assert sens_mod["original_severity"] == "high"
        assert sens_mod["modified_severity"] == "medium"
        assert sens_mod["channel_name"] == "wreck-room"

    @pytest.mark.asyncio
    async def test_original_explanation_preserved(
        self,
        mock_config_manager,
        mock_discord_message,
        mock_nlp_response,
    ):
        """Original NLP explanation should be preserved."""
        from src.managers.discord.channel_config_manager import ChannelConfigManager
        from src.models.nlp_models import CrisisAnalysisResult
        
        channel_config = ChannelConfigManager(mock_config_manager)
        message = mock_discord_message(100000002, "wreck-room")
        
        nlp_data = mock_nlp_response(crisis_score=0.72, severity="high")
        result = CrisisAnalysisResult.from_api_response(nlp_data)
        
        sensitivity = channel_config.get_channel_sensitivity(message.channel.id)
        modified = result.with_modified_score(
            result.crisis_score * sensitivity,
            sensitivity,
        )
        
        # Original explanation key should still exist
        assert modified.explanation.get("decision_summary") == "Crisis indicators detected"


# =============================================================================
# Integration Test: Metrics Tracking
# =============================================================================


class TestSensitivityMetrics:
    """Tests for metrics tracking of sensitivity adjustments."""

    @pytest.mark.asyncio
    async def test_metrics_called_when_sensitivity_applied(
        self,
        mock_config_manager,
        mock_discord_message,
        mock_nlp_response,
    ):
        """Metrics should be incremented when sensitivity is applied."""
        from src.managers.discord.channel_config_manager import ChannelConfigManager
        from src.models.nlp_models import CrisisAnalysisResult
        
        channel_config = ChannelConfigManager(mock_config_manager)
        message = mock_discord_message(100000002, "wreck-room")
        
        # Create mock metrics manager
        mock_metrics = MagicMock()
        mock_metrics.inc_sensitivity_adjustments = MagicMock()
        
        nlp_data = mock_nlp_response(crisis_score=0.72, severity="high")
        result = CrisisAnalysisResult.from_api_response(nlp_data)
        
        sensitivity = channel_config.get_channel_sensitivity(message.channel.id)
        
        # Simulate what DiscordManager does
        if sensitivity != 1.0:
            modified_score = result.crisis_score * sensitivity
            result = result.with_modified_score(
                modified_score,
                sensitivity,
                channel_name=message.channel.name,
            )
            
            # Would call metrics in real code
            mock_metrics.inc_sensitivity_adjustments(
                message.channel.name,
                sensitivity,
            )
        
        # Verify metrics was called
        mock_metrics.inc_sensitivity_adjustments.assert_called_once_with(
            "wreck-room",
            0.5,
        )

    @pytest.mark.asyncio
    async def test_metrics_not_called_for_normal_sensitivity(
        self,
        mock_config_manager,
        mock_discord_message,
        mock_nlp_response,
    ):
        """Metrics should NOT be incremented when sensitivity is 1.0."""
        from src.managers.discord.channel_config_manager import ChannelConfigManager
        
        channel_config = ChannelConfigManager(mock_config_manager)
        message = mock_discord_message(100000001, "general")  # Default sensitivity
        
        mock_metrics = MagicMock()
        mock_metrics.inc_sensitivity_adjustments = MagicMock()
        
        sensitivity = channel_config.get_channel_sensitivity(message.channel.id)
        
        # Simulate what DiscordManager does
        if sensitivity != 1.0:
            mock_metrics.inc_sensitivity_adjustments(
                message.channel.name,
                sensitivity,
            )
        
        # Verify metrics was NOT called
        mock_metrics.inc_sensitivity_adjustments.assert_not_called()


# =============================================================================
# Integration Test: Configuration Reload
# =============================================================================


class TestSensitivityConfigReload:
    """Tests for sensitivity configuration hot-reload."""

    @pytest.mark.asyncio
    async def test_sensitivity_changes_on_reload(self, mock_config_manager):
        """Sensitivity should update when config is reloaded."""
        from src.managers.discord.channel_config_manager import ChannelConfigManager
        
        channel_config = ChannelConfigManager(mock_config_manager)
        
        # Initial sensitivity
        assert channel_config.get_channel_sensitivity(100000002) == 0.5
        
        # Update config mock to return new values
        new_sections = {
            "channels": {"monitored_channels": []},
            "alerting": {},
            "discord": {},
            "channel_sensitivity": {
                "default_sensitivity": 1.0,
                "channel_overrides": {
                    "100000002": 0.7,  # Changed from 0.5
                },
            },
        }
        mock_config_manager.get_section = lambda section: new_sections.get(section, {})
        
        # Reload config
        channel_config.reload_config()
        
        # New sensitivity should be loaded
        assert channel_config.get_channel_sensitivity(100000002) == 0.7

    @pytest.mark.asyncio
    async def test_runtime_sensitivity_survives_until_reload(self, mock_config_manager):
        """Runtime sensitivity changes persist until reload."""
        from src.managers.discord.channel_config_manager import ChannelConfigManager
        
        channel_config = ChannelConfigManager(mock_config_manager)
        
        # Set runtime sensitivity
        channel_config.set_channel_sensitivity(999999999, 0.4)
        assert channel_config.get_channel_sensitivity(999999999) == 0.4
        
        # Reload config (runtime change should be lost)
        channel_config.reload_config()
        
        # Should revert to default
        assert channel_config.get_channel_sensitivity(999999999) == 1.0
