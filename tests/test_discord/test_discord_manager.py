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
Discord Manager Tests for Ash-Bot Service
---
FILE VERSION: v5.0-4-9.0-1
LAST MODIFIED: 2026-01-04
PHASE: Phase 4 - Ash AI Integration
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-bot
Community: The Alphabet Cartel - https://discord.gg/alphabetcartel | https://alphabetcartel.org
============================================================================
Tests for DiscordManager including:
- Factory function creation
- Intents configuration
- Message handling
- Connection management
- Phase 4: DM handling for Ash AI sessions
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

__version__ = "v5.0-4-9.0-2"


# =============================================================================
# Factory Function Tests
# =============================================================================


class TestDiscordManagerFactory:
    """Tests for DiscordManager factory function."""

    def test_create_discord_manager(
        self,
        test_config_manager,
        test_secrets_manager,
        test_channel_config,
        test_nlp_client,
        mock_event_loop,
    ):
        """Test factory function creates manager correctly."""
        from src.managers.discord import create_discord_manager

        manager = create_discord_manager(
            config_manager=test_config_manager,
            secrets_manager=test_secrets_manager,
            channel_config=test_channel_config,
            nlp_client=test_nlp_client,
        )

        assert manager is not None
        assert manager.bot is not None

    def test_create_discord_manager_with_ash_managers(
        self,
        test_config_manager,
        test_secrets_manager,
        test_channel_config,
        test_nlp_client,
        mock_event_loop,
    ):
        """Test factory function with Ash AI managers (Phase 4)."""
        from src.managers.discord import create_discord_manager

        mock_session_manager = MagicMock()
        mock_personality_manager = MagicMock()

        manager = create_discord_manager(
            config_manager=test_config_manager,
            secrets_manager=test_secrets_manager,
            channel_config=test_channel_config,
            nlp_client=test_nlp_client,
            ash_session_manager=mock_session_manager,
            ash_personality_manager=mock_personality_manager,
        )

        assert manager.ash_session_manager is mock_session_manager
        assert manager.ash_personality_manager is mock_personality_manager
        assert manager.has_ash_ai is True

        # Check managers attached to bot
        assert manager.bot.ash_session_manager is mock_session_manager
        assert manager.bot.ash_personality_manager is mock_personality_manager

    def test_repr(
        self,
        test_config_manager,
        test_secrets_manager,
        test_channel_config,
        test_nlp_client,
        mock_event_loop,
    ):
        """Test string representation."""
        from src.managers.discord import create_discord_manager

        manager = create_discord_manager(
            config_manager=test_config_manager,
            secrets_manager=test_secrets_manager,
            channel_config=test_channel_config,
            nlp_client=test_nlp_client,
        )

        repr_str = repr(manager)

        assert "DiscordManager" in repr_str


# =============================================================================
# Intents Tests
# =============================================================================


class TestIntentsConfiguration:
    """Tests for Discord intents configuration."""

    def test_intents_configured(
        self,
        test_config_manager,
        test_secrets_manager,
        test_channel_config,
        test_nlp_client,
        mock_event_loop,
    ):
        """Test that required intents are enabled."""
        from src.managers.discord import create_discord_manager

        manager = create_discord_manager(
            config_manager=test_config_manager,
            secrets_manager=test_secrets_manager,
            channel_config=test_channel_config,
            nlp_client=test_nlp_client,
        )

        intents = manager.bot.intents

        # Required intents should be enabled
        assert intents.guilds is True
        assert intents.message_content is True
        assert intents.dm_messages is True  # Phase 4


# =============================================================================
# Connection Tests
# =============================================================================


class TestConnection:
    """Tests for connection management."""

    def test_connect_without_token_raises_sync(
        self, test_config_manager, test_channel_config, test_nlp_client
    ):
        """Test that connect raises if no token (sync validation check)."""
        from src.managers.secrets_manager import create_secrets_manager
        import tempfile
        from pathlib import Path
        import os

        # Create secrets manager with empty paths (no token anywhere)
        with tempfile.TemporaryDirectory() as tmpdir:
            empty_path = Path(tmpdir)
            
            # Clear any env var fallback
            old_token = os.environ.pop("DISCORD_BOT_TOKEN", None)
            try:
                # Override BOTH docker_path and local_path to empty dirs
                empty_secrets = create_secrets_manager(
                    docker_path=empty_path / "docker",  # Non-existent
                    local_path=empty_path / "local",    # Non-existent
                )

                # Verify token is not found (the actual check that connect() does)
                token = empty_secrets.get_discord_bot_token()
                assert token is None, "Expected no token in empty secrets dir"
            finally:
                # Restore env var if it existed
                if old_token is not None:
                    os.environ["DISCORD_BOT_TOKEN"] = old_token

    def test_is_connected_property(
        self,
        test_config_manager,
        test_secrets_manager,
        test_channel_config,
        test_nlp_client,
        mock_event_loop,
    ):
        """Test is_connected property."""
        from src.managers.discord import create_discord_manager

        manager = create_discord_manager(
            config_manager=test_config_manager,
            secrets_manager=test_secrets_manager,
            channel_config=test_channel_config,
            nlp_client=test_nlp_client,
        )

        # Initially not connected
        assert manager.is_connected is False

    def test_status_dict(
        self,
        test_config_manager,
        test_secrets_manager,
        test_channel_config,
        test_nlp_client,
        mock_event_loop,
    ):
        """Test get_status method."""
        from src.managers.discord import create_discord_manager

        manager = create_discord_manager(
            config_manager=test_config_manager,
            secrets_manager=test_secrets_manager,
            channel_config=test_channel_config,
            nlp_client=test_nlp_client,
        )

        status = manager.get_status()

        assert isinstance(status, dict)
        assert "connected" in status
        assert "messages_processed" in status
        assert "crises_detected" in status
        assert "ash_messages_handled" in status  # Phase 4
        assert "ash_ai_enabled" in status  # Phase 4


# =============================================================================
# Message Handling Tests
# =============================================================================


class TestMessageHandling:
    """Tests for message handling."""

    @pytest.mark.asyncio
    async def test_on_message_ignores_bot_messages(
        self,
        test_config_manager,
        test_secrets_manager,
        test_channel_config,
        test_nlp_client,
        mock_bot_message,
    ):
        """Test that bot messages are ignored."""
        from src.managers.discord import create_discord_manager

        manager = create_discord_manager(
            config_manager=test_config_manager,
            secrets_manager=test_secrets_manager,
            channel_config=test_channel_config,
            nlp_client=test_nlp_client,
        )

        # Mock the NLP client analyze method
        test_nlp_client.analyze_message = AsyncMock()

        # Process bot message
        await manager._on_message(mock_bot_message)

        # NLP should not be called for bot messages
        test_nlp_client.analyze_message.assert_not_called()

    @pytest.mark.asyncio
    async def test_on_message_ignores_unmonitored_channels(
        self,
        test_config_manager,
        test_secrets_manager,
        test_channel_config,
        test_nlp_client,
        mock_discord_message,
    ):
        """Test that unmonitored channels are ignored."""
        from src.managers.discord import create_discord_manager

        manager = create_discord_manager(
            config_manager=test_config_manager,
            secrets_manager=test_secrets_manager,
            channel_config=test_channel_config,
            nlp_client=test_nlp_client,
        )

        # Set channel to unmonitored
        mock_discord_message.channel.id = 999999999  # Not in whitelist

        # Mock the NLP client
        test_nlp_client.analyze_message = AsyncMock()

        # Process message
        await manager._on_message(mock_discord_message)

        # NLP should not be called for unmonitored channels
        test_nlp_client.analyze_message.assert_not_called()


# =============================================================================
# Phase 4: DM Handling Tests
# =============================================================================


class TestDMHandling:
    """Tests for Phase 4 DM handling."""

    @pytest.mark.asyncio
    async def test_dm_without_ash_managers_ignored(
        self,
        test_config_manager,
        test_secrets_manager,
        test_channel_config,
        test_nlp_client,
    ):
        """Test DMs are ignored when Ash managers not configured."""
        from src.managers.discord import create_discord_manager

        manager = create_discord_manager(
            config_manager=test_config_manager,
            secrets_manager=test_secrets_manager,
            channel_config=test_channel_config,
            nlp_client=test_nlp_client,
            # No Ash managers
        )

        # Create mock DM message
        mock_dm = MagicMock()
        mock_dm.author.bot = False
        mock_dm.guild = None  # DM has no guild
        mock_dm.author.id = 123456789
        mock_dm.content = "Hello Ash"

        # Should not raise
        await manager._handle_dm_message(mock_dm)

    @pytest.mark.asyncio
    async def test_dm_without_active_session_ignored(
        self,
        test_config_manager,
        test_secrets_manager,
        test_channel_config,
        test_nlp_client,
    ):
        """Test DMs from users without active session are ignored."""
        from src.managers.discord import create_discord_manager

        mock_session_manager = MagicMock()
        mock_session_manager.get_session.return_value = None  # No active session
        mock_personality_manager = MagicMock()

        manager = create_discord_manager(
            config_manager=test_config_manager,
            secrets_manager=test_secrets_manager,
            channel_config=test_channel_config,
            nlp_client=test_nlp_client,
            ash_session_manager=mock_session_manager,
            ash_personality_manager=mock_personality_manager,
        )

        # Create mock DM message
        mock_dm = MagicMock()
        mock_dm.author.bot = False
        mock_dm.guild = None
        mock_dm.author.id = 123456789
        mock_dm.content = "Hello Ash"

        await manager._handle_dm_message(mock_dm)

        # Should check for session
        mock_session_manager.get_session.assert_called_once_with(123456789)

        # Should not generate response
        mock_personality_manager.generate_response.assert_not_called()

    @pytest.mark.asyncio
    async def test_dm_with_active_session_processes(
        self,
        test_config_manager,
        test_secrets_manager,
        test_channel_config,
        test_nlp_client,
    ):
        """Test DMs with active session are processed."""
        from src.managers.discord import create_discord_manager

        # Create mock session
        mock_session = MagicMock()
        mock_session.session_id = "session_123"

        mock_session_manager = MagicMock()
        mock_session_manager.get_session.return_value = mock_session

        mock_personality_manager = MagicMock()
        mock_personality_manager.detect_end_request.return_value = False
        mock_personality_manager.detect_crt_request.return_value = False
        mock_personality_manager.generate_response = AsyncMock(
            return_value="I hear you. How are you feeling?"
        )

        manager = create_discord_manager(
            config_manager=test_config_manager,
            secrets_manager=test_secrets_manager,
            channel_config=test_channel_config,
            nlp_client=test_nlp_client,
            ash_session_manager=mock_session_manager,
            ash_personality_manager=mock_personality_manager,
        )

        # Create mock DM message
        mock_dm = MagicMock()
        mock_dm.author.bot = False
        mock_dm.guild = None
        mock_dm.author.id = 123456789
        mock_dm.author.display_name = "TestUser"
        mock_dm.content = "I'm feeling sad today"
        mock_dm.channel.typing = MagicMock(return_value=AsyncMock())
        mock_dm.channel.send = AsyncMock()

        await manager._handle_dm_message(mock_dm)

        # Should check for session
        mock_session_manager.get_session.assert_called_once_with(123456789)

        # Should generate response
        mock_personality_manager.generate_response.assert_called_once()

        # Should send response
        mock_dm.channel.send.assert_called_once_with("I hear you. How are you feeling?")

        # Stats should be updated
        assert manager._ash_messages_handled == 1

    @pytest.mark.asyncio
    async def test_dm_end_request_ends_session(
        self,
        test_config_manager,
        test_secrets_manager,
        test_channel_config,
        test_nlp_client,
    ):
        """Test that end request phrases end the session."""
        from src.managers.discord import create_discord_manager

        mock_session = MagicMock()
        mock_session.session_id = "session_123"

        mock_session_manager = MagicMock()
        mock_session_manager.get_session.return_value = mock_session
        mock_session_manager.end_session = AsyncMock()

        mock_personality_manager = MagicMock()
        mock_personality_manager.detect_end_request.return_value = True

        manager = create_discord_manager(
            config_manager=test_config_manager,
            secrets_manager=test_secrets_manager,
            channel_config=test_channel_config,
            nlp_client=test_nlp_client,
            ash_session_manager=mock_session_manager,
            ash_personality_manager=mock_personality_manager,
        )

        # Create mock DM message
        mock_dm = MagicMock()
        mock_dm.author.bot = False
        mock_dm.guild = None
        mock_dm.author.id = 123456789
        mock_dm.content = "goodbye"

        await manager._handle_dm_message(mock_dm)

        # Should end session
        mock_session_manager.end_session.assert_called_once_with(
            user_id=123456789,
            reason="user_ended",
            send_closing=True,
        )

    @pytest.mark.asyncio
    async def test_dm_crt_request_transfers(
        self,
        test_config_manager,
        test_secrets_manager,
        test_channel_config,
        test_nlp_client,
    ):
        """Test that CRT request phrases transfer to human support."""
        from src.managers.discord import create_discord_manager

        mock_session = MagicMock()
        mock_session.session_id = "session_123"

        mock_session_manager = MagicMock()
        mock_session_manager.get_session.return_value = mock_session
        mock_session_manager.end_session = AsyncMock()

        mock_personality_manager = MagicMock()
        mock_personality_manager.detect_end_request.return_value = False
        mock_personality_manager.detect_crt_request.return_value = True
        mock_personality_manager.get_handoff_message.return_value = "Connecting you with a human..."

        manager = create_discord_manager(
            config_manager=test_config_manager,
            secrets_manager=test_secrets_manager,
            channel_config=test_channel_config,
            nlp_client=test_nlp_client,
            ash_session_manager=mock_session_manager,
            ash_personality_manager=mock_personality_manager,
        )

        # Create mock DM message
        mock_dm = MagicMock()
        mock_dm.author.bot = False
        mock_dm.guild = None
        mock_dm.author.id = 123456789
        mock_dm.content = "can I talk to a real person?"
        mock_dm.channel.send = AsyncMock()

        await manager._handle_dm_message(mock_dm)

        # Should send handoff message
        mock_dm.channel.send.assert_called_once_with("Connecting you with a human...")

        # Should end session with transfer reason
        mock_session_manager.end_session.assert_called_once_with(
            user_id=123456789,
            reason="transfer",
            send_closing=True,
        )


# =============================================================================
# Analysis and Logging Tests
# =============================================================================


class TestAnalysisAndLogging:
    """Tests for message analysis and logging."""

    @pytest.mark.asyncio
    async def test_analyze_and_process_success(
        self,
        test_config_manager,
        test_secrets_manager,
        test_channel_config,
        test_nlp_client,
        mock_discord_message,
        sample_crisis_result,
    ):
        """Test successful message analysis."""
        from src.managers.discord import create_discord_manager

        manager = create_discord_manager(
            config_manager=test_config_manager,
            secrets_manager=test_secrets_manager,
            channel_config=test_channel_config,
            nlp_client=test_nlp_client,
        )

        # Mock NLP client to return crisis result
        test_nlp_client.analyze_message = AsyncMock(return_value=sample_crisis_result)

        # Run analysis
        await manager._analyze_and_process(mock_discord_message)

        # Verify NLP was called
        test_nlp_client.analyze_message.assert_called_once()

        # Verify stats were updated
        assert manager._messages_processed == 1
        assert manager._crises_detected == 1

    @pytest.mark.asyncio
    async def test_analyze_and_process_safe_message(
        self,
        test_config_manager,
        test_secrets_manager,
        test_channel_config,
        test_nlp_client,
        mock_discord_message,
        sample_safe_result,
    ):
        """Test safe message analysis."""
        from src.managers.discord import create_discord_manager

        manager = create_discord_manager(
            config_manager=test_config_manager,
            secrets_manager=test_secrets_manager,
            channel_config=test_channel_config,
            nlp_client=test_nlp_client,
        )

        # Mock NLP client to return safe result
        test_nlp_client.analyze_message = AsyncMock(return_value=sample_safe_result)

        # Run analysis
        await manager._analyze_and_process(mock_discord_message)

        # Verify stats
        assert manager._messages_processed == 1
        assert manager._crises_detected == 0  # Safe message

    @pytest.mark.asyncio
    async def test_analyze_and_process_handles_error(
        self,
        test_config_manager,
        test_secrets_manager,
        test_channel_config,
        test_nlp_client,
        mock_discord_message,
    ):
        """Test that analysis errors are handled gracefully."""
        from src.managers.discord import create_discord_manager

        manager = create_discord_manager(
            config_manager=test_config_manager,
            secrets_manager=test_secrets_manager,
            channel_config=test_channel_config,
            nlp_client=test_nlp_client,
        )

        # Mock NLP client to raise error
        test_nlp_client.analyze_message = AsyncMock(side_effect=Exception("API error"))

        # Should not raise
        await manager._analyze_and_process(mock_discord_message)


# =============================================================================
# Statistics Tests
# =============================================================================


class TestStatistics:
    """Tests for statistics tracking."""

    def test_initial_statistics(
        self,
        test_config_manager,
        test_secrets_manager,
        test_channel_config,
        test_nlp_client,
        mock_event_loop,
    ):
        """Test initial statistics are zero."""
        from src.managers.discord import create_discord_manager

        manager = create_discord_manager(
            config_manager=test_config_manager,
            secrets_manager=test_secrets_manager,
            channel_config=test_channel_config,
            nlp_client=test_nlp_client,
        )

        assert manager.messages_processed == 0
        assert manager.crises_detected == 0
        assert manager.ash_messages_handled == 0  # Phase 4

    def test_latency_property(
        self,
        test_config_manager,
        test_secrets_manager,
        test_channel_config,
        test_nlp_client,
        mock_event_loop,
    ):
        """Test latency property."""
        import math
        from src.managers.discord import create_discord_manager

        manager = create_discord_manager(
            config_manager=test_config_manager,
            secrets_manager=test_secrets_manager,
            channel_config=test_channel_config,
            nlp_client=test_nlp_client,
        )

        # Latency is nan when not connected (discord.py behavior)
        latency = manager.latency
        assert math.isnan(latency) or latency == 0.0, f"Expected nan or 0.0, got {latency}"

    def test_guild_count_property(
        self,
        test_config_manager,
        test_secrets_manager,
        test_channel_config,
        test_nlp_client,
        mock_event_loop,
    ):
        """Test guild count property."""
        from src.managers.discord import create_discord_manager

        manager = create_discord_manager(
            config_manager=test_config_manager,
            secrets_manager=test_secrets_manager,
            channel_config=test_channel_config,
            nlp_client=test_nlp_client,
        )

        # Guild count should be 0 when not connected
        assert manager.guild_count == 0

    def test_has_ash_ai_property(
        self,
        test_config_manager,
        test_secrets_manager,
        test_channel_config,
        test_nlp_client,
        mock_event_loop,
    ):
        """Test has_ash_ai property."""
        from src.managers.discord import create_discord_manager

        # Without Ash managers
        manager1 = create_discord_manager(
            config_manager=test_config_manager,
            secrets_manager=test_secrets_manager,
            channel_config=test_channel_config,
            nlp_client=test_nlp_client,
        )
        assert manager1.has_ash_ai is False

        # With Ash managers
        manager2 = create_discord_manager(
            config_manager=test_config_manager,
            secrets_manager=test_secrets_manager,
            channel_config=test_channel_config,
            nlp_client=test_nlp_client,
            ash_session_manager=MagicMock(),
            ash_personality_manager=MagicMock(),
        )
        assert manager2.has_ash_ai is True
