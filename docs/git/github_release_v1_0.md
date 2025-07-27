# 🖤 Ash Bot v1.0 - "Building Chosen Family"

> *The gothic mental health sage for The Alphabet Cartel Discord community*

## 🎉 First Stable Release

This is the first production-ready release of **Ash Bot**, an AI-powered mental health support system designed specifically for LGBTQIA+ Discord communities. Ash provides 24/7 crisis detection and support while seamlessly integrating with human crisis response teams.

## ✨ Key Features

### 🚨 **Three-Tier Crisis Detection System**
- **🟢 Low Crisis**: Depression, anxiety, identity struggles → Ash support only
- **🟡 Medium Crisis**: Severe distress, panic attacks → Team alerts
- **🔴 High Crisis**: Suicidal ideation, self-harm → Full escalation (staff DM + team alerts)

### 🎭 **Authentic Character**
- **Gothic counselor** persona with sardonic but caring voice
- Validates pain without toxic positivity
- Uses "we" language and dark humor appropriately
- References art/music for emotional connection

### 💬 **Smart Conversation System**
- **5-minute follow-up windows** for continued support
- **Crisis escalation detection** during conversations
- **Channel restrictions** for appropriate deployment
- **Rate limiting** to prevent abuse

### 🏗️ **Production-Ready Architecture**
- **Modular keyword system** for easy maintenance
- **Docker containerization** with health checks
- **GitHub Actions CI/CD** for automated deployments
- **Claude 3.5 Sonnet** integration for natural responses

## 📊 What's Included

### Core Bot System
- **Crisis detection** with 200+ mental health keywords
- **Conversation tracking** with escalation handling
- **Staff notifications** via DM and team alerts
- **Comprehensive logging** and monitoring

### Deployment Infrastructure
- **Docker containers** with proper security (non-root user)
- **GitHub Container Registry** integration
- **Environment-based configuration**
- **Auto-restart** and health monitoring

### Team Integration
- **Crisis response alerts** in dedicated channels
- **Staff escalation** for high-risk situations
- **Team coordination** tools and workflows
- **Comprehensive documentation**

## 🛡️ Security & Safety

- **Channel restrictions** - only responds where appropriate
- **Rate limiting** - prevents spam and abuse
- **Non-root containers** - secure deployment
- **Professional referrals** - recognizes limitations
- **Crisis escalation** - ensures human oversight

## 💰 Cost Management

- **Estimated $15-45/month** depending on usage
- **Daily API limits** and **per-user rate limiting**
- **Efficient conversation windows** (5 minutes, no reset)
- **Usage monitoring** and **cost controls**

## 🚀 Deployment

### Quick Start
```bash
# Clone and configure
git clone https://github.com/The-Alphabet-Cartel/ash.git
cd ash
cp .env.template .env
# Edit .env with your tokens

# Deploy with Docker
docker-compose up -d
```

### GitHub Actions
- **Automatic builds** on every push
- **Container registry** publishing
- **Production deployment** ready

## 📈 Community Impact

### For Community Members
- **24/7 mental health support** availability
- **Immediate crisis acknowledgment** and validation
- **Bridge to human care** when needed
- **LGBTQIA+-informed** responses

### For Crisis Response Teams
- **Automated detection** reduces monitoring burden
- **Smart alerts** for efficient team coordination
- **Detailed context** for informed responses
- **Consistent initial support** while team mobilizes

## 🎯 Technical Highlights

- **Python 3.11** with async/await architecture
- **Discord.py 2.3.2** for robust Discord integration
- **Anthropic Claude API** for natural language processing
- **Modular keyword system** with 200+ crisis indicators
- **Redis integration** for future conversation persistence
- **Comprehensive test suite** and health checks

## 📚 Documentation

### Included Guides
- **README.md** - Complete technical documentation
- **TEAM_GUIDE.md** - Crisis response team procedures
- **Keyword files** - Organized by crisis level with utility functions
- **Deployment guides** - Local, Docker, and production setups

### Key Resources
- Environment configuration templates
- Docker deployment instructions
- Crisis response workflows
- Monitoring and maintenance guides

## 🔄 Upgrade Path

This v1.0 release establishes:
- **Stable API** for keyword detection
- **Consistent alert formats** for team integration
- **Modular architecture** for future enhancements
- **Production deployment** patterns

## ⚠️ Known Limitations

- **English language only** - keyword detection is English-specific
- **Text-based detection** - cannot analyze images or voice
- **Static keywords** - requires manual updates for new terminology
- **Single server** - designed for one Discord community

## 🛣️ Future Roadmap

### v1.1 Planned Features
- Enhanced conversation context understanding
- Improved LGBTQIA+ terminology detection
- Analytics dashboard for team performance
- Multi-language support exploration

### v2.0 Vision
- Advanced conversation persistence
- ML-powered keyword discovery
- Integration with external mental health resources

## 🙏 Acknowledgments

- **The Alphabet Cartel** community for testing and feedback
- **Anthropic** for Claude API access
- **Discord.py** maintainers for excellent library support
- **Crisis response volunteers** who make this meaningful

## 📞 Support

- **Issues**: Use GitHub Issues for bug reports
- **Documentation**: Check README.md and TEAM_GUIDE.md
- **Community**: The Alphabet Cartel Discord server

---

## 📦 Installation

1. Download the release assets or clone the repository
2. Copy `.env.template` to `.env` and configure your tokens
3. Deploy using Docker: `docker-compose up -d`
4. Monitor logs: `docker-compose logs -f ash`

**Full deployment instructions available in README.md**

---

*"We've all been in that dark place where everything feels impossible. You're not alone."* - Ash

**Built with 🖤 for chosen family everywhere.**