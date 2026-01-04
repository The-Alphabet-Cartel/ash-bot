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
Metrics Manager for Ash-Bot Service
---
FILE VERSION: v5.0-5-5.5-2
LAST MODIFIED: 2026-01-04
PHASE: Phase 5 - Production Hardening
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-bot
Community: The Alphabet Cartel - https://discord.gg/alphabetcartel | https://alphabetcartel.org
============================================================================
RESPONSIBILITIES:
- Collect operational metrics across all components
- Provide metric types: Counter, Gauge, Histogram
- Export metrics in Prometheus format
- Export metrics as JSON for health endpoints
- Thread-safe metric updates

METRICS COLLECTED:
- messages_processed_total: Total messages processed
- messages_analyzed_total: Messages sent to NLP (by severity)
- alerts_sent_total: Alerts dispatched (by severity, channel type)
- ash_sessions_total: Total Ash sessions started
- ash_sessions_active: Currently active Ash sessions
- nlp_request_duration_seconds: NLP API latency histogram
- nlp_errors_total: NLP API errors
- redis_operations_total: Redis operations (by type)
- redis_errors_total: Redis errors
- discord_reconnects_total: Discord reconnection count

USAGE:
    from src.managers.metrics import create_metrics_manager

    metrics = create_metrics_manager()
    
    # Record metrics
    metrics.inc_messages_processed()
    metrics.inc_messages_analyzed(severity="high")
    metrics.observe_nlp_duration(0.125)
    
    # Export
    print(metrics.export_prometheus())
"""

import logging
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

# Module version
__version__ = "v5.0-5-5.2-1"

# Initialize logger
logger = logging.getLogger(__name__)


# =============================================================================
# Metric Types
# =============================================================================


@dataclass
class Counter:
    """
    Counter metric that can only increase.

    Useful for tracking: requests, errors, events.

    Attributes:
        name: Metric name
        help_text: Description of what this metric measures
        value: Current counter value
        labels: Optional label key-value pairs
    """

    name: str
    help_text: str = ""
    value: int = 0
    labels: Dict[str, str] = field(default_factory=dict)
    _lock: threading.Lock = field(default_factory=threading.Lock, repr=False)

    def inc(self, amount: int = 1) -> None:
        """
        Increment counter.

        Args:
            amount: Amount to increment (must be positive)
        """
        if amount < 0:
            raise ValueError("Counter can only increase")
        with self._lock:
            self.value += amount

    def reset(self) -> None:
        """Reset counter to zero (use with caution)."""
        with self._lock:
            self.value = 0

    def get(self) -> int:
        """Get current value."""
        with self._lock:
            return self.value


@dataclass
class Gauge:
    """
    Gauge metric that can increase or decrease.

    Useful for tracking: current connections, active sessions, queue size.

    Attributes:
        name: Metric name
        help_text: Description of what this metric measures
        value: Current gauge value
        labels: Optional label key-value pairs
    """

    name: str
    help_text: str = ""
    value: float = 0.0
    labels: Dict[str, str] = field(default_factory=dict)
    _lock: threading.Lock = field(default_factory=threading.Lock, repr=False)

    def set(self, value: float) -> None:
        """Set gauge to specific value."""
        with self._lock:
            self.value = value

    def inc(self, amount: float = 1.0) -> None:
        """Increment gauge."""
        with self._lock:
            self.value += amount

    def dec(self, amount: float = 1.0) -> None:
        """Decrement gauge."""
        with self._lock:
            self.value -= amount

    def get(self) -> float:
        """Get current value."""
        with self._lock:
            return self.value


@dataclass
class Histogram:
    """
    Histogram for tracking value distributions.

    Useful for tracking: latencies, sizes, durations.

    Attributes:
        name: Metric name
        help_text: Description of what this metric measures
        buckets: Bucket boundaries
        bucket_counts: Count of observations in each bucket
        sum: Sum of all observed values
        count: Total number of observations
        labels: Optional label key-value pairs
    """

    name: str
    help_text: str = ""
    buckets: Tuple[float, ...] = (
        0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0
    )
    bucket_counts: Dict[float, int] = field(default_factory=dict)
    sum: float = 0.0
    count: int = 0
    labels: Dict[str, str] = field(default_factory=dict)
    _lock: threading.Lock = field(default_factory=threading.Lock, repr=False)

    def __post_init__(self):
        """Initialize bucket counts."""
        for bucket in self.buckets:
            self.bucket_counts[bucket] = 0
        # Add +Inf bucket
        self.bucket_counts[float("inf")] = 0

    def observe(self, value: float) -> None:
        """
        Record an observation.

        Args:
            value: Value to observe
        """
        with self._lock:
            self.sum += value
            self.count += 1

            # Increment all buckets >= value
            for bucket in self.buckets:
                if value <= bucket:
                    self.bucket_counts[bucket] = self.bucket_counts.get(bucket, 0) + 1

            # Always increment +Inf
            self.bucket_counts[float("inf")] = self.bucket_counts.get(float("inf"), 0) + 1

    def get_percentile(self, percentile: float) -> Optional[float]:
        """
        Estimate percentile value from histogram.

        Args:
            percentile: Percentile to calculate (0.0 to 1.0)

        Returns:
            Estimated percentile value or None if no observations
        """
        with self._lock:
            if self.count == 0:
                return None

            target = percentile * self.count
            cumulative = 0

            sorted_buckets = sorted(
                [b for b in self.bucket_counts.keys() if b != float("inf")]
            )

            for bucket in sorted_buckets:
                cumulative += self.bucket_counts.get(bucket, 0)
                if cumulative >= target:
                    return bucket

            return sorted_buckets[-1] if sorted_buckets else None

    def get_stats(self) -> Dict[str, Any]:
        """Get histogram statistics."""
        with self._lock:
            avg = self.sum / self.count if self.count > 0 else 0
            return {
                "count": self.count,
                "sum": self.sum,
                "avg": avg,
                "p50": self.get_percentile(0.5),
                "p95": self.get_percentile(0.95),
                "p99": self.get_percentile(0.99),
            }


# =============================================================================
# Labeled Metrics Store
# =============================================================================


class LabeledCounter:
    """
    Counter with label support for multiple dimensions.

    Allows tracking different series under the same metric name.
    """

    def __init__(self, name: str, help_text: str = "", label_names: Tuple[str, ...] = ()):
        self.name = name
        self.help_text = help_text
        self.label_names = label_names
        self._counters: Dict[Tuple[str, ...], int] = {}
        self._lock = threading.Lock()

    def labels(self, **kwargs: str) -> "LabeledCounterValue":
        """Get counter for specific label values."""
        label_values = tuple(kwargs.get(name, "") for name in self.label_names)
        return LabeledCounterValue(self, label_values)

    def inc(self, label_values: Tuple[str, ...], amount: int = 1) -> None:
        """Increment counter for label values."""
        with self._lock:
            current = self._counters.get(label_values, 0)
            self._counters[label_values] = current + amount

    def get_all(self) -> Dict[Tuple[str, ...], int]:
        """Get all counter values."""
        with self._lock:
            return dict(self._counters)


class LabeledCounterValue:
    """Wrapper for incrementing a specific labeled counter."""

    def __init__(self, parent: LabeledCounter, label_values: Tuple[str, ...]):
        self._parent = parent
        self._label_values = label_values

    def inc(self, amount: int = 1) -> None:
        """Increment this counter."""
        self._parent.inc(self._label_values, amount)


# =============================================================================
# Metrics Manager
# =============================================================================


class MetricsManager:
    """
    Collects and manages operational metrics for Ash-Bot.

    Provides methods to record various metrics and export them
    in different formats (Prometheus, JSON).

    Attributes:
        start_time: When the metrics manager was created

    Example:
        >>> metrics = create_metrics_manager()
        >>> metrics.inc_messages_processed()
        >>> metrics.inc_alerts_sent(severity="high", channel_type="crisis")
        >>> print(metrics.export_json())
    """

    def __init__(self):
        """Initialize MetricsManager with all metrics."""
        self.start_time = time.time()
        self._lock = threading.Lock()

        # Initialize all metrics
        self._setup_metrics()

        logger.info(f"✅ MetricsManager v{__version__} initialized")

    def _setup_metrics(self) -> None:
        """Initialize all metric instances."""
        # =================================================================
        # Counters
        # =================================================================

        self._messages_processed = Counter(
            name="ash_messages_processed_total",
            help_text="Total messages processed by the bot",
        )

        self._messages_analyzed = LabeledCounter(
            name="ash_messages_analyzed_total",
            help_text="Messages analyzed by NLP by severity",
            label_names=("severity",),
        )

        self._alerts_sent = LabeledCounter(
            name="ash_alerts_sent_total",
            help_text="Alerts sent by severity and channel type",
            label_names=("severity", "channel_type"),
        )

        self._ash_sessions = Counter(
            name="ash_sessions_total",
            help_text="Total Ash personality sessions started",
        )

        self._nlp_errors = Counter(
            name="ash_nlp_errors_total",
            help_text="Total NLP API errors",
        )

        self._redis_operations = LabeledCounter(
            name="ash_redis_operations_total",
            help_text="Redis operations by type and status",
            label_names=("operation", "status"),
        )

        self._redis_errors = Counter(
            name="ash_redis_errors_total",
            help_text="Total Redis errors",
        )

        self._discord_reconnects = Counter(
            name="ash_discord_reconnects_total",
            help_text="Discord gateway reconnection count",
        )

        self._claude_requests = Counter(
            name="ash_claude_requests_total",
            help_text="Total Claude API requests",
        )

        self._claude_errors = Counter(
            name="ash_claude_errors_total",
            help_text="Total Claude API errors",
        )

        # =================================================================
        # Gauges
        # =================================================================

        self._active_ash_sessions = Gauge(
            name="ash_sessions_active",
            help_text="Currently active Ash personality sessions",
        )

        self._connected_guilds = Gauge(
            name="ash_connected_guilds",
            help_text="Number of Discord guilds the bot is in",
        )

        self._circuit_breaker_state = LabeledCounter(
            name="ash_circuit_breaker_state",
            help_text="Circuit breaker state (0=closed, 1=open, 2=half-open)",
            label_names=("breaker",),
        )

        # =================================================================
        # Histograms
        # =================================================================

        self._nlp_duration = Histogram(
            name="ash_nlp_request_duration_seconds",
            help_text="NLP API request duration in seconds",
            buckets=(0.05, 0.1, 0.25, 0.5, 0.75, 1.0, 2.0, 3.0, 5.0, 10.0),
        )

        self._claude_duration = Histogram(
            name="ash_claude_request_duration_seconds",
            help_text="Claude API request duration in seconds",
            buckets=(0.5, 1.0, 2.0, 3.0, 5.0, 7.5, 10.0, 15.0, 20.0, 30.0),
        )

        self._redis_duration = Histogram(
            name="ash_redis_operation_duration_seconds",
            help_text="Redis operation duration in seconds",
            buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0),
        )

    # =========================================================================
    # Message Metrics
    # =========================================================================

    def inc_messages_processed(self, count: int = 1) -> None:
        """Increment messages processed counter."""
        self._messages_processed.inc(count)

    def inc_messages_analyzed(self, severity: str, count: int = 1) -> None:
        """
        Increment messages analyzed counter.

        Args:
            severity: Crisis severity level (critical, high, medium, low, safe)
            count: Number to increment by
        """
        self._messages_analyzed.labels(severity=severity.lower()).inc(count)

    # =========================================================================
    # Alert Metrics
    # =========================================================================

    def inc_alerts_sent(self, severity: str, channel_type: str, count: int = 1) -> None:
        """
        Increment alerts sent counter.

        Args:
            severity: Crisis severity level
            channel_type: Channel type (crisis, monitor, dm)
            count: Number to increment by
        """
        self._alerts_sent.labels(
            severity=severity.lower(),
            channel_type=channel_type.lower(),
        ).inc(count)

    # =========================================================================
    # Ash Session Metrics
    # =========================================================================

    def inc_ash_sessions(self, count: int = 1) -> None:
        """Increment total Ash sessions counter."""
        self._ash_sessions.inc(count)

    def set_active_ash_sessions(self, count: int) -> None:
        """Set currently active Ash sessions gauge."""
        self._active_ash_sessions.set(float(count))

    # =========================================================================
    # NLP Metrics
    # =========================================================================

    def observe_nlp_duration(self, duration_seconds: float) -> None:
        """Record NLP request duration."""
        self._nlp_duration.observe(duration_seconds)

    def inc_nlp_errors(self, count: int = 1) -> None:
        """Increment NLP error counter."""
        self._nlp_errors.inc(count)

    # =========================================================================
    # Claude API Metrics
    # =========================================================================

    def inc_claude_requests(self, count: int = 1) -> None:
        """Increment Claude API request counter."""
        self._claude_requests.inc(count)

    def observe_claude_duration(self, duration_seconds: float) -> None:
        """Record Claude API request duration."""
        self._claude_duration.observe(duration_seconds)

    def inc_claude_errors(self, count: int = 1) -> None:
        """Increment Claude API error counter."""
        self._claude_errors.inc(count)

    # =========================================================================
    # Redis Metrics
    # =========================================================================

    def inc_redis_operations(self, operation: str, status: str = "success", count: int = 1) -> None:
        """
        Increment Redis operations counter.

        Args:
            operation: Operation type (zadd, zrange, delete, etc.)
            status: Operation result (success, failure, error)
            count: Number to increment by
        """
        self._redis_operations.labels(
            operation=operation.lower(),
            status=status.lower(),
        ).inc(count)

    def set_ash_sessions_active(self, count: int) -> None:
        """Set currently active Ash sessions gauge (alias for set_active_ash_sessions)."""
        self._active_ash_sessions.set(float(count))

    def observe_redis_duration(self, duration_seconds: float) -> None:
        """Record Redis operation duration."""
        self._redis_duration.observe(duration_seconds)

    def inc_redis_errors(self, count: int = 1) -> None:
        """Increment Redis error counter."""
        self._redis_errors.inc(count)

    # =========================================================================
    # Discord Metrics
    # =========================================================================

    def inc_discord_reconnects(self, count: int = 1) -> None:
        """Increment Discord reconnection counter."""
        self._discord_reconnects.inc(count)

    def set_connected_guilds(self, count: int) -> None:
        """Set connected guilds gauge."""
        self._connected_guilds.set(float(count))

    # =========================================================================
    # Export Methods
    # =========================================================================

    def export_prometheus(self) -> str:
        """
        Export all metrics in Prometheus text format.

        Returns:
            Prometheus-formatted metrics string
        """
        lines: List[str] = []
        timestamp = int(time.time() * 1000)  # Milliseconds

        # Helper to add metric
        def add_metric(name: str, help_text: str, metric_type: str, value: float, labels: Dict[str, str] = None):
            lines.append(f"# HELP {name} {help_text}")
            lines.append(f"# TYPE {name} {metric_type}")

            label_str = ""
            if labels:
                label_parts = [f'{k}="{v}"' for k, v in labels.items()]
                label_str = "{" + ",".join(label_parts) + "}"

            lines.append(f"{name}{label_str} {value}")

        # Uptime
        uptime = time.time() - self.start_time
        add_metric(
            "ash_uptime_seconds",
            "Time since metrics manager started",
            "gauge",
            uptime,
        )

        # Simple counters
        add_metric(
            self._messages_processed.name,
            self._messages_processed.help_text,
            "counter",
            self._messages_processed.get(),
        )

        add_metric(
            self._ash_sessions.name,
            self._ash_sessions.help_text,
            "counter",
            self._ash_sessions.get(),
        )

        add_metric(
            self._nlp_errors.name,
            self._nlp_errors.help_text,
            "counter",
            self._nlp_errors.get(),
        )

        add_metric(
            self._redis_errors.name,
            self._redis_errors.help_text,
            "counter",
            self._redis_errors.get(),
        )

        add_metric(
            self._discord_reconnects.name,
            self._discord_reconnects.help_text,
            "counter",
            self._discord_reconnects.get(),
        )

        add_metric(
            self._claude_requests.name,
            self._claude_requests.help_text,
            "counter",
            self._claude_requests.get(),
        )

        add_metric(
            self._claude_errors.name,
            self._claude_errors.help_text,
            "counter",
            self._claude_errors.get(),
        )

        # Gauges
        add_metric(
            self._active_ash_sessions.name,
            self._active_ash_sessions.help_text,
            "gauge",
            self._active_ash_sessions.get(),
        )

        add_metric(
            self._connected_guilds.name,
            self._connected_guilds.help_text,
            "gauge",
            self._connected_guilds.get(),
        )

        # Labeled counters
        lines.append(f"# HELP {self._messages_analyzed.name} {self._messages_analyzed.help_text}")
        lines.append(f"# TYPE {self._messages_analyzed.name} counter")
        for labels, value in self._messages_analyzed.get_all().items():
            label_str = f'{{severity="{labels[0]}"}}'
            lines.append(f"{self._messages_analyzed.name}{label_str} {value}")

        lines.append(f"# HELP {self._alerts_sent.name} {self._alerts_sent.help_text}")
        lines.append(f"# TYPE {self._alerts_sent.name} counter")
        for labels, value in self._alerts_sent.get_all().items():
            label_str = f'{{severity="{labels[0]}",channel_type="{labels[1]}"}}'
            lines.append(f"{self._alerts_sent.name}{label_str} {value}")

        lines.append(f"# HELP {self._redis_operations.name} {self._redis_operations.help_text}")
        lines.append(f"# TYPE {self._redis_operations.name} counter")
        for labels, value in self._redis_operations.get_all().items():
            label_str = f'{{operation="{labels[0]}",status="{labels[1]}"}}'
            lines.append(f"{self._redis_operations.name}{label_str} {value}")

        # Histograms
        for histogram in [self._nlp_duration, self._claude_duration, self._redis_duration]:
            lines.append(f"# HELP {histogram.name} {histogram.help_text}")
            lines.append(f"# TYPE {histogram.name} histogram")
            
            cumulative = 0
            for bucket in sorted(histogram.bucket_counts.keys()):
                if bucket == float("inf"):
                    lines.append(f'{histogram.name}_bucket{{le="+Inf"}} {histogram.bucket_counts[bucket]}')
                else:
                    cumulative += histogram.bucket_counts.get(bucket, 0)
                    lines.append(f'{histogram.name}_bucket{{le="{bucket}"}} {cumulative}')
            
            lines.append(f"{histogram.name}_sum {histogram.sum}")
            lines.append(f"{histogram.name}_count {histogram.count}")

        return "\n".join(lines)

    def export_json(self) -> Dict[str, Any]:
        """
        Export all metrics as JSON dictionary.

        Returns:
            Dictionary of all metrics
        """
        uptime = time.time() - self.start_time

        return {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "uptime_seconds": uptime,
            "counters": {
                "messages_processed": self._messages_processed.get(),
                "messages_analyzed": dict(self._messages_analyzed.get_all()),
                "alerts_sent": {
                    f"{k[0]}_{k[1]}": v
                    for k, v in self._alerts_sent.get_all().items()
                },
                "ash_sessions": self._ash_sessions.get(),
                "nlp_errors": self._nlp_errors.get(),
                "redis_operations": dict(self._redis_operations.get_all()),
                "redis_errors": self._redis_errors.get(),
                "discord_reconnects": self._discord_reconnects.get(),
                "claude_requests": self._claude_requests.get(),
                "claude_errors": self._claude_errors.get(),
            },
            "gauges": {
                "active_ash_sessions": self._active_ash_sessions.get(),
                "connected_guilds": self._connected_guilds.get(),
            },
            "histograms": {
                "nlp_duration": self._nlp_duration.get_stats(),
                "claude_duration": self._claude_duration.get_stats(),
                "redis_duration": self._redis_duration.get_stats(),
            },
        }

    def reset_all(self) -> None:
        """Reset all metrics (use with caution, mainly for testing)."""
        self._setup_metrics()
        logger.warning("⚠️ All metrics have been reset")

    def __repr__(self) -> str:
        """String representation."""
        return f"MetricsManager(uptime={time.time() - self.start_time:.1f}s)"


# =============================================================================
# Factory Function
# =============================================================================


def create_metrics_manager() -> MetricsManager:
    """
    Factory function for MetricsManager.

    Creates a MetricsManager instance.
    Following Clean Architecture v5.1 Rule #1: Factory Functions.

    Returns:
        Configured MetricsManager instance

    Example:
        >>> metrics = create_metrics_manager()
        >>> metrics.inc_messages_processed()
    """
    logger.info("🏭 Creating MetricsManager")
    return MetricsManager()


# =============================================================================
# Export public interface
# =============================================================================

__all__ = [
    "MetricsManager",
    "Counter",
    "Gauge",
    "Histogram",
    "LabeledCounter",
    "create_metrics_manager",
]
