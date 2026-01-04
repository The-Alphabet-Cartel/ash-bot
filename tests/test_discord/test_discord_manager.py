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
FILE VERSION: v5.0-1-1.7-1
LAST MODIFIED: 2026-01-03
PHASE: Phase 1 - Discord Connectivity
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-bot
Community: The Alphabet Cartel - https://discord.gg/alphabetcartel | https://alphabetcartel.org
============================================================================
Tests for DiscordManager including:
- Factory function creation
- Intents configuration
- Message handling
- Connection management
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

__version__ = "v5.0-1-1.7-1"


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

    def test_repr(
        self,
        test_config_manager,
        test_secrets_manager,
        test_channel_config,
        test_nlp_client,
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


# =============================================================================
# Connection Tests
# =============================================================================


class TestConnection:
    """Tests for connection management."""

    @pytest.mark.asyncio
    async def test_connect_without_token_raises(
        self, test_config_manager, test_channel_config, test_nlp_client
    ):
        """Test that connect raises if no token."""
        from src.managers.discord import create_discord_manager
        from src.managers.secrets_manager import create_secrets_manager
        import tempfile
        from pathlib import Path

        # Create secrets manager without token
        with tempfile.TemporaryDirectory() as tmpdir:
            empty_secrets = create_secrets_manager(local_path=Path(tmpdir))

            manager = create_discord_manager(
                config_manager=test_config_manager,
                secrets_manager=empty_secrets,
                channel_config=test_channel_config,
                nlp_client=test_nlp_client,
            )

            with pytest.raises(ValueError, match="Discord bot token not found"):
                await manager.connect()

    def test_is_connected_property(
        self,
        test_config_manager,
        test_secrets_manager,
        test_channel_config,
        test_nlp_client,
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

    @pytest.mark.asyncio
    async def test_on_message_ignores_dms(
        self,
        test_config_manager,
        test_secrets_manager,
        test_channel_config,
        test_nlp_client,
        mock_discord_message,
    ):
        """Test that DMs are ignored."""
        from src.managers.discord import create_discord_manager

        manager = create_discord_manager(
            config_manager=test_config_manager,
            secrets_manager=test_secrets_manager,
            channel_config=test_channel_config,
            nlp_client=test_nlp_client,
        )

        # Set guild to None (DM)
        mock_discord_message.guild = None

        # Mock the NLP client
        test_nlp_client.analyze_message = AsyncMock()

        # Process message
        await manager._on_message(mock_discord_message)

        # NLP should not be called for DMs
        test_nlp_client.analyze_message.assert_not_called()


# =============================================================================
# Analysis and Logging Tests
# =============================================================================


class TestAnalysisAndLogging:
    """Tests for message analysis and logging."""

    @pytest.mark.asyncio
    async def test_analyze_and_log_success(
        self,
        test_config_manager,
        test_secrets_manager,
        test_channel_config,
        test_nlp_client,
        mock_discord_message,
        sample_crisis_result,
    ):
        """Test successful message analysis and logging."""
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
        await manager._analyze_and_log(mock_discord_message)

        # Verify NLP was called
        test_nlp_client.analyze_message.assert_called_once()

        # Verify stats were updated
        assert manager._messages_processed == 1
        assert manager._crises_detected == 1

    @pytest.mark.asyncio
    async def test_analyze_and_log_safe_message(
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
        await manager._analyze_and_log(mock_discord_message)

        # Verify stats
        assert manager._messages_processed == 1
        assert manager._crises_detected == 0  # Safe message

    @pytest.mark.asyncio
    async def test_analyze_and_log_handles_error(
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
        await manager._analyze_and_log(mock_discord_message)

        # Message not counted as processed due to error
        # (depends on implementation - could count it anyway)


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

    def test_latency_property(
        self,
        test_config_manager,
        test_secrets_manager,
        test_channel_config,
        test_nlp_client,
    ):
        """Test latency property."""
        from src.managers.discord import create_discord_manager

        manager = create_discord_manager(
            config_manager=test_config_manager,
            secrets_manager=test_secrets_manager,
            channel_config=test_channel_config,
            nlp_client=test_nlp_client,
        )

        # Latency should be 0 when not connected
        assert manager.latency == 0.0

    def test_guild_count_property(
        self,
        test_config_manager,
        test_secrets_manager,
        test_channel_config,
        test_nlp_client,
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
