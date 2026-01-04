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
NLP Data Models for Ash-Bot Service
---
FILE VERSION: v5.0-1-1.2-1
LAST MODIFIED: 2026-01-03
PHASE: Phase 1 - Discord Connectivity
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-bot
Community: The Alphabet Cartel - https://discord.gg/alphabetcartel | https://alphabetcartel.org
============================================================================
RESPONSIBILITIES:
- Define data classes for NLP API request/response structures
- Provide type-safe access to crisis analysis results
- Enable serialization for API communication

MODELS:
- MessageHistoryItem: Single message in history context
- SignalResult: Individual model signal result
- CrisisAnalysisResult: Complete analysis response from Ash-NLP
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import logging

# Module version
__version__ = "v5.0-1-1.2-1"

# Initialize logger
logger = logging.getLogger(__name__)


# =============================================================================
# Severity Level Constants
# =============================================================================


class SeverityLevel:
    """Crisis severity level constants matching Ash-NLP API."""

    SAFE = "safe"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

    # Ordered list for comparison
    LEVELS = [SAFE, LOW, MEDIUM, HIGH, CRITICAL]

    @classmethod
    def is_valid(cls, severity: str) -> bool:
        """Check if severity is valid."""
        return severity.lower() in cls.LEVELS

    @classmethod
    def get_level_index(cls, severity: str) -> int:
        """Get numeric index for severity (higher = more severe)."""
        try:
            return cls.LEVELS.index(severity.lower())
        except ValueError:
            return -1

    @classmethod
    def is_actionable(cls, severity: str) -> bool:
        """Check if severity requires action (MEDIUM+)."""
        return severity.lower() in (cls.MEDIUM, cls.HIGH, cls.CRITICAL)

    @classmethod
    def requires_alert(cls, severity: str) -> bool:
        """Check if severity requires CRT alert (MEDIUM+)."""
        return cls.is_actionable(severity)

    @classmethod
    def requires_ash_response(cls, severity: str) -> bool:
        """Check if severity requires Ash AI response (HIGH+)."""
        return severity.lower() in (cls.HIGH, cls.CRITICAL)


# =============================================================================
# Message History Item
# =============================================================================


@dataclass
class MessageHistoryItem:
    """
    Single message item in user history context.

    Used to provide previous messages to Ash-NLP for
    escalation pattern detection.

    Attributes:
        message: Message content text
        timestamp: ISO-8601 timestamp of the message
        crisis_score: Pre-computed crisis score (0.0-1.0), optional
        message_id: Unique message identifier, optional
    """

    message: str
    timestamp: str
    crisis_score: Optional[float] = None
    message_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary for API request.

        Returns:
            Dictionary representation for JSON serialization
        """
        result: Dict[str, Any] = {
            "message": self.message,
            "timestamp": self.timestamp,
        }

        if self.crisis_score is not None:
            result["crisis_score"] = self.crisis_score

        if self.message_id is not None:
            result["message_id"] = self.message_id

        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MessageHistoryItem":
        """
        Create from dictionary.

        Args:
            data: Dictionary with message data

        Returns:
            MessageHistoryItem instance
        """
        return cls(
            message=data.get("message", ""),
            timestamp=data.get("timestamp", ""),
            crisis_score=data.get("crisis_score"),
            message_id=data.get("message_id"),
        )


# =============================================================================
# Signal Result
# =============================================================================


@dataclass
class SignalResult:
    """
    Individual model signal result from Ash-NLP.

    Each model in the ensemble produces a signal with:
    - Classification label (what it detected)
    - Model confidence score
    - Crisis relevance score (normalized 0-1)

    Attributes:
        label: Classification label from the model
        score: Raw model confidence score (0.0-1.0)
        crisis_signal: Transformed crisis relevance score (0.0-1.0)
    """

    label: str
    score: float
    crisis_signal: float

    @property
    def is_crisis_indicator(self) -> bool:
        """Check if this signal indicates crisis (>0.5)."""
        return self.crisis_signal > 0.5

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SignalResult":
        """
        Create from dictionary.

        Args:
            data: Dictionary with signal data

        Returns:
            SignalResult instance
        """
        return cls(
            label=data.get("label", "unknown"),
            score=float(data.get("score", 0.0)),
            crisis_signal=float(data.get("crisis_signal", 0.0)),
        )


# =============================================================================
# Crisis Analysis Result
# =============================================================================


@dataclass
class CrisisAnalysisResult:
    """
    Complete result from Ash-NLP crisis analysis.

    Contains all information from the NLP ensemble analysis
    including crisis detection, severity, model signals,
    and optional detailed explanations.

    Attributes:
        crisis_detected: Whether a crisis situation was detected
        severity: Crisis severity level (safe, low, medium, high, critical)
        confidence: Model agreement confidence (0.0-1.0)
        crisis_score: Final weighted crisis score (0.0-1.0)
        requires_intervention: Whether human intervention is recommended
        recommended_action: Suggested action string
        request_id: Unique request identifier
        timestamp: ISO-8601 timestamp of analysis
        processing_time_ms: Time taken to process in milliseconds
        models_used: List of model names that contributed
        is_degraded: Whether system was in degraded mode
        signals: Per-model signal results
        explanation: Human-readable explanation (optional)
        consensus: Consensus algorithm details (optional)
        conflict_analysis: Model disagreement analysis (optional)
        context_analysis: Temporal/escalation analysis (optional)
    """

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

    # Signal results per model
    signals: Dict[str, SignalResult] = field(default_factory=dict)

    # Optional detailed analysis
    explanation: Optional[Dict[str, Any]] = None
    consensus: Optional[Dict[str, Any]] = None
    conflict_analysis: Optional[Dict[str, Any]] = None
    context_analysis: Optional[Dict[str, Any]] = None

    # ==========================================================================
    # Convenience Properties
    # ==========================================================================

    @property
    def is_crisis(self) -> bool:
        """Alias for crisis_detected."""
        return self.crisis_detected

    @property
    def is_actionable(self) -> bool:
        """Check if result requires action (MEDIUM+)."""
        return SeverityLevel.is_actionable(self.severity)

    @property
    def requires_alert(self) -> bool:
        """Check if result requires CRT alert (MEDIUM+)."""
        return SeverityLevel.requires_alert(self.severity)

    @property
    def requires_ash_response(self) -> bool:
        """Check if result requires Ash AI response (HIGH+)."""
        return SeverityLevel.requires_ash_response(self.severity)

    @property
    def severity_index(self) -> int:
        """Get numeric severity index (0-4)."""
        return SeverityLevel.get_level_index(self.severity)

    @property
    def explanation_summary(self) -> Optional[str]:
        """Get decision summary from explanation if available."""
        if self.explanation:
            return self.explanation.get("decision_summary")
        return None

    @property
    def key_factors(self) -> List[str]:
        """Get key factors from explanation if available."""
        if self.explanation:
            return self.explanation.get("key_factors", [])
        return []

    @property
    def has_conflicts(self) -> bool:
        """Check if model conflicts were detected."""
        if self.conflict_analysis:
            return self.conflict_analysis.get("has_conflicts", False)
        return False

    @property
    def escalation_detected(self) -> bool:
        """Check if escalation pattern was detected."""
        if self.context_analysis:
            return self.context_analysis.get("escalation_detected", False)
        return False

    # ==========================================================================
    # Factory Methods
    # ==========================================================================

    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> "CrisisAnalysisResult":
        """
        Create CrisisAnalysisResult from API response dictionary.

        Args:
            data: Raw API response dictionary

        Returns:
            CrisisAnalysisResult instance

        Note:
            Handles missing fields gracefully with safe defaults.
        """
        # Parse signals
        signals: Dict[str, SignalResult] = {}
        for model_name, signal_data in data.get("signals", {}).items():
            try:
                signals[model_name] = SignalResult.from_dict(signal_data)
            except Exception as e:
                logger.warning(f"Failed to parse signal for {model_name}: {e}")

        return cls(
            crisis_detected=data.get("crisis_detected", False),
            severity=data.get("severity", "safe"),
            confidence=float(data.get("confidence", 0.0)),
            crisis_score=float(data.get("crisis_score", 0.0)),
            requires_intervention=data.get("requires_intervention", False),
            recommended_action=data.get("recommended_action", "none"),
            request_id=data.get("request_id", "unknown"),
            timestamp=data.get("timestamp", ""),
            processing_time_ms=float(data.get("processing_time_ms", 0.0)),
            models_used=data.get("models_used", []),
            is_degraded=data.get("is_degraded", False),
            signals=signals,
            explanation=data.get("explanation"),
            consensus=data.get("consensus"),
            conflict_analysis=data.get("conflict_analysis"),
            context_analysis=data.get("context_analysis"),
        )

    @classmethod
    def create_error_result(
        cls,
        error_message: str,
        request_id: str = "error",
    ) -> "CrisisAnalysisResult":
        """
        Create an error result for failed analysis.

        Used when NLP API is unavailable or returns an error.
        Returns a SAFE result to avoid false alerts.

        Args:
            error_message: Error description
            request_id: Request identifier

        Returns:
            CrisisAnalysisResult with safe defaults
        """
        from datetime import datetime

        return cls(
            crisis_detected=False,
            severity=SeverityLevel.SAFE,
            confidence=0.0,
            crisis_score=0.0,
            requires_intervention=False,
            recommended_action="none",
            request_id=request_id,
            timestamp=datetime.utcnow().isoformat() + "Z",
            processing_time_ms=0.0,
            models_used=[],
            is_degraded=True,
            signals={},
            explanation={
                "decision_summary": f"Analysis failed: {error_message}",
                "key_factors": ["error"],
            },
        )

    # ==========================================================================
    # Serialization
    # ==========================================================================

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary for storage or logging.

        Returns:
            Dictionary representation
        """
        return {
            "crisis_detected": self.crisis_detected,
            "severity": self.severity,
            "confidence": self.confidence,
            "crisis_score": self.crisis_score,
            "requires_intervention": self.requires_intervention,
            "recommended_action": self.recommended_action,
            "request_id": self.request_id,
            "timestamp": self.timestamp,
            "processing_time_ms": self.processing_time_ms,
            "models_used": self.models_used,
            "is_degraded": self.is_degraded,
            "signals": {
                name: {
                    "label": sig.label,
                    "score": sig.score,
                    "crisis_signal": sig.crisis_signal,
                }
                for name, sig in self.signals.items()
            },
            "explanation": self.explanation,
            "consensus": self.consensus,
            "conflict_analysis": self.conflict_analysis,
            "context_analysis": self.context_analysis,
        }

    def to_log_dict(self) -> Dict[str, Any]:
        """
        Convert to compact dictionary for logging.

        Returns:
            Minimal dictionary with key information
        """
        return {
            "crisis": self.crisis_detected,
            "severity": self.severity,
            "score": round(self.crisis_score, 3),
            "confidence": round(self.confidence, 3),
            "action": self.recommended_action,
            "request_id": self.request_id,
            "degraded": self.is_degraded,
        }

    def __str__(self) -> str:
        """Human-readable string representation."""
        return (
            f"CrisisAnalysisResult("
            f"severity={self.severity}, "
            f"score={self.crisis_score:.3f}, "
            f"confidence={self.confidence:.3f}, "
            f"action={self.recommended_action})"
        )


# =============================================================================
# Export public interface
# =============================================================================

__all__ = [
    "SeverityLevel",
    "MessageHistoryItem",
    "SignalResult",
    "CrisisAnalysisResult",
]
