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
Metrics Package for Ash-Bot Service
----------------------------------------------------------------------------
FILE VERSION: v5.0-8-1.0-1
LAST MODIFIED: 2026-01-05
PHASE: Phase 8 - Metrics & Reporting
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-bot
============================================================================

PACKAGE CONTENTS:
- MetricsManager: Collects and exports operational metrics
- Counter: Simple incrementing counter metric
- Gauge: Metric that can increase or decrease
- Histogram: Distribution tracking metric
- LabeledCounter: Counter with label dimensions
- ResponseMetricsManager: Tracks alert response times (Phase 8)
- AlertMetrics: Data model for individual alert metrics (Phase 8)
- DailyAggregate: Data model for daily aggregated metrics (Phase 8)
- WeeklySummary: Data model for weekly report summaries (Phase 8)

USAGE:
    from src.managers.metrics import create_metrics_manager, create_response_metrics_manager

    # Operational metrics
    metrics = create_metrics_manager()
    metrics.inc_messages_processed()

    # Response time tracking (Phase 8)
    response_metrics = create_response_metrics_manager(config, redis)
    await response_metrics.record_alert_created(...)
"""

# Module version
__version__ = "v5.0-8-1.0-1"

# Operational metrics (Phase 5)
from .metrics_manager import (
    MetricsManager,
    Counter,
    Gauge,
    Histogram,
    LabeledCounter,
    create_metrics_manager,
)

# Response time tracking (Phase 8)
from .response_metrics_manager import (
    ResponseMetricsManager,
    create_response_metrics_manager,
)

# Data models (Phase 8)
from .models import (
    AlertMetrics,
    DailyAggregate,
    WeeklySummary,
)

__all__ = [
    # Module version
    "__version__",
    # Operational metrics (Phase 5)
    "MetricsManager",
    "Counter",
    "Gauge",
    "Histogram",
    "LabeledCounter",
    "create_metrics_manager",
    # Response time tracking (Phase 8)
    "ResponseMetricsManager",
    "create_response_metrics_manager",
    # Data models (Phase 8)
    "AlertMetrics",
    "DailyAggregate",
    "WeeklySummary",
]
