# Ash-Bot Discord Deployment Guide

============================================================================
**Ash-Bot**: Crisis Detection Discord Bot for The Alphabet Cartel  
**The Alphabet Cartel** - https://discord.gg/alphabetcartel | https://alphabetcartel.org
============================================================================

**Document Version**: v1.0.0  
**Last Updated**: 2026-01-04  
**Repository**: https://github.com/the-alphabet-cartel/ash-bot

---

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Discord Developer Portal Setup](#discord-developer-portal-setup)
   - [Create Application](#step-1-create-application)
   - [Configure Bot User](#step-2-configure-bot-user)
   - [Set Privileged Intents](#step-3-set-privileged-intents)
   - [Configure OAuth2](#step-4-configure-oauth2)
   - [Generate Invite Link](#step-5-generate-invite-link)
4. [Discord Server Setup](#discord-server-setup)
   - [Channel Structure](#channel-structure)
   - [Role Configuration](#role-configuration)
   - [Bot Permissions](#bot-permissions)
5. [Environment Configuration](#environment-configuration)
6. [Verification Checklist](#verification-checklist)
7. [Troubleshooting](#troubleshooting)
8. [Updating Bot Scope](#updating-bot-scope)

---

## Overview

This guide walks through the complete process of setting up Ash-Bot on Discord's Developer Portal and configuring your Discord server to work with the bot.

### What Ash-Bot Needs

| Requirement | Purpose |
|-------------|---------|
| Message Content Intent | Read message content for crisis analysis |
| Server Members Intent | Access member information for alerts |
| Presence Intent | (Optional) Track user status |
| Send Messages | Post alerts to crisis channels |
| Embed Links | Create rich embed alerts |
| Read Message History | Context for escalation detection |
| Manage Messages | (Optional) Pin important alerts |
| Use External Emojis | Display severity indicators |

---

## Prerequisites

Before starting, ensure you have:

- [ ] Discord account with a verified email
- [ ] Administrator access to your target Discord server
- [ ] Access to Discord Developer Portal: https://discord.com/developers/applications

---

## Discord Developer Portal Setup

### Step 1: Create Application

1. Navigate to **Discord Developer Portal**:
   ```
   https://discord.com/developers/applications
   ```

2. Click **"New Application"** (top right)

3. Enter application details:
   - **Name**: `Ash-Bot` (or your preferred name)
   - Accept the Developer Terms of Service
   - Click **"Create"**

4. On the **General Information** page:
   - **Description**: `Crisis Detection Discord Bot for community mental health support`
   - **App Icon**: Upload your bot avatar (optional but recommended)
   - Click **"Save Changes"**

5. **Record your Application ID** (you'll need this later):
   ```
   Application ID: ___________________________
   ```

---

### Step 2: Configure Bot User

1. In the left sidebar, click **"Bot"**

2. Click **"Add Bot"** → Confirm **"Yes, do it!"**

3. Configure bot settings:

   **Username & Avatar**:
   - Set bot username (can differ from application name)
   - Upload bot avatar

   **Token** (CRITICAL - Keep Secret!):
   - Click **"Reset Token"** → Confirm
   - **Copy the token immediately** - you won't see it again!
   - Store securely in `secrets/discord_bot_token`:
     ```bash
     echo "YOUR_BOT_TOKEN_HERE" > secrets/discord_bot_token
     chmod 600 secrets/discord_bot_token
     ```

   **Public Bot**:
   - **Disable** "Public Bot" toggle (recommended for private communities)
   - This prevents others from inviting your bot

   **Requires OAuth2 Code Grant**:
   - Leave **disabled** (not needed for bot-only functionality)

4. Click **"Save Changes"**

---

### Step 3: Set Privileged Intents

Ash-Bot requires **Privileged Gateway Intents** to function properly.

1. Still on the **"Bot"** page, scroll to **Privileged Gateway Intents**

2. **Enable the following intents**:

   | Intent | Toggle | Why Required |
   |--------|--------|--------------|
   | **Presence Intent** | ⬜ Optional | Track online/offline status |
   | **Server Members Intent** | ✅ Required | Access member details for alerts |
   | **Message Content Intent** | ✅ Required | Read messages for crisis analysis |

   **⚠️ CRITICAL**: Message Content Intent is **required** for Ash-Bot to analyze messages!

3. Click **"Save Changes"**

**Note**: For bots in 100+ servers, you must apply for intent verification. For private community bots, this is automatic.

---

### Step 4: Configure OAuth2

1. In the left sidebar, click **"OAuth2"** → **"General"**

2. Under **Redirects**, add (optional, for future web dashboard):
   ```
   https://your-domain.com/callback
   ```

3. Click **"OAuth2"** → **"URL Generator"**

4. **Select Scopes**:
   
   | Scope | Select | Purpose |
   |-------|--------|---------|
   | `bot` | ✅ | Core bot functionality |
   | `applications.commands` | ✅ | Slash commands (/userhistory) |

5. **Select Bot Permissions**:

   **Text Permissions** (Required):
   | Permission | Select | Purpose |
   |------------|--------|---------|
   | Send Messages | ✅ | Post alerts |
   | Send Messages in Threads | ✅ | Thread support |
   | Embed Links | ✅ | Rich embed alerts |
   | Attach Files | ⬜ | Optional attachments |
   | Read Message History | ✅ | Context retrieval |
   | Use External Emojis | ✅ | Severity indicators |
   | Add Reactions | ⬜ | Optional reactions |

   **General Permissions** (Required):
   | Permission | Select | Purpose |
   |------------|--------|---------|
   | View Channels | ✅ | See monitored channels |
   | Manage Messages | ⬜ | Optional: pin alerts |

   **Advanced Permissions** (Optional):
   | Permission | Select | Purpose |
   |------------|--------|---------|
   | Mention @everyone | ⬜ | Generally not needed |
   | Manage Roles | ⬜ | Only if auto-assigning roles |

6. **Record the Permissions Integer**:
   ```
   Permissions Integer: ___________________________
   ```
   
   Recommended minimum: `274877991936`
   
   This includes: View Channels, Send Messages, Send Messages in Threads, Embed Links, Read Message History, Use External Emojis

---

### Step 5: Generate Invite Link

1. After selecting scopes and permissions, the **Generated URL** appears at the bottom

2. Copy the URL. It will look like:
   ```
   https://discord.com/api/oauth2/authorize?client_id=YOUR_APP_ID&permissions=274877991936&scope=bot%20applications.commands
   ```

3. **Test the invite link**:
   - Open in browser
   - Select your target server
   - Review permissions
   - Click **"Authorize"**
   - Complete CAPTCHA if prompted

4. **Verify bot joined**:
   - Check your server's member list
   - Bot should appear as offline (until code is running)

---

## Discord Server Setup

### Channel Structure

Create the following channels for Ash-Bot alerts:

#### Alert Channels

| Channel | Purpose | Who Can See |
|---------|---------|-------------|
| `#crisis-monitor` | MEDIUM severity alerts | CRT + Moderators |
| `#crisis-response` | HIGH severity alerts | CRT only |
| `#crisis-critical` | CRITICAL severity alerts | CRT only |

**Recommended Category Structure**:
```
📋 CRISIS RESPONSE (Category)
├── #crisis-monitor      (MEDIUM alerts)
├── #crisis-response     (HIGH alerts)  
├── #crisis-critical     (CRITICAL alerts)
└── #crt-discussion      (Team coordination)
```

#### Monitored Channels

Identify which channels Ash-Bot should monitor for crisis content:

```
Example channels to monitor:
- #venting
- #mental-health
- #support
- #general (optional, high volume)
```

**Record Channel IDs**:

To get a channel ID:
1. Enable Developer Mode: User Settings → Advanced → Developer Mode
2. Right-click channel → "Copy Channel ID"

| Channel | ID |
|---------|-----|
| #crisis-monitor | `___________________________` |
| #crisis-response | `___________________________` |
| #crisis-critical | `___________________________` |
| Monitored Channel 1 | `___________________________` |
| Monitored Channel 2 | `___________________________` |

---

### Role Configuration

#### Crisis Response Team (CRT) Role

Create a role for your crisis response team:

1. Server Settings → Roles → Create Role

2. Configure the role:
   - **Name**: `Crisis Response Team` or `CRT`
   - **Color**: Red (recommended for visibility)
   - **Display separately**: ✅ Yes
   - **Allow anyone to @mention**: ✅ Yes (for emergency pings)

3. **Assign permissions**:
   - View Channels (grant access to alert channels)
   - No special permissions needed otherwise

4. **Record Role ID**:
   - Right-click role → "Copy Role ID"
   ```
   CRT Role ID: ___________________________
   ```

5. **Assign to team members**:
   - Add the role to all crisis response volunteers

---

### Bot Permissions

Ensure Ash-Bot has proper channel access:

#### Alert Channels

For each alert channel (`#crisis-monitor`, `#crisis-response`, `#crisis-critical`):

1. Channel Settings → Permissions → Add Role/Member
2. Add **Ash-Bot** with these permissions:

| Permission | Allow |
|------------|-------|
| View Channel | ✅ |
| Send Messages | ✅ |
| Embed Links | ✅ |
| Read Message History | ✅ |
| Use External Emojis | ✅ |

#### Monitored Channels

For each channel Ash-Bot should monitor:

1. Channel Settings → Permissions
2. Verify Ash-Bot can:

| Permission | Allow |
|------------|-------|
| View Channel | ✅ |
| Read Message History | ✅ |

**Note**: Ash-Bot does NOT need Send Messages in monitored channels (it only reads).

---

## Environment Configuration

After Discord setup, configure Ash-Bot's environment variables.

### Required Variables

Add to your `.env` file or set in your environment:

```bash
# =============================================================
# Discord Configuration
# =============================================================

# Bot token (from Developer Portal → Bot → Token)
# ⚠️ Store in secrets/discord_bot_token instead of .env!

# Guild/Server ID (optional, for single-server deployment)
BOT_DISCORD_GUILD_ID=YOUR_GUILD_ID_HERE

# =============================================================
# Channel Configuration  
# =============================================================

# Alert channels (by severity)
BOT_ALERT_CHANNEL_MONITOR=CHANNEL_ID_FOR_MEDIUM
BOT_ALERT_CHANNEL_CRISIS=CHANNEL_ID_FOR_HIGH
BOT_ALERT_CHANNEL_CRITICAL=CHANNEL_ID_FOR_CRITICAL

# Channels to monitor (comma-separated list)
BOT_MONITORED_CHANNELS=["CHANNEL_ID_1","CHANNEL_ID_2","CHANNEL_ID_3"]

# =============================================================
# Alerting Configuration
# =============================================================

# Crisis Response Team role ID
BOT_CRT_ROLE_ID=YOUR_CRT_ROLE_ID_HERE

# Alerting settings
BOT_ALERTING_ENABLED=true
BOT_ALERT_MIN_SEVERITY=medium
BOT_ALERT_COOLDOWN=300
```

### Secrets Configuration

Store sensitive values in Docker secrets:

```bash
# Create secrets directory
mkdir -p secrets

# Store bot token (from Step 2)
echo "YOUR_BOT_TOKEN" > secrets/discord_bot_token
chmod 600 secrets/discord_bot_token

# Store alert webhook (optional, for system notifications)
echo "YOUR_WEBHOOK_URL" > secrets/discord_alert_token
chmod 600 secrets/discord_alert_token
```

---

## Verification Checklist

Use this checklist to verify your setup:

### Discord Developer Portal
- [ ] Application created
- [ ] Bot user added
- [ ] Bot token saved to `secrets/discord_bot_token`
- [ ] Message Content Intent enabled
- [ ] Server Members Intent enabled
- [ ] OAuth2 scopes selected (bot, applications.commands)
- [ ] Bot permissions configured
- [ ] Invite link generated and used

### Discord Server
- [ ] Bot appears in member list
- [ ] `#crisis-monitor` channel created
- [ ] `#crisis-response` channel created
- [ ] `#crisis-critical` channel created
- [ ] CRT role created and assigned to team
- [ ] Bot has View Channel on alert channels
- [ ] Bot has Send Messages on alert channels
- [ ] Bot has View Channel on monitored channels
- [ ] Channel IDs recorded

### Environment Configuration
- [ ] `BOT_DISCORD_GUILD_ID` set (if single-server)
- [ ] `BOT_ALERT_CHANNEL_MONITOR` set
- [ ] `BOT_ALERT_CHANNEL_CRISIS` set
- [ ] `BOT_ALERT_CHANNEL_CRITICAL` set
- [ ] `BOT_MONITORED_CHANNELS` set
- [ ] `BOT_CRT_ROLE_ID` set
- [ ] `secrets/discord_bot_token` exists with valid token

### Startup Verification
- [ ] Bot comes online when started
- [ ] Bot logs "Connected to Discord" message
- [ ] Bot logs monitored channel count
- [ ] No permission errors in logs

---

## Troubleshooting

### Bot Won't Come Online

**Symptom**: Bot shows offline in Discord after starting

**Solutions**:
1. Verify token is correct:
   ```bash
   cat secrets/discord_bot_token
   ```
2. Check Docker logs:
   ```bash
   docker logs ash-bot
   ```
3. Regenerate token if compromised (Developer Portal → Bot → Reset Token)

---

### "Missing Access" Errors

**Symptom**: Logs show `discord.errors.Forbidden: Missing Access`

**Solutions**:
1. Verify bot is in the server
2. Check channel permissions (bot needs View Channel)
3. Re-invite bot with correct permissions

---

### "Missing Intent" Errors

**Symptom**: `discord.errors.PrivilegedIntentsRequired`

**Solutions**:
1. Go to Developer Portal → Bot → Privileged Gateway Intents
2. Enable **Message Content Intent**
3. Enable **Server Members Intent**
4. Restart the bot

---

### Bot Can't Read Messages

**Symptom**: Bot online but not detecting messages

**Solutions**:
1. Verify Message Content Intent is enabled
2. Check `BOT_MONITORED_CHANNELS` includes target channels
3. Verify bot has View Channel permission
4. Check channel ID format (should be integers as strings)

---

### Alerts Not Posting

**Symptom**: Crisis detected but no alert appears

**Solutions**:
1. Verify alert channel IDs are correct
2. Check bot has Send Messages permission in alert channels
3. Verify `BOT_ALERTING_ENABLED=true`
4. Check cooldown hasn't blocked the alert

---

### CRT Not Being Pinged

**Symptom**: Alerts appear but no @CRT mention

**Solutions**:
1. Verify `BOT_CRT_ROLE_ID` is set correctly
2. Role must have "Allow anyone to @mention" enabled
3. Only HIGH and CRITICAL alerts ping CRT (MEDIUM does not)

---

## Updating Bot Scope

When you need to add new permissions or features:

### Adding New Permissions

1. Go to Developer Portal → OAuth2 → URL Generator
2. Select new permissions needed
3. Generate new invite link
4. **Kick the bot** from your server
5. Re-invite using new link
6. Verify permissions applied

**Alternative** (without re-invite):
- Server Settings → Integrations → Ash-Bot → Manage
- Manually adjust permissions

### Adding New Intents

1. Developer Portal → Bot → Privileged Gateway Intents
2. Enable new intent(s)
3. Update bot code to request new intent
4. Restart bot

**Note**: Changing intents doesn't require re-inviting the bot.

### Common Scope Changes

| Feature | Requires |
|---------|----------|
| Slash commands | `applications.commands` scope |
| DM users | No extra permissions (bots can DM by default) |
| Create threads | `Create Public Threads` permission |
| Pin messages | `Manage Messages` permission |
| Add reactions | `Add Reactions` permission |
| Manage roles | `Manage Roles` permission + role hierarchy |

---

## Quick Reference Card

### Developer Portal URLs

| Page | URL |
|------|-----|
| Applications | https://discord.com/developers/applications |
| Your App | https://discord.com/developers/applications/YOUR_APP_ID |
| Bot Settings | https://discord.com/developers/applications/YOUR_APP_ID/bot |
| OAuth2 | https://discord.com/developers/applications/YOUR_APP_ID/oauth2 |

### Minimum Required Intents

```python
intents = discord.Intents.default()
intents.message_content = True  # Required
intents.members = True          # Required
intents.presences = False       # Optional
```

### Minimum Required Permissions

```
Permissions Integer: 274877991936

Includes:
- View Channels
- Send Messages
- Send Messages in Threads
- Embed Links
- Read Message History
- Use External Emojis
```

### Invite Link Template

```
https://discord.com/api/oauth2/authorize?client_id=YOUR_APP_ID&permissions=274877991936&scope=bot%20applications.commands
```

---

## Support

- **Discord**: [discord.gg/alphabetcartel](https://discord.gg/alphabetcartel)
- **GitHub Issues**: [github.com/the-alphabet-cartel/ash-bot/issues](https://github.com/the-alphabet-cartel/ash-bot/issues)
- **Website**: [alphabetcartel.org](https://alphabetcartel.org)

---

**Built with care for chosen family** 🏳️‍🌈
