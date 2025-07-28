# 🤖 ASH-BOT: Discord Crisis Detection and Community Support

**Advanced Discord bot for crisis detection and community mental health support**

[![Docker](https://img.shields.io/badge/Docker-Ready-blue?logo=docker)](https://docker.com)
[![Python](https://img.shields.io/badge/Python-3.9+-blue?logo=python)](https://python.org)
[![Discord.py](https://img.shields.io/badge/Discord.py-2.3+-purple?logo=discord)](https://discordpy.readthedocs.io/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

**Repository**: https://github.com/the-alphabet-cartel/ash-bot  
**Main Project**: https://github.com/the-alphabet-cartel/ash  
**Discord Community**: https://discord.gg/alphabetcartel  
**Website**: https://alphabetcartel.org  

---

## 🌟 Overview

ASH-BOT is the core Discord bot component of The Alphabet Cartel's comprehensive crisis detection and community support ecosystem. It monitors Discord conversations in real-time, detects potential mental health crises, and provides immediate support while alerting trained response teams.

### Key Features

🔍 **Real-Time Crisis Detection**
- Advanced keyword and phrase detection
- Integration with AI-powered NLP analysis
- Multi-level crisis severity assessment
- Context-aware message analysis

🚨 **Immediate Response System**
- Automated crisis intervention messages
- Crisis response team notifications
- Escalation management
- Safe space creation and moderation

🤝 **Community Support Tools**
- Mental health resource distribution
- Supportive response suggestions
- Community wellness monitoring
- Anonymous reporting systems

📊 **Analytics and Insights**
- Real-time dashboard integration
- Crisis pattern analysis
- Response effectiveness tracking
- Community health metrics

## 🏗️ Architecture

ASH-BOT operates as part of the integrated Ash ecosystem on dedicated server infrastructure:

```
┌─────────────────────────────────────────────────────────────────┐
│                    DEDICATED SERVER                            │
│                  IP: 10.20.30.253                              │
│                Debian 12 Linux Server                          │
│            AMD Ryzen 7 5800X | 64GB RAM | RTX 3060            │
└─────────────────────────────────────────────────────────────────┘
                                │
         ┌──────────────────────┼──────────────────────┐
         │                      │                      │
         ▼                      ▼                      ▼
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│    ASH-BOT       │  │    ASH-NLP       │  │   ASH-DASH       │
│  Port: 8882      │◄─│  Port: 8881      │─►│  Port: 8883      │
│  Discord Bot     │  │  AI Analysis     │  │  Dashboard       │
│  API Server      │  │  Crisis Scoring  │  │  Analytics       │
└──────────────────┘  └──────────────────┘  └──────────────────┘
         │                      │                      │
         └──────────────────────┼──────────────────────┘
                                ▼
                   ┌──────────────────────┐
                   │     ASH-THRASH       │
                   │    Port: 8884        │
                   │   Testing Suite      │
                   │   Quality Assurance  │
                   └──────────────────────┘
```

### System Integration

- **NLP Integration**: Sends messages to ASH-NLP for advanced AI analysis
- **Dashboard Reporting**: Real-time metrics and alerts to ASH-DASH
- **Quality Validation**: Continuous testing via ASH-THRASH
- **API Endpoints**: RESTful API for external integrations

## 🚀 Quick Start

### Production Deployment (Docker - Recommended)

```bash
# Clone the repository
git clone https://github.com/the-alphabet-cartel/ash-bot.git
cd ash-bot

# Configure environment
cp .env.template .env
# Edit .env with your Discord token and configuration

# Deploy with Docker
docker-compose up -d

# Verify deployment
curl http://10.20.30.253:8882/health
```

### Development Setup

```bash
# Clone and setup development environment
git clone https://github.com/the-alphabet-cartel/ash-bot.git
cd ash-bot

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements-dev.txt

# Configure environment
cp .env.template .env
# Edit .env for development settings

# Run bot
python main.py
```

### Integration with Full Ecosystem

```bash
# Deploy complete ecosystem (recommended)
git clone --recursive https://github.com/the-alphabet-cartel/ash.git
cd ash

# Configure all components
for component in ash-bot ash-nlp ash-dash ash-thrash; do
  cd $component && cp .env.template .env && cd ..
done

# Deploy all services
docker-compose up -d

# Verify ecosystem health
curl http://10.20.30.253:8882/health  # Bot
curl http://10.20.30.253:8881/health  # NLP
curl http://10.20.30.253:8883/health  # Dashboard
curl http://10.20.30.253:8884/health  # Testing
```

## ⚙️ Configuration

### Environment Variables

```bash
# Discord Configuration
DISCORD_TOKEN=your_discord_bot_token
DISCORD_GUILD_ID=your_server_id
CRISIS_RESPONSE_CHANNEL_ID=your_crisis_channel_id
CRISIS_RESPONSE_ROLE_ID=your_crisis_team_role_id

# Server Configuration
BOT_API_HOST=0.0.0.0
BOT_API_PORT=8882

# NLP Integration
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

# Security
API_KEY=secure_api_key_for_external_access
ENABLE_API_AUTHENTICATION=true
```

### Discord Permissions

The bot requires the following Discord permissions:

- **Read Messages/View Channels**: Monitor conversations
- **Send Messages**: Provide crisis responses
- **Manage Messages**: Moderate harmful content
- **Manage Roles**: Assign crisis support roles
- **Kick Members**: Remove disruptive users during crises
- **Ban Members**: Handle severe cases
- **Manage Channels**: Create safe spaces
- **View Audit Log**: Track moderation actions

## 📊 API Reference

### Health Check
```bash
GET /health
# Returns bot status and connectivity to other services
```

### Crisis Detection
```bash
POST /api/analyze
{
  "message": "text to analyze",
  "user_id": "discord_user_id",
  "channel_id": "discord_channel_id"
}
```

### Statistics
```bash
GET /api/stats
# Returns crisis detection statistics and bot metrics
```

### Team Alerts
```bash
POST /api/alert
{
  "level": "high|medium|low",
  "message": "alert message",
  "user_id": "discord_user_id",
  "channel_id": "discord_channel_id"
}
```

For complete API documentation, see [docs/tech/API_v2_1.md](docs/tech/API_v2_1.md)

## 🧪 Testing

### Automated Testing

```bash
# Run unit tests
pytest tests/

# Run integration tests
pytest tests/integration/

# Test with full ecosystem
cd ../ash-thrash
python src/comprehensive_testing.py
```

### Manual Testing

```bash
# Test crisis detection
python scripts/test_crisis_detection.py

# Test NLP integration
python scripts/test_nlp_connection.py

# Test Discord connectivity
python scripts/test_discord_connection.py
```

## 📚 Documentation

### Core Documentation
- **[Deployment Guide](docs/deployment_v2_1.md)** - Complete deployment instructions
- **[API Documentation](docs/tech/API_v2_1.md)** - Full API reference
- **[Architecture Guide](docs/tech/architecture_v2_1.md)** - System design and integration
- **[Implementation Guide](docs/tech/implementation_v2_1.md)** - Technical implementation details
- **[Troubleshooting Guide](docs/tech/troubleshooting_v2_1.md)** - Common issues and solutions

### Team Resources
- **[Team Guide](docs/team/team_guide_v2_1.md)** - Crisis response team procedures
- **[GitHub Release Guide](docs/github_release_v2_1.md)** - Release management

### External Documentation
- **[Ecosystem Overview](https://github.com/the-alphabet-cartel/ash)** - Complete system documentation
- **[Dashboard Guide](https://github.com/the-alphabet-cartel/ash-dash)** - Analytics and monitoring
- **[Testing Suite](https://github.com/the-alphabet-cartel/ash-thrash)** - Quality assurance

## 🛠️ Development

### Development Environment

**Prerequisites**:
- Python 3.9+
- Docker and Docker Compose
- Discord bot application
- Access to The Alphabet Cartel GitHub organization

**Recommended Development Setup**:
- **Editor**: Atom (or VS Code)
- **Git**: GitHub Desktop (or command line)
- **Docker**: Docker Desktop
- **Operating System**: Windows 11 (development) / Debian 12 (production)

### Development Workflow

```bash
# 1. Fork and clone
git clone https://github.com/YourUsername/ash-bot.git
cd ash-bot

# 2. Create development branch
git checkout -b feature/your-feature-name

# 3. Set up development environment
python -m venv venv
source venv/bin/activate
pip install -r requirements-dev.txt

# 4. Configure for development
cp .env.template .env.development
# Edit .env.development with development settings

# 5. Run tests
pytest tests/

# 6. Run bot in development mode
ENVIRONMENT=development python main.py

# 7. Test integration with other services
python scripts/test_ecosystem_integration.py

# 8. Submit pull request
git push origin feature/your-feature-name
# Create PR on GitHub
```

### Code Standards

- **Python Style**: Follow PEP 8
- **Testing**: Minimum 80% code coverage
- **Documentation**: Update docs for any API changes
- **Security**: No hardcoded credentials
- **Logging**: Comprehensive logging for debugging

## 🔐 Security & Privacy

### Privacy Protection
- **No Personal Data Storage**: Messages analyzed in memory only
- **Anonymized Analytics**: User identifiers stripped from metrics
- **Consent-Based**: Clear opt-out mechanisms
- **Data Retention**: Minimal necessary data only

### Security Features
- **API Authentication**: Secure API key management
- **Rate Limiting**: Protection against abuse
- **Input Validation**: Sanitized message processing
- **Audit Logging**: Complete action tracking

### Crisis Data Handling
- **Encrypted Communication**: TLS for all API calls
- **Secure Storage**: Crisis alerts encrypted at rest
- **Access Controls**: Role-based team access
- **Compliance**: GDPR and privacy law adherence

## 📞 Support

### Community Support
- **Discord**: https://discord.gg/alphabetcartel (#tech-support)
- **Issues**: [GitHub Issues](https://github.com/the-alphabet-cartel/ash-bot/issues)
- **Discussions**: [GitHub Discussions](https://github.com/the-alphabet-cartel/ash-bot/discussions)

### Documentation
- **Implementation Guide**: Step-by-step technical setup
- **Troubleshooting**: Common problems and solutions
- **API Reference**: Complete endpoint documentation
- **Team Procedures**: Crisis response protocols

### Crisis Response Training
- **Team Onboarding**: Crisis response team training
- **Best Practices**: Community mental health guidelines
- **Escalation Procedures**: When and how to escalate
- **Legal Compliance**: Understanding your obligations

## 🤝 Contributing

We welcome contributions from the community! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details on:

- **Code of Conduct**: Community standards
- **Development Process**: How to contribute code
- **Issue Reporting**: Bug reports and feature requests
- **Testing Requirements**: Quality assurance standards

### Key Contribution Areas
- **Crisis Detection Accuracy**: Improve keyword and AI models
- **Response Templates**: Better crisis intervention messages
- **Integration Features**: New platform integrations
- **Documentation**: User guides and technical docs
- **Testing**: Quality assurance and validation

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

### Technical Contributors
- **The Alphabet Cartel Community**: Testing, feedback, and continuous improvement
- **Crisis Response Team**: Real-world validation and training
- **Open Source Community**: Libraries and frameworks that make this possible

### Mental Health Advocates
- **Crisis Intervention Specialists**: Guidance on best practices
- **LGBTQIA+ Community Leaders**: Cultural sensitivity and inclusivity
- **Mental Health Professionals**: Clinical guidance and validation

---

**The Alphabet Cartel** - Building inclusive gaming communities through technology.

🌈 **Discord**: https://discord.gg/alphabetcartel | 🌐 **Website**: https://alphabetcartel.org

*Together, we create safer, more supportive communities for everyone.*