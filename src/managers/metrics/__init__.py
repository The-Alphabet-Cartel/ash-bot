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
---
FILE VERSION: v5.0-5-5.5-1
LAST MODIFIED: 2026-01-04
PHASE: Phase 5 - Production Hardening
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-bot
Community: The Alphabet Cartel - https://discord.gg/alphabetcartel | https://alphabetcartel.org
============================================================================
PACKAGE CONTENTS:
- MetricsManager: Collects and exports operational metrics
- Counter: Simple incrementing counter metric
- Gauge: Metric that can increase or decrease
- Histogram: Distribution tracking metric
- LabeledCounter: Counter with label dimensions

USAGE:
    from src.managers.metrics import create_metrics_manager

    metrics = create_metrics_manager()
    metrics.inc_messages_processed()
    print(metrics.export_json())
"""

# Module version
__version__ = "v5.0-5-5.5-1"

from .metrics_manager import (
    MetricsManager,
    Counter,
    Gauge,
    Histogram,
    LabeledCounter,
    create_metrics_manager,
)

__all__ = [
    "__version__",
    "MetricsManager",
    "Counter",
    "Gauge",
    "Histogram",
    "LabeledCounter",
    "create_metrics_manager",
]
