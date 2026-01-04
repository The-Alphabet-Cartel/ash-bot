"""
============================================================================
Ash-Bot: Crisis Detection Discord Bot
The Alphabet Cartel - https://discord.gg/alphabetcartel | alphabetcartel.org
============================================================================
Test Suite for Metrics Manager
---
FILE VERSION: v5.0-5-5.2-1
LAST MODIFIED: 2026-01-04
PHASE: Phase 5 - Production Hardening
Repository: https://github.com/the-alphabet-cartel/ash-bot
============================================================================
Tests for MetricsManager and metric types.
"""

import threading
import time

import pytest

from src.managers.metrics import (
    MetricsManager,
    Counter,
    Gauge,
    Histogram,
    create_metrics_manager,
)


# =============================================================================
# Counter Tests
# =============================================================================


class TestCounter:
    """Tests for Counter metric type."""

    def test_counter_initialization(self):
        """Test counter initializes to zero."""
        counter = Counter(name="test_counter", help_text="Test counter")
        assert counter.get() == 0
        assert counter.name == "test_counter"
        assert counter.help_text == "Test counter"

    def test_counter_increment(self):
        """Test counter increments correctly."""
        counter = Counter(name="test")
        counter.inc()
        assert counter.get() == 1

    def test_counter_increment_by_amount(self):
        """Test counter increments by specified amount."""
        counter = Counter(name="test")
        counter.inc(5)
        assert counter.get() == 5
        counter.inc(3)
        assert counter.get() == 8

    def test_counter_rejects_negative(self):
        """Test counter rejects negative increments."""
        counter = Counter(name="test")
        with pytest.raises(ValueError, match="can only increase"):
            counter.inc(-1)

    def test_counter_reset(self):
        """Test counter reset."""
        counter = Counter(name="test")
        counter.inc(10)
        counter.reset()
        assert counter.get() == 0

    def test_counter_thread_safety(self):
        """Test counter is thread-safe."""
        counter = Counter(name="test")
        threads = []

        def increment_100_times():
            for _ in range(100):
                counter.inc()

        for _ in range(10):
            t = threading.Thread(target=increment_100_times)
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        assert counter.get() == 1000


# =============================================================================
# Gauge Tests
# =============================================================================


class TestGauge:
    """Tests for Gauge metric type."""

    def test_gauge_initialization(self):
        """Test gauge initializes to zero."""
        gauge = Gauge(name="test_gauge", help_text="Test gauge")
        assert gauge.get() == 0.0
        assert gauge.name == "test_gauge"

    def test_gauge_set(self):
        """Test gauge set value."""
        gauge = Gauge(name="test")
        gauge.set(42.5)
        assert gauge.get() == 42.5

    def test_gauge_increment(self):
        """Test gauge increment."""
        gauge = Gauge(name="test")
        gauge.inc(5.0)
        assert gauge.get() == 5.0
        gauge.inc(2.5)
        assert gauge.get() == 7.5

    def test_gauge_decrement(self):
        """Test gauge decrement."""
        gauge = Gauge(name="test")
        gauge.set(10.0)
        gauge.dec(3.0)
        assert gauge.get() == 7.0

    def test_gauge_can_go_negative(self):
        """Test gauge can have negative values."""
        gauge = Gauge(name="test")
        gauge.dec(5.0)
        assert gauge.get() == -5.0

    def test_gauge_thread_safety(self):
        """Test gauge is thread-safe."""
        gauge = Gauge(name="test")

        def set_values():
            for i in range(100):
                gauge.set(float(i))

        threads = [threading.Thread(target=set_values) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Should have some valid value (not corrupt)
        value = gauge.get()
        assert 0 <= value < 100


# =============================================================================
# Histogram Tests
# =============================================================================


class TestHistogram:
    """Tests for Histogram metric type."""

    def test_histogram_initialization(self):
        """Test histogram initializes correctly."""
        histogram = Histogram(name="test_histogram", help_text="Test")
        assert histogram.count == 0
        assert histogram.sum == 0.0

    def test_histogram_observe(self):
        """Test histogram observation."""
        histogram = Histogram(name="test", buckets=(0.1, 0.5, 1.0))
        
        histogram.observe(0.05)
        assert histogram.count == 1
        assert histogram.sum == 0.05

        histogram.observe(0.25)
        assert histogram.count == 2
        assert histogram.sum == 0.30

    def test_histogram_buckets(self):
        """Test histogram bucket counts."""
        histogram = Histogram(name="test", buckets=(0.1, 0.5, 1.0))
        
        histogram.observe(0.05)  # Goes in 0.1, 0.5, 1.0, +Inf
        histogram.observe(0.25)  # Goes in 0.5, 1.0, +Inf
        histogram.observe(0.75)  # Goes in 1.0, +Inf
        histogram.observe(5.0)   # Goes only in +Inf
        
        assert histogram.bucket_counts.get(0.1, 0) >= 1
        assert histogram.bucket_counts.get(0.5, 0) >= 1
        assert histogram.bucket_counts.get(1.0, 0) >= 1

    def test_histogram_stats(self):
        """Test histogram statistics."""
        histogram = Histogram(name="test", buckets=(0.1, 0.5, 1.0))
        
        for value in [0.1, 0.2, 0.3, 0.4, 0.5]:
            histogram.observe(value)
        
        stats = histogram.get_stats()
        assert stats["count"] == 5
        assert stats["sum"] == 1.5
        assert stats["avg"] == 0.3

    def test_histogram_percentile_empty(self):
        """Test percentile returns None when empty."""
        histogram = Histogram(name="test")
        assert histogram.get_percentile(0.5) is None

    def test_histogram_thread_safety(self):
        """Test histogram is thread-safe."""
        histogram = Histogram(name="test")
        
        def observe_values():
            for i in range(100):
                histogram.observe(float(i) / 100)
        
        threads = [threading.Thread(target=observe_values) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        assert histogram.count == 1000


# =============================================================================
# MetricsManager Tests
# =============================================================================


class TestMetricsManager:
    """Tests for MetricsManager."""

    @pytest.fixture
    def metrics(self) -> MetricsManager:
        """Create a MetricsManager instance."""
        return create_metrics_manager()

    def test_factory_function(self):
        """Test factory function creates instance."""
        metrics = create_metrics_manager()
        assert isinstance(metrics, MetricsManager)

    def test_uptime_tracking(self, metrics):
        """Test uptime is tracked."""
        time.sleep(0.1)
        json_data = metrics.export_json()
        assert json_data["uptime_seconds"] >= 0.1

    # =========================================================================
    # Message Metrics Tests
    # =========================================================================

    def test_inc_messages_processed(self, metrics):
        """Test incrementing messages processed."""
        metrics.inc_messages_processed()
        metrics.inc_messages_processed()
        
        json_data = metrics.export_json()
        assert json_data["counters"]["messages_processed"] == 2

    def test_inc_messages_analyzed(self, metrics):
        """Test incrementing messages analyzed by severity."""
        metrics.inc_messages_analyzed(severity="high")
        metrics.inc_messages_analyzed(severity="high")
        metrics.inc_messages_analyzed(severity="low")
        
        json_data = metrics.export_json()
        analyzed = json_data["counters"]["messages_analyzed"]
        assert analyzed.get(("high",), 0) == 2
        assert analyzed.get(("low",), 0) == 1

    # =========================================================================
    # Alert Metrics Tests
    # =========================================================================

    def test_inc_alerts_sent(self, metrics):
        """Test incrementing alerts sent."""
        metrics.inc_alerts_sent(severity="critical", channel_type="crisis")
        metrics.inc_alerts_sent(severity="high", channel_type="crisis")
        metrics.inc_alerts_sent(severity="medium", channel_type="monitor")
        
        json_data = metrics.export_json()
        alerts = json_data["counters"]["alerts_sent"]
        assert "critical_crisis" in alerts or alerts.get(("critical", "crisis"), 0) > 0

    # =========================================================================
    # Ash Session Metrics Tests
    # =========================================================================

    def test_ash_session_metrics(self, metrics):
        """Test Ash session metrics."""
        metrics.inc_ash_sessions()
        metrics.inc_ash_sessions()
        metrics.set_active_ash_sessions(5)
        
        json_data = metrics.export_json()
        assert json_data["counters"]["ash_sessions"] == 2
        assert json_data["gauges"]["active_ash_sessions"] == 5.0

    # =========================================================================
    # NLP Metrics Tests
    # =========================================================================

    def test_nlp_duration_observation(self, metrics):
        """Test NLP duration histogram."""
        metrics.observe_nlp_duration(0.125)
        metrics.observe_nlp_duration(0.250)
        metrics.observe_nlp_duration(0.500)
        
        json_data = metrics.export_json()
        nlp_stats = json_data["histograms"]["nlp_duration"]
        assert nlp_stats["count"] == 3
        assert abs(nlp_stats["sum"] - 0.875) < 0.001

    def test_nlp_error_counting(self, metrics):
        """Test NLP error counting."""
        metrics.inc_nlp_errors()
        metrics.inc_nlp_errors(3)
        
        json_data = metrics.export_json()
        assert json_data["counters"]["nlp_errors"] == 4

    # =========================================================================
    # Claude API Metrics Tests
    # =========================================================================

    def test_claude_metrics(self, metrics):
        """Test Claude API metrics."""
        metrics.inc_claude_requests()
        metrics.observe_claude_duration(1.5)
        metrics.inc_claude_errors()
        
        json_data = metrics.export_json()
        assert json_data["counters"]["claude_requests"] == 1
        assert json_data["counters"]["claude_errors"] == 1
        assert json_data["histograms"]["claude_duration"]["count"] == 1

    # =========================================================================
    # Redis Metrics Tests
    # =========================================================================

    def test_redis_operation_metrics(self, metrics):
        """Test Redis operation metrics."""
        metrics.inc_redis_operations("get")
        metrics.inc_redis_operations("get")
        metrics.inc_redis_operations("set")
        metrics.observe_redis_duration(0.005)
        
        json_data = metrics.export_json()
        redis_ops = json_data["counters"]["redis_operations"]
        assert redis_ops.get(("get",), 0) == 2
        assert redis_ops.get(("set",), 0) == 1

    def test_redis_error_counting(self, metrics):
        """Test Redis error counting."""
        metrics.inc_redis_errors(2)
        
        json_data = metrics.export_json()
        assert json_data["counters"]["redis_errors"] == 2

    # =========================================================================
    # Discord Metrics Tests
    # =========================================================================

    def test_discord_metrics(self, metrics):
        """Test Discord metrics."""
        metrics.inc_discord_reconnects()
        metrics.set_connected_guilds(3)
        
        json_data = metrics.export_json()
        assert json_data["counters"]["discord_reconnects"] == 1
        assert json_data["gauges"]["connected_guilds"] == 3.0

    # =========================================================================
    # Export Tests
    # =========================================================================

    def test_export_json_structure(self, metrics):
        """Test JSON export structure."""
        json_data = metrics.export_json()
        
        assert "timestamp" in json_data
        assert "uptime_seconds" in json_data
        assert "counters" in json_data
        assert "gauges" in json_data
        assert "histograms" in json_data

    def test_export_prometheus_format(self, metrics):
        """Test Prometheus export format."""
        metrics.inc_messages_processed(5)
        
        prometheus = metrics.export_prometheus()
        
        # Should contain HELP and TYPE comments
        assert "# HELP" in prometheus
        assert "# TYPE" in prometheus
        
        # Should contain our metric
        assert "ash_messages_processed_total" in prometheus

    def test_export_prometheus_histogram(self, metrics):
        """Test Prometheus histogram export."""
        metrics.observe_nlp_duration(0.5)
        
        prometheus = metrics.export_prometheus()
        
        assert "ash_nlp_request_duration_seconds" in prometheus
        assert "_bucket" in prometheus
        assert "_sum" in prometheus
        assert "_count" in prometheus

    # =========================================================================
    # Reset Tests
    # =========================================================================

    def test_reset_all(self, metrics):
        """Test reset clears all metrics."""
        metrics.inc_messages_processed(100)
        metrics.inc_alerts_sent(severity="high", channel_type="crisis")
        
        metrics.reset_all()
        
        json_data = metrics.export_json()
        assert json_data["counters"]["messages_processed"] == 0

    # =========================================================================
    # Repr Tests
    # =========================================================================

    def test_repr(self, metrics):
        """Test string representation."""
        repr_str = repr(metrics)
        assert "MetricsManager" in repr_str
        assert "uptime=" in repr_str


# =============================================================================
# Thread Safety Tests
# =============================================================================


class TestMetricsThreadSafety:
    """Tests for thread-safe metric operations."""

    def test_concurrent_increments(self):
        """Test concurrent increments are safe."""
        metrics = create_metrics_manager()
        threads = []

        def increment_many():
            for _ in range(100):
                metrics.inc_messages_processed()

        for _ in range(10):
            t = threading.Thread(target=increment_many)
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        json_data = metrics.export_json()
        assert json_data["counters"]["messages_processed"] == 1000

    def test_concurrent_observations(self):
        """Test concurrent histogram observations are safe."""
        metrics = create_metrics_manager()
        threads = []

        def observe_many():
            for i in range(100):
                metrics.observe_nlp_duration(float(i) / 100)

        for _ in range(10):
            t = threading.Thread(target=observe_many)
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        json_data = metrics.export_json()
        assert json_data["histograms"]["nlp_duration"]["count"] == 1000
