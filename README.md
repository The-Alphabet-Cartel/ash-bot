# Ash Bot v3.1 - Advanced Discord Crisis Response System

**Intelligent mental health crisis detection and response bot for LGBTQIA+ Discord communities**

[![Discord](https://img.shields.io/badge/Discord-Join%20Server-7289da)](https://discord.gg/alphabetcartel)
[![Website](https://img.shields.io/badge/Website-alphabetcartel.org-blue)](http://alphabetcartel.org)
[![GitHub](https://img.shields.io/badge/Branch-Main-green)](https://github.com/the-alphabet-cartel/ash-bot)

## 🚀 What is Ash Bot v3.1?

Ash Bot v3.1 is a sophisticated **Discord crisis response system** that utilizes advanced NLP analysis to provide 24/7 mental health crisis support in LGBTQIA+ communities. Built with safety-first design principles, Ash creates a protective layer of support while maintaining community privacy and autonomy.

### Key Features

- **⚡ Real-time Crisis Response**: Sub-second message analysis and immediate support
- **🛡️ Multi-tier Crisis Escalation**: Graduated response based on crisis severity
- **🏳️‍🌈 LGBTQIA+ Aware**: Trained on community-specific language and experiences
- **💬 Conversation Support**: Sustained crisis conversations with natural continuation
- **🔒 Privacy-First**: No message storage, real-time analysis only

## 🤖 Architecture Overview

### Detection Pipeline
```
Discord Message → NLP Ensemble → Context Analysis → Crisis Assessment → Response
```

### Integration Components
- **[Ash NLP](https://github.com/the-alphabet-cartel/ash-nlp)** - Three Zero-Shot Model Ensemble Crisis Detection (Port 8881)

## 🎯 Crisis Response System

### Three-Tier Crisis Levels

#### 🚨 High/Critical Crisis (Immediate Intervention)
- **Detection**: Suicidal ideation, immediate harm indicators
- **Response**: Instant crisis resources + Direct staff DM + Team alert with role ping
- **Speed**: <2 seconds from detection to full escalation

#### ⚠️ Medium Crisis (Active Support)
- **Detection**: Depression indicators, distress patterns, help-seeking
- **Response**: Supportive response + Crisis team notification + Conversation activation
- **Features**: Natural conversation continuation, context-aware support

#### ℹ️ Low Crisis (Monitoring Support)
- **Detection**: Emotional distress, mild depression indicators
- **Response**: Supportive message + Conversation availability + Trend monitoring
- **Goal**: Early intervention and community connection

### Smart Conversation System
```python
# Natural conversation triggers
@Ash can you help me with...
Ash, I'm still struggling...
Hey ash, what if I...

# Context-aware responses maintain conversation flow
# 5-minute active conversation windows
# Graceful conversation conclusion
```

## 🛠️ Slash Commands

### Crisis Management Commands
**(Requires CrisisResponse Role)**

#### Advanced Analysis
- `/analyze_message` - Test message detection pipeline
- `/context_stats` - Context detection performance

#### False Positive Learning
- `/report_false_positive` - Report incorrect crisis detection
- `/report_false_negative` - Report missed crisis situations
- `/learning_stats` - View learning system performance

#### System Monitoring
- `/crisis_stats` - Crisis response statistics
- `/conversation_stats` - Conversation system metrics
- `/active_conversations` - View ongoing crisis conversations

### Public Commands
**(Available to all users)**

#### Information & Help
- `/help` - Bot capabilities and usage guide *Planned*
- `/resources` - Mental health resources and crisis hotlines *Planned*
- `/privacy` - Privacy policy and data handling information *Planned*

#### Crisis Support
- `/crisis_chat` - Start a private crisis conversation *Planned*
- `/anonymous_report` - Anonymous crisis reporting *Planned*

## 🔒 Security & Privacy

### Data Handling
- **Zero Message Storage**: Messages analyzed in real-time, never stored
- **Ephemeral Analysis**: Detection results discarded after response
- **Audit Logging**: Crisis interventions logged for effectiveness review
- **Role-Based Access**: Sensitive commands restricted to crisis team

### Security Features
- **Input Sanitization**: All user inputs validated and sanitized
- **Rate Limiting**: Prevents abuse of crisis detection system
- **Secure Secrets**: Docker secrets support for production deployment
- **Access Controls**: Multi-tier permission system

### Privacy Commitment
- **No User Profiling**: Individual patterns not tracked or stored
- **Anonymous Analytics**: Only aggregate usage statistics collected
- **Opt-out Support**: Users can request exclusion from monitoring *Planned*
- **Transparent Operation**: All detection logic open source and auditable

## 🧪 Advanced Features

### Context-Aware Detection
```python
# Gaming context reduces false positives
"I want to kill this boss" → Gaming Context → Low Crisis Priority

# Support conversation context increases sensitivity  
"I still feel like ending it" → Support Context → High Crisis Priority

# Creative writing context adjusts interpretation
"The character wanted to die" → Creative Context → Reduced Priority
```

### Intelligent Conversation Flow
- **Natural Triggers**: Responds to mentions and conversation starters after initial contact
- **Context Preservation**: Maintains conversation awareness for 5 minutes
- **Graceful Transitions**: Smooth conversation conclusion with resource offers
- **Crisis Override**: Critical-priority crises bypass conversation limits

### Community-Specific Patterns
- **LGBTQIA+ Language**: Understands community-specific expressions and concerns
- **Cultural Sensitivity**: Trained on inclusive language and experiences
- **Identity-Aware**: Recognizes identity-related distress patterns
- **Safe Space Maintenance**: Preserves community autonomy while providing support

## 📈 Monitoring & Analytics

### Real-time Metrics
```bash
# Bot health and performance
curl http://10.20.30.253:8882/health

# Crisis response statistics  
curl http://10.20.30.253:8882/stats

# Conversation system metrics
curl http://10.20.30.253:8882/conversation_stats
```

## 🤝 Contributing

We welcome contributions from community members who share our commitment to LGBTQIA+ safety and mental health support.

## 📞 Support & Community

### Getting Help
- **Discord Community**: [Join our server](https://discord.gg/alphabetcartel) for community support
- **GitHub Issues**: Report bugs and request features
- **Crisis Team Direct**: Contact crisis response team for urgent issues

### Crisis Resources
If you're in crisis right now:
- **US Crisis Hotline**: 988 (Call or text)
- **LGBTQ National Hotline**: 1-888-843-4564
- **Trans Lifeline**: 877-565-8860
- **Crisis Text Line**: Text HOME to 741741

## 📄 License

This project is licensed under the **GNU General Public License v3.0** - see the [LICENSE](LICENSE) file for details.

**Open source for community mental health support.**

### License Summary
- ✅ **Freedom to use**: Use for any purpose including commercial
- ✅ **Freedom to modify**: Change and adapt the code
- ✅ **Freedom to distribute**: Share original or modified versions
- ✅ **Freedom to contribute**: Submit improvements back to the community
- ⚠️ **Copyleft requirement**: Derivative works must use compatible license
- ⚠️ **Source disclosure**: Modified versions must provide source code

## 🏳️‍🌈 The Alphabet Cartel

**Building technology for chosen family, one conversation at a time.**

We're an LGBTQIA+ organization dedicated to creating safe, supportive technology for our communities. Our approach prioritizes:

- **Community Safety**: Every feature designed with user wellbeing in mind
- **Privacy Respect**: Minimal data collection, maximum user control
- **Inclusive Design**: Built by and for diverse LGBTQIA+ experiences
- **Open Source**: Transparent, auditable, community-improvable technology
- **Chosen Family Support**: Technology that strengthens community bonds

### Connect With Us
- **Discord Community**: [https://discord.gg/alphabetcartel](https://discord.gg/alphabetcartel)
- **Website**: [http://alphabetcartel.org](http://alphabetcartel.org)
- **GitHub Organization**: [https://github.com/the-alphabet-cartel](https://github.com/the-alphabet-cartel)

---

*Remember: Technology is only as caring as the community that builds it. Thank you for being part of a community that prioritizes mental health, safety, and the power of chosen family.*

**Made with ❤️ by The Alphabet Cartel**  
*Serving LGBTQIA+ communities since 2023*