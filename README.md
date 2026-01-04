# Ash-Bot v5.0

**Crisis Detection Discord Bot for [The Alphabet Cartel](https://discord.gg/alphabetcartel) Discord Community**

[![Version](https://img.shields.io/badge/version-5.0.0-blue.svg)](https://github.com/the-alphabet-cartel/ash-bot)
[![License](https://img.shields.io/badge/license-GPL--3.0-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/)
[![Discord](https://img.shields.io/badge/Discord-Join%20Us-7289da?logo=discord&logoColor=white)](https://discord.gg/alphabetcartel)

---

## 🎯 Overview

Ash-Bot is a crisis detection Discord bot that monitors community messages for signs of mental health crises and alerts the Crisis Response Team (CRT) when intervention may be needed.

### Core Capabilities

| Feature | Description |
|---------|-------------|
| **Message Monitoring** | Monitors whitelisted channels for crisis indicators |
| **NLP Analysis** | Sends messages to [Ash-NLP](https://github.com/the-alphabet-cartel/ash-nlp) for semantic classification |
| **Crisis Alerting** | Notifies CRT via Discord embeds with severity-based routing |
| **Escalation Tracking** | Maintains user history to detect escalation patterns |
| **Ash Personality** | AI-powered conversational support via Claude API |

### Architecture

```
Discord Message → Ash-Bot → Ash-NLP API → Crisis Assessment
                     ↓              ↓
                  Redis ←──────────┘
                     ↓
              Alert Dispatch → CRT Notification
                     ↓
              Ash Response (if HIGH/CRITICAL)
```

---

## 🚀 Quick Start

### Prerequisites

- Docker Engine 24.0+
- Docker Compose v2.20+
- Discord Bot Token
- Access to Ash-NLP API

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/the-alphabet-cartel/ash-bot.git
   cd ash-bot
   ```

2. **Create secrets files**
   ```bash
   # Create secrets directory (if not exists)
   mkdir -p secrets
   
   # Add your Discord bot token
   echo "your_discord_bot_token" > secrets/discord_bot_token
   
   # Add Claude API key (for Ash personality)
   echo "your_claude_api_key" > secrets/claude_api_token
   
   # Set permissions
   chmod 600 secrets/*
   ```

3. **Create environment file**
   ```bash
   cp .env.template .env
   # Edit .env as needed
   ```

4. **Build and start**
   ```bash
   docker compose build
   docker compose up -d
   ```

5. **Verify it's running**
   ```bash
   docker ps
   docker exec ash-bot python --version
   ```

---

## 🛠️ Development

### Development Workflow

All development and testing happens inside Docker containers - never on bare metal.

```bash
# Build the container
docker compose build

# Start the container (stays running)
docker compose up -d

# Run tests
docker exec ash-bot python -m pytest tests/ -v

# Run specific test file
docker exec ash-bot python -m pytest tests/test_managers/test_config.py -v

# Run main.py
docker exec ash-bot python main.py

# Interactive Python shell
docker exec -it ash-bot python

# Bash shell access
docker exec -it ash-bot /bin/bash

# View logs
docker compose logs -f ash-bot

# Stop containers
docker compose down
```

### Source Code Mounting

The `docker-compose.override.yml` mounts source code as volumes, so:
- ✅ Python code changes are reflected immediately
- ✅ No rebuild needed for code changes
- ❌ **MUST rebuild** if `requirements.txt` or `Dockerfile` changes

```bash
# After changing requirements.txt or Dockerfile
docker compose down
docker compose build
docker compose up -d
```

### Project Structure

```
ash-bot/
├── src/
│   ├── __init__.py
│   ├── config/              # JSON configuration files
│   │   ├── default.json
│   │   ├── production.json
│   │   └── testing.json
│   └── managers/            # Resource managers
│       ├── __init__.py
│       ├── config_manager.py
│       ├── secrets_manager.py
│       ├── discord/         # Discord-related managers
│       ├── redis/           # Redis-related managers
│       ├── nlp/             # NLP client managers
│       └── ash/             # Ash personality managers
├── tests/                   # Test suite
├── docs/                    # Documentation
├── secrets/                 # Docker secrets (gitignored)
├── logs/                    # Log files (gitignored)
├── main.py                  # Entry point
├── Dockerfile
├── docker-compose.yml
├── docker-compose.override.yml  # Local dev overrides (gitignored)
├── requirements.txt
├── pytest.ini
└── .env                     # Environment variables (gitignored)
```

### Configuration

Configuration uses a layered approach:

1. **JSON Defaults** (`src/config/default.json`) - Base configuration
2. **Environment Overrides** (`src/config/{environment}.json`) - Environment-specific
3. **Environment Variables** (`.env`) - Runtime overrides

```bash
# Set environment
BOT_ENVIRONMENT=testing  # or production

# Override specific values
BOT_LOG_LEVEL=DEBUG
BOT_LOG_FORMAT=text
```

### Secrets Management

Sensitive credentials use Docker Secrets:

| Secret | Description |
|--------|-------------|
| `discord_bot_token` | Discord bot authentication token |
| `claude_api_token` | Claude API key for Ash personality |
| `discord_alert_token` | Webhook URL for system alerts |
| `redis_token` | Redis password (if enabled) |

See [secrets/README.md](secrets/README.md) for setup instructions.

---

## 📊 Severity Levels

| Severity | Store | Alert Channel | Ash Behavior |
|----------|-------|---------------|--------------|
| SAFE/NONE | ❌ | None | None |
| LOW | ✅ | None | None |
| MEDIUM | ✅ | #monitor-queue | Monitor silently |
| HIGH | ✅ | #crisis-response | Opener + session |
| CRITICAL | ✅ | #critical-response + DMs | Immediate intervention |

---

## 📚 Documentation

- [Discord Deployment Guide](docs/discord_deployment_guide.md) - **Start here for new deployments**
- [System Architecture](docs/architecture/system_architecture.md)
- [Clean Architecture Charter](docs/standards/clean_architecture_charter.md)
- [Development Roadmap](docs/v5.0/roadmap.md)
- [Ash-NLP API Reference](docs/api/reference.md)

---

## 🧪 Testing

```bash
# Run all tests
docker exec ash-bot python -m pytest tests/ -v

# Run with coverage
docker exec ash-bot python -m pytest tests/ -v --cov=src --cov-report=html

# Run specific test
docker exec ash-bot python -m pytest tests/test_managers/test_config.py::test_specific -v
```

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

- The Alphabet Cartel community for inspiration and support
- The Crisis Response Team for their dedication to community safety

---

**Built with care for chosen family** 🏳️‍🌈
