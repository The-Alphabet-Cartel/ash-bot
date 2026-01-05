<!--
============================================================================
Ash-Bot: Crisis Detection Discord Bot
The Alphabet Cartel - https://discord.gg/alphabetcartel | alphabetcartel.org
============================================================================

MISSION - NEVER TO BE VIOLATED:
    Monitor  → Send messages to Ash-NLP for crisis classification
    Alert    → Notify Crisis Response Team via embeds when crisis detected
    Track    → Maintain user history for escalation pattern detection
    Protect  → Safeguard our LGBTQIA+ community through early intervention

============================================================================
Developer Guide - Setup, Standards, and Contributing
----------------------------------------------------------------------------
FILE VERSION: v5.0-6-3.0-1
LAST MODIFIED: 2026-01-04
PHASE: Phase 6 - Final Testing & Documentation
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-bot
============================================================================
-->

# Ash-Bot Development Guide

---

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Development Environment Setup](#development-environment-setup)
4. [Project Structure](#project-structure)
5. [Architecture Principles](#architecture-principles)
6. [Coding Standards](#coding-standards)
7. [Testing](#testing)
8. [Git Workflow](#git-workflow)
9. [Common Development Tasks](#common-development-tasks)
10. [Troubleshooting](#troubleshooting)

---

## Overview

This guide covers everything needed to contribute to Ash-Bot development.

### Technology Stack

| Component | Technology | Version |
|-----------|------------|---------|
| Runtime | Python | 3.11+ |
| Discord Library | discord.py | 2.3+ |
| HTTP Client | httpx | 0.26+ |
| Redis Client | redis-py | 5.0+ |
| Testing | pytest | 7.4+ |
| Containerization | Docker | 24.0+ |

---

## Prerequisites

### Required Software

- **Docker Desktop** (Windows/Mac) or **Docker Engine** (Linux)
- **Git** for version control
- **Text Editor/IDE** (VS Code, Zed, PyCharm)

### Access Requirements

- GitHub account with access to the-alphabet-cartel organization
- Discord Developer account with test bot token
- Claude API key (optional, for Ash AI development)

---

## Development Environment Setup

### Step 1: Clone Repository

```bash
git clone https://github.com/the-alphabet-cartel/ash-bot.git
cd ash-bot
```

### Step 2: Create Secrets

```bash
mkdir -p secrets
echo "your_test_bot_token" > secrets/discord_bot_token
echo "your_claude_api_key" > secrets/claude_api_token
chmod 600 secrets/*
```

### Step 3: Configure Environment

```bash
cp .env.template .env
```

**Minimum `.env` for development:**

```bash
BOT_ENVIRONMENT=testing
BOT_LOG_LEVEL=DEBUG
BOT_LOG_FORMAT=text
```

### Step 4: Start Development Environment

```bash
docker compose up -d --build
docker compose logs -f ash-bot
```

### Step 5: Verify Setup

```bash
docker ps
curl http://localhost:30881/health
docker exec ash-bot python -m pytest tests/ -v
```

---

## Project Structure

```
ash-bot/
├── src/                          # Source code
│   ├── api/                      # Health/metrics endpoints
│   ├── config/                   # JSON configuration
│   ├── managers/                 # Business logic managers
│   │   ├── alerting/             # Alert dispatch system
│   │   ├── ash/                  # Ash AI personality
│   │   ├── discord/              # Discord integration
│   │   ├── health/               # Health monitoring
│   │   ├── metrics/              # Prometheus metrics
│   │   ├── nlp/                  # NLP client
│   │   └── storage/              # Redis storage
│   ├── models/                   # Data models
│   ├── prompts/                  # Ash character prompts
│   ├── utils/                    # Utilities
│   └── views/                    # Discord UI components
├── tests/                        # Test suite
├── docs/                         # Documentation
├── secrets/                      # Docker secrets (git-ignored)
└── docker-compose.yml
```

---

## Architecture Principles

All code must follow the [Clean Architecture Charter](standards/clean_architecture_charter.md).

### Rule #1: Factory Function Pattern

```python
# ✅ CORRECT
from src.managers import create_config_manager
config = create_config_manager(environment="testing")

# ❌ WRONG
config = ConfigManager(environment="testing")
```

### Rule #2: Dependency Injection

```python
class AlertDispatcher:
    def __init__(self, config_manager, embed_builder, cooldown_manager):
        self._config = config_manager
        self._embed_builder = embed_builder
        self._cooldown = cooldown_manager
```

### Rule #5: Resilient Validation

```python
def get_cooldown(self) -> int:
    try:
        return int(self._config.get("alerting", "cooldown_seconds"))
    except (ValueError, TypeError):
        logger.warning("Invalid cooldown, using default: 60")
        return 60
```

---

## Coding Standards

### File Headers

Every Python file must include the standard header:

```python
"""
============================================================================
Ash-Bot: Crisis Detection Discord Bot
The Alphabet Cartel - https://discord.gg/alphabetcartel | alphabetcartel.org
============================================================================

MISSION - NEVER TO BE VIOLATED:
    Monitor  → Send messages to Ash-NLP for crisis classification
    Alert    → Notify Crisis Response Team via embeds when crisis detected
    Track    → Maintain user history for escalation pattern detection
    Protect  → Safeguard our LGBTQIA+ community through early intervention

============================================================================
{File Description}
----------------------------------------------------------------------------
FILE VERSION: v5.0-X-X.X-X
LAST MODIFIED: YYYY-MM-DD
PHASE: Phase X - Description
CLEAN ARCHITECTURE: Compliant
Repository: https://github.com/the-alphabet-cartel/ash-bot
============================================================================
"""
```

### Naming Conventions

| Element | Convention | Example |
|---------|------------|---------|
| Files | snake_case | `alert_dispatcher.py` |
| Classes | PascalCase | `AlertDispatcher` |
| Functions | snake_case | `dispatch_alert()` |
| Constants | UPPER_SNAKE | `MAX_RETRIES` |

### Type Hints

```python
async def analyze_message(
    self,
    message: str,
    user_id: str,
    history: Optional[List[Dict[str, Any]]] = None,
) -> AnalysisResult:
    ...
```

---

## Testing

### Running Tests

```bash
# All tests
docker exec ash-bot python -m pytest tests/ -v

# Specific file
docker exec ash-bot python -m pytest tests/test_alerting/test_embed_builder.py -v

# With coverage
docker exec ash-bot python -m pytest tests/ --cov=src --cov-report=html

# Integration tests
docker exec ash-bot python -m pytest tests/integration/ -v
```

### Test Structure

```python
class TestAlertDispatcher:
    @pytest.fixture
    def mock_config(self):
        config = MagicMock()
        config.get.return_value = 60
        return config

    @pytest.mark.asyncio
    async def test_dispatch_high_severity(self, mock_config):
        dispatcher = create_alert_dispatcher(config_manager=mock_config)
        result = await dispatcher.dispatch(severity="high", user_id="123")
        assert result.dispatched is True
```

---

## Git Workflow

### Branch Naming

```
feature/description    # New features
bugfix/description     # Bug fixes
docs/description       # Documentation
```

### Commit Messages

```
feat(alerting): add cooldown manager
fix(discord): handle reconnection
docs(readme): update quick start
```

### Pull Request Process

1. Create branch from `main`
2. Make changes following standards
3. Write tests for new functionality
4. Run tests locally
5. Create PR with description
6. Address review feedback
7. Squash and merge when approved

---

## Common Development Tasks

### Adding a New Manager

1. Create file with proper header
2. Implement class with dependency injection
3. Add factory function
4. Export in `__init__.py`
5. Write tests

### Adding Configuration

1. Add to `src/config/default.json`
2. Add to `.env.template`
3. Access via `config.get("section", "key")`

---

## Troubleshooting

### Container Won't Start

```bash
docker compose logs ash-bot
docker compose down -v
docker compose up -d --build
```

### Tests Failing

```bash
docker exec ash-bot python -m pytest tests/ -v --tb=long
```

### Configuration Not Loading

```bash
docker exec ash-bot python -c "
from src.managers import create_config_manager
c = create_config_manager()
print(c.to_dict())
"
```

---

## Support

- **Discord**: [discord.gg/alphabetcartel](https://discord.gg/alphabetcartel)
- **GitHub Issues**: [github.com/the-alphabet-cartel/ash-bot/issues](https://github.com/the-alphabet-cartel/ash-bot/issues)

---

**Built with care for chosen family** 🏳️‍🌈
