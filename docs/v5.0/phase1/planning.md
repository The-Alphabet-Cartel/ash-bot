# Phase 1: Discord Connectivity - Planning Document

============================================================================
**Ash-Bot**: Crisis Detection Discord Bot for The Alphabet Cartel  
**The Alphabet Cartel** - https://discord.gg/alphabetcartel | alphabetcartel.org
============================================================================

**Document Version**: v1.1.0  
**Created**: 2026-01-03  
**Completed**: 2026-01-03  
**Phase**: 1 - Discord Connectivity  
**Status**: 🟢 Complete  
**Estimated Time**: 1 week  
**Actual Time**: ~8 hours

---

## Table of Contents

1. [Overview](#overview)
2. [Goals](#goals)
3. [Architecture](#architecture)
4. [File Structure](#file-structure)
5. [Implementation Details](#implementation-details)
6. [Configuration](#configuration)
7. [Testing Requirements](#testing-requirements)
8. [Integration Points](#integration-points)
9. [Step-by-Step Implementation](#step-by-step-implementation)
10. [Acceptance Criteria](#acceptance-criteria)

---

## Overview

Phase 1 establishes the core Discord connectivity layer for Ash-Bot. This phase creates the foundation for all Discord interactions including message monitoring, channel filtering, and NLP integration.

### Key Deliverables

1. Bot connects to Discord gateway successfully
2. Bot monitors only whitelisted channels
3. Bot sends messages to Ash-NLP API for classification
4. Bot logs all classification results
5. All managers follow Clean Architecture patterns

---

## Goals

### Primary Goals

| Goal | Description |
|------|-------------|
| Discord Connection | Establish stable gateway connection using discord.py |
| Channel Filtering | Only process messages from whitelisted channels |
| NLP Integration | Send messages to Ash-NLP API and receive classification |
| Logging | Comprehensive logging of all operations |

### Non-Goals (Deferred to Later Phases)

- Alert dispatching (Phase 3)
- Redis storage (Phase 2)
- Ash AI responses (Phase 4)
- Button interactions (Phase 3)

---

## Architecture

### Component Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         main.py                                  │
│                    (Entry Point)                                 │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DiscordManager                                │
│              (Gateway Connection)                                │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │  on_ready()  │  │ on_message() │  │ connect()/disconnect()│  │
│  └──────────────┘  └──────┬───────┘  └──────────────────────┘  │
└─────────────────────────────┼───────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│ChannelConfig    │  │  NLPClient      │  │  ConfigManager  │
│Manager          │  │  Manager        │  │  (existing)     │
│                 │  │                 │  │                 │
│is_monitored()   │  │analyze_message()│  │get_section()    │
│get_alert_channel│  │                 │  │                 │
└─────────────────┘  └────────┬────────┘  └─────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │   Ash-NLP API   │
                    │ http://ash-nlp  │
                    │    :30880       │
                    └─────────────────┘
```

### Data Flow

```
1. Discord Message Received
        │
        ▼
2. ChannelConfigManager.is_monitored(channel_id)
        │
        ├── False → Ignore message
        │
        ▼ True
3. NLPClientManager.analyze_message(content, user_id, history)
        │
        ▼
4. Ash-NLP API → Returns CrisisAnalysisResult
        │
        ▼
5. Log result (Phase 1 only - alerting in Phase 3)
```

---

## File Structure

### New Files to Create

```
src/
├── managers/
│   ├── discord/
│   │   ├── __init__.py                    # Package exports
│   │   ├── discord_manager.py             # Main Discord manager
│   │   └── channel_config_manager.py      # Channel whitelist manager
│   └── nlp/
│       ├── __init__.py                    # Package exports
│       └── nlp_client_manager.py          # Ash-NLP API client
└── models/
    ├── __init__.py                        # Package exports
    └── nlp_models.py                      # Data classes for NLP responses

tests/
├── test_discord/
│   ├── __init__.py
│   ├── test_discord_manager.py
│   └── test_channel_config.py
└── test_nlp/
    ├── __init__.py
    └── test_nlp_client.py
```

### Files to Update

```
src/
├── managers/
│   └── __init__.py                        # Add new exports
└── main.py                                # Add bot initialization

tests/
└── conftest.py                            # Add new fixtures
```

---

## Implementation Details

### 1. Discord Manager (`src/managers/discord/discord_manager.py`)

#### Class Design

```python
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
Discord Manager for Ash-Bot Service
----------------------------------------------------------------------------
FILE VERSION: v5.0-1-1.0-1
LAST MODIFIED: {date}
PHASE: Phase 1 - Discord Connectivity
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-bot
============================================================================
"""

import discord
from discord.ext import commands
from typing import Optional, Callable, Awaitable
import logging
import asyncio

class DiscordManager:
    """
    Manages Discord gateway connection and event handling.
    
    Responsibilities:
    - Establish and maintain Discord gateway connection
    - Handle on_ready and on_message events
    - Route messages to appropriate handlers
    - Graceful shutdown handling
    
    Attributes:
        bot: discord.ext.commands.Bot instance
        config_manager: ConfigManager for settings
        channel_config: ChannelConfigManager for whitelist
        nlp_client: NLPClientManager for analysis
        message_handler: Callback for processed messages
    """
    
    def __init__(
        self,
        config_manager: "ConfigManager",
        secrets_manager: "SecretsManager",
        channel_config: "ChannelConfigManager",
        nlp_client: "NLPClientManager",
    ):
        """
        Initialize DiscordManager with dependencies.
        
        Args:
            config_manager: Configuration manager instance
            secrets_manager: Secrets manager for bot token
            channel_config: Channel configuration manager
            nlp_client: NLP client for message analysis
        """
        pass
    
    async def connect(self) -> None:
        """
        Connect to Discord gateway.
        
        Raises:
            ConnectionError: If connection fails
            ValueError: If bot token is missing
        """
        pass
    
    async def disconnect(self) -> None:
        """
        Gracefully disconnect from Discord.
        """
        pass
    
    async def _on_ready(self) -> None:
        """
        Handle bot ready event.
        
        Logs connection status and guild information.
        """
        pass
    
    async def _on_message(self, message: discord.Message) -> None:
        """
        Handle incoming messages.
        
        Flow:
        1. Ignore bot messages
        2. Check if channel is monitored
        3. Send to NLP for analysis
        4. Log results (Phase 1) / Dispatch alerts (Phase 3)
        
        Args:
            message: Discord message object
        """
        pass
    
    def _setup_intents(self) -> discord.Intents:
        """
        Configure Discord intents.
        
        Required intents:
        - guilds: For guild information
        - guild_messages: For message events
        - message_content: For message content access
        - members: For user information
        
        Returns:
            Configured Intents object
        """
        pass
    
    @property
    def is_connected(self) -> bool:
        """Check if bot is connected to Discord."""
        pass


def create_discord_manager(
    config_manager: "ConfigManager",
    secrets_manager: "SecretsManager",
    channel_config: "ChannelConfigManager",
    nlp_client: "NLPClientManager",
) -> DiscordManager:
    """
    Factory function for DiscordManager.
    
    Args:
        config_manager: Configuration manager
        secrets_manager: Secrets manager
        channel_config: Channel config manager
        nlp_client: NLP client manager
    
    Returns:
        Configured DiscordManager instance
    """
    return DiscordManager(
        config_manager=config_manager,
        secrets_manager=secrets_manager,
        channel_config=channel_config,
        nlp_client=nlp_client,
    )
```

#### Key Implementation Notes

1. **Intents Configuration**:
   ```python
   intents = discord.Intents.default()
   intents.message_content = True  # Required for reading message content
   intents.guilds = True
   intents.members = True
   ```

2. **Bot Token Loading**:
   - Load from SecretsManager: `secrets_manager.get_discord_bot_token()`
   - Validate token exists before connecting
   - Never log the token value

3. **Graceful Shutdown**:
   - Handle SIGINT/SIGTERM signals
   - Close bot connection cleanly
   - Log shutdown reason

4. **Error Handling**:
   - Catch and log Discord API errors
   - Implement reconnection logic (discord.py handles this)
   - Don't crash on individual message failures

---

### 2. Channel Config Manager (`src/managers/discord/channel_config_manager.py`)

#### Class Design

```python
class ChannelConfigManager:
    """
    Manages channel whitelist and alert routing configuration.
    
    Responsibilities:
    - Load channel whitelist from configuration
    - Check if channels should be monitored
    - Route alerts to appropriate channels by severity
    - Cache lookups for performance
    
    Attributes:
        config_manager: ConfigManager for settings
        monitored_channels: Set of monitored channel IDs
        alert_channels: Dict mapping severity to channel ID
    """
    
    def __init__(self, config_manager: "ConfigManager"):
        """
        Initialize ChannelConfigManager.
        
        Args:
            config_manager: Configuration manager instance
        """
        pass
    
    def is_monitored_channel(self, channel_id: int) -> bool:
        """
        Check if a channel should be monitored.
        
        Args:
            channel_id: Discord channel ID
            
        Returns:
            True if channel is in whitelist
        """
        pass
    
    def get_alert_channel(self, severity: str) -> Optional[int]:
        """
        Get the alert channel for a given severity.
        
        Args:
            severity: Crisis severity (medium, high, critical)
            
        Returns:
            Channel ID or None if not configured
        """
        pass
    
    def reload_config(self) -> None:
        """
        Reload channel configuration from ConfigManager.
        
        Call this if configuration changes at runtime.
        """
        pass
    
    @property
    def monitored_channel_count(self) -> int:
        """Get count of monitored channels."""
        pass


def create_channel_config_manager(
    config_manager: "ConfigManager",
) -> ChannelConfigManager:
    """Factory function for ChannelConfigManager."""
    return ChannelConfigManager(config_manager=config_manager)
```

#### Configuration Mapping

| Config Key | Purpose |
|------------|---------|
| `channels.monitored_channels` | List of channel IDs to monitor |
| `channels.alert_channel_monitor` | MEDIUM severity alerts |
| `channels.alert_channel_crisis` | HIGH severity alerts |
| `channels.alert_channel_critical` | CRITICAL severity alerts |

---

### 3. NLP Client Manager (`src/managers/nlp/nlp_client_manager.py`)

#### Class Design

```python
import httpx
from typing import Optional, List, Dict, Any
from dataclasses import dataclass

@dataclass
class MessageHistoryItem:
    """Single item in message history for context."""
    message: str
    timestamp: str
    crisis_score: Optional[float] = None
    message_id: Optional[str] = None


@dataclass  
class CrisisAnalysisResult:
    """Result from Ash-NLP analysis."""
    crisis_detected: bool
    severity: str  # safe, low, medium, high, critical
    confidence: float
    crisis_score: float
    requires_intervention: bool
    recommended_action: str
    signals: Dict[str, Any]
    request_id: str
    processing_time_ms: float
    
    # Optional fields (may not always be present)
    explanation: Optional[Dict[str, Any]] = None
    consensus: Optional[Dict[str, Any]] = None
    conflict_analysis: Optional[Dict[str, Any]] = None
    context_analysis: Optional[Dict[str, Any]] = None


class NLPClientManager:
    """
    Async HTTP client for Ash-NLP API.
    
    Responsibilities:
    - Send messages to Ash-NLP for analysis
    - Handle request timeouts and retries
    - Parse and validate responses
    - Connection pooling for performance
    
    Attributes:
        config_manager: ConfigManager for settings
        base_url: Ash-NLP API base URL
        timeout: Request timeout in seconds
        retry_attempts: Number of retry attempts
        client: httpx.AsyncClient instance
    """
    
    def __init__(self, config_manager: "ConfigManager"):
        """
        Initialize NLPClientManager.
        
        Args:
            config_manager: Configuration manager instance
        """
        pass
    
    async def analyze_message(
        self,
        message: str,
        user_id: Optional[str] = None,
        channel_id: Optional[str] = None,
        message_history: Optional[List[MessageHistoryItem]] = None,
        user_timezone: Optional[str] = None,
    ) -> CrisisAnalysisResult:
        """
        Analyze a message for crisis signals.
        
        Args:
            message: Message content to analyze
            user_id: Optional Discord user ID
            channel_id: Optional Discord channel ID
            message_history: Optional list of previous messages
            user_timezone: Optional user timezone (IANA format)
            
        Returns:
            CrisisAnalysisResult with analysis details
            
        Raises:
            NLPClientError: If API call fails after retries
        """
        pass
    
    async def health_check(self) -> bool:
        """
        Check if Ash-NLP API is healthy.
        
        Returns:
            True if API is healthy and ready
        """
        pass
    
    async def close(self) -> None:
        """Close the HTTP client connection pool."""
        pass
    
    async def __aenter__(self) -> "NLPClientManager":
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, *args) -> None:
        """Async context manager exit."""
        await self.close()


class NLPClientError(Exception):
    """Raised when NLP API calls fail."""
    pass


def create_nlp_client_manager(
    config_manager: "ConfigManager",
) -> NLPClientManager:
    """Factory function for NLPClientManager."""
    return NLPClientManager(config_manager=config_manager)
```

#### API Request Format

```python
# POST /analyze
request_body = {
    "message": "I'm feeling really down today",
    "user_id": "123456789",
    "channel_id": "987654321",
    "include_explanation": True,
    "verbosity": "standard",
    "message_history": [
        {
            "message": "Previous message",
            "timestamp": "2026-01-03T10:00:00Z",
            "crisis_score": 0.3
        }
    ],
    "user_timezone": "America/Los_Angeles"
}
```

#### Retry Logic

```python
async def _make_request_with_retry(self, ...) -> dict:
    """Make request with exponential backoff retry."""
    last_error = None
    
    for attempt in range(self.retry_attempts + 1):
        try:
            response = await self.client.post(
                f"{self.base_url}/analyze",
                json=request_body,
                timeout=self.timeout,
            )
            response.raise_for_status()
            return response.json()
            
        except httpx.TimeoutException as e:
            last_error = e
            if attempt < self.retry_attempts:
                await asyncio.sleep(self.retry_delay * (2 ** attempt))
                
        except httpx.HTTPStatusError as e:
            # Don't retry on 4xx errors
            if 400 <= e.response.status_code < 500:
                raise NLPClientError(f"Client error: {e}")
            last_error = e
            if attempt < self.retry_attempts:
                await asyncio.sleep(self.retry_delay * (2 ** attempt))
    
    raise NLPClientError(f"Failed after {self.retry_attempts} retries: {last_error}")
```

---

### 4. NLP Models (`src/models/nlp_models.py`)

```python
"""
Data models for NLP API responses.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from datetime import datetime


@dataclass
class MessageHistoryItem:
    """Single item in message history for context."""
    message: str
    timestamp: str
    crisis_score: Optional[float] = None
    message_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to API request format."""
        result = {
            "message": self.message,
            "timestamp": self.timestamp,
        }
        if self.crisis_score is not None:
            result["crisis_score"] = self.crisis_score
        if self.message_id is not None:
            result["message_id"] = self.message_id
        return result


@dataclass
class SignalResult:
    """Individual model signal result."""
    label: str
    score: float
    crisis_signal: float


@dataclass
class CrisisAnalysisResult:
    """Complete result from Ash-NLP analysis."""
    
    # Required fields
    crisis_detected: bool
    severity: str
    confidence: float
    crisis_score: float
    requires_intervention: bool
    recommended_action: str
    request_id: str
    timestamp: str
    processing_time_ms: float
    models_used: List[str]
    is_degraded: bool
    
    # Signal results
    signals: Dict[str, SignalResult] = field(default_factory=dict)
    
    # Optional detailed analysis
    explanation: Optional[Dict[str, Any]] = None
    consensus: Optional[Dict[str, Any]] = None
    conflict_analysis: Optional[Dict[str, Any]] = None
    context_analysis: Optional[Dict[str, Any]] = None
    
    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> "CrisisAnalysisResult":
        """Create from API response dictionary."""
        # Parse signals
        signals = {}
        for model_name, signal_data in data.get("signals", {}).items():
            signals[model_name] = SignalResult(
                label=signal_data["label"],
                score=signal_data["score"],
                crisis_signal=signal_data["crisis_signal"],
            )
        
        return cls(
            crisis_detected=data["crisis_detected"],
            severity=data["severity"],
            confidence=data["confidence"],
            crisis_score=data["crisis_score"],
            requires_intervention=data["requires_intervention"],
            recommended_action=data["recommended_action"],
            request_id=data["request_id"],
            timestamp=data["timestamp"],
            processing_time_ms=data["processing_time_ms"],
            models_used=data["models_used"],
            is_degraded=data["is_degraded"],
            signals=signals,
            explanation=data.get("explanation"),
            consensus=data.get("consensus"),
            conflict_analysis=data.get("conflict_analysis"),
            context_analysis=data.get("context_analysis"),
        )
    
    @property
    def is_crisis(self) -> bool:
        """Convenience property for crisis check."""
        return self.crisis_detected
    
    @property
    def is_actionable(self) -> bool:
        """Check if this result requires action (MEDIUM+)."""
        return self.severity in ("medium", "high", "critical")
```

---

## Configuration

### Required Configuration (default.json)

Already added in Phase 0:

```json
{
    "discord": {
        "guild_id": "${BOT_DISCORD_GUILD_ID}",
        "defaults": { "guild_id": null }
    },
    "channels": {
        "monitored_channels": "${BOT_MONITORED_CHANNELS}",
        "alert_channel_monitor": "${BOT_ALERT_CHANNEL_MONITOR}",
        "alert_channel_crisis": "${BOT_ALERT_CHANNEL_CRISIS}",
        "alert_channel_critical": "${BOT_ALERT_CHANNEL_CRITICAL}",
        "defaults": {
            "monitored_channels": [],
            "alert_channel_monitor": null,
            "alert_channel_crisis": null,
            "alert_channel_critical": null
        }
    },
    "nlp": {
        "base_url": "${BOT_NLP_BASE_URL}",
        "timeout_seconds": "${BOT_NLP_TIMEOUT}",
        "retry_attempts": "${BOT_NLP_RETRIES}",
        "retry_delay_seconds": "${BOT_NLP_RETRY_DELAY}",
        "defaults": {
            "base_url": "http://ash-nlp:30880",
            "timeout_seconds": 5,
            "retry_attempts": 2,
            "retry_delay_seconds": 1
        }
    }
}
```

### Required Secrets

| Secret | Location | Purpose |
|--------|----------|---------|
| `discord_bot_token` | `secrets/discord_bot_token` | Discord bot authentication |

---

## Testing Requirements

### Unit Tests

#### test_discord_manager.py

```python
"""Tests for DiscordManager."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

class TestDiscordManager:
    """Test suite for DiscordManager."""
    
    def test_create_discord_manager(self, test_config_manager):
        """Test factory function creates manager."""
        pass
    
    def test_intents_configuration(self):
        """Test that required intents are enabled."""
        pass
    
    def test_connect_without_token_raises(self):
        """Test that connect raises if no token."""
        pass
    
    @pytest.mark.asyncio
    async def test_on_message_ignores_bot_messages(self):
        """Test that bot messages are ignored."""
        pass
    
    @pytest.mark.asyncio
    async def test_on_message_ignores_unmonitored_channels(self):
        """Test that unmonitored channels are ignored."""
        pass
    
    @pytest.mark.asyncio
    async def test_on_message_sends_to_nlp(self):
        """Test that monitored messages are sent to NLP."""
        pass
```

#### test_channel_config.py

```python
"""Tests for ChannelConfigManager."""

class TestChannelConfigManager:
    """Test suite for ChannelConfigManager."""
    
    def test_create_channel_config_manager(self):
        """Test factory function."""
        pass
    
    def test_is_monitored_channel_true(self):
        """Test returns True for whitelisted channel."""
        pass
    
    def test_is_monitored_channel_false(self):
        """Test returns False for non-whitelisted channel."""
        pass
    
    def test_get_alert_channel_medium(self):
        """Test returns correct channel for MEDIUM."""
        pass
    
    def test_get_alert_channel_high(self):
        """Test returns correct channel for HIGH."""
        pass
    
    def test_get_alert_channel_critical(self):
        """Test returns correct channel for CRITICAL."""
        pass
    
    def test_empty_whitelist(self):
        """Test behavior with empty whitelist."""
        pass
```

#### test_nlp_client.py

```python
"""Tests for NLPClientManager."""

class TestNLPClientManager:
    """Test suite for NLPClientManager."""
    
    def test_create_nlp_client_manager(self):
        """Test factory function."""
        pass
    
    @pytest.mark.asyncio
    async def test_analyze_message_success(self):
        """Test successful message analysis."""
        pass
    
    @pytest.mark.asyncio
    async def test_analyze_message_timeout_retry(self):
        """Test retry on timeout."""
        pass
    
    @pytest.mark.asyncio
    async def test_analyze_message_max_retries(self):
        """Test failure after max retries."""
        pass
    
    @pytest.mark.asyncio
    async def test_health_check_healthy(self):
        """Test health check returns True when healthy."""
        pass
    
    @pytest.mark.asyncio
    async def test_health_check_unhealthy(self):
        """Test health check returns False when unhealthy."""
        pass
    
    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Test async context manager."""
        pass
```

### Integration Tests

```python
"""Integration tests for Phase 1."""

@pytest.mark.integration
class TestPhase1Integration:
    """Integration tests requiring live services."""
    
    @pytest.mark.asyncio
    async def test_nlp_api_reachable(self):
        """Test that Ash-NLP API is reachable."""
        pass
    
    @pytest.mark.asyncio
    async def test_full_message_flow(self):
        """Test complete message → NLP → result flow."""
        pass
```

---

## Integration Points

### With Existing Code

| Component | Integration Point |
|-----------|------------------|
| ConfigManager | Load NLP, Discord, Channel settings |
| SecretsManager | Load Discord bot token |
| main.py | Initialize and start bot |

### With Future Phases

| Phase | Integration Point |
|-------|------------------|
| Phase 2 | Pass NLP results to UserHistoryManager |
| Phase 3 | Pass NLP results to AlertDispatcher |
| Phase 4 | Pass NLP results to AshPersonalityManager |

---

## Step-by-Step Implementation

### Step 1.1: Create Package Structure

1. Create `src/managers/discord/__init__.py`
2. Create `src/managers/nlp/__init__.py`
3. Create `src/models/__init__.py`
4. Create test directories

### Step 1.2: Implement NLP Models

1. Create `src/models/nlp_models.py`
2. Implement `MessageHistoryItem` dataclass
3. Implement `SignalResult` dataclass
4. Implement `CrisisAnalysisResult` dataclass
5. Write unit tests

### Step 1.3: Implement NLP Client Manager

1. Create `src/managers/nlp/nlp_client_manager.py`
2. Implement `NLPClientManager` class
3. Implement `analyze_message()` method
4. Implement retry logic
5. Implement health check
6. Write unit tests
7. Test against live Ash-NLP API

### Step 1.4: Implement Channel Config Manager

1. Create `src/managers/discord/channel_config_manager.py`
2. Implement `ChannelConfigManager` class
3. Implement whitelist loading
4. Implement `is_monitored_channel()` method
5. Implement `get_alert_channel()` method
6. Write unit tests

### Step 1.5: Implement Discord Manager

1. Create `src/managers/discord/discord_manager.py`
2. Implement `DiscordManager` class
3. Implement intents configuration
4. Implement `connect()` / `disconnect()` methods
5. Implement `on_ready` handler
6. Implement `on_message` handler
7. Write unit tests

### Step 1.6: Update Main Entry Point

1. Update `main.py` with async event loop
2. Initialize all managers in correct order
3. Add signal handlers for graceful shutdown
4. Add startup validation (token exists, NLP reachable)

### Step 1.7: Integration Testing

1. Test bot connects to Discord
2. Test message flow end-to-end
3. Test with various message types
4. Test error handling

### Step 1.8: Update Package Exports

1. Update `src/managers/__init__.py`
2. Update `src/managers/discord/__init__.py`
3. Update `src/managers/nlp/__init__.py`
4. Update `src/models/__init__.py`

---

## Acceptance Criteria

### Must Have

- [x] Bot connects to Discord successfully
- [x] Bot logs "Ready" with guild/channel count
- [x] Bot ignores messages from non-whitelisted channels
- [x] Bot sends messages to Ash-NLP API
- [x] Bot logs NLP analysis results
- [x] Bot handles NLP API timeouts gracefully
- [x] Bot handles NLP API errors gracefully
- [x] All managers use factory function pattern
- [x] All new files have correct header format
- [x] All unit tests passing (77/77)

### Should Have

- [x] Health check for NLP API on startup
- [x] Graceful shutdown on SIGINT/SIGTERM
- [x] Reconnection handling (via discord.py)

### Nice to Have

- [ ] Metrics logging (messages processed, latency) - Deferred to Phase 5
- [x] Debug logging toggle

---

## Notes

### Completion Notes (2026-01-03)

Phase 1 completed successfully in approximately 8 hours (vs. 1 week estimate).

**Key accomplishments:**
- 12 new files created
- 3 files updated
- 77 unit tests written and passing
- Full NLP integration with retry logic
- Clean Architecture patterns throughout

**Issues resolved during implementation:**
1. ConfigManager cleanup (removed Ash-NLP consensus code)
2. Test configuration URL alignment
3. Async test handling for Discord.py
4. Exception export completeness
5. Context manager close logic

**See also:** [Phase 1 Completion Report](complete.md)

---

**Built with care for chosen family** 🏳️‍🌈
