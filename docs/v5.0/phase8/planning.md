# Phase 8: Metrics & Reporting - Planning Document

============================================================================
**Ash-Bot**: Crisis Detection Discord Bot for The Alphabet Cartel  
**The Alphabet Cartel** - https://discord.gg/alphabetcartel | alphabetcartel.org
============================================================================

**Document Version**: v1.0.0  
**Created**: 2026-01-05  
**Phase**: 8 - Metrics & Reporting  
**Status**: 🔵 Planning  
**Estimated Time**: 10-14 hours  
**Dependencies**: Phase 7 Complete

---

## Table of Contents

1. [Overview](#overview)
2. [Goals](#goals)
3. [Prerequisites](#prerequisites)
4. [Step 8.1: Response Time Tracking](#step-81-response-time-tracking)
5. [Step 8.2: Weekly CRT Report](#step-82-weekly-crt-report)
6. [Step 8.3: Data Retention Policy](#step-83-data-retention-policy)
7. [Configuration Summary](#configuration-summary)
8. [Acceptance Criteria](#acceptance-criteria)
9. [Risk Assessment](#risk-assessment)

---

## Overview

Phase 8 focuses on operational metrics and reporting capabilities. These features help CRT leadership understand response effectiveness and ensure data hygiene through automated retention policies.

### Key Deliverables

1. **Response Time Tracking** - Measure alert-to-acknowledgment and alert-to-resolution times
2. **Weekly CRT Report** - Automated summary posted to configurable channel
3. **Data Retention Policy** - Auto-purge old data with configurable TTL

### Why This Order?

| Step | Feature | Rationale |
|------|---------|-----------|
| 8.1 | Response Time Tracking | Foundation for reporting - must collect data first |
| 8.2 | Weekly CRT Report | Depends on 8.1 metrics - provides actionable insights |
| 8.3 | Data Retention | Good hygiene - prevents unbounded storage growth |

---

## Goals

| Goal | Description | Priority |
|------|-------------|----------|
| Operational Visibility | CRT knows how well they're responding | High |
| Continuous Improvement | Data-driven insights for CRT process | High |
| Storage Management | Prevent Redis bloat over time | Medium |
| Privacy Compliance | Don't retain data longer than needed | Medium |

---

## Prerequisites

Before starting Phase 8, ensure:

- [ ] Phase 7 complete (Core Safety & User Preferences)
- [ ] Auto-initiate feature operational
- [ ] Redis operational with authentication
- [ ] All Phase 7 tests passing

---

## Step 8.1: Response Time Tracking

**Goal**: Track and store response time metrics for all crisis alerts.

**Estimated Time**: 3-4 hours

### 8.1.1: Metrics to Track

| Metric | Description | Calculation |
|--------|-------------|-------------|
| `time_to_acknowledge` | Alert posted to Acknowledge clicked | `ack_time - alert_time` |
| `time_to_ash_contact` | Alert posted to Talk to Ash clicked (or auto-initiated) | `ash_time - alert_time` |
| `time_to_first_response` | Alert posted to First human message in thread | `response_time - alert_time` |
| `was_auto_initiated` | Whether Ash auto-initiated | Boolean |
| `severity` | Alert severity level | String |
| `channel_sensitivity` | Channel sensitivity modifier applied | Float |

### 8.1.2: Data Model

```python
@dataclass
class AlertMetrics:
    """Metrics for a single alert."""
    alert_id: str                          # Unique identifier
    alert_message_id: int                  # Discord message ID
    user_id: int                           # User who triggered alert
    channel_id: int                        # Source channel
    severity: str                          # low, medium, high, critical
    channel_sensitivity: float             # Modifier applied
    
    # Timestamps
    alert_created_at: datetime             # When alert was posted
    acknowledged_at: Optional[datetime]    # When acknowledged
    ash_contacted_at: Optional[datetime]   # When Ash initiated
    first_response_at: Optional[datetime]  # When human responded
    resolved_at: Optional[datetime]        # When marked resolved
    
    # Computed (stored for efficiency)
    time_to_acknowledge_seconds: Optional[int]
    time_to_ash_seconds: Optional[int]
    time_to_response_seconds: Optional[int]
    
    # Flags
    was_auto_initiated: bool
    user_opted_out: bool
```

### 8.1.3: Storage Design (Redis)

```python
# Individual alert metrics
key = f"ash:metrics:alert:{alert_id}"
value = {
    "alert_id": "alert_abc123",
    "alert_message_id": 123456789,
    "user_id": 987654321,
    "severity": "high",
    "alert_created_at": "2026-01-05T12:00:00Z",
    "acknowledged_at": "2026-01-05T12:02:30Z",
    "time_to_acknowledge_seconds": 150,
    # ... other fields
}
ttl = 90 * 24 * 60 * 60  # 90 days (configurable)

# Daily aggregates for faster reporting
key = f"ash:metrics:daily:{date}"  # e.g., "ash:metrics:daily:2026-01-05"
value = {
    "date": "2026-01-05",
    "total_alerts": 5,
    "by_severity": {"low": 1, "medium": 2, "high": 2, "critical": 0},
    "avg_acknowledge_seconds": 180,
    "avg_ash_contact_seconds": 45,
    "auto_initiated_count": 1,
    "user_optout_count": 0
}
ttl = 365 * 24 * 60 * 60  # 1 year for aggregates
```

### 8.1.4: Implementation Details

#### New Files

| File | Purpose |
|------|---------|
| `src/managers/metrics/response_metrics_manager.py` | Track and store response metrics |
| `src/managers/metrics/__init__.py` | Package init |
| `tests/test_response_metrics.py` | Unit tests |

#### Modified Files

| File | Changes |
|------|---------|
| `src/managers/alerting/alert_dispatcher.py` | Record alert creation time |
| `src/managers/alerting/button_handlers.py` | Record acknowledge/Ash contact times |
| `src/managers/alerting/auto_initiate_manager.py` | Record auto-initiation |
| `src/config/default.json` | Add metrics settings |
| `.env.template` | Add environment variables |

#### ResponseMetricsManager Design

```python
class ResponseMetricsManager:
    """
    Tracks and stores response time metrics for crisis alerts.
    
    Provides:
    - Individual alert metric recording
    - Daily aggregate computation
    - Query methods for reporting
    """
    
    def __init__(
        self,
        config_manager: ConfigManager,
        redis_manager: RedisManager,
    ):
        self._config = config_manager
        self._redis = redis_manager
        self._retention_days = config_manager.get(
            "metrics", "retention_days", 90
        )
    
    async def record_alert_created(
        self,
        alert_id: str,
        alert_message_id: int,
        user_id: int,
        channel_id: int,
        severity: str,
        channel_sensitivity: float = 1.0,
    ) -> None:
        """Record when an alert is created."""
    
    async def record_acknowledged(
        self,
        alert_id: str,
        acknowledged_by: int,
    ) -> None:
        """Record when alert is acknowledged."""
    
    async def record_ash_contacted(
        self,
        alert_id: str,
        was_auto_initiated: bool = False,
    ) -> None:
        """Record when Ash contact initiated."""
    
    async def record_user_opted_out(
        self,
        alert_id: str,
    ) -> None:
        """Record when user opts out of Ash."""
    
    async def record_first_response(
        self,
        alert_id: str,
        responder_id: int,
    ) -> None:
        """Record first human response."""
    
    async def get_alert_metrics(
        self,
        alert_id: str,
    ) -> Optional[AlertMetrics]:
        """Get metrics for specific alert."""
    
    async def get_daily_aggregate(
        self,
        date: datetime.date,
    ) -> Optional[DailyAggregate]:
        """Get aggregate metrics for a day."""
    
    async def get_weekly_summary(
        self,
        end_date: Optional[datetime.date] = None,
    ) -> WeeklySummary:
        """Get summary for past 7 days."""
```

### 8.1.5: Configuration

**Environment Variables** (`.env.template`):

```bash
# ------------------------------------------------------- #
# RESPONSE METRICS CONFIGURATION
# ------------------------------------------------------- #
BOT_METRICS_ENABLED=true                                  # Enable response time tracking
BOT_METRICS_RETENTION_DAYS=90                             # Days to retain individual metrics (1-365)
BOT_METRICS_AGGREGATE_RETENTION_DAYS=365                  # Days to retain daily aggregates (30-730)
# ------------------------------------------------------- #
```

### 8.1.6: Acceptance Criteria

- [ ] Alert creation time recorded
- [ ] Acknowledgment time recorded
- [ ] Ash contact time recorded (manual and auto)
- [ ] Time deltas calculated correctly
- [ ] Daily aggregates computed
- [ ] TTL applied to stored data
- [ ] Feature can be disabled via config

---

## Step 8.2: Weekly CRT Report

**Goal**: Generate and post automated weekly summary to a configurable channel.

**Estimated Time**: 4-6 hours

### 8.2.1: Report Contents

```
═══════════════════════════════════════════════════════════
📊 Weekly Crisis Response Report
Week of January 1 - January 7, 2026
═══════════════════════════════════════════════════════════

📈 ALERT SUMMARY
────────────────────────────────────────────────────────────
Total Alerts:          12
├─ 🔴 Critical:         0
├─ 🟠 High:             3
├─ 🟡 Medium:           6
└─ 🟢 Low:              3

⏱️ RESPONSE TIMES
────────────────────────────────────────────────────────────
Avg. Time to Acknowledge:    2m 45s
Avg. Time to Ash Contact:    1m 12s
Avg. Time to Human Response: 8m 30s

🤖 ASH ENGAGEMENT
────────────────────────────────────────────────────────────
Ash Sessions Started:         8
├─ Manual (button):          6
├─ Auto-initiated:           2
└─ User Opted Out:           1

Sessions Completed:           7
Avg. Session Duration:       12m 15s

📅 BUSIEST TIMES
────────────────────────────────────────────────────────────
Peak Day:    Wednesday (4 alerts)
Peak Hour:   10 PM - 11 PM (3 alerts)

🏆 CRT RESPONDERS
────────────────────────────────────────────────────────────
1. @CRTMember1 - 5 acknowledgments
2. @CRTMember2 - 4 acknowledgments
3. @CRTMember3 - 3 acknowledgments

═══════════════════════════════════════════════════════════
Generated by Ash-Bot v5.0 | The Alphabet Cartel
═══════════════════════════════════════════════════════════
```

### 8.2.2: Implementation Details

#### New Files

| File | Purpose |
|------|---------|
| `src/managers/reporting/weekly_report_manager.py` | Generate and post weekly reports |
| `src/managers/reporting/__init__.py` | Package init |
| `tests/test_weekly_report.py` | Unit tests |

#### Modified Files

| File | Changes |
|------|---------|
| `src/config/default.json` | Add reporting settings |
| `.env.template` | Add environment variables |
| `main.py` | Schedule weekly report task |

### 8.2.3: Configuration

**Environment Variables** (`.env.template`):

```bash
# ------------------------------------------------------- #
# WEEKLY REPORT CONFIGURATION
# ------------------------------------------------------- #
BOT_WEEKLY_REPORT_ENABLED=true                            # Enable weekly reports
BOT_WEEKLY_REPORT_CHANNEL_ID=                             # Channel ID to post reports
BOT_WEEKLY_REPORT_DAY=monday                              # Day of week: monday-sunday
BOT_WEEKLY_REPORT_HOUR=9                                  # Hour (0-23) in UTC
# ------------------------------------------------------- #
```

### 8.2.4: Acceptance Criteria

- [ ] Report generates correctly from metrics
- [ ] Report posts to configured channel
- [ ] Scheduler runs on configured day/time
- [ ] Empty weeks handled gracefully
- [ ] Top responders shown (without revealing private info)
- [ ] Feature can be disabled via config
- [ ] Missing channel ID prevents startup crash

---

## Step 8.3: Data Retention Policy

**Goal**: Automatically purge old data based on configurable retention periods.

**Estimated Time**: 3-4 hours

### 8.3.1: Data Categories and Retention

| Data Type | Default Retention | Configurable | Notes |
|-----------|-------------------|--------------|-------|
| Alert metrics (individual) | 90 days | Yes | Per-alert response times |
| Daily aggregates | 365 days | Yes | Aggregated daily stats |
| User opt-out preferences | 30 days | Yes | Already has TTL |
| Message history | 7 days | Yes | For context analysis |
| Ash session data | 30 days | Yes | Conversation metadata |

### 8.3.2: Implementation Details

#### New Files

| File | Purpose |
|------|---------|
| `src/managers/storage/data_retention_manager.py` | Manage data retention and cleanup |
| `tests/test_data_retention.py` | Unit tests |

#### Modified Files

| File | Changes |
|------|---------|
| `src/config/default.json` | Add retention settings |
| `.env.template` | Add environment variables |
| `main.py` | Schedule retention cleanup task |

### 8.3.3: Configuration

**Environment Variables** (`.env.template`):

```bash
# ------------------------------------------------------- #
# DATA RETENTION CONFIGURATION
# ------------------------------------------------------- #
BOT_RETENTION_ENABLED=true                                # Enable automated data cleanup
BOT_RETENTION_ALERT_METRICS_DAYS=90                       # Retain individual alert metrics (1-365)
BOT_RETENTION_AGGREGATES_DAYS=365                         # Retain daily aggregates (30-730)
BOT_RETENTION_MESSAGE_HISTORY_DAYS=7                      # Retain message history (1-30)
BOT_RETENTION_SESSION_DATA_DAYS=30                        # Retain session metadata (7-90)
BOT_RETENTION_CLEANUP_HOUR=3                              # Hour (0-23) to run daily cleanup (UTC)
# ------------------------------------------------------- #
```

### 8.3.4: Acceptance Criteria

- [ ] Daily cleanup runs at configured hour
- [ ] Expired data removed correctly
- [ ] TTLs enforced on all relevant keys
- [ ] Storage stats available
- [ ] Cleanup report logged
- [ ] Feature can be disabled via config

---

## Configuration Summary

### Environment Variables Added

```bash
# ======================================================= #
# PHASE 8: METRICS & REPORTING
# ======================================================= #

# ------------------------------------------------------- #
# 8.1 RESPONSE METRICS CONFIGURATION
# ------------------------------------------------------- #
BOT_METRICS_ENABLED=true                                  # Enable response time tracking
BOT_METRICS_RETENTION_DAYS=90                             # Days to retain individual metrics (1-365)
BOT_METRICS_AGGREGATE_RETENTION_DAYS=365                  # Days to retain daily aggregates (30-730)
# ------------------------------------------------------- #

# ------------------------------------------------------- #
# 8.2 WEEKLY REPORT CONFIGURATION
# ------------------------------------------------------- #
BOT_WEEKLY_REPORT_ENABLED=true                            # Enable weekly reports
BOT_WEEKLY_REPORT_CHANNEL_ID=                             # Channel ID to post reports
BOT_WEEKLY_REPORT_DAY=monday                              # Day of week: monday-sunday
BOT_WEEKLY_REPORT_HOUR=9                                  # Hour (0-23) in UTC
# ------------------------------------------------------- #

# ------------------------------------------------------- #
# 8.3 DATA RETENTION CONFIGURATION
# ------------------------------------------------------- #
BOT_RETENTION_ENABLED=true                                # Enable automated data cleanup
BOT_RETENTION_ALERT_METRICS_DAYS=90                       # Retain individual alert metrics (1-365)
BOT_RETENTION_AGGREGATES_DAYS=365                         # Retain daily aggregates (30-730)
BOT_RETENTION_MESSAGE_HISTORY_DAYS=7                      # Retain message history (1-30)
BOT_RETENTION_SESSION_DATA_DAYS=30                        # Retain session metadata (7-90)
BOT_RETENTION_CLEANUP_HOUR=3                              # Hour (0-23) to run daily cleanup (UTC)
# ------------------------------------------------------- #
```

---

## Acceptance Criteria

### Must Have (Critical)

- [ ] Response times tracked for all alerts
- [ ] Weekly report generates and posts
- [ ] Data cleanup runs daily
- [ ] All features configurable via environment

### Should Have (Important)

- [ ] Daily aggregates for efficient reporting
- [ ] Storage stats available
- [ ] Graceful handling of missing data

### Nice to Have (Bonus)

- [ ] Manual report trigger command
- [ ] Storage usage alerts

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Report channel not configured | Medium | Low | Log warning, skip posting |
| Missing metrics for report | Low | Medium | Handle gracefully, show available data |
| Cleanup removes needed data | Low | High | Conservative defaults, logging |
| Scheduler drift | Low | Low | Use absolute times, not intervals |

---

## Timeline Estimate

| Step | Duration | Notes |
|------|----------|-------|
| 8.1: Response Metrics | 3-4 hours | Foundation for reporting |
| 8.2: Weekly Report | 4-6 hours | Report generation + scheduling |
| 8.3: Data Retention | 3-4 hours | Cleanup + stats |
| **Total** | **10-14 hours** | ~2 days |

---

## Notes

*(Space for implementation notes)*

---

**Built with care for chosen family** 🏳️‍🌈
