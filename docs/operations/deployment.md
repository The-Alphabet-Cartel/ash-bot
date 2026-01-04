# Ash-Bot Deployment Guide

============================================================================
**Ash-Bot**: Crisis Detection Discord Bot for The Alphabet Cartel  
**The Alphabet Cartel** - https://discord.gg/alphabetcartel | alphabetcartel.org
============================================================================

**Document Version**: v1.1.0  
**Created**: 2026-01-04  
**Phase**: 5 - Production Hardening  
**Repository**: https://github.com/the-alphabet-cartel/ash-bot

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Secret Management](#secret-management)
4. [Initial Deployment](#initial-deployment)
5. [Updating Deployments](#updating-deployments)
6. [Rollback Procedures](#rollback-procedures)
7. [Production Checklist](#production-checklist)

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
curl http://localhost:30882/health
docker compose logs -f ash-bot
```

---

## Updating Deployments

```bash
git pull origin main
docker compose build
docker compose up -d
curl http://localhost:30882/health
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
- [ ] Correct guild and channel IDs configured
- [ ] Health checks passing
- [ ] Bot online in Discord
- [ ] Test message processed successfully

---

**Built with care for chosen family** 🏳️‍🌈
