# Ash-Bot - Discord Crisis Detection Bot

**Part of the Ash Ecosystem** | **Main Repository:** https://github.com/the-alphabet-cartel/ash

This repository contains **only the Discord bot component** of the Ash crisis detection system. For the complete ecosystem including NLP server, dashboard, and testing suite, see the [main Ash repository](https://github.com/the-alphabet-cartel/ash).

**Discord Community:** https://discord.gg/alphabetcartel  
**Website:** http://alphabetcartel.org  
**Organization:** https://github.com/the-alphabet-cartel

## 🤖 About Ash-Bot

Ash-Bot is the Discord interface for The Alphabet Cartel's crisis detection and community support system. It monitors Discord conversations, detects potential crisis situations, and coordinates appropriate support responses within LGBTQIA+ gaming communities.

### 🏗️ Architecture Position

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Discord Bot   │◄──►│   NLP Server    │◄──►│   Dashboard     │
│   (THIS REPO)   │    │   (ash-nlp)     │    │   (ash-dash)    │
│                 │    │                 │    │                 │
│ 10.20.30.253    │    │ 10.20.30.16     │    │ 10.20.30.16     │
│ Port: 8882      │    │ Port: 8881      │    │ Port: 8883      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                 ▲
                                 │
                       ┌─────────────────┐
                       │  Testing Suite  │
                       │  (ash-thrash)   │
                       │                 │
                       │ 10.20.30.16     │
                       │ Port: 8884      │
                       └─────────────────┘
```

## 🚀 Quick Start

### For Development
If you're working on the bot specifically:

```bash
# Clone this repository
git clone https://github.com/the-alphabet-cartel/ash-bot.git
cd ash-bot

# Setup development environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements-dev.txt

# Configure environment
cp .env.template .env
# Edit .env with your Discord token and API keys

# Run development server
python -m bot
```

### For Complete Ecosystem
If you need the full Ash system (recommended):

```bash
# Clone the main ecosystem repository
git clone --recursive https://github.com/the-alphabet-cartel/ash.git
cd ash

# Follow setup instructions in main repository
# This includes ash-bot as a submodule along with all other components
```

## 🔧 Core Features

### Discord Integration
- **Message Monitoring**: Real-time processing of Discord messages across channels
- **Command System**: Slash commands for bot management and user interaction
- **Permission Management**: Role-based access control for administrative functions
- **Rate Limiting**: Discord API compliance and respectful usage patterns

### Crisis Detection Pipeline
- **Initial Filtering**: Keyword-based pre-screening to optimize performance
- **NLP Integration**: Seamless communication with ash-nlp server for advanced analysis
- **Context Awareness**: Understanding conversation flow and user interaction patterns
- **Alert Generation**: Immediate notification system for crisis situations

### Community Support
- **Privacy-First Design**: Processes only necessary text, no permanent personal data storage
- **Configurable Responses**: Customizable bot responses for different crisis levels
- **Team Coordination**: Integration with moderation workflows and support team alerts
- **Learning System**: Continuous improvement through feedback and testing integration

## 📦 Repository Structure

```
ash-bot/                          # THIS REPOSITORY
├── bot/                          # Main bot application
│   ├── core/                     # Core bot functionality
│   │   ├── bot.py               # Main bot client and event handlers
│   │   ├── config.py            # Configuration management
│   │   └── database.py          # Data storage and management
│   ├── handlers/                 # Message and event handlers
│   │   ├── message_handler.py   # Message processing logic
│   │   ├── crisis_handler.py    # Crisis detection coordination
│   │   └── command_handler.py   # Slash command implementations
│   ├── utils/                    # Utility functions
│   │   ├── helpers.py           # General helper functions
│   │   ├── logger.py            # Logging configuration
│   │   └── validators.py        # Input validation utilities
│   ├── keywords/                 # Crisis detection keywords
│   │   ├── high_crisis.py       # High-priority crisis terms
│   │   ├── medium_crisis.py     # Medium-priority crisis terms
│   │   └── low_crisis.py        # Low-priority crisis terms
│   ├── data/                     # Data storage
│   └── logs/                     # Log files
├── tests/                        # Unit tests for bot functionality
├── docs/                         # Bot-specific documentation
├── docker/                       # Docker configuration
├── scripts/                      # Utility scripts
├── .env.template                 # Environment configuration template
├── docker-compose.yml            # Docker deployment configuration
├── requirements.txt              # Production dependencies
├── requirements-dev.txt          # Development dependencies
└── README.md                     # This file
```

## 🛠️ Development

### Prerequisites
- Python 3.9+
- Discord Bot Token (from Discord Developer Portal)
- Access to ash-nlp server (for full functionality)
- Docker (for containerized deployment)

### Environment Configuration

Create `.env` file from template:
```bash
cp .env.template .env
```

Required environment variables:
```bash
# Discord Configuration
DISCORD_TOKEN=your_discord_bot_token_here
GUILD_ID=your_discord_server_id_here

# NLP Server Integration
NLP_SERVER_URL=http://10.20.30.16:8881
NLP_API_TIMEOUT=30

# Bot Configuration
API_PORT=8882
ENVIRONMENT=development
DEBUG_MODE=true

# Claude API (for enhanced responses)
CLAUDE_API_KEY=your_claude_api_key_here
```

### Testing

```bash
# Run unit tests
pytest tests/

# Run with coverage
pytest --cov=bot tests/

# Run integration tests (requires NLP server)
pytest tests/integration/
```

### Docker Deployment

```bash
# Build and run locally
docker-compose up --build

# Production deployment
docker-compose -f docker-compose.prod.yml up -d
```

## 🔗 Integration with Ash Ecosystem

### NLP Server Communication
- **Endpoint**: `http://10.20.30.16:8881/analyze`
- **Protocol**: REST API with JSON payloads
- **Fallback**: Keyword-only detection if NLP server unavailable
- **Caching**: Local caching of recent NLP results for performance

### Dashboard Integration
- **Metrics Reporting**: Real-time statistics to ash-dash
- **Alert Coordination**: Crisis alerts displayed in dashboard
- **Performance Monitoring**: Bot health and response time metrics

### Testing Integration
- **Validation**: Tested by ash-thrash 350-phrase test suite
- **Quality Assurance**: Continuous validation of detection accuracy
- **Performance Benchmarking**: Response time and reliability metrics

## 📊 Bot Performance

### Specifications
- **Server**: Linux (10.20.30.253)
- **Resources**: 1GB RAM, 0.5 CPU cores
- **Uptime Target**: 99.9%
- **Response Time**: <500ms for standard messages
- **Crisis Detection**: <2s end-to-end including NLP analysis

### Monitoring
- **Health Endpoint**: `http://10.20.30.253:8882/health`
- **Metrics**: Available via ash-dash dashboard
- **Logging**: Comprehensive logs in `/bot/logs/`
- **Alerts**: Automated alerting for service disruptions

## 🧪 Testing

This repository includes unit tests for bot-specific functionality. For comprehensive system testing including crisis detection accuracy, see [ash-thrash](https://github.com/the-alphabet-cartel/ash-thrash).

```bash
# Bot-specific testing
python -m pytest tests/unit/

# Integration testing (requires full ecosystem)
python -m pytest tests/integration/
```

## 🚨 Crisis Detection Logic

### Detection Pipeline
1. **Message Reception**: Discord message received via event handler
2. **Initial Filtering**: Fast keyword-based pre-screening
3. **NLP Analysis**: Advanced analysis via ash-nlp server (if needed)
4. **Risk Assessment**: Combined scoring from keywords and NLP
5. **Response Coordination**: Alert generation and response execution

### Keywords Management
Crisis detection keywords are maintained in `/bot/keywords/`:
- `high_crisis.py`: Immediate intervention required
- `medium_crisis.py`: Close monitoring and support needed
- `low_crisis.py`: Wellness check and resource sharing

These keyword files are synchronized with ash-thrash testing suite to ensure consistent detection logic.

## 🤝 Contributing

### Development Process
1. **Fork this repository** (ash-bot specifically)
2. **Create feature branch** for your changes
3. **Write tests** for new functionality
4. **Test integration** with ash-nlp server
5. **Update documentation** as needed
6. **Submit pull request** to this repository

### Integration Testing
Changes to crisis detection logic should be validated with the complete ecosystem:
1. Test with ash-thrash comprehensive suite
2. Verify dashboard integration works correctly
3. Confirm NLP server communication functions properly

### Main Ecosystem
For changes affecting multiple components, work with the [main ash repository](https://github.com/the-alphabet-cartel/ash) which includes this repository as a submodule.

## 📞 Support

### Bot-Specific Issues
- **GitHub Issues**: [ash-bot/issues](https://github.com/the-alphabet-cartel/ash-bot/issues)
- **Discord Support**: #ash-bot-support in https://discord.gg/alphabetcartel

### Ecosystem-Wide Issues
- **Main Repository**: [ash/issues](https://github.com/the-alphabet-cartel/ash/issues)
- **General Discussion**: #tech-help in https://discord.gg/alphabetcartel

### Security Issues
Report security vulnerabilities privately to repository maintainers.

## 📜 License

This project is part of The Alphabet Cartel's open-source initiatives. See [LICENSE](LICENSE) file for details.

---

## ⚠️ Important Notes

### Repository Scope
This repository contains **ONLY the Discord bot component**. For:
- **NLP Server**: See [ash-nlp](https://github.com/the-alphabet-cartel/ash-nlp)
- **Analytics Dashboard**: See [ash-dash](https://github.com/the-alphabet-cartel/ash-dash)
- **Testing Suite**: See [ash-thrash](https://github.com/the-alphabet-cartel/ash-thrash)
- **Complete System**: See [main ash repository](https://github.com/the-alphabet-cartel/ash)

### Development Recommendations
- **New Contributors**: Start with the [main ash repository](https://github.com/the-alphabet-cartel/ash) for complete system overview
- **Bot-Specific Work**: Use this repository for Discord integration and bot logic
- **System Integration**: Test changes against the full ecosystem using ash-thrash

### Deployment
While this repository can be deployed standalone for development, **production deployment should use the main ash repository** with Docker Compose orchestration for all components.

---

**Built with 🖤 for LGBTQIA+ gaming communities by [The Alphabet Cartel](https://discord.gg/alphabetcartel)**