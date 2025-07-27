# Troubleshooting Guide - Ash System

**Comprehensive Problem Resolution Guide for Mental Health Crisis Detection System**

This guide provides step-by-step troubleshooting procedures for common issues with the Ash mental health crisis detection system serving [The Alphabet Cartel Discord community](https://discord.gg/alphabetcartel).

---

## 🎯 Quick Reference

### Emergency Contacts
- **Crisis Response Lead:** [Contact Information]
- **Technical Team Lead:** [Contact Information]
- **System Administrator:** [Contact Information]
- **Community Leadership:** [Contact Information]

### Critical System URLs
- **Main Dashboard:** https://10.20.30.16:8883
- **System Health:** http://10.20.30.16:8884/health
- **NLP Server:** http://10.20.30.16:8881/health
- **Bot Status:** http://10.20.30.253:8882/health

### Emergency Procedures
1. **If main bot is offline:** Activate manual crisis monitoring immediately
2. **If NLP server fails:** Bot continues with keyword-only detection
3. **If dashboard is down:** Use direct Discord monitoring and API calls
4. **If multiple systems fail:** Contact technical lead and implement emergency protocols

---

## 🚨 Critical Issues (Immediate Action Required)

### Bot Completely Offline

**Symptoms:**
- Ash bot shows as offline in Discord
- No response to commands or mentions
- Health check fails: `curl http://10.20.30.253:8882/health`

**Immediate Actions:**
1. **Activate Manual Monitoring** (PRIORITY 1)
   - Alert crisis response team via Discord #crisis-response
   - Implement manual message monitoring procedures
   - Notify community leadership if extended outage expected

2. **Diagnose Issue**
   ```bash
   # Check bot container status
   ssh admin@10.20.30.253
   docker-compose ps
   docker-compose logs ash
   ```

**Common Causes & Solutions:**

**Docker Container Stopped:**
```bash
# Restart bot service
docker-compose restart ash

# If restart fails, rebuild
docker-compose down
docker-compose up -d

# Verify restart
curl http://10.20.30.253:8882/health
```

**Discord Token Invalid:**
```bash
# Check Discord connection in logs
docker-compose logs ash | grep -i "discord\|token\|auth"

# If token expired, update .env file
nano .env
# Update DISCORD_TOKEN value
docker-compose restart ash
```

**Database Connection Issues:**
```bash
# Check database connectivity
docker-compose exec ash python -c "from bot.core.database import test_connection; test_connection()"

# If PostgreSQL issues
docker-compose restart db
docker-compose restart ash
```

**Network/Firewall Issues:**
```bash
# Check network connectivity
ping discord.com
telnet gateway.discord.gg 443

# Check firewall rules
sudo ufw status
# Ensure Discord gateway ports are open
```

**Resource Exhaustion:**
```bash
# Check system resources
free -h
df -h
docker stats

# If memory issues, restart system services
sudo systemctl restart docker
docker-compose up -d
```

### NLP Server Unresponsive

**Symptoms:**
- Health check fails: `curl http://10.20.30.16:8881/health`
- Bot logs show NLP connection timeouts
- Detection accuracy drops significantly

**Immediate Actions:**
1. **Verify Bot Continues Operating** (Bot should fall back to keyword-only detection)
2. **Check NLP Server Status**

**Windows PowerShell Diagnostics:**
```powershell
# Check container status
docker-compose ps

# Check logs for errors
docker-compose logs ash-nlp

# Check system resources
docker stats
Get-Process | Where-Object {$_.ProcessName -like "*docker*"}
```

**Common Causes & Solutions:**

**GPU Driver Issues:**
```powershell
# Check GPU status
nvidia-smi

# If GPU not detected
# Restart Docker Desktop
# Update NVIDIA drivers if needed
# Restart ash-nlp container
docker-compose restart ash-nlp
```

**Memory Exhaustion:**
```powershell
# Check memory usage
Get-Process | Sort-Object WorkingSet -Descending | Select-Object -First 10

# If memory issues, restart NLP server
docker-compose restart ash-nlp

# If persistent, restart Docker Desktop
```

**Model Loading Failure:**
```powershell
# Check model files
docker-compose exec ash-nlp ls -la /app/models/

# If models missing or corrupted
# Download fresh models (see implementation guide)
# Restart service
docker-compose restart ash-nlp
```

**CUDA/PyTorch Issues:**
```powershell
# Test CUDA availability
docker-compose exec ash-nlp python -c "import torch; print(torch.cuda.is_available())"

# If CUDA unavailable, check:
# 1. NVIDIA drivers updated
# 2. Docker Desktop WSL2 integration enabled
# 3. NVIDIA Container Toolkit installed
```

### Dashboard Inaccessible

**Symptoms:**
- Cannot access https://10.20.30.16:8883
- 502 Bad Gateway or connection timeout errors
- Crisis alerts not displaying

**Immediate Actions:**
1. **Use Alternative Monitoring**
   ```bash
   # Direct API status checks
   curl http://10.20.30.16:8881/health  # NLP
   curl http://10.20.30.253:8882/health # Bot
   curl http://10.20.30.16:8884/health  # Testing
   ```

2. **Diagnose Dashboard Issues**
   ```powershell
   # Check dashboard container
   docker-compose ps ash-dash
   docker-compose logs ash-dash

   # Check port availability
   netstat -an | findstr :8883
   ```

**Common Causes & Solutions:**

**Container Not Running:**
```powershell
# Restart dashboard
docker-compose restart ash-dash

# If fails to start, check logs
docker-compose logs ash-dash

# Rebuild if necessary
docker-compose down ash-dash
docker-compose up -d ash-dash
```

**SSL Certificate Issues:**
```powershell
# Check certificate validity
openssl x509 -in certs/dashboard.crt -text -noout

# If certificate expired, regenerate
# See implementation guide for certificate generation
# Restart dashboard after certificate update
docker-compose restart ash-dash
```

**Database Connection Issues:**
```powershell
# Check database connectivity
docker-compose exec ash-dash node -e "
const db = require('./src/database');
db.testConnection().then(console.log).catch(console.error);
"

# If database issues, restart database service
docker-compose restart db
docker-compose restart ash-dash
```

**Port Conflicts:**
```powershell
# Check if port 8883 is in use
netstat -an | findstr :8883

# If port conflict, stop conflicting service or change port in .env
# Update DASHBOARD_PORT in .env
# Restart dashboard
docker-compose restart ash-dash
```

---

## ⚠️ High Priority Issues

### Crisis Detection Accuracy Drop

**Symptoms:**
- Testing suite reports accuracy below 95%
- Increase in false positives or false negatives
- Crisis team reports missed alerts or inappropriate alerts

**Diagnosis Steps:**
1. **Run Comprehensive Test**
   ```bash
   curl -X POST http://10.20.30.16:8884/api/test/comprehensive
   # Wait for completion, then check results
   curl http://10.20.30.16:8884/api/test/results/latest
   ```

2. **Check System Performance**
   ```bash
   # Check all service health
   curl http://10.20.30.253:8882/health
   curl http://10.20.30.16:8881/health
   curl http://10.20.30.16:8883/health
   curl http://10.20.30.16:8884/health
   ```

**Common Causes & Solutions:**

**NLP Model Degradation:**
```powershell
# Check model performance metrics
curl http://10.20.30.16:8881/api/performance/metrics

# If model performance poor:
# 1. Restart NLP server to reload model
docker-compose restart ash-nlp

# 2. Check model files integrity
docker-compose exec ash-nlp python src/validate_model.py

# 3. If model corrupted, restore from backup
# See backup/recovery procedures in implementation guide
```

**Keyword Dictionary Outdated:**
```bash
# Check keyword update date
curl http://10.20.30.253:8882/api/config/detection-settings

# If keywords old, update from repository
git pull origin main
docker-compose restart ash

# Verify keyword reload
curl http://10.20.30.253:8882/api/config/detection-settings
```

**Configuration Drift:**
```bash
# Check detection thresholds
curl http://10.20.30.253:8882/api/config/detection-settings

# If thresholds incorrect, update .env
nano .env
# Verify THRESHOLD values
docker-compose restart ash
```

### Slow Response Times

**Symptoms:**
- End-to-end alert time >10 seconds
- NLP processing >5 seconds
- Dashboard updates delayed

**Diagnosis:**
```powershell
# Check processing times
curl http://10.20.30.16:8881/api/performance/metrics

# Check system resources
docker stats
Get-Process | Sort-Object CPU -Descending | Select-Object -First 10
```

**Solutions:**

**GPU Utilization Issues:**
```powershell
# Check GPU usage
nvidia-smi

# If GPU underutilized:
# 1. Check CUDA availability
docker-compose exec ash-nlp python -c "import torch; print(torch.cuda.is_available())"

# 2. Restart NLP server with GPU access
docker-compose restart ash-nlp

# 3. Check Docker GPU access
docker run --rm --gpus all nvidia/cuda:11.0-base nvidia-smi
```

**Memory Pressure:**
```powershell
# If high memory usage
# Clear Docker caches
docker system prune -f

# Restart memory-intensive services
docker-compose restart ash-nlp
docker-compose restart ash-dash
```

**Network Latency:**
```bash
# Test network latency between services
ping 10.20.30.16
ping 10.20.30.253

# Check for network congestion
iperf3 -c 10.20.30.16
```

### Testing Suite Failures

**Symptoms:**
- Comprehensive test accuracy <90%
- Test timeouts or errors
- Inconsistent test results

**Diagnosis:**
```bash
# Check testing suite health
curl http://10.20.30.16:8884/health

# Review latest test results
curl http://10.20.30.16:8884/api/test/results/latest

# Check detailed failure analysis
curl http://10.20.30.16:8884/api/test/comprehensive/latest/failures
```

**Solutions:**

**Test Data Corruption:**
```powershell
# Verify test data integrity
docker-compose exec ash-thrash python src/validate_test_data.py

# If test data corrupted, restore from repository
git pull origin main
docker-compose restart ash-thrash
```

**NLP Server Connection Issues:**
```powershell
# Test NLP connectivity from testing suite
docker-compose exec ash-thrash curl http://localhost:8881/health

# If connection fails, check network configuration
docker network ls
docker network inspect ash-network
```

---

## 🔧 Medium Priority Issues

### Authentication Problems

**Symptoms:**
- Unable to log into dashboard
- API authentication failures
- Team member access denied

**Dashboard Login Issues:**
```powershell
# Check dashboard authentication service
docker-compose logs ash-dash | grep -i auth

# Reset admin password if needed
docker-compose exec ash-dash node scripts/reset-admin-password.js

# Check database user records
docker-compose exec ash-dash node scripts/list-users.js
```

**API Key Issues:**
```bash
# Test API key validity
curl -H "Authorization: Bearer your-api-key" http://10.20.30.16:8881/health

# If API key invalid, regenerate
# Update .env files with new keys
# Restart affected services
```

### Discord Integration Issues

**Symptoms:**
- Bot responds but slowly
- Some Discord features not working
- Permissions errors

**Permission Diagnostics:**
```bash
# Check bot permissions in Discord
# Bot should have:
# - Read Messages/View Channels
# - Send Messages  
# - Read Message History
# - Use Slash Commands
# - Manage Messages (optional)

# Check Discord rate limiting
docker-compose logs ash | grep -i "rate limit\|429"
```

**Solutions:**
```bash
# If rate limited, implement backoff
# Check bot configuration for proper rate limiting
# Consider reducing message processing frequency temporarily

# If permission issues, update bot permissions in Discord
# Restart bot after permission changes
docker-compose restart ash
```

### Database Performance Issues

**Symptoms:**
- Slow dashboard loading
- API response delays
- Database connection errors

**Database Diagnostics:**
```bash
# Check database performance
docker-compose exec db psql -U postgres -c "
SELECT query, mean_time, calls 
FROM pg_stat_statements 
ORDER BY mean_time DESC LIMIT 10;"

# Check database connections
docker-compose exec db psql -U postgres -c "
SELECT count(*) as active_connections 
FROM pg_stat_activity 
WHERE state = 'active';"
```

**Solutions:**
```bash
# If too many connections, restart services
docker-compose restart ash
docker-compose restart ash-dash

# If slow queries, analyze and optimize
# Check for missing indexes
docker-compose exec db psql -U postgres -c "
SELECT schemaname, tablename, attname, null_frac, avg_width, n_distinct 
FROM pg_stats 
WHERE schemaname = 'public';"

# Restart database if needed
docker-compose restart db
```

---

## 🔍 Diagnostic Tools and Procedures

### Health Check Scripts

**Comprehensive System Health Check:**
```bash
#!/bin/bash
# system_health_check.sh

echo "=== Ash System Health Check ==="
echo "Timestamp: $(date)"
echo

# Check all services
services=("10.20.30.253:8882" "10.20.30.16:8881" "10.20.30.16:8883" "10.20.30.16:8884")
service_names=("Ash Bot" "NLP Server" "Dashboard" "Testing Suite")

for i in "${!services[@]}"; do
    echo "Checking ${service_names[$i]} (${services[$i]})..."
    if curl -f -s "http://${services[$i]}/health" > /dev/null; then
        echo "✅ ${service_names[$i]}: HEALTHY"
    else
        echo "❌ ${service_names[$i]}: UNHEALTHY"
    fi
done

echo
echo "=== Quick Validation Test ==="
response=$(curl -s -X POST http://10.20.30.16:8884/api/test/quick-validation)
accuracy=$(echo $response | jq -r '.results.accuracy_percent')
echo "Detection Accuracy: $accuracy%"

if (( $(echo "$accuracy >= 90" | bc -l) )); then
    echo "✅ Accuracy: ACCEPTABLE"
else
    echo "❌ Accuracy: BELOW THRESHOLD"
fi

echo
echo "=== Resource Usage ==="
echo "Bot Server (10.20.30.253):"
ssh admin@10.20.30.253 "docker stats --no-stream --format 'table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}'"

echo
echo "AI Server (10.20.30.16):"
# Run locally on AI server
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"

echo
echo "=== Recent Alerts ==="
alerts=$(curl -s http://10.20.30.16:8883/api/alerts/active | jq -r '.summary')
echo $alerts
```

**PowerShell Health Check (Windows):**
```powershell
# system_health_check.ps1

Write-Host "=== Ash System Health Check ===" -ForegroundColor Cyan
Write-Host "Timestamp: $(Get-Date)" -ForegroundColor Gray
Write-Host

# Check services
$services = @(
    @{Name="Ash Bot"; URL="http://10.20.30.253:8882/health"},
    @{Name="NLP Server"; URL="http://10.20.30.16:8881/health"}, 
    @{Name="Dashboard"; URL="http://10.20.30.16:8883/health"},
    @{Name="Testing Suite"; URL="http://10.20.30.16:8884/health"}
)

foreach ($service in $services) {
    Write-Host "Checking $($service.Name)..." -NoNewline
    try {
        $response = Invoke-RestMethod -Uri $service.URL -TimeoutSec 10
        Write-Host " ✅ HEALTHY" -ForegroundColor Green
    }
    catch {
        Write-Host " ❌ UNHEALTHY" -ForegroundColor Red
        Write-Host "  Error: $($_.Exception.Message)" -ForegroundColor Yellow
    }
}

Write-Host
Write-Host "=== GPU Status ===" -ForegroundColor Cyan
nvidia-smi --query-gpu=name,memory.used,memory.total,utilization.gpu --format=csv

Write-Host
Write-Host "=== Docker Container Status ===" -ForegroundColor Cyan
docker-compose ps

Write-Host
Write-Host "=== Resource Usage ===" -ForegroundColor Cyan
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"
```

### Log Analysis Tools

**Error Pattern Detection:**
```bash
#!/bin/bash
# analyze_logs.sh

echo "=== Log Analysis for Ash System ==="

# Analyze bot logs
echo "Bot Error Patterns (Last 24h):"
docker-compose logs ash --since 24h | grep -i "error\|exception\|fail" | head -10

# Analyze NLP server logs  
echo "NLP Server Error Patterns:"
docker-compose logs ash-nlp --since 24h | grep -i "error\|exception\|cuda\|memory" | head -10

# Analyze dashboard logs
echo "Dashboard Error Patterns:"
docker-compose logs ash-dash --since 24h | grep -i "error\|exception\|database" | head -10

# Check for memory issues
echo "Memory-related Issues:"
docker-compose logs --since 24h | grep -i "memory\|oom\|killed" | head -5

# Check for network issues
echo "Network-related Issues:"
docker-compose logs --since 24h | grep -i "timeout\|connection\|network" | head -5
```

**Performance Monitoring:**
```bash
#!/bin/bash
# performance_monitor.sh

echo "=== Performance Monitoring ==="

# API response times
echo "Testing API Response Times:"
for service in "10.20.30.253:8882" "10.20.30.16:8881" "10.20.30.16:8883" "10.20.30.16:8884"; do
    echo -n "$service: "
    time curl -f -s "http://$service/health" > /dev/null
done

# Detection accuracy over time
echo "Recent Detection Accuracy:"
curl -s http://10.20.30.16:8884/api/test/analytics/accuracy-trends?timeframe=7d | jq -r '.data_points[-5:][] | "\(.date): \(.overall_accuracy)%"'

# Resource usage trends
echo "Resource Usage Alerts:"
docker stats --no-stream | awk 'NR>1 {
    gsub(/%/, "", $3); gsub(/%/, "", $4);
    if ($3 > 80) print $1 ": High CPU (" $3 "%)";
    if ($4 > 85) print $1 ": High Memory (" $4 "%)";
}'
```

---

## 🔄 Recovery Procedures

### Service Recovery

**Individual Service Recovery:**
```bash
# Restart specific service
docker-compose restart service_name

# If restart fails, rebuild
docker-compose stop service_name
docker-compose rm service_name
docker-compose up -d service_name

# Verify recovery
curl http://service_url/health
```

**Full System Recovery:**
```bash
#!/bin/bash
# full_system_recovery.sh

echo "=== Full System Recovery Procedure ==="

# Step 1: Backup current state
echo "Creating emergency backup..."
timestamp=$(date +%Y%m%d_%H%M%S)
docker-compose exec ash tar -czf /tmp/emergency_backup_$timestamp.tar.gz /app/data
docker cp ash-bot:/tmp/emergency_backup_$timestamp.tar.gz ./backups/

# Step 2: Stop all services
echo "Stopping all services..."
docker-compose down

# Step 3: Clean Docker system
echo "Cleaning Docker system..."
docker system prune -f
docker volume prune -f

# Step 4: Pull latest images
echo "Pulling latest images..."
docker-compose pull

# Step 5: Restart services in order
echo "Starting services..."
docker-compose up -d db          # Database first
sleep 10
docker-compose up -d ash-nlp     # NLP server
sleep 30
docker-compose up -d ash         # Main bot
sleep 10
docker-compose up -d ash-dash    # Dashboard
docker-compose up -d ash-thrash  # Testing suite

# Step 6: Verify recovery
echo "Verifying system recovery..."
sleep 30
./system_health_check.sh
```

### Database Recovery

**Database Connection Recovery:**
```bash
# Check database status
docker-compose exec db pg_isready -U postgres

# If database unresponsive, restart
docker-compose restart db

# Wait for database to be ready
sleep 30

# Restart dependent services
docker-compose restart ash
docker-compose restart ash-dash
```

**Database Corruption Recovery:**
```bash
# Stop all services using database
docker-compose stop ash ash-dash

# Create database backup
docker-compose exec db pg_dump -U postgres ash_db > backup_before_recovery.sql

# Check database integrity
docker-compose exec db postgres -D /var/lib/postgresql/data --check

# If corruption found, restore from backup
# See backup/recovery procedures in implementation guide

# Restart services
docker-compose up -d ash ash-dash
```

### Model Recovery

**NLP Model Recovery:**
```powershell
# Stop NLP server
docker-compose stop ash-nlp

# Verify model files
docker-compose exec ash-nlp ls -la /app/models/

# If models missing or corrupted, restore
# Download models from backup or retrain
# See implementation guide for model restoration

# Restart NLP server
docker-compose up -d ash-nlp

# Verify model loading
docker-compose logs ash-nlp | grep -i "model.*loaded"

# Test model functionality
curl -X POST http://10.20.30.16:8881/analyze -H "Content-Type: application/json" -d '{"text":"test message"}'
```

---

## 📋 Maintenance Procedures

### Preventive Maintenance

**Daily Maintenance Checklist:**
- [ ] Run system health check script
- [ ] Review error logs for patterns
- [ ] Check resource usage trends
- [ ] Verify backup completion
- [ ] Run quick validation test
- [ ] Review crisis response metrics

**Weekly Maintenance Tasks:**
```bash
#!/bin/bash
# weekly_maintenance.sh

echo "=== Weekly Maintenance ==="

# 1. Run comprehensive testing
curl -X POST http://10.20.30.16:8884/api/test/comprehensive

# 2. Update system packages
docker-compose pull
docker system prune -f

# 3. Analyze performance trends
curl -s http://10.20.30.16:8884/api/test/analytics/accuracy-trends?timeframe=7d

# 4. Check disk usage
df -h

# 5. Rotate logs
docker-compose logs --since 7d > logs/weekly_logs_$(date +%Y%m%d).log

# 6. Update documentation if needed
echo "Review and update troubleshooting procedures based on week's issues"
```

**Monthly Maintenance Tasks:**
- Update security patches
- Review and rotate API keys
- Comprehensive performance analysis
- Disaster recovery testing
- Team training updates
- Documentation review and updates

### Emergency Maintenance

**When to Trigger Emergency Maintenance:**
- System-wide failures affecting crisis detection
- Security incidents or breaches
- Data corruption or loss
- Multiple service failures
- Community safety concerns

**Emergency Maintenance Procedure:**
1. **Immediate Response**
   - Activate manual crisis monitoring
   - Alert crisis response team and technical leads
   - Document incident timeline

2. **Assessment**
   - Identify scope and severity of issues
   - Determine if emergency maintenance required
   - Plan maintenance window and communication

3. **Communication**
   - Notify community if service interruption expected
   - Update team on maintenance progress
   - Coordinate with crisis response team

4. **Execution**
   - Follow established recovery procedures
   - Monitor progress and document actions
   - Test thoroughly before returning to service

5. **Post-Maintenance**
   - Verify all systems operational
   - Run comprehensive testing
   - Document lessons learned
   - Update procedures as needed

---

## 📞 Escalation Procedures

### When to Escalate

**Immediate Escalation (Contact Technical Lead):**
- Main bot offline >15 minutes
- Multiple critical services failing
- Security incident detected
- Data loss or corruption
- Community safety at risk

**Standard Escalation (Contact Crisis Response Lead):**
- Detection accuracy consistently <90%
- Response time degradation
- Team member access issues
- Configuration problems

**Community Escalation (Contact Community Leadership):**
- Extended service outages (>2 hours)
- Public relations concerns
- Legal or compliance issues
- Major system architecture changes needed

### Escalation Communication Template

```
Subject: [URGENT/HIGH/MEDIUM] Ash System Issue - [Brief Description]

Issue Summary:
- System affected: [Bot/NLP/Dashboard/All]
- Impact level: [Critical/High/Medium/Low]
- Users affected: [Number or scope]
- Duration: [How long issue has persisted]

Current Status:
- [What is currently working/not working]
- [Actions taken so far]
- [Temporary workarounds in place]

Technical Details:
- Error messages: [Specific errors]
- Logs: [Relevant log excerpts]
- Diagnostics: [Health check results]

Next Steps:
- [Immediate actions planned]
- [Resources needed]
- [Estimated resolution time]

Contact: [Your name and contact info]
Incident ID: [Tracking reference]
```

---

## 📚 Knowledge Base

### Common Error Messages

**"NLP Server Connection Timeout"**
- **Cause:** NLP server overloaded or network issues
- **Solution:** Restart NLP server, check network connectivity
- **Prevention:** Monitor NLP server resources, implement load balancing

**"Discord Gateway Disconnected"**
- **Cause:** Network interruption or Discord API issues
- **Solution:** Bot should auto-reconnect, restart if persistent
- **Prevention:** Implement robust reconnection logic

**"Model Loading Failed"**
- **Cause:** Corrupted model files or insufficient GPU memory
- **Solution:** Restore model files, check GPU memory usage
- **Prevention:** Regular model validation, monitor GPU resources

**"Database Connection Pool Exhausted"**
- **Cause:** Too many concurrent connections
- **Solution:** Restart affected services, optimize connection usage
- **Prevention:** Monitor connection pools, implement connection limits

### Performance Benchmarks

**Normal Operating Parameters:**
- **Bot Response Time:** <2 seconds end-to-end
- **NLP Processing:** <3 seconds per message
- **Dashboard Load Time:** <5 seconds
- **System Uptime:** >99.5%
- **Detection Accuracy:** >95% overall

**Resource Usage Expectations:**
- **CPU:** <50% average, <80% peak
- **Memory:** <70% utilization
- **Disk:** <80% utilization
- **Network:** <100Mbps sustained

**Alert Thresholds:**
- **Response Time:** >5 seconds sustained
- **Error Rate:** >1% of requests
- **Resource Usage:** >90% for >5 minutes
- **Detection Accuracy:** <90% in testing

---

## 🔄 Continuous Improvement

### Issue Tracking

**Document All Issues:**
- Incident date and time
- Symptoms observed
- Root cause analysis
- Resolution steps taken
- Prevention measures implemented
- Lessons learned

**Monthly Review Process:**
- Analyze recurring issues
- Identify system weaknesses
- Plan infrastructure improvements
- Update troubleshooting procedures
- Train team on new procedures

### Knowledge Sharing

**Team Training:**
- Regular troubleshooting workshops
- Incident response simulations
- Cross-training on system components
- Documentation updates

**Community Contribution:**
- Share learnings with broader mental health tech community
- Contribute improvements to open source projects
- Present at conferences and meetups
- Collaborate with other crisis response organizations

---

*This troubleshooting guide supports the critical mission of providing reliable mental health crisis detection for [The Alphabet Cartel Discord community](https://discord.gg/alphabetcartel). Regular maintenance and prompt issue resolution ensure our chosen family members can always count on this safety net.*

**Built with 🖤 for chosen family everywhere.**

---

**Document Version:** 1.0  
**Last Updated:** July 27, 2025  
**Next Review:** August 27, 2025  
**Emergency Contact:** Technical Team Lead  
**Community:** [The Alphabet Cartel Discord](https://discord.gg/alphabetcartel)