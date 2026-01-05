# Ash-Bot v5.0

**Crisis Detection Discord Bot for [The Alphabet Cartel](https://discord.gg/alphabetcartel) Discord Community**

[![Version](https://img.shields.io/badge/version-5.0.0-blue.svg)](https://github.com/the-alphabet-cartel/ash-bot)
[![License](https://img.shields.io/badge/license-GPL--3.0-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/)
[![Discord](https://img.shields.io/badge/Discord-Join%20Us-7289da?logo=discord&logoColor=white)](https://discord.gg/alphabetcartel)

---

## 🎯 Overview

Ash-Bot is a crisis detection Discord bot that monitors community messages for signs of mental health crises and alerts the Crisis Response Team (CRT) when intervention may be needed. The bot leverages multi-model NLP analysis to provide accurate crisis detection while minimizing false positives.

### Mission

> **Protect our LGBTQIA+ community through early intervention and compassionate support.**

### Core Capabilities

| Feature | Description |
|---------|-------------|
| **Message Monitoring** | Monitors whitelisted channels for crisis indicators |
| **NLP Analysis** | Multi-model ensemble (BART, Sentiment, Irony, Emotions) via [Ash-NLP](https://github.com/the-alphabet-cartel/ash-nlp) |
| **Crisis Alerting** | Severity-based routing with Discord embeds and CRT pinging |
| **Escalation Tracking** | Redis-backed user history for pattern detection |
| **Ash AI Support** | Claude-powered conversational crisis support |
| **Production Hardening** | Circuit breakers, retry logic, health endpoints, and metrics |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              Ash-Bot v5.0                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  Discord Gateway ──────► DiscordManager ──────► Message Processing      │
│                               │                        │                │
│                               ▼                        ▼                │
│                     ChannelConfigManager        NLPClientManager        │
│                     (monitored channels)       (circuit breaker)        │
│                                                       │                 │
│                                                       ▼                 │
│                                               ┌───────────────┐         │
│                                               │   Ash-NLP     │         │
│                                               │  (External)   │         │
│                                               └───────────────┘         │
│                                                       │                 │
│  ┌─────────────────────────────────────────────────────┘                │
│  │                                                                      │
│  ▼                                                                      │
│  UserHistoryManager ◄────► RedisManager ◄────► ash-redis               │
│  (escalation tracking)     (with retry)                                 │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    Alert Dispatching (Phase 3)                   │   │
│  │  CooldownManager ─► EmbedBuilder ─► AlertDispatcher ─► Discord   │   │
│  │                                            │                     │   │
│  │                                   AlertButtons (Ack/Talk to Ash) │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    Ash AI Support (Phase 4)                      │   │
│  │  AshPersonalityManager ─► ClaudeClientManager ─► AshSessionMgr   │   │
│  │                           (circuit breaker)                      │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                 Production Hardening (Phase 5)                   │   │
│  │  HealthManager ─► HealthServer (:30882) ─► /health, /metrics     │   │
│  │  MetricsManager ─► Prometheus-format export                      │   │
│  │  CircuitBreaker + RetryLogic for all external services           │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## ✨ Features

### Phase 1: Discord Connectivity
- Secure bot token management via Docker Secrets
- Configurable channel monitoring
- Clean Architecture compliance

### Phase 2: NLP Integration & History
- Ash-NLP API integration with circuit breaker
- Redis-backed user message history
- Severity-based storage (LOW+ only)

### Phase 3: Alert Dispatching
- Severity-based channel routing (MEDIUM → monitor, HIGH/CRITICAL → crisis)
- CRT role pinging for HIGH/CRITICAL
- Interactive embed buttons (Acknowledge, Talk to Ash)
- User-based cooldown to prevent alert spam

### Phase 4: Ash AI Personality
- Claude API integration for conversational support
- Severity-appropriate welcome messages
- Session management with timeout cleanup
- DM-based private conversations

### Phase 5: Production Hardening
- Circuit breakers on all external services
- Retry logic with exponential backoff
- HTTP health endpoints for Kubernetes
- Prometheus-format metrics export
- Comprehensive operational documentation

---

## 🚀 Quick Start

### Prerequisites

- Docker Engine 24.0+
- Docker Compose v2.20+
- Discord Bot Token ([setup guide](docs/discord_deployment_guide.md))
- Access to Ash-NLP service
- (Optional) Claude API key for Ash AI

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/the-alphabet-cartel/ash-bot.git
   cd ash-bot
   ```

2. **Create secrets**
   ```bash
   mkdir -p secrets
   
   # Required: Discord bot token
   echo "your_discord_bot_token" > secrets/discord_bot_token
   
   # Optional: Claude API key (enables Ash AI)
   echo "your_claude_api_key" > secrets/claude_api_token
   
   # Optional: Redis password
   echo "your_redis_password" > secrets/redis_token
   
   chmod 600 secrets/*
   ```

3. **Configure environment**
   ```bash
   cp .env.template .env
   # Edit .env with your channel IDs and settings
   ```

4. **Start the bot**
   ```bash
   docker compose up -d
   ```

5. **Verify health**
   ```bash
   # Check container status
   docker ps
   
   # Check health endpoint
   curl http://localhost:30882/health
   
   # View logs
   docker compose logs -f ash-bot
   ```

---

## ⚙️ Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `BOT_ENVIRONMENT` | `production` | Environment: production, testing |
| `BOT_LOG_LEVEL` | `INFO` | Log level: DEBUG, INFO, WARNING, ERROR |
| `BOT_LOG_FORMAT` | `json` | Log format: json, text |
| `BOT_MONITORED_CHANNELS` | - | Comma-separated channel IDs to monitor |
| `BOT_ALERT_CHANNEL_CRISIS` | - | Channel ID for HIGH/CRITICAL alerts |
| `BOT_ALERT_CHANNEL_MONITOR` | - | Channel ID for MEDIUM alerts |
| `BOT_CRT_ROLE_ID` | - | Role ID to ping for HIGH/CRITICAL |

### JSON Configuration

Configuration files are in `src/config/`:
- `default.json` - Base configuration with defaults
- `production.json` - Production environment overrides
- `testing.json` - Testing environment overrides

See [Configuration Reference](docs/configuration.md) for full documentation.

---

## 📊 Severity Levels & Alert Routing

| Severity | Score Range | Storage | Alert Channel | CRT Ping | Ash AI |
|----------|-------------|---------|---------------|----------|--------|
| **CRITICAL** | ≥ 0.85 | ✅ | #crisis-response | ✅ | Auto-initiate |
| **HIGH** | ≥ 0.70 | ✅ | #crisis-response | ✅ | "Talk to Ash" button |
| **MEDIUM** | ≥ 0.50 | ✅ | #crisis-monitor | ❌ | ❌ |
| **LOW** | ≥ 0.30 | ✅ | ❌ | ❌ | ❌ |
| **SAFE** | < 0.30 | ❌ | ❌ | ❌ | ❌ |

---

## 📈 Monitoring

### Health Endpoints

| Endpoint | Purpose | Response |
|----------|---------|----------|
| `GET /health` | Liveness probe | Always 200 |
| `GET /healthz` | Liveness (k8s alias) | Always 200 |
| `GET /health/ready` | Readiness probe | 200/503 based on Discord |
| `GET /readyz` | Readiness (k8s alias) | 200/503 |
| `GET /health/detailed` | Full component status | JSON with all components |
| `GET /metrics` | Prometheus metrics | Text format |

### Key Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `messages_processed_total` | Counter | Total messages processed |
| `messages_analyzed_total` | Counter | Messages by severity |
| `alerts_sent_total` | Counter | Alerts by severity/channel |
| `ash_sessions_total` | Counter | Total Ash AI sessions |
| `ash_sessions_active` | Gauge | Currently active sessions |
| `nlp_request_duration_seconds` | Histogram | NLP API latency |
| `nlp_errors_total` | Counter | NLP API errors |

### Docker Health Check

```bash
# Check container health
docker inspect ash-bot --format='{{.State.Health.Status}}'

# View health check logs
docker inspect ash-bot --format='{{json .State.Health}}'
```

---

## 🔧 Operations

### Common Commands

```bash
# Start services
docker compose up -d

# Stop services
docker compose down

# View logs
docker compose logs -f ash-bot

# Restart bot only
docker compose restart ash-bot

# Rebuild after code changes
docker compose build
docker compose up -d

# Enter container shell
docker exec -it ash-bot /bin/bash

# Run tests
docker exec ash-bot python -m pytest tests/ -v
```

### Troubleshooting

| Issue | Likely Cause | Solution |
|-------|--------------|----------|
| Bot not connecting | Invalid token | Check `secrets/discord_bot_token` |
| No alerts sent | Channel IDs wrong | Verify `BOT_ALERT_CHANNEL_*` in `.env` |
| NLP failures | Service down | Check `docker compose logs ash-nlp` |
| Redis errors | Connection refused | Verify Redis is running |

See [Troubleshooting Guide](docs/operations/troubleshooting.md) for detailed solutions.

---

## 📚 Documentation

### For Crisis Response Team

| Document | Description |
|----------|-------------|
| [CRT Guide](docs/crt_guide.md) | **Start here!** Complete guide for Crisis Response Team members |

### For Developers & Operators

| Document | Description |
|----------|-------------|
| [Development Guide](docs/development.md) | Developer setup and coding standards |
| [Discord Deployment Guide](docs/discord_deployment_guide.md) | Setting up Discord bot and permissions |
| [System Architecture](docs/architecture/system_architecture.md) | Technical architecture details |
| [Configuration Reference](docs/configuration.md) | All configuration options |
| [Operations Runbook](docs/operations/runbook.md) | Day-to-day operations |
| [Troubleshooting](docs/operations/troubleshooting.md) | Common issues and solutions |
| [Deployment Guide](docs/operations/deployment.md) | Production deployment steps |
| [Clean Architecture Charter](docs/standards/clean_architecture_charter.md) | Development standards |
| [Ash-NLP API Reference](docs/api/reference.md) | NLP API documentation |

---

## 🧪 Testing

```bash
# Run all tests
docker exec ash-bot python -m pytest tests/ -v

# Run integration tests
docker exec ash-bot python -m pytest tests/integration/ -v

# Run with coverage
docker exec ash-bot python -m pytest tests/ --cov=src --cov-report=html

# Run specific test
docker exec ash-bot python -m pytest tests/test_alerting/test_embed_builder.py -v
```

---

## 🤝 Contributing

We welcome contributions from the community! Please follow our development standards:

1. Read the [Clean Architecture Charter](docs/standards/clean_architecture_charter.md)
2. Use factory functions for all managers
3. Include proper file version headers
4. Write tests for new functionality
5. Update documentation as needed

---

## 🏳️‍🌈 Community

**The Alphabet Cartel** is an LGBTQIA+ Discord community centered around gaming, political discourse, activism, and societal advocacy.

- 🌐 **Website**: [alphabetcartel.org](https://alphabetcartel.org)
- 💬 **Discord**: [discord.gg/alphabetcartel](https://discord.gg/alphabetcartel)
- 🐙 **GitHub**: [github.com/the-alphabet-cartel](https://github.com/the-alphabet-cartel)

---

## 📄 License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- The Alphabet Cartel community for inspiration and unwavering support
- The Crisis Response Team for their dedication to community safety
- All contributors who help make this project better

---

**Built with care for chosen family** 🏳️‍🌈
