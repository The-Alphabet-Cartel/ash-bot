# Ash-Bot v5.0

**Crisis Detection Discord Bot for [The Alphabet Cartel](https://discord.gg/alphabetcartel) LGBTQIA+ Community**

[![Version](https://img.shields.io/badge/version-5.0.0-blue.svg)](https://github.com/the-alphabet-cartel/ash-bot/releases)
[![License](https://img.shields.io/badge/license-GPL--3.0-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![Discord](https://img.shields.io/badge/Discord-Join%20Us-7289da?logo=discord&logoColor=white)](https://discord.gg/alphabetcartel)
[![Tests](https://img.shields.io/badge/tests-308%2B%20passing-brightgreen.svg)](#testing)

---

## 🎯 Overview

Ash-Bot is a comprehensive crisis detection and support system for Discord communities. It monitors messages for signs of mental health crises, alerts the Crisis Response Team (CRT), and provides compassionate AI-powered support through **Ash** — our caring AI companion.

### Mission

> **Protect our LGBTQIA+ community through early intervention, compassionate support, and ongoing care.**

### What Makes Ash-Bot Special

| Feature | Description |
|---------|-------------|
| 🤖 **Ash AI Companion** | Claude-powered conversational support with warmth and empathy |
| 🔍 **Smart Detection** | Multi-model NLP analysis via [Ash-NLP](https://github.com/the-alphabet-cartel/ash-nlp) |
| 🚨 **Intelligent Alerting** | Severity-based routing with beautiful Discord embeds |
| 🛡️ **Privacy First** | User opt-out system, minimal data retention |
| 📊 **CRT Tools** | Slash commands, session notes, response metrics |
| 💜 **Ongoing Care** | Automated follow-up check-ins after sessions |

---

## ✨ Features at a Glance

### For Community Members
- **Talk to Ash** — Compassionate AI support when you need someone to listen
- **Opt-Out Control** — `/ash optout` to control your interaction with Ash
- **Follow-Up Care** — Ash checks in 24 hours after conversations
- **Privacy Respected** — Your preferences are always honored

### For Crisis Response Team
- **Real-Time Alerts** — Severity-coded alerts with full context
- **One-Click Actions** — Acknowledge, Talk to Ash, View History buttons
- **Session Handoff** — Smoothly take over from Ash when needed
- **Documentation** — Add notes for continuity of care
- **Weekly Reports** — Response time metrics and trends
- **Slash Commands** — `/ash health`, `/ash stats`, `/ash notes`

### For Operators
- **Health API** — Kubernetes-ready liveness and readiness probes
- **Prometheus Metrics** — Full observability integration
- **Circuit Breakers** — Resilient external service handling
- **Auto-Cleanup** — Configurable data retention policies
- **Docker First** — Production-ready containerization

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           Ash-Bot v5.0 Architecture                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────┐    ┌─────────────────┐    ┌──────────────────────────┐   │
│  │   Discord    │───►│  DiscordManager │───►│   Message Processing     │   │
│  │   Gateway    │    │                 │    │   & Channel Filtering    │   │
│  └──────────────┘    └────────┬────────┘    └────────────┬─────────────┘   │
│                               │                          │                  │
│                               ▼                          ▼                  │
│                    ┌──────────────────┐       ┌──────────────────┐         │
│                    │ SlashCommandMgr  │       │  NLPClientManager │         │
│                    │ /ash commands    │       │  (circuit breaker)│         │
│                    └──────────────────┘       └─────────┬────────┘         │
│                                                         │                   │
│                                                         ▼                   │
│                                               ┌──────────────────┐          │
│                                               │     Ash-NLP      │          │
│                                               │   (External)     │          │
│                                               └─────────┬────────┘          │
│                                                         │                   │
│  ┌──────────────────────────────────────────────────────┘                   │
│  │                                                                          │
│  ▼                                                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         Alert System                                 │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌────────────┐  │   │
│  │  │  Cooldown   │─►│   Embed     │─►│   Alert     │─►│  Discord   │  │   │
│  │  │  Manager    │  │   Builder   │  │  Dispatcher │  │  Channels  │  │   │
│  │  └─────────────┘  └─────────────┘  └──────┬──────┘  └────────────┘  │   │
│  │                                           │                          │   │
│  │                              ┌────────────┴────────────┐             │   │
│  │                              ▼                         ▼             │   │
│  │                    ┌──────────────────┐     ┌──────────────────┐    │   │
│  │                    │  AutoInitiate    │     │ ResponseMetrics  │    │   │
│  │                    │  Manager         │     │ Manager          │    │   │
│  │                    └──────────────────┘     └──────────────────┘    │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                        Ash AI System                                 │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌────────────┐  │   │
│  │  │ Personality │─►│   Claude    │─►│   Session   │─►│  Follow-Up │  │   │
│  │  │  Manager    │  │   Client    │  │   Manager   │  │  Manager   │  │   │
│  │  └─────────────┘  └─────────────┘  └──────┬──────┘  └────────────┘  │   │
│  │                                           │                          │   │
│  │                              ┌────────────┴────────────┐             │   │
│  │                              ▼                         ▼             │   │
│  │                    ┌──────────────────┐     ┌──────────────────┐    │   │
│  │                    │    Handoff       │     │     Notes        │    │   │
│  │                    │    Manager       │     │    Manager       │    │   │
│  │                    └──────────────────┘     └──────────────────┘    │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                       Storage & Persistence                          │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌────────────┐  │   │
│  │  │   Redis     │◄─│UserHistory  │  │UserPrefs    │  │  Data      │  │   │
│  │  │  Manager    │  │  Manager    │  │  Manager    │  │ Retention  │  │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └────────────┘  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      Operations & Monitoring                         │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌────────────┐  │   │
│  │  │   Health    │─►│   Health    │  │   Metrics   │  │  Weekly    │  │   │
│  │  │   Manager   │  │   Server    │  │   Manager   │  │  Reports   │  │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └────────────┘  │   │
│  │         │              :30881                                        │   │
│  │         └──► /health, /health/ready, /health/detailed, /metrics      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- Docker Engine 24.0+
- Docker Compose v2.20+
- Discord Bot Token ([setup guide](docs/operations/discord_deployment_guide.md))
- Ash-NLP service running
- Claude API key (for Ash AI features)

### Installation

```bash
# Clone the repository
git clone https://github.com/the-alphabet-cartel/ash-bot.git
cd ash-bot

# Create secrets directory
mkdir -p secrets

# Add required secrets
echo "your_discord_bot_token" > secrets/discord_bot_token
echo "your_claude_api_key" > secrets/claude_api_token
chmod 600 secrets/*

# Configure environment
cp .env.template .env
# Edit .env with your channel IDs and settings

# Start the bot
docker compose up -d

# Verify it's running
curl http://localhost:30881/health
docker compose logs -f ash-bot
```

### Verify Installation

```bash
# Check health endpoint
curl http://localhost:30881/health
# Expected: {"status": "healthy", ...}

# Check readiness
curl http://localhost:30881/health/ready
# Expected: {"status": "ready", ...}

# Run tests
docker exec ash-bot python -m pytest tests/ -v
# Expected: 308+ tests passed
```

---

## 📋 Slash Commands

| Command | Description | Who Can Use |
|---------|-------------|-------------|
| `/ash status` | Check your opt-out status | Everyone |
| `/ash optout` | Opt out of Ash interaction | Everyone |
| `/ash optin` | Opt back in to Ash | Everyone |
| `/ash health` | Check bot system status | CRT Members |
| `/ash stats` | View response statistics | CRT Members |
| `/ash notes add` | Add notes about a user | CRT Members |
| `/ash notes view` | View notes about a user | CRT Members |

---

## 🚨 Severity Levels & Alert Routing

| Severity | Threshold | Alert Channel | CRT Ping | Ash Response |
|----------|-----------|---------------|----------|--------------|
| 🔴 **CRITICAL** | ≥ 0.85 | #crisis-response | ✅ Yes | Auto-initiate if unacknowledged |
| 🟠 **HIGH** | ≥ 0.70 | #crisis-response | ✅ Yes | "Talk to Ash" button |
| 🟡 **MEDIUM** | ≥ 0.50 | #crisis-monitor | ❌ No | Available on request |
| 🟢 **LOW** | ≥ 0.30 | ❌ None | ❌ No | ❌ No |
| ⚪ **SAFE** | < 0.30 | ❌ None | ❌ No | ❌ No |

---

## ⚙️ Configuration

### Key Environment Variables

```bash
# Core Settings
BOT_ENVIRONMENT=production          # production, testing
BOT_LOG_LEVEL=INFO                  # DEBUG, INFO, WARNING, ERROR

# Discord Channels
BOT_MONITORED_CHANNELS=123,456      # Channels to monitor
BOT_ALERT_CHANNEL_CRISIS=789        # HIGH/CRITICAL alerts
BOT_ALERT_CHANNEL_MONITOR=012       # MEDIUM alerts
BOT_CRT_ROLE_ID=345                 # Role to ping

# Features (all default to true)
BOT_ALERTING_ENABLED=true
BOT_AUTO_INITIATE_ENABLED=true
BOT_FOLLOWUP_ENABLED=true
BOT_SLASH_COMMANDS_ENABLED=true

# Data Retention
BOT_RETENTION_ALERT_METRICS_DAYS=90
BOT_RETENTION_SESSION_DATA_DAYS=30
BOT_RETENTION_HISTORY_DAYS=7
```

See [.env.template](.env.template) for complete configuration reference.

---

## 📈 Monitoring

### Health Endpoints

| Endpoint | Purpose | Use Case |
|----------|---------|----------|
| `GET /health` | Liveness probe | Kubernetes liveness |
| `GET /health/ready` | Readiness probe | Kubernetes readiness |
| `GET /health/detailed` | Full status | Debugging, dashboards |
| `GET /metrics` | Prometheus metrics | Monitoring systems |

### Key Metrics

```
# Message Processing
ash_messages_processed_total
ash_messages_analyzed_total{severity="..."}
ash_alerts_sent_total{severity="...", channel="..."}

# Ash AI Sessions
ash_sessions_total
ash_sessions_active
ash_session_duration_seconds

# Response Times
ash_response_time_seconds{type="acknowledge|contact|resolve"}

# System Health
ash_nlp_request_duration_seconds
ash_nlp_errors_total
ash_redis_operations_total
```

---

## 📊 Weekly Reports

Every Monday, Ash-Bot posts a weekly summary to the CRT channel:

```
╔════════════════════════════════════════════════════╗
║  📊 Weekly CRT Report                               ║
╠════════════════════════════════════════════════════╣
║  Alerts: 23 (🔴 2, 🟠 8, 🟡 13)                     ║
║  Avg Response: 4.2 minutes ✅                       ║
║  Ash Sessions: 15 (3 handed to CRT)                ║
║  Follow-ups Sent: 8 (62% response rate)            ║
║  Trend: ↓ 15% fewer alerts than last week          ║
╚════════════════════════════════════════════════════╝
```

---

## 🧪 Testing

```bash
# Run all tests
docker exec ash-bot python -m pytest tests/ -v

# Run specific phase tests
docker exec ash-bot python -m pytest tests/test_alerting/ -v
docker exec ash-bot python -m pytest tests/test_followup/ -v

# Run with coverage
docker exec ash-bot python -m pytest tests/ --cov=src --cov-report=html

# Quick smoke test
docker exec ash-bot python -m pytest tests/ -v --tb=short -q
```

**Test Coverage**: 308+ tests with 100% pass rate

---

## 📚 Documentation

### For Crisis Response Team
| Document | Description |
|----------|-------------|
| [Crisis Response Guide](docs/operations/crisis_response_guide.md) | **Start here!** Complete CRT operational guide |

### For Operators
| Document | Description |
|----------|-------------|
| [Discord Deployment Guide](docs/operations/discord_deployment_guide.md) | Bot setup and permissions |
| [Configuration Reference](docs/configuration.md) | All configuration options |
| [Troubleshooting Guide](docs/operations/troubleshooting.md) | Common issues and solutions |

### For Developers
| Document | Description |
|----------|-------------|
| [Clean Architecture Charter](docs/standards/clean_architecture_charter.md) | Code standards |
| [Phase Documentation](docs/v5.0/) | Detailed implementation docs |
| [Release Notes](RELEASE_NOTES.md) | Full changelog |

---

## 🔧 Operations

### Common Commands

```bash
# Start/Stop
docker compose up -d
docker compose down

# Logs
docker compose logs -f ash-bot

# Restart
docker compose restart ash-bot

# Rebuild
docker compose down && docker compose up --build -d

# Shell access
docker exec -it ash-bot /bin/bash
```

### Troubleshooting Quick Reference

| Issue | Check |
|-------|-------|
| Bot not connecting | `secrets/discord_bot_token` exists and is valid |
| No alerts | Channel IDs in `.env` are correct |
| NLP failures | Ash-NLP service is running |
| Redis errors | `docker compose logs ash-redis` |
| Ash not responding | Claude API key is valid |

---

## 🛣️ Development Phases

| Phase | Feature | Status |
|-------|---------|--------|
| 1 | Discord Gateway & Clean Architecture | ✅ Complete |
| 2 | Redis Storage & Message History | ✅ Complete |
| 3 | Alert Dispatching & Embeds | ✅ Complete |
| 4 | Ash AI Personality | ✅ Complete |
| 5 | Production Hardening | ✅ Complete |
| 6 | Health API & Probes | ✅ Complete |
| 7 | User Preferences & Auto-Initiate | ✅ Complete |
| 8 | Metrics & Reporting | ✅ Complete |
| 9 | CRT Workflow Enhancements | ✅ Complete |

---

## 🤝 Contributing

We welcome contributions! Please:

1. Read the [Clean Architecture Charter](docs/standards/clean_architecture_charter.md)
2. Follow the existing code patterns
3. Write tests for new functionality
4. Update documentation as needed
5. Submit a PR with a clear description

---

## 🏳️‍🌈 Community

**The Alphabet Cartel** is an LGBTQIA+ Discord community centered around gaming, political discourse, activism, and societal advocacy.

| | |
|---|---|
| 🌐 **Website** | [alphabetcartel.org](https://alphabetcartel.org) |
| 💬 **Discord** | [discord.gg/alphabetcartel](https://discord.gg/alphabetcartel) |
| 🐙 **GitHub** | [github.com/the-alphabet-cartel](https://github.com/the-alphabet-cartel) |

---

## 📄 License

This project is licensed under the GNU General Public License v3.0 — see [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

- **The Alphabet Cartel community** for inspiration and trust
- **Crisis Response Team** for dedication to community safety
- **Anthropic** for Claude, powering Ash's compassionate conversations
- **All contributors** who help make this project better

---

**Built with care for chosen family** 🏳️‍🌈

