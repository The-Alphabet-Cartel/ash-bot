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
Alert Dispatcher Tests
---
FILE VERSION: v5.0-3-8.3-3
LAST MODIFIED: 2026-01-04
PHASE: Phase 3 - Alert Dispatching
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-bot
Community: The Alphabet Cartel - https://discord.gg/alphabetcartel | https://alphabetcartel.org
============================================================================
Tests for AlertDispatcher:
- Alert qualification by severity
- Cooldown enforcement
- Channel routing
- CRT role pinging
"""

import pytest
from datetime import datetime, timezone
from unittest.mock import MagicMock, AsyncMock, patch
import discord


# =============================================================================
# Test Fixtures
# =============================================================================


@pytest.fixture
def mock_config():
    """Create mock config manager."""
    config = MagicMock()
    
    def get_side_effect(section, key, default=None):
        values = {
            ("alerting", "enabled"): True,
            ("alerting", "min_severity_to_alert"): "medium",
            ("alerting", "cooldown_seconds"): 300,
        }
        return values.get((section, key), default)
    
    config.get.side_effect = get_side_effect
    return config


@pytest.fixture
def mock_channel_config():
    """Create mock channel config manager."""
    channel_config = MagicMock()
    
    # CRT Role ID (configurable via JSON/env)
    channel_config.get_crt_role_id.return_value = 999888777
    
    # Alert channels (configurable via JSON/env)
    def get_alert_channel_side_effect(severity):
        channels = {
            "medium": 111000111,
            "high": 222000222,
            "critical": 333000333,
        }
        return channels.get(severity.lower())
    
    channel_config.get_alert_channel.side_effect = get_alert_channel_side_effect
    
    # All alert channels
    channel_config.get_all_alert_channels.return_value = {
        "medium": 111000111,
        "high": 222000222,
        "critical": 333000333,
    }
    
    return channel_config


@pytest.fixture
def mock_cooldown_manager():
    """Create mock cooldown manager."""
    cooldown = MagicMock()
    cooldown.is_on_cooldown.return_value = False
    cooldown.set_cooldown.return_value = None
    cooldown.get_remaining_cooldown.return_value = 0
    return cooldown


@pytest.fixture
def mock_embed_builder():
    """Create mock embed builder."""
    builder = MagicMock()
    builder.build_crisis_embed.return_value = discord.Embed(title="Test Crisis Alert")
    builder.build_escalation_embed.return_value = discord.Embed(title="Test Escalation Alert")
    return builder


@pytest.fixture
def mock_bot():
    """Create mock Discord bot."""
    bot = MagicMock()
    
    # Mock channels (IDs match mock_channel_config)
    monitor_channel = MagicMock(spec=discord.TextChannel)
    monitor_channel.id = 111000111
    monitor_channel.name = "monitor-queue"
    monitor_channel.send = AsyncMock(return_value=MagicMock(id=123))
    
    crisis_channel = MagicMock(spec=discord.TextChannel)
    crisis_channel.id = 222000222
    crisis_channel.name = "crisis-response"
    crisis_channel.send = AsyncMock(return_value=MagicMock(id=456))
    
    critical_channel = MagicMock(spec=discord.TextChannel)
    critical_channel.id = 333000333
    critical_channel.name = "critical-response"
    critical_channel.send = AsyncMock(return_value=MagicMock(id=789))
    
    def get_channel_side_effect(channel_id):
        channels = {
            111000111: monitor_channel,
            222000222: crisis_channel,
            333000333: critical_channel,
        }
        return channels.get(channel_id)
    
    bot.get_channel.side_effect = get_channel_side_effect
    
    return bot


@pytest.fixture
def mock_user():
    """Create mock Discord user."""
    user = MagicMock(spec=discord.Member)
    user.id = 123456789
    user.name = "TestUser"
    user.display_name = "Test User"
    user.mention = "<@123456789>"
    return user


@pytest.fixture
def mock_message(mock_user):
    """Create mock Discord message."""
    message = MagicMock(spec=discord.Message)
    message.id = 987654321
    message.author = mock_user
    message.content = "I'm feeling really overwhelmed"
    message.channel.id = 111222333
    message.guild.id = 444555666
    message.jump_url = "https://discord.com/channels/444555666/111222333/987654321"
    return message


@pytest.fixture
def mock_analysis_result():
    """Create mock NLP analysis result."""
    result = MagicMock()
    result.severity = "high"
    result.crisis_score = 0.78
    result.confidence = 0.85
    result.requires_intervention = True
    result.recommended_action = "priority_response"
    result.explanation = {"key_factors": ["emotional distress"]}
    result.request_id = "req_abc123"
    result.processing_time_ms = 125.5
    return result


@pytest.fixture
def alert_dispatcher(
    mock_config, mock_channel_config, mock_cooldown_manager, 
    mock_embed_builder, mock_bot
):
    """Create AlertDispatcher instance."""
    from src.managers.alerting.alert_dispatcher import AlertDispatcher
    
    return AlertDispatcher(
        config_manager=mock_config,
        channel_config=mock_channel_config,
        embed_builder=mock_embed_builder,
        cooldown_manager=mock_cooldown_manager,
        bot=mock_bot,
    )


# =============================================================================
# Initialization Tests
# =============================================================================


class TestAlertDispatcherInit:
    """Tests for AlertDispatcher initialization."""

    def test_init_creates_instance(self, alert_dispatcher):
        """Test initialization creates valid instance."""
        assert alert_dispatcher is not None

    def test_init_loads_enabled_from_config(self, alert_dispatcher):
        """Test initialization loads enabled setting."""
        assert alert_dispatcher._enabled is True

    def test_init_loads_min_severity_from_config(self, alert_dispatcher):
        """Test initialization loads min severity setting."""
        assert alert_dispatcher._min_severity == "medium"

    def test_init_loads_crt_role_from_channel_config(self, alert_dispatcher):
        """Test initialization loads CRT role from channel config."""
        assert alert_dispatcher._crt_role_id == 999888777


# =============================================================================
# Severity Qualification Tests
# =============================================================================


class TestSeverityQualification:
    """Tests for severity-based alert qualification."""

    def test_safe_severity_not_qualified(self, alert_dispatcher):
        """Test safe severity does not qualify for alert."""
        qualified = alert_dispatcher._should_alert("safe")
        
        assert qualified is False

    def test_low_severity_not_qualified(self, alert_dispatcher):
        """Test low severity does not qualify for alert."""
        qualified = alert_dispatcher._should_alert("low")
        
        assert qualified is False

    def test_medium_severity_qualified(self, alert_dispatcher):
        """Test medium severity qualifies for alert."""
        qualified = alert_dispatcher._should_alert("medium")
        
        assert qualified is True

    def test_high_severity_qualified(self, alert_dispatcher):
        """Test high severity qualifies for alert."""
        qualified = alert_dispatcher._should_alert("high")
        
        assert qualified is True

    def test_critical_severity_qualified(self, alert_dispatcher):
        """Test critical severity qualifies for alert."""
        qualified = alert_dispatcher._should_alert("critical")
        
        assert qualified is True

    def test_disabled_alerting_returns_false(self, mock_config, mock_channel_config, 
                                              mock_cooldown_manager, mock_embed_builder, 
                                              mock_bot):
        """Test disabled alerting always returns false."""
        from src.managers.alerting.alert_dispatcher import AlertDispatcher
        
        # Override config to disable alerting
        mock_config.get.side_effect = lambda s, k, d=None: False if k == "enabled" else d
        
        dispatcher = AlertDispatcher(
            config_manager=mock_config,
            channel_config=mock_channel_config,
            embed_builder=mock_embed_builder,
            cooldown_manager=mock_cooldown_manager,
            bot=mock_bot,
        )
        
        assert dispatcher._should_alert("critical") is False


# =============================================================================
# CRT Ping Tests
# =============================================================================


class TestCRTPinging:
    """Tests for Crisis Response Team pinging."""

    def test_medium_does_not_ping_crt(self, alert_dispatcher):
        """Test medium severity does not ping CRT."""
        should_ping = alert_dispatcher._should_ping_crt("medium")
        
        assert should_ping is False

    def test_high_pings_crt(self, alert_dispatcher):
        """Test high severity pings CRT."""
        should_ping = alert_dispatcher._should_ping_crt("high")
        
        assert should_ping is True

    def test_critical_pings_crt(self, alert_dispatcher):
        """Test critical severity pings CRT."""
        should_ping = alert_dispatcher._should_ping_crt("critical")
        
        assert should_ping is True

    def test_no_crt_role_never_pings(self, mock_config, mock_channel_config, 
                                      mock_cooldown_manager, mock_embed_builder, 
                                      mock_bot):
        """Test no pinging when CRT role not configured."""
        from src.managers.alerting.alert_dispatcher import AlertDispatcher
        
        # Override to return None for CRT role
        mock_channel_config.get_crt_role_id.return_value = None
        
        dispatcher = AlertDispatcher(
            config_manager=mock_config,
            channel_config=mock_channel_config,
            embed_builder=mock_embed_builder,
            cooldown_manager=mock_cooldown_manager,
            bot=mock_bot,
        )
        
        assert dispatcher._should_ping_crt("critical") is False


# =============================================================================
# Channel Routing Tests
# =============================================================================


class TestChannelRouting:
    """Tests for channel routing based on severity."""

    def test_medium_routes_to_monitor(self, alert_dispatcher):
        """Test medium severity routes to monitor channel."""
        channel = alert_dispatcher._get_alert_channel("medium")
        
        assert channel is not None
        assert channel.id == 111000111
        assert channel.name == "monitor-queue"

    def test_high_routes_to_crisis(self, alert_dispatcher):
        """Test high severity routes to crisis channel."""
        channel = alert_dispatcher._get_alert_channel("high")
        
        assert channel is not None
        assert channel.id == 222000222
        assert channel.name == "crisis-response"

    def test_critical_routes_to_critical(self, alert_dispatcher):
        """Test critical severity routes to critical channel."""
        channel = alert_dispatcher._get_alert_channel("critical")
        
        assert channel is not None
        assert channel.id == 333000333
        assert channel.name == "critical-response"

    def test_unconfigured_channel_returns_none(self, alert_dispatcher, mock_channel_config):
        """Test unconfigured channel returns None."""
        mock_channel_config.get_alert_channel.return_value = None
        
        channel = alert_dispatcher._get_alert_channel("unknown")
        
        assert channel is None


# =============================================================================
# Cooldown Tests
# =============================================================================


class TestCooldownEnforcement:
    """Tests for cooldown enforcement."""

    @pytest.mark.asyncio
    async def test_alert_blocked_when_on_cooldown(
        self, alert_dispatcher, mock_message, mock_analysis_result, mock_cooldown_manager
    ):
        """Test alert is blocked when user is on cooldown."""
        mock_cooldown_manager.is_on_cooldown.return_value = True
        
        result = await alert_dispatcher.dispatch_alert(
            message=mock_message,
            result=mock_analysis_result,
        )

        assert result is None
        assert alert_dispatcher._alerts_skipped_cooldown == 1

    @pytest.mark.asyncio
    async def test_cooldown_set_after_alert(
        self, alert_dispatcher, mock_message, mock_analysis_result, mock_cooldown_manager
    ):
        """Test cooldown is set after successful alert."""
        mock_cooldown_manager.is_on_cooldown.return_value = False
        
        await alert_dispatcher.dispatch_alert(
            message=mock_message,
            result=mock_analysis_result,
        )

        mock_cooldown_manager.set_cooldown.assert_called_once_with(mock_message.author.id)

    @pytest.mark.asyncio
    async def test_force_bypasses_cooldown(
        self, alert_dispatcher, mock_message, mock_analysis_result, mock_cooldown_manager
    ):
        """Test force=True bypasses cooldown."""
        mock_cooldown_manager.is_on_cooldown.return_value = True
        
        result = await alert_dispatcher.dispatch_alert(
            message=mock_message,
            result=mock_analysis_result,
            force=True,
        )

        # Should still dispatch despite cooldown
        assert result is not None


# =============================================================================
# Dispatch Alert Tests
# =============================================================================


class TestDispatchAlert:
    """Tests for dispatch_alert method."""

    @pytest.mark.asyncio
    async def test_dispatch_alert_success(
        self, alert_dispatcher, mock_message, mock_analysis_result
    ):
        """Test successful alert dispatch."""
        result = await alert_dispatcher.dispatch_alert(
            message=mock_message,
            result=mock_analysis_result,
        )

        assert result is not None
        assert alert_dispatcher.alerts_sent == 1

    @pytest.mark.asyncio
    async def test_dispatch_alert_not_qualified(
        self, alert_dispatcher, mock_message, mock_analysis_result
    ):
        """Test alert not dispatched for non-qualifying severity."""
        mock_analysis_result.severity = "low"
        
        result = await alert_dispatcher.dispatch_alert(
            message=mock_message,
            result=mock_analysis_result,
        )

        assert result is None
        assert alert_dispatcher._alerts_skipped_severity == 1

    @pytest.mark.asyncio
    async def test_dispatch_alert_sends_to_channel(
        self, alert_dispatcher, mock_message, mock_analysis_result, mock_bot
    ):
        """Test alert is sent to correct channel."""
        await alert_dispatcher.dispatch_alert(
            message=mock_message,
            result=mock_analysis_result,
        )

        # High severity goes to crisis channel (222000222)
        crisis_channel = mock_bot.get_channel(222000222)
        crisis_channel.send.assert_called_once()

    @pytest.mark.asyncio
    async def test_dispatch_alert_includes_view(
        self, alert_dispatcher, mock_message, mock_analysis_result, mock_bot
    ):
        """Test alert includes button view."""
        await alert_dispatcher.dispatch_alert(
            message=mock_message,
            result=mock_analysis_result,
        )

        crisis_channel = mock_bot.get_channel(222000222)
        call_kwargs = crisis_channel.send.call_args.kwargs
        
        # Should include view parameter
        assert "view" in call_kwargs

    @pytest.mark.asyncio
    async def test_dispatch_alert_with_crt_ping(
        self, alert_dispatcher, mock_message, mock_analysis_result, mock_bot
    ):
        """Test high severity includes CRT ping."""
        await alert_dispatcher.dispatch_alert(
            message=mock_message,
            result=mock_analysis_result,
        )

        crisis_channel = mock_bot.get_channel(222000222)
        call_kwargs = crisis_channel.send.call_args.kwargs
        
        # Should include content with role mention
        assert "content" in call_kwargs
        assert "<@&999888777>" in call_kwargs["content"]

    @pytest.mark.asyncio
    async def test_dispatch_medium_no_crt_ping(
        self, alert_dispatcher, mock_message, mock_analysis_result, mock_bot
    ):
        """Test medium severity does NOT ping CRT."""
        mock_analysis_result.severity = "medium"
        
        await alert_dispatcher.dispatch_alert(
            message=mock_message,
            result=mock_analysis_result,
        )

        monitor_channel = mock_bot.get_channel(111000111)
        call_kwargs = monitor_channel.send.call_args.kwargs
        
        # Content should be None (no ping)
        assert call_kwargs.get("content") is None


# =============================================================================
# Dispatch Escalation Tests
# =============================================================================


class TestDispatchEscalation:
    """Tests for dispatch_escalation_alert method."""

    @pytest.mark.asyncio
    async def test_dispatch_escalation_success(
        self, alert_dispatcher, mock_message, mock_analysis_result
    ):
        """Test successful escalation dispatch."""
        result = await alert_dispatcher.dispatch_escalation_alert(
            message=mock_message,
            result=mock_analysis_result,
            history_count=5,
            trend="escalating",
        )

        assert result is not None
        assert alert_dispatcher.alerts_sent == 1

    @pytest.mark.asyncio
    async def test_escalation_uses_escalation_embed(
        self, alert_dispatcher, mock_message, mock_analysis_result, mock_embed_builder
    ):
        """Test escalation uses escalation embed builder."""
        await alert_dispatcher.dispatch_escalation_alert(
            message=mock_message,
            result=mock_analysis_result,
            history_count=5,
            trend="escalating",
        )

        mock_embed_builder.build_escalation_embed.assert_called_once()

    @pytest.mark.asyncio
    async def test_escalation_always_pings_crt(
        self, alert_dispatcher, mock_message, mock_analysis_result, mock_bot
    ):
        """Test escalation alerts always ping CRT."""
        # Even for medium severity
        mock_analysis_result.severity = "medium"
        
        await alert_dispatcher.dispatch_escalation_alert(
            message=mock_message,
            result=mock_analysis_result,
            history_count=5,
            trend="escalating",
        )

        monitor_channel = mock_bot.get_channel(111000111)
        call_kwargs = monitor_channel.send.call_args.kwargs
        
        # Should include CRT ping with ESCALATION prefix
        assert "content" in call_kwargs
        assert "ESCALATION" in call_kwargs["content"]


# =============================================================================
# Statistics Tests
# =============================================================================


class TestAlertStatistics:
    """Tests for alert statistics tracking."""

    @pytest.mark.asyncio
    async def test_alerts_sent_counter(
        self, alert_dispatcher, mock_message, mock_analysis_result
    ):
        """Test alerts_sent counter increments."""
        initial_count = alert_dispatcher.alerts_sent
        
        await alert_dispatcher.dispatch_alert(
            message=mock_message,
            result=mock_analysis_result,
        )

        assert alert_dispatcher.alerts_sent == initial_count + 1

    @pytest.mark.asyncio
    async def test_skipped_cooldown_counter(
        self, alert_dispatcher, mock_message, mock_analysis_result, mock_cooldown_manager
    ):
        """Test alerts_skipped_cooldown counter increments."""
        mock_cooldown_manager.is_on_cooldown.return_value = True
        initial_count = alert_dispatcher._alerts_skipped_cooldown
        
        await alert_dispatcher.dispatch_alert(
            message=mock_message,
            result=mock_analysis_result,
        )

        assert alert_dispatcher._alerts_skipped_cooldown == initial_count + 1

    @pytest.mark.asyncio
    async def test_skipped_severity_counter(
        self, alert_dispatcher, mock_message, mock_analysis_result
    ):
        """Test alerts_skipped_severity counter increments."""
        mock_analysis_result.severity = "low"
        initial_count = alert_dispatcher._alerts_skipped_severity
        
        await alert_dispatcher.dispatch_alert(
            message=mock_message,
            result=mock_analysis_result,
        )

        assert alert_dispatcher._alerts_skipped_severity == initial_count + 1

    def test_alerts_skipped_total(self, alert_dispatcher):
        """Test alerts_skipped returns total of skipped alerts."""
        alert_dispatcher._alerts_skipped_cooldown = 3
        alert_dispatcher._alerts_skipped_severity = 2
        
        assert alert_dispatcher.alerts_skipped == 5


# =============================================================================
# Status Tests
# =============================================================================


class TestAlertDispatcherStatus:
    """Tests for get_status method."""

    def test_get_status_returns_dict(self, alert_dispatcher):
        """Test get_status returns dictionary."""
        status = alert_dispatcher.get_status()

        assert isinstance(status, dict)

    def test_status_contains_statistics(self, alert_dispatcher):
        """Test status contains statistics."""
        status = alert_dispatcher.get_status()

        assert "alerts_sent" in status
        assert "alerts_skipped_cooldown" in status
        assert "alerts_skipped_severity" in status

    def test_status_contains_config(self, alert_dispatcher):
        """Test status contains configuration info."""
        status = alert_dispatcher.get_status()

        assert "enabled" in status
        assert "min_severity" in status
        assert "crt_role_configured" in status

    def test_repr(self, alert_dispatcher):
        """Test string representation."""
        repr_str = repr(alert_dispatcher)
        
        assert "AlertDispatcher" in repr_str
        assert "enabled=True" in repr_str


# =============================================================================
# Error Handling Tests
# =============================================================================


class TestErrorHandling:
    """Tests for error handling."""

    @pytest.mark.asyncio
    async def test_handles_missing_channel(
        self, alert_dispatcher, mock_message, mock_analysis_result, mock_channel_config
    ):
        """Test graceful handling of missing channel."""
        # Channel ID configured but bot can't find it
        # Clear side_effect so return_value takes effect
        mock_channel_config.get_alert_channel.side_effect = None
        mock_channel_config.get_alert_channel.return_value = 999999999
        
        result = await alert_dispatcher.dispatch_alert(
            message=mock_message,
            result=mock_analysis_result,
        )

        # Should return None gracefully
        assert result is None

    @pytest.mark.asyncio
    async def test_handles_send_failure(
        self, alert_dispatcher, mock_message, mock_analysis_result, mock_bot
    ):
        """Test graceful handling of send failure."""
        crisis_channel = mock_bot.get_channel(222000222)
        crisis_channel.send.side_effect = discord.HTTPException(
            MagicMock(), "Failed to send"
        )
        
        result = await alert_dispatcher.dispatch_alert(
            message=mock_message,
            result=mock_analysis_result,
        )

        assert result is None

    @pytest.mark.asyncio
    async def test_handles_forbidden(
        self, alert_dispatcher, mock_message, mock_analysis_result, mock_bot
    ):
        """Test graceful handling of permission denied."""
        crisis_channel = mock_bot.get_channel(222000222)
        crisis_channel.send.side_effect = discord.Forbidden(
            MagicMock(), "Missing permissions"
        )
        
        result = await alert_dispatcher.dispatch_alert(
            message=mock_message,
            result=mock_analysis_result,
        )

        assert result is None


# =============================================================================
# Factory Function Tests
# =============================================================================


class TestAlertDispatcherFactory:
    """Tests for factory function."""

    def test_create_alert_dispatcher(
        self, mock_config, mock_channel_config, mock_cooldown_manager,
        mock_embed_builder, mock_bot
    ):
        """Test factory function creates dispatcher."""
        from src.managers.alerting import create_alert_dispatcher

        dispatcher = create_alert_dispatcher(
            config_manager=mock_config,
            channel_config=mock_channel_config,
            embed_builder=mock_embed_builder,
            cooldown_manager=mock_cooldown_manager,
            bot=mock_bot,
        )

        assert dispatcher is not None
        assert dispatcher.is_enabled is True
