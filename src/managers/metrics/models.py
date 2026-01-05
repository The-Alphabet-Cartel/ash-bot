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
Metrics Data Models for Response Time Tracking
----------------------------------------------------------------------------
FILE VERSION: v5.0-8-1.0-1
LAST MODIFIED: 2026-01-05
PHASE: Phase 8 - Metrics & Reporting
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-bot
============================================================================

RESPONSIBILITIES:
- Define data structures for alert metrics tracking
- Provide AlertMetrics dataclass for individual alert tracking
- Provide DailyAggregate dataclass for daily statistics
- Provide WeeklySummary dataclass for weekly reports
- JSON serialization/deserialization support

USAGE:
    from src.managers.metrics.models import AlertMetrics, DailyAggregate

    metrics = AlertMetrics(
        alert_id="alert_abc123",
        alert_message_id=123456789,
        user_id=987654321,
        severity="high",
    )
"""

import json
import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime, date
from typing import Any, Dict, List, Optional

# Module version
__version__ = "v5.0-8-1.0-1"

# Initialize logger
logger = logging.getLogger(__name__)


# =============================================================================
# Alert Metrics Model
# =============================================================================


@dataclass
class AlertMetrics:
    """
    Metrics for a single crisis alert.

    Tracks timestamps and calculated response times for an alert
    from creation through acknowledgment and resolution.

    Attributes:
        alert_id: Unique identifier for this alert
        alert_message_id: Discord message ID of the alert
        user_id: Discord ID of user who triggered alert
        channel_id: Discord channel ID where original message was sent
        severity: Crisis severity level (low, medium, high, critical)
        channel_sensitivity: Sensitivity modifier applied to channel

        alert_created_at: When the alert was posted
        acknowledged_at: When CRT acknowledged the alert
        acknowledged_by: User ID of CRT member who acknowledged
        ash_contacted_at: When Ash session was initiated
        ash_initiated_by: User ID who initiated Ash (or "auto" for auto-initiate)
        first_response_at: When first human response occurred
        first_responder_id: User ID of first human responder
        resolved_at: When alert was marked resolved

        time_to_acknowledge_seconds: Calculated time from alert to ack
        time_to_ash_seconds: Calculated time from alert to Ash contact
        time_to_response_seconds: Calculated time from alert to human response

        was_auto_initiated: Whether Ash was auto-initiated
        user_opted_out: Whether user opted out of Ash

    Example:
        >>> metrics = AlertMetrics(
        ...     alert_id="alert_abc123",
        ...     alert_message_id=123456789,
        ...     user_id=987654321,
        ...     channel_id=111222333,
        ...     severity="high",
        ... )
        >>> metrics.record_acknowledged(acknowledged_by=555666777)
    """

    # Required fields
    alert_id: str
    alert_message_id: int
    user_id: int
    channel_id: int
    severity: str

    # Optional configuration
    channel_sensitivity: float = 1.0

    # Timestamps (ISO format strings for JSON compatibility)
    alert_created_at: Optional[str] = None
    acknowledged_at: Optional[str] = None
    ash_contacted_at: Optional[str] = None
    first_response_at: Optional[str] = None
    resolved_at: Optional[str] = None

    # Who performed actions
    acknowledged_by: Optional[int] = None
    ash_initiated_by: Optional[str] = None  # User ID as string or "auto"
    first_responder_id: Optional[int] = None

    # Calculated durations (seconds)
    time_to_acknowledge_seconds: Optional[int] = None
    time_to_ash_seconds: Optional[int] = None
    time_to_response_seconds: Optional[int] = None

    # Flags
    was_auto_initiated: bool = False
    user_opted_out: bool = False

    def __post_init__(self):
        """Set creation timestamp if not provided."""
        if self.alert_created_at is None:
            self.alert_created_at = datetime.utcnow().isoformat() + "Z"

    # =========================================================================
    # Recording Methods
    # =========================================================================

    def record_acknowledged(self, acknowledged_by: int) -> None:
        """
        Record when alert was acknowledged.

        Args:
            acknowledged_by: User ID of CRT member who acknowledged
        """
        now = datetime.utcnow()
        self.acknowledged_at = now.isoformat() + "Z"
        self.acknowledged_by = acknowledged_by

        # Calculate time to acknowledge
        if self.alert_created_at:
            created = datetime.fromisoformat(
                self.alert_created_at.replace("Z", "+00:00")
            )
            delta = now - created.replace(tzinfo=None)
            self.time_to_acknowledge_seconds = int(delta.total_seconds())

        logger.debug(
            f"Alert {self.alert_id} acknowledged by {acknowledged_by} "
            f"in {self.time_to_acknowledge_seconds}s"
        )

    def record_ash_contacted(
        self,
        initiated_by: int | str,
        was_auto: bool = False,
    ) -> None:
        """
        Record when Ash session was initiated.

        Args:
            initiated_by: User ID who clicked button, or "auto" for auto-initiate
            was_auto: Whether this was auto-initiated
        """
        now = datetime.utcnow()
        self.ash_contacted_at = now.isoformat() + "Z"
        self.ash_initiated_by = str(initiated_by)
        self.was_auto_initiated = was_auto

        # Calculate time to Ash contact
        if self.alert_created_at:
            created = datetime.fromisoformat(
                self.alert_created_at.replace("Z", "+00:00")
            )
            delta = now - created.replace(tzinfo=None)
            self.time_to_ash_seconds = int(delta.total_seconds())

        logger.debug(
            f"Alert {self.alert_id} Ash contacted by {initiated_by} "
            f"(auto={was_auto}) in {self.time_to_ash_seconds}s"
        )

    def record_first_response(self, responder_id: int) -> None:
        """
        Record first human response in thread/DM.

        Args:
            responder_id: User ID of first human responder
        """
        now = datetime.utcnow()
        self.first_response_at = now.isoformat() + "Z"
        self.first_responder_id = responder_id

        # Calculate time to first response
        if self.alert_created_at:
            created = datetime.fromisoformat(
                self.alert_created_at.replace("Z", "+00:00")
            )
            delta = now - created.replace(tzinfo=None)
            self.time_to_response_seconds = int(delta.total_seconds())

        logger.debug(
            f"Alert {self.alert_id} first response by {responder_id} "
            f"in {self.time_to_response_seconds}s"
        )

    def record_user_opted_out(self) -> None:
        """Record that user opted out of Ash."""
        self.user_opted_out = True
        logger.debug(f"Alert {self.alert_id} user opted out")

    def record_resolved(self) -> None:
        """Record when alert was resolved."""
        self.resolved_at = datetime.utcnow().isoformat() + "Z"
        logger.debug(f"Alert {self.alert_id} resolved")

    # =========================================================================
    # Serialization
    # =========================================================================

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary for JSON storage.

        Returns:
            Dictionary representation of metrics
        """
        return asdict(self)

    def to_json(self) -> str:
        """
        Convert to JSON string for Redis storage.

        Returns:
            JSON string representation
        """
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AlertMetrics":
        """
        Create AlertMetrics from dictionary.

        Args:
            data: Dictionary with metrics data

        Returns:
            AlertMetrics instance
        """
        return cls(**data)

    @classmethod
    def from_json(cls, json_str: str) -> "AlertMetrics":
        """
        Create AlertMetrics from JSON string.

        Args:
            json_str: JSON string with metrics data

        Returns:
            AlertMetrics instance
        """
        data = json.loads(json_str)
        return cls.from_dict(data)

    # =========================================================================
    # Properties
    # =========================================================================

    @property
    def is_acknowledged(self) -> bool:
        """Check if alert has been acknowledged."""
        return self.acknowledged_at is not None

    @property
    def is_ash_engaged(self) -> bool:
        """Check if Ash session was started."""
        return self.ash_contacted_at is not None

    @property
    def is_resolved(self) -> bool:
        """Check if alert is resolved."""
        return self.resolved_at is not None

    def __repr__(self) -> str:
        """String representation for debugging."""
        status = "resolved" if self.is_resolved else (
            "acknowledged" if self.is_acknowledged else "pending"
        )
        return (
            f"AlertMetrics(id={self.alert_id}, severity={self.severity}, "
            f"status={status}, ack_time={self.time_to_acknowledge_seconds}s)"
        )


# =============================================================================
# Daily Aggregate Model
# =============================================================================


@dataclass
class DailyAggregate:
    """
    Aggregated metrics for a single day.

    Provides summary statistics that are more efficient to query
    than recalculating from individual alerts.

    Attributes:
        date: Date in YYYY-MM-DD format
        total_alerts: Total alerts for the day
        by_severity: Count breakdown by severity level
        acknowledged_count: Number of alerts acknowledged
        ash_sessions_count: Number of Ash sessions started
        auto_initiated_count: Number of auto-initiated sessions
        user_optout_count: Number of user opt-outs

        avg_acknowledge_seconds: Average time to acknowledge
        avg_ash_contact_seconds: Average time to Ash contact
        avg_response_seconds: Average time to first response

        min_acknowledge_seconds: Fastest acknowledgment
        max_acknowledge_seconds: Slowest acknowledgment

        top_responders: Dict of responder_id -> count

    Example:
        >>> aggregate = DailyAggregate(date="2026-01-05")
        >>> aggregate.add_alert(severity="high", ack_time=150)
    """

    # Required
    date: str  # YYYY-MM-DD format

    # Counts
    total_alerts: int = 0
    by_severity: Dict[str, int] = field(default_factory=lambda: {
        "low": 0,
        "medium": 0,
        "high": 0,
        "critical": 0,
    })
    acknowledged_count: int = 0
    ash_sessions_count: int = 0
    auto_initiated_count: int = 0
    user_optout_count: int = 0

    # Timing aggregates (seconds)
    avg_acknowledge_seconds: Optional[float] = None
    avg_ash_contact_seconds: Optional[float] = None
    avg_response_seconds: Optional[float] = None

    min_acknowledge_seconds: Optional[int] = None
    max_acknowledge_seconds: Optional[int] = None

    # For computing averages
    _sum_acknowledge: int = field(default=0, repr=False)
    _sum_ash_contact: int = field(default=0, repr=False)
    _sum_response: int = field(default=0, repr=False)
    _count_acknowledge: int = field(default=0, repr=False)
    _count_ash_contact: int = field(default=0, repr=False)
    _count_response: int = field(default=0, repr=False)

    # Top responders
    top_responders: Dict[str, int] = field(default_factory=dict)

    # =========================================================================
    # Aggregation Methods
    # =========================================================================

    def add_alert(
        self,
        severity: str,
        ack_time: Optional[int] = None,
        ash_time: Optional[int] = None,
        response_time: Optional[int] = None,
        was_auto_initiated: bool = False,
        user_opted_out: bool = False,
        acknowledged_by: Optional[int] = None,
    ) -> None:
        """
        Add an alert's metrics to the aggregate.

        Args:
            severity: Alert severity level
            ack_time: Time to acknowledge in seconds
            ash_time: Time to Ash contact in seconds
            response_time: Time to first response in seconds
            was_auto_initiated: Whether Ash was auto-initiated
            user_opted_out: Whether user opted out
            acknowledged_by: User ID who acknowledged
        """
        self.total_alerts += 1

        # Count by severity
        severity_lower = severity.lower()
        if severity_lower in self.by_severity:
            self.by_severity[severity_lower] += 1

        # Track acknowledgments
        if ack_time is not None:
            self.acknowledged_count += 1
            self._sum_acknowledge += ack_time
            self._count_acknowledge += 1

            # Track min/max
            if self.min_acknowledge_seconds is None or ack_time < self.min_acknowledge_seconds:
                self.min_acknowledge_seconds = ack_time
            if self.max_acknowledge_seconds is None or ack_time > self.max_acknowledge_seconds:
                self.max_acknowledge_seconds = ack_time

            # Update average
            self.avg_acknowledge_seconds = self._sum_acknowledge / self._count_acknowledge

        # Track Ash sessions
        if ash_time is not None:
            self.ash_sessions_count += 1
            self._sum_ash_contact += ash_time
            self._count_ash_contact += 1
            self.avg_ash_contact_seconds = self._sum_ash_contact / self._count_ash_contact

        # Track response times
        if response_time is not None:
            self._sum_response += response_time
            self._count_response += 1
            self.avg_response_seconds = self._sum_response / self._count_response

        # Track flags
        if was_auto_initiated:
            self.auto_initiated_count += 1
        if user_opted_out:
            self.user_optout_count += 1

        # Track responders
        if acknowledged_by is not None:
            responder_key = str(acknowledged_by)
            self.top_responders[responder_key] = self.top_responders.get(responder_key, 0) + 1

    # =========================================================================
    # Serialization
    # =========================================================================

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary for JSON storage.

        Returns:
            Dictionary representation (excludes internal counters)
        """
        return {
            "date": self.date,
            "total_alerts": self.total_alerts,
            "by_severity": self.by_severity,
            "acknowledged_count": self.acknowledged_count,
            "ash_sessions_count": self.ash_sessions_count,
            "auto_initiated_count": self.auto_initiated_count,
            "user_optout_count": self.user_optout_count,
            "avg_acknowledge_seconds": self.avg_acknowledge_seconds,
            "avg_ash_contact_seconds": self.avg_ash_contact_seconds,
            "avg_response_seconds": self.avg_response_seconds,
            "min_acknowledge_seconds": self.min_acknowledge_seconds,
            "max_acknowledge_seconds": self.max_acknowledge_seconds,
            "top_responders": self.top_responders,
            # Internal state for recomputation
            "_sum_acknowledge": self._sum_acknowledge,
            "_sum_ash_contact": self._sum_ash_contact,
            "_sum_response": self._sum_response,
            "_count_acknowledge": self._count_acknowledge,
            "_count_ash_contact": self._count_ash_contact,
            "_count_response": self._count_response,
        }

    def to_json(self) -> str:
        """Convert to JSON string for Redis storage."""
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DailyAggregate":
        """
        Create DailyAggregate from dictionary.

        Args:
            data: Dictionary with aggregate data

        Returns:
            DailyAggregate instance
        """
        # Extract internal counters
        internal_fields = [
            "_sum_acknowledge", "_sum_ash_contact", "_sum_response",
            "_count_acknowledge", "_count_ash_contact", "_count_response",
        ]
        internal_data = {k: data.pop(k, 0) for k in internal_fields}

        instance = cls(**{k: v for k, v in data.items() if not k.startswith("_")})

        # Restore internal state
        for field_name, value in internal_data.items():
            setattr(instance, field_name, value)

        return instance

    @classmethod
    def from_json(cls, json_str: str) -> "DailyAggregate":
        """Create DailyAggregate from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)

    def __repr__(self) -> str:
        """String representation for debugging."""
        return (
            f"DailyAggregate(date={self.date}, total={self.total_alerts}, "
            f"acked={self.acknowledged_count}, avg_ack={self.avg_acknowledge_seconds:.1f}s)"
            if self.avg_acknowledge_seconds else
            f"DailyAggregate(date={self.date}, total={self.total_alerts})"
        )


# =============================================================================
# Weekly Summary Model
# =============================================================================


@dataclass
class WeeklySummary:
    """
    Summary of metrics for a week (7 days).

    Used for generating weekly CRT reports.

    Attributes:
        start_date: First day of the week (YYYY-MM-DD)
        end_date: Last day of the week (YYYY-MM-DD)
        total_alerts: Total alerts for the week
        by_severity: Count breakdown by severity
        by_day: Count breakdown by day of week

        avg_acknowledge_seconds: Average time to acknowledge
        avg_ash_contact_seconds: Average time to Ash contact
        avg_response_seconds: Average time to first response

        ash_sessions_total: Total Ash sessions started
        ash_manual_count: Manually initiated Ash sessions
        ash_auto_count: Auto-initiated Ash sessions
        user_optout_count: Users who opted out

        peak_day: Day with most alerts
        peak_hour: Hour with most alerts (0-23)

        top_responders: List of (user_id, count) tuples, sorted by count

    Example:
        >>> summary = WeeklySummary.from_aggregates(daily_aggregates)
        >>> print(f"Week of {summary.start_date}: {summary.total_alerts} alerts")
    """

    # Date range
    start_date: str
    end_date: str

    # Counts
    total_alerts: int = 0
    by_severity: Dict[str, int] = field(default_factory=lambda: {
        "low": 0,
        "medium": 0,
        "high": 0,
        "critical": 0,
    })
    by_day: Dict[str, int] = field(default_factory=dict)

    # Timing averages
    avg_acknowledge_seconds: Optional[float] = None
    avg_ash_contact_seconds: Optional[float] = None
    avg_response_seconds: Optional[float] = None

    # Ash engagement
    ash_sessions_total: int = 0
    ash_manual_count: int = 0
    ash_auto_count: int = 0
    user_optout_count: int = 0

    # Peaks
    peak_day: Optional[str] = None
    peak_hour: Optional[int] = None

    # Top responders
    top_responders: List[tuple] = field(default_factory=list)

    # =========================================================================
    # Factory Methods
    # =========================================================================

    @classmethod
    def from_aggregates(
        cls,
        aggregates: List[DailyAggregate],
        start_date: str,
        end_date: str,
    ) -> "WeeklySummary":
        """
        Create WeeklySummary from list of DailyAggregates.

        Args:
            aggregates: List of DailyAggregate objects
            start_date: Week start date
            end_date: Week end date

        Returns:
            WeeklySummary instance
        """
        summary = cls(start_date=start_date, end_date=end_date)

        if not aggregates:
            return summary

        # Aggregate totals
        total_ack_time = 0
        total_ash_time = 0
        total_response_time = 0
        ack_count = 0
        ash_count = 0
        response_count = 0
        responder_totals: Dict[str, int] = {}

        for agg in aggregates:
            summary.total_alerts += agg.total_alerts

            # Severity breakdown
            for severity, count in agg.by_severity.items():
                summary.by_severity[severity] = summary.by_severity.get(severity, 0) + count

            # Day breakdown
            summary.by_day[agg.date] = agg.total_alerts

            # Ash stats
            summary.ash_sessions_total += agg.ash_sessions_count
            summary.ash_auto_count += agg.auto_initiated_count
            summary.user_optout_count += agg.user_optout_count

            # Calculate manual sessions
            manual_sessions = agg.ash_sessions_count - agg.auto_initiated_count
            if manual_sessions > 0:
                summary.ash_manual_count += manual_sessions

            # Timing aggregates
            if agg._count_acknowledge > 0:
                total_ack_time += agg._sum_acknowledge
                ack_count += agg._count_acknowledge

            if agg._count_ash_contact > 0:
                total_ash_time += agg._sum_ash_contact
                ash_count += agg._count_ash_contact

            if agg._count_response > 0:
                total_response_time += agg._sum_response
                response_count += agg._count_response

            # Responder totals
            for responder_id, count in agg.top_responders.items():
                responder_totals[responder_id] = responder_totals.get(responder_id, 0) + count

        # Calculate averages
        if ack_count > 0:
            summary.avg_acknowledge_seconds = total_ack_time / ack_count
        if ash_count > 0:
            summary.avg_ash_contact_seconds = total_ash_time / ash_count
        if response_count > 0:
            summary.avg_response_seconds = total_response_time / response_count

        # Find peak day
        if summary.by_day:
            summary.peak_day = max(summary.by_day, key=summary.by_day.get)

        # Sort top responders
        summary.top_responders = sorted(
            responder_totals.items(),
            key=lambda x: x[1],
            reverse=True,
        )[:10]  # Top 10

        return summary

    # =========================================================================
    # Serialization
    # =========================================================================

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WeeklySummary":
        """Create from dictionary."""
        # Convert top_responders back to list of tuples
        if "top_responders" in data and data["top_responders"]:
            data["top_responders"] = [tuple(item) for item in data["top_responders"]]
        return cls(**data)

    @classmethod
    def from_json(cls, json_str: str) -> "WeeklySummary":
        """Create from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"WeeklySummary({self.start_date} to {self.end_date}, "
            f"alerts={self.total_alerts})"
        )


# =============================================================================
# Export public interface
# =============================================================================

__all__ = [
    "AlertMetrics",
    "DailyAggregate",
    "WeeklySummary",
]
