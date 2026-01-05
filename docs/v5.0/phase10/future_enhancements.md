# Phase 10+: Future Enhancements & Improvements

============================================================================
**Ash-Bot**: Crisis Detection Discord Bot for The Alphabet Cartel  
**The Alphabet Cartel** - https://discord.gg/alphabetcartel | alphabetcartel.org
============================================================================

**Document Version**: v1.1.0  
**Created**: 2026-01-05  
**Phase**: 10+ (Future Planning)  
**Status**: 📋 Backlog  
**Last Updated**: 2026-01-05

---

## Table of Contents

1. [Overview](#overview)
2. [Deferred Features](#deferred-features)
3. [Technical Improvements](#technical-improvements)
4. [Integration Opportunities](#integration-opportunities)
5. [Maybe Later](#maybe-later)
6. [Ruled Out (With Rationale)](#ruled-out-with-rationale)
7. [Ash Ecosystem Integration](#ash-ecosystem-integration)
8. [Community Requests](#community-requests)
9. [Technical Debt](#technical-debt)
10. [Research & Exploration](#research--exploration)

---

## Overview

This document tracks future enhancement ideas, deferred features, and potential improvements for Ash-Bot beyond Phase 9. Items here are not currently scheduled but represent the product backlog for future consideration.

### Priority Legend

| Priority | Description |
|----------|-------------|
| 🔴 High | Significant user value, should be scheduled soon |
| 🟡 Medium | Good to have, schedule when capacity allows |
| 🟢 Low | Nice to have, opportunistic implementation |
| ⚪ Someday | Long-term vision, no immediate plans |

### Complexity Legend

| Complexity | Description |
|------------|-------------|
| 🟦 Low | < 4 hours, minimal dependencies |
| 🟨 Medium | 4-8 hours, some dependencies |
| 🟧 High | 8-16 hours, significant work |
| 🟥 Very High | 16+ hours, major feature |

---

## Deferred Features

Features discussed and approved but deferred for later implementation.

### 10.1: Repeat Crisis Detection
**Priority**: 🔴 High  
**Complexity**: 🟨 Medium  
**Deferred From**: Phase 7 discussion  
**Estimated Time**: 4-6 hours

**Description**: Track when users have multiple crisis alerts in a short period and escalate accordingly.

**Behavior**:
- 2nd alert in 7 days → Note in embed: "⚠️ 2nd alert this week"
- 3rd+ alert in 7 days → Elevated priority, different embed color
- Pattern tracking for CRT awareness

**Why Deferred**: Current community size allows CRT to manually track repeat users. Implement when community grows or CRT requests it.

**Implementation Notes**:
```python
# Redis storage
key = f"ash:user:alerts:{user_id}"
value = [
    {"alert_id": "...", "timestamp": "...", "severity": "..."},
    ...
]
ttl = 7 * 24 * 60 * 60  # 7 days rolling window
```

---

### 10.2: Alert Severity Override
**Priority**: 🟡 Medium  
**Complexity**: 🟦 Low  
**Estimated Time**: 2-3 hours

**Description**: Allow CRT to manually adjust alert severity after review.

**Use Case**: NLP flags as HIGH but CRT determines it's actually LOW (false positive), or vice versa.

**Implementation**:
- Add "Adjust Severity" dropdown to alert embed
- Log adjustment with reason
- Update metrics to track overrides
- Feed back into future NLP tuning

---

### 10.3: CRT Availability Status
**Priority**: 🟡 Medium  
**Complexity**: 🟨 Medium  
**Estimated Time**: 5-7 hours

**Description**: Allow CRT members to set availability status.

**Features**:
- `/ash available` - Mark self as available
- `/ash away [reason]` - Mark self as away
- Show available CRT count in alerts
- Adjust auto-initiate based on CRT availability

**Benefit**: If no CRT available, auto-initiate faster. If many available, allow more time for manual response.

---

### 10.4: Alert Escalation Chain
**Priority**: 🟢 Low  
**Complexity**: 🟧 High  
**Estimated Time**: 8-12 hours

**Description**: Implement escalation chain for unacknowledged alerts.

**Flow**:
1. Alert posted → Wait 3 min
2. No response → Ping CRT role again
3. Still no response (5 min) → Auto-initiate + ping Admins
4. Still no response (10 min) → Log critical incident

**Configuration**:
```bash
BOT_ESCALATION_ENABLED=true
BOT_ESCALATION_STEP1_MINUTES=3
BOT_ESCALATION_STEP2_MINUTES=5
BOT_ESCALATION_STEP3_MINUTES=10
BOT_ESCALATION_ADMIN_ROLE=Admin
```

---

## Technical Improvements

Enhancements to existing functionality.

### 10.5: Graceful Shutdown Enhancement
**Priority**: 🟡 Medium  
**Complexity**: 🟦 Low  
**Estimated Time**: 2-3 hours

**Description**: Ensure clean shutdown preserves all pending state.

**Current Gap**: Auto-initiate timers may be lost on restart.

**Solution**:
- Persist pending alerts to Redis
- Restore pending alerts on startup
- Resume timers with adjusted remaining time

---

### 10.6: Health Check Dashboard Endpoint
**Priority**: 🟢 Low  
**Complexity**: 🟦 Low  
**Estimated Time**: 2-3 hours

**Description**: Add endpoint returning HTML dashboard for quick status view.

**Endpoint**: `GET /health/dashboard`

**Returns**: Simple HTML page showing:
- Component status with colors
- Recent alert count
- Active sessions
- Uptime

**Use Case**: Quick browser check without parsing JSON.

---

## Integration Opportunities

Potential integrations with external services.

### 10.7: Discord Audit Log Integration
**Priority**: 🟢 Low  
**Complexity**: 🟨 Medium  
**Estimated Time**: 5-6 hours

**Description**: Log significant bot actions to Discord audit log or dedicated channel.

**Events to Log**:
- Bot startup/shutdown
- Configuration changes
- Alert acknowledgments
- Session starts/ends
- Opt-out changes

---

## Maybe Later

Features we might implement eventually, but not a current priority.

### Prometheus Metrics Enhancement
**Priority**: ⚪ Someday  
**Complexity**: 🟨 Medium  
**Estimated Time**: 4-6 hours

**Description**: Expand Prometheus metrics for better observability.

**New Metrics**:
- `ash_session_duration_seconds` (histogram)
- `ash_nlp_request_duration_seconds` (histogram)
- `ash_alert_severity_total` (counter by severity)
- `ash_user_optout_total` (counter)
- `ash_followup_sent_total` (counter)
- `ash_followup_response_rate` (gauge)

**Status**: Would be nice for advanced monitoring, but current `/metrics` endpoint is sufficient for now.

---

### Grafana Dashboard Template
**Priority**: ⚪ Someday  
**Complexity**: 🟦 Low  
**Estimated Time**: 3-4 hours

**Description**: Create pre-built Grafana dashboard JSON for Ash-Bot metrics.

**Panels**:
- Alert volume over time
- Response time percentiles
- NLP API latency
- Session counts
- Error rates

**Deliverable**: `docs/monitoring/grafana-dashboard.json`

**Status**: Depends on Prometheus Metrics Enhancement. Consider when/if we set up proper monitoring infrastructure.

---

## Ruled Out (With Rationale)

Features considered but intentionally not planned.

### ❌ SMS Gateway Integration
**Reason**: Cost, privacy concerns, complexity. Discord mobile notifications serve the same purpose. CRT members should have Discord notifications enabled.

**Reconsidered If**: Community explicitly requests and is willing to manage phone number collection securely.

---

### ❌ Multi-Language Support
**Reason**: The Alphabet Cartel is an English-only server with no plans to change. Would require significant NLP model changes.

**Reconsidered If**: Community becomes multilingual or bot is open-sourced for other communities.

---

### ❌ Email Notifications
**Reason**: Similar to SMS - adds complexity, requires email collection, Discord notifications are sufficient.

**Reconsidered If**: CRT requests backup notification channel.

---

### ❌ Public Bot Distribution
**Reason**: Bot is purpose-built for The Alphabet Cartel. Would require significant generalization, security hardening, and support infrastructure.

**Reconsidered If**: Other LGBTQIA+ communities express strong interest and resources are available.

---

### ❌ Voice Channel Monitoring
**Reason**: Privacy concerns, technical complexity, limited crisis detection value from audio.

**Reconsidered If**: Voice-to-text technology matures significantly and community consents.

---

### ❌ Quiet Hours Configuration
**Reason**: Adds complexity for limited benefit. Auto-initiate already handles unresponsive periods. CRT can manage their own notification settings.

---

### ❌ NLP Response Caching
**Reason**: Adds complexity, edge cases around message editing. NLP API is fast enough. Redis storage for cache adds overhead without significant benefit.

---

### ❌ Structured Logging Enhancement
**Reason**: Current logging is sufficient for debugging. Would add complexity without immediate operational benefit.

---

### ❌ Circuit Breaker Tuning
**Reason**: Current hardcoded values work well. Making them configurable adds complexity without clear use case for changing them.

---

## Ash Ecosystem Integration

Features that integrate with other Ash projects.

### 10.8: Ash-Dash Integration
**Priority**: 🔴 High  
**Complexity**: 🟥 Very High  
**Estimated Time**: Part of Ash-Dash project

**Description**: Full web dashboard for Ash-Bot.

**Features** (handled by Ash-Dash):
- Real-time alert feed
- User history lookup
- Session management
- Analytics and trends
- Configuration management
- CRT scheduling

**Ash-Bot Changes**:
- WebSocket endpoint for real-time updates
- REST API for dashboard queries
- Authentication token support

**Status**: Planned for Ash-Dash v5.0 recode.

---

### 10.9: Ash-NLP Feedback Loop
**Priority**: 🟡 Medium  
**Complexity**: 🟧 High  
**Estimated Time**: 8-10 hours (both sides)

**Description**: Send CRT severity overrides back to NLP for model improvement.

**Flow**:
1. CRT adjusts severity (10.2)
2. Ash-Bot sends feedback to Ash-NLP
3. Ash-NLP logs for future training data
4. Periodic model retraining improves accuracy

---

### 10.10: Shared User Profile Service
**Priority**: 🟢 Low  
**Complexity**: 🟥 Very High  
**Estimated Time**: New service

**Description**: Centralized user preference/profile service for Ash ecosystem.

**Benefits**:
- Single opt-out across all Ash services
- Shared user history
- Consistent preferences

**Status**: Long-term vision, requires new microservice.

---

## Community Requests

Space for tracking community-requested features.

### Template for New Requests

```markdown
### CR-XXX: [Feature Name]
**Requested By**: [Discord username or "Multiple users"]
**Date**: YYYY-MM-DD
**Priority**: 🔴/🟡/🟢/⚪
**Complexity**: 🟦/🟨/🟧/🟥

**Description**: [What the community wants]

**Use Case**: [Why they want it]

**Notes**: [Implementation thoughts, concerns]
```

---

### CR-001: [Placeholder for first community request]
**Requested By**: -  
**Date**: -  
**Priority**: -  
**Complexity**: -

**Description**: *No community requests logged yet.*

---

## Technical Debt

Known issues and code improvements needed.

### TD-001: Test Coverage Gaps
**Priority**: 🟡 Medium  
**Complexity**: 🟨 Medium

**Description**: Some edge cases lack test coverage.

**Areas to Improve**:
- Redis connection failure scenarios
- Discord rate limiting handling
- NLP API timeout edge cases
- Concurrent session handling

---

### TD-002: Configuration Validation Centralization
**Priority**: 🟢 Low  
**Complexity**: 🟦 Low

**Description**: Some validation happens in managers rather than ConfigManager.

**Solution**: Move all validation to ConfigManager with schema-based approach.

---

### TD-003: Error Message Consistency
**Priority**: 🟢 Low  
**Complexity**: 🟦 Low

**Description**: Error messages and logging formats vary slightly across managers.

**Solution**: Create error message constants/templates for consistency.

---

### TD-004: Type Hints Completion
**Priority**: 🟢 Low  
**Complexity**: 🟦 Low

**Description**: Some functions missing complete type hints.

**Solution**: Add comprehensive type hints and run mypy validation.

---

## Research & Exploration

Ideas requiring research before planning.

### RE-001: Sentiment Trend Analysis
**Status**: 🔬 Research Needed

**Question**: Can we detect users trending toward crisis before they reach alert threshold?

**Approach**:
- Track per-user sentiment over time
- Identify downward trends
- Proactive gentle check-in (not crisis response)

**Concerns**: Privacy, false positives, user consent.

---

### RE-002: Community Health Metrics
**Status**: 🔬 Research Needed

**Question**: Can we provide aggregate community health metrics without individual tracking?

**Possible Metrics**:
- Overall sentiment trends (anonymized)
- Peak stress times
- Community mood indicators

**Concerns**: Privacy, potential misuse, actionability.

---

### RE-003: Peer Support Matching
**Status**: 🔬 Research Needed

**Question**: Can we facilitate peer support connections for non-crisis situations?

**Concept**:
- User opts into peer support
- Bot connects users with similar experiences
- Moderated introduction

**Concerns**: Safety, liability, complexity.

---

### RE-004: Crisis Prevention Resources
**Status**: 🔬 Research Needed

**Question**: Can Ash proactively share mental health resources based on detected themes?

**Concept**:
- Detect themes (anxiety, depression, relationship issues)
- Share relevant resources (not triggered by crisis)
- Educational, not clinical

**Concerns**: Coming across as preachy, accuracy of theme detection.

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| v1.1.0 | 2026-01-05 | Removed 10.3, 10.6, 10.9, 10.10; moved Prometheus/Grafana to Maybe Later; renumbered |
| v1.0.0 | 2026-01-05 | Initial document creation |

---

## Notes

*(Space for additional notes and ideas)*

---

**Built with care for chosen family** 🏳️‍🌈
