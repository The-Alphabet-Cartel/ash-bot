# Ash Bot v3.0 Troubleshooting Guide

**Comprehensive troubleshooting guide for Ash Bot crisis response system**

---

## 🚨 Emergency Procedures

### Critical System Failure

If Ash Bot is completely unresponsive during a crisis situation:

1. **Immediate Action**: Manually handle any active crisis situations
2. **Team Alert**: Notify crisis team of system outage
3. **Backup Procedures**: Activate manual crisis monitoring protocols
4. **System Check**: Follow diagnostic steps below
5. **Escalation**: Contact technical support if needed

### Partial System Failure

If some features are working but crisis detection is impaired:

1. **Verify Discord connection**: Check if bot is online and responding
2. **Test basic commands**: Try `/help` or `/crisis_stats`
3. **Check NLP service**: Verify connection to ash-nlp service
4. **Enable verbose logging**: Increase log level for debugging
5. **Monitor manually**: Increase human monitoring until resolved

---

## 🔍 Diagnostic Commands

### System Health Checks

```bash
# Check overall system health
curl http://10.20.30.253:8882/health

# Verify all services are running
docker-compose ps

# Check recent logs
docker-compose logs --tail=50 ash-bot

# Verify NLP service connection
curl http://10.20.30.253:8881/health
```

### Discord Commands for Testing

```
/crisis_stats          # Verify bot is responding to slash commands
/test_mention message:test # Test conversation system
/keyword_stats         # Check keyword system status
/conversation_stats    # Verify conversation system functionality
```

---

## 🚫 Crisis Detection Issues

### Issue: Bot Not Detecting Crisis Messages

**Symptoms:**
- Obvious crisis messages not triggering alerts
- No response from bot to crisis indicators
- Crisis team not receiving notifications

**Diagnostic Steps:**

1. **Verify bot permissions**:
```bash
# Check if bot can read messages in channel
# Bot needs "Read Messages" and "Send Messages" permissions
```

2. **Test keyword detection**:
```bash
# Use test command with known crisis phrase
/test_mention message:I want to end it all
```

3. **Check NLP service**:
```bash
# Verify NLP service is responding
curl http://10.20.30.253:8881/health

# Check NLP service logs
docker-compose logs ash-nlp
```

4. **Review message content**:
- Check if message exceeds length limits (2000 characters)
- Verify message contains detectable crisis language
- Check for special characters or encoding issues

**Solutions:**

#### 1. Restart Detection System
```bash
# Restart bot container
docker-compose restart ash-bot

# Check startup logs
docker-compose logs -f ash-bot
```

#### 2. Verify Configuration
```bash
# Check environment variables
docker-compose exec ash-bot env | grep BOT_

# Verify NLP service URL
echo $BOT_NLP_SERVICE_URL
```

#### 3. Reset Keyword System
```bash
# Clear keyword cache and reload
docker-compose exec ash-bot python -c "
from bot.utils.keyword_detector import KeywordDetector
detector = KeywordDetector()
detector.reload_keywords()
print('Keywords reloaded successfully')
"
```

#### 4. Manual NLP Test
```bash
# Test NLP service directly
curl -X POST http://10.20.30.253:8881/analyze \
  -H "Content-Type: application/json" \
  -d '{"message": "I want to end it all"}'
```

---

### Issue: Too Many False Positives

**Symptoms:**
- Bot alerting on gaming discussions
- Creative writing triggering crisis alerts
- Casual expressions being flagged as crisis

**Diagnostic Steps:**

```bash
# Review recent false positive reports
/learning_stats

# Check context detection performance
curl http://10.20.30.253:8882/stats | jq '.detection_system'

# Analyze recent keyword matches
docker-compose logs ash-bot | grep "keyword_match" | tail -20
```

**Solutions:**

#### 1. Report False Positives
```bash
# Use Discord command to report each false positive
/report_false_positive 
  message_link:https://discord.com/channels/server/channel/message
  detected_level:Medium Crisis
  correct_level:No Crisis
  context:Gaming discussion about defeating boss
```

#### 2. Adjust Context Detection
```bash
# Check context detection settings
docker-compose exec ash-bot python -c "
from bot.utils.context_analyzer import ContextAnalyzer
analyzer = ContextAnalyzer()
print(f'Gaming patterns: {len(analyzer.gaming_patterns)}')
print(f'Creative patterns: {len(analyzer.creative_patterns)}')
"
```

#### 3. Remove Problematic Keywords
```bash
# Identify and remove keywords causing false positives
/list_keywords crisis_level:Medium Crisis
/remove_keyword crisis_level:Medium Crisis keyword:problematic_phrase
```

#### 4. Enable Enhanced Context Detection
```bash
# Update environment configuration
# Add to .env file:
BOT_ENHANCED_CONTEXT_DETECTION=true
BOT_GAMING_CONTEXT_WEIGHT=0.2
BOT_CREATIVE_CONTEXT_WEIGHT=0.3

# Restart bot
docker-compose restart ash-bot
```

---

### Issue: Missing Crisis Situations (False Negatives)

**Symptoms:**
- Team noticing crises that bot didn't detect
- Crisis situations reaching team through other channels
- Users reporting bot didn't respond to crisis

**Investigation Steps:**

1. **Review specific missed cases**:
```bash
# Check if messages were processed at all
docker-compose logs ash-bot | grep "user_id:123456789"
```

2. **Test similar phrases**:
```bash
# Test variations of missed crisis language
/test_mention message:similar_crisis_phrase
```

3. **Check keyword coverage**:
```bash
# Review current keyword patterns
/list_keywords crisis_level:High Crisis
/keyword_stats
```

**Solutions:**

#### 1. Report False Negatives
```bash
# Report each missed crisis for learning
/report_false_negative
  message_link:discord_message_link
  correct_level:High Crisis
  context:User expressing suicidal ideation in indirect language
```

#### 2. Expand Keyword Coverage
```bash
# Add keywords for missed crisis patterns
/add_keyword crisis_level:High Crisis keyword:new_crisis_phrase
```

#### 3. Improve NLP Detection
```bash
# Check NLP model performance
curl http://10.20.30.253:8881/learning_statistics

# Trigger NLP model update if needed
curl -X POST http://10.20.30.253:8881/api/retrain \
  -H "Authorization: Bearer $NLP_API_KEY"
```

#### 4. Lower Detection Thresholds
```bash
# Temporarily lower thresholds for testing
# Edit .env file:
BOT_HIGH_CRISIS_THRESHOLD=0.75    # Was 0.8
BOT_MEDIUM_CRISIS_THRESHOLD=0.55  # Was 0.6
BOT_LOW_CRISIS_THRESHOLD=0.35     # Was 0.4

# Restart bot
docker-compose restart ash-bot
```

---

## 💬 Conversation System Issues

### Issue: Conversation System Not Working

**Symptoms:**
- Bot not responding to mentions
- Conversation context not maintained
- Natural starters not triggering responses

**Diagnostic Steps:**

```bash
# Check conversation system status
/conversation_stats

# Test mention system
/test_mention message:@Ash can you help me

# Review conversation handler logs
docker-compose logs ash-bot | grep "conversation_handler"
```

**Solutions:**

#### 1. Verify Conversation Configuration
```bash
# Check conversation settings
docker-compose exec ash-bot env | grep BOT_CONVERSATION

# Required settings:
BOT_CONVERSATION_REQUIRES_MENTION=true
BOT_CONVERSATION_SETUP_INSTRUCTIONS=true
BOT_CONVERSATION_ALLOW_STARTERS=true
```

#### 2. Restart Conversation Handler
```bash
# Restart bot to reload conversation system
docker-compose restart ash-bot

# Check conversation handler initialization
docker-compose logs ash-bot | grep "conversation_handler initialized"
```

#### 3. Test Natural Triggers
```bash
# Test various conversation starters
/test_mention message:hey ash can you help
/test_mention message:I need to talk
/test_mention message:ash what should I do
```

#### 4. Check Active Conversations
```bash
# View currently active conversations
/active_conversations

# Clear stuck conversations if needed
docker-compose exec ash-bot python -c "
from bot.handlers.conversation_handler import ConversationHandler
handler = ConversationHandler(None, None)
handler.cleanup_expired_conversations()
print('Expired conversations cleaned up')
"
```

---

### Issue: Conversations Timing Out Too Quickly

**Symptoms:**
- Users complaining conversations end abruptly
- Context lost during longer conversations
- Bot not recognizing follow-up messages

**Solutions:**

#### 1. Extend Conversation Timeout
```bash
# Increase conversation timeout
# Edit .env file:
BOT_CONVERSATION_TIMEOUT_MINUTES=10  # Was 5

# Restart bot
docker-compose restart ash-bot
```

#### 2. Add More Trigger Phrases
```bash
# Expand trigger phrase list
# Edit .env file:
BOT_CONVERSATION_TRIGGER_PHRASES=ash,hey ash,@ash,can you help,I need help

# Restart bot
docker-compose restart ash-bot
```

#### 3. Enable Conversation Extensions
```bash
# Allow conversations to be extended
# Add to .env file:
BOT_CONVERSATION_ALLOW_EXTENSIONS=true
BOT_CONVERSATION_EXTENSION_PHRASES=continue,keep talking,still here

# Restart bot
docker-compose restart ash-bot
```

---

## 🚨 Alert System Issues

### Issue: Crisis Team Not Receiving Alerts

**Symptoms:**
- High crisis situations not pinging team
- Staff DMs not being sent
- Crisis channel not receiving notifications

**Diagnostic Steps:**

```bash
# Check alert configuration
docker-compose exec ash-bot env | grep BOT_CRISIS

# Verify Discord IDs are correct
echo "Crisis Channel: $BOT_CRISIS_RESPONSE_CHANNEL_ID"
echo "Crisis Role: $BOT_CRISIS_RESPONSE_ROLE_ID"
echo "Staff User: $BOT_STAFF_PING_USER"
```

**Solutions:**

#### 1. Verify Discord Configuration
```bash
# Check if bot has permission to mention role
# Bot needs "Mention Everyone" permission or specific role mention permission

# Verify channel exists and bot has access
# Check if crisis response channel ID is correct
```

#### 2. Test Alert System
```bash
# Trigger test alert
/test_mention message:I want to kill myself

# Check if alerts were sent
docker-compose logs ash-bot | grep "crisis_alert_sent"
```

#### 3. Fix Permissions Issues
```bash
# Bot needs these permissions in crisis channel:
# - Send Messages
# - Mention @everyone, @here, and All Roles
# - Read Message History
# - Embed Links
```

#### 4. Verify Role and User IDs
```bash
# Get Discord IDs for verification
# Use Discord Developer Mode to copy IDs
# Right-click on channel/role/user -> Copy ID

# Update .env file with correct IDs
BOT_CRISIS_RESPONSE_CHANNEL_ID=correct_channel_id
BOT_CRISIS_RESPONSE_ROLE_ID=correct_role_id
BOT_STAFF_PING_USER=correct_user_id
```

---

### Issue: Alert Spam or Duplicate Alerts

**Symptoms:**
- Multiple alerts for same crisis message
- Team getting overwhelmed with notifications
- Duplicate DMs to staff members

**Solutions:**

#### 1. Enable Alert Deduplication
```bash
# Add deduplication settings to .env
BOT_ALERT_DEDUPLICATION=true
BOT_ALERT_COOLDOWN_SECONDS=300  # 5 minutes between alerts for same user

# Restart bot
docker-compose restart ash-bot
```

#### 2. Adjust Alert Thresholds
```bash
# Raise thresholds to reduce alert volume
BOT_HIGH_CRISIS_THRESHOLD=0.85    # Was 0.8
BOT_MEDIUM_CRISIS_THRESHOLD=0.70  # Was 0.6

# Restart bot
docker-compose restart ash-bot
```

#### 3. Implement Alert Rate Limiting
```bash
# Limit alerts per time period
BOT_MAX_ALERTS_PER_HOUR=10
BOT_MAX_ALERTS_PER_USER_PER_DAY=3

# Restart bot
docker-compose restart ash-bot
```

---

## 🐳 Docker & Infrastructure Issues

### Issue: Container Startup Problems

**Symptoms:**
- Ash bot container fails to start
- Container exits immediately after startup
- Health checks failing

**Diagnostic Steps:**

```bash
# Check container status
docker-compose ps

# View startup logs
docker-compose logs ash-bot

# Check resource usage
docker stats --no-stream

# Verify dependencies
docker-compose logs ash-nlp
```

**Solutions:**

#### 1. Check Resource Constraints
```bash
# Verify system resources
free -h  # Check available memory
df -h    # Check disk space

# Increase container memory if needed
# Edit docker-compose.yml:
services:
  ash-bot:
    mem_limit: 512m  # Increase if needed
```

#### 2. Fix Environment Configuration
```bash
# Check for missing environment variables
docker-compose exec ash-bot env | grep BOT_ | sort

# Verify required variables are set:
# BOT_DISCORD_TOKEN
# BOT_NLP_SERVICE_URL
# BOT_CRISIS_RESPONSE_CHANNEL_ID
# BOT_CRISIS_RESPONSE_ROLE_ID
```

#### 3. Resolve Dependency Issues
```bash
# Ensure NLP service starts first
# Edit docker-compose.yml:
services:
  ash-bot:
    depends_on:
      - ash-nlp
    restart: unless-stopped
```

#### 4. Fix Permission Issues
```bash
# Check file permissions
ls -la data/
chmod 755 data/
chmod 644 data/*.json

# Ensure Docker has access to required directories
```

---

### Issue: High Memory Usage

**Symptoms:**
- Container using excessive memory
- System running out of memory
- Performance degradation

**Solutions:**

#### 1. Monitor Memory Usage
```bash
# Check current usage
docker stats ash-bot --no-stream

# Monitor over time
docker stats ash-bot
```

#### 2. Optimize Configuration
```bash
# Reduce keyword cache size
# Edit .env:
BOT_KEYWORD_CACHE_SIZE=1000  # Reduce if needed

# Limit concurrent processing
BOT_MAX_CONCURRENT_ANALYSES=3  # Reduce from default 5
```

#### 3. Enable Memory Limits
```bash
# Set container memory limits
# Edit docker-compose.yml:
services:
  ash-bot:
    mem_limit: 300m
    mem_reservation: 200m
```

#### 4. Restart Periodically
```bash
# Add scheduled restart for memory cleanup
# Add to crontab:
0 4 * * * docker-compose restart ash-bot
```

---

### Issue: Network Connectivity Problems

**Symptoms:**
- Cannot connect to NLP service
- Discord API timeouts
- External service failures

**Diagnostic Steps:**

```bash
# Test connectivity to NLP service
docker-compose exec ash-bot ping ash-nlp

# Check network configuration
docker network ls
docker network inspect ash_default

# Test external connectivity
docker-compose exec ash-bot ping discord.com
```

**Solutions:**

#### 1. Fix Docker Network Issues
```bash
# Recreate Docker network
docker-compose down
docker network prune
docker-compose up -d
```

#### 2. Check Firewall Rules
```bash
# Ensure required ports are open
# Port 8881 (ash-nlp service)
# Port 443 (Discord API)
# Port 80/443 (External services)
```

#### 3. Configure DNS Resolution
```bash
# Add DNS configuration to docker-compose.yml
services:
  ash-bot:
    dns:
      - 8.8.8.8
      - 8.8.4.4
```

---

## 📊 Performance Issues

### Issue: Slow Crisis Detection Response

**Symptoms:**
- Long delays between message and crisis response
- Team complaints about slow alerts
- High response times in metrics

**Diagnostic Steps:**

```bash
# Check response time metrics
curl http://10.20.30.253:8882/stats | jq '.performance'

# Monitor processing times
docker-compose logs ash-bot | grep "processing_time_ms"

# Check system load
top
iostat 1 5
```

**Solutions:**

#### 1. Optimize NLP Integration
```bash
# Reduce NLP timeout
BOT_NLP_TIMEOUT=3  # Reduce from 10 seconds
BOT_NLP_RETRY_ATTEMPTS=1  # Reduce retries

# Enable faster fallback
BOT_ENABLE_FAST_FALLBACK=true
```

#### 2. Improve System Performance
```bash
# Increase system resources
# Consider upgrading server specifications
# Add SSD storage if using HDD
# Increase available RAM
```

#### 3. Enable Performance Caching
```bash
# Enable result caching
BOT_ENABLE_RESPONSE_CACHE=true
BOT_CACHE_TTL_SECONDS=30

# Cache similar message patterns
BOT_ENABLE_PATTERN_CACHE=true
```

#### 4. Optimize Database Operations
```bash
# Clean up old data
docker-compose exec ash-bot python -c "
import os
from pathlib import Path

# Clean old log files
log_files = Path('./logs').glob('*.log.*')
for log_file in log_files:
    if log_file.stat().st_mtime < time.time() - 604800:  # 1 week
        log_file.unlink()
"
```

---

## 🔧 Configuration Issues

### Issue: Environment Variables Not Loading

**Symptoms:**
- Bot using default configuration values
- Features not enabling despite configuration
- Errors about missing configuration

**Solutions:**

#### 1. Verify .env File Format
```bash
# Check .env file syntax
cat .env

# Ensure no spaces around = signs
# Correct: BOT_DISCORD_TOKEN=your_token
# Incorrect: BOT_DISCORD_TOKEN = your_token
```

#### 2. Restart with Fresh Environment
```bash
# Reload environment variables
docker-compose down
docker-compose up -d

# Check if variables are loaded
docker-compose exec ash-bot env | grep BOT_
```

#### 3. Use Docker Secrets (Production)
```bash
# For production, use Docker secrets instead of .env
echo "your_discord_token" | docker secret create discord_token -
echo "your_nlp_url" | docker secret create nlp_service_url -

# Update docker-compose.yml to use secrets
```

---

### Issue: Slash Commands Not Registering

**Symptoms:**
- /commands not appearing in Discord
- "Application did not respond" errors
- Commands working intermittently

**Solutions:**

#### 1. Force Command Registration
```bash
# Restart bot to re-register commands
docker-compose restart ash-bot

# Check command registration logs
docker-compose logs ash-bot | grep "command.*registered"
```

#### 2. Verify Bot Permissions
```bash
# Bot needs "applications.commands" scope
# Ensure bot has "Use Slash Commands" permission
# Check bot invite URL includes proper scopes
```

#### 3. Clear Command Cache
```bash
# Clear Discord's command cache
# Kick and re-invite bot to server
# Or wait up to 1 hour for cache refresh
```

---

## 📞 Getting Additional Help

### Escalation Procedures

#### Level 1: Self-Service
- Review this troubleshooting guide
- Check recent documentation updates
- Test basic diagnostic commands

#### Level 2: Community Support
- Post in Discord support channel: [https://discord.gg/alphabetcartel](https://discord.gg/alphabetcartel)
- Search GitHub issues: [https://github.com/the-alphabet-cartel/ash-bot/issues](https://github.com/the-alphabet-cartel/ash-bot/issues)
- Review community wiki and FAQs

#### Level 3: Technical Support
- Create detailed GitHub issue with:
  - Problem description
  - Steps to reproduce
  - System information
  - Relevant log excerpts
  - Configuration details (sanitized)

#### Emergency Escalation
- For critical crisis system failures affecting user safety
- Contact crisis team leadership immediately
- Implement manual monitoring procedures
- Document incident for post-mortem analysis

### Information to Collect

When reporting issues, gather:

```bash
# System information
docker-compose version
docker version
uname -a

# Service status
docker-compose ps
curl http://10.20.30.253:8882/health
curl http://10.20.30.253:8881/health

# Recent logs (last 100 lines)
docker-compose logs --tail=100 ash-bot > ash-bot-logs.txt
docker-compose logs --tail=100 ash-nlp > ash-nlp-logs.txt

# Configuration (sanitize sensitive data)
docker-compose exec ash-bot env | grep BOT_ | sed 's/TOKEN=.*/TOKEN=***/' > config.txt

# Performance metrics
docker stats --no-stream > performance.txt
```

### Support Channels

- **GitHub Issues**: Technical bugs and feature requests
- **Discord Community**: General support and questions  
- **Documentation**: Comprehensive guides and references
- **Crisis Team**: Emergency escalation for safety issues

---

**Remember: When in doubt about crisis situations, always err on the side of caution. Manual intervention and human judgment take priority over automated systems during crisis response.**

**For immediate crisis support resources:**
- **US Crisis Hotline**: 988
- **Crisis Text Line**: Text HOME to 741741
- **LGBTQ National Hotline**: 1-888-843-4564

---

*This troubleshooting guide is maintained by The Alphabet Cartel technical team. For updates and additional resources, visit our community channels.*

**Discord**: [https://discord.gg/alphabetcartel](https://discord.gg/alphabetcartel)  
**Website**: [http://alphabetcartel.org](http://alphabetcartel.org)  
**Repository**: [https://github.com/the-alphabet-cartel/ash-bot](https://github.com/the-alphabet-cartel/ash-bot)