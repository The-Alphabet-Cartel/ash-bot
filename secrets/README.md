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

| File | Description | Required |
|------|-------------|----------|
| `claude_api_key` | Claude API key | Required |
| `discord_bot_token` | Discord bot token | Required |
| `redis` | Redis Password | Required |
| `discord_alert_webhook` | Discord webhook for system alerts | Optional |

---

## Setup Instructions

### 1. Create the secrets directory

```bash
mkdir -p secrets
```

### 2. Add Claude API Key

Get your token from: https://platform.claude.com/settings/keys

```bash
# Create the secret file (no file extension)
echo "claude_api_your_token_here" > secrets/claude_api_key

# Set secure permissions
chmod 600 secrets/claude_api_key
```

### 3. Add Discord Bot Token

Get your token from: https://discord.com/developers/applications

```bash
# Create the secret file (no file extension)
echo "discord_bot_your_token_here" > secrets/discord_bot_token

# Set secure permissions
chmod 600 secrets/discord_bot_token
```

### 4. Add Redis Password

```bash
# Create the secret file (no file extension)
echo "redis_password_here" > secrets/redis

# Set secure permissions
chmod 600 secrets/redis
```

### 5. Add Discord Alert Webhook (Optional)

For system alerts (bot failures, startup notifications):

1. In Discord: Server Settings → Integrations → Webhooks → New Webhook
2. Copy the webhook URL
3. Create the secret:

```bash
# Create the webhook secret
echo "https://discord.com/api/webhooks/YOUR_WEBHOOK_ID/YOUR_WEBHOOK_TOKEN" > secrets/discord_alert_webhook

# Set secure permissions
chmod 600 secrets/discord_alert_webhook
```

**Important**: 
- The file should contain ONLY the token, no quotes or extra whitespace
- Do NOT add a file extension (not `.txt`, not `.token`)

### 6. Verify Setup

```bash
# Check file exists and has content
cat secrets/discord_alert_webhook

# Verify permissions (should be 600 or rw-------)
ls -la secrets/
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

services:
  ash-bot:
    secrets:
      - discord_bot_token
```

Inside the container, the secret is available at:
```
/run/secrets/discord_bot_token
```

### Local Development

For local development without Docker:
1. `SecretsManager` checks `/run/secrets/` first
2. Falls back to `./secrets/` directory
3. Finally checks environment variables

```python
from src.managers import get_secret

token = get_secret("discord_bot_token")
```

---

## Security Best Practices

### DO ✅

- Use `chmod 600` for secret files
- Keep secrets out of Git (check `.gitignore`)
- Rotate tokens periodically
- Use Docker Secrets in production
- Delete tokens you no longer use

### DON'T ❌

- Commit secrets to Git
- Log or print secret values
- Share secrets in chat/email
- Use the same token for dev and prod
- Store secrets in environment files committed to Git

---

## File Format

Secret files should contain **only** the secret value:

**Correct** ✅
```
abcdef123456789
```

**Wrong** ❌
```
DISCORD_BOT_TOKEN=abcdef123456789
```

**Wrong** ❌
```
"abcdef123456789"
```

**Wrong** ❌
```
abcdef123456789

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

1. Verify token at provider
2. Check token has correct permissions
3. Token may have expired - generate a new one

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

---

## Testing Secrets

### Verify SecretsManager

```python
from src.managers import create_secrets_manager

secrets = create_secrets_manager()
print(secrets.get_status())
# Shows which secrets are available

token = secrets.get_discord_bot_token()
if token:
    print(f"Token loaded: {token[:10]}...")  # Only show prefix!
else:
    print("No token found")
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
4. Access in code:
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
