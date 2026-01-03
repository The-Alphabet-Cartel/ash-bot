# Ash-NLP API Reference

**FILE VERSION**: v5.0.7  
**LAST UPDATED**: 2026-01-02  
**Base URL**: `http://localhost:30880` (or `http://10.20.30.253:30880` on Lofn)  
**Repository**: https://github.com/the-alphabet-cartel/ash-nlp  
**Community**: [The Alphabet Cartel](https://discord.gg/alphabetcartel) | [alphabetcartel.org](https://alphabetcartel.org)

---

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Endpoints](#endpoints)
   - [Analysis Endpoints](#analysis-endpoints)
   - [Configuration Endpoints](#configuration-endpoints)
   - [Health & Status Endpoints](#health--status-endpoints)
   - [Model Endpoints](#model-endpoints)
4. [Request Schemas](#request-schemas)
5. [Response Schemas](#response-schemas)
   - [Top-Level Fields](#top-level-fields)
   - [Model Signals](#model-signals)
   - [Explanation](#explanation)
   - [Consensus](#consensus)
   - [Conflict Analysis](#conflict-analysis)
   - [Context Analysis](#context-analysis-phase-5)
6. [Enumerations](#enumerations)
7. [Error Handling](#error-handling)
8. [Rate Limiting](#rate-limiting)
9. [Examples](#examples)
10. [Integration Notes](#integration-notes)

---

## Overview

Ash-NLP is a crisis detection API that uses a multi-model ensemble to identify crisis signals in text messages. The API is designed for integration with Discord bots and other community moderation tools.

### Architecture

```
Message → [BART 0.50] ─────────────┐
        → [Sentiment 0.25] ────────┼→ Weighted Decision Engine → Crisis Assessment
        → [Irony 0.15] ────────────┤
        → [Emotions 0.10] ─────────┘
```

### Model Weights

| Model | Weight | Purpose |
|-------|--------|---------|
| **BART Zero-Shot** | 0.50 | Primary semantic crisis detection |
| **Cardiff Sentiment** | 0.25 | Emotional tone analysis |
| **Cardiff Irony** | 0.15 | Sarcasm/irony detection |
| **RoBERTa Emotions** | 0.10 | Fine-grained emotion classification |

### Crisis Severity Levels

| Level | Score Range | Recommended Action |
|-------|-------------|-------------------|
| 🔴 `critical` | ≥ 0.85 | Immediate intervention |
| 🟠 `high` | ≥ 0.70 | Priority response |
| 🟡 `medium` | ≥ 0.50 | Standard monitoring |
| 🟢 `low` | ≥ 0.30 | Passive monitoring |
| ⚪ `safe` | < 0.30 | No action needed |

### Interactive Documentation

- **Swagger UI**: http://localhost:30880/docs
- **ReDoc**: http://localhost:30880/redoc
- **OpenAPI Schema**: http://localhost:30880/openapi.json

---

## Quick Start

### Basic Analysis

```bash
curl -X POST http://localhost:30880/analyze \
  -H "Content-Type: application/json" \
  -d '{"message": "I am feeling overwhelmed and anxious"}'
```

### Health Check

```bash
curl http://localhost:30880/health
```

### Response Overview

```json
{
  "crisis_detected": true,
  "severity": "high",
  "crisis_score": 0.78,
  "confidence": 0.87,
  "requires_intervention": true,
  "recommended_action": "priority_response"
}
```

---

## Endpoints

### Analysis Endpoints

#### POST /analyze

Analyze a single message for crisis signals.

**Request:**

```json
{
  "message": "string (required, 1-10000 chars)",
  "user_id": "string (optional)",
  "channel_id": "string (optional)",
  "metadata": "object (optional)",
  "include_explanation": "boolean (default: true)",
  "verbosity": "minimal | standard | detailed (optional)",
  "consensus_algorithm": "weighted_voting | majority_voting | unanimous | conflict_aware (optional)",
  "message_history": "array (optional, Phase 5)",
  "user_timezone": "string (optional, e.g., 'America/New_York')"
}
```

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `message` | string | ✅ Yes | - | Text to analyze (1-10,000 chars) |
| `user_id` | string | No | null | Optional user identifier |
| `channel_id` | string | No | null | Optional channel identifier |
| `metadata` | object | No | null | Optional additional context |
| `include_explanation` | boolean | No | true | Include human-readable explanation |
| `verbosity` | string | No | standard | Explanation detail level |
| `consensus_algorithm` | string | No | weighted_voting | Override consensus algorithm |
| `message_history` | array | No | null | Previous messages for context analysis |
| `user_timezone` | string | No | UTC | User timezone for temporal analysis |

**Message History Item:**

```json
{
  "message": "string (required)",
  "timestamp": "ISO-8601 string (required)",
  "crisis_score": "float (optional, 0.0-1.0)",
  "message_id": "string (optional)"
}
```

**Response (200 OK):**

See [Response Schemas](#response-schemas) for complete field documentation.

```json
{
  "crisis_detected": true,
  "severity": "high",
  "confidence": 0.87,
  "crisis_score": 0.78,
  "requires_intervention": true,
  "recommended_action": "priority_response",
  "signals": {...},
  "explanation": {...},
  "consensus": {...},
  "conflict_analysis": {...},
  "context_analysis": {...},
  "processing_time_ms": 145.32,
  "models_used": ["bart", "sentiment", "irony", "emotions"],
  "is_degraded": false,
  "request_id": "req_abc123",
  "timestamp": "2026-01-02T12:00:00Z"
}
```

---

#### POST /analyze/batch

Analyze multiple messages in a single request.

**Request:**

```json
{
  "messages": ["string", "string", ...],
  "include_details": false,
  "include_explanation": false
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `messages` | array | ✅ Yes | List of messages (1-100) |
| `include_details` | boolean | No | Include detailed signals (default: false) |
| `include_explanation` | boolean | No | Include explanations (default: false) |

**Response (200 OK):**

```json
{
  "total_messages": 3,
  "crisis_count": 1,
  "critical_count": 0,
  "high_count": 1,
  "results": [
    {
      "index": 0,
      "message_preview": "I'm having a great day!",
      "crisis_detected": false,
      "severity": "safe",
      "crisis_score": 0.12,
      "requires_intervention": false,
      "explanation_summary": "No crisis indicators detected"
    }
  ],
  "processing_time_ms": 425.67,
  "request_id": "req_batch_123",
  "timestamp": "2026-01-02T12:00:00Z"
}
```

---

### Configuration Endpoints

#### GET /config/consensus

Get current consensus algorithm configuration.

**Response (200 OK):**

```json
{
  "default_algorithm": "weighted_voting",
  "available_algorithms": [
    "weighted_voting",
    "majority_voting",
    "unanimous",
    "conflict_aware"
  ],
  "weights": {
    "bart": 0.50,
    "sentiment": 0.25,
    "irony": 0.15,
    "emotions": 0.10
  },
  "thresholds": {
    "crisis": 0.5,
    "majority": 0.5,
    "unanimous": 0.6,
    "disagreement": 0.15
  },
  "conflict_detection_enabled": true,
  "resolution_strategy": "conservative",
  "explainability_verbosity": "standard"
}
```

---

#### PUT /config/consensus

Update consensus algorithm configuration. Changes take effect immediately.

**Request:**

```json
{
  "default_algorithm": "conflict_aware",
  "resolution_strategy": "review_flag",
  "explainability_verbosity": "detailed",
  "thresholds": {
    "crisis": 0.45,
    "disagreement": 0.20
  }
}
```

**Response (200 OK):** Returns updated configuration.

---

#### GET /config/context

Get context analysis configuration.

**Response (200 OK):**

```json
{
  "enabled": true,
  "escalation": {
    "rapid_threshold_hours": 4,
    "gradual_threshold_hours": 24,
    "score_increase_threshold": 0.3
  },
  "temporal": {
    "late_night_start": 22,
    "late_night_end": 4,
    "late_night_modifier": 1.2,
    "weekend_modifier": 1.1,
    "rapid_posting_threshold": 5,
    "rapid_posting_window_minutes": 30
  },
  "severity_thresholds": {
    "critical": {"threshold": 0.15, "window_hours": 1},
    "high": {"threshold": 0.20, "window_hours": 2},
    "medium": {"threshold": 0.25, "window_hours": 4},
    "low": {"threshold": 0.30, "window_hours": 8}
  }
}
```

---

#### PUT /config/context

Update context analysis configuration.

---

### Health & Status Endpoints

#### GET /health

Simple health check for load balancers.

**Response (200 OK):**

```json
{
  "status": "healthy",
  "ready": true,
  "degraded": false,
  "models_loaded": 4,
  "total_models": 4,
  "uptime_seconds": 3600.5,
  "version": "v5.0.7",
  "timestamp": "2026-01-02T12:00:00Z"
}
```

**Response (503 Service Unavailable):**

```json
{
  "status": "unhealthy",
  "ready": false,
  "degraded": false,
  "models_loaded": 0,
  "total_models": 4
}
```

| Status | HTTP Code | Description |
|--------|-----------|-------------|
| `healthy` | 200 | All systems operational |
| `degraded` | 200 | Some models unavailable |
| `unhealthy` | 503 | Service not ready |

---

#### GET /healthz

Kubernetes-style health check (alias for /health).

---

#### GET /ready

Readiness probe for Kubernetes.

**Response (200 OK):**

```json
{
  "ready": true,
  "message": "Service is ready"
}
```

---

#### GET /status

Detailed service status including all components.

**Response (200 OK):**

```json
{
  "service": "ash-nlp",
  "version": "v5.0.7",
  "environment": "production",
  "status": "healthy",
  "ready": true,
  "degraded": false,
  "degradation_reason": null,
  "models": [
    {
      "name": "bart",
      "loaded": true,
      "enabled": true,
      "device": "cuda:0",
      "weight": 0.50,
      "average_latency_ms": 45.2
    }
  ],
  "stats": {
    "total_requests": 1523,
    "crisis_detections": 47,
    "conflicts_detected": 12,
    "cache_hits": 350,
    "cache_hit_rate": 0.23,
    "average_latency_ms": 125.4
  },
  "config": {
    "weights": {"bart": 0.50, "sentiment": 0.25, "irony": 0.15, "emotions": 0.10},
    "thresholds": {"critical": 0.85, "high": 0.70, "medium": 0.50, "low": 0.30},
    "async_inference": true
  },
  "phase4": {
    "enabled": true,
    "consensus_algorithm": "weighted_voting",
    "resolution_strategy": "conservative",
    "explainability_verbosity": "standard"
  },
  "phase5": {
    "enabled": true,
    "context_analysis": true,
    "escalation_detection": true,
    "temporal_analysis": true
  },
  "timestamp": "2026-01-02T12:00:00Z"
}
```

---

### Model Endpoints

#### GET /models

List all ensemble models.

**Response (200 OK):**

```json
[
  {
    "name": "bart",
    "loaded": true,
    "enabled": true,
    "device": "cuda:0",
    "weight": 0.50,
    "average_latency_ms": 45.2
  },
  {
    "name": "sentiment",
    "loaded": true,
    "enabled": true,
    "device": "cuda:0",
    "weight": 0.25,
    "average_latency_ms": 12.5
  }
]
```

---

#### GET /models/{model_name}

Get details for a specific model.

**Response (200 OK):**

```json
{
  "name": "bart",
  "loaded": true,
  "enabled": true,
  "device": "cuda:0",
  "weight": 0.50,
  "average_latency_ms": 45.2
}
```

**Response (404 Not Found):**

```json
{
  "detail": "Model 'invalid_model' not found"
}
```

---

## Request Schemas

### AnalyzeRequest

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `message` | string | Yes | - | Message to analyze (1-10000 chars) |
| `user_id` | string | No | null | User identifier for tracking |
| `channel_id` | string | No | null | Channel identifier |
| `metadata` | object | No | null | Additional context |
| `include_explanation` | boolean | No | true | Include explanation in response |
| `verbosity` | string | No | standard | Explanation verbosity level |
| `consensus_algorithm` | string | No | null | Override default consensus algorithm |
| `message_history` | array | No | null | Previous messages for context (max 20) |
| `user_timezone` | string | No | UTC | User timezone (IANA format) |

### MessageHistoryItem

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `message` | string | Yes | Previous message text |
| `timestamp` | string | Yes | ISO-8601 timestamp |
| `crisis_score` | float | No | Pre-computed crisis score (0.0-1.0) |
| `message_id` | string | No | Unique message identifier |

### BatchAnalyzeRequest

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `messages` | array | Yes | List of messages (1-100) |
| `include_details` | boolean | No | Include detailed signals |
| `include_explanation` | boolean | No | Include explanations |

---

## Response Schemas

### Top-Level Fields

| Field | Type | Description |
|-------|------|-------------|
| `crisis_detected` | boolean | Whether a crisis situation was detected |
| `severity` | string | Crisis severity: `critical`, `high`, `medium`, `low`, `safe` |
| `confidence` | float | Model agreement confidence (0.0-1.0) |
| `crisis_score` | float | Final crisis score after conflict resolution (0.0-1.0) |
| `requires_intervention` | boolean | Whether human intervention is recommended |
| `recommended_action` | string | Suggested action (see [Recommended Actions](#recommended-actions)) |
| `processing_time_ms` | float | Total processing time in milliseconds |
| `models_used` | array | List of models that contributed |
| `is_degraded` | boolean | Whether system is in degraded mode |
| `request_id` | string | Unique request identifier |
| `timestamp` | string | ISO-8601 timestamp |

### Recommended Actions

| Action | Severity | Description |
|--------|----------|-------------|
| `immediate_outreach` | CRITICAL | Contact user immediately |
| `priority_response` | HIGH | Respond within minutes |
| `standard_monitoring` | MEDIUM | Add to watch list |
| `passive_monitoring` | LOW | Normal observation |
| `none` | SAFE | No action required |

---

### Model Signals

The `signals` object contains individual results from each model.

```json
"signals": {
  "bart": {
    "label": "emotional distress",
    "score": 0.89,
    "crisis_signal": 0.89
  },
  "sentiment": {
    "label": "negative",
    "score": 0.85,
    "crisis_signal": 0.75
  },
  "irony": {
    "label": "non_irony",
    "score": 0.95,
    "crisis_signal": 0.95
  },
  "emotions": {
    "label": "sadness",
    "score": 0.78,
    "crisis_signal": 0.65
  }
}
```

| Field | Description |
|-------|-------------|
| `label` | The classification label from the model |
| `score` | Raw model confidence score (0.0-1.0) |
| `crisis_signal` | Transformed crisis relevance score (0.0-1.0) |

#### BART Crisis Labels

- `suicide ideation` - Direct or indirect suicidal thoughts
- `emotional distress` - Significant emotional pain
- `self-harm` - References to self-injury
- `hopelessness` - Expressions of despair
- `casual conversation` - Normal communication
- `positive sharing` - Positive expression
- `seeking support` - Asking for help (non-crisis)

---

### Explanation

The `explanation` object provides human-readable interpretation.

```json
"explanation": {
  "verbosity": "standard",
  "decision_summary": "HIGH CONCERN: Crisis indicators detected with 87% confidence.",
  "key_factors": ["emotional distress", "negative sentiment"],
  "recommended_action": {
    "priority": "HIGH",
    "action": "Respond promptly with supportive outreach",
    "escalation": "Monitor for escalation",
    "rationale": "Crisis indicators require attention"
  },
  "plain_text": "DECISION SUMMARY:\n...",
  "confidence_summary": "High confidence (87%) based on 4 models",
  "model_contributions": [...],
  "conflict_summary": null
}
```

#### Verbosity Levels

| Level | Contents |
|-------|----------|
| `minimal` | Decision summary only |
| `standard` | Summary + key factors + recommendation |
| `detailed` | Full breakdown including model contributions |

---

### Consensus

The `consensus` object shows how the weighted voting algorithm reached its decision.

```json
"consensus": {
  "algorithm": "weighted_voting",
  "crisis_score": 0.78,
  "confidence": 0.87,
  "agreement_level": "strong_agreement",
  "is_crisis": true,
  "requires_review": false,
  "has_conflict": false,
  "individual_scores": {
    "bart": 0.89,
    "sentiment": 0.75,
    "irony": 0.95,
    "emotions": 0.70
  },
  "vote_breakdown": {
    "total_weight": 1.0,
    "weighted_sum": 0.78
  }
}
```

#### Consensus Formula

```
crisis_score = Σ(signal_i × weight_i) / Σ(weight_i)
```

#### Agreement Levels

| Level | Variance | Description |
|-------|----------|-------------|
| `strong_agreement` | < 0.05 | Models highly aligned |
| `moderate_agreement` | < 0.15 | Models generally aligned |
| `weak_agreement` | < 0.25 | Some disagreement |
| `significant_disagreement` | ≥ 0.25 or conflict detected | Major disagreement |

---

### Conflict Analysis

The `conflict_analysis` object describes model disagreements and resolution.

```json
"conflict_analysis": {
  "has_conflicts": true,
  "conflict_count": 1,
  "conflicts": [
    {
      "type": "score_disagreement",
      "severity": "high",
      "models": ["bart", "sentiment"],
      "description": "Large gap between model scores",
      "values": {"bart": 0.89, "sentiment": 0.45}
    }
  ],
  "highest_severity": "high",
  "requires_review": true,
  "summary": "Model disagreement detected",
  "resolution_strategy": "conservative",
  "original_score": 0.67,
  "resolved_score": 0.89
}
```

#### Conflict Types

| Type | Severity | Description |
|------|----------|-------------|
| `score_disagreement` | HIGH | Large gap between model scores |
| `irony_sentiment_conflict` | MEDIUM | Irony with negative sentiment |
| `emotion_crisis_mismatch` | MEDIUM | High crisis, non-crisis emotions |
| `label_disagreement` | MEDIUM | Conflicting classification labels |

#### Resolution Strategies

| Strategy | Description |
|----------|-------------|
| `conservative` | Use highest crisis score (default, safety-first) |
| `optimistic` | Use lowest crisis score |
| `mean` | Use average of all scores |
| `review_flag` | Use conservative, always flag for review |

---

### Context Analysis (Phase 5)

The `context_analysis` object provides temporal and escalation analysis when message history is provided.

```json
"context_analysis": {
  "escalation_detected": true,
  "escalation_rate": "rapid",
  "escalation_pattern": "spike",
  "pattern_confidence": 0.85,
  "trend": {
    "direction": "escalating",
    "velocity": "rapid",
    "score_delta": 0.35,
    "time_span_hours": 2.5
  },
  "temporal_factors": {
    "late_night_risk": true,
    "rapid_posting": false,
    "time_risk_modifier": 1.2,
    "hour_of_day": 23,
    "is_weekend": false,
    "timezone_used": "America/New_York"
  },
  "trajectory": {
    "start_score": 0.35,
    "end_score": 0.78,
    "peak_score": 0.78,
    "scores": [0.35, 0.45, 0.62, 0.78]
  },
  "intervention": {
    "urgency": "high",
    "recommended_point": "immediate",
    "intervention_delayed": false,
    "reason": "Rapid escalation with late-night activity"
  },
  "history_analyzed": {
    "message_count": 4,
    "time_span_hours": 2.5,
    "oldest_timestamp": "2026-01-02T21:30:00Z",
    "newest_timestamp": "2026-01-02T23:59:00Z"
  }
}
```

#### Escalation Rates

| Rate | Description |
|------|-------------|
| `rapid` | Fast escalation (> 0.3 score increase per hour) |
| `gradual` | Slow escalation (0.1-0.3 per hour) |
| `stable` | No significant change |
| `improving` | Crisis indicators decreasing |
| `none` | No history to analyze |

#### Escalation Patterns

| Pattern | Description |
|---------|-------------|
| `linear` | Steady increase over time |
| `exponential` | Accelerating increase |
| `spike` | Sudden jump in crisis score |
| `plateau` | Elevated but stable |
| `oscillating` | Fluctuating up and down |

#### Trend Directions

| Direction | Description |
|-----------|-------------|
| `escalating` | Crisis indicators increasing |
| `stable` | No significant change |
| `improving` | Crisis indicators decreasing |
| `volatile` | Unpredictable changes |

#### Intervention Urgency

| Urgency | Description |
|---------|-------------|
| `immediate` | Immediate intervention required |
| `high` | Intervention needed soon |
| `standard` | Standard response appropriate |
| `low` | Monitoring sufficient |
| `none` | No intervention needed |

#### Temporal Risk Factors

| Factor | Description |
|--------|-------------|
| `late_night_risk` | Message sent 10 PM - 4 AM (user timezone) |
| `rapid_posting` | 5+ messages in 30 minutes |
| `is_weekend` | Saturday or Sunday |
| `time_risk_modifier` | Score multiplier (1.0 = no change, 1.2 = 20% increase) |

---

## Enumerations

### ConsensusAlgorithm

| Value | Description |
|-------|-------------|
| `weighted_voting` | Weight-based scoring (default) |
| `majority_voting` | Binary majority decision |
| `unanimous` | All models must agree |
| `conflict_aware` | Detect and resolve disagreements |

### ResolutionStrategy

| Value | Description |
|-------|-------------|
| `conservative` | Use highest crisis score (default) |
| `optimistic` | Use lowest crisis score |
| `mean` | Use average score |
| `review_flag` | Flag for human review |

### VerbosityLevel

| Value | Description |
|-------|-------------|
| `minimal` | Crisis level and score only |
| `standard` | Summary + key factors + recommendation |
| `detailed` | Full model breakdown |

### SeverityLevel

| Value | Threshold |
|-------|-----------|
| `critical` | ≥ 0.85 |
| `high` | ≥ 0.70 |
| `medium` | ≥ 0.50 |
| `low` | ≥ 0.30 |
| `safe` | < 0.30 |

### AgreementLevel

| Value | Variance |
|-------|----------|
| `strong_agreement` | < 0.05 |
| `moderate_agreement` | < 0.15 |
| `weak_agreement` | < 0.25 |
| `significant_disagreement` | ≥ 0.25 or conflict detected |

### ConflictSeverity

| Value | Description |
|-------|-------------|
| `high` | Requires immediate attention |
| `medium` | Should be reviewed |
| `low` | Informational |

---

## Error Handling

### Error Response Format

```json
{
  "error": "validation_error",
  "message": "Human-readable error message",
  "details": [
    {
      "code": "value_error",
      "message": "Message cannot be empty",
      "field": "message"
    }
  ],
  "request_id": "req_abc123",
  "timestamp": "2026-01-02T12:00:00Z"
}
```

### HTTP Status Codes

| Code | Description | When |
|------|-------------|------|
| 200 | Success | Request processed successfully |
| 400 | Bad Request | Malformed request body |
| 404 | Not Found | Resource not found |
| 422 | Validation Error | Request validation failed |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Unexpected server error |
| 503 | Service Unavailable | Service not ready |

### Common Errors

**Validation Error (422):**

```json
{
  "error": "validation_error",
  "message": "Request validation failed",
  "details": [
    {
      "code": "value_error",
      "message": "Message cannot be empty or whitespace only",
      "field": "message"
    }
  ]
}
```

**Service Unavailable (503):**

```json
{
  "error": "service_unavailable",
  "message": "Service not initialized"
}
```

---

## Rate Limiting

Default rate limiting is enabled:

| Limit | Value |
|-------|-------|
| Requests per minute | 60 |
| Per client (IP-based) | Yes |
| Burst allowed | No |

### Rate Limit Headers

| Header | Description |
|--------|-------------|
| `X-RateLimit-Limit` | Maximum requests per window |
| `X-RateLimit-Remaining` | Remaining requests |
| `X-RateLimit-Reset` | Window reset timestamp |
| `Retry-After` | Seconds until limit resets (on 429) |

### Rate Limit Response (429)

```json
{
  "error": "rate_limit_exceeded",
  "message": "Rate limit exceeded. Max 60 requests per minute.",
  "request_id": "req_abc123"
}
```

---

## Examples

### cURL

**Basic Analysis:**

```bash
curl -X POST http://localhost:30880/analyze \
  -H "Content-Type: application/json" \
  -d '{"message": "I am feeling overwhelmed and anxious"}'
```

**With Context Analysis:**

```bash
curl -X POST http://localhost:30880/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I dont know what to do anymore",
    "user_id": "user_123",
    "user_timezone": "America/New_York",
    "message_history": [
      {"message": "Having a rough day", "timestamp": "2026-01-02T20:00:00Z"},
      {"message": "Things are getting worse", "timestamp": "2026-01-02T22:00:00Z"}
    ]
  }'
```

**Batch Analysis:**

```bash
curl -X POST http://localhost:30880/analyze/batch \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      "Having a great time!",
      "I feel so alone",
      "Anyone want to play games?"
    ]
  }'
```

**Detailed Status:**

```bash
curl http://localhost:30880/status | jq
```

---

### Python

**Using requests:**

```python
import requests

response = requests.post(
    "http://localhost:30880/analyze",
    json={"message": "I'm struggling today"}
)

result = response.json()
if result["crisis_detected"]:
    print(f"Crisis detected! Severity: {result['severity']}")
    print(f"Recommended action: {result['recommended_action']}")
```

**Using httpx (async):**

```python
import httpx
import asyncio

async def analyze_message(message: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:30880/analyze",
            json={"message": message}
        )
        return response.json()

result = asyncio.run(analyze_message("I need help"))
print(result)
```

**With Context History:**

```python
import requests
from datetime import datetime, timedelta

history = [
    {
        "message": "Having a rough day",
        "timestamp": (datetime.utcnow() - timedelta(hours=2)).isoformat() + "Z"
    },
    {
        "message": "Things are getting worse",
        "timestamp": (datetime.utcnow() - timedelta(hours=1)).isoformat() + "Z"
    }
]

response = requests.post(
    "http://localhost:30880/analyze",
    json={
        "message": "I dont know what to do anymore",
        "message_history": history,
        "user_timezone": "America/New_York"
    }
)

result = response.json()
if result.get("context_analysis", {}).get("escalation_detected"):
    print(f"Escalation detected: {result['context_analysis']['escalation_rate']}")
```

---

### JavaScript

**Using fetch:**

```javascript
async function analyzeMessage(message) {
  const response = await fetch('http://localhost:30880/analyze', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ message }),
  });
  
  return response.json();
}

analyzeMessage("I'm feeling down today")
  .then(result => {
    if (result.crisis_detected) {
      console.log(`Alert: ${result.severity} severity detected`);
      console.log(`Action: ${result.recommended_action}`);
    }
  });
```

---

## Integration Notes

### For Discord Bots

When integrating with a Discord bot:

1. **Check `crisis_detected`** first for quick filtering
2. **Use `severity`** to determine response urgency
3. **Check `requires_intervention`** to decide on alerting moderators
4. **Use `context_analysis`** for users with message history
5. **Include `request_id`** in logs for troubleshooting
6. **Monitor `is_degraded`** for system health alerts

### Recommended Response Flow

```
if crisis_detected:
    if severity == "critical":
        → Immediate moderator alert
        → DM user with crisis resources
        → Log with high priority
    elif severity == "high":
        → Priority moderator queue
        → Monitor user activity
        → Check escalation patterns
    elif severity == "medium":
        → Standard monitoring
        → Log for review
    else:
        → Passive monitoring
else:
    → No action needed
```

### Request Headers

| Header | Value | Description |
|--------|-------|-------------|
| `Content-Type` | `application/json` | Required for POST |
| `Accept` | `application/json` | Optional |
| `X-Request-ID` | `string` | Optional custom request ID |

### Response Headers

| Header | Description |
|--------|-------------|
| `X-Request-ID` | Unique request identifier |
| `Content-Type` | Response content type |

---

## Support

- **Discord**: [discord.gg/alphabetcartel](https://discord.gg/alphabetcartel)
- **GitHub Issues**: [github.com/the-alphabet-cartel/ash-nlp/issues](https://github.com/the-alphabet-cartel/ash-nlp/issues)
- **Website**: [alphabetcartel.org](https://alphabetcartel.org)

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| v5.0.7 | 2026-01-02 | Final bug fixes, consolidated documentation |
| v5.0.6 | 2026-01-02 | Phase 6 enhancements, timezone support |
| v5.0.5 | 2026-01-02 | Phase 5 context analysis |
| v5.0.4 | 2026-01-01 | Phase 4 consensus & explainability |
| v5.0.0 | 2026-01-01 | Multi-model ensemble architecture |

---

**Built with care for chosen family** 🏳️‍🌈
