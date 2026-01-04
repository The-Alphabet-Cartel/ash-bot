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
FILE VERSION: v5.0-2-2.0-1
LAST MODIFIED: 2026-01-03
PHASE: Phase 2 - Redis History Storage
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-bot
Community: The Alphabet Cartel - https://discord.gg/alphabetcartel | https://alphabetcartel.org
============================================================================

RESPONSIBILITIES:
- Define data classes for Redis history storage
- Provide serialization/deserialization for JSON storage
- Enable conversion to NLP API format (MessageHistoryItem)

MODELS:
- StoredMessage: Message stored in Redis with crisis analysis metadata
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional
import logging

# Module version
__version__ = "v5.0-2-2.0-1"

# Initialize logger
logger = logging.getLogger(__name__)


# =============================================================================
# Stored Message
# =============================================================================


@dataclass
class StoredMessage:
    """
    Message stored in Redis history.

    Contains the message content plus metadata from NLP analysis.
    Used for retrieving historical context and building escalation patterns.

    Attributes:
        message: Truncated message content (max 500 chars)
        timestamp: ISO-8601 timestamp of original message
        crisis_score: Score from NLP analysis (0.0-1.0)
        severity: Severity level (low, medium, high, critical)
        message_id: Discord message ID (optional)

    Key Format in Redis:
        ash:history:{guild_id}:{user_id}

    Storage Format:
        Sorted set with timestamp as score, JSON as member
    """

    message: str
    timestamp: str
    crisis_score: float
    severity: str
    message_id: Optional[str] = None

    # Maximum message length to store
    MAX_MESSAGE_LENGTH = 500

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary for JSON serialization.

        Returns:
            Dictionary representation for Redis storage
        """
        return {
            "message": self.message,
            "timestamp": self.timestamp,
            "crisis_score": self.crisis_score,
            "severity": self.severity,
            "message_id": self.message_id,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StoredMessage":
        """
        Create from dictionary (JSON deserialization).

        Args:
            data: Dictionary with stored message data

        Returns:
            StoredMessage instance

        Raises:
            KeyError: If required fields are missing
        """
        return cls(
            message=data["message"],
            timestamp=data["timestamp"],
            crisis_score=float(data.get("crisis_score", 0.0)),
            severity=data.get("severity", "unknown"),
            message_id=data.get("message_id"),
        )

    @classmethod
    def create(
        cls,
        message: str,
        timestamp: datetime,
        crisis_score: float,
        severity: str,
        message_id: Optional[str] = None,
    ) -> "StoredMessage":
        """
        Factory method to create a StoredMessage with validation.

        Args:
            message: Original message content (will be truncated if too long)
            timestamp: Message timestamp
            crisis_score: Crisis score from NLP (0.0-1.0)
            severity: Severity level string
            message_id: Discord message ID (optional)

        Returns:
            StoredMessage instance
        """
        # Truncate message if too long
        truncated_message = message[: cls.MAX_MESSAGE_LENGTH]
        if len(message) > cls.MAX_MESSAGE_LENGTH:
            truncated_message = truncated_message.rstrip() + "..."
            logger.debug(
                f"Truncated message from {len(message)} to {cls.MAX_MESSAGE_LENGTH} chars"
            )

        # Ensure timestamp is ISO format
        if isinstance(timestamp, datetime):
            iso_timestamp = timestamp.isoformat()
        else:
            iso_timestamp = str(timestamp)

        # Clamp crisis score to valid range
        clamped_score = max(0.0, min(1.0, crisis_score))

        return cls(
            message=truncated_message,
            timestamp=iso_timestamp,
            crisis_score=clamped_score,
            severity=severity.lower(),
            message_id=message_id,
        )

    @property
    def parsed_timestamp(self) -> datetime:
        """
        Parse timestamp string to datetime.

        Returns:
            datetime object

        Note:
            Handles both 'Z' suffix and '+00:00' offset formats
        """
        ts = self.timestamp.replace("Z", "+00:00")
        return datetime.fromisoformat(ts)

    @property
    def age_seconds(self) -> float:
        """
        Calculate age of message in seconds.

        Returns:
            Number of seconds since message was created
        """
        from datetime import timezone

        now = datetime.now(timezone.utc)
        msg_time = self.parsed_timestamp
        return (now - msg_time).total_seconds()

    def to_history_item(self) -> "MessageHistoryItem":
        """
        Convert to MessageHistoryItem for NLP API request.

        Returns:
            MessageHistoryItem compatible with NLP API
        """
        # Import here to avoid circular imports
        from src.models.nlp_models import MessageHistoryItem

        return MessageHistoryItem(
            message=self.message,
            timestamp=self.timestamp,
            crisis_score=self.crisis_score,
            message_id=self.message_id,
        )

    def __str__(self) -> str:
        """Human-readable string representation."""
        preview = self.message[:50] + "..." if len(self.message) > 50 else self.message
        return (
            f"StoredMessage("
            f"severity={self.severity}, "
            f"score={self.crisis_score:.2f}, "
            f"msg='{preview}')"
        )


# =============================================================================
# Export public interface
# =============================================================================

__all__ = [
    "StoredMessage",
]
