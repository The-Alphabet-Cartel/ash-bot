# 🚀 ASH-BOT Deployment Guide v2.1

**Complete deployment instructions for ASH-BOT Discord crisis detection system**

**Repository**: https://github.com/the-alphabet-cartel/ash-bot  
**Ecosystem**: https://github.com/the-alphabet-cartel/ash  
**Discord**: https://discord.gg/alphabetcartel  

---

## 📋 Deployment Overview

### System Architecture

ASH-BOT runs on a dedicated Debian 12 server as part of the integrated Ash ecosystem:

```
┌─────────────────────────────────────────────────────────────────┐
│                    DEDICATED SERVER                            │
│                  IP: 10.20.30.253                              │
│                Debian 12 Linux Server                          │
│            AMD Ryzen 7 5800X | 64GB RAM | RTX 3060            │
└─────────────────────────────────────────────────────────────────┘
                                │
    ┌───────────────────────────┼───────────────────────────┐
    │                           │                           │
    ▼                           ▼                           ▼
┌─────────────┐        ┌─────────────┐        ┌─────────────┐
│  ASH-BOT    │◄──────►│  ASH-NLP    │◄──────►│ ASH-DASH    │
│ Port: 8882  │        │ Port: 8881  │        │ Port: 8883  │
│Discord Bot  │        │AI Analysis  │        │Analytics    │
│API Server   │        │Crisis Score │        │Dashboard    │
└─────────────┘        └─────────────┘        └─────────────┘
    │                           │                           │
    └───────────────────────────┼───────────────────────────┘
                                ▼
                       ┌─────────────┐
                       │ ASH-THRASH  │
                       │ Port: 8884  │
                       │Testing Suite│
                       │Quality Check│
                       └─────────────┘
```

### Service Endpoints

- **ASH-BOT API**: `http://10.20.30.253:8882`
- **NLP Integration**: `http://10.20.30.253:8881` 
- **Dashboard Reporting**: `http://10.20.30.253:8883`
- **Testing Integration**: `http://10.20.30.253:8884`
- **External Dashboard**: `https://dashboard.alphabetcartel.net`

---

## 🎯 Prerequisites

### Infrastructure Requirements

**Server Specifications:**
- **Operating System**: Debian 12 (recommended) or Ubuntu 20.04+
- **CPU**: Multi-core processor (AMD Ryzen 7 5800X or equivalent)
- **RAM**: 8GB minimum, 16GB+ recommended
- **Storage**: 50GB+ SSD storage
- **Network**: Stable internet connection with static IP

**Software Requirements:**
- **Docker**: 20.10+ and Docker Compose 2.0+
- **Git**: For repository management
- **Python**: 3.9+ (for development)
- **SSH Access**: For remote management

### Discord Application Setup

**Create Discord Bot:**
1. Go to https://discord.com/developers/applications
2. Click "New Application" and name it "Ash"
3. Navigate to "Bot" section and create a bot
4. **Copy and save the Bot Token securely**
5. Enable required bot permissions (see Configuration section)
6. Generate OAuth2 URL and invite bot to your server

**Required Discord Permissions:**
```
Permissions Integer: 8589934591
- Read Messages/View Channels
- Send Messages  
- Manage Messages
- Manage Roles
- Kick Members
- Ban Members
- Manage Channels
- View Audit Log
- Use Slash Commands
```

### Access Requirements

**GitHub Access:**
- Access to The Alphabet Cartel organization
- SSH keys configured for repository access
- Required for private repository access

**API Keys:**
- Discord Bot Token
- NLP Server API Key (generated during deployment)
- Dashboard Webhook URLs

---

## 🚀 Deployment Methods

### Method 1: Standalone ASH-BOT Deployment

**Use Case**: Deploying only the Discord bot component

```bash
# 1. Clone the repository
git clone https://github.com/the-alphabet-cartel/ash-bot.git
cd ash-bot

# 2. Configure environment
cp .env.template .env

# Edit .env with the following configuration:
cat > .env << 'EOF'
# Discord Configuration
DISCORD_TOKEN=your_discord_bot_token_here
DISCORD_GUILD_ID=your_server_id_here
CRISIS_RESPONSE_CHANNEL_ID=your_crisis_channel_id
CRISIS_RESPONSE_ROLE_ID=your_crisis_team_role_id

# Server Configuration
BOT_API_HOST=0.0.0.0
BOT_API_PORT=8882

# NLP Integration (if available)
NLP_SERVER_URL=http://10.20.30.253:8881
NLP_SERVER_API_KEY=secure_api_key_here
ENABLE_NLP_INTEGRATION=true

# Database Configuration
DATABASE_URL=sqlite:///data/ash_bot.db

# Crisis Detection Settings
HIGH_PRIORITY_THRESHOLD=0.8
MEDIUM_PRIORITY_THRESHOLD=0.6
LOW_PRIORITY_THRESHOLD=0.4
ENABLE_KEYWORD_DETECTION=true
ENABLE_AI_ANALYSIS=true

# Analytics Integration
DASHBOARD_WEBHOOK_URL=http://10.20.30.253:8883/webhook/bot_events
ENABLE_ANALYTICS_EXPORT=true

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/ash_bot.log
ENABLE_DEBUG_LOGGING=false

# Security
API_KEY=secure_api_key_for_external_access
ENABLE_API_AUTHENTICATION=true
EOF

# 3. Create required directories
mkdir -p data logs

# 4. Deploy with Docker
docker-compose up -d

# 5. Verify deployment
curl http://10.20.30.253:8882/health
```

### Method 2: Full Ecosystem Deployment (Recommended)

**Use Case**: Complete Ash crisis detection platform

```bash
# 1. Clone the main ecosystem repository
git clone --recursive https://github.com/the-alphabet-cartel/ash.git
cd ash

# 2. Configure all components
# Configure ASH-BOT
cd ash-bot
cp .env.template .env
# Edit .env with bot-specific configuration (see above)
cd ..

# Configure ASH-NLP
cd ash-nlp  
cp .env.template .env
# Edit .env with NLP configuration
cd ..

# Configure ASH-DASH
cd ash-dash
cp .env.template .env
# Edit .env with dashboard configuration  
cd ..

# Configure ASH-THRASH
cd ash-thrash
cp .env.template .env
# Edit .env with testing configuration
cd ..

# 3. Deploy complete ecosystem
docker-compose up -d

# 4. Verify all services
curl http://10.20.30.253:8882/health  # Bot
curl http://10.20.30.253:8881/health  # NLP
curl http://10.20.30.253:8883/health  # Dashboard
curl http://10.20.30.253:8884/health  # Testing

# 5. Access dashboard
open https://dashboard.alphabetcartel.net
```

### Method 3: Development Deployment

**Use Case**: Development and testing environment

```bash
# 1. Clone for development
git clone https://github.com/the-alphabet-cartel/ash-bot.git
cd ash-bot

# 2. Set up Python virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install development dependencies
pip install -r requirements-dev.txt

# 4. Configure development environment
cp .env.template .env.development

# Edit .env.development for development settings:
cat > .env.development << 'EOF'
# Development Configuration
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG

# Discord Configuration (use test server)
DISCORD_TOKEN=your_development_bot_token
DISCORD_GUILD_ID=your_test_server_id
CRISIS_RESPONSE_CHANNEL_ID=your_test_channel_id

# Local Development URLs
NLP_SERVER_URL=http://localhost:8881
DASHBOARD_WEBHOOK_URL=http://localhost:8883/webhook/bot_events

# Development Database
DATABASE_URL=sqlite:///data/ash_bot_dev.db

# Development Security (less strict)
ENABLE_API_AUTHENTICATION=false
API_KEY=dev_api_key

# Enhanced Logging for Development
ENABLE_DEBUG_LOGGING=true
LOG_FILE=logs/ash_bot_dev.log
EOF

# 5. Run in development mode
python main.py

# 6. Run development tests
pytest tests/
```

---

## ⚙️ Configuration Details

### Critical Configuration Parameters

**Discord Configuration:**
```bash
# Required: Discord bot token from Discord Developer Portal
DISCORD_TOKEN=your_discord_bot_token_here

# Required: Your Discord server ID (enable Developer Mode to copy)
DISCORD_GUILD_ID=123456789012345678

# Required: Channel where crisis alerts are sent
CRISIS_RESPONSE_CHANNEL_ID=123456789012345678

# Required: Role that gets notified for crises (@Crisis Team)
CRISIS_RESPONSE_ROLE_ID=123456789012345678

# Optional: Admin user IDs (comma-separated)
ADMIN_USER_IDS=123456789012345678,987654321098765432
```

**Crisis Detection Configuration:**
```bash
# Crisis severity thresholds (0.0 to 1.0)
HIGH_PRIORITY_THRESHOLD=0.8    # Immediate intervention required
MEDIUM_PRIORITY_THRESHOLD=0.6  # Close monitoring needed
LOW_PRIORITY_THRESHOLD=0.4     # General support offered

# Detection methods
ENABLE_KEYWORD_DETECTION=true  # Use keyword-based detection
ENABLE_AI_ANALYSIS=true        # Use NLP AI analysis (requires ash-nlp)

# Response behavior
AUTO_RESPOND_TO_CRISIS=true    # Send automatic support messages
NOTIFY_TEAM_FOR_HIGH=true      # Alert team for high-priority cases
MODERATE_HARMFUL_CONTENT=true  # Remove harmful content automatically
```

**Integration Configuration:**
```bash
# NLP Server Integration
NLP_SERVER_URL=http://10.20.30.253:8881
NLP_SERVER_API_KEY=secure_generated_api_key
NLP_TIMEOUT=30                 # Timeout for NLP requests (seconds)
NLP_RETRY_ATTEMPTS=3           # Number of retry attempts

# Dashboard Integration  
DASHBOARD_WEBHOOK_URL=http://10.20.30.253:8883/webhook/bot_events
ANALYTICS_UPDATE_INTERVAL=300  # Send stats every 5 minutes
ENABLE_ANALYTICS_EXPORT=true

# Testing Integration
TESTING_WEBHOOK_URL=http://10.20.30.253:8884/webhook/bot_test_results
ENABLE_TESTING_INTEGRATION=true
```

### Docker Configuration

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  ash-bot:
    build: .
    container_name: ash-bot
    restart: unless-stopped
    ports:
      - "8882:8882"
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
      - ./config:/app/config
    environment:
      - DISCORD_TOKEN=${DISCORD_TOKEN}
      - DISCORD_GUILD_ID=${DISCORD_GUILD_ID}
      - NLP_SERVER_URL=http://ash-nlp:8881
      - DATABASE_URL=sqlite:///data/ash_bot.db
    networks:
      - ash-network
    depends_on:
      - ash-nlp
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8882/health"]
      interval: 30s
      timeout: 10s
      retries: 3

networks:
  ash-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16

volumes:
  bot-data:
  bot-logs:
```

**Dockerfile:**
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p data logs config

# Expose port
EXPOSE 8882

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8882/health || exit 1

# Run the application
CMD ["python", "main.py"]
```

---

## 🔧 Advanced Configuration

### Database Configuration

**SQLite (Default):**
```bash
DATABASE_URL=sqlite:///data/ash_bot.db
DATABASE_POOL_SIZE=10
DATABASE_TIMEOUT=30
```

**PostgreSQL (Production):**
```bash
DATABASE_URL=postgresql://username:password@localhost:5432/ash_bot
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=30
DATABASE_POOL_TIMEOUT=30
```

**MySQL (Alternative):**
```bash
DATABASE_URL=mysql://username:password@localhost:3306/ash_bot
DATABASE_CHARSET=utf8mb4
DATABASE_POOL_SIZE=15
```

### Security Configuration

**API Security:**
```bash
# API authentication
ENABLE_API_AUTHENTICATION=true
API_KEY=secure_randomly_generated_key_here
API_RATE_LIMIT=100  # Requests per minute

# Webhook security
WEBHOOK_SECRET=secure_webhook_secret_here
ENABLE_WEBHOOK_VALIDATION=true

# Discord security
VERIFY_GUILD_MEMBERSHIP=true
REQUIRE_ROLE_FOR_COMMANDS=true
ADMIN_ONLY_COMMANDS=true
```

**Data Protection:**
```bash
# Privacy settings
ANONYMIZE_USER_DATA=true
DATA_RETENTION_DAYS=30
ENABLE_GDPR_COMPLIANCE=true
LOG_PERSONAL_DATA=false

# Encryption
ENCRYPT_SENSITIVE_DATA=true
ENCRYPTION_KEY=base64_encoded_encryption_key
```

### Performance Configuration

**Bot Performance:**
```bash
# Discord.py settings
MAX_MESSAGES_CACHED=1000
HEARTBEAT_TIMEOUT=60
GUILD_READY_TIMEOUT=30

# Processing settings
MAX_CONCURRENT_ANALYSES=10
MESSAGE_QUEUE_SIZE=1000
BATCH_PROCESSING_SIZE=50

# Caching
ENABLE_REDIS_CACHE=false
REDIS_URL=redis://localhost:6379/0
CACHE_TTL=3600  # 1 hour
```

---

## 🧪 Testing and Validation

### Pre-Deployment Testing

**Configuration Validation:**
```bash
# Test configuration file
python scripts/validate_config.py

# Test Discord connection
python scripts/test_discord_connection.py

# Test NLP integration
python scripts/test_nlp_integration.py

# Test database connection
python scripts/test_database.py
```

**Integration Testing:**
```bash
# Test complete workflow
python scripts/test_crisis_workflow.py

# Test API endpoints
python scripts/test_api_endpoints.py

# Test webhook integration
python scripts/test_webhook_integration.py
```

### Post-Deployment Validation

**Health Checks:**
```bash
# Bot health check
curl http://10.20.30.253:8882/health

# Detailed status
curl http://10.20.30.253:8882/api/status

# Integration status
curl http://10.20.30.253:8882/api/integrations/status
```

**Functional Testing:**
```bash
# Test crisis detection in test channel
# Send test message: "I'm feeling really depressed today"
# Verify bot responds appropriately

# Test team notification
# Send high-priority test message
# Verify crisis team gets notified

# Test API endpoints
curl -X POST http://10.20.30.253:8882/api/analyze \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $API_KEY" \
  -d '{"message": "test crisis message", "user_id": "123", "channel_id": "456"}'
```

### Monitoring and Logs

**Log Analysis:**
```bash
# View real-time logs
docker-compose logs -f ash-bot

# Check for errors
docker-compose logs ash-bot | grep -i error

# Monitor crisis detections
docker-compose logs ash-bot | grep -i "crisis detected"

# Check NLP integration
docker-compose logs ash-bot | grep -i "nlp"
```

**Performance Monitoring:**
```bash
# Monitor Docker stats
docker stats ash-bot

# Check memory usage
docker exec ash-bot ps aux

# Monitor API response times
curl -w "@curl-format.txt" http://10.20.30.253:8882/health
```

---

## 🚨 Troubleshooting

### Common Issues

**Bot Not Connecting to Discord:**
```bash
# Check token validity
# Verify bot permissions in Discord server
# Check firewall settings
# Review logs for connection errors

# Debug steps:
docker-compose logs ash-bot | grep -i "discord\|connection\|token"
python scripts/test_discord_connection.py
```

**NLP Integration Failing:**
```bash
# Check NLP server status
curl http://10.20.30.253:8881/health

# Test network connectivity
docker exec ash-bot ping ash-nlp

# Check API key configuration
docker exec ash-bot env | grep NLP

# Review integration logs
docker-compose logs ash-bot | grep -i nlp
```

**Crisis Detection Not Working:**
```bash
# Verify keyword configuration
# Check crisis detection thresholds
# Test with known trigger phrases
# Review detection logs

# Debug commands:
python scripts/test_crisis_detection.py
docker-compose logs ash-bot | grep -i "crisis\|detection"
```

**Performance Issues:**
```bash
# Check resource usage
docker stats ash-bot

# Analyze slow queries
# Review caching configuration
# Check database performance

# Optimization steps:
# Increase cache TTL
# Optimize database queries
# Adjust processing batch sizes
```

### Recovery Procedures

**Service Recovery:**
```bash
# Restart bot only
docker-compose restart ash-bot

# Full restart with cleanup
docker-compose down
docker-compose up -d

# Reset database (CAUTION)
docker-compose down -v
docker-compose up -d
```

**Configuration Reset:**
```bash
# Backup current configuration
cp .env .env.backup

# Reset to template
cp .env.template .env
# Reconfigure with correct values

# Restart with new configuration
docker-compose down
docker-compose up -d
```

---

## 📚 Additional Resources

### Documentation Links
- **[API Documentation](docs/tech/API_v2_1.md)** - Complete API reference
- **[Architecture Guide](docs/tech/architecture_v2_1.md)** - System design details
- **[Implementation Guide](docs/tech/implementation_v2_1.md)** - Technical implementation
- **[Team Guide](docs/team/team_guide_v2_1.md)** - Crisis response procedures
- **[Troubleshooting Guide](docs/tech/troubleshooting_v2_1.md)** - Detailed problem resolution

### External Resources
- **[Discord.py Documentation](https://discordpy.readthedocs.io/)** - Discord library reference
- **[Docker Documentation](https://docs.docker.com/)** - Containerization guide
- **[FastAPI Documentation](https://fastapi.tiangolo.com/)** - API framework reference

### Support Channels
- **Discord Community**: https://discord.gg/alphabetcartel (#tech-support)
- **GitHub Issues**: https://github.com/the-alphabet-cartel/ash-bot/issues
- **Documentation**: Complete guides in docs/ directory

---

**Deployment successful! Your ASH-BOT is now ready to help keep your community safe and supported.**

🌈 **Discord**: https://discord.gg/alphabetcartel | 🌐 **Website**: https://alphabetcartel.org