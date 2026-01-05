# Phase 7: Future Enhancements and Fixes

**Version**: v5.0  
**Created**: 2026-01-05  
**Status**: Planning  
**Repository**: https://github.com/the-alphabet-cartel/ash-bot  
**Community**: [The Alphabet Cartel](https://discord.gg/alphabetcartel) | [alphabetcartel.org](https://alphabetcartel.org)

---

## Overview

Phase 7 contains planned enhancements, improvements, and fixes identified during development and production use of Ash-Bot v5.0. These items are not critical for initial deployment but will improve the system's effectiveness and user experience.

---

## Planned Enhancements

### 7.1 Auto-Initiate Contact on Unacknowledged Alerts

**Priority**: High  
**Complexity**: Medium  
**Status**: Planned

#### Problem Statement

Currently, when Ash-Bot detects a crisis of MEDIUM severity or higher, it:
1. Sends an alert to the appropriate crisis channel
2. Pings the Crisis Response Team (CRT)
3. Displays "Acknowledge" and "Talk to Ash" buttons
4. **Waits indefinitely** for staff to click "Talk to Ash" before initiating contact with the user

**Issue**: If no staff member is available to acknowledge or initiate contact, the user in crisis receives no support. This creates a gap in our crisis response coverage, particularly during off-hours or when staff are unavailable.

#### Proposed Solution

Implement an **auto-initiation timer** that automatically triggers Ash to reach out to the user if staff has not acknowledged the alert within a configurable time period.

#### Behavior Flow

```
Crisis Detected (MEDIUM+)
    │
    ▼
Alert Posted to Crisis Channel
    │
    ▼
Timer Starts (X minutes countdown)
    │
    ├─── Staff clicks "Acknowledge" ───► Timer cancelled, manual flow continues
    │
    ├─── Staff clicks "Talk to Ash" ───► Timer cancelled, Ash initiates contact
    │
    └─── Timer expires (X minutes) ───► Ash auto-initiates contact with user
                                         │
                                         ▼
                                   Update alert embed to show:
                                   "⏰ Auto-initiated (no staff response)"
```

#### Configuration

New configuration options to add to `src/config/default.json`:

```json
"alerting": {
    "auto_initiate_enabled": "${BOT_ALERT_AUTO_INITIATE}",
    "auto_initiate_delay_minutes": "${BOT_ALERT_AUTO_INITIATE_DELAY}",
    "auto_initiate_min_severity": "${BOT_ALERT_AUTO_INITIATE_MIN_SEVERITY}",
    "defaults": {
        "auto_initiate_enabled": true,
        "auto_initiate_delay_minutes": 3,
        "auto_initiate_min_severity": "medium"
    }
}
```

| Setting | Default | Description |
|---------|---------|-------------|
| `auto_initiate_enabled` | `true` | Enable/disable auto-initiation feature |
| `auto_initiate_delay_minutes` | `3` | Minutes to wait before auto-initiating |
| `auto_initiate_min_severity` | `medium` | Minimum severity for auto-initiation |

#### Implementation Approach

1. **AlertDispatcher Enhancement**
   - Track pending alerts with timestamps
   - Store message ID, user ID, channel ID, and alert time
   
2. **Auto-Initiate Timer Task**
   - Background task that checks pending alerts every 30 seconds
   - For alerts exceeding the delay threshold without acknowledgment:
     - Trigger Ash to initiate contact
     - Update the alert embed to show auto-initiation
     - Log the auto-initiation event
   
3. **Embed Updates**
   - Add visual indicator when auto-initiated
   - Show time elapsed before auto-initiation
   - Disable "Talk to Ash" button (replace with "Auto-Initiated")

4. **Metrics Tracking**
   - Count of auto-initiated contacts
   - Average time to staff acknowledgment
   - Percentage of alerts auto-initiated vs manually handled

#### Files to Modify

- `src/managers/alerting/alert_dispatcher.py` - Add pending alert tracking
- `src/managers/alerting/auto_initiate_manager.py` - New manager for timer logic
- `src/managers/discord/discord_manager.py` - Handle auto-initiation trigger
- `src/managers/alerting/embed_builder.py` - Add auto-initiated visual state
- `src/config/default.json` - Add configuration options
- `.env.template` - Add environment variable documentation
- `tests/test_auto_initiate.py` - Unit tests for new functionality

#### Acceptance Criteria

- [ ] Auto-initiation triggers after configurable delay (default 3 minutes)
- [ ] Staff acknowledgment cancels the auto-initiation timer
- [ ] Alert embed updates to show auto-initiation occurred
- [ ] Feature can be enabled/disabled via configuration
- [ ] Delay is configurable via environment variable
- [ ] Minimum severity for auto-initiation is configurable
- [ ] Metrics track auto-initiation events
- [ ] Unit tests achieve 90%+ coverage for new code

---

## Future Ideas (Not Yet Planned)

Items collected for potential future implementation. These require further discussion before planning.

### Potential Enhancements

1. **Escalation Tiers**
   - If initial Ash contact doesn't receive response, escalate to different CRT members
   - Tiered escalation based on time without response

2. **Shift Scheduling Integration**
   - Aware of CRT member schedules
   - Route alerts to on-duty members first
   - Adjust auto-initiate timing based on coverage

3. **Multi-Language Support**
   - Ash personality responses in multiple languages
   - Language detection from user messages

4. **Analytics Dashboard**
   - Web dashboard for crisis response metrics
   - Historical trends and patterns
   - Staff response time tracking

5. **Integration with External Crisis Resources**
   - Automated resource links based on crisis type
   - Integration with crisis hotline information

---

## Bug Fixes (Deferred)

Known issues that are not blocking but should be addressed.

*None identified yet.*

---

## Technical Debt

Items that should be refactored or improved for maintainability.

*None identified yet.*

---

## Notes

- Phase 7 items will be prioritized after Phase 6 (Deployment Verification) is complete
- High-priority items may be pulled into earlier phases if needed
- All implementations must follow Clean Architecture Charter guidelines

---

**Built with care for chosen family** 🏳️‍🌈
