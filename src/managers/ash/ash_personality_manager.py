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
Ash Personality Manager for Ash-Bot Service
---
FILE VERSION: v5.0-4-5.0-1
LAST MODIFIED: 2026-01-04
PHASE: Phase 4 - Ash AI Integration
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-bot
Community: The Alphabet Cartel - https://discord.gg/alphabetcartel | https://alphabetcartel.org
============================================================================
RESPONSIBILITIES:
- Orchestrate Ash conversation responses
- Build prompts with system + context
- Generate responses via Claude API
- Check for safety triggers
- Handle resource sharing
- Manage conversation flow

USAGE:
    from src.managers.ash import create_ash_personality_manager

    personality_manager = create_ash_personality_manager(
        config_manager=config_manager,
        claude_client=claude_client,
    )

    response = await personality_manager.generate_response(
        message=discord_message,
        session=ash_session,
    )
"""

import logging
from typing import Any, Dict, List, Optional, Tuple, TYPE_CHECKING

import discord

from src.prompts import (
    ASH_SYSTEM_PROMPT,
    CRISIS_RESOURCES,
    SAFETY_TRIGGERS,
    HANDOFF_MESSAGE,
    CRT_ARRIVAL_MESSAGE,
    get_welcome_message,
    get_closing_message,
)

if TYPE_CHECKING:
    from src.managers.config_manager import ConfigManager
    from .claude_client_manager import ClaudeClientManager
    from .ash_session_manager import AshSession

# Module version
__version__ = "v5.0-4-5.0-1"

# Initialize logger
logger = logging.getLogger(__name__)


# =============================================================================
# Ash Personality Manager
# =============================================================================


class AshPersonalityManager:
    """
    Manages Ash's personality and response generation.

    Orchestrates the full response flow including:
    - Building prompts with system and context
    - Generating responses via Claude API
    - Checking for safety triggers
    - Injecting crisis resources when needed

    Attributes:
        config_manager: ConfigManager for settings
        claude_client: ClaudeClientManager for API calls

    Example:
        >>> personality = create_ash_personality_manager(config, claude)
        >>> response = await personality.generate_response(message, session)
    """

    def __init__(
        self,
        config_manager: "ConfigManager",
        claude_client: "ClaudeClientManager",
    ):
        """
        Initialize AshPersonalityManager.

        Args:
            config_manager: Configuration manager for settings
            claude_client: Claude client for API calls
        """
        self._config = config_manager
        self._claude = claude_client
        self._logger = logging.getLogger(__name__)

        # Statistics
        self._responses_generated = 0
        self._safety_triggers_detected = 0

        self._logger.info("🌸 AshPersonalityManager initialized")

    # =========================================================================
    # Response Generation
    # =========================================================================

    async def generate_response(
        self,
        message: discord.Message,
        session: "AshSession",
    ) -> str:
        """
        Generate Ash's response to a user message.

        Full flow:
        1. Extract user content
        2. Check for safety triggers
        3. Add user message to session history
        4. Call Claude API
        5. Add assistant response to history
        6. Append resources if safety triggered

        Args:
            message: User's Discord message
            session: Active Ash session

        Returns:
            Ash's response text (may include crisis resources)
        """
        user_content = message.content

        self._logger.debug(
            f"📝 Generating response for session {session.session_id} "
            f"(message length: {len(user_content)})"
        )

        # Check for safety triggers before processing
        safety_triggered = self._check_safety_triggers(user_content)

        if safety_triggered:
            self._safety_triggers_detected += 1
            self._logger.warning(
                f"⚠️ Safety trigger detected in session {session.session_id}"
            )

        # Add user message to conversation history
        session.add_user_message(user_content)

        # Build messages for Claude API
        messages = session.messages.copy()

        # Generate response using Claude
        try:
            response = await self._claude.create_message_safe(
                system_prompt=ASH_SYSTEM_PROMPT,
                messages=messages,
            )
        except Exception as e:
            self._logger.error(f"Error generating response: {e}")
            response = self._get_fallback_response()

        # Add assistant response to history
        session.add_assistant_message(response)

        # Append safety resources if triggered
        if safety_triggered:
            response = self._append_crisis_resources(response)

        self._responses_generated += 1

        self._logger.debug(
            f"📤 Response generated for session {session.session_id} "
            f"(length: {len(response)}, safety: {safety_triggered})"
        )

        return response

    async def generate_response_from_text(
        self,
        text: str,
        session: "AshSession",
    ) -> str:
        """
        Generate response from raw text (not Discord message).

        Useful for programmatic responses or testing.

        Args:
            text: User's text content
            session: Active Ash session

        Returns:
            Ash's response text
        """
        # Check safety triggers
        safety_triggered = self._check_safety_triggers(text)

        if safety_triggered:
            self._safety_triggers_detected += 1

        # Add to history
        session.add_user_message(text)

        # Generate response
        try:
            response = await self._claude.create_message_safe(
                system_prompt=ASH_SYSTEM_PROMPT,
                messages=session.messages.copy(),
            )
        except Exception as e:
            self._logger.error(f"Error generating response: {e}")
            response = self._get_fallback_response()

        session.add_assistant_message(response)

        if safety_triggered:
            response = self._append_crisis_resources(response)

        self._responses_generated += 1

        return response

    # =========================================================================
    # Safety Detection
    # =========================================================================

    def _check_safety_triggers(self, content: str) -> bool:
        """
        Check message for safety trigger phrases.

        Scans content for keywords that indicate immediate crisis
        and require resource sharing.

        Args:
            content: Message content to check

        Returns:
            True if safety trigger detected
        """
        content_lower = content.lower()

        for trigger in SAFETY_TRIGGERS:
            if trigger in content_lower:
                self._logger.debug(f"Safety trigger matched: '{trigger}'")
                return True

        return False

    def check_safety_triggers(self, content: str) -> Tuple[bool, List[str]]:
        """
        Check message for safety triggers and return matched triggers.

        Public method for external use (e.g., testing, logging).

        Args:
            content: Message content to check

        Returns:
            Tuple of (has_triggers, list_of_matched_triggers)
        """
        content_lower = content.lower()
        matched = []

        for trigger in SAFETY_TRIGGERS:
            if trigger in content_lower:
                matched.append(trigger)

        return (len(matched) > 0, matched)

    def _append_crisis_resources(self, response: str) -> str:
        """
        Append crisis resources to response.

        Args:
            response: Original response text

        Returns:
            Response with crisis resources appended
        """
        return f"{response}\n\n{CRISIS_RESOURCES}"

    # =========================================================================
    # Canned Messages
    # =========================================================================

    def get_welcome_message(
        self,
        severity: str,
        username: Optional[str] = None,
    ) -> str:
        """
        Get welcome message based on trigger severity.

        Args:
            severity: Original crisis severity (critical, high, medium)
            username: Optional username to personalize message

        Returns:
            Welcome message text
        """
        return get_welcome_message(severity, username)

    def get_closing_message(self, reason: str) -> str:
        """
        Get closing message for session end.

        Args:
            reason: Reason for ending (ended, timeout, max_duration, transfer, user_ended)

        Returns:
            Closing message text
        """
        return get_closing_message(reason)

    def get_handoff_message(self) -> str:
        """
        Get message for CRT handoff suggestion.

        Returns:
            Handoff suggestion message
        """
        return HANDOFF_MESSAGE

    def get_crt_arrival_message(self) -> str:
        """
        Get message for when CRT member arrives.

        Returns:
            CRT arrival notification message
        """
        return CRT_ARRIVAL_MESSAGE

    def _get_fallback_response(self) -> str:
        """
        Get fallback response when Claude fails.

        Returns:
            Safe fallback response
        """
        return (
            "I'm here with you. I'm having a little trouble right now, "
            "but I want to make sure you're okay. Would you like me to "
            "connect you with our Crisis Response Team?"
        )

    # =========================================================================
    # End Phrase Detection
    # =========================================================================

    def detect_end_request(self, content: str) -> bool:
        """
        Detect if user wants to end the conversation.

        Args:
            content: Message content to check

        Returns:
            True if user wants to end conversation
        """
        content_lower = content.lower().strip()

        end_phrases = [
            "bye",
            "goodbye",
            "good bye",
            "thanks bye",
            "thank you bye",
            "i'm done",
            "im done",
            "i am done",
            "end conversation",
            "stop",
            "end chat",
            "that's all",
            "thats all",
            "i'm okay now",
            "im okay now",
            "i feel better",
            "feeling better now",
        ]

        for phrase in end_phrases:
            if content_lower == phrase or content_lower.startswith(f"{phrase} "):
                return True

        return False

    def detect_crt_request(self, content: str) -> bool:
        """
        Detect if user wants to talk to a human (CRT).

        Args:
            content: Message content to check

        Returns:
            True if user wants human support
        """
        content_lower = content.lower()

        crt_phrases = [
            "talk to a human",
            "talk to a person",
            "real person",
            "real human",
            "want a human",
            "need a human",
            "crisis response team",
            "crisis team",
            "crt",
            "talk to someone",
            "actual person",
            "not a bot",
            "are you a bot",
            "are you real",
        ]

        for phrase in crt_phrases:
            if phrase in content_lower:
                return True

        return False

    # =========================================================================
    # Properties and Statistics
    # =========================================================================

    @property
    def responses_generated(self) -> int:
        """Get total responses generated."""
        return self._responses_generated

    @property
    def safety_triggers_detected(self) -> int:
        """Get total safety triggers detected."""
        return self._safety_triggers_detected

    def get_stats(self) -> Dict[str, Any]:
        """
        Get personality manager statistics.

        Returns:
            Dictionary with response statistics
        """
        return {
            "responses_generated": self._responses_generated,
            "safety_triggers_detected": self._safety_triggers_detected,
            "claude_stats": self._claude.get_stats(),
        }

    def __repr__(self) -> str:
        """String representation for debugging."""
        return (
            f"AshPersonalityManager("
            f"responses={self._responses_generated}, "
            f"safety_triggers={self._safety_triggers_detected})"
        )


# =============================================================================
# Factory Function
# =============================================================================


def create_ash_personality_manager(
    config_manager: "ConfigManager",
    claude_client: "ClaudeClientManager",
) -> AshPersonalityManager:
    """
    Factory function for AshPersonalityManager.

    Following Clean Architecture v5.1 Rule #1: Factory Functions.

    Args:
        config_manager: Configuration manager
        claude_client: Claude client for API calls

    Returns:
        Configured AshPersonalityManager instance

    Example:
        >>> personality = create_ash_personality_manager(config, claude)
        >>> response = await personality.generate_response(message, session)
    """
    return AshPersonalityManager(
        config_manager=config_manager,
        claude_client=claude_client,
    )


# =============================================================================
# Export public interface
# =============================================================================

__all__ = [
    "AshPersonalityManager",
    "create_ash_personality_manager",
]
