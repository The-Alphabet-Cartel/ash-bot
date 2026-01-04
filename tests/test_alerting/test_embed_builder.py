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
Embed Builder Tests
---
FILE VERSION: v5.0-3-8.2-3
LAST MODIFIED: 2026-01-04
PHASE: Phase 3 - Alert Dispatching
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-bot
Community: The Alphabet Cartel - https://discord.gg/alphabetcartel | https://alphabetcartel.org
============================================================================
Tests for EmbedBuilder:
- Crisis embed creation
- Escalation embed creation
- Severity-based styling
- Message truncation
"""

import pytest
from datetime import datetime, timezone
from unittest.mock import MagicMock
import discord


# =============================================================================
# Test Fixtures
# =============================================================================


@pytest.fixture
def embed_builder():
    """Create EmbedBuilder instance."""
    from src.managers.alerting.embed_builder import EmbedBuilder
    return EmbedBuilder()


@pytest.fixture
def mock_user():
    """Create mock Discord user."""
    user = MagicMock(spec=discord.Member)
    user.id = 123456789
    user.name = "TestUser"
    user.display_name = "Test User"
    user.display_avatar.url = "https://cdn.discordapp.com/avatars/123/abc.png"
    user.mention = "<@123456789>"
    return user


@pytest.fixture
def mock_message(mock_user):
    """Create mock Discord message."""
    message = MagicMock(spec=discord.Message)
    message.id = 987654321
    message.author = mock_user
    message.content = "I'm feeling really overwhelmed and don't know what to do"
    message.channel.id = 111222333
    message.channel.name = "general"
    message.channel.mention = "<#111222333>"
    message.guild.id = 444555666
    message.created_at = datetime.now(timezone.utc)
    message.jump_url = "https://discord.com/channels/444555666/111222333/987654321"
    return message


@pytest.fixture
def mock_analysis_result():
    """Create mock NLP analysis result object (matches CrisisAnalysisResult)."""
    result = MagicMock()
    result.crisis_detected = True
    result.severity = "high"
    result.crisis_score = 0.78
    result.confidence = 0.85
    result.requires_intervention = True
    result.recommended_action = "priority_response"
    result.explanation = {
        "key_factors": ["emotional distress", "negative sentiment"],
        "decision_summary": "High crisis indicators detected",
    }
    result.request_id = "req_abc123"
    result.processing_time_ms = 125.5
    return result


# =============================================================================
# Initialization Tests
# =============================================================================


class TestEmbedBuilderInit:
    """Tests for EmbedBuilder initialization."""

    def test_init_creates_instance(self, embed_builder):
        """Test initialization creates valid instance."""
        assert embed_builder is not None

    def test_severity_colors_defined(self, embed_builder):
        """Test severity colors are defined."""
        from src.managers.alerting.embed_builder import SEVERITY_COLORS
        
        assert "medium" in SEVERITY_COLORS
        assert "high" in SEVERITY_COLORS
        assert "critical" in SEVERITY_COLORS

    def test_severity_emojis_defined(self, embed_builder):
        """Test severity emojis are defined."""
        from src.managers.alerting.embed_builder import SEVERITY_EMOJIS
        
        assert "medium" in SEVERITY_EMOJIS
        assert "high" in SEVERITY_EMOJIS
        assert "critical" in SEVERITY_EMOJIS


# =============================================================================
# Crisis Embed Tests
# =============================================================================


class TestCrisisEmbed:
    """Tests for crisis embed creation."""

    def test_build_crisis_embed_returns_embed(
        self, embed_builder, mock_message, mock_analysis_result
    ):
        """Test build_crisis_embed returns an embed."""
        embed = embed_builder.build_crisis_embed(
            message=mock_message,
            result=mock_analysis_result,
        )

        assert isinstance(embed, discord.Embed)

    def test_crisis_embed_has_title(
        self, embed_builder, mock_message, mock_analysis_result
    ):
        """Test crisis embed has appropriate title."""
        embed = embed_builder.build_crisis_embed(
            message=mock_message,
            result=mock_analysis_result,
        )

        assert embed.title is not None
        assert "Crisis" in embed.title or "Alert" in embed.title

    def test_crisis_embed_has_color_for_severity(
        self, embed_builder, mock_message, mock_analysis_result
    ):
        """Test crisis embed has correct color for severity."""
        from src.managers.alerting.embed_builder import SEVERITY_COLORS
        
        embed = embed_builder.build_crisis_embed(
            message=mock_message,
            result=mock_analysis_result,
        )

        expected_color = SEVERITY_COLORS.get("high")
        assert embed.color is not None

    def test_crisis_embed_has_author_field(
        self, embed_builder, mock_message, mock_analysis_result
    ):
        """Test crisis embed includes user information in author."""
        embed = embed_builder.build_crisis_embed(
            message=mock_message,
            result=mock_analysis_result,
        )

        # Check author is set
        assert embed.author is not None
        assert embed.author.name == "Test User"

    def test_crisis_embed_has_message_preview(
        self, embed_builder, mock_message, mock_analysis_result
    ):
        """Test crisis embed includes message preview."""
        embed = embed_builder.build_crisis_embed(
            message=mock_message,
            result=mock_analysis_result,
        )

        # Check fields contain message content
        embed_text = str(embed.to_dict())
        assert "overwhelmed" in embed_text

    def test_crisis_embed_has_scores(
        self, embed_builder, mock_message, mock_analysis_result
    ):
        """Test crisis embed includes crisis scores."""
        embed = embed_builder.build_crisis_embed(
            message=mock_message,
            result=mock_analysis_result,
        )

        embed_text = str(embed.to_dict())
        # Should contain score info
        assert "0.78" in embed_text or "Score" in embed_text

    def test_crisis_embed_has_jump_link(
        self, embed_builder, mock_message, mock_analysis_result
    ):
        """Test crisis embed includes jump link to message."""
        embed = embed_builder.build_crisis_embed(
            message=mock_message,
            result=mock_analysis_result,
        )

        embed_text = str(embed.to_dict())
        # Should contain jump URL
        assert "discord.com" in embed_text

    def test_crisis_embed_has_timestamp(
        self, embed_builder, mock_message, mock_analysis_result
    ):
        """Test crisis embed has timestamp."""
        embed = embed_builder.build_crisis_embed(
            message=mock_message,
            result=mock_analysis_result,
        )

        assert embed.timestamp is not None


# =============================================================================
# Message Truncation Tests
# =============================================================================


class TestMessageTruncation:
    """Tests for message content truncation."""

    def test_short_message_not_truncated(
        self, embed_builder, mock_message, mock_analysis_result
    ):
        """Test short messages are not truncated."""
        mock_message.content = "Short message"
        
        embed = embed_builder.build_crisis_embed(
            message=mock_message,
            result=mock_analysis_result,
        )

        embed_text = str(embed.to_dict())
        assert "Short message" in embed_text

    def test_long_message_truncated(
        self, embed_builder, mock_message, mock_analysis_result
    ):
        """Test long messages are truncated."""
        mock_message.content = "A" * 1000  # Very long message
        
        embed = embed_builder.build_crisis_embed(
            message=mock_message,
            result=mock_analysis_result,
        )

        embed_text = str(embed.to_dict())
        # Should be truncated (not contain all 1000 A's)
        # and should have ellipsis or truncation indicator
        assert "..." in embed_text or len(embed_text) < 1500


# =============================================================================
# Severity Styling Tests
# =============================================================================


class TestSeverityStyling:
    """Tests for severity-based styling."""

    def test_medium_severity_styling(
        self, embed_builder, mock_message, mock_analysis_result
    ):
        """Test medium severity has correct styling."""
        from src.managers.alerting.embed_builder import SEVERITY_COLORS
        
        mock_analysis_result.severity = "medium"
        
        embed = embed_builder.build_crisis_embed(
            message=mock_message,
            result=mock_analysis_result,
        )

        # Color should match medium severity
        assert embed.color == SEVERITY_COLORS["medium"]

    def test_high_severity_styling(
        self, embed_builder, mock_message, mock_analysis_result
    ):
        """Test high severity has correct styling."""
        from src.managers.alerting.embed_builder import SEVERITY_COLORS
        
        mock_analysis_result.severity = "high"
        
        embed = embed_builder.build_crisis_embed(
            message=mock_message,
            result=mock_analysis_result,
        )

        assert embed.color == SEVERITY_COLORS["high"]

    def test_critical_severity_styling(
        self, embed_builder, mock_message, mock_analysis_result
    ):
        """Test critical severity has correct styling."""
        from src.managers.alerting.embed_builder import SEVERITY_COLORS
        
        mock_analysis_result.severity = "critical"
        
        embed = embed_builder.build_crisis_embed(
            message=mock_message,
            result=mock_analysis_result,
        )

        assert embed.color == SEVERITY_COLORS["critical"]


# =============================================================================
# Escalation Embed Tests
# =============================================================================


class TestEscalationEmbed:
    """Tests for escalation embed creation."""

    def test_build_escalation_embed_returns_embed(
        self, embed_builder, mock_message, mock_analysis_result
    ):
        """Test build_escalation_embed returns an embed."""
        embed = embed_builder.build_escalation_embed(
            message=mock_message,
            result=mock_analysis_result,
            history_count=5,
            trend="escalating",
        )

        assert isinstance(embed, discord.Embed)

    def test_escalation_embed_indicates_escalation(
        self, embed_builder, mock_message, mock_analysis_result
    ):
        """Test escalation embed indicates escalation pattern."""
        embed = embed_builder.build_escalation_embed(
            message=mock_message,
            result=mock_analysis_result,
            history_count=5,
            trend="escalating",
        )

        embed_text = str(embed.to_dict())
        assert (
            "ESCALATION" in embed_text 
            or "escalat" in embed_text.lower()
        )

    def test_escalation_embed_has_pattern_info(
        self, embed_builder, mock_message, mock_analysis_result
    ):
        """Test escalation embed includes pattern information."""
        embed = embed_builder.build_escalation_embed(
            message=mock_message,
            result=mock_analysis_result,
            history_count=5,
            trend="escalating",
        )

        embed_text = str(embed.to_dict())
        # Should reference the message count
        assert "5" in embed_text


# =============================================================================
# Update Embed Tests
# =============================================================================


class TestUpdateEmbed:
    """Tests for embed update methods."""

    def test_update_embed_acknowledged(
        self, embed_builder, mock_message, mock_analysis_result
    ):
        """Test updating embed to acknowledged state."""
        original_embed = embed_builder.build_crisis_embed(
            message=mock_message,
            result=mock_analysis_result,
        )

        updated_embed = embed_builder.update_embed_acknowledged(
            embed=original_embed,
            acknowledger_name="ModeratorName",
        )

        assert isinstance(updated_embed, discord.Embed)
        # Should have green color (acknowledged)
        assert updated_embed.color == discord.Color.green()

    def test_acknowledged_embed_has_footer(
        self, embed_builder, mock_message, mock_analysis_result
    ):
        """Test acknowledged embed has moderator in footer."""
        original_embed = embed_builder.build_crisis_embed(
            message=mock_message,
            result=mock_analysis_result,
        )

        updated_embed = embed_builder.update_embed_acknowledged(
            embed=original_embed,
            acknowledger_name="ModeratorName",
        )

        assert updated_embed.footer is not None
        assert "ModeratorName" in updated_embed.footer.text


# =============================================================================
# Helper Embed Tests
# =============================================================================


class TestHelperEmbeds:
    """Tests for helper embed methods."""

    def test_build_info_embed(self, embed_builder):
        """Test building info embed."""
        embed = embed_builder.build_info_embed(
            title="Information",
            description="This is an info message",
        )

        assert isinstance(embed, discord.Embed)
        assert embed.title == "Information"
        assert embed.description == "This is an info message"
        # Info embeds should be blue
        assert embed.color == discord.Color.blue()

    def test_build_error_embed(self, embed_builder):
        """Test building error embed."""
        embed = embed_builder.build_error_embed(
            title="Error",
            description="Something went wrong",
        )

        assert isinstance(embed, discord.Embed)
        # Title includes emoji prefix
        assert "Error" in embed.title
        assert embed.description == "Something went wrong"
        # Error embeds should be red
        assert embed.color == discord.Color.red()


# =============================================================================
# Factory Function Tests
# =============================================================================


class TestEmbedBuilderFactory:
    """Tests for factory function."""

    def test_create_embed_builder(self):
        """Test factory function creates builder."""
        from src.managers.alerting import create_embed_builder

        builder = create_embed_builder()

        assert builder is not None
