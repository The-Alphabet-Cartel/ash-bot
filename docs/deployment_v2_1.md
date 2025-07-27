# Ash v2.1 Complete Ecosystem Deployment Guide

**Comprehensive deployment instructions for the complete Ash crisis detection platform**

This guide provides step-by-step instructions for deploying the complete Ash v2.1 ecosystem, including the main Discord bot, NLP server, analytics dashboard, and testing suite across your infrastructure.

---

## 🎯 Deployment Overview

### System Architecture Summary

The Ash v2.1 ecosystem consists of four integrated services:

- **🤖 Ash Bot** - Main Discord bot (Linux server: 10.20.30.253:8882)
- **🧠 Ash-NLP** - AI processing server (Windows 11: 10.20.30.16:8881)
- **📊 Ash-Dash** - Analytics dashboard (Windows 11: 10.20.30.16:8883)
- **🧪 Ash-Thrash** - Testing suite (Windows 11: 10.20.30.16:8884)

### Deployment Prerequisites

**Infrastructure Requirements:**
- **Linux Server** (Debian/Ubuntu) with Docker for main bot
- **Windows 11 Server** with Docker Desktop, RTX 3050 GPU, Ryzen 7 7700X, 64GB RAM
- **Network connectivity** between servers
- **GitHub access** to The Alphabet Cartel organization repositories
- **Discord Bot Application** with proper permissions

**Required Accounts & Tokens:**
- Discord Bot Token with appropriate permissions
- Claude 4 Sonnet API key from Anthropic
- GitHub access to private repositories
- SSL certificates for HTTPS dashboard (optional but recommended)

---

## 🚀 Quick Deployment (Experienced Users)

### One-Command Deployment

```bash
# Clone all repositories
git clone https://github.com/The-Alphabet-Cartel/ash.git
git clone https://github.com/The-Alphabet-Cartel/ash-nlp.git
git clone https://github.com/The-Alphabet-Cartel/ash-dash.git
git clone https://github.com/The-Alphabet-Cartel/ash-thrash.git

# Configure all services (edit .env files)
cd ash && cp .env.template .env && cd ..
cd ash-nlp && cp .env.template .env && cd ..
cd ash-dash && cp .env.template .env && cd ..
cd ash-thrash && cp .env.template .env && cd ..

# Deploy complete ecosystem
cd ash && docker-compose up -d && cd ..
cd ash-nlp && docker-compose up -d && cd ..
cd ash-dash && docker-compose up -d && cd ..
cd ash-thrash && docker-compose up -d && cd ..

# Verify deployment
curl http://10.20.30.253:8882/health  # Bot
curl http://10.20.30.16:8881/health   # NLP
curl http://10.20.30.16:8883/health   # Dashboard
curl http://10.20.30.16:8884/health   # Testing
```

### Quick Verification

```bash
# Access analytics dashboard
open https://10.20.30.16:8883

# Run quick test
curl -X POST http://10.20.30.16:8884/api/test/quick-validation

# Check Discord bot status
# Bot should appear online in Discord server
```

---

## 📋 Detailed Step-by-Step Deployment

### Phase 1: Prerequisites Setup

#### 1.1 Discord Bot Application Setup

**Create Discord Application:**
1. Go to https://discord.com/developers/applications
2. Click "New Application" and name it "Ash"
3. Go to "Bot" section and create a bot
4. **Save the Bot Token** securely
5. Enable all necessary Intents:
   - Presence Intent
   - Server Members Intent
   - Message Content Intent

**Generate Invite URL:**
1. Go to "OAuth2" > "URL Generator"
2. Select scopes: `bot` and `applications.commands`
3. Select permissions:
   - Read Messages/View Channels
   - Send Messages
   - Read Message History
   - Use Slash Commands
   - Manage Messages (optional)
4. **Invite bot to your Discord server** using generated URL

#### 1.2 API Keys and Accounts

**Anthropic Claude API:**
1. Sign up at https://console.anthropic.com/
2. Generate API key for Claude 4 Sonnet
3. **Save API key securely**
4. Verify you have access to `claude-sonnet-4-20250514` model

**GitHub Access:**
1. Ensure access to The Alphabet Cartel organization
2. Generate Personal Access Token if using HTTPS
3. Configure SSH keys if using SSH authentication

#### 1.3 Server Preparation

**Linux Server (10.20.30.253):**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker and Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo apt install docker-compose -y

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Verify installation
docker --version
docker-compose --version

# Create application directory
sudo mkdir -p /opt/ash
sudo chown $USER:$USER /opt/ash
```

**Windows 11 Server (10.20.30.16):**
```powershell
# Install Docker Desktop for Windows
# Download from: https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe
# Follow installation wizard and enable WSL2 integration

# Install Windows Subsystem for Linux (if needed)
wsl --install

# Verify Docker installation
docker --version
docker-compose --version

# Install NVIDIA Container Toolkit for GPU access
# Follow guide: https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html

# Verify GPU access
docker run --rm --gpus all nvidia/cuda:11.0-base nvidia-smi

# Create project directories
New-Item -Path "C:\Projects" -ItemType Directory -Force
```

### Phase 2: Service Deployment

#### 2.1 Deploy Main Bot (Linux Server)

**Clone and Configure:**
```bash
# SSH into Linux server (10.20.30.253)
ssh admin@10.20.30.253

# Clone repository
cd /opt
sudo git clone https://github.com/The-Alphabet-Cartel/ash.git
sudo chown -R $USER:$USER ash
cd ash

# Create environment configuration
cp .env.template .env
```

**Configure Environment (.env):**
```bash
# Edit .env file
nano .env

# Required configuration:
DISCORD_TOKEN=your_discord_bot_token_here
GUILD_ID=your_discord_server_id_here
CLAUDE_API_KEY=your_claude_api_key_here
CLAUDE_MODEL=claude-sonnet-4-20250514

# Channel Configuration
RESOURCES_CHANNEL_ID=your_resources_channel_id
CRISIS_RESPONSE_CHANNEL_ID=your_crisis_response_channel_id
ALLOWED_CHANNELS=channel_id_1,channel_id_2,channel_id_3

# Team Configuration
STAFF_PING_USER=staff_user_id_here
CRISIS_RESPONSE_ROLE_ID=crisis_team_role_id_here

# Learning System
ENABLE_LEARNING_SYSTEM=true
LEARNING_CONFIDENCE_THRESHOLD=0.6
MAX_LEARNING_ADJUSTMENTS_PER_DAY=50

# NLP Server Integration
NLP_SERVICE_HOST=10.20.30.16
NLP_SERVICE_PORT=8881

# Dashboard Integration
DASHBOARD_URL=https://10.20.30.16:8883
ENABLE_DASHBOARD_INTEGRATION=true

# Testing Integration
TESTING_API_URL=http://10.20.30.16:8884
ENABLE_AUTOMATED_TESTING=true

# Optional Settings
LOG_LEVEL=INFO
MAX_DAILY_CALLS=1000
RATE_LIMIT_PER_USER=10
```

**Deploy Bot:**
```bash
# Build and start bot
docker-compose build
docker-compose up -d

# Verify deployment
docker-compose ps
docker-compose logs ash

# Check health endpoint
curl http://localhost:8882/health
```

#### 2.2 Deploy NLP Server (Windows 11)

**Clone and Configure:**
```powershell
# On Windows 11 server (10.20.30.16)
cd C:\Projects

# Clone NLP repository
git clone https://github.com/The-Alphabet-Cartel/ash-nlp.git
cd ash-nlp

# Create environment configuration
Copy-Item .env.template .env
```

**Configure Environment (.env):**
```powershell
# Edit .env file
notepad .env

# Required configuration:
NODE_ENV=production
NLP_SERVER_HOST=0.0.0.0
NLP_SERVER_PORT=8881

# AI Model Configuration
MODEL_PATH=models/crisis_detection_model
MODEL_TYPE=transformers
CUDA_VISIBLE_DEVICES=0

# Processing Configuration
MAX_BATCH_SIZE=32
PROCESSING_TIMEOUT=30
CACHE_SIZE=1000

# Learning Integration
ENABLE_LEARNING_UPDATES=true
LEARNING_MODEL_PATH=models/learning_adjustments

# API Configuration
API_KEY=secure_api_key_for_internal_communication

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/nlp_server.log
```

**Deploy NLP Server:**
```powershell
# Build and start NLP server
docker-compose build
docker-compose up -d

# Verify deployment
docker-compose ps
docker-compose logs ash-nlp

# Check health endpoint
curl http://localhost:8881/health

# Test GPU access
docker-compose exec ash-nlp python -c "import torch; print(torch.cuda.is_available())"
```

#### 2.3 Deploy Analytics Dashboard (Windows 11)

**Clone and Configure:**
```powershell
# Continue on Windows 11 server (10.20.30.16)
cd C:\Projects

# Clone dashboard repository
git clone https://github.com/The-Alphabet-Cartel/ash-dash.git
cd ash-dash

# Create environment configuration
Copy-Item .env.template .env
```

**Configure Environment (.env):**
```powershell
# Edit .env file
notepad .env

# Server Configuration
NODE_ENV=production
PORT=8883
ENABLE_SSL=true

# SSL Configuration (create certificates first)
SSL_CERT_PATH=C:\Projects\ash-dash\certs\cert.pem
SSL_KEY_PATH=C:\Projects\ash-dash\certs\key.pem

# Service Endpoints
ASH_BOT_API=http://10.20.30.253:8882
ASH_NLP_API=http://localhost:8881
ASH_TESTING_API=http://localhost:8884

# Dashboard Branding
DASHBOARD_TITLE="Ash Analytics Dashboard"
DASHBOARD_SUBTITLE="The Alphabet Cartel Crisis Detection Analytics"
COMMUNITY_NAME="The Alphabet Cartel"
COMMUNITY_DISCORD="https://discord.gg/alphabetcartel"

# Performance Settings
CACHE_TTL=600
HEALTH_CHECK_INTERVAL=120000
METRICS_UPDATE_INTERVAL=60000

# Security
ENABLE_CORS=true
RATE_LIMIT_WINDOW=900000
RATE_LIMIT_MAX=100
SESSION_TIMEOUT=3600

# Authentication (optional)
ADMIN_USERNAME=admin
ADMIN_PASSWORD=secure_password_here

# Database
DATABASE_URL=sqlite:///data/dashboard.db
```

**Generate SSL Certificates (Recommended):**
```powershell
# Create certificate directory
New-Item -Path "C:\Projects\ash-dash\certs" -ItemType Directory -Force
cd C:\Projects\ash-dash\certs

# Generate self-signed certificate (for development/internal use)
# Install OpenSSL for Windows first
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes

# Or use PowerShell (Windows 10+)
$cert = New-SelfSignedCertificate -DnsName "10.20.30.16" -CertStoreLocation "cert:\LocalMachine\My"
Export-Certificate -Cert $cert -FilePath "cert.pem"
```

**Deploy Dashboard:**
```powershell
# Build and start dashboard
docker-compose build
docker-compose up -d

# Verify deployment
docker-compose ps
docker-compose logs ash-dash

# Check health endpoint
curl http://localhost:8883/health

# Access dashboard
start https://localhost:8883
```

#### 2.4 Deploy Testing Suite (Windows 11)

**Clone and Configure:**
```powershell
# Continue on Windows 11 server (10.20.30.16)
cd C:\Projects

# Clone testing repository
git clone https://github.com/The-Alphabet-Cartel/ash-thrash.git
cd ash-thrash

# Create environment configuration
Copy-Item .env.template .env
```

**Configure Environment (.env):**
```powershell
# Edit .env file
notepad .env

# Testing Configuration
NODE_ENV=production
PORT=8884

# Target Services
NLP_SERVER_URL=http://localhost:8881
ASH_BOT_URL=http://10.20.30.253:8882
DASHBOARD_URL=http://localhost:8883

# Test Configuration
COMPREHENSIVE_TEST_SIZE=350
QUICK_TEST_SIZE=10
TEST_TIMEOUT=60
PARALLEL_TESTS=4

# Accuracy Targets
OVERALL_ACCURACY_TARGET=0.85
HIGH_CRISIS_ACCURACY_TARGET=1.0
MEDIUM_CRISIS_ACCURACY_TARGET=0.95
LOW_CRISIS_ACCURACY_TARGET=0.90

# Automated Testing
ENABLE_SCHEDULED_TESTING=true
TESTING_SCHEDULE="0 6 * * *"    # Daily at 6 AM
ACCURACY_ALERT_THRESHOLD=0.85

# Results & Reporting
RESULTS_RETENTION_DAYS=30
ENABLE_PERFORMANCE_TRACKING=true
ENABLE_TREND_ANALYSIS=true

# Notifications
DISCORD_WEBHOOK_URL=your_webhook_url_for_test_results
ALERT_ON_FAILURE_RATE=0.1
```

**Deploy Testing Suite:**
```powershell
# Build and start testing suite
docker-compose build
docker-compose up -d

# Verify deployment
docker-compose ps
docker-compose logs ash-thrash

# Check health endpoint
curl http://localhost:8884/health

# Run initial test
curl -X POST http://localhost:8884/api/test/quick-validation
```

### Phase 3: System Integration & Verification

#### 3.1 Complete System Health Check

**Automated Health Check Script:**
```bash
#!/bin/bash
# save as check_ash_health.sh

echo "=== Ash v2.1 Complete Ecosystem Health Check ==="
echo "Timestamp: $(date)"
echo

# Check all services
services=(
    "10.20.30.253:8882|Ash Bot"
    "10.20.30.16:8881|NLP Server"
    "10.20.30.16:8883|Dashboard"
    "10.20.30.16:8884|Testing Suite"
)

for service in "${services[@]}"; do
    IFS='|' read -r url name <<< "$service"
    echo -n "Checking $name ($url)... "
    
    if curl -f -s "http://$url/health" > /dev/null; then
        echo "✅ HEALTHY"
    else
        echo "❌ UNHEALTHY"
    fi
done

echo
echo "=== Integration Test ==="
echo "Running quick validation test..."
response=$(curl -s -X POST http://10.20.30.16:8884/api/test/quick-validation)
accuracy=$(echo $response | jq -r '.results.accuracy_percent' 2>/dev/null || echo "unknown")
echo "Detection Accuracy: $accuracy%"

echo
echo "=== Dashboard Access ==="
echo "Analytics Dashboard: https://10.20.30.16:8883"
echo "System Status: All services operational"
```

**Run Health Check:**
```bash
chmod +x check_ash_health.sh
./check_ash_health.sh
```

#### 3.2 Discord Integration Verification

**Test Discord Bot:**
1. **Check Bot Status** - Bot should appear online in Discord
2. **Test Slash Commands** - Use `/keyword_stats` to verify commands work
3. **Test Crisis Detection** - Send test message in allowed channel
4. **Verify Team Alerts** - Ensure crisis team receives appropriate notifications

**Test Learning System:**
```bash
# In Discord, as Crisis Response team member:
/learning_stats
# Should show learning system status and statistics

# Test false positive reporting (use a non-crisis message):
/report_false_positive message_link:... detected_level:High correct_level:None context:Test message
```

#### 3.3 Dashboard Integration Test

**Access Dashboard:**
1. **Open Browser** - Go to https://10.20.30.16:8883
2. **Verify SSL** - Check certificate is working (or accept self-signed)
3. **Check Real-time Data** - Verify crisis alerts and system metrics display
4. **Test Mobile** - Access dashboard from mobile device

**Verify Data Flow:**
1. **Send Test Crisis Message** in Discord
2. **Check Dashboard** - Alert should appear in real-time
3. **Verify Analytics** - Charts and metrics should update
4. **Test Team Coordination** - Use dashboard to coordinate response

#### 3.4 Testing Suite Validation

**Run Comprehensive Test:**
```bash
curl -X POST http://10.20.30.16:8884/api/test/comprehensive
```

**Monitor Test Progress:**
```bash
# Check test status
curl http://10.20.30.16:8884/api/test/status

# View results
curl http://10.20.30.16:8884/api/test/results/latest
```

**Verify Scheduled Testing:**
```bash
# Check that daily testing is scheduled
curl http://10.20.30.16:8884/api/test/schedule
```

---

## 🔧 Configuration Management

### Centralized Configuration

**Configuration File Locations:**
- **Main Bot:** `/opt/ash/.env` (Linux)
- **NLP Server:** `C:\Projects\ash-nlp\.env` (Windows)
- **Dashboard:** `C:\Projects\ash-dash\.env` (Windows)
- **Testing:** `C:\Projects\ash-thrash\.env` (Windows)

**Environment Template Management:**
```bash
# Keep templates updated
cd /opt/ash && git pull origin main && cp .env.template .env.new
# Compare and merge new settings

cd C:\Projects\ash-nlp && git pull origin main && Compare-Object (Get-Content .env.template) (Get-Content .env)
```

### Network Configuration

**Firewall Setup (Linux Server):**
```bash
# Configure UFW firewall
sudo ufw allow ssh
sudo ufw allow 8882  # Ash Bot API
sudo ufw allow from 10.20.30.16  # Allow Windows server access
sudo ufw enable
```

**Windows Firewall (Windows Server):**
```powershell
# Allow inbound connections for services
New-NetFirewallRule -DisplayName "Ash-NLP" -Direction Inbound -Port 8881 -Protocol TCP -Action Allow
New-NetFirewallRule -DisplayName "Ash-Dashboard" -Direction Inbound -Port 8883 -Protocol TCP -Action Allow
New-NetFirewallRule -DisplayName "Ash-Testing" -Direction Inbound -Port 8884 -Protocol TCP -Action Allow
```

### Docker Network Configuration

**Custom Docker Network (Optional):**
```yaml
# Add to all docker-compose.yml files
networks:
  ash-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16

services:
  # Add to each service:
  networks:
    - ash-network
```

---

## 🔄 Update & Maintenance Procedures

### Update Process

**Complete Ecosystem Update:**
```bash
# Create update script: update_ash_ecosystem.sh
#!/bin/bash

echo "=== Ash v2.1 Ecosystem Update ==="

# Backup current state
mkdir -p backups/$(date +%Y%m%d_%H%M%S)
docker-compose exec ash tar -czf /tmp/ash-data-backup.tar.gz /app/data
docker cp ash:/tmp/ash-data-backup.tar.gz backups/$(date +%Y%m%d_%H%M%S)/

# Update repositories
cd /opt/ash && git pull origin main
cd /path/to/ash-nlp && git pull origin main
cd /path/to/ash-dash && git pull origin main
cd /path/to/ash-thrash && git pull origin main

# Pull latest images
cd /opt/ash && docker-compose pull
cd /path/to/ash-nlp && docker-compose pull
cd /path/to/ash-dash && docker-compose pull
cd /path/to/ash-thrash && docker-compose pull

# Deploy updates
cd /opt/ash && docker-compose up -d
cd /path/to/ash-nlp && docker-compose up -d
cd /path/to/ash-dash && docker-compose up -d
cd /path/to/ash-thrash && docker-compose up -d

# Verify update
./check_ash_health.sh

echo "Update completed. Check health status above."
```

### Backup Procedures

**Automated Backup Script:**
```bash
#!/bin/bash
# save as backup_ash_ecosystem.sh

BACKUP_DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/ash_ecosystem_$BACKUP_DATE"

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup bot data
docker-compose exec ash tar -czf /tmp/ash_data.tar.gz /app/data
docker cp ash:/tmp/ash_data.tar.gz $BACKUP_DIR/

# Backup NLP models and data
docker-compose exec ash-nlp tar -czf /tmp/nlp_data.tar.gz /app/models /app/data
docker cp ash-nlp:/tmp/nlp_data.tar.gz $BACKUP_DIR/

# Backup dashboard data
docker-compose exec ash-dash tar -czf /tmp/dashboard_data.tar.gz /app/data
docker cp ash-dash:/tmp/dashboard_data.tar.gz $BACKUP_DIR/

# Backup testing data
docker-compose exec ash-thrash tar -czf /tmp/testing_data.tar.gz /app/data
docker cp ash-thrash:/tmp/testing_data.tar.gz $BACKUP_DIR/

# Backup configurations
cp /opt/ash/.env $BACKUP_DIR/ash_config.env
cp /path/to/ash-nlp/.env $BACKUP_DIR/nlp_config.env
cp /path/to/ash-dash/.env $BACKUP_DIR/dashboard_config.env
cp /path/to/ash-thrash/.env $BACKUP_DIR/testing_config.env

# Compress entire backup
tar -czf "$BACKUP_DIR.tar.gz" $BACKUP_DIR
rm -rf $BACKUP_DIR

echo "Backup completed: $BACKUP_DIR.tar.gz"
```

### Rollback Procedures

**Emergency Rollback Script:**
```bash
#!/bin/bash
# save as rollback_ash_ecosystem.sh

BACKUP_FILE=$1

if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: $0 <backup_file.tar.gz>"
    echo "Available backups:"
    ls -la /backups/ash_ecosystem_*.tar.gz
    exit 1
fi

echo "Rolling back to: $BACKUP_FILE"

# Stop all services
cd /opt/ash && docker-compose down
cd /path/to/ash-nlp && docker-compose down
cd /path/to/ash-dash && docker-compose down
cd /path/to/ash-thrash && docker-compose down

# Extract backup
tar -xzf $BACKUP_FILE -C /tmp/

# Restore data
docker-compose up -d ash  # Start bot first
docker cp /tmp/ash_ecosystem_*/ash_data.tar.gz ash:/tmp/
docker-compose exec ash tar -xzf /tmp/ash_data.tar.gz -C /app/

# Restore other services similarly...
# [Add restoration steps for each service]

# Restart all services
cd /opt/ash && docker-compose up -d
cd /path/to/ash-nlp && docker-compose up -d
cd /path/to/ash-dash && docker-compose up -d
cd /path/to/ash-thrash && docker-compose up -d

# Verify rollback
./check_ash_health.sh

echo "Rollback completed"
```

---

## 🛡️ Security Configuration

### SSL/TLS Setup

**Generate Production SSL Certificates:**
```bash
# For production use, get certificates from Let's Encrypt
sudo apt install certbot
sudo certbot certonly --standalone -d your-domain.com

# Copy certificates to dashboard
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem /path/to/ash-dash/certs/cert.pem
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem /path/to/ash-dash/certs/key.pem
sudo chown $USER:$USER /path/to/ash-dash/certs/*
```

### Access Control

**API Security Configuration:**
```bash
# Generate secure API keys
INTERNAL_API_KEY=$(openssl rand -hex 32)
DASHBOARD_SECRET=$(openssl rand -hex 32)

# Add to all .env files
echo "INTERNAL_API_KEY=$INTERNAL_API_KEY" >> .env
echo "DASHBOARD_SECRET_KEY=$DASHBOARD_SECRET" >> .env
```

**User Authentication Setup:**
```bash
# Configure dashboard authentication
# Edit ash-dash/.env
ENABLE_AUTHENTICATION=true
ADMIN_USERNAME=admin
ADMIN_PASSWORD=$(openssl rand -base64 32)
SESSION_SECRET=$(openssl rand -hex 32)
```

### Network Security

**VPN Setup (Optional but Recommended):**
```bash
# Install WireGuard VPN for secure access
sudo apt install wireguard

# Generate VPN configuration
# [Follow WireGuard setup guide for secure remote access]
```

**IP Whitelisting:**
```bash
# Restrict dashboard access to specific IPs
# Edit ash-dash/.env
ALLOWED_IPS=192.168.1.0/24,10.0.0.0/8
ENABLE_IP_WHITELIST=true
```

---

## 📊 Monitoring & Alerting

### Log Management

**Centralized Logging Setup:**
```yaml
# Add to all docker-compose.yml files
logging:
  driver: "json-file"
  options:
    max-size: "100m"
    max-file: "5"
    labels: "service,environment"
```

**Log Rotation:**
```bash
# Create logrotate configuration
sudo tee /etc/logrotate.d/ash-ecosystem << EOF
/opt/ash/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 $USER $USER
    postrotate
        docker-compose -f /opt/ash/docker-compose.yml restart ash
    endscript
}
EOF
```

### Health Monitoring

**Automated Health Monitoring:**
```bash
# Create systemd service for health monitoring
sudo tee /etc/systemd/system/ash-health-monitor.service << EOF
[Unit]
Description=Ash Ecosystem Health Monitor
After=docker.service

[Service]
Type=oneshot
User=$USER
ExecStart=/opt/ash/check_ash_health.sh
WorkingDirectory=/opt/ash

[Install]
WantedBy=multi-user.target
EOF

# Create timer for regular health checks
sudo tee /etc/systemd/system/ash-health-monitor.timer << EOF
[Unit]
Description=Run Ash Health Monitor every 5 minutes
Requires=ash-health-monitor.service

[Timer]
OnCalendar=*:0/5
Persistent=true

[Install]
WantedBy=timers.target
EOF

# Enable and start timer
sudo systemctl enable ash-health-monitor.timer
sudo systemctl start ash-health-monitor.timer
```

### Alerting Setup

**Discord Webhook Alerts:**
```bash
# Configure webhook for system alerts
# Add to testing suite .env
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/your_webhook_url

# Configure alert thresholds
ACCURACY_ALERT_THRESHOLD=0.85
RESPONSE_TIME_ALERT_THRESHOLD=5000
UPTIME_ALERT_THRESHOLD=0.99
```

---

## 🚨 Troubleshooting

### Common Deployment Issues

**Issue: Docker Permission Denied**
```bash
# Solution: Add user to docker group
sudo usermod -aG docker $USER
newgrp docker
# Or restart your session
```

**Issue: GPU Not Available in NLP Container**
```powershell
# Solution: Install NVIDIA Container Toolkit
# Download from: https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html

# Verify GPU access
docker run --rm --gpus all nvidia/cuda:11.0-base nvidia-smi
```

**Issue: SSL Certificate Errors**
```bash
# Solution: Regenerate certificates
cd /path/to/ash-dash/certs
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes

# Or disable SSL temporarily
echo "ENABLE_SSL=false" >> .env
```

**Issue: Service Communication Failures**
```bash
# Solution: Check network connectivity
ping 10.20.30.16
telnet 10.20.30.16 8881

# Check firewall rules
sudo ufw status
netsh advfirewall show allprofiles
```

### Performance Optimization

**Memory Optimization:**
```yaml
# Add to docker-compose.yml
deploy:
  resources:
    limits:
      memory: 2G
    reservations:
      memory: 1G
```

**CPU Optimization:**
```yaml
# Add CPU limits
deploy:
  resources:
    limits:
      cpus: '2.0'
    reservations:
      cpus: '1.0'
```

### Emergency Recovery

**Complete System Recovery:**
```bash
#!/bin/bash
# save as emergency_recovery.sh

echo "=== Emergency Recovery Procedure ==="

# Stop all services
docker-compose down  # In each service directory

# Clean Docker system
docker system prune -af
docker volume prune -f

# Pull fresh images
docker-compose pull  # In each service directory

# Restore from backup
LATEST_BACKUP=$(ls -t /backups/ash_ecosystem_*.tar.gz | head -1)
echo "Restoring from: $LATEST_BACKUP"
tar -xzf $LATEST_BACKUP -C /tmp/

# Restart services with backup data
# [Add specific restoration steps]

# Verify recovery
./check_ash_health.sh
```

---

## 📋 Post-Deployment Checklist

### Immediate Verification (First 24 Hours)

- [ ] **All Services Online** - Verify health endpoints respond
- [ ] **Discord Bot Active** - Bot appears online and responds to commands
- [ ] **Crisis Detection Working** - Test with safe crisis language
- [ ] **Dashboard Accessible** - Can access analytics dashboard via HTTPS
- [ ] **Learning System Active** - `/learning_stats` shows system enabled
- [ ] **Testing Suite Running** - Quick validation test passes
- [ ] **Team Commands Working** - Crisis Response team can use slash commands
- [ ] **Mobile Access** - Dashboard works on mobile devices
- [ ] **SSL Certificates Valid** - No certificate warnings
- [ ] **Backup System Working** - Automated backups completing

### Week 1 Validation

- [ ] **Detection Accuracy** - Accuracy meets targets (>85% overall)
- [ ] **False Positive Rate** - Under 8% inappropriate alerts
- [ ] **Response Times** - Under 3 seconds end-to-end
- [ ] **Learning System** - Community corrections improving accuracy
- [ ] **Team Training** - Crisis Response team trained on new dashboard
- [ ] **Daily Testing** - Automated testing running at 6 AM daily
- [ ] **Performance Monitoring** - All metrics within expected ranges
- [ ] **Cost Tracking** - API usage within budget expectations
- [ ] **Community Feedback** - Positive reception from community members
- [ ] **Documentation Current** - All team guides reflect actual deployment

### Month 1 Assessment

- [ ] **System Stability** - 99%+ uptime achieved
- [ ] **Learning Effectiveness** - Measurable accuracy improvements
- [ ] **Team Efficiency** - Faster crisis response times
- [ ] **Cost Optimization** - 80%+ reduction in AI costs achieved
- [ ] **Quality Assurance** - Testing suite catching regressions
- [ ] **Community Adaptation** - LGBTQIA+-specific patterns recognized
- [ ] **Performance Trends** - Improving metrics over time
- [ ] **Security Audit** - No security incidents or vulnerabilities
- [ ] **Backup Validation** - Recovery procedures tested successfully
- [ ] **Team Satisfaction** - Crisis Response team satisfied with tools

---

## 📞 Support & Next Steps

### Getting Help

**Technical Support:**
- **GitHub Issues** - Report bugs and technical problems
- **Discord #tech-support** - Community assistance
- **Documentation** - Comprehensive guides for troubleshooting

**Training Resources:**
- **Team Guide v2.1** - Complete usage instructions for Crisis Response team
- **Video Tutorials** - Available in Discord resources channel
- **Best Practices** - Community-tested optimization strategies

### Ongoing Maintenance

**Daily Tasks:**
- Check system health dashboard
- Review crisis response metrics
- Monitor learning system progress

**Weekly Tasks:**
- Review testing suite results
- Update security patches
- Analyze performance trends

**Monthly Tasks:**
- Comprehensive system review
- Team training updates
- Documentation updates

### Future Enhancements

**Planned v2.2 Features:**
- Enhanced mobile application
- Advanced team management tools
- External service integrations
- Multi-language support

**Long-term Roadmap:**
- Voice channel integration
- Predictive analytics
- Professional service APIs
- Advanced AI capabilities

---

**Deployment completed! Your Ash v2.1 ecosystem is now providing comprehensive crisis detection and response capabilities for [The Alphabet Cartel Discord community](https://discord.gg/alphabetcartel).**

**Built with 🖤 for chosen family everywhere.**

---

**Document Version:** 1.0  
**Last Updated:** July 27, 2025  
**Next Review:** Monthly with major updates  
**Support Contact:** Technical Team Lead  
**Community:** [The Alphabet Cartel Discord](https://discord.gg/alphabetcartel)