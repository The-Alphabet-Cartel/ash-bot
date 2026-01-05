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
Reporting Package - Automated Report Generation and Delivery
----------------------------------------------------------------------------
FILE VERSION: v5.0-8-2.0-1
LAST MODIFIED: 2026-01-05
PHASE: Phase 8 - Metrics & Reporting
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-bot
============================================================================

PACKAGE CONTENTS:
- WeeklyReportManager: Generates and posts weekly CRT summary reports

USAGE:
    from src.managers.reporting import create_weekly_report_manager

    report_mgr = create_weekly_report_manager(
        config_manager=config,
        response_metrics_manager=metrics,
        bot=discord_bot,
    )

    await report_mgr.start()
"""

from src.managers.reporting.weekly_report_manager import (
    WeeklyReportManager,
    create_weekly_report_manager,
    DAY_NAME_TO_WEEKDAY,
)


__version__ = "v5.0-8-2.0-1"


__all__ = [
    "WeeklyReportManager",
    "create_weekly_report_manager",
    "DAY_NAME_TO_WEEKDAY",
]
