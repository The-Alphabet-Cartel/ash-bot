# Ash-Bot Secrets

**Repository**: https://github.com/the-alphabet-cartel/ash-bot  
**Community**: [The Alphabet Cartel](https://discord.gg/alphabetcartel) | [alphabetcartel.org](https://alphabetcartel.org)

---

## Overview

This directory contains sensitive credentials used by Ash-Bot. These files are:
- **NOT** committed to Git (via `.gitignore`)
- Mounted into Docker containers via Docker Secrets
- Read by the `SecretsManager` at runtime

---

## Secret Files

| File | Description | Required | Phase |
|------|-------------|----------|-------|
| `discord_bot_token` | Discord bot token | ✅ Required | Phase 1 |
| `claude_api_token` | Claude API key for Ash AI | ✅ Required | Phase 4 |
| `redis_token` | Redis password | Optional | Phase 2 |
| `discord_alert_token` | Discord webhook for system alerts | Optional | Phase 3 |

---

## Setup Instructions

### 1. Create the secrets directory

```bash
mkdir -p secrets
```

### 2. Add Discord Bot Token (Required)

Get your token from: https://discord.com/developers/applications

```bash
# Create the secret file (no file extension)
echo "your_discord_bot_token_here" > secrets/discord_bot_token

# Set secure permissions
chmod 600 secrets/discord_bot_token
```

### 3. Add Claude API Token (Required for Phase 4)

Get your API key from: https://console.anthropic.com/settings/keys

```bash
# Create the secret file (no file extension)
echo "sk-ant-your_claude_api_key_here" > secrets/claude_api_token

# Set secure permissions
chmod 600 secrets/claude_api_token
```

**Note**: The Claude API key enables the Ash AI conversational support feature. Without it, the "Talk to Ash" button will not appear on alerts.

### 4. Add Redis Password (Optional)

Only needed if your Redis instance requires authentication:

```bash
# Create the secret file (no file extension)
echo "your_redis_password_here" > secrets/redis_token

# Set secure permissions
chmod 600 secrets/redis_token
```

### 5. Add Discord Alert Webhook (Optional)

For system alerts (bot failures, startup notifications):

1. In Discord: Server Settings → Integrations → Webhooks → New Webhook
2. Copy the webhook URL
3. Create the secret:

```bash
# Create the webhook secret
echo "https://discord.com/api/webhooks/YOUR_WEBHOOK_ID/YOUR_WEBHOOK_TOKEN" > secrets/discord_alert_token

# Set secure permissions
chmod 600 secrets/discord_alert_token
```

### 6. Verify Setup

```bash
# Check files exist and have content
ls -la secrets/

# Verify permissions (should be 600 or -rw-------)
# Verify no trailing whitespace
cat -A secrets/discord_bot_token
```

---

## How It Works

### Docker Secrets (Production)

When running with Docker Compose, secrets are:
1. Defined in `docker-compose.yml`
2. Mounted to `/run/secrets/<name>` inside the container
3. Read by `SecretsManager` at startup

```yaml
# docker-compose.yml
secrets:
  discord_bot_token:
    file: ./secrets/discord_bot_token
  claude_api_token:
    file: ./secrets/claude_api_token

services:
  ash-bot:
    secrets:
      - discord_bot_token
      - claude_api_token
```

Inside the container, the secrets are available at:
```
/run/secrets/discord_bot_token
/run/secrets/claude_api_token
```

### Local Development

For local development without Docker:
1. `SecretsManager` checks `/run/secrets/` first
2. Falls back to `./secrets/` directory
3. Finally checks environment variables

```python
from src.managers import get_secret

# Get any secret
token = get_secret("discord_bot_token")

# Or use convenience methods
from src.managers import create_secrets_manager
secrets = create_secrets_manager()
discord_token = secrets.get_discord_bot_token()
claude_token = secrets.get_claude_api_token()
```

---

## Security Best Practices

### DO ✅

- Use `chmod 600` for secret files
- Keep secrets out of Git (check `.gitignore`)
- Rotate tokens periodically
- Use Docker Secrets in production
- Delete tokens you no longer use
- Use separate tokens for dev and prod

### DON'T ❌

- Commit secrets to Git
- Log or print secret values
- Share secrets in chat/email
- Use the same token for dev and prod
- Store secrets in environment files committed to Git
- Include quotes or extra whitespace in secret files

---

## File Format

Secret files should contain **only** the secret value:

**Correct** ✅
```
sk-ant-abcdef123456789
```

**Wrong** ❌
```
CLAUDE_API_KEY=sk-ant-abcdef123456789
```

**Wrong** ❌
```
"sk-ant-abcdef123456789"
```

**Wrong** ❌
```
sk-ant-abcdef123456789

```
(trailing newline can cause issues)

---

## Troubleshooting

### Secret Not Found

```
DEBUG: Secret 'discord_bot_token' not found
```

Check:
1. File exists: `ls -la secrets/discord_bot_token`
2. File has content: `cat secrets/discord_bot_token`
3. No extra whitespace: `cat -A secrets/discord_bot_token`

### Permission Denied

```
WARNING: Failed to read Docker secret 'discord_bot_token': Permission denied
```

Fix permissions:
```bash
chmod 600 secrets/discord_bot_token
```

### Token Not Working

1. Verify token at provider (Discord Developer Portal or Anthropic Console)
2. Check token has correct permissions/scopes
3. Token may have expired - generate a new one
4. Check for rate limiting or account issues

### Docker Secrets Not Mounting

Verify in docker-compose.yml:
```yaml
secrets:
  discord_bot_token:
    file: ./secrets/discord_bot_token  # Path relative to docker-compose.yml

services:
  ash-bot:
    secrets:
      - discord_bot_token  # Must be listed here
```

Check inside container:
```bash
docker exec ash-bot ls -la /run/secrets/
docker exec ash-bot cat /run/secrets/discord_bot_token
```

### Claude API Token Issues

If Ash AI isn't working:

1. Verify the token starts with `sk-ant-`
2. Check your Anthropic account has API credits
3. Verify the model (`claude-sonnet-4-20250514`) is available
4. Check logs for API error messages

```bash
# Check if token is loaded
docker exec ash-bot python -c "
from src.managers import create_secrets_manager
s = create_secrets_manager()
token = s.get_claude_api_token()
if token:
    print(f'Claude token loaded: {token[:15]}...')
else:
    print('No Claude token found')
"
```

---

## Testing Secrets

### Verify SecretsManager

```python
from src.managers import create_secrets_manager

secrets = create_secrets_manager()
print(secrets.get_status())
# Shows which secrets are available

# Check individual secrets (only show prefix!)
discord = secrets.get_discord_bot_token()
claude = secrets.get_claude_api_token()

if discord:
    print(f"Discord token: {discord[:10]}...")
if claude:
    print(f"Claude token: {claude[:15]}...")
```

### Verify in Docker

```bash
# Check secrets are mounted
docker exec ash-bot ls -la /run/secrets/

# Check SecretsManager can read them
docker exec ash-bot python -c "
from src.managers import create_secrets_manager
s = create_secrets_manager()
print(s.get_status())
"
```

---

## Required Secrets by Phase

| Phase | Required Secrets |
|-------|------------------|
| Phase 1 (Discord) | `discord_bot_token` |
| Phase 2 (Redis) | `redis_token` (if auth enabled) |
| Phase 3 (Alerting) | `discord_alert_token` (optional) |
| Phase 4 (Ash AI) | `claude_api_token` |

---

## Adding New Secrets

1. Create the secret file in `secrets/`
2. Add to `docker-compose.yml`:
   ```yaml
   secrets:
     new_secret:
       file: ./secrets/new_secret
   
   services:
     ash-bot:
       secrets:
         - new_secret
   ```
3. Add to `KNOWN_SECRETS` in `src/managers/secrets_manager.py`
4. Add convenience getter method if needed
5. Access in code:
   ```python
   from src.managers import get_secret
   value = get_secret("new_secret")
   ```

---

## Support

- **Discord**: [discord.gg/alphabetcartel](https://discord.gg/alphabetcartel)
- **GitHub Issues**: [github.com/the-alphabet-cartel/ash-bot/issues](https://github.com/the-alphabet-cartel/ash-bot/issues)

---

**Built with care for chosen family** 🏳️‍🌈
