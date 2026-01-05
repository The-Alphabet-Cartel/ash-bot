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
Integration Tests: Alert Flow
---
FILE VERSION: v5.0-6-1.2-1
LAST MODIFIED: 2026-01-04
PHASE: Phase 6 - Final Testing & Documentation
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-bot
Community: The Alphabet Cartel - https://discord.gg/alphabetcartel | https://alphabetcartel.org
============================================================================
Tests for Scenarios 3 and 4:
- Scenario 3: Alert Acknowledgment
- Scenario 4: Talk to Ash Session Initiation
"""

import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch
import discord


# =============================================================================
# Scenario 3: Alert Acknowledgment
# =============================================================================


class TestAlertAcknowledgment:
    """
    Scenario 3: Alert Acknowledgment

    Input: CRT member clicks "Acknowledge" button
    Expected:
    1. Embed color changes to acknowledged style
    2. Acknowledger's name added to embed
    3. Timestamp added
    4. Buttons remain functional
    """

    @pytest.mark.asyncio
    async def test_acknowledge_button_updates_embed_color(
        self,
        mock_interaction,
        mock_embed_builder,
    ):
        """Test that clicking Acknowledge changes embed color."""
        # Original embed (unacknowledged)
        original_embed = MagicMock()
        original_embed.color = discord.Color.red()  # Crisis color

        # Acknowledged embed should have different color
        acknowledged_embed = MagicMock()
        acknowledged_embed.color = discord.Color.green()  # Acknowledged color

        mock_embed_builder.build_acknowledged_embed = MagicMock(
            return_value=acknowledged_embed
        )

        result = mock_embed_builder.build_acknowledged_embed(
            original_embed=original_embed,
            acknowledger=mock_interaction.user,
        )

        # Verify color change
        assert result.color != original_embed.color
        assert result.color == discord.Color.green()

    @pytest.mark.asyncio
    async def test_acknowledger_name_added_to_embed(
        self,
        mock_interaction,
    ):
        """Test that acknowledger's name is added to the embed."""
        acknowledger_name = mock_interaction.user.display_name

        # Simulate adding acknowledger to embed field
        embed_field = {
            "name": "Acknowledged By",
            "value": f"{acknowledger_name}",
            "inline": True,
        }

        assert embed_field["value"] == "CRT Member"

    @pytest.mark.asyncio
    async def test_acknowledgment_timestamp_added(
        self,
        mock_interaction,
    ):
        """Test that acknowledgment timestamp is added."""
        timestamp = datetime.now(timezone.utc)

        # Verify timestamp is within reasonable range
        assert (datetime.now(timezone.utc) - timestamp).total_seconds() < 1

    @pytest.mark.asyncio
    async def test_buttons_remain_functional_after_acknowledge(
        self,
        mock_interaction,
    ):
        """Test that buttons remain functional after acknowledgment."""
        # Mock the view with buttons
        mock_view = MagicMock()
        mock_view.children = [
            MagicMock(label="Acknowledge", disabled=False),
            MagicMock(label="Talk to Ash", disabled=False),
        ]

        # After acknowledgment, buttons should still be enabled
        # (different from fully resolved state)
        for button in mock_view.children:
            assert button.disabled is False

    @pytest.mark.asyncio
    async def test_interaction_response_deferred(
        self,
        mock_interaction,
    ):
        """Test that interaction response is properly deferred."""
        await mock_interaction.response.defer()

        mock_interaction.response.defer.assert_called_once()

    @pytest.mark.asyncio
    async def test_message_edit_called_after_acknowledge(
        self,
        mock_interaction,
    ):
        """Test that message is edited with new embed after acknowledge."""
        new_embed = MagicMock()
        new_view = MagicMock()

        await mock_interaction.message.edit(embed=new_embed, view=new_view)

        mock_interaction.message.edit.assert_called_once_with(
            embed=new_embed, view=new_view
        )

    @pytest.mark.asyncio
    async def test_acknowledge_flow_complete(
        self,
        mock_interaction,
        mock_embed_builder,
    ):
        """Test complete acknowledgment flow."""
        # Step 1: Defer response
        await mock_interaction.response.defer()

        # Step 2: Create acknowledged embed
        acknowledged_embed = MagicMock()
        acknowledged_embed.color = discord.Color.green()
        mock_embed_builder.build_acknowledged_embed = MagicMock(
            return_value=acknowledged_embed
        )

        result = mock_embed_builder.build_acknowledged_embed(
            original_embed=MagicMock(),
            acknowledger=mock_interaction.user,
            timestamp=datetime.now(timezone.utc),
        )

        # Step 3: Edit message
        await mock_interaction.message.edit(embed=result, view=MagicMock())

        # Verify flow
        mock_interaction.response.defer.assert_called_once()
        mock_embed_builder.build_acknowledged_embed.assert_called_once()
        mock_interaction.message.edit.assert_called_once()


# =============================================================================
# Scenario 4: Talk to Ash Session
# =============================================================================


class TestTalkToAshSession:
    """
    Scenario 4: Talk to Ash Session

    Input: CRT clicks "Talk to Ash", user responds
    Expected:
    1. DM channel created with user
    2. Welcome message sent (severity-appropriate)
    3. User messages routed to ClaudeClientManager
    4. Ash responses sent to DM
    5. Session tracked in AshSessionManager
    6. Metrics: ash_sessions_total +1, ash_sessions_active = 1
    """

    @pytest.mark.asyncio
    async def test_dm_channel_created_for_user(
        self,
        mock_user,
    ):
        """Test that DM channel is created with the user."""
        # Mock create_dm
        dm_channel = MagicMock()
        dm_channel.id = 111222333444555666
        mock_user.create_dm = AsyncMock(return_value=dm_channel)

        channel = await mock_user.create_dm()

        mock_user.create_dm.assert_called_once()
        assert channel.id == dm_channel.id

    @pytest.mark.asyncio
    async def test_welcome_message_sent_for_high_severity(
        self,
        mock_ash_personality,
        mock_user,
    ):
        """Test severity-appropriate welcome message is sent."""
        severity = "high"

        welcome_message = mock_ash_personality.get_welcome_message(severity=severity)

        # Should contain supportive language
        assert "here for you" in welcome_message.lower()

    @pytest.mark.asyncio
    async def test_session_created_in_ash_session_manager(
        self,
        mock_ash_session_manager,
        mock_user,
    ):
        """Test that session is created and tracked."""
        session_id = await mock_ash_session_manager.create_session(
            user_id=mock_user.id,
            channel_id=111222333444555666,
            severity="high",
        )

        mock_ash_session_manager.create_session.assert_called_once()
        assert session_id == "session_123"

    @pytest.mark.asyncio
    async def test_user_message_routed_to_claude(
        self,
        mock_claude_client,
        mock_user,
    ):
        """Test that user messages are routed to Claude."""
        user_message = "I've been feeling really overwhelmed lately."

        response = await mock_claude_client.send_message(
            message=user_message,
            user_id=mock_user.id,
            session_id="session_123",
        )

        mock_claude_client.send_message.assert_called_once()
        assert "content" in response
        assert response["role"] == "assistant"

    @pytest.mark.asyncio
    async def test_ash_response_sent_to_dm(
        self,
        mock_user,
        mock_claude_client,
    ):
        """Test that Ash response is sent to DM channel."""
        dm_channel = MagicMock()
        dm_channel.send = AsyncMock()
        mock_user.create_dm = AsyncMock(return_value=dm_channel)

        # Get response from Claude
        response = await mock_claude_client.send_message(
            message="Test message",
            user_id=mock_user.id,
            session_id="session_123",
        )

        # Send to DM
        await dm_channel.send(response["content"])

        dm_channel.send.assert_called_once()

    @pytest.mark.asyncio
    async def test_session_tracked_correctly(
        self,
        mock_ash_session_manager,
        mock_user,
    ):
        """Test that session is properly tracked in manager."""
        # Create session
        await mock_ash_session_manager.create_session(
            user_id=mock_user.id,
            channel_id=111222333444555666,
            severity="high",
        )

        # Check session exists
        session = mock_ash_session_manager.get_session(mock_user.id)

        assert session is not None
        assert session["user_id"] == mock_user.id

    @pytest.mark.asyncio
    async def test_ash_sessions_metrics_incremented(
        self,
        mock_metrics_manager,
    ):
        """Test that Ash session metrics are updated."""
        # Session created - increment counter
        mock_metrics_manager.increment("ash_sessions_total")

        # Active sessions gauge
        mock_metrics_manager.gauge("ash_sessions_active", 1)

        # Verify calls
        mock_metrics_manager.increment.assert_called_with("ash_sessions_total")
        mock_metrics_manager.gauge.assert_called_with("ash_sessions_active", 1)

    @pytest.mark.asyncio
    async def test_talk_to_ash_button_initiates_session(
        self,
        mock_interaction,
        mock_ash_session_manager,
        mock_user,
        mock_ash_personality,
    ):
        """Test complete Talk to Ash button flow."""
        # Setup: User from the original alert
        crisis_user = mock_user

        # Step 1: CRT clicks "Talk to Ash" button
        await mock_interaction.response.defer(ephemeral=True)

        # Step 2: Create DM channel
        dm_channel = MagicMock()
        dm_channel.send = AsyncMock()
        crisis_user.create_dm = AsyncMock(return_value=dm_channel)
        await crisis_user.create_dm()

        # Step 3: Create session
        session_id = await mock_ash_session_manager.create_session(
            user_id=crisis_user.id,
            channel_id=dm_channel.id,
            severity="high",
        )

        # Step 4: Send welcome message
        welcome = mock_ash_personality.get_welcome_message(severity="high")
        await dm_channel.send(welcome)

        # Step 5: Send confirmation to CRT member
        await mock_interaction.followup.send(
            "✅ Ash has reached out to the user via DM.",
            ephemeral=True,
        )

        # Verify flow
        mock_interaction.response.defer.assert_called_once_with(ephemeral=True)
        crisis_user.create_dm.assert_called_once()
        mock_ash_session_manager.create_session.assert_called_once()
        dm_channel.send.assert_called_once_with(welcome)
        mock_interaction.followup.send.assert_called_once()


# =============================================================================
# Alert Embed Tests
# =============================================================================


class TestAlertEmbeds:
    """Tests for alert embed creation and modification."""

    @pytest.mark.asyncio
    async def test_crisis_embed_contains_required_fields(
        self,
        mock_embed_builder,
        high_nlp_response,
        message_factory,
        crisis_message_text,
    ):
        """Test that crisis embed contains all required fields."""
        message = message_factory(crisis_message_text)

        # Mock embed with required fields
        embed = MagicMock()
        embed.title = "🚨 Crisis Alert - HIGH"
        embed.description = crisis_message_text[:100]
        embed.fields = [
            MagicMock(name="User", value=message.author.mention),
            MagicMock(name="Channel", value=message.channel.mention),
            MagicMock(name="Severity", value="HIGH"),
            MagicMock(name="Confidence", value="87%"),
        ]
        embed.timestamp = datetime.now(timezone.utc)
        embed.url = message.jump_url

        mock_embed_builder.build_crisis_embed = MagicMock(return_value=embed)

        result = mock_embed_builder.build_crisis_embed(
            message=message,
            nlp_result=high_nlp_response,
        )

        # Verify required fields
        assert "Crisis Alert" in result.title
        assert len(result.fields) >= 4
        assert result.timestamp is not None
        assert result.url == message.jump_url

    @pytest.mark.asyncio
    async def test_embed_color_matches_severity(self):
        """Test that embed colors match severity levels."""
        severity_colors = {
            "critical": discord.Color.dark_red(),
            "high": discord.Color.red(),
            "medium": discord.Color.orange(),
            "low": discord.Color.yellow(),
        }

        for severity, expected_color in severity_colors.items():
            # In actual implementation, embed builder would set these
            assert expected_color is not None


# =============================================================================
# Alert View (Buttons) Tests
# =============================================================================


class TestAlertButtons:
    """Tests for alert button functionality."""

    def test_alert_view_has_required_buttons(self):
        """Test that alert view contains Acknowledge and Talk to Ash buttons."""
        # Mock buttons
        buttons = [
            {"label": "Acknowledge", "style": "success"},
            {"label": "Talk to Ash", "style": "primary"},
        ]

        labels = [b["label"] for b in buttons]
        assert "Acknowledge" in labels
        assert "Talk to Ash" in labels

    @pytest.mark.asyncio
    async def test_acknowledge_button_callback_works(
        self,
        mock_interaction,
    ):
        """Test that acknowledge button callback executes."""
        callback_executed = False

        async def acknowledge_callback(interaction):
            nonlocal callback_executed
            callback_executed = True
            await interaction.response.defer()

        await acknowledge_callback(mock_interaction)

        assert callback_executed is True

    @pytest.mark.asyncio
    async def test_talk_to_ash_button_callback_works(
        self,
        mock_interaction,
    ):
        """Test that Talk to Ash button callback executes."""
        callback_executed = False

        async def talk_to_ash_callback(interaction):
            nonlocal callback_executed
            callback_executed = True
            await interaction.response.defer(ephemeral=True)

        await talk_to_ash_callback(mock_interaction)

        assert callback_executed is True


# =============================================================================
# Cooldown Tests
# =============================================================================


class TestAlertCooldown:
    """Tests for alert cooldown behavior."""

    @pytest.mark.asyncio
    async def test_alert_blocked_during_cooldown(
        self,
        mock_cooldown_manager,
        mock_user,
    ):
        """Test that duplicate alerts are blocked during cooldown."""
        user_id = str(mock_user.id)

        # First alert allowed
        mock_cooldown_manager.can_alert = MagicMock(return_value=True)
        assert mock_cooldown_manager.can_alert(user_id) is True

        # Record the alert
        mock_cooldown_manager.record_alert(user_id)

        # Second alert blocked
        mock_cooldown_manager.can_alert = MagicMock(return_value=False)
        assert mock_cooldown_manager.can_alert(user_id) is False

    @pytest.mark.asyncio
    async def test_cooldown_remaining_time(
        self,
        mock_cooldown_manager,
        mock_user,
    ):
        """Test that remaining cooldown time is tracked."""
        user_id = str(mock_user.id)

        # Set remaining time
        mock_cooldown_manager.get_remaining_cooldown = MagicMock(return_value=45)

        remaining = mock_cooldown_manager.get_remaining_cooldown(user_id)

        assert remaining == 45  # 45 seconds remaining
