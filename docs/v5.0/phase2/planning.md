# Phase 2: Redis History Storage - Planning Document

============================================================================
**Ash-Bot**: Crisis Detection Discord Bot for The Alphabet Cartel  
**The Alphabet Cartel** - https://discord.gg/alphabetcartel | alphabetcartel.org
============================================================================

**Document Version**: v1.1.0  
**Created**: 2026-01-03  
**Updated**: 2026-01-03  
**Phase**: 2 - Redis History Storage  
**Status**: 🟡 In Progress  
**Depends On**: Phase 1 (Discord Connectivity)  
**Estimated Time**: 3-4 days

---

## Table of Contents

1. [Overview](#overview)
2. [Goals](#goals)
3. [Architecture](#architecture)
4. [File Structure](#file-structure)
5. [Implementation Details](#implementation-details)
6. [Data Schema](#data-schema)
7. [Configuration](#configuration)
8. [Testing Requirements](#testing-requirements)
9. [Step-by-Step Implementation](#step-by-step-implementation)
10. [Acceptance Criteria](#acceptance-criteria)

---

## Overview

Phase 2 implements Redis-based message history storage for context-aware crisis detection. By maintaining recent message history per user, the NLP API can detect escalation patterns over time rather than analyzing messages in isolation.

### Key Deliverables

1. Redis connection management with password authentication
2. User message history storage (severity LOW+)
3. Automatic TTL-based expiration
4. History retrieval for NLP context
5. Clean Architecture compliant managers

### Why Redis?

| Requirement | Redis Solution |
|-------------|----------------|
| Fast lookups | In-memory, O(1) key access |
| TTL expiration | Native EXPIRE support |
| Sorted history | Sorted sets with timestamps |
| Scalability | Cluster support if needed |
| Persistence | AOF/RDB backup options |

---

## Goals

### Primary Goals

| Goal | Description |
|------|-------------|
| Store History | Save messages with LOW+ severity to Redis |
| Retrieve Context | Fetch recent history for NLP context |
| Auto-Expire | TTL-based cleanup (14 days default) |
| Secure Connection | Password authentication via Docker Secrets |

### Storage Rules (From Architecture Decisions)

| Severity | Store? | Rationale |
|----------|--------|-----------|
| SAFE | ❌ No | No crisis indicators |
| LOW | ✅ Yes | May indicate developing pattern |
| MEDIUM | ✅ Yes | Confirmed concern |
| HIGH | ✅ Yes | Significant crisis |
| CRITICAL | ✅ Yes | Immediate crisis |

### Non-Goals (Deferred)

- Alert history storage (alerts are ephemeral)
- Cross-guild history (privacy boundary)
- Analytics/reporting (future feature)

---

## Architecture

### Component Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                       DiscordManager                             │
│                      (from Phase 1)                              │
└─────────────────────────┬───────────────────────────────────────┘
                          │ on_message()
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                     NLPClientManager                             │
│                      (from Phase 1)                              │
│                                                                  │
│  analyze_message(message, history) ◄── History injected here    │
└─────────────────────────┬───────────────────────────────────────┘
                          │ Returns CrisisAnalysisResult
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                   UserHistoryManager                             │
│                      (Phase 2 NEW)                               │
│                                                                  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │ add_message()   │  │ get_history()   │  │ clear_history() │  │
│  │ (if LOW+)       │  │ (for context)   │  │ (on request)    │  │
│  └────────┬────────┘  └────────┬────────┘  └─────────────────┘  │
└───────────┼────────────────────┼────────────────────────────────┘
            │                    │
            ▼                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                     RedisManager                                 │
│                      (Phase 2 NEW)                               │
│                                                                  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │ connect()       │  │ zadd/zrange     │  │ expire()        │  │
│  │ disconnect()    │  │ (sorted sets)   │  │ (TTL management)│  │
│  └────────┬────────┘  └─────────────────┘  └─────────────────┘  │
└───────────┼─────────────────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Redis Container                             │
│                       (ash-redis)                                │
│                     Port: 6379                                   │
└─────────────────────────────────────────────────────────────────┘
```

### Data Flow

```
1. Message received → NLP analysis (Phase 1)
        │
        ▼
2. UserHistoryManager.get_history(user_id)
        │
        ▼
3. Include history in NLP request
        │
        ▼
4. NLP returns CrisisAnalysisResult
        │
        ▼
5. If severity >= LOW:
   UserHistoryManager.add_message(user_id, message, result)
        │
        ▼
6. RedisManager stores with TTL
```

---

## File Structure

### New Files to Create

```
src/
├── managers/
│   └── storage/
│       ├── __init__.py                    # Package exports
│       ├── redis_manager.py               # Redis connection manager
│       └── user_history_manager.py        # User history operations
└── models/
    └── history_models.py                  # History data classes
    
tests/
└── test_storage/
    ├── __init__.py
    ├── test_redis_manager.py
    └── test_user_history_manager.py
```

### Files to Update

```
src/
├── managers/
│   ├── __init__.py                        # Add storage exports
│   └── discord/
│       └── discord_manager.py             # Inject history into NLP calls
└── main.py                                # Initialize Redis/History managers
```

---

## Implementation Details

### 1. Redis Manager (`src/managers/storage/redis_manager.py`)

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
Redis Manager for Ash-Bot Service
----------------------------------------------------------------------------
FILE VERSION: v5.0-2-1.0-1
LAST MODIFIED: {date}
PHASE: Phase 2 - Redis History Storage
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-bot
============================================================================
"""

import redis.asyncio as redis
from typing import Optional, List, Any, Dict
import logging
import json

class RedisManager:
    """
    Manages Redis connection and low-level operations.
    
    Responsibilities:
    - Establish authenticated Redis connection
    - Provide async Redis operations
    - Handle connection pooling
    - Graceful error handling
    
    Attributes:
        config_manager: ConfigManager for settings
        secrets_manager: SecretsManager for password
        client: redis.Redis async client
    """
    
    def __init__(
        self,
        config_manager: "ConfigManager",
        secrets_manager: "SecretsManager",
    ):
        """
        Initialize RedisManager.
        
        Args:
            config_manager: Configuration manager
            secrets_manager: Secrets manager for Redis password
        """
        self._config = config_manager
        self._secrets = secrets_manager
        self._client: Optional[redis.Redis] = None
        self._logger = logging.getLogger(__name__)
    
    async def connect(self) -> None:
        """
        Establish Redis connection.
        
        Raises:
            ConnectionError: If connection fails
        """
        host = self._config.get("redis", "host", "ash-redis")
        port = self._config.get("redis", "port", 6379)
        db = self._config.get("redis", "db", 0)
        password = self._secrets.get_redis_token()
        
        self._client = redis.Redis(
            host=host,
            port=port,
            db=db,
            password=password,
            decode_responses=True,
            socket_timeout=5.0,
            socket_connect_timeout=5.0,
        )
        
        # Test connection
        await self._client.ping()
        self._logger.info(f"✅ Connected to Redis at {host}:{port}")
    
    async def disconnect(self) -> None:
        """Close Redis connection."""
        if self._client:
            await self._client.close()
            self._logger.info("🔌 Disconnected from Redis")
    
    async def health_check(self) -> bool:
        """
        Check Redis connection health.
        
        Returns:
            True if Redis is responsive
        """
        try:
            if self._client:
                await self._client.ping()
                return True
            return False
        except Exception:
            return False
    
    # =========================================================================
    # Sorted Set Operations (for time-ordered history)
    # =========================================================================
    
    async def zadd(
        self,
        key: str,
        score: float,
        member: str,
    ) -> int:
        """
        Add member to sorted set with score (timestamp).
        
        Args:
            key: Redis key
            score: Score (timestamp as float)
            member: Value to store (JSON string)
            
        Returns:
            Number of elements added
        """
        return await self._client.zadd(key, {member: score})
    
    async def zrange(
        self,
        key: str,
        start: int,
        stop: int,
        desc: bool = True,
        withscores: bool = False,
    ) -> List[Any]:
        """
        Get range from sorted set.
        
        Args:
            key: Redis key
            start: Start index
            stop: Stop index (-1 for all)
            desc: Reverse order (newest first)
            withscores: Include scores in result
            
        Returns:
            List of members (optionally with scores)
        """
        if desc:
            return await self._client.zrevrange(
                key, start, stop, withscores=withscores
            )
        return await self._client.zrange(
            key, start, stop, withscores=withscores
        )
    
    async def zcard(self, key: str) -> int:
        """Get count of members in sorted set."""
        return await self._client.zcard(key)
    
    async def zremrangebyrank(
        self,
        key: str,
        start: int,
        stop: int,
    ) -> int:
        """
        Remove members by rank (for trimming old entries).
        
        Args:
            key: Redis key
            start: Start rank
            stop: Stop rank
            
        Returns:
            Number of members removed
        """
        return await self._client.zremrangebyrank(key, start, stop)
    
    # =========================================================================
    # Key Management
    # =========================================================================
    
    async def expire(self, key: str, seconds: int) -> bool:
        """
        Set TTL on a key.
        
        Args:
            key: Redis key
            seconds: TTL in seconds
            
        Returns:
            True if TTL was set
        """
        return await self._client.expire(key, seconds)
    
    async def delete(self, key: str) -> int:
        """Delete a key."""
        return await self._client.delete(key)
    
    async def exists(self, key: str) -> bool:
        """Check if key exists."""
        return await self._client.exists(key) > 0
    
    @property
    def is_connected(self) -> bool:
        """Check if client is connected."""
        return self._client is not None


def create_redis_manager(
    config_manager: "ConfigManager",
    secrets_manager: "SecretsManager",
) -> RedisManager:
    """Factory function for RedisManager."""
    return RedisManager(
        config_manager=config_manager,
        secrets_manager=secrets_manager,
    )
```

---

### 2. User History Manager (`src/managers/storage/user_history_manager.py`)

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
User History Manager for Ash-Bot Service
----------------------------------------------------------------------------
FILE VERSION: v5.0-2-2.0-1
LAST MODIFIED: {date}
PHASE: Phase 2 - Redis History Storage
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-bot
============================================================================
"""

from typing import List, Optional
from datetime import datetime, timezone
import json
import logging

from src.models.nlp_models import MessageHistoryItem, CrisisAnalysisResult

# Severity levels that qualify for storage
STORABLE_SEVERITIES = {"low", "medium", "high", "critical"}


class UserHistoryManager:
    """
    Manages user message history in Redis.
    
    Responsibilities:
    - Store messages with crisis indicators (LOW+)
    - Retrieve recent history for NLP context
    - Enforce TTL and max message limits
    - Per-user isolation
    
    Key Format:
        ash:history:{guild_id}:{user_id}
    
    Attributes:
        config_manager: ConfigManager for settings
        redis_manager: RedisManager for storage
        ttl_days: Days to retain history
        max_messages: Maximum messages per user
        min_severity: Minimum severity to store
    """
    
    def __init__(
        self,
        config_manager: "ConfigManager",
        redis_manager: "RedisManager",
    ):
        """
        Initialize UserHistoryManager.
        
        Args:
            config_manager: Configuration manager
            redis_manager: Redis manager for storage
        """
        self._config = config_manager
        self._redis = redis_manager
        self._logger = logging.getLogger(__name__)
        
        # Load configuration
        self._ttl_days = self._config.get("history", "ttl_days", 14)
        self._max_messages = self._config.get("history", "max_messages", 100)
        self._min_severity = self._config.get("history", "min_severity_to_store", "low")
        
        self._logger.info(
            f"📚 UserHistoryManager initialized "
            f"(TTL: {self._ttl_days}d, max: {self._max_messages} msgs)"
        )
    
    def _make_key(self, guild_id: int, user_id: int) -> str:
        """
        Generate Redis key for user history.
        
        Args:
            guild_id: Discord guild ID
            user_id: Discord user ID
            
        Returns:
            Redis key string
        """
        return f"ash:history:{guild_id}:{user_id}"
    
    def _should_store(self, severity: str) -> bool:
        """
        Check if message severity qualifies for storage.
        
        Args:
            severity: Crisis severity level
            
        Returns:
            True if should be stored
        """
        return severity.lower() in STORABLE_SEVERITIES
    
    async def add_message(
        self,
        guild_id: int,
        user_id: int,
        message: str,
        analysis_result: CrisisAnalysisResult,
        message_id: Optional[str] = None,
    ) -> bool:
        """
        Add a message to user's history.
        
        Only stores if severity is LOW or higher.
        
        Args:
            guild_id: Discord guild ID
            user_id: Discord user ID
            message: Original message content
            analysis_result: NLP analysis result
            message_id: Optional Discord message ID
            
        Returns:
            True if message was stored
        """
        # Check severity threshold
        if not self._should_store(analysis_result.severity):
            self._logger.debug(
                f"Skipping storage for {user_id}: "
                f"severity {analysis_result.severity} below threshold"
            )
            return False
        
        key = self._make_key(guild_id, user_id)
        timestamp = datetime.now(timezone.utc)
        
        # Create history entry
        entry = {
            "message": message[:500],  # Truncate long messages
            "timestamp": timestamp.isoformat(),
            "crisis_score": analysis_result.crisis_score,
            "severity": analysis_result.severity,
            "message_id": message_id,
        }
        
        # Score = timestamp as float for ordering
        score = timestamp.timestamp()
        
        # Add to sorted set
        await self._redis.zadd(key, score, json.dumps(entry))
        
        # Set TTL (refresh on each add)
        ttl_seconds = self._ttl_days * 24 * 60 * 60
        await self._redis.expire(key, ttl_seconds)
        
        # Trim to max messages (remove oldest)
        count = await self._redis.zcard(key)
        if count > self._max_messages:
            # Remove oldest entries (lowest scores)
            to_remove = count - self._max_messages
            await self._redis.zremrangebyrank(key, 0, to_remove - 1)
        
        self._logger.debug(
            f"📝 Stored message for user {user_id} "
            f"(severity: {analysis_result.severity}, score: {analysis_result.crisis_score:.2f})"
        )
        
        return True
    
    async def get_history(
        self,
        guild_id: int,
        user_id: int,
        limit: int = 20,
    ) -> List[MessageHistoryItem]:
        """
        Get recent message history for a user.
        
        Args:
            guild_id: Discord guild ID
            user_id: Discord user ID
            limit: Maximum messages to retrieve
            
        Returns:
            List of MessageHistoryItem (newest first)
        """
        key = self._make_key(guild_id, user_id)
        
        # Get most recent entries (highest scores = newest)
        entries = await self._redis.zrange(key, 0, limit - 1, desc=True)
        
        history = []
        for entry_json in entries:
            try:
                entry = json.loads(entry_json)
                history.append(MessageHistoryItem(
                    message=entry["message"],
                    timestamp=entry["timestamp"],
                    crisis_score=entry.get("crisis_score"),
                    message_id=entry.get("message_id"),
                ))
            except (json.JSONDecodeError, KeyError) as e:
                self._logger.warning(f"Invalid history entry: {e}")
                continue
        
        return history
    
    async def get_history_count(self, guild_id: int, user_id: int) -> int:
        """Get count of stored messages for user."""
        key = self._make_key(guild_id, user_id)
        return await self._redis.zcard(key)
    
    async def clear_history(self, guild_id: int, user_id: int) -> bool:
        """
        Clear all history for a user.
        
        Args:
            guild_id: Discord guild ID
            user_id: Discord user ID
            
        Returns:
            True if history was cleared
        """
        key = self._make_key(guild_id, user_id)
        result = await self._redis.delete(key)
        
        if result > 0:
            self._logger.info(f"🗑️ Cleared history for user {user_id}")
            return True
        return False
    
    async def has_history(self, guild_id: int, user_id: int) -> bool:
        """Check if user has any stored history."""
        key = self._make_key(guild_id, user_id)
        return await self._redis.exists(key)


def create_user_history_manager(
    config_manager: "ConfigManager",
    redis_manager: "RedisManager",
) -> UserHistoryManager:
    """Factory function for UserHistoryManager."""
    return UserHistoryManager(
        config_manager=config_manager,
        redis_manager=redis_manager,
    )
```

---

### 3. History Models (`src/models/history_models.py`)

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
History Data Models for Ash-Bot Service
----------------------------------------------------------------------------
FILE VERSION: v5.0-2-3.0-1
LAST MODIFIED: {date}
PHASE: Phase 2 - Redis History Storage
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-bot
============================================================================
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class StoredMessage:
    """
    Message stored in Redis history.
    
    Attributes:
        message: Truncated message content (max 500 chars)
        timestamp: ISO-8601 timestamp
        crisis_score: Score from NLP analysis (0.0-1.0)
        severity: Severity level (low, medium, high, critical)
        message_id: Discord message ID (optional)
    """
    message: str
    timestamp: str
    crisis_score: float
    severity: str
    message_id: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "message": self.message,
            "timestamp": self.timestamp,
            "crisis_score": self.crisis_score,
            "severity": self.severity,
            "message_id": self.message_id,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "StoredMessage":
        """Create from dictionary."""
        return cls(
            message=data["message"],
            timestamp=data["timestamp"],
            crisis_score=data["crisis_score"],
            severity=data["severity"],
            message_id=data.get("message_id"),
        )
    
    @property
    def parsed_timestamp(self) -> datetime:
        """Parse timestamp string to datetime."""
        return datetime.fromisoformat(self.timestamp.replace("Z", "+00:00"))
```

---

## Data Schema

### Redis Key Format

```
ash:history:{guild_id}:{user_id}
```

**Examples:**
- `ash:history:123456789:987654321`
- `ash:history:111222333:444555666`

### Sorted Set Structure

| Component | Description |
|-----------|-------------|
| **Key** | `ash:history:{guild_id}:{user_id}` |
| **Score** | Unix timestamp (float) for ordering |
| **Member** | JSON string with message data |

### Member JSON Format

```json
{
    "message": "Truncated message content...",
    "timestamp": "2026-01-03T12:00:00+00:00",
    "crisis_score": 0.45,
    "severity": "low",
    "message_id": "1234567890"
}
```

### TTL Management

| Setting | Default | Description |
|---------|---------|-------------|
| `history.ttl_days` | 14 | Days to retain history |
| `history.max_messages` | 100 | Max messages per user |

TTL is refreshed on each new message to keep active users' history alive.

---

## Configuration

### Required Configuration (already in default.json)

```json
{
    "redis": {
        "host": "${BOT_REDIS_HOST}",
        "port": "${BOT_REDIS_PORT}",
        "db": "${BOT_REDIS_DB}",
        "defaults": {
            "host": "ash-redis",
            "port": 6379,
            "db": 0
        }
    },
    "history": {
        "ttl_days": "${BOT_HISTORY_TTL_DAYS}",
        "max_messages": "${BOT_HISTORY_MAX_MESSAGES}",
        "min_severity_to_store": "${BOT_HISTORY_MIN_SEVERITY}",
        "defaults": {
            "ttl_days": 14,
            "max_messages": 100,
            "min_severity_to_store": "low"
        }
    }
}
```

### Required Secrets

| Secret | Location | Purpose |
|--------|----------|---------|
| `redis_token` | `secrets/redis_token` | Redis authentication |

---

## Testing Requirements

### Unit Tests

#### test_redis_manager.py

```python
"""Tests for RedisManager."""

class TestRedisManager:
    """Test suite for RedisManager."""
    
    @pytest.mark.asyncio
    async def test_connect_success(self):
        """Test successful connection."""
        pass
    
    @pytest.mark.asyncio
    async def test_connect_wrong_password(self):
        """Test connection with wrong password fails."""
        pass
    
    @pytest.mark.asyncio
    async def test_zadd_and_zrange(self):
        """Test sorted set operations."""
        pass
    
    @pytest.mark.asyncio
    async def test_expire_sets_ttl(self):
        """Test TTL is set correctly."""
        pass
    
    @pytest.mark.asyncio
    async def test_health_check(self):
        """Test health check returns correct status."""
        pass
```

#### test_user_history_manager.py

```python
"""Tests for UserHistoryManager."""

class TestUserHistoryManager:
    """Test suite for UserHistoryManager."""
    
    @pytest.mark.asyncio
    async def test_add_message_stores_low_severity(self):
        """Test LOW severity messages are stored."""
        pass
    
    @pytest.mark.asyncio
    async def test_add_message_skips_safe_severity(self):
        """Test SAFE severity messages are not stored."""
        pass
    
    @pytest.mark.asyncio
    async def test_get_history_returns_newest_first(self):
        """Test history is returned in descending order."""
        pass
    
    @pytest.mark.asyncio
    async def test_max_messages_enforced(self):
        """Test old messages are trimmed."""
        pass
    
    @pytest.mark.asyncio
    async def test_clear_history(self):
        """Test history can be cleared."""
        pass
    
    @pytest.mark.asyncio
    async def test_ttl_is_set(self):
        """Test TTL is applied to keys."""
        pass
```

### Integration Tests

```python
"""Integration tests for Phase 2."""

@pytest.mark.integration
class TestPhase2Integration:
    """Integration tests requiring live Redis."""
    
    @pytest.mark.asyncio
    async def test_redis_connection(self):
        """Test connection to ash-redis container."""
        pass
    
    @pytest.mark.asyncio
    async def test_full_history_cycle(self):
        """Test add → retrieve → clear cycle."""
        pass
```

---

## Step-by-Step Implementation

### Step 2.1: Create Package Structure

1. Create `src/managers/storage/__init__.py`
2. Create `tests/test_storage/__init__.py`

### Step 2.2: Implement History Models

1. Create `src/models/history_models.py`
2. Implement `StoredMessage` dataclass
3. Add to `src/models/__init__.py` exports

### Step 2.3: Implement Redis Manager

1. Create `src/managers/storage/redis_manager.py`
2. Implement connection management
3. Implement sorted set operations
4. Implement TTL management
5. Write unit tests

### Step 2.4: Implement User History Manager

1. Create `src/managers/storage/user_history_manager.py`
2. Implement `add_message()` with severity filtering
3. Implement `get_history()` with limit
4. Implement trimming logic
5. Implement `clear_history()`
6. Write unit tests

### Step 2.5: Update Secrets Manager

1. Ensure `get_redis_token()` method exists (already added in Phase 0)
2. Verify Redis secret loading works

### Step 2.6: Integrate with Discord Manager

1. Update `discord_manager.py` to inject history into NLP calls
2. Update `discord_manager.py` to store results after analysis
3. Update flow: message → get_history → analyze → store_if_needed

### Step 2.7: Update Main Entry Point

1. Initialize RedisManager in `main.py`
2. Initialize UserHistoryManager in `main.py`
3. Pass UserHistoryManager to DiscordManager
4. Add Redis health check on startup

### Step 2.8: Integration Testing

1. Test against live ash-redis container
2. Verify history accumulates correctly
3. Verify TTL expiration works
4. Verify max_messages trimming works

### Step 2.9: Update Package Exports

1. Update `src/managers/__init__.py`
2. Update `src/managers/storage/__init__.py`

---

## Acceptance Criteria

### Must Have

- [ ] Redis connection established with authentication
- [ ] Messages with LOW+ severity stored in Redis
- [ ] Messages with SAFE severity NOT stored
- [ ] History retrieved in newest-first order
- [ ] TTL automatically expires old history
- [ ] Max messages limit enforced (trimming)
- [ ] History passed to NLP for context
- [ ] All managers use factory function pattern
- [ ] All new files have correct header format
- [ ] All unit tests passing

### Should Have

- [ ] Redis health check on startup
- [ ] Graceful handling of Redis unavailability
- [ ] History count logging

### Nice to Have

- [ ] Clear history slash command (future)
- [ ] History statistics endpoint (future)

---

## Notes

```
Implementation notes will be added here as we progress...
```

---

**Built with care for chosen family** 🏳️‍🌈
