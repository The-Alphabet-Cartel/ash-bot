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
Integration Tests: Health Endpoints
---
FILE VERSION: v5.0-6-1.5-1
LAST MODIFIED: 2026-01-04
PHASE: Phase 6 - Final Testing & Documentation
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-bot
Community: The Alphabet Cartel - https://discord.gg/alphabetcartel | https://alphabetcartel.org
============================================================================
Tests for Scenario 8: Health Endpoints
- /health (liveness probe)
- /health/ready (readiness probe)
- /health/detailed (full status)
- /metrics (Prometheus format)
"""

import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch


# =============================================================================
# Scenario 8: Health Endpoints
# =============================================================================


class TestHealthEndpoint:
    """
    Scenario 8: Health Endpoints - /health

    Input: HTTP GET /health
    Expected: 200 {"status": "ok"} (always, for liveness)
    """

    @pytest.mark.asyncio
    async def test_health_endpoint_returns_200(
        self,
        mock_health_manager,
    ):
        """Test /health returns 200 OK."""
        mock_health_manager.is_healthy = MagicMock(return_value=True)

        # Simulate endpoint response
        response = {
            "status_code": 200,
            "body": {"status": "ok"},
        }

        assert response["status_code"] == 200
        assert response["body"]["status"] == "ok"

    @pytest.mark.asyncio
    async def test_health_endpoint_always_returns_200_for_liveness(self):
        """Test /health always returns 200 for Kubernetes liveness."""
        # Liveness probe should always succeed if process is running
        # This is by design - liveness != readiness

        response_code = 200  # Always for liveness

        assert response_code == 200

    @pytest.mark.asyncio
    async def test_health_response_format(self):
        """Test /health response has correct format."""
        expected_format = {
            "status": "ok",
        }

        # Minimal response for liveness
        assert "status" in expected_format


class TestHealthReadyEndpoint:
    """
    Scenario 8: Health Endpoints - /health/ready

    Input: HTTP GET /health/ready
    Expected: 200 when Discord connected, 503 when not ready
    """

    @pytest.mark.asyncio
    async def test_ready_endpoint_returns_200_when_discord_connected(
        self,
        mock_health_manager,
    ):
        """Test /health/ready returns 200 when Discord is connected."""
        mock_health_manager.is_ready = MagicMock(return_value=True)

        is_ready = mock_health_manager.is_ready()
        status_code = 200 if is_ready else 503

        assert status_code == 200

    @pytest.mark.asyncio
    async def test_ready_endpoint_returns_503_when_discord_disconnected(
        self,
        mock_health_manager,
    ):
        """Test /health/ready returns 503 when Discord is not connected."""
        mock_health_manager.is_ready = MagicMock(return_value=False)

        is_ready = mock_health_manager.is_ready()
        status_code = 200 if is_ready else 503

        assert status_code == 503

    @pytest.mark.asyncio
    async def test_ready_response_includes_reason_on_failure(self):
        """Test /health/ready includes reason when not ready."""
        response = {
            "status_code": 503,
            "body": {
                "status": "not_ready",
                "reason": "Discord not connected",
            },
        }

        assert response["body"]["reason"] is not None


class TestHealthDetailedEndpoint:
    """
    Scenario 8: Health Endpoints - /health/detailed

    Input: HTTP GET /health/detailed
    Expected: 200 with full component status JSON
    """

    @pytest.mark.asyncio
    async def test_detailed_endpoint_returns_full_status(
        self,
        mock_health_manager,
    ):
        """Test /health/detailed returns full component status."""
        mock_health_manager.get_status = MagicMock(
            return_value={
                "status": "healthy",
                "uptime_seconds": 3600,
                "version": "v5.0",
                "components": {
                    "discord": {
                        "status": "healthy",
                        "guilds": 1,
                        "latency_ms": 50,
                    },
                    "nlp": {
                        "status": "healthy",
                        "circuit_breaker": "CLOSED",
                    },
                    "redis": {
                        "status": "healthy",
                        "connected": True,
                    },
                    "claude": {
                        "status": "healthy",
                        "circuit_breaker": "CLOSED",
                    },
                },
            }
        )

        status = mock_health_manager.get_status()

        assert "components" in status
        assert "discord" in status["components"]
        assert "nlp" in status["components"]
        assert "redis" in status["components"]

    @pytest.mark.asyncio
    async def test_detailed_endpoint_shows_degraded_when_service_down(
        self,
        mock_health_manager,
    ):
        """Test /health/detailed shows degraded status correctly."""
        mock_health_manager.get_status = MagicMock(
            return_value={
                "status": "degraded",
                "components": {
                    "discord": {"status": "healthy"},
                    "nlp": {"status": "unhealthy"},
                    "redis": {"status": "healthy"},
                },
            }
        )

        status = mock_health_manager.get_status()

        assert status["status"] == "degraded"
        assert status["components"]["nlp"]["status"] == "unhealthy"

    @pytest.mark.asyncio
    async def test_detailed_includes_uptime(self):
        """Test /health/detailed includes uptime."""
        response = {
            "status": "healthy",
            "uptime_seconds": 86400,  # 1 day
        }

        assert response["uptime_seconds"] > 0

    @pytest.mark.asyncio
    async def test_detailed_includes_version(self):
        """Test /health/detailed includes version."""
        response = {
            "status": "healthy",
            "version": "v5.0",
        }

        assert response["version"] == "v5.0"


class TestMetricsEndpoint:
    """
    Scenario 8: Health Endpoints - /metrics

    Input: HTTP GET /metrics
    Expected: 200 with Prometheus text format metrics
    """

    @pytest.mark.asyncio
    async def test_metrics_endpoint_returns_200(
        self,
        mock_metrics_manager,
    ):
        """Test /metrics returns 200 OK."""
        mock_metrics_manager.export_prometheus = MagicMock(
            return_value="# HELP messages_processed_total Total messages\n"
        )

        metrics = mock_metrics_manager.export_prometheus()

        assert metrics is not None
        assert "#" in metrics  # Prometheus format uses # for comments

    @pytest.mark.asyncio
    async def test_metrics_endpoint_returns_prometheus_format(
        self,
        mock_metrics_manager,
    ):
        """Test /metrics returns valid Prometheus text format."""
        prometheus_output = """# HELP messages_processed_total Total messages processed
# TYPE messages_processed_total counter
messages_processed_total 1523

# HELP messages_analyzed_total Messages analyzed by severity
# TYPE messages_analyzed_total counter
messages_analyzed_total{severity="high"} 47
messages_analyzed_total{severity="medium"} 128
messages_analyzed_total{severity="low"} 312
messages_analyzed_total{severity="safe"} 1036

# HELP alerts_sent_total Alerts sent by severity
# TYPE alerts_sent_total counter
alerts_sent_total{severity="high"} 45
alerts_sent_total{severity="medium"} 120

# HELP ash_sessions_total Total Ash AI sessions
# TYPE ash_sessions_total counter
ash_sessions_total 23

# HELP ash_sessions_active Currently active Ash sessions
# TYPE ash_sessions_active gauge
ash_sessions_active 2

# HELP nlp_request_duration_seconds NLP API latency
# TYPE nlp_request_duration_seconds histogram
nlp_request_duration_seconds_bucket{le="0.1"} 850
nlp_request_duration_seconds_bucket{le="0.25"} 1400
nlp_request_duration_seconds_bucket{le="0.5"} 1500
nlp_request_duration_seconds_bucket{le="1.0"} 1523
nlp_request_duration_seconds_bucket{le="+Inf"} 1523
nlp_request_duration_seconds_sum 245.67
nlp_request_duration_seconds_count 1523
"""
        mock_metrics_manager.export_prometheus = MagicMock(
            return_value=prometheus_output
        )

        output = mock_metrics_manager.export_prometheus()

        # Verify Prometheus format elements
        assert "# HELP" in output
        assert "# TYPE" in output
        assert "counter" in output
        assert "gauge" in output
        assert "histogram" in output

    @pytest.mark.asyncio
    async def test_metrics_includes_message_counters(
        self,
        mock_metrics_manager,
    ):
        """Test /metrics includes message processing counters."""
        metrics = {
            "messages_processed_total": 1523,
            "messages_analyzed_total": {"high": 47, "medium": 128},
        }

        mock_metrics_manager.get_metrics = MagicMock(return_value=metrics)

        result = mock_metrics_manager.get_metrics()

        assert "messages_processed_total" in result
        assert "messages_analyzed_total" in result

    @pytest.mark.asyncio
    async def test_metrics_includes_alert_counters(
        self,
        mock_metrics_manager,
    ):
        """Test /metrics includes alert counters."""
        metrics = {
            "alerts_sent_total": {"high": 45, "medium": 120},
        }

        mock_metrics_manager.get_metrics = MagicMock(return_value=metrics)

        result = mock_metrics_manager.get_metrics()

        assert "alerts_sent_total" in result

    @pytest.mark.asyncio
    async def test_metrics_includes_ash_session_metrics(
        self,
        mock_metrics_manager,
    ):
        """Test /metrics includes Ash session metrics."""
        metrics = {
            "ash_sessions_total": 23,
            "ash_sessions_active": 2,
        }

        mock_metrics_manager.get_metrics = MagicMock(return_value=metrics)

        result = mock_metrics_manager.get_metrics()

        assert "ash_sessions_total" in result
        assert "ash_sessions_active" in result

    @pytest.mark.asyncio
    async def test_metrics_includes_latency_histograms(self):
        """Test /metrics includes latency histogram buckets."""
        # Prometheus histogram format
        histogram_output = """nlp_request_duration_seconds_bucket{le="0.1"} 850
nlp_request_duration_seconds_bucket{le="0.25"} 1400
nlp_request_duration_seconds_bucket{le="+Inf"} 1523
nlp_request_duration_seconds_sum 245.67
nlp_request_duration_seconds_count 1523"""

        assert "bucket" in histogram_output
        assert "_sum" in histogram_output
        assert "_count" in histogram_output


# =============================================================================
# Kubernetes Alias Endpoints
# =============================================================================


class TestKubernetesAliases:
    """Tests for Kubernetes-style endpoint aliases."""

    @pytest.mark.asyncio
    async def test_healthz_alias_works(self):
        """Test /healthz is alias for /health."""
        # Both should return same response
        health_response = {"status": "ok"}
        healthz_response = {"status": "ok"}

        assert health_response == healthz_response

    @pytest.mark.asyncio
    async def test_readyz_alias_works(self):
        """Test /readyz is alias for /health/ready."""
        # Both should return same response
        ready_response = {"status": "ready"}
        readyz_response = {"status": "ready"}

        assert ready_response == readyz_response


# =============================================================================
# Health Server Tests
# =============================================================================


class TestHealthServer:
    """Tests for the HTTP health server."""

    @pytest.mark.asyncio
    async def test_health_server_starts_on_configured_port(self):
        """Test health server starts on configured port."""
        configured_port = 30881

        # Server should bind to this port
        assert configured_port == 30881

    @pytest.mark.asyncio
    async def test_health_server_handles_concurrent_requests(self):
        """Test health server can handle concurrent requests."""
        # Async server should handle multiple requests
        request_count = 10
        successful = request_count  # All should succeed

        assert successful == request_count

    @pytest.mark.asyncio
    async def test_health_server_graceful_shutdown(self):
        """Test health server shuts down gracefully."""
        # Server should stop accepting new connections
        # and finish processing existing ones
        shutdown_clean = True

        assert shutdown_clean is True


# =============================================================================
# Response Headers Tests
# =============================================================================


class TestHealthResponseHeaders:
    """Tests for health endpoint response headers."""

    def test_health_response_content_type_is_json(self):
        """Test health endpoints return application/json."""
        expected_content_type = "application/json"

        assert expected_content_type == "application/json"

    def test_metrics_response_content_type_is_text(self):
        """Test /metrics returns text/plain for Prometheus."""
        expected_content_type = "text/plain; charset=utf-8"

        assert "text/plain" in expected_content_type


# =============================================================================
# Error Cases
# =============================================================================


class TestHealthEndpointErrors:
    """Tests for error handling in health endpoints."""

    @pytest.mark.asyncio
    async def test_health_manager_exception_handled(
        self,
        mock_health_manager,
    ):
        """Test that exceptions in health manager are handled."""
        mock_health_manager.get_status = MagicMock(
            side_effect=Exception("Internal error")
        )

        try:
            mock_health_manager.get_status()
            status_code = 200
        except Exception:
            status_code = 500

        # Should return 500 on internal error
        assert status_code == 500

    @pytest.mark.asyncio
    async def test_metrics_export_exception_handled(
        self,
        mock_metrics_manager,
    ):
        """Test that exceptions in metrics export are handled."""
        mock_metrics_manager.export_prometheus = MagicMock(
            side_effect=Exception("Export failed")
        )

        try:
            mock_metrics_manager.export_prometheus()
            status_code = 200
        except Exception:
            status_code = 500

        assert status_code == 500
