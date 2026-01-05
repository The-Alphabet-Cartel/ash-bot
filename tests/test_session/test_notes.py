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
Unit Tests for NotesManager (Phase 9.2)
----------------------------------------------------------------------------
FILE VERSION: v5.0-9-2.0-1
LAST MODIFIED: 2026-01-05
PHASE: Phase 9 - CRT Workflow Enhancements (Step 9.2)
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-bot
============================================================================

USAGE:
    docker exec ash-bot python3.11 -m pytest tests/test_notes.py -v
"""

import json
import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))


# =============================================================================
# Module version
# =============================================================================

__version__ = "v5.0-9-2.0-1"


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def mock_config_manager():
    """Create mock ConfigManager."""
    config = MagicMock()
    
    def get_config(section, key, default=None):
        configs = {
            ("handoff", "notes_channel_id"): "123456789",
            ("data_retention", "session_data_days"): 30,
        }
        return configs.get((section, key), default)
    
    config.get = MagicMock(side_effect=get_config)
    return config


@pytest.fixture
def mock_config_manager_no_channel():
    """Create mock ConfigManager with no notes channel."""
    config = MagicMock()
    
    def get_config(section, key, default=None):
        configs = {
            ("handoff", "notes_channel_id"): None,
            ("data_retention", "session_data_days"): 30,
        }
        return configs.get((section, key), default)
    
    config.get = MagicMock(side_effect=get_config)
    return config


@pytest.fixture
def mock_redis_manager():
    """Create mock RedisManager."""
    redis = MagicMock()
    redis.rpush = AsyncMock(return_value=1)
    redis.lrange = AsyncMock(return_value=[])
    redis.get = AsyncMock(return_value=None)
    redis.set = AsyncMock(return_value=True)
    redis.expire = AsyncMock(return_value=True)
    redis.exists = AsyncMock(return_value=False)
    return redis


@pytest.fixture
def mock_bot():
    """Create mock Discord bot."""
    bot = MagicMock()
    
    # Mock channel
    channel = MagicMock()
    channel.send = AsyncMock(return_value=MagicMock())
    
    bot.get_channel = MagicMock(return_value=channel)
    bot.fetch_channel = AsyncMock(return_value=channel)
    
    return bot


# =============================================================================
# NotesManager Tests
# =============================================================================


class TestNotesManagerInitialization:
    """Tests for NotesManager initialization."""
    
    def test_initialization_with_channel(self, mock_config_manager, mock_redis_manager):
        """Test initialization with notes channel configured."""
        from src.managers.session.notes_manager import create_notes_manager
        
        manager = create_notes_manager(
            config_manager=mock_config_manager,
            redis_manager=mock_redis_manager,
        )
        
        assert manager is not None
        assert manager.notes_channel_id == 123456789
        assert manager.is_notes_channel_configured is True
    
    def test_initialization_without_channel(self, mock_config_manager_no_channel, mock_redis_manager):
        """Test initialization without notes channel configured."""
        from src.managers.session.notes_manager import create_notes_manager
        
        manager = create_notes_manager(
            config_manager=mock_config_manager_no_channel,
            redis_manager=mock_redis_manager,
        )
        
        assert manager is not None
        assert manager.notes_channel_id is None
        assert manager.is_notes_channel_configured is False
    
    def test_initialization_without_redis(self, mock_config_manager):
        """Test initialization without Redis."""
        from src.managers.session.notes_manager import create_notes_manager
        
        manager = create_notes_manager(
            config_manager=mock_config_manager,
            redis_manager=None,
        )
        
        assert manager is not None


class TestNotesManagerAddNote:
    """Tests for adding notes."""
    
    @pytest.mark.asyncio
    async def test_add_note_success(self, mock_config_manager, mock_redis_manager):
        """Test adding a note successfully."""
        from src.managers.session.notes_manager import create_notes_manager
        
        manager = create_notes_manager(
            config_manager=mock_config_manager,
            redis_manager=mock_redis_manager,
        )
        
        success, message, note = await manager.add_note(
            session_id="test_session",
            author_id=12345,
            author_name="TestUser",
            note_text="This is a test note.",
        )
        
        assert success is True
        assert "test_session" in message
        assert note is not None
        assert note.note_text == "This is a test note."
        assert note.author_name == "TestUser"
        
        # Verify Redis was called
        mock_redis_manager.rpush.assert_called_once()
        mock_redis_manager.expire.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_add_note_without_redis(self, mock_config_manager):
        """Test adding note without Redis fails gracefully."""
        from src.managers.session.notes_manager import create_notes_manager
        
        manager = create_notes_manager(
            config_manager=mock_config_manager,
            redis_manager=None,
        )
        
        success, message, note = await manager.add_note(
            session_id="test_session",
            author_id=12345,
            author_name="TestUser",
            note_text="This is a test note.",
        )
        
        assert success is False
        assert "not available" in message.lower()
        assert note is None


class TestNotesManagerGetNotes:
    """Tests for retrieving notes."""
    
    @pytest.mark.asyncio
    async def test_get_notes_empty(self, mock_config_manager, mock_redis_manager):
        """Test getting notes when none exist."""
        from src.managers.session.notes_manager import create_notes_manager
        
        manager = create_notes_manager(
            config_manager=mock_config_manager,
            redis_manager=mock_redis_manager,
        )
        
        notes = await manager.get_notes("nonexistent_session")
        
        assert notes == []
    
    @pytest.mark.asyncio
    async def test_get_notes_with_data(self, mock_config_manager, mock_redis_manager):
        """Test getting notes when data exists."""
        from src.managers.session.notes_manager import create_notes_manager
        
        # Setup mock to return note data
        note_data = {
            "note_id": "note_123",
            "session_id": "test_session",
            "author_id": 12345,
            "author_name": "TestUser",
            "note_text": "Test note content",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        mock_redis_manager.lrange = AsyncMock(return_value=[json.dumps(note_data)])
        
        manager = create_notes_manager(
            config_manager=mock_config_manager,
            redis_manager=mock_redis_manager,
        )
        
        notes = await manager.get_notes("test_session")
        
        assert len(notes) == 1
        assert notes[0].note_text == "Test note content"
        assert notes[0].author_name == "TestUser"


class TestNotesManagerSessionMetadata:
    """Tests for session metadata storage."""
    
    @pytest.mark.asyncio
    async def test_store_session_metadata(self, mock_config_manager, mock_redis_manager):
        """Test storing session metadata."""
        from src.managers.session.notes_manager import create_notes_manager
        
        manager = create_notes_manager(
            config_manager=mock_config_manager,
            redis_manager=mock_redis_manager,
        )
        
        result = await manager.store_session_metadata(
            session_id="test_session",
            user_id=12345,
            user_name="TestUser",
            severity="high",
            started_at=datetime.now(timezone.utc),
        )
        
        assert result is True
        mock_redis_manager.set.assert_called_once()
        mock_redis_manager.expire.assert_called()
    
    @pytest.mark.asyncio
    async def test_update_session_end(self, mock_config_manager, mock_redis_manager):
        """Test updating session end data."""
        from src.managers.session.notes_manager import create_notes_manager
        
        # Setup mock to return existing metadata
        existing_meta = {
            "session_id": "test_session",
            "user_id": 12345,
            "user_name": "TestUser",
            "severity": "high",
            "started_at": datetime.now(timezone.utc).isoformat(),
            "status": "active",
        }
        mock_redis_manager.get = AsyncMock(return_value=json.dumps(existing_meta))
        
        manager = create_notes_manager(
            config_manager=mock_config_manager,
            redis_manager=mock_redis_manager,
        )
        
        result = await manager.update_session_end(
            session_id="test_session",
            ended_at=datetime.now(timezone.utc),
            duration_seconds=300.0,
            message_count=10,
            end_reason="ended",
            ash_summary="Test summary",
        )
        
        assert result is True
        # Verify set was called to update the metadata
        assert mock_redis_manager.set.call_count >= 1
    
    @pytest.mark.asyncio
    async def test_get_session_metadata(self, mock_config_manager, mock_redis_manager):
        """Test retrieving session metadata."""
        from src.managers.session.notes_manager import create_notes_manager
        
        # Setup mock to return metadata
        existing_meta = {
            "session_id": "test_session",
            "user_id": 12345,
            "user_name": "TestUser",
            "severity": "high",
            "started_at": datetime.now(timezone.utc).isoformat(),
            "status": "active",
        }
        mock_redis_manager.get = AsyncMock(return_value=json.dumps(existing_meta))
        
        manager = create_notes_manager(
            config_manager=mock_config_manager,
            redis_manager=mock_redis_manager,
        )
        
        metadata = await manager.get_session_metadata("test_session")
        
        assert metadata is not None
        assert metadata["session_id"] == "test_session"
        assert metadata["user_id"] == 12345


class TestNotesManagerSessionSummary:
    """Tests for session summary posting."""
    
    @pytest.mark.asyncio
    async def test_post_session_summary(self, mock_config_manager, mock_redis_manager, mock_bot):
        """Test posting session summary to channel."""
        from src.managers.session.notes_manager import (
            create_notes_manager,
            SessionSummary,
        )
        
        manager = create_notes_manager(
            config_manager=mock_config_manager,
            redis_manager=mock_redis_manager,
        )
        
        summary = SessionSummary(
            session_id="test_session",
            user_id=12345,
            user_name="TestUser",
            severity="high",
            started_at=datetime.now(timezone.utc),
            ended_at=datetime.now(timezone.utc),
            duration_seconds=300.0,
            message_count=10,
            ash_summary="Test session summary",
            end_reason="ended",
        )
        
        message = await manager.post_session_summary(summary, mock_bot)
        
        assert message is not None
        mock_bot.get_channel.assert_called_with(123456789)
    
    @pytest.mark.asyncio
    async def test_post_session_summary_no_channel(
        self, mock_config_manager_no_channel, mock_redis_manager, mock_bot
    ):
        """Test posting summary when no channel configured."""
        from src.managers.session.notes_manager import (
            create_notes_manager,
            SessionSummary,
        )
        
        manager = create_notes_manager(
            config_manager=mock_config_manager_no_channel,
            redis_manager=mock_redis_manager,
        )
        
        summary = SessionSummary(
            session_id="test_session",
            user_id=12345,
            user_name="TestUser",
            severity="high",
            started_at=datetime.now(timezone.utc),
            ended_at=datetime.now(timezone.utc),
            duration_seconds=300.0,
            message_count=10,
            end_reason="ended",
        )
        
        message = await manager.post_session_summary(summary, mock_bot)
        
        # Should return None when no channel configured
        assert message is None


class TestSessionNoteDataClass:
    """Tests for SessionNote data class."""
    
    def test_session_note_creation(self):
        """Test creating a SessionNote."""
        from src.managers.session.notes_manager import SessionNote
        
        note = SessionNote(
            note_id="note_123",
            session_id="session_456",
            author_id=12345,
            author_name="TestUser",
            note_text="This is a test note.",
        )
        
        assert note.note_id == "note_123"
        assert note.session_id == "session_456"
        assert note.author_id == 12345
        assert note.author_name == "TestUser"
        assert note.note_text == "This is a test note."
        assert note.created_at is not None
    
    def test_session_note_to_dict(self):
        """Test converting SessionNote to dictionary."""
        from src.managers.session.notes_manager import SessionNote
        
        note = SessionNote(
            note_id="note_123",
            session_id="session_456",
            author_id=12345,
            author_name="TestUser",
            note_text="This is a test note.",
        )
        
        note_dict = note.to_dict()
        
        assert note_dict["note_id"] == "note_123"
        assert note_dict["session_id"] == "session_456"
        assert note_dict["author_id"] == 12345
        assert note_dict["author_name"] == "TestUser"
        assert note_dict["note_text"] == "This is a test note."
        assert "created_at" in note_dict
    
    def test_session_note_from_dict(self):
        """Test creating SessionNote from dictionary."""
        from src.managers.session.notes_manager import SessionNote
        
        data = {
            "note_id": "note_123",
            "session_id": "session_456",
            "author_id": 12345,
            "author_name": "TestUser",
            "note_text": "This is a test note.",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        
        note = SessionNote.from_dict(data)
        
        assert note.note_id == "note_123"
        assert note.session_id == "session_456"
        assert note.author_id == 12345


class TestSessionSummaryDataClass:
    """Tests for SessionSummary data class."""
    
    def test_session_summary_creation(self):
        """Test creating a SessionSummary."""
        from src.managers.session.notes_manager import SessionSummary
        
        summary = SessionSummary(
            session_id="session_123",
            user_id=12345,
            user_name="TestUser",
            severity="high",
            started_at=datetime.now(timezone.utc),
            ended_at=datetime.now(timezone.utc),
            duration_seconds=300.0,
            message_count=10,
            ash_summary="Test summary",
            end_reason="ended",
        )
        
        assert summary.session_id == "session_123"
        assert summary.user_id == 12345
        assert summary.severity == "high"
        assert summary.duration_seconds == 300.0
        assert summary.message_count == 10


# =============================================================================
# Run tests
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
