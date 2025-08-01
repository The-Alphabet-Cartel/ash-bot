# Ash Bot v3.0 API Documentation

**Complete API reference for the intelligent Discord crisis response system**

---

## 🚀 API Overview

Ash Bot v3.0 provides a RESTful API for crisis detection monitoring, system health checks, and integration with external systems. The API is designed for:

- **System health monitoring** and performance metrics
- **Crisis response analytics** and reporting
- **Integration testing** and development support
- **Administrative management** and configuration

**Base URL**: `http://localhost:8882` (default)  
**Content-Type**: `application/json`  
**Authentication**: Optional (configurable via environment)

---

## 📊 Quick Reference

| Endpoint | Method | Purpose | Response Time |
|----------|--------|---------|---------------|
| `/health` | GET | System health check | ~5ms |
| `/stats` | GET | Service statistics | ~10ms |
| `/crisis_metrics` | GET | Crisis response analytics | ~15ms |
| `/conversation_stats` | GET | Conversation system metrics | ~8ms |
| `/api/analyze` | POST | Message analysis pipeline | ~350ms |
| `/api/test_keywords` | POST | Keyword detection testing | ~50ms |

---

## 🏥 Health & Status Endpoints

### GET `/health`

**Purpose**: Check system health and service status

**Response**:
```json
{
  "status": "healthy",
  "bot_connected": true,
  "uptime_seconds": 7842.1234567890,
  "discord_connection": {
    "connected": true,
    "latency_ms": 45.2,
    "guild_count": 12,
    "monitored_channels": 847
  },
  "services": {
    "nlp_service": {
      "status": "connected",
      "url": "http://10.20.30.253:8881",
      "response_time_ms": 28.5,
      "last_check": "2025-08-01T14:32:15Z"
    },
    "keyword_detector": {
      "status": "loaded",
      "total_keywords": 342,
      "custom_keywords": 28,
      "last_updated": "2025-08-01T09:15:30Z"
    },
    "conversation_handler": {
      "status": "active",
      "active_conversations": 3,
      "total_today": 47
    }
  },
  "crisis_system": {
    "enabled": true,
    "escalation_channels_configured": true,
    "staff_notifications_enabled": true,
    "learning_system_active": true
  }
}
```

**Status Codes**:
- `200`: System healthy and operational
- `503`: System unhealthy (critical components down)
- `500`: Internal server error

---

### GET `/stats`

**Purpose**: Comprehensive service statistics and performance metrics

**Response**:
```json
{
  "service": "Ash Bot - Intelligent Crisis Response System",
  "version": "3.0.0",
  "uptime_seconds": 7842.1234567890,
  "performance": {
    "avg_response_time_ms": 320,
    "messages_processed_today": 12847,
    "crisis_detections_today": 23,
    "false_positive_rate": 0.07,
    "accuracy_percentage": 89.3
  },
  "crisis_system": {
    "total_interventions": 1847,
    "interventions_today": 23,
    "by_level": {
      "high_crisis": 4,
      "medium_crisis": 14,
      "low_crisis": 5
    },
    "resolution_rate": 0.85,
    "avg_response_time_seconds": 3.2
  },
  "conversation_system": {
    "conversations_started_today": 47,
    "active_conversations": 3,
    "avg_conversation_duration_minutes": 12.4,
    "engagement_rate": 0.67,
    "successful_resource_connections": 31
  },
  "detection_system": {
    "keyword_matches_today": 156,
    "nlp_analyses_today": 89,
    "context_adjustments_applied": 67,
    "learning_adjustments_today": 8
  },
  "system_resources": {
    "memory_usage_mb": 180,
    "cpu_usage_percent": 12.4,
    "disk_usage_mb": 245
  }
}
```

---

## 🚨 Crisis Analytics Endpoints

### GET `/crisis_metrics`

**Purpose**: Detailed crisis response analytics and performance data

**Parameters**:
- `timeframe` (optional): `day`, `week`, `month`, `year` (default: `day`)
- `include_details` (optional): `true`/`false` (default: `false`)

**Example Request**:
```bash
GET /crisis_metrics?timeframe=week&include_details=true
```

**Response**:
```json
{
  "timeframe": "week",
  "period": {
    "start": "2025-07-25T00:00:00Z",
    "end": "2025-08-01T23:59:59Z"
  },
  "crisis_interventions": {
    "total": 164,
    "by_level": {
      "high_crisis": {
        "count": 28,
        "avg_response_time_seconds": 2.1,
        "resolution_rate": 0.96,
        "escalation_success_rate": 0.98
      },
      "medium_crisis": {
        "count": 89,
        "avg_response_time_seconds": 3.4,
        "resolution_rate": 0.87,
        "conversation_engagement_rate": 0.72
      },
      "low_crisis": {
        "count": 47,
        "avg_response_time_seconds": 4.1,
        "resolution_rate": 0.81,
        "follow_up_rate": 0.34
      }
    }
  },
  "detection_accuracy": {
    "overall_accuracy": 0.893,
    "false_positive_rate": 0.071,
    "false_negative_rate": 0.036,
    "improvement_trend": "+2.3% vs last week"
  },
  "team_performance": {
    "avg_team_response_time_minutes": 4.7,
    "coverage_percentage": 0.94,
    "successful_interventions": 0.91,
    "team_satisfaction_score": 4.6
  },
  "community_impact": {
    "help_seeking_increase": 0.23,
    "resource_connection_rate": 0.78,
    "user_satisfaction_score": 4.8,
    "repeat_crisis_reduction": 0.15
  }
}
```

---

### GET `/conversation_stats`

**Purpose**: Conversation system performance and engagement metrics

**Response**:
```json
{
  "active_conversations": {
    "count": 3,
    "conversations": [
      {
        "user_id": "123456789",
        "channel_id": "987654321",
        "started_at": "2025-08-01T14:25:30Z",
        "crisis_level": "medium",
        "messages_exchanged": 8,
        "status": "active"
      }
    ]
  },
  "daily_metrics": {
    "conversations_started": 47,
    "avg_duration_minutes": 12.4,
    "engagement_rate": 0.67,
    "natural_conclusions": 0.82,
    "escalated_to_team": 0.18,
    "resource_connections": 31
  },
  "conversation_triggers": {
    "mention_triggers": 28,
    "keyword_triggers": 19,
    "natural_starters": 15,
    "crisis_overrides": 6
  },
  "effectiveness": {
    "user_satisfaction": 4.7,
    "crisis_de_escalation_rate": 0.84,
    "successful_handoffs": 0.91,
    "follow_up_engagement": 0.43
  }
}
```

---

## 🔍 Analysis & Testing Endpoints

### POST `/api/analyze`

**Purpose**: Analyze message through complete detection pipeline (testing/development)

**Authentication**: Required (API key or admin role)

**Request Body**:
```json
{
  "message": "I'm feeling really hopeless lately and don't know what to do",
  "context": {
    "channel_type": "support",
    "user_history": "previous_support_seeker",
    "time_of_day": "evening"
  },
  "options": {
    "include_reasoning": true,
    "test_mode": true
  }
}
```

**Response**:
```json
{
  "analysis_id": "uuid-1234-5678-9abc",
  "timestamp": "2025-08-01T14:32:15Z",
  "processing_time_ms": 347,
  "message": "I'm feeling really hopeless lately and don't know what to do",
  "detection_results": {
    "crisis_detected": true,
    "crisis_level": "medium",
    "confidence": 0.82,
    "requires_intervention": true
  },
  "keyword_analysis": {
    "matches_found": [
      {
        "keyword": "hopeless",
        "category": "depression_indicators",
        "confidence": 0.75,
        "crisis_level": "medium"
      },
      {
        "phrase": "don't know what to do",
        "category": "help_seeking",
        "confidence": 0.68,
        "crisis_level": "medium"
      }
    ],
    "context_modifiers": {
      "gaming_context": false,
      "creative_context": false,
      "support_context": true,
      "adjustment_factor": 1.2
    }
  },
  "nlp_analysis": {
    "depression_model": {
      "prediction": "crisis",
      "confidence": 0.78,
      "reasoning": "Strong depression indicators: hopelessness, lack of direction"
    },
    "sentiment_model": {
      "prediction": "negative",
      "confidence": 0.85,
      "reasoning": "Highly negative emotional tone with distress markers"
    },
    "emotional_distress_model": {
      "prediction": "distress",
      "confidence": 0.81,
      "reasoning": "Clear emotional distress with help-seeking behavior"
    },
    "ensemble_decision": {
      "final_prediction": "medium_crisis",
      "confidence": 0.82,
      "model_agreement": "consensus",
      "gaps_detected": false
    }
  },
  "response_plan": {
    "recommended_action": "medium_crisis_response",
    "response_type": "supportive_engagement",
    "escalation_required": false,
    "conversation_activation": true,
    "team_notification": true,
    "resource_offering": "mental_health_resources"
  },
  "test_mode_info": {
    "actual_response_sent": false,
    "would_trigger_alerts": true,
    "estimated_team_response_time": "8-12 minutes"
  }
}
```

**Status Codes**:
- `200`: Analysis completed successfully
- `400`: Invalid message format or missing required fields
- `401`: Authentication required
- `429`: Rate limit exceeded
- `500`: Analysis pipeline error

---

### POST `/api/test_keywords`

**Purpose**: Test keyword detection system with specific message

**Authentication**: Required (Crisis team role or API key)

**Request Body**:
```json
{
  "message": "I want to kill this boss in the game",
  "crisis_level": "test_all",
  "include_context": true
}
```

**Response**:
```json
{
  "message": "I want to kill this boss in the game",
  "timestamp": "2025-08-01T14:32:15Z",
  "processing_time_ms": 52,
  "keyword_detection": {
    "high_crisis_matches": [
      {
        "keyword": "kill",
        "category": "violence_indicators",
        "base_confidence": 0.65,
        "adjusted_confidence": 0.12,
        "context_adjustment": "gaming_context_detected"
      }
    ],
    "medium_crisis_matches": [],
    "low_crisis_matches": []
  },
  "context_analysis": {
    "gaming_context": {
      "detected": true,
      "confidence": 0.92,
      "indicators": ["boss", "game"],
      "adjustment_factor": 0.18
    },
    "creative_context": {
      "detected": false,
      "confidence": 0.05
    },
    "support_context": {
      "detected": false,
      "confidence": 0.03
    }
  },
  "final_assessment": {
    "crisis_detected": false,
    "crisis_level": "none",
    "confidence": 0.12,
    "reason": "Gaming context significantly reduces crisis interpretation"
  },
  "recommendations": {
    "action": "no_intervention",
    "would_alert_team": false,
    "context_learning": "gaming_pattern_reinforced"
  }
}
```

---

## 📊 Learning System Endpoints

### GET `/api/learning_stats`

**Purpose**: View learning system performance and improvement metrics

**Authentication**: Required (Crisis team role)

**Response**:
```json
{
  "learning_system": {
    "status": "active",
    "last_update": "2025-08-01T12:15:30Z",
    "total_adjustments": 1247
  },
  "false_positive_learning": {
    "reports_processed": 89,
    "accuracy_improvement": 0.034,
    "patterns_learned": [
      {
        "pattern": "gaming_violence_context",
        "adjustments_applied": 156,
        "effectiveness": 0.78
      },
      {
        "pattern": "creative_writing_death",
        "adjustments_applied": 67,
        "effectiveness": 0.82
      }
    ]
  },
  "false_negative_learning": {
    "reports_processed": 23,
    "new_patterns_discovered": 12,
    "detection_improvement": 0.018,
    "keyword_suggestions": [
      {
        "suggested_phrase": "can't take it anymore",
        "crisis_level": "high",
        "confidence": 0.89,
        "supporting_evidence": "3 confirmed cases"
      }
    ]
  },
  "community_adaptation": {
    "server_specific_patterns": 45,
    "lgbtqia_patterns_learned": 28,
    "cultural_context_improvements": 19
  },
  "effectiveness_metrics": {
    "overall_accuracy_improvement": 0.052,
    "false_positive_reduction": 0.038,
    "team_efficiency_gain": 0.21,
    "user_satisfaction_increase": 0.16
  }
}
```

---

### POST `/api/submit_feedback`

**Purpose**: Submit crisis response feedback for system learning

**Authentication**: Required (Crisis team role)

**Request Body**:
```json
{
  "feedback_type": "false_positive",
  "message_id": "discord_message_id_123456789",
  "original_detection": {
    "crisis_level": "medium",
    "confidence": 0.75
  },
  "correct_assessment": {
    "crisis_level": "none",
    "reason": "gaming_context"
  },
  "context": {
    "user_id": "user_123456789",
    "channel_id": "channel_987654321",
    "timestamp": "2025-08-01T14:30:00Z",
    "additional_context": "User was discussing video game strategy"
  },
  "reviewer_info": {
    "team_member_id": "team_member_456",
    "confidence_in_assessment": 0.95
  }
}
```

**Response**:
```json
{
  "feedback_id": "feedback_uuid_1234",
  "status": "accepted",
  "processing_result": {
    "learning_applied": true,
    "pattern_updated": "gaming_context_violence",
    "estimated_improvement": 0.003,
    "similar_cases_updated": 7
  },
  "system_impact": {
    "keyword_adjustments": 2,
    "context_rules_updated": 1,
    "false_positive_reduction_estimate": "0.5% over next week"
  }
}
```

---

## ⚙️ Administrative Endpoints

### GET `/api/system_config`

**Purpose**: Retrieve current system configuration (admin only)

**Authentication**: Required (Admin role or system token)

**Response**:
```json
{
  "crisis_detection": {
    "enabled": true,
    "detection_modes": ["keyword", "nlp_ensemble"],
    "thresholds": {
      "high_crisis": 0.8,
      "medium_crisis": 0.6,
      "low_crisis": 0.4
    }
  },
  "conversation_system": {
    "enabled": true,
    "conversation_timeout_minutes": 5,
    "requires_mention": true,
    "setup_instructions": true,
    "natural_starters": true
  },
  "escalation_config": {
    "crisis_channel_id": "123456789",
    "crisis_role_id": "987654321",
    "staff_dm_user_id": "456789123",
    "high_crisis_ping": true
  },
  "learning_system": {
    "enabled": true,
    "auto_adjustments": true,
    "max_adjustments_per_day": 50,
    "confidence_adjustment_range": [0.05, 0.30]
  },
  "api_settings": {
    "rate_limiting": true,
    "authentication_required": ["analyze", "admin"],
    "cors_enabled": false,
    "request_logging": true
  }
}
```

---

### POST `/api/emergency_override`

**Purpose**: Emergency system override for critical situations

**Authentication**: Required (Admin role with emergency permissions)

**Request Body**:
```json
{
  "override_type": "disable_detection",
  "duration_minutes": 30,
  "reason": "System maintenance during crisis drill",
  "affected_channels": ["all"],
  "emergency_contact": "admin_user_id_789"
}
```

**Response**:
```json
{
  "override_id": "emergency_override_uuid",
  "status": "active",
  "override_details": {
    "type": "disable_detection",
    "started_at": "2025-08-01T14:45:00Z",
    "expires_at": "2025-08-01T15:15:00Z",
    "affected_systems": ["crisis_detection", "auto_escalation"]
  },
  "safety_measures": {
    "manual_monitoring_required": true,
    "team_notifications_sent": true,
    "fallback_procedures_active": true
  }
}
```

---

## 📈 Integration Examples

### Health Check Integration

**Python Example**:
```python
import requests
import json

def check_ash_bot_health():
    try:
        response = requests.get('http://10.20.30.253:8882/health', timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            if health_data['status'] == 'healthy':
                return True, "System operational"
            else:
                return False, f"System unhealthy: {health_data}"
        else:
            return False, f"HTTP {response.status_code}"
    except Exception as e:
        return False, f"Connection error: {e}"

# Usage
healthy, message = check_ash_bot_health()
print(f"Ash Bot Status: {message}")
```

### Crisis Analytics Dashboard

**JavaScript Example**:
```javascript
async function getCrisisMetrics(timeframe = 'day') {
    try {
        const response = await fetch(
            `http://10.20.30.253:8882/crisis_metrics?timeframe=${timeframe}&include_details=true`
        );
        const data = await response.json();
        
        return {
            totalInterventions: data.crisis_interventions.total,
            accuracyRate: data.detection_accuracy.overall_accuracy,
            falsePositiveRate: data.detection_accuracy.false_positive_rate,
            responseTime: data.team_performance.avg_team_response_time_minutes
        };
    } catch (error) {
        console.error('Failed to fetch crisis metrics:', error);
        return null;
    }
}

// Usage
getCrisisMetrics('week').then(metrics => {
    console.log('Weekly Crisis Metrics:', metrics);
});
```

### Testing Integration

**Bash Script Example**:
```bash
#!/bin/bash
# Test message analysis pipeline

API_BASE="http://10.20.30.253:8882"
API_KEY="your_api_key_here"

test_message() {
    local message="$1"
    local expected_level="$2"
    
    response=$(curl -s -X POST \
        -H "Authorization: Bearer $API_KEY" \
        -H "Content-Type: application/json" \
        -d "{\"message\": \"$message\", \"options\": {\"test_mode\": true}}" \
        "$API_BASE/api/analyze")
    
    detected_level=$(echo "$response" | jq -r '.detection_results.crisis_level')
    
    if [ "$detected_level" = "$expected_level" ]; then
        echo "✅ PASS: '$message' -> $detected_level"
    else
        echo "❌ FAIL: '$message' -> Expected: $expected_level, Got: $detected_level"
    fi
}

# Run tests
test_message "I want to kill this boss" "none"
test_message "I feel hopeless and don't know what to do" "medium"
test_message "I'm going to end it all tonight" "high"
```

---

## 🔒 Security & Authentication

### API Key Authentication

**Header Format**:
```
Authorization: Bearer your_api_key_here
```

**Scope-based Access**:
- **Public endpoints**: No authentication required (`/health`, `/stats`)
- **Team endpoints**: Crisis team role or team API key required
- **Admin endpoints**: Administrator role or admin API key required
- **Emergency endpoints**: Special emergency permissions required

### Rate Limiting

**Default Limits**:
- **Health checks**: 100 requests/minute per IP
- **Analytics**: 30 requests/minute per authenticated user
- **Analysis endpoints**: 10 requests/minute per authenticated user
- **Admin endpoints**: 5 requests/minute per authenticated admin

**Rate Limit Headers**:
```
X-RateLimit-Limit: 30
X-RateLimit-Remaining: 27
X-RateLimit-Reset: 1672531200
```

### Data Privacy

**Privacy Protections**:
- **No message storage**: Messages analyzed in real-time, never persisted
- **Anonymized analytics**: User identifiers hashed for statistical analysis
- **Configurable logging**: Detailed logging can be disabled for privacy
- **GDPR compliance**: Data handling complies with privacy regulations

---

## 🚨 Error Handling

### Standard Error Response Format

```json
{
  "error": {
    "code": "INVALID_MESSAGE_FORMAT",
    "message": "Message content is required and must be a non-empty string",
    "details": {
      "field": "message",
      "received_type": "null",
      "expected_type": "string"
    },
    "timestamp": "2025-08-01T14:32:15Z",
    "request_id": "req_uuid_1234"
  }
}
```

### Common Error Codes

| Code | HTTP Status | Description | Resolution |
|------|------------|-------------|------------|
| `INVALID_MESSAGE_FORMAT` | 400 | Message content invalid | Check message format and encoding |
| `AUTHENTICATION_REQUIRED` | 401 | API key missing or invalid | Provide valid authentication |
| `INSUFFICIENT_PERMISSIONS` | 403 | User lacks required role | Contact admin for permission upgrade |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests | Wait for rate limit reset |
| `NLP_SERVICE_UNAVAILABLE` | 503 | NLP service connection failed | Check service status, retry later |
| `ANALYSIS_PIPELINE_ERROR` | 500 | Internal analysis error | Check logs, contact support |

---

## 📞 Support & Documentation

### Additional Resources

- **OpenAPI Specification**: Available at `/api/openapi.json`
- **Interactive API Explorer**: Available at `/api/docs` *[Planned]*
- **SDK Documentation**: Language-specific SDKs *[Planned]*
- **Integration Examples**: Complete examples repository

### Getting Help

- **Technical Issues**: [GitHub Issues](https://github.com/the-alphabet-cartel/ash-bot/issues)
- **Community Support**: [Discord Server](https://discord.gg/alphabetcartel)
- **API Questions**: Documentation team via GitHub discussions
- **Emergency Support**: Contact through established crisis team channels

### API Changelog

- **v3.0.0**: Initial API release with health, analytics, and testing endpoints
- **v3.0.1**: Added learning system endpoints and feedback submission *[Planned]*
- **v3.1.0**: Enhanced analysis endpoints with context detection *[Planned]*

---

**The Ash Bot API is designed to support transparent, effective crisis response while maintaining user privacy and community autonomy. For questions or feature requests, engage with our community through the channels listed above.**

**Discord**: [https://discord.gg/alphabetcartel](https://discord.gg/alphabetcartel)  
**Website**: [http://alphabetcartel.org](http://alphabetcartel.org)  
**Repository**: [https://github.com/the-alphabet-cartel/ash-bot](https://github.com/the-alphabet-cartel/ash-bot)

*Built with ❤️ for chosen family, one API call at a time.*