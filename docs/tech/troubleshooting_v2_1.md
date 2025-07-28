# 🛠️ ASH-BOT Troubleshooting Guide v2.1

**Comprehensive troubleshooting guide for ASH-BOT Discord crisis detection system**

**Repository**: https://github.com/the-alphabet-cartel/ash-bot  
**Support**: https://discord.gg/alphabetcartel (#tech-support)  

---

## 📋 Quick Diagnostic Checklist

Before diving into specific issues, run this quick diagnostic checklist:

```bash
#!/bin/bash
# quick_diagnostics.sh - Run this first for any issues

echo "=== ASH-BOT Quick Diagnostics ==="
echo "Timestamp: $(date)"
echo

# 1. Check if services are running
echo "🔍 Service Status:"
docker ps | grep -E "(ash-bot|ash-nlp|ash-dash|ash-thrash)" || echo "❌ No Ash services running"

# 2. Check service health
echo -e "\n🏥 Health Checks:"
curl -sf http://10.20.30.253:8882/health && echo "✅ ASH-BOT: Healthy" || echo "❌ ASH-BOT: Unhealthy"
curl -sf http://10.20.30.253:8881/health && echo "✅ ASH-NLP: Healthy" || echo "❌ ASH-NLP: Unhealthy"
curl -sf http://10.20.30.253:8883/health && echo "✅ ASH-DASH: Healthy" || echo "❌ ASH-DASH: Unhealthy"
curl -sf http://10.20.30.253:8884/health && echo "✅ ASH-THRASH: Healthy" || echo "❌ ASH-THRASH: Unhealthy"

# 3. Check recent logs for errors
echo -e "\n📋 Recent Errors:"
docker logs --since=1h ash-bot 2>&1 | grep -i error | tail -5

# 4. Check resource usage
echo -e "\n💾 Resource Usage:"
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}" ash-bot ash-nlp ash-dash ash-thrash

# 5. Check disk space
echo -e "\n💿 Disk Space:"
df -h | grep -E "(/$|/var|/tmp)"

echo -e "\n✅ Quick diagnostics complete"
```

---

## 🚨 Critical Issues (Service Down)

### Issue: ASH-BOT Not Starting

**Symptoms:**
- Bot appears offline in Discord
- Docker container exits immediately
- Connection refused errors

**Diagnostic Steps:**

```bash
# Check container status
docker ps -a | grep ash-bot

# Check logs for startup errors
docker logs ash-bot --tail 50

# Check configuration
docker exec ash-bot env | grep -E "(BOT_DISCORD_TOKEN|BOT_GUILD_ID)"

# Test Discord token validity
curl -H "Authorization: Bot YOUR_TOKEN" https://discord.com/api/v10/users/@me
```

**Common Causes & Solutions:**

#### 1. Invalid Discord Token
```bash
# Solution: Verify and update token
docker exec ash-bot env | grep BOT_DISCORD_TOKEN

# If empty or invalid, update .env file:
echo "BOT_DISCORD_TOKEN=your_new_token_here" >> .env
docker-compose restart ash-bot
```

#### 2. Missing Permissions
```bash
# Check bot permissions in Discord server
# Required permissions integer: 8589934591
# Includes: Read Messages, Send Messages, Manage Messages, etc.

# Verify guild ID
docker exec ash-bot env | grep DISCORD_BOT_GUILD_ID
```

#### 3. Network Connectivity Issues
```bash
# Test external connectivity from container
docker exec ash-bot ping discord.com
docker exec ash-bot nslookup discord.com

# Check firewall settings
sudo ufw status
sudo iptables -L | grep 8882
```

#### 4. Database Connection Issues
```bash
# Check database connectivity
docker exec ash-bot python -c "
import asyncio
from bot.data.database import Database
async def test():
    db = Database()
    await db.connect()
    print('Database connection successful')
asyncio.run(test())
"

# If SQLite database is corrupted
mv data/ash_bot.db data/ash_bot.db.backup
docker-compose restart ash-bot
```

### Issue: High Memory Usage / OOM Kills

**Symptoms:**
- Container frequently restarts
- "Killed" messages in logs
- Slow response times

**Diagnostic Steps:**

```bash
# Monitor memory usage over time
docker stats ash-bot

# Check for memory leaks in logs
docker logs ash-bot | grep -i "memory\|oom"

# Check system memory
free -h
cat /proc/meminfo | grep Available
```

**Solutions:**

```bash
# 1. Increase container memory limit
# Edit docker-compose.yml:
services:
  ash-bot:
    deploy:
      resources:
        limits:
          memory: 2G
        reservations:
          memory: 1G

# 2. Enable memory monitoring
# Add to .env:
ENABLE_MEMORY_MONITORING=true
MEMORY_WARNING_THRESHOLD=1GB

# 3. Optimize Python memory usage
# Add to .env:
PYTHONOPTIMIZE=1
PYTHON_GC_THRESHOLD=700,10,10

# Restart with new settings
docker-compose down
docker-compose up -d
```

---

## ⚠️ Integration Issues

### Issue: NLP Service Connection Failing

**Symptoms:**
- Crisis detection accuracy drops
- "NLP service unavailable" errors
- Keyword-only detection working

**Diagnostic Steps:**

```bash
# Test NLP service directly
curl -X POST http://10.20.30.253:8881/api/v2/analyze \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{"text": "test message", "user_id": "123"}'

# Check ASH-BOT to NLP connectivity
docker exec ash-bot curl http://10.20.30.253:8881/health

# Check circuit breaker status in logs
docker logs ash-bot | grep -i "circuit breaker"
```

**Solutions:**

#### 1. NLP Service Down
```bash
# Check NLP service status
docker ps | grep ash-nlp
docker logs ash-nlp --tail 20

# If not running, start it
cd ../ash-nlp
docker-compose up -d

# Verify startup
curl http://10.20.30.253:8881/health
```

#### 2. API Key Issues
```bash
# Verify API key configuration
docker exec ash-bot env | grep NLP_SERVER_API_KEY
docker exec ash-nlp env | grep API_KEY

# Generate new API key if needed
docker exec ash-nlp python scripts/generate_api_key.py

# Update ASH-BOT configuration
# Edit .env and restart
docker-compose restart ash-bot
```

#### 3. Circuit Breaker Stuck Open
```bash
# Reset circuit breaker
docker exec ash-bot python -c "
from bot.integrations.nlp_client import NLPClient
client = NLPClient('http://10.20.30.253:8881', 'api_key')
client.circuit_state = 'CLOSED'
client.failure_count = 0
print('Circuit breaker reset')
"

# Or restart ASH-BOT
docker-compose restart ash-bot
```

### Issue: Dashboard Integration Problems

**Symptoms:**
- No real-time updates in dashboard
- Missing analytics data
- Webhook failures in logs

**Diagnostic Steps:**

```bash
# Test dashboard webhook
curl -X POST http://10.20.30.253:8883/webhook/bot_events \
  -H "Content-Type: application/json" \
  -d '{"event": "test", "data": {}}'

# Check webhook URL configuration
docker exec ash-bot env | grep DASHBOARD_WEBHOOK_URL

# Monitor webhook calls
docker logs ash-bot | grep -i webhook
```

**Solutions:**

```bash
# 1. Verify dashboard service
curl http://10.20.30.253:8883/health

# If dashboard is down
cd ../ash-dash
docker-compose up -d

# 2. Update webhook URL if changed
# Edit .env:
DASHBOARD_WEBHOOK_URL=http://10.20.30.253:8883/webhook/bot_events

# Restart bot
docker-compose restart ash-bot

# 3. Check for webhook authentication issues
# Add webhook secret if required
WEBHOOK_SECRET=your_webhook_secret
```

---

## 🔍 Crisis Detection Issues

### Issue: False Positives (Non-Crisis Detected as Crisis)

**Symptoms:**
- Team alerts for obviously non-crisis messages
- High false positive rate in dashboard
- Team complaints about unnecessary notifications

**Diagnostic Steps:**

```bash
# Check recent false positive examples
docker logs ash-bot | grep -A 5 -B 5 "Crisis detected" | tail -20

# Review keyword detection accuracy
curl http://10.20.30.253:8882/api/v2/analytics/accuracy

# Test specific message patterns
curl -X POST http://10.20.30.253:8882/api/v2/analyze \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"message": "this game is killing me", "user_id": "test"}'
```

**Solutions:**

#### 1. Adjust Detection Thresholds
```bash
# Edit .env to raise thresholds:
HIGH_PRIORITY_THRESHOLD=0.85    # Was 0.8
MEDIUM_PRIORITY_THRESHOLD=0.70  # Was 0.6
LOW_PRIORITY_THRESHOLD=0.50     # Was 0.4

# Restart to apply changes
docker-compose restart ash-bot
```

#### 2. Improve Keyword Context Analysis
```bash
# Add context exclusions for gaming
# Edit bot/crisis/keywords.py to add:
GAMING_CONTEXTS = [
    'this game', 'the game', 'gaming', 'boss fight',
    'level', 'character', 'player', 'match'
]

# Apply context modifiers for gaming terms
# Rebuild and restart
docker-compose build ash-bot
docker-compose restart ash-bot
```

#### 3. Enable Enhanced NLP Context
```bash
# Enable context analysis
ENABLE_CONTEXT_ANALYSIS=true
CONTEXT_WEIGHT_FACTOR=0.4  # Increase context influence

# Restart with new settings
docker-compose restart ash-bot
```

### Issue: False Negatives (Crisis Not Detected)

**Symptoms:**
- Missed crisis situations reported by team
- Low detection rate in analytics
- Crisis situations reaching team through other channels

**Diagnostic Steps:**

```bash
# Test with known crisis phrases
curl -X POST http://10.20.30.253:8882/api/v2/analyze \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"message": "I want to end it all", "user_id": "test"}'

# Check if keywords are properly loaded
docker exec ash-bot python -c "
from bot.crisis.keywords import KeywordAnalyzer
analyzer = KeywordAnalyzer({})
print('High priority keywords:', len(analyzer.keyword_patterns['high']))
"

# Review NLP service accuracy
curl http://10.20.30.253:8881/api/v2/metrics/accuracy
```

**Solutions:**

#### 1. Lower Detection Thresholds
```bash
# Edit .env to lower thresholds:
HIGH_PRIORITY_THRESHOLD=0.75    # Was 0.8
MEDIUM_PRIORITY_THRESHOLD=0.55  # Was 0.6
LOW_PRIORITY_THRESHOLD=0.35     # Was 0.4

# Restart to apply changes
docker-compose restart ash-bot
```

#### 2. Expand Keyword Patterns
```bash
# Add more crisis indicators
# Edit bot/crisis/keywords.py to include:
# - Cultural/generational specific phrases
# - LGBTQIA+ specific crisis language
# - Gaming community specific expressions

# Example additions:
'medium': {
    'depression': [
        # Add existing patterns plus:
        r'\bnot\s+okay\b',
        r'\bstruggling\s+hard\b',
        r'\bcan[\'']?t\s+anymore\b',
        r'\btired\s+of\s+everything\b'
    ]
}

# Rebuild and restart
docker-compose build ash-bot
docker-compose restart ash-bot
```

#### 3. Improve NLP Model Training
```bash
# Check if NLP service needs retraining
curl http://10.20.30.253:8881/api/v2/model/stats

# If accuracy is low, trigger retraining
curl -X POST http://10.20.30.253:8881/api/v2/model/retrain \
  -H "Authorization: Bearer YOUR_API_KEY"
```

---

## 🔧 Performance Issues

### Issue: Slow Crisis Detection Response

**Symptoms:**
- Message analysis takes >500ms
- Team complaints about delayed alerts
- High response times in metrics

**Diagnostic Steps:**

```bash
# Monitor processing times
docker logs ash-bot | grep "processing_time_ms" | tail -10

# Check system performance
docker exec ash-bot python -c "
import time
start = time.time()
# Simulate message analysis
print(f'Test processing time: {(time.time() - start) * 1000:.0f}ms')
"

# Check resource usage
docker stats ash-bot --no-stream
```

**Solutions:**

#### 1. Optimize NLP Integration
```bash
# Reduce NLP timeout for faster fallback
# Edit .env:
NLP_TIMEOUT=5  # Reduce from 30 seconds
NLP_RETRY_ATTEMPTS=1  # Reduce retries

# Enable async processing
ENABLE_ASYNC_PROCESSING=true
MAX_CONCURRENT_ANALYSES=5

# Restart with new settings
docker-compose restart ash-bot
```

#### 2. Implement Caching
```bash
# Enable Redis caching
# Edit .env:
ENABLE_REDIS_CACHE=true
REDIS_URL=redis://redis:6379/0
CACHE_TTL=300  # 5 minutes

# Add Redis service to docker-compose.yml if not present
services:
  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes --maxmemory 256mb

# Restart all services
docker-compose down
docker-compose up -d
```

#### 3. Database Query Optimization
```bash
# Add database indexes
docker exec ash-bot python -c "
import asyncio
from bot.data.database import Database

async def optimize():
    db = Database()
    await db.connect()
    
    # Add indexes for common queries
    await db.execute('CREATE INDEX IF NOT EXISTS idx_crisis_alerts_user_id ON crisis_alerts(user_id)')
    await db.execute('CREATE INDEX IF NOT EXISTS idx_crisis_alerts_created_at ON crisis_alerts(created_at)')
    await db.execute('CREATE INDEX IF NOT EXISTS idx_crisis_alerts_status ON crisis_alerts(status)')
    
    print('Database indexes optimized')

asyncio.run(optimize())
"
```

### Issue: High CPU Usage

**Symptoms:**
- Container CPU usage >80%
- System becoming unresponsive
- Slow Discord message processing

**Diagnostic Steps:**

```bash
# Monitor CPU usage patterns
docker stats ash-bot

# Check for CPU-intensive operations
docker exec ash-bot top -bn1 | grep python

# Profile Python application
docker exec ash-bot python -m cProfile -s tottime -m bot.main | head -20
```

**Solutions:**

```bash
# 1. Reduce concurrent processing
# Edit .env:
MAX_CONCURRENT_ANALYSES=3  # Reduce from 10
MESSAGE_QUEUE_SIZE=500     # Reduce from 1000

# 2. Optimize keyword matching
# Use compiled regex patterns
# Edit bot/crisis/keywords.py:
import re

class KeywordAnalyzer:
    def __init__(self, config):
        self.compiled_patterns = {}
        for severity, categories in self.keyword_patterns.items():
            self.compiled_patterns[severity] = {}
            for category, patterns in categories.items():
                self.compiled_patterns[severity][category] = [
                    re.compile(pattern, re.IGNORECASE) for pattern in patterns
                ]

# 3. Implement message batching
# Edit .env:
ENABLE_MESSAGE_BATCHING=true
BATCH_SIZE=10
BATCH_TIMEOUT=1000  # 1 second

# Restart services
docker-compose restart ash-bot
```

---

## 🔐 Security Issues

### Issue: Unauthorized API Access

**Symptoms:**
- Unknown API calls in logs
- Rate limiting triggered frequently
- Suspicious activity alerts

**Diagnostic Steps:**

```bash
# Check recent API access logs
docker logs ash-bot | grep -E "(401|403|429)" | tail -20

# Monitor API key usage
docker logs ash-bot | grep "API key" | tail -10

# Check rate limiting
docker logs ash-bot | grep "rate limit" | tail -10
```

**Solutions:**

#### 1. Rotate API Keys
```bash
# Generate new API key
docker exec ash-bot python scripts/generate_api_key.py

# Update external integrations with new key
# Update dashboard configuration
# Update testing suite configuration

# Revoke old API keys
docker exec ash-bot python scripts/revoke_api_key.py OLD_KEY
```

#### 2. Strengthen Rate Limiting
```bash
# Edit .env for stricter limits:
API_RATE_LIMIT=50          # Reduce from 100
API_BURST_LIMIT=100        # Reduce from 200
ENABLE_IP_WHITELIST=true
GLOBAL_ALLOWED_IPS=10.20.30.253,127.0.0.1

# Enable request logging
ENABLE_REQUEST_LOGGING=true
LOG_FAILED_AUTH_ATTEMPTS=true

# Restart with new security settings
docker-compose restart ash-bot
```

#### 3. Enable Audit Logging
```bash
# Enhanced security logging
# Edit .env:
ENABLE_AUDIT_LOGGING=true
AUDIT_GLOBAL_LOG_LEVEL=INFO
SECURITY_ALERT_WEBHOOK=your_security_webhook_url

# Monitor security events
tail -f logs/security_audit.log
```

### Issue: Discord Token Compromise

**Symptoms:**
- Bot performing unauthorized actions
- Unexpected bot behavior
- Security warnings from Discord

**Immediate Response:**

```bash
# 1. Immediately disable current token
# Go to Discord Developer Portal
# Regenerate bot token

# 2. Update configuration with new token
# Edit .env:
BOT_DISCORD_TOKEN=new_token_here

# 3. Restart bot immediately
docker-compose restart ash-bot

# 4. Review recent bot actions
docker logs ash-bot --since=24h | grep -E "(command|action|guild)" > security_review.log

# 5. Check for unauthorized guild additions
curl -H "Authorization: Bot YOUR_NEW_TOKEN" \
     https://discord.com/api/v10/users/@me/guilds
```

---

## 📊 Monitoring and Alerting Issues

### Issue: Missing Metrics/Analytics

**Symptoms:**
- Dashboard shows no data
- Missing performance metrics
- Analytics queries returning empty results

**Diagnostic Steps:**

```bash
# Check metrics collection
curl http://10.20.30.253:8882/api/v2/system/metrics

# Verify database has data
docker exec ash-bot python -c "
import asyncio
from bot.data.repositories import AnalyticsRepository
async def check():
    repo = AnalyticsRepository()
    count = await repo.get_total_analyses()
    print(f'Total analyses in database: {count}')
asyncio.run(check())
"

# Check dashboard integration
curl http://10.20.30.253:8883/api/data/recent
```

**Solutions:**

```bash
# 1. Enable metrics collection
# Edit .env:
ENABLE_METRICS_COLLECTION=true
METRICS_EXPORT_INTERVAL=60  # seconds
ENABLE_ANALYTICS_EXPORT=true

# 2. Verify database permissions
docker exec ash-bot python -c "
import asyncio
from bot.data.database import Database
async def test():
    db = Database()
    await db.execute('INSERT INTO test_table (data) VALUES (?)', ('test',))
    print('Database write test successful')
asyncio.run(test())
"

# 3. Restart metrics collection
docker-compose restart ash-bot
```

### Issue: Alert System Not Working

**Symptoms:**
- No crisis team notifications
- Missing Discord alerts
- Silent failures during crisis detection

**Diagnostic Steps:**

```bash
# Test notification system
docker exec ash-bot python -c "
import asyncio
from bot.team.manager import TeamManager
from bot.utils.notifications import NotificationManager

async def test():
    manager = NotificationManager(None)
    await manager.test_notifications()
    print('Notification test complete')

asyncio.run(test())
"

# Check Discord permissions
curl -H "Authorization: Bot YOUR_TOKEN" \
     https://discord.com/api/v10/channels/YOUR_CRISIS_CHANNEL_ID

# Verify role mentions work
docker logs ash-bot | grep "role mention" | tail -5
```

**Solutions:**

```bash
# 1. Fix Discord permissions
# Ensure bot has:
# - Send Messages in crisis channel
# - Mention Everyone (for role pings)
# - Embed Links
# - Add Reactions

# 2. Test notification channels
# Edit .env to verify:
BOT_CRISIS_RESPONSE_CHANNEL_ID=correct_channel_id
CRISIS_TEAM_ROLE_ID=correct_role_id

# 3. Enable notification debugging
ENABLE_NOTIFICATION_DEBUG=true
LOG_NOTIFICATION_ATTEMPTS=true

# Restart and test
docker-compose restart ash-bot
```

---

## 🔄 Recovery Procedures

### Complete System Recovery

When everything is broken and you need to start fresh:

```bash
#!/bin/bash
# emergency_recovery.sh

echo "🚨 Starting emergency ASH-BOT recovery..."

# 1. Stop all services
docker-compose down

# 2. Backup current data
timestamp=$(date +%Y%m%d_%H%M%S)
mkdir -p backups/$timestamp
cp -r data/ backups/$timestamp/
cp -r logs/ backups/$timestamp/
cp .env backups/$timestamp/

echo "✅ Data backed up to backups/$timestamp/"

# 3. Clean up containers and images
docker system prune -f
docker volume prune -f

# 4. Reset to known good configuration
git checkout main
git pull origin main

# 5. Restore configuration
cp backups/$timestamp/.env .env

# 6. Rebuild everything
docker-compose build --no-cache

# 7. Start services one by one
echo "🔄 Starting database..."
docker-compose up -d postgres redis

echo "🔄 Waiting for database..."
sleep 30

echo "🔄 Starting ASH-BOT..."
docker-compose up -d ash-bot

# 8. Verify health
sleep 60
curl -f http://10.20.30.253:8882/health && echo "✅ ASH-BOT recovered successfully" || echo "❌ Recovery failed"

echo "🏁 Emergency recovery complete"
```

### Database Recovery

When database is corrupted or missing:

```bash
#!/bin/bash
# database_recovery.sh

echo "🔧 Starting database recovery..."

# 1. Stop ASH-BOT
docker-compose stop ash-bot

# 2. Backup corrupted database
mv data/ash_bot.db data/ash_bot.db.corrupted.$(date +%Y%m%d_%H%M%S)

# 3. Initialize fresh database
docker-compose up -d postgres

# 4. Run database migrations
docker-compose exec postgres psql -U ash_user -d ash_bot -f /docker-entrypoint-initdb.d/init.sql

# 5. Restart ASH-BOT
docker-compose up -d ash-bot

# 6. Verify database health
docker exec ash-bot python -c "
import asyncio
from bot.data.database import Database
async def test():
    db = Database()
    await db.connect()
    result = await db.fetch('SELECT COUNT(*) FROM crisis_alerts')
    print(f'Database initialized: {result[0][0]} alerts')
asyncio.run(test())
"

echo "✅ Database recovery complete"
```

### Configuration Reset

When configuration is corrupted:

```bash
#!/bin/bash
# config_reset.sh

echo "⚙️ Resetting configuration..."

# 1. Backup current config
cp .env .env.backup.$(date +%Y%m%d_%H%M%S)

# 2. Generate fresh config from template
cp .env.template .env

# 3. Prompt for essential values
read -p "Discord Token: " BOT_DISCORD_TOKEN
read -p "Discord Guild ID: " DISCORD_BOT_GUILD_ID
read -p "Crisis Channel ID: " BOT_CRISIS_RESPONSE_CHANNEL_ID

# 4. Update .env file
sed -i "s/BOT_DISCORD_TOKEN=.*/BOT_DISCORD_TOKEN=$BOT_DISCORD_TOKEN/" .env
sed -i "s/DISCORD_BOT_GUILD_ID=.*/DISCORD_BOT_GUILD_ID=$DISCORD_BOT_GUILD_ID/" .env
sed -i "s/BOT_CRISIS_RESPONSE_CHANNEL_ID=.*/BOT_CRISIS_RESPONSE_CHANNEL_ID=$BOT_CRISIS_RESPONSE_CHANNEL_ID/" .env

# 5. Set safe defaults
echo "
# Safe default settings
HIGH_PRIORITY_THRESHOLD=0.8
MEDIUM_PRIORITY_THRESHOLD=0.6
LOW_PRIORITY_THRESHOLD=0.4
ENABLE_KEYWORD_DETECTION=true
ENABLE_NLP_INTEGRATION=true
AUTO_RESPOND_TO_CRISIS=true
GLOBAL_LOG_LEVEL=INFO
" >> .env

# 6. Restart with new config
docker-compose restart ash-bot

echo "✅ Configuration reset complete"
```

---

## 📞 Getting Help

### Self-Service Resources

1. **Check this troubleshooting guide first**
2. **Review logs**: `docker logs ash-bot --tail 50`
3. **Run diagnostics**: Use the quick diagnostic script at the top
4. **Check dashboard**: https://dashboard.alphabetcartel.net for system status
5. **Test individual components**: Use health check endpoints

### Community Support

**Discord Support**: https://discord.gg/alphabetcartel
- **#tech-support**: General technical issues
- **#crisis-response**: Crisis team specific issues
- **#development**: Development and contribution questions

**GitHub Issues**: https://github.com/the-alphabet-cartel/ash-bot/issues
- Bug reports with full diagnostic information
- Feature requests
- Documentation improvements

### Professional Support

For critical production issues or security concerns:

1. **Emergency Discord**: @TechLead or @AdminTeam in Discord
2. **Email**: urgent-tech@alphabetcartel.org
3. **Include**: 
   - Diagnostic script output
   - Recent logs
   - Environment details
   - Impact assessment

### Creating Effective Bug Reports

When reporting issues, include:

```markdown
## Issue Description
Brief description of the problem

## Environment
- ASH-BOT Version: v2.1.x
- Server OS: Debian 12
- Docker Version: 
- Deployment Type: Production/Development

## Steps to Reproduce
1. Step one
2. Step two
3. Step three

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Diagnostic Information
```bash
# Paste output from quick_diagnostics.sh
```

## Logs
```
# Paste relevant log entries
```

## Additional Context
Any other relevant information
```

---

## 🔧 Preventive Maintenance

### Daily Checks

```bash
#!/bin/bash
# daily_maintenance.sh

# Health checks
curl -sf http://10.20.30.253:8882/health > /dev/null && echo "✅ Bot healthy" || echo "❌ Bot unhealthy"

# Disk space check
DISK_USAGE=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 80 ]; then
    echo "⚠️ Disk usage high: ${DISK_USAGE}%"
fi

# Log rotation
find logs/ -name "*.log" -mtime +7 -delete

# Database cleanup
docker exec ash-bot python scripts/cleanup_old_data.py --days 30

echo "✅ Daily maintenance complete"
```

### Weekly Checks

```bash
#!/bin/bash
# weekly_maintenance.sh

# Update system packages
sudo apt update && sudo apt upgrade -y

# Docker cleanup
docker system prune -f

# Backup database
pg_dump ash_bot > backups/weekly_backup_$(date +%Y%m%d).sql

# Performance analysis
docker exec ash-bot python scripts/generate_performance_report.py

# Security audit
docker exec ash-bot python scripts/security_audit.py

echo "✅ Weekly maintenance complete"
```

### Monthly Checks

```bash
#!/bin/bash
# monthly_maintenance.sh

# Full system backup
tar -czf backups/monthly_backup_$(date +%Y%m%d).tar.gz data/ logs/ .env

# Update Docker images
docker-compose pull
docker-compose build --no-cache

# Review and rotate logs
logrotate /etc/logrotate.d/ash-bot

# Performance optimization
docker exec ash-bot python scripts/optimize_database.py

# Security updates
sudo apt update && sudo apt upgrade -y

echo "✅ Monthly maintenance complete"
```

---

**This troubleshooting guide covers the most common issues and provides systematic approaches to diagnosing and resolving problems. Keep this guide updated as new issues are discovered and resolved.**

🌈 **Discord**: https://discord.gg/alphabetcartel