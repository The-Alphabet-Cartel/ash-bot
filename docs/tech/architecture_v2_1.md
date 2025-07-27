# Ash System Architecture Overview

**Mental Health Crisis Detection System for Discord Communities**

This document provides a comprehensive overview of the Ash system architecture, designed specifically for [The Alphabet Cartel](https://discord.gg/alphabetcartel) LGBTQIA+ community mental health support.

---

## 🎯 System Overview

### Mission Statement
Provide automated, compassionate, and reliable mental health crisis detection and response capabilities within Discord communities, specifically designed to support LGBTQIA+ individuals and chosen family networks.

### Core Objectives
- **Real-time Crisis Detection:** Monitor Discord messages for mental health crisis indicators
- **Immediate Alert System:** Notify trained crisis responders within seconds of detection
- **High Accuracy:** Minimize false positives while ensuring no crisis situations are missed
- **Privacy Protection:** Process only necessary text data with robust privacy safeguards
- **Scalability:** Support community growth and expanding crisis response capabilities
- **Reliability:** Maintain 99.5%+ uptime for critical mental health support functions

---

## 🏗️ System Architecture

### Distributed Microservices Design

```
┌─────────────────────────────────────────────────────────────────┐
│                    The Alphabet Cartel Discord                  │
│                         Community                               │
└─────────────────────┬───────────────────────────────────────────┘
                      │ Discord Messages
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                 Linux Server (10.20.30.253)                    │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │               ASH DISCORD BOT                           │   │
│  │                                                         │   │
│  │  • Discord.py Integration                              │   │
│  │  • Message Processing Pipeline                         │   │
│  │  • Keyword Detection Engine                           │   │
│  │  • Crisis Response Coordination                       │   │
│  │  • Alert Generation & Routing                         │   │
│  │                                                         │   │
│  │  Port: 8882 (API)                                     │   │
│  │  Docker Container                                      │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────┬───────────────────────────────────────────┘
                      │ NLP API Calls
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│              Windows 11 AI Server (10.20.30.16)               │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                ASH-NLP SERVER                           │   │
│  │                                                         │   │
│  │  • Advanced NLP Processing                             │   │
│  │  • Transformer Models                                  │   │
│  │  • CUDA GPU Acceleration                               │   │
│  │  • Crisis Severity Analysis                            │   │
│  │  • Context Understanding                               │   │
│  │                                                         │   │
│  │  Port: 8881 (API)                                     │   │
│  │  Hardware: Ryzen 7 7700X, 64GB RAM, RTX 3050         │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              ASH-DASH ANALYTICS                         │   │
│  │                                                         │   │
│  │  • Real-time Dashboard                                 │   │
│  │  • Crisis Alert Management                             │   │
│  │  • Performance Analytics                               │   │
│  │  • Team Coordination Interface                         │   │
│  │  • Historical Data Analysis                            │   │
│  │                                                         │   │
│  │  Port: 8883 (HTTPS Web)                               │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │             ASH-THRASH TESTING                          │   │
│  │                                                         │   │
│  │  • 350-Phrase Test Suite                               │   │
│  │  • Automated Validation                                │   │
│  │  • Quality Assurance                                   │   │
│  │  • Performance Benchmarking                            │   │
│  │  • Regression Testing                                  │   │
│  │                                                         │   │
│  │  Port: 8884 (API)                                     │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🧩 Component Details

### 1. Ash Discord Bot (Primary)
**Repository:** https://github.com/The-Alphabet-Cartel/ash  
**Location:** Linux Server (10.20.30.253:8882)  
**Technology Stack:** Python, Discord.py, SQLite/PostgreSQL, Docker

**Core Functions:**
- **Message Monitoring:** Real-time processing of Discord messages across all channels
- **Initial Filtering:** Keyword-based pre-filtering to reduce NLP processing load
- **Crisis Detection Pipeline:** Hybrid approach combining keyword detection with NLP analysis
- **Alert Generation:** Create and route crisis alerts to appropriate team members
- **Response Coordination:** Manage automated and manual crisis response workflows
- **Discord Integration:** Handle Discord API interactions, permissions, and rate limiting

**Key Features:**
- **Multi-layered Detection:** Combines rule-based keywords with AI-powered NLP analysis
- **Context Awareness:** Understands conversation context and user interaction patterns
- **Privacy by Design:** Processes only text necessary for crisis detection
- **Scalable Architecture:** Handles message volume growth and expanding server communities
- **Fail-safe Design:** Continues operating with degraded functionality if NLP server unavailable

### 2. Ash-NLP Server (AI Processing)
**Repository:** https://github.com/The-Alphabet-Cartel/ash-nlp  
**Location:** Windows 11 Server (10.20.30.16:8881)  
**Technology Stack:** Python, PyTorch, Transformers, CUDA, FastAPI, Docker

**Core Functions:**
- **Advanced Text Analysis:** Deep learning models for nuanced crisis detection
- **Sentiment Analysis:** Understanding emotional context and urgency levels
- **Intent Recognition:** Identifying specific types of mental health crises
- **Severity Scoring:** Quantitative assessment of crisis urgency (0.0-1.0 scale)
- **Context Integration:** Considering message history and conversation patterns

**Technical Specifications:**
- **Models:** Fine-tuned transformer models for mental health text analysis
- **GPU Acceleration:** NVIDIA RTX 3050 for real-time inference
- **Processing Capacity:** 100+ messages per second with sub-2-second response times
- **Memory Management:** 64GB RAM for large model hosting and batch processing
- **API Design:** RESTful API with WebSocket support for real-time streaming

### 3. Ash-Dash Analytics Dashboard
**Repository:** https://github.com/The-Alphabet-Cartel/ash-dash  
**Location:** Windows 11 Server (10.20.30.16:8883)  
**Technology Stack:** Node.js, Express, Vue.js, Chart.js, WebSocket, Docker

**Core Functions:**
- **Real-time Monitoring:** Live system status and crisis alert tracking
- **Crisis Management:** Alert queue, response tracking, and escalation management
- **Performance Analytics:** Detection accuracy, response times, system health metrics
- **Team Coordination:** Crisis responder assignments, shift scheduling, communication tools
- **Historical Analysis:** Trends, patterns, and long-term community mental health insights

**Dashboard Features:**
- **Crisis Alert Queue:** Real-time list of active and pending crisis situations
- **System Health:** Status indicators for all services, performance metrics, error tracking
- **Analytics Views:** Charts and graphs for detection accuracy, response effectiveness
- **Team Management:** Crisis responder status, availability, response assignments
- **Mobile Responsive:** Accessible on mobile devices for crisis responders

### 4. Ash-Thrash Testing Suite
**Repository:** https://github.com/The-Alphabet-Cartel/ash-thrash  
**Location:** Windows 11 Server (10.20.30.16:8884)  
**Technology Stack:** Python, pytest, requests, pandas, Docker

**Core Functions:**
- **Comprehensive Testing:** 350-phrase test suite covering all crisis detection scenarios
- **Automated Validation:** Daily/weekly automated testing with result reporting
- **Performance Benchmarking:** System response times, accuracy metrics, resource usage
- **Regression Testing:** Ensure system improvements don't break existing functionality
- **Quality Assurance:** Validate detection accuracy before production deployments

**Testing Categories:**
- **Definite High Priority:** Explicit crisis language requiring immediate response
- **Definite Medium Priority:** Concerning language requiring timely follow-up
- **Definite Low Priority:** General mental health discussions for awareness
- **Maybe Categories:** Ambiguous language testing edge case handling
- **False Positive Testing:** Normal conversation that should not trigger alerts

---

## 🔄 Data Flow Architecture

### Message Processing Pipeline

```
Discord Message
       │
       ▼
┌─────────────────┐
│   Ash Bot       │
│   Receives      │
│   Message       │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│   Pre-filter    │
│   Keywords      │
│   Check         │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐     ┌─────────────────┐
│   Send to       │────▶│   NLP Server    │
│   NLP Server    │     │   Analysis      │
│   for Analysis  │     │   (GPU Accel)   │
└─────────┬───────┘     └─────────┬───────┘
          │                       │
          ▼                       ▼
┌─────────────────┐     ┌─────────────────┐
│   Receive       │◀────│   Return        │
│   Crisis Score  │     │   Analysis      │
│   & Analysis    │     │   Results       │
└─────────┬───────┘     └─────────────────┘
          │
          ▼
┌─────────────────┐
│   Evaluate      │
│   Crisis Level  │
│   & Generate    │
│   Alerts        │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐     ┌─────────────────┐
│   Send Alert    │────▶│   Dashboard     │
│   to Dashboard  │     │   Updates       │
│   & Discord     │     │   Alert Queue   │
└─────────┬───────┘     └─────────────