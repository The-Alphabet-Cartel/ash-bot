# Ash-Bot Deployment Guide

============================================================================
**Ash-Bot**: Crisis Detection Discord Bot for The Alphabet Cartel  
**The Alphabet Cartel** - https://discord.gg/alphabetcartel | alphabetcartel.org
============================================================================

**Document Version**: v1.2.0  
**Created**: 2026-01-04  
**Updated**: 2026-01-05  
**Repository**: https://github.com/the-alphabet-cartel/ash-bot

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [User/Group Configuration](#usergroup-configuration)
4. [Secret Management](#secret-management)
5. [Initial Deployment](#initial-deployment)
6. [Updating Deployments](#updating-deployments)
7. [Rollback Procedures](#rollback-procedures)
8. [Production Checklist](#production-checklist)

---

## Prerequisites

### Hardware Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| CPU | 2 cores | 4+ cores |
| RAM | 2 GB | 4+ GB |
| Storage | 10 GB | 20+ GB |

### Software Requirements

| Software | Minimum Version | Purpose |
|----------|-----------------|---------|
| Docker Engine | 24.0+ | Container runtime |
| Docker Compose | 2.20+ | Service orchestration |
| Git | 2.0+ | Source control |

### Discord Requirements

1. Discord Application created at https://discord.com/developers
2. Bot Token with required permissions
3. Privileged Intents enabled (MESSAGE CONTENT, SERVER MEMBERS)

---

## Environment Setup

### 1. Clone Repository

```bash
git clone https://github.com/the-alphabet-cartel/ash-bot.git
cd ash-bot
git checkout main
```

### 2. Create Environment File

```bash
cp .env.template .env
nano .env
```

### 3. Configure Discord Channels

Edit `config/discord/channels.json` with your channel and role IDs.

### 4. Create Docker Network

```bash
docker network create ash-network
```

---

## User/Group Configuration

Ash-Bot supports LinuxServer.io-style PUID/PGID environment variables for managing file permissions. This is especially useful when running on NAS systems or shared storage.

### Why This Matters

When a container creates files (like logs), those files are owned by the user ID running inside the container. If this doesn't match your host user, you may encounter permission issues when accessing these files from the host.

### Find Your User/Group IDs

```bash
# On Linux/macOS, run:
id

# Output example:
# uid=1000(bubba) gid=1000(bubba) groups=1000(bubba),998(docker)
```

### Configure PUID/PGID

**Option 1: In `.env` file (Recommended)**

Edit your `.env` file:

```bash
# Match your host user
PUID=1000
PGID=1000
```

**Option 2: In `docker-compose.yml`**

Edit the environment section:

```yaml
environment:
  - PUID=1000
  - PGID=1000
```

**Option 3: Command line**

```bash
PUID=1000 PGID=1000 docker compose up -d
```

### Verify Configuration

When the container starts, you'll see the PUID/PGID in the logs:

```
[entrypoint] INFO: ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[entrypoint] INFO:   🤖 Ash-Bot Container Starting
[entrypoint] INFO: ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[entrypoint] INFO:   PUID: 1000
[entrypoint] INFO:   PGID: 1000
[entrypoint] INFO: ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Common Scenarios

| Scenario | PUID | PGID | Notes |
|----------|------|------|-------|
| Default Linux user | 1000 | 1000 | Most desktop Linux installs |
| Synology DSM | Varies | Varies | Use `id` in SSH session |
| TrueNAS | Often 568 | 568 | `apps` user |
| Unraid | 99 | 100 | `nobody:users` |
| macOS | 501 | 20 | First user account |

---

## Secret Management

### Create Secrets

```bash
mkdir -p secrets

echo "YOUR_DISCORD_BOT_TOKEN" > secrets/discord_bot_token
echo "YOUR_CLAUDE_API_KEY" > secrets/claude_api_token
echo "YOUR_REDIS_PASSWORD" > secrets/redis_token

chmod 600 secrets/*
```

---

## Initial Deployment

### Deploy

```bash
docker compose build
docker compose up -d
```

### Verify

```bash
docker compose ps
curl http://localhost:30881/health
docker compose logs -f ash-bot
```

---

## Updating Deployments

```bash
git pull origin main
docker compose build
docker compose up -d
curl http://localhost:30881/health
```

---

## Rollback Procedures

```bash
docker compose down
git checkout PREVIOUS_VERSION
docker compose up -d --build
```

---

## Production Checklist

- [ ] All secrets configured with proper permissions
- [ ] PUID/PGID configured to match host user
- [ ] Correct guild and channel IDs configured
- [ ] Health checks passing
- [ ] Bot online in Discord
- [ ] Test message processed successfully
- [ ] Log files have correct ownership

---

**Built with care for chosen family** 🏳️‍🌈
