# API Documentation - Ash System

**Complete API Reference for The Alphabet Cartel's Mental Health Crisis Detection System**

This documentation covers all API endpoints for the Ash system components, providing developers and integrators with comprehensive technical reference material.

---

## 🎯 API Overview

### System APIs

The Ash system exposes four primary APIs across different services:

- **Ash Bot API (8882):** Main Discord bot coordination and status
- **NLP Server API (8881):** Natural language processing and crisis analysis  
- **Dashboard API (8883):** Analytics dashboard and crisis management
- **Testing Suite API (8884):** Automated testing and validation

### Authentication

**API Key Authentication:**
```http
Authorization: Bearer your-api-key-here
```

**Service-to-Service Authentication:**
```http
X-Service-Key: internal-service-key
X-Service-Name: requesting-service-name
```

### Rate Limiting

**Standard Rate Limits:**
- **Public APIs:** 100 requests/hour per API key
- **Internal APIs:** 1000 requests/hour per service
- **Critical APIs:** No rate limit (health checks, alerts)

**Rate Limit Headers:**
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1627847400
```

---

## 🤖 Ash Bot API (Port 8882)

**Base URL:** `http://10.20.30.253:8882/api/v1`

### Health and Status

#### GET /health
**Description:** Check bot health and operational status

**Response:**
```json
{
  "status": "healthy",
  "version": "2.0.0",
  "uptime": 3600,
  "discord_connected": true,
  "nlp_server_connected": true,
  "database_connected": true,
  "last_message_processed": "2025-07-27T10:30:00Z",
  "message_processing_rate": 45.2,
  "alerts_sent_today": 12,
  "response_time_ms": 150
}
```

**Status Codes:**
- `200 OK`: Service healthy
- `503 Service Unavailable`: Service degraded or offline

#### GET /status/detailed
**Description:** Comprehensive system status information

**Authentication:** Required

**Response:**
```json
{
  "service": "ash-bot",
  "version": "2.0.0", 
  "environment": "production",
  "uptime_seconds": 86400,
  "connections": {
    "discord": {
      "status": "connected",
      "latency_ms": 45,
      "guilds_connected": 1,
      "last_heartbeat": "2025-07-27T10:30:00Z"
    },
    "nlp_server": {
      "status": "connected",
      "url": "http://10.20.30.16:8881",
      "response_time_ms": 234,
      "last_request": "2025-07-27T10:29:45Z"
    },
    "database": {
      "status": "connected",
      "type": "postgresql",
      "connection_pool_active": 8,
      "connection_pool_max": 20
    }
  },
  "performance": {
    "messages_processed_24h": 2847,
    "average_processing_time_ms": 125,
    "crisis_alerts_generated_24h": 5,
    "false_positive_rate_24h": 0.023
  },
  "resources": {
    "cpu_usage_percent": 15.6,
    "memory_usage_mb": 512,
    "memory_total_mb": 2048,
    "disk_usage_percent": 35.2
  }
}
```

### Crisis Detection

#### POST /analyze/message
**Description:** Submit a message for crisis analysis

**Authentication:** Required

**Request Body:**
```json
{
  "message_id": "123456789012345678",
  "user_id": "987654321098765432",
  "channel_id": "456789012345678901", 
  "content": "I've been feeling really down lately",
  "timestamp": "2025-07-27T10:30:00Z",
  "context": {
    "previous_messages": [
      {
        "content": "How was your day?",
        "timestamp": "2025-07-27T10:25:00Z"
      }
    ],
    "user_history": {
      "previous_alerts": 0,
      "last_interaction": "2025-07-26T14:20:00Z"
    }
  }
}
```

**Response:**
```json
{
  "analysis_id": "uuid-string",
  "message_id": "123456789012345678",
  "crisis_detected": false,
  "priority_level": "none",
  "confidence_score": 0.23,
  "analysis": {
    "keyword_matches": [],
    "nlp_analysis": {
      "sentiment": "negative",
      "intent": "expression_of_sadness",
      "urgency": "low",
      "context_score": 0.15
    },
    "recommendation": "monitor",
    "threshold_analysis": {
      "high_priority": 0.8,
      "medium_priority": 0.6,
      "low_priority": 0.4,
      "current_score": 0.23
    }
  },
  "processing_time_ms": 1250,
  "timestamp": "2025-07-27T10:30:02Z"
}
```

#### POST /analyze/batch
**Description:** Batch process multiple messages for efficiency

**Authentication:** Required

**Request Body:**
```json
{
  "messages": [
    {
      "message_id": "123456789012345678",
      "content": "Message content here",
      "user_id": "987654321098765432",
      "timestamp": "2025-07-27T10:30:00Z"
    }
  ],
  "options": {
    "include_context": true,
    "priority_only": false,
    "async_processing": false
  }
}
```

### Alert Management

#### POST /alerts/send
**Description:** Send crisis alert to response team

**Authentication:** Required

**Request Body:**
```json
{
  "alert_type": "high_priority",
  "message_id": "123456789012345678",
  "user_id": "987654321098765432",
  "analysis_summary": {
    "confidence_score": 0.85,
    "detected_indicators": ["explicit_self_harm", "urgency_keywords"],
    "recommended_response": "immediate_intervention"
  },
  "responder_assignments": ["crisis_team_lead", "available_responders"],
  "escalation_rules": {
    "auto_escalate_after_minutes": 15,
    "escalation_targets": ["senior_crisis_responder"]
  }
}
```

**Response:**
```json
{
  "alert_id": "uuid-string",
  "status": "sent",
  "recipients": [
    {
      "type": "discord_role",
      "target": "crisis_response_team",
      "notification_sent": true,
      "timestamp": "2025-07-27T10:30:05Z"
    },
    {
      "type": "dashboard_alert", 
      "target": "ash_dashboard",
      "notification_sent": true,
      "timestamp": "2025-07-27T10:30:05Z"
    }
  ],
  "estimated_response_time": "2-5 minutes",
  "alert_reference": "ALERT-20250727-001"
}
```

### Configuration

#### GET /config/detection-settings
**Description:** Retrieve current crisis detection configuration

**Authentication:** Required

**Response:**
```json
{
  "thresholds": {
    "high_priority": 0.8,
    "medium_priority": 0.6,
    "low_priority": 0.4
  },
  "keywords": {
    "high_crisis_count": 45,
    "medium_crisis_count": 78,
    "low_crisis_count": 123,
    "last_updated": "2025-07-20T09:00:00Z"
  },
  "detection_settings": {
    "nlp_enabled": true,
    "keyword_detection_enabled": true,
    "context_analysis_enabled": true,
    "learning_mode": false
  },
  "response_settings": {
    "auto_alert_enabled": true,
    "response_timeout_minutes": 30,
    "escalation_enabled": true
  }
}
```

---

## 🧠 NLP Server API (Port 8881)

**Base URL:** `http://10.20.30.16:8881/api/v1`

### Health and Performance

#### GET /health
**Description:** NLP server health check

**Response:**
```json
{
  "status": "healthy",
  "version": "1.5.2",
  "uptime": 7200,
  "gpu_available": true,
  "model_loaded": true,
  "processing_queue_size": 0,
  "average_response_time_ms": 1850,
  "total_analyses_today": 1247,
  "gpu_utilization_percent": 34.5,
  "memory_usage_gb": 12.8
}
```

#### GET /performance/metrics
**Description:** Detailed performance metrics

**Authentication:** Required

**Response:**
```json
{
  "processing_stats": {
    "total_requests_24h": 2847,
    "average_response_time_ms": 1650,
    "p95_response_time_ms": 2800,
    "p99_response_time_ms": 4200,
    "error_rate_percent": 0.12
  },
  "model_performance": {
    "model_name": "crisis-detection-v2.1",
    "model_size_gb": 3.2,
    "inference_time_ms": 1450,
    "batch_processing_enabled": true,
    "max_batch_size": 32
  },
  "resource_usage": {
    "cpu_cores": 8,
    "cpu_usage_percent": 45.2,
    "ram_total_gb": 64,
    "ram_used_gb": 18.7,
    "gpu_model": "RTX 3050",
    "gpu_memory_used_mb": 6144,
    "gpu_memory_total_mb": 8192
  }
}
```

### Text Analysis

#### POST /analyze
**Description:** Analyze text for crisis indicators

**Request Body:**
```json
{
  "text": "I've been having a really hard time lately and don't know what to do",
  "context": {
    "user_id": "user123",
    "conversation_history": [
      {
        "text": "How are you feeling today?",
        "timestamp": "2025-07-27T10:25:00Z",
        "speaker": "friend"
      }
    ],
    "metadata": {
      "channel_type": "private_message",
      "time_of_day": "evening",
      "user_timezone": "America/Los_Angeles"
    }
  },
  "options": {
    "include_explanations": true,
    "detailed_analysis": true,
    "sentiment_analysis": true
  }
}
```

**Response:**
```json
{
  "analysis_id": "uuid-string",
  "timestamp": "2025-07-27T10:30:02Z",
  "processing_time_ms": 1650,
  "results": {
    "crisis_detected": true,
    "priority_level": "medium",
    "confidence_score": 0.72,
    "detailed_scores": {
      "self_harm_risk": 0.15,
      "suicide_ideation": 0.08,
      "emotional_distress": 0.78,
      "help_seeking": 0.65,
      "urgency": 0.42
    }
  },
  "analysis": {
    "sentiment": {
      "overall": "negative",
      "polarity": -0.6,
      "subjectivity": 0.8,
      "emotions": {
        "sadness": 0.72,
        "fear": 0.23,
        "anger": 0.05
      }
    },
    "intent_classification": {
      "primary_intent": "seeking_support",
      "secondary_intent": "expressing_distress",
      "confidence": 0.85
    },
    "linguistic_features": {
      "negation_count": 1,
      "first_person_pronouns": 3,
      "emotional_intensity": "high",
      "temporal_references": ["lately"]
    },
    "context_analysis": {
      "conversation_flow": "help_seeking_response",
      "relationship_indicators": "supportive_environment",
      "environmental_factors": ["evening_timing"]
    }
  },
  "recommendations": {
    "response_urgency": "moderate",
    "suggested_approach": "empathetic_outreach",
    "escalation_indicators": ["monitor_for_worsening"],
    "followup_timeline": "within_2_hours"
  },
  "model_info": {
    "model_version": "crisis-detection-v2.1",
    "training_date": "2025-06-15",
    "model_confidence": 0.94
  }
}
```

#### POST /analyze/batch
**Description:** Batch analysis for multiple texts

**Request Body:**
```json
{
  "texts": [
    {
      "id": "msg_001",
      "text": "First message content",
      "context": {}
    },
    {
      "id": "msg_002", 
      "text": "Second message content",
      "context": {}
    }
  ],
  "options": {
    "parallel_processing": true,
    "priority_queue": false,
    "max_processing_time_ms": 5000
  }
}
```

### Model Management

#### GET /models/info
**Description:** Information about loaded models

**Authentication:** Required

**Response:**
```json
{
  "active_models": [
    {
      "name": "crisis-detection-v2.1",
      "type": "transformer",
      "size_gb": 3.2,
      "loaded_date": "2025-07-27T08:00:00Z",
      "performance": {
        "accuracy": 0.94,
        "precision": 0.91,
        "recall": 0.97,
        "f1_score": 0.94
      },
      "specializations": [
        "suicide_ideation",
        "self_harm_detection", 
        "emotional_distress",
        "help_seeking_behavior"
      ]
    }
  ],
  "available_models": [
    {
      "name": "crisis-detection-v2.0",
      "status": "standby",
      "can_load": true
    }
  ],
  "model_capabilities": {
    "max_text_length": 2048,
    "supported_languages": ["en"],
    "context_window": 512,
    "batch_processing": true
  }
}
```

#### POST /models/reload
**Description:** Reload or switch models

**Authentication:** Required

**Request Body:**
```json
{
  "model_name": "crisis-detection-v2.1",
  "reload_reason": "configuration_update",
  "preserve_cache": true
}
```

---

## 📊 Dashboard API (Port 8883)

**Base URL:** `http://10.20.30.16:8883/api/v1`

### Authentication

#### POST /auth/login
**Description:** Authenticate dashboard user

**Request Body:**
```json
{
  "username": "crisis_responder",
  "password": "secure_password",
  "remember_me": true
}
```

**Response:**
```json
{
  "success": true,
  "token": "jwt-token-string",
  "expires_at": "2025-07-28T10:30:00Z",
  "user": {
    "id": "user123",
    "username": "crisis_responder",
    "role": "crisis_team",
    "permissions": ["view_alerts", "respond_to_crisis", "view_analytics"],
    "last_login": "2025-07-27T09:15:00Z"
  },
  "preferences": {
    "dashboard_layout": "crisis_focused",
    "notification_settings": {
      "high_priority_sound": true,
      "desktop_notifications": true
    }
  }
}
```

### Crisis Alert Management

#### GET /alerts/active
**Description:** Retrieve active crisis alerts

**Authentication:** Required

**Query Parameters:**
- `priority`: Filter by priority level (high, medium, low)
- `assignee`: Filter by assigned responder
- `limit`: Number of results (default: 50)
- `offset`: Pagination offset

**Response:**
```json
{
  "alerts": [
    {
      "alert_id": "uuid-string",
      "created_at": "2025-07-27T10:30:00Z",
      "priority": "high",
      "status": "active",
      "user_info": {
        "user_id": "discord_user_id",
        "username": "anonymized_user",
        "display_name": "User#1234"
      },
      "message_info": {
        "channel": "general-chat",
        "timestamp": "2025-07-27T10:29:45Z",
        "content_summary": "Expressed explicit self-harm thoughts"
      },
      "analysis": {
        "confidence_score": 0.89,
        "detected_indicators": ["explicit_self_harm", "urgent_help_seeking"],
        "risk_assessment": "immediate_intervention_needed"
      },
      "response_info": {
        "assigned_responder": "crisis_team_lead",
        "response_time_target": "5_minutes",
        "escalation_timer": "12_minutes_remaining",
        "status": "initial_contact_made"
      },
      "actions_available": [
        "respond_directly",
        "escalate_to_professional",
        "mark_resolved",
        "request_backup"
      ]
    }
  ],
  "pagination": {
    "total": 3,
    "limit": 50,
    "offset": 0,
    "has_more": false
  },
  "summary": {
    "total_active": 3,
    "high_priority": 1,
    "medium_priority": 2,
    "low_priority": 0,
    "unassigned": 0,
    "overdue_response": 0
  }
}
```

#### POST /alerts/{alert_id}/respond
**Description:** Record crisis response action

**Authentication:** Required

**Request Body:**
```json
{
  "response_type": "direct_contact",
  "action_taken": "sent_supportive_dm",
  "outcome": "user_responded_positively",
  "notes": "User expressed gratitude for outreach. Provided crisis resources. Will follow up in 2 hours.",
  "next_actions": [
    {
      "action": "follow_up_contact",
      "scheduled_time": "2025-07-27T12:30:00Z",
      "assigned_to": "crisis_team_lead"
    }
  ],
  "status_update": "monitoring",
  "escalation_needed": false,
  "resources_provided": [
    "crisis_text_line",
    "local_counseling_services"
  ]
}
```

**Response:**
```json
{
  "success": true,
  "alert_id": "uuid-string",
  "response_id": "response-uuid",
  "updated_status": "monitoring",
  "next_review": "2025-07-27T12:30:00Z",
  "response_recorded_at": "2025-07-27T10:45:00Z",
  "response_time_minutes": 15,
  "alert_timeline": [
    {
      "timestamp": "2025-07-27T10:30:00Z",
      "event": "alert_created",
      "details": "High priority crisis detected"
    },
    {
      "timestamp": "2025-07-27T10:32:00Z", 
      "event": "responder_assigned",
      "details": "Assigned to crisis_team_lead"
    },
    {
      "timestamp": "2025-07-27T10:45:00Z",
      "event": "initial_response",
      "details": "Direct contact made, positive response"
    }
  ]
}
```

### Analytics and Reporting

#### GET /analytics/dashboard
**Description:** Dashboard analytics overview

**Authentication:** Required

**Query Parameters:**
- `timeframe`: Time period (24h, 7d, 30d, 90d)
- `include_trends`: Include trend analysis (true/false)

**Response:**
```json
{
  "timeframe": "24h",
  "generated_at": "2025-07-27T10:30:00Z",
  "system_health": {
    "overall_status": "healthy",
    "uptime_percent": 99.8,
    "average_response_time_ms": 1650,
    "error_rate_percent": 0.05
  },
  "crisis_detection": {
    "total_messages_processed": 2847,
    "alerts_generated": 12,
    "alert_breakdown": {
      "high_priority": 3,
      "medium_priority": 6,
      "low_priority": 3
    },
    "detection_accuracy": {
      "true_positive_rate": 0.94,
      "false_positive_rate": 0.06,
      "precision": 0.91,
      "recall": 0.97
    }
  },
  "response_performance": {
    "average_response_time_minutes": 4.2,
    "response_rate_percent": 100,
    "escalation_rate_percent": 8.3,
    "resolution_rate_percent": 91.7,
    "responder_activity": {
      "total_responders": 8,
      "active_responders": 6,
      "average_caseload": 2.0
    }
  },
  "community_insights": {
    "peak_activity_hours": ["18:00-22:00"],
    "common_crisis_types": [
      {"type": "emotional_distress", "percentage": 45},
      {"type": "anxiety_panic", "percentage": 23},
      {"type": "depression_symptoms", "percentage": 32}
    ],
    "support_effectiveness": {
      "positive_outcomes": 89,
      "neutral_outcomes": 8,
      "escalated_cases": 3
    }
  },
  "trends": {
    "crisis_volume_trend": "stable",
    "response_time_trend": "improving",
    "accuracy_trend": "stable_high",
    "team_performance_trend": "excellent"
  }
}
```

### Team Management

#### GET /team/status
**Description:** Crisis response team status

**Authentication:** Required

**Response:**
```json
{
  "team_overview": {
    "total_members": 12,
    "currently_active": 8,
    "on_duty": 6,
    "available": 4,
    "busy": 2,
    "offline": 4
  },
  "shift_coverage": {
    "current_shift": "day_shift",
    "shift_lead": "crisis_team_lead",
    "coverage_level": "full",
    "next_shift_change": "2025-07-27T18:00:00Z"
  },
  "team_members": [
    {
      "user_id": "responder_001",
      "display_name": "Crisis Responder 1",
      "role": "senior_responder",
      "status": "available",
      "current_caseload": 1,
      "max_caseload": 3,
      "shift_hours": "08:00-16:00",
      "last_activity": "2025-07-27T10:15:00Z",
      "response_stats": {
        "responses_today": 3,
        "average_response_time_minutes": 3.2,
        "success_rate_percent": 95
      }
    }
  ],
  "coverage_gaps": [],
  "alerts_waiting_assignment": 0,
  "team_performance": {
    "overall_rating": "excellent",
    "response_time_rating": "excellent", 
    "resolution_rate_rating": "good",
    "community_feedback_rating": "excellent"
  }
}
```

---

## 🧪 Testing Suite API (Port 8884)

**Base URL:** `http://10.20.30.16:8884/api/v1`

### Test Execution

#### POST /test/comprehensive
**Description:** Run comprehensive 350-phrase test suite

**Authentication:** Required

**Request Body:**
```json
{
  "test_type": "comprehensive",
  "options": {
    "include_performance_metrics": true,
    "save_detailed_results": true,
    "notify_on_completion": true,
    "test_categories": ["all"],
    "parallel_execution": true
  },
  "configuration": {
    "target_accuracy": 0.95,
    "max_processing_time_ms": 5000,
    "retry_failed_tests": true
  }
}
```

**Response:**
```json
{
  "test_id": "test-uuid-string",
  "status": "running",
  "started_at": "2025-07-27T10:30:00Z",
  "estimated_completion": "2025-07-27T10:45:00Z",
  "progress": {
    "total_tests": 350,
    "completed": 0,
    "remaining": 350,
    "current_category": "definite_high_priority"
  },
  "test_url": "/test/comprehensive/test-uuid-string",
  "results_url": "/test/comprehensive/test-uuid-string/results",
  "webhook_notifications": {
    "progress_updates": true,
    "completion_notification": true
  }
}
```

#### GET /test/comprehensive/{test_id}
**Description:** Get comprehensive test status and results

**Authentication:** Required

**Response:**
```json
{
  "test_id": "test-uuid-string",
  "status": "completed",
  "started_at": "2025-07-27T10:30:00Z",
  "completed_at": "2025-07-27T10:42:30Z",
  "duration_seconds": 750,
  "overall_results": {
    "total_tests": 350,
    "passed": 332,
    "failed": 18,
    "accuracy_percent": 94.9,
    "target_accuracy_met": false
  },
  "category_breakdown": {
    "definite_high_priority": {
      "total": 45,
      "passed": 44,
      "failed": 1,
      "accuracy_percent": 97.8,
      "target_met": true
    },
    "definite_medium_priority": {
      "total": 78,
      "passed": 75,
      "failed": 3,
      "accuracy_percent": 96.2,
      "target_met": true
    },
    "definite_low_priority": {
      "total": 67,
      "passed": 63,
      "failed": 4,
      "accuracy_percent": 94.0,
      "target_met": false
    },
    "maybe_categories": {
      "total": 95,
      "passed": 85,
      "failed": 10,
      "accuracy_percent": 89.5,
      "acceptable_range": true
    },
    "false_positive_prevention": {
      "total": 65,
      "passed": 65,
      "failed": 0,
      "accuracy_percent": 100.0,
      "target_met": true
    }
  },
  "performance_metrics": {
    "average_processing_time_ms": 1650,
    "p95_processing_time_ms": 2800,
    "max_processing_time_ms": 4200,
    "timeout_count": 0,
    "nlp_server_uptime_percent": 100
  },
  "failure_analysis": {
    "common_failure_patterns": [
      {
        "pattern": "ambiguous_metaphorical_language",
        "count": 8,
        "examples": ["walking on thin ice", "drowning in work"]
      },
      {
        "pattern": "context_dependent_expressions",
        "count": 6,
        "examples": ["I'm dying to see that movie"]
      }
    ],
    "recommended_improvements": [
      "enhance_context_analysis",
      "improve_metaphor_detection",
      "update_cultural_language_patterns"
    ]
  },
  "detailed_results_available": true,
  "export_formats": ["json", "csv", "pdf_report"]
}
```

#### POST /test/quick-validation
**Description:** Run quick 10-phrase validation test

**Request Body:**
```json
{
  "test_type": "quick_validation",
  "options": {
    "random_sample": true,
    "include_all_priorities": true
  }
}
```

**Response:**
```json
{
  "test_id": "quick-test-uuid",
  "status": "completed",
  "duration_seconds": 25,
  "results": {
    "total_tests": 10,
    "passed": 9,
    "failed": 1,
    "accuracy_percent": 90.0
  },
  "system_health": {
    "nlp_server_responsive": true,
    "average_response_time_ms": 1450,
    "all_services_operational": true
  },
  "recommendation": "system_operational_with_minor_issues",
  "next_action": "monitor_accuracy_trends"
}
```

### Test Results and Analytics

#### GET /test/results/latest
**Description:** Get latest test results summary

**Authentication:** Required

**Response:**
```json
{
  "latest_comprehensive": {
    "test_id": "test-uuid-string",
    "completed_at": "2025-07-27T10:42:30Z",
    "accuracy_percent": 94.9,
    "status": "passed_with_warnings"
  },
  "latest_quick_validation": {
    "test_id": "quick-test-uuid",
    "completed_at": "2025-07-27T10:30:00Z", 
    "accuracy_percent": 90.0,
    "status": "passed"
  },
  "trend_analysis": {
    "accuracy_trend_7d": "stable",
    "performance_trend_7d": "improving",
    "failure_pattern_trends": ["metaphorical_language_increasing"]
  },
  "health_indicators": {
    "overall_system_health": "good",
    "detection_accuracy_health": "good",
    "performance_health": "excellent",
    "reliability_health": "excellent"
  }
}
```

#### GET /test/analytics/accuracy-trends
**Description:** Historical accuracy trend analysis

**Authentication:** Required

**Query Parameters:**
- `timeframe`: Analysis period (7d, 30d, 90d)
- `category`: Specific test category or "all"

**Response:**
```json
{
  "timeframe": "30d",
  "category": "all",
  "data_points": [
    {
      "date": "2025-07-01",
      "overall_accuracy": 94.2,
      "high_priority_accuracy": 97.8,
      "medium_priority_accuracy": 95.1,
      "low_priority_accuracy": 92.3,
      "false_positive_rate": 0.058
    }
  ],
  "trends": {
    "overall_direction": "stable_high",
    "significant_changes": [],
    "accuracy_variance": 0.023,
    "performance_correlation": "positive"
  },
  "insights": {
    "best_performing_category": "high_priority_detection",
    "improvement_opportunities": ["context_dependent_detection"],
    "stability_rating": "excellent"
  }
}
```

### Configuration and Management

#### GET /test/configuration
**Description:** Get testing suite configuration

**Authentication:** Required

**Response:**
```json
{
  "test_suite_version": "2.1.0",
  "total_test_phrases": 350,
  "test_categories": {
    "definite_high_priority": 45,
    "definite_medium_priority": 78,
    "definite_low_priority": 67,
    "maybe_high_priority": 32,
    "maybe_medium_priority": 38,
    "maybe_low_priority": 25,
    "false_positive_prevention": 65
  },
  "accuracy_targets": {
    "overall_minimum": 0.95,
    "high_priority_minimum": 0.98,
    "medium_priority_minimum": 0.95,
    "low_priority_minimum": 0.90,
    "false_positive_maximum": 0.05
  },
  "performance_targets": {
    "max_processing_time_ms": 3000,
    "average_target_ms": 2000,
    "timeout_threshold_ms": 5000
  },
  "scheduling": {
    "quick_validation_frequency": "hourly",
    "comprehensive_test_frequency": "daily",
    "performance_analysis_frequency": "weekly"
  }
}
```

---

## 🔄 Webhooks and Real-time Updates

### Webhook Configuration

**Webhook Registration:**
```http
POST /webhooks/register
Content-Type: application/json
Authorization: Bearer api-key

{
  "url": "https://your-service.com/webhook/ash-alerts",
  "events": ["crisis_alert_created", "crisis_alert_resolved"],
  "secret": "webhook-verification-secret",
  "active": true
}
```

**Webhook Payload Example:**
```json
{
  "event": "crisis_alert_created",
  "timestamp": "2025-07-27T10:30:00Z",
  "data": {
    "alert_id": "uuid-string",
    "priority": "high",
    "confidence_score": 0.89,
    "user_info": {
      "user_id": "anonymized_id",
      "channel": "general"
    },
    "response_required": true,
    "estimated_response_time": "5_minutes"
  },
  "signature": "sha256=webhook-verification-signature"
}
```

### WebSocket Connections

**Dashboard Real-time Updates:**
```javascript
// WebSocket connection for real-time dashboard updates
const socket = new WebSocket('wss://10.20.30.16:8883/ws/dashboard');

socket.onmessage = function(event) {
  const update = JSON.parse(event.data);
  
  if (update.type === 'new_alert') {
    // Handle new crisis alert
    displayAlert(update.data);
  } else if (update.type === 'alert_update') {
    // Handle alert status update  
    updateAlertStatus(update.data);
  }
};
```

**Message Types:**
- `new_alert`: New crisis alert created
- `alert_update`: Alert status or assignment changed
- `system_status`: System health status change
- `team_update`: Crisis team member status change

---

## 🔒 Security and Best Practices

### API Security

**Authentication Best Practices:**
- **Secure API Keys:** Use strong, randomly generated API keys
- **Key Rotation:** Rotate API keys quarterly or after security incidents
- **Scope Limitation:** Use minimum necessary permissions for each API key
- **Secure Storage:** Store API keys in secure environment variables

**Rate Limiting:**
- **Implement Backoff:** Use exponential backoff for failed requests
- **Monitor Usage:** Track API usage patterns for anomaly detection
- **Cache Responses:** Cache non-sensitive responses to reduce API calls
- **Batch Operations:** Use batch endpoints for bulk operations

### Error Handling

**Standard Error Response:**
```json
{
  "error": {
    "code": "CRISIS_ANALYSIS_FAILED",
    "message": "Unable to analyze text for crisis indicators",
    "details": "NLP server temporarily unavailable",
    "timestamp": "2025-07-27T10:30:00Z",
    "request_id": "req-uuid-string",
    "retry_after": 30
  },
  "support": {
    "documentation": "https://docs.alphabetcartel.org/ash/api",
    "contact": "https://discord.gg/alphabetcartel"
  }
}
```

**Error Codes:**
- `INVALID_API_KEY`: Authentication failed
- `RATE_LIMIT_EXCEEDED`: Too many requests
- `CRISIS_ANALYSIS_FAILED`: NLP processing error
- `SERVICE_UNAVAILABLE`: Dependent service offline
- `VALIDATION_ERROR`: Invalid request parameters

### Data Privacy

**Privacy Safeguards:**
- **Data Minimization:** Process only necessary text content
- **Anonymization:** Remove or hash personal identifiers
- **Retention Limits:** Automatic deletion of processed data
- **Access Logging:** Log all API access for audit purposes

---

## 📞 Support and Resources

### API Support

**Getting Help:**
- **GitHub Issues:** https://github.com/The-Alphabet-Cartel/ash/issues
- **Discord Community:** [The Alphabet Cartel Discord](https://discord.gg/alphabetcartel) #tech-support
- **Documentation:** Complete API reference and guides

**Response Times:**
- **Critical Issues:** Within 4 hours during business hours
- **General Support:** Within 24 hours
- **Feature Requests:** Reviewed weekly in team meetings

### Development Resources

**SDKs and Libraries:**
- **Python SDK:** `pip install ash-client` (coming soon)
- **JavaScript SDK:** `npm install @alphabet-cartel/ash-client` (coming soon)
- **Postman Collection:** Available in repository `/docs/postman/`

**Code Examples:**
- **Crisis Detection Integration:** `/examples/crisis-detection/`
- **Dashboard Integration:** `/examples/dashboard-integration/`
- **Webhook Handling:** `/examples/webhook-handlers/`

---

*This API documentation supports the mental health crisis detection mission of [The Alphabet Cartel Discord community](https://discord.gg/alphabetcartel). Our APIs enable compassionate, technology-assisted crisis response for LGBTQIA+ individuals and chosen family networks.*

**Built with 🖤 for chosen family everywhere.**

---

**Document Version:** 1.0  
**Last Updated:** July 27, 2025  
**API Version:** v1  
**Next Review:** August 27, 2025