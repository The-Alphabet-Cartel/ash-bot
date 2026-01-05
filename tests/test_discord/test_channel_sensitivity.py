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
Unit Tests for Channel Sensitivity (Phase 7.3)
---
FILE VERSION: v5.0-7-3.0-1
LAST MODIFIED: 2026-01-05
PHASE: Phase 7 - Core Safety & User Preferences
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-bot
Community: The Alphabet Cartel - https://discord.gg/alphabetcartel | https://alphabetcartel.org
============================================================================
TESTS:
- ChannelConfigManager sensitivity methods
- CrisisAnalysisResult.with_modified_score()
- SeverityLevel.from_score()
- Score modification logic
"""

import pytest
from unittest.mock import MagicMock, patch

# Module version
__version__ = "v5.0-7-3.0-1"


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def mock_config_manager():
    """Create a mock ConfigManager with channel sensitivity config."""
    config = MagicMock()
    
    # Define sections
    sections = {
        "channels": {
            "monitored_channels": ["123456789", "987654321"],
            "alert_channel_monitor": "111111111",
            "alert_channel_crisis": "222222222",
            "alert_channel_critical": "333333333",
        },
        "alerting": {
            "crt_role_id": "444444444",
        },
        "discord": {
            "guild_id": "555555555",
        },
        "channel_sensitivity": {
            "default_sensitivity": 1.0,
            "channel_overrides": {
                "123456789": 0.5,  # Wreck Room - reduced sensitivity
                "987654321": 1.5,  # High-risk channel - increased sensitivity
            },
        },
    }
    
    config.get_section = lambda section: sections.get(section, {})
    config.get = lambda section, key, default=None: sections.get(section, {}).get(key, default)
    
    return config


@pytest.fixture
def channel_config(mock_config_manager):
    """Create ChannelConfigManager with sensitivity config."""
    from src.managers.discord.channel_config_manager import ChannelConfigManager
    return ChannelConfigManager(mock_config_manager)


@pytest.fixture
def sample_analysis_result():
    """Create a sample CrisisAnalysisResult for testing."""
    from src.models.nlp_models import CrisisAnalysisResult
    
    return CrisisAnalysisResult(
        crisis_detected=True,
        severity="high",
        confidence=0.85,
        crisis_score=0.72,
        requires_intervention=True,
        recommended_action="alert",
        request_id="test-123",
        timestamp="2026-01-05T12:00:00Z",
        processing_time_ms=150.5,
        models_used=["model_a", "model_b"],
        is_degraded=False,
        signals={},
        explanation={"decision_summary": "Test explanation"},
    )


# =============================================================================
# SeverityLevel.from_score() Tests
# =============================================================================


class TestSeverityLevelFromScore:
    """Tests for SeverityLevel.from_score() method."""

    def test_critical_threshold(self):
        """Score >= 0.85 should return CRITICAL."""
        from src.models.nlp_models import SeverityLevel
        
        assert SeverityLevel.from_score(0.85) == "critical"
        assert SeverityLevel.from_score(0.90) == "critical"
        assert SeverityLevel.from_score(1.0) == "critical"

    def test_high_threshold(self):
        """Score >= 0.55 and < 0.85 should return HIGH."""
        from src.models.nlp_models import SeverityLevel
        
        assert SeverityLevel.from_score(0.55) == "high"
        assert SeverityLevel.from_score(0.70) == "high"
        assert SeverityLevel.from_score(0.84) == "high"

    def test_medium_threshold(self):
        """Score >= 0.28 and < 0.55 should return MEDIUM."""
        from src.models.nlp_models import SeverityLevel
        
        assert SeverityLevel.from_score(0.28) == "medium"
        assert SeverityLevel.from_score(0.40) == "medium"
        assert SeverityLevel.from_score(0.54) == "medium"

    def test_low_threshold(self):
        """Score >= 0.16 and < 0.28 should return LOW."""
        from src.models.nlp_models import SeverityLevel
        
        assert SeverityLevel.from_score(0.16) == "low"
        assert SeverityLevel.from_score(0.20) == "low"
        assert SeverityLevel.from_score(0.27) == "low"

    def test_safe_threshold(self):
        """Score < 0.16 should return SAFE."""
        from src.models.nlp_models import SeverityLevel
        
        assert SeverityLevel.from_score(0.0) == "safe"
        assert SeverityLevel.from_score(0.10) == "safe"
        assert SeverityLevel.from_score(0.15) == "safe"


# =============================================================================
# ChannelConfigManager Sensitivity Tests
# =============================================================================


class TestChannelSensitivityConfig:
    """Tests for ChannelConfigManager sensitivity methods."""

    def test_default_sensitivity_loaded(self, channel_config):
        """Default sensitivity should be loaded from config."""
        assert channel_config.default_sensitivity == 1.0

    def test_channel_override_loaded(self, channel_config):
        """Channel sensitivity overrides should be loaded."""
        # Wreck Room - reduced sensitivity
        assert channel_config.get_channel_sensitivity(123456789) == 0.5
        
        # High-risk channel - increased sensitivity
        assert channel_config.get_channel_sensitivity(987654321) == 1.5

    def test_unconfigured_channel_uses_default(self, channel_config):
        """Channels without override should use default."""
        unknown_channel = 999999999
        assert channel_config.get_channel_sensitivity(unknown_channel) == 1.0

    def test_set_channel_sensitivity_valid(self, channel_config):
        """Valid sensitivity can be set at runtime."""
        new_channel = 777777777
        
        result = channel_config.set_channel_sensitivity(new_channel, 0.7)
        
        assert result is True
        assert channel_config.get_channel_sensitivity(new_channel) == 0.7

    def test_set_channel_sensitivity_out_of_range_low(self, channel_config):
        """Sensitivity below 0.3 should be rejected."""
        result = channel_config.set_channel_sensitivity(888888888, 0.1)
        
        assert result is False
        # Should still use default
        assert channel_config.get_channel_sensitivity(888888888) == 1.0

    def test_set_channel_sensitivity_out_of_range_high(self, channel_config):
        """Sensitivity above 2.0 should be rejected."""
        result = channel_config.set_channel_sensitivity(888888888, 2.5)
        
        assert result is False
        assert channel_config.get_channel_sensitivity(888888888) == 1.0

    def test_remove_channel_sensitivity(self, channel_config):
        """Custom sensitivity can be removed, reverting to default."""
        # First set a custom value
        channel_config.set_channel_sensitivity(666666666, 0.6)
        assert channel_config.get_channel_sensitivity(666666666) == 0.6
        
        # Remove it
        result = channel_config.remove_channel_sensitivity(666666666)
        
        assert result is True
        assert channel_config.get_channel_sensitivity(666666666) == 1.0  # Default

    def test_remove_nonexistent_sensitivity(self, channel_config):
        """Removing sensitivity from unconfigured channel returns False."""
        result = channel_config.remove_channel_sensitivity(999999999)
        assert result is False

    def test_get_all_sensitivities(self, channel_config):
        """get_all_channel_sensitivities returns all overrides."""
        all_sens = channel_config.get_all_channel_sensitivities()
        
        assert 123456789 in all_sens
        assert 987654321 in all_sens
        assert all_sens[123456789] == 0.5
        assert all_sens[987654321] == 1.5

    def test_sensitivity_override_count(self, channel_config):
        """sensitivity_override_count property works."""
        assert channel_config.sensitivity_override_count == 2

    def test_status_includes_sensitivity(self, channel_config):
        """get_status() includes sensitivity info."""
        status = channel_config.get_status()
        
        assert "default_sensitivity" in status
        assert status["default_sensitivity"] == 1.0
        assert "sensitivity_overrides" in status
        assert status["sensitivity_overrides"] == 2


# =============================================================================
# CrisisAnalysisResult.with_modified_score() Tests
# =============================================================================


class TestWithModifiedScore:
    """Tests for CrisisAnalysisResult.with_modified_score() method."""

    def test_score_modified_correctly(self, sample_analysis_result):
        """Crisis score should be modified by sensitivity."""
        # Original score: 0.72
        # Sensitivity: 0.5
        # Expected: 0.72 * 0.5 = 0.36
        
        modified = sample_analysis_result.with_modified_score(
            modified_score=0.36,
            sensitivity=0.5,
            channel_name="wreck-room",
        )
        
        assert modified.crisis_score == 0.36

    def test_severity_recalculated(self, sample_analysis_result):
        """Severity should be recalculated based on new score."""
        # Original: HIGH (0.72)
        # Modified: 0.36 -> MEDIUM (0.28-0.55)
        
        modified = sample_analysis_result.with_modified_score(
            modified_score=0.36,
            sensitivity=0.5,
        )
        
        assert modified.severity == "medium"

    def test_score_capped_at_one(self, sample_analysis_result):
        """Modified score should be capped at 1.0."""
        # Sensitivity > 1.0 could push score over 1.0
        # 0.72 * 1.5 = 1.08 -> should cap at 1.0
        
        modified = sample_analysis_result.with_modified_score(
            modified_score=1.08,
            sensitivity=1.5,
        )
        
        assert modified.crisis_score == 1.0

    def test_score_floored_at_zero(self, sample_analysis_result):
        """Modified score should not go below 0."""
        modified = sample_analysis_result.with_modified_score(
            modified_score=-0.5,
            sensitivity=0.3,
        )
        
        assert modified.crisis_score == 0.0

    def test_original_data_preserved(self, sample_analysis_result):
        """Original explanation should contain sensitivity modification info."""
        modified = sample_analysis_result.with_modified_score(
            modified_score=0.36,
            sensitivity=0.5,
            channel_name="wreck-room",
        )
        
        sens_mod = modified.explanation.get("sensitivity_modification")
        assert sens_mod is not None
        assert sens_mod["original_score"] == 0.72
        assert sens_mod["modified_score"] == 0.36
        assert sens_mod["sensitivity_applied"] == 0.5
        assert sens_mod["original_severity"] == "high"
        assert sens_mod["modified_severity"] == "medium"
        assert sens_mod["channel_name"] == "wreck-room"

    def test_requires_intervention_updated(self, sample_analysis_result):
        """requires_intervention should be updated based on new severity."""
        # Original: HIGH -> requires_intervention=True
        # Modified: SAFE -> requires_intervention=False
        
        modified = sample_analysis_result.with_modified_score(
            modified_score=0.10,
            sensitivity=0.3,
        )
        
        assert modified.severity == "safe"
        assert modified.requires_intervention is False

    def test_recommended_action_updated(self, sample_analysis_result):
        """recommended_action should be updated based on new severity."""
        # Original: HIGH -> alert
        # Modified: SAFE -> none
        
        modified = sample_analysis_result.with_modified_score(
            modified_score=0.10,
            sensitivity=0.3,
        )
        
        assert modified.recommended_action == "none"

    def test_crisis_detected_updated(self, sample_analysis_result):
        """crisis_detected should be updated based on new score."""
        # If score drops below LOW threshold (0.16), crisis_detected=False
        
        modified = sample_analysis_result.with_modified_score(
            modified_score=0.10,
            sensitivity=0.3,
        )
        
        assert modified.crisis_detected is False

    def test_immutable_original_not_modified(self, sample_analysis_result):
        """Original result should not be modified."""
        original_score = sample_analysis_result.crisis_score
        original_severity = sample_analysis_result.severity
        
        modified = sample_analysis_result.with_modified_score(
            modified_score=0.36,
            sensitivity=0.5,
        )
        
        # Original unchanged
        assert sample_analysis_result.crisis_score == original_score
        assert sample_analysis_result.severity == original_severity
        
        # Modified is different
        assert modified.crisis_score != original_score
        assert modified.severity != original_severity


# =============================================================================
# Score Modification Scenarios
# =============================================================================


class TestSensitivityScenarios:
    """Tests for real-world sensitivity scenarios."""

    def test_wreck_room_reduces_high_to_medium(self, sample_analysis_result):
        """Wreck Room (0.5 sensitivity) should reduce HIGH to MEDIUM."""
        # Score: 0.72 (HIGH) * 0.5 = 0.36 (MEDIUM)
        
        modified = sample_analysis_result.with_modified_score(
            modified_score=0.72 * 0.5,
            sensitivity=0.5,
            channel_name="wreck-room",
        )
        
        assert modified.severity == "medium"
        assert modified.requires_intervention is True  # MEDIUM still actionable

    def test_wreck_room_reduces_medium_to_low(self):
        """Wreck Room should reduce borderline MEDIUM to LOW."""
        from src.models.nlp_models import CrisisAnalysisResult
        
        result = CrisisAnalysisResult(
            crisis_detected=True,
            severity="medium",
            confidence=0.7,
            crisis_score=0.40,  # MEDIUM
            requires_intervention=True,
            recommended_action="monitor",
            request_id="test-456",
            timestamp="2026-01-05T12:00:00Z",
            processing_time_ms=100.0,
            models_used=["model_a"],
            is_degraded=False,
        )
        
        # 0.40 * 0.5 = 0.20 (LOW)
        modified = result.with_modified_score(
            modified_score=0.40 * 0.5,
            sensitivity=0.5,
        )
        
        assert modified.severity == "low"
        assert modified.requires_intervention is False  # LOW not actionable

    def test_high_sensitivity_elevates_medium_to_high(self):
        """High-sensitivity channel (1.5) should elevate MEDIUM to HIGH."""
        from src.models.nlp_models import CrisisAnalysisResult
        
        result = CrisisAnalysisResult(
            crisis_detected=True,
            severity="medium",
            confidence=0.7,
            crisis_score=0.40,  # MEDIUM
            requires_intervention=True,
            recommended_action="monitor",
            request_id="test-789",
            timestamp="2026-01-05T12:00:00Z",
            processing_time_ms=100.0,
            models_used=["model_a"],
            is_degraded=False,
        )
        
        # 0.40 * 1.5 = 0.60 (HIGH)
        modified = result.with_modified_score(
            modified_score=0.40 * 1.5,
            sensitivity=1.5,
        )
        
        assert modified.severity == "high"
        assert modified.recommended_action == "alert"

    def test_normal_sensitivity_unchanged(self, sample_analysis_result):
        """Sensitivity 1.0 should not change the score."""
        # Score: 0.72 * 1.0 = 0.72 (unchanged)
        
        modified = sample_analysis_result.with_modified_score(
            modified_score=0.72 * 1.0,
            sensitivity=1.0,
        )
        
        assert modified.crisis_score == 0.72
        assert modified.severity == "high"

    def test_sensitivity_affects_alert_routing(self, sample_analysis_result):
        """Sensitivity modification should affect alert routing decisions."""
        # HIGH alerts go to crisis channel with CRT ping
        # MEDIUM alerts go to monitor channel without ping
        
        # Original: HIGH -> would go to crisis channel
        assert sample_analysis_result.severity == "high"
        
        # Modified: MEDIUM -> would go to monitor channel
        modified = sample_analysis_result.with_modified_score(
            modified_score=0.72 * 0.5,
            sensitivity=0.5,
        )
        
        assert modified.severity == "medium"
        # In real use, AlertDispatcher would route to different channel


# =============================================================================
# Edge Cases
# =============================================================================


class TestSensitivityEdgeCases:
    """Tests for edge cases in sensitivity handling."""

    def test_minimum_sensitivity(self, sample_analysis_result):
        """Minimum sensitivity (0.3) should work correctly."""
        # 0.72 * 0.3 = 0.216 (LOW)
        
        modified = sample_analysis_result.with_modified_score(
            modified_score=0.72 * 0.3,
            sensitivity=0.3,
        )
        
        assert 0.21 <= modified.crisis_score <= 0.22
        assert modified.severity == "low"

    def test_maximum_sensitivity(self, sample_analysis_result):
        """Maximum sensitivity (2.0) should cap score at 1.0."""
        # 0.72 * 2.0 = 1.44 -> capped to 1.0 (CRITICAL)
        
        modified = sample_analysis_result.with_modified_score(
            modified_score=0.72 * 2.0,
            sensitivity=2.0,
        )
        
        assert modified.crisis_score == 1.0
        assert modified.severity == "critical"

    def test_zero_score_remains_zero(self):
        """Zero score should remain zero regardless of sensitivity."""
        from src.models.nlp_models import CrisisAnalysisResult
        
        result = CrisisAnalysisResult(
            crisis_detected=False,
            severity="safe",
            confidence=0.9,
            crisis_score=0.0,
            requires_intervention=False,
            recommended_action="none",
            request_id="test-000",
            timestamp="2026-01-05T12:00:00Z",
            processing_time_ms=100.0,
            models_used=["model_a"],
            is_degraded=False,
        )
        
        modified = result.with_modified_score(
            modified_score=0.0 * 2.0,
            sensitivity=2.0,
        )
        
        assert modified.crisis_score == 0.0
        assert modified.severity == "safe"

    def test_explanation_preserved_when_none(self):
        """Explanation should be created even if original is None."""
        from src.models.nlp_models import CrisisAnalysisResult
        
        result = CrisisAnalysisResult(
            crisis_detected=True,
            severity="high",
            confidence=0.8,
            crisis_score=0.72,
            requires_intervention=True,
            recommended_action="alert",
            request_id="test-noexp",
            timestamp="2026-01-05T12:00:00Z",
            processing_time_ms=100.0,
            models_used=["model_a"],
            is_degraded=False,
            explanation=None,  # No original explanation
        )
        
        modified = result.with_modified_score(
            modified_score=0.36,
            sensitivity=0.5,
        )
        
        assert modified.explanation is not None
        assert "sensitivity_modification" in modified.explanation


# =============================================================================
# Default Sensitivity Validation
# =============================================================================


class TestDefaultSensitivityValidation:
    """Tests for default sensitivity validation during config load."""

    def test_default_sensitivity_out_of_range_low(self):
        """Default sensitivity below 0.3 should fallback to 1.0."""
        from src.managers.discord.channel_config_manager import ChannelConfigManager
        
        config = MagicMock()
        config.get_section = lambda section: {
            "channels": {},
            "alerting": {},
            "discord": {},
            "channel_sensitivity": {
                "default_sensitivity": 0.1,  # Too low
                "channel_overrides": {},
            },
        }.get(section, {})
        
        manager = ChannelConfigManager(config)
        
        # Should fallback to 1.0
        assert manager.default_sensitivity == 1.0

    def test_default_sensitivity_out_of_range_high(self):
        """Default sensitivity above 2.0 should fallback to 1.0."""
        from src.managers.discord.channel_config_manager import ChannelConfigManager
        
        config = MagicMock()
        config.get_section = lambda section: {
            "channels": {},
            "alerting": {},
            "discord": {},
            "channel_sensitivity": {
                "default_sensitivity": 3.0,  # Too high
                "channel_overrides": {},
            },
        }.get(section, {})
        
        manager = ChannelConfigManager(config)
        
        # Should fallback to 1.0
        assert manager.default_sensitivity == 1.0

    def test_channel_override_out_of_range_ignored(self):
        """Channel override out of range should be ignored."""
        from src.managers.discord.channel_config_manager import ChannelConfigManager
        
        config = MagicMock()
        config.get_section = lambda section: {
            "channels": {},
            "alerting": {},
            "discord": {},
            "channel_sensitivity": {
                "default_sensitivity": 1.0,
                "channel_overrides": {
                    "123456789": 0.1,  # Too low - should be ignored
                    "987654321": 0.5,  # Valid
                },
            },
        }.get(section, {})
        
        manager = ChannelConfigManager(config)
        
        # Invalid override should not be loaded
        assert 123456789 not in manager.get_all_channel_sensitivities()
        # Valid override should be loaded
        assert manager.get_channel_sensitivity(987654321) == 0.5
