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
Tests for Alert Button Views
---
FILE VERSION: v5.0-4-9.0-1
LAST MODIFIED: 2026-01-04
PHASE: Phase 4 - Ash AI Integration
Repository: https://github.com/the-alphabet-cartel/ash-bot
Community: The Alphabet Cartel - https://discord.gg/alphabetcartel | https://alphabetcartel.org
============================================================================
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch, PropertyMock

import pytest

# Module version
__version__ = "v5.0-4-9.0-2"


# =============================================================================
# Helper: Create mock event loop for View tests
# =============================================================================


@pytest.fixture
def mock_event_loop():
    """
    Fixture to mock asyncio.get_running_loop for discord.View instantiation.

    Discord's View class requires a running event loop on __init__.
    This fixture patches it for synchronous test contexts.
    """
    mock_loop = MagicMock()
    mock_future = MagicMock()
    mock_loop.create_future.return_value = mock_future

    with patch("asyncio.get_running_loop", return_value=mock_loop):
        yield mock_loop


# =============================================================================
# AlertButtonView Tests
# =============================================================================


class TestAlertButtonView:
    """Tests for AlertButtonView class."""

    def test_init_with_high_severity(self, mock_event_loop):
        """Test view creation with high severity includes Talk to Ash button."""
        from src.views.alert_buttons import AlertButtonView

        view = AlertButtonView(
            user_id=123456789,
            message_id=987654321,
            severity="high",
        )

        assert view.user_id == 123456789
        assert view.message_id == 987654321
        assert view.severity == "high"
        assert not view.is_acknowledged
        assert view.acknowledged_by is None
        assert not view.is_ash_engaged

        # Should have 2 buttons (Talk to Ash + Acknowledge)
        assert len(view.children) == 2

    def test_init_with_critical_severity(self, mock_event_loop):
        """Test view creation with critical severity includes Talk to Ash button."""
        from src.views.alert_buttons import AlertButtonView

        view = AlertButtonView(
            user_id=123456789,
            message_id=987654321,
            severity="critical",
        )

        assert view.severity == "critical"
        # Should have 2 buttons (Talk to Ash + Acknowledge)
        assert len(view.children) == 2

    def test_init_with_medium_severity(self, mock_event_loop):
        """Test view creation with medium severity does NOT include Talk to Ash button."""
        from src.views.alert_buttons import AlertButtonView

        view = AlertButtonView(
            user_id=123456789,
            message_id=987654321,
            severity="medium",
        )

        assert view.severity == "medium"
        # Should only have 1 button (Acknowledge)
        assert len(view.children) == 1

    def test_init_with_low_severity(self, mock_event_loop):
        """Test view creation with low severity does NOT include Talk to Ash button."""
        from src.views.alert_buttons import AlertButtonView

        view = AlertButtonView(
            user_id=123456789,
            message_id=987654321,
            severity="low",
        )

        assert view.severity == "low"
        # Should only have 1 button (Acknowledge)
        assert len(view.children) == 1

    def test_severity_normalized_to_lowercase(self, mock_event_loop):
        """Test that severity is normalized to lowercase."""
        from src.views.alert_buttons import AlertButtonView

        view = AlertButtonView(
            user_id=123456789,
            message_id=987654321,
            severity="HIGH",
        )

        assert view.severity == "high"

    def test_custom_timeout(self, mock_event_loop):
        """Test custom timeout is applied."""
        from src.views.alert_buttons import AlertButtonView

        view = AlertButtonView(
            user_id=123456789,
            message_id=987654321,
            severity="high",
            timeout=7200.0,  # 2 hours
        )

        assert view.timeout == 7200.0

    def test_repr(self, mock_event_loop):
        """Test string representation."""
        from src.views.alert_buttons import AlertButtonView

        view = AlertButtonView(
            user_id=123456789,
            message_id=987654321,
            severity="high",
        )

        repr_str = repr(view)
        assert "user=123456789" in repr_str
        assert "severity=high" in repr_str
        assert "status=pending" in repr_str
        assert "ash=not engaged" in repr_str


class TestAlertButtonViewCallbacks:
    """Tests for AlertButtonView callback methods."""

    @pytest.mark.asyncio
    async def test_acknowledge_callback(self):
        """Test acknowledge button callback."""
        from src.views.alert_buttons import AlertButtonView

        view = AlertButtonView(
            user_id=123456789,
            message_id=987654321,
            severity="high",
        )

        # Create mock interaction
        interaction = MagicMock()
        interaction.user.id = 111111111
        interaction.user.display_name = "CRT Member"
        interaction.response = AsyncMock()
        interaction.message = MagicMock()
        interaction.message.embeds = [MagicMock()]
        interaction.message.embeds[0].footer = MagicMock()
        interaction.message.embeds[0].footer.text = "Original Footer"

        # Call the callback
        await view._acknowledge_callback(interaction)

        # Verify state updated
        assert view.is_acknowledged
        assert view.acknowledged_by == 111111111

        # Verify interaction response
        interaction.response.edit_message.assert_called_once()

    @pytest.mark.asyncio
    async def test_acknowledge_callback_double_click(self):
        """Test acknowledge button prevents double acknowledgment."""
        from src.views.alert_buttons import AlertButtonView

        view = AlertButtonView(
            user_id=123456789,
            message_id=987654321,
            severity="high",
        )

        # Pre-acknowledge
        view._acknowledged = True
        view._acknowledged_by = 111111111

        # Create mock interaction
        interaction = MagicMock()
        interaction.user.id = 222222222
        interaction.response = AsyncMock()

        # Call the callback
        await view._acknowledge_callback(interaction)

        # Verify ephemeral message sent
        interaction.response.send_message.assert_called_once()
        call_kwargs = interaction.response.send_message.call_args[1]
        assert call_kwargs.get("ephemeral") is True

    @pytest.mark.asyncio
    async def test_talk_to_ash_no_managers(self):
        """Test Talk to Ash when managers not available."""
        from src.views.alert_buttons import AlertButtonView

        view = AlertButtonView(
            user_id=123456789,
            message_id=987654321,
            severity="high",
        )

        # Create mock interaction without Ash managers
        interaction = MagicMock()
        interaction.client = MagicMock()
        interaction.client.ash_session_manager = None
        interaction.user.id = 111111111
        interaction.response = AsyncMock()

        # Call the callback
        await view._talk_to_ash_callback(interaction)

        # Verify warning message sent
        interaction.response.send_message.assert_called_once()
        call_args = interaction.response.send_message.call_args[0][0]
        assert "not currently available" in call_args

    @pytest.mark.asyncio
    async def test_talk_to_ash_existing_session(self):
        """Test Talk to Ash when user already has session."""
        from src.views.alert_buttons import AlertButtonView

        view = AlertButtonView(
            user_id=123456789,
            message_id=987654321,
            severity="high",
        )

        # Create mock interaction with session manager that has active session
        interaction = MagicMock()
        interaction.client = MagicMock()
        interaction.client.ash_session_manager = MagicMock()
        interaction.client.ash_session_manager.has_active_session.return_value = True
        interaction.client.ash_personality_manager = MagicMock()
        interaction.user.id = 111111111
        interaction.response = AsyncMock()

        # Call the callback
        await view._talk_to_ash_callback(interaction)

        # Verify info message sent
        interaction.response.send_message.assert_called_once()
        call_kwargs = interaction.response.send_message.call_args[1]
        assert call_kwargs.get("ephemeral") is True

    @pytest.mark.asyncio
    async def test_talk_to_ash_session_already_started_from_alert(self):
        """Test Talk to Ash when session already started from this alert."""
        from src.views.alert_buttons import AlertButtonView

        view = AlertButtonView(
            user_id=123456789,
            message_id=987654321,
            severity="high",
        )

        # Mark session as started
        view._ash_session_started = True
        view._ash_started_by = 111111111

        # Create mock interaction
        interaction = MagicMock()
        interaction.client = MagicMock()
        interaction.client.ash_session_manager = MagicMock()
        interaction.client.ash_session_manager.has_active_session.return_value = False
        interaction.client.ash_personality_manager = MagicMock()
        interaction.user.id = 222222222
        interaction.response = AsyncMock()

        # Call the callback
        await view._talk_to_ash_callback(interaction)

        # Verify info message sent
        interaction.response.send_message.assert_called_once()
        call_args = interaction.response.send_message.call_args[0][0]
        assert "already started" in call_args


class TestPersistentAlertView:
    """Tests for PersistentAlertView class."""

    def test_init(self, mock_event_loop):
        """Test persistent view creation."""
        from src.views.alert_buttons import PersistentAlertView

        view = PersistentAlertView()

        # Should never timeout
        assert view.timeout is None

        # Should have 2 buttons
        assert len(view.children) == 2

    def test_button_custom_ids(self, mock_event_loop):
        """Test that buttons have persistent custom IDs."""
        from src.views.alert_buttons import PersistentAlertView

        view = PersistentAlertView()

        custom_ids = [child.custom_id for child in view.children]
        assert "persistent:ash_talk" in custom_ids
        assert "persistent:ash_ack" in custom_ids


# =============================================================================
# Export Tests
# =============================================================================


class TestViewExports:
    """Tests for view module exports."""

    def test_all_exports_exist(self):
        """Test that all expected exports are available."""
        from src.views.alert_buttons import AlertButtonView, PersistentAlertView

        assert AlertButtonView is not None
        assert PersistentAlertView is not None

    def test_module_version(self):
        """Test module has version."""
        from src.views import alert_buttons

        assert hasattr(alert_buttons, "__version__")
        assert alert_buttons.__version__.startswith("v5.0")
