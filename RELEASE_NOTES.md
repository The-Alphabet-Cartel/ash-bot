# Ash-Bot v5.0 Release Notes

## 🎉 The Complete Recode

**Release Date**: January 2026  
**Codename**: "Chosen Family"

---

We're thrilled to announce **Ash-Bot v5.0** — a complete ground-up recode of our crisis detection system for [The Alphabet Cartel](https://discord.gg/alphabetcartel) LGBTQIA+ community.

This release represents months of careful development, transforming Ash-Bot from a simple alerting system into a comprehensive crisis support platform with AI-powered conversations, automated follow-ups, and powerful CRT workflow tools.

---

## ✨ Highlights

### 🤖 Meet Ash — Your AI Support Companion

Ash is now a fully-realized AI personality powered by Claude, capable of:
- **Compassionate conversations** with community members in crisis
- **Warm, supportive tone** that feels genuine, not robotic
- **Context awareness** through conversation history
- **Graceful handoffs** when CRT members take over

### 📊 Intelligent Crisis Detection

- **NLP-powered analysis** via the Ash-NLP service
- **Severity classification**: CRITICAL, HIGH, MEDIUM, LOW
- **Pattern detection** for escalating behavior
- **Confidence scoring** so CRT knows how certain the detection is

### 🛡️ Privacy-First Design

- **User opt-out system** — community members control their interaction with Ash
- **No message storage for safe content** — only concerning messages are retained
- **Configurable data retention** with automatic cleanup
- **Double opt-out checking** for follow-up messages

---

## 🚀 What's New

### Phase 1: Discord Gateway
- Clean Architecture foundation
- Robust Discord.py integration
- Channel monitoring with configurable filters
- Graceful connection handling

### Phase 2: Redis Storage
- Message history tracking (severity-filtered)
- User context retention
- TTL-based automatic expiration
- Graceful degradation when Redis unavailable

### Phase 3: Alert Dispatching
- Severity-based channel routing
- Beautiful embed alerts with all context
- Acknowledge, Talk to Ash, and History buttons
- CRT role pinging for urgent alerts
- Cooldown management to prevent alert fatigue

### Phase 4: Ash AI Personality
- Claude-powered conversational AI
- Session management with timeouts
- Personality consistency across conversations
- Context-aware responses using message history

### Phase 5: Production Hardening
- Comprehensive health check API
- Prometheus-compatible metrics endpoint
- Circuit breaker for external services
- Structured logging with configurable levels

### Phase 6: Health API
- `/health` — Kubernetes liveness probe
- `/health/ready` — Readiness probe
- `/health/detailed` — Full system status
- `/metrics` — Prometheus metrics

### Phase 7: User Preferences
- `/ash optout` and `/ash optin` commands
- Auto-initiate for unacknowledged alerts
- Preference persistence in Redis
- Opt-out indicators on alerts

### Phase 8: Metrics & Reporting
- Response time tracking per alert
- Weekly summary reports to CRT channel
- Automated data retention cleanup
- Historical trend analysis

### Phase 9: CRT Workflow Enhancements
- **Slash Commands**: `/ash status`, `/ash health`, `/ash stats`, `/ash notes`
- **Session Handoff**: Smooth transition from Ash to CRT
- **Session Notes**: Documentation for continuity of care
- **Follow-Up Check-Ins**: Automated 24-hour DM check-ins

---

## 📋 Command Reference

| Command | Description | Who Can Use |
|---------|-------------|-------------|
| `/ash status` | Check your opt-out status | Everyone |
| `/ash optout` | Opt out of Ash interaction | Everyone |
| `/ash optin` | Opt back in to Ash | Everyone |
| `/ash health` | Check bot system status | CRT Members |
| `/ash stats` | View response statistics | CRT Members |
| `/ash notes add` | Add notes about a user | CRT Members |
| `/ash notes view` | View notes about a user | CRT Members |

---

## ⚙️ Configuration

### Environment Variables

Ash-Bot v5.0 uses environment variables for all configuration. A complete `.env.template` is provided with documentation for every setting.

**Key Configuration Areas**:
- Discord bot credentials
- Redis connection
- NLP API endpoint
- Claude API credentials
- Alert channel mappings
- CRT role configuration
- Feature toggles for all major features

### Docker Deployment

```bash
# Clone the repository
git clone https://github.com/the-alphabet-cartel/ash-bot.git
cd ash-bot

# Copy and configure environment
cp .env.template .env
# Edit .env with your settings

# Start with Docker Compose
docker compose up -d
```

### Health Checks

```bash
# Liveness probe
curl http://localhost:30881/health

# Readiness probe
curl http://localhost:30881/health/ready

# Detailed status
curl http://localhost:30881/health/detailed

# Prometheus metrics
curl http://localhost:30881/metrics
```

---

## 📊 Technical Specifications

| Component | Technology |
|-----------|------------|
| Runtime | Python 3.11 |
| Discord Library | discord.py 2.x |
| AI Backend | Claude (Anthropic API) |
| NLP Service | Ash-NLP (separate container) |
| Database | Redis 7.x |
| Container | Docker with multi-stage build |
| Architecture | Clean Architecture |

### Test Coverage

| Phase | Tests | Pass Rate |
|-------|-------|-----------|
| Core | 89 | 100% |
| Phase 7 | 45 | 100% |
| Phase 8 | 67 | 100% |
| Phase 9 | 107 | 100% |
| **Total** | **308+** | **100%** |

---

## 📚 Documentation

Comprehensive documentation is available in the `docs/` directory:

| Document | Description |
|----------|-------------|
| `docs/operations/crisis_response_guide.md` | Complete CRT operational guide |
| `docs/operations/discord_deployment_guide.md` | Discord setup instructions |
| `docs/standards/clean_architecture_charter.md` | Code standards and patterns |
| `docs/v5.0/phase*/` | Detailed phase documentation |

---

## 🔄 Upgrading from v4.x

Ash-Bot v5.0 is a complete recode. **There is no migration path from v4.x** — this is a fresh deployment.

### Before You Begin

1. **Backup any existing data** you want to preserve
2. **Review the new configuration** requirements
3. **Set up the Ash-NLP service** (required for crisis detection)
4. **Configure Claude API access** (required for Ash AI)

### Fresh Installation Steps

1. Clone the v5.0 repository
2. Copy `.env.template` to `.env`
3. Configure all required environment variables
4. Deploy Ash-NLP service
5. Deploy Ash-Bot with `docker compose up -d`
6. Verify health at `http://localhost:30881/health`
7. Test slash commands in Discord

---

## 🙏 Acknowledgments

Ash-Bot v5.0 was built with love for The Alphabet Cartel community.

Special thanks to:
- Our Crisis Response Team for their invaluable feedback
- The Alphabet Cartel community for trusting us with their safety
- Anthropic for Claude, powering Ash's compassionate conversations

---

## 🐛 Known Issues

- **Redis `keys` method**: Some managers show warnings about missing `keys` method on RedisManager. This doesn't affect functionality and will be addressed in v5.0.1.
- **Notes channel**: If `BOT_CRT_NOTES_CHANNEL_ID` is not configured, notes are stored but not posted to a channel.

---

## 🔮 What's Next

Future releases may include:
- Multi-language support for Ash conversations
- Advanced analytics dashboard
- Mobile push notifications for CRITICAL alerts
- Integration with external crisis resources

---

## 💜 A Note from the Team

> "Ash-Bot isn't just code — it's a promise to our community that someone is always watching out for them. When someone is struggling at 3 AM and feels completely alone, Ash is there. When our CRT members need context to help someone effectively, Ash provides it. When a community member needs space, Ash respects that.
>
> This v5.0 release represents our commitment to building technology that genuinely helps people. We hope it serves our community well."
>
> — The Alphabet Cartel Tech Team

---

**Built with care for chosen family** 🏳️‍🌈

[Discord](https://discord.gg/alphabetcartel) | [Website](https://alphabetcartel.org) | [GitHub](https://github.com/the-alphabet-cartel)

---

## 📝 Full Changelog

### Added
- Complete ground-up recode using Clean Architecture
- Ash AI personality with Claude integration
- NLP-powered crisis detection via Ash-NLP service
- Redis-backed message history and user preferences
- Severity-based alert routing (CRITICAL, HIGH, MEDIUM)
- Interactive alert embeds with Acknowledge, Talk to Ash, History buttons
- User opt-out system with `/ash optout` and `/ash optin`
- Auto-initiate for unacknowledged alerts
- Session handoff protocol for CRT takeover
- Session notes for documentation
- Automated 24-hour follow-up check-ins
- Weekly CRT reports with response metrics
- Health API with Kubernetes-compatible probes
- Prometheus metrics endpoint
- Configurable data retention with automatic cleanup
- Comprehensive slash command suite
- Circuit breaker for external service resilience
- Docker multi-stage build for optimized images
- 308+ unit tests with 100% pass rate

### Changed
- Architecture: Migrated to Clean Architecture pattern
- Configuration: All settings via environment variables
- Storage: Redis replaces previous storage solution
- AI: Claude replaces previous AI integration

### Removed
- Legacy v4.x codebase (complete replacement)
- Previous configuration file format
- Old database schema

---

**Version**: v5.0.0  
**Release Type**: Major Release  
**Minimum Python**: 3.11  
**Minimum Redis**: 7.0  
**Required Services**: Ash-NLP, Redis
