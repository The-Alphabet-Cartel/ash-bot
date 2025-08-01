# Crisis Response Team Guide - Ash Bot v3.0

**A comprehensive guide for crisis response teams using Ash Bot's intelligent crisis detection system**

---

## 🎯 Quick Start for Crisis Response Teams

### What is Ash Bot v3.0?

Ash Bot v3.0 is an **intelligent Discord crisis response system** that combines keyword detection with advanced NLP analysis to provide 24/7 mental health crisis monitoring for LGBTQIA+ communities. The system automatically detects crisis situations and escalates them appropriately while maintaining community privacy and autonomy.

### How It Helps Your Team

✅ **24/7 Crisis Monitoring** - Never-offline detection across all monitored channels  
✅ **Intelligent Escalation** - Three-tier crisis response system with appropriate urgency  
✅ **Reduced False Alarms** - 42% fewer false positives through context-aware detection  
✅ **Immediate Response** - Sub-second crisis detection with <2 second full escalation  
✅ **Conversation Support** - Sustained crisis conversations with natural continuation  
✅ **Learning System** - Improves accuracy based on your feedback and corrections  

---

## 🚨 Understanding the Three-Tier Crisis System

### 🚨 High Crisis - Immediate Intervention Required

**What Triggers High Crisis:**
- Direct suicidal ideation ("I want to kill myself", "I'm going to end it")
- Immediate harm indicators ("I have the pills", "I'm on the bridge")
- Active crisis language ("This is my goodbye", "I can't take it anymore")

**System Response:**
1. **Instant Crisis Resources** (< 1 second)
2. **Direct Staff DM** to configured staff member (< 2 seconds)
3. **Crisis Team Alert** with role ping in crisis channel (< 2 seconds)
4. **Conversation Activation** for immediate follow-up support

**Your Role:**
- **Respond immediately** - High crisis alerts require urgent attention
- **Check Discord DM** - Staff member gets direct message with details
- **Coordinate response** - Work with team to provide immediate support
- **Document outcome** - Use `/crisis_stats` to track resolution

**Example High Crisis Alert:**
```
🚨 URGENT CRISIS DETECTED 🚨
User: @username (ID: 123456789)
Channel: #support-chat
Message: "I'm done fighting. I have the pills and I'm ready to end it."
Time: 2025-08-01 14:32:15 UTC
Crisis Level: HIGH
NLP Confidence: 0.94
Keyword Matches: ["end it", "have the pills", "done fighting"]
```

### ⚠️ Medium Crisis - Active Support Needed

**What Triggers Medium Crisis:**
- Depression indicators ("I feel hopeless", "Nothing matters anymore")
- Help-seeking behavior ("I don't know what to do", "I need help but...")
- Distress patterns ("I can't cope", "Everything is falling apart")
- Emotional crisis ("I'm breaking down", "I can't handle this")

**System Response:**
1. **Supportive Message** with empathy and resources
2. **Crisis Team Notification** (no urgent ping, but team is alerted)
3. **Conversation Activation** - 5-minute window for natural follow-up
4. **Resource Availability** - Mental health resources offered naturally

**Your Role:**
- **Monitor notification** - Check crisis team channel within 10-15 minutes
- **Assess need for escalation** - Determine if additional support needed
- **Join conversation if appropriate** - Natural entry into supportive conversation
- **Provide resource guidance** - Help connect user with appropriate resources

**Example Medium Crisis Response:**
```
⚠️ Crisis Support Provided ⚠️
User: @username (ID: 123456789)
Channel: #general-chat
Message: "I just feel so hopeless lately. Nothing I do seems to matter."
Ash Response: "I hear that you're feeling hopeless right now, and I want you to 
know that what you're experiencing matters. It sounds like you're going through 
a really difficult time. Would it help to talk about what's been weighing on you?"
Crisis Level: MEDIUM
Team Action: Monitor for escalation
```

### ℹ️ Low Crisis - Monitoring Support

**What Triggers Low Crisis:**
- Mild depression indicators ("I'm feeling down", "Having a rough day")
- Stress expressions ("This is overwhelming", "I'm struggling with...")
- Emotional distress ("I'm tired of everything", "Nothing is going right")

**System Response:**
1. **Gentle Support Message** - Non-intrusive, supportive response
2. **Conversation Availability** - Bot available for follow-up if needed
3. **Resource Mention** - Subtle mention of available support
4. **Trend Monitoring** - Pattern tracking for early intervention

**Your Role:**
- **Passive monitoring** - Awareness without immediate action required
- **Pattern recognition** - Watch for escalation or repeated low-crisis patterns
- **Resource readiness** - Be prepared to provide support if situation escalates
- **Trend analysis** - Use `/crisis_stats` to identify community patterns

---

## 💬 Understanding the Conversation System

### How Conversations Work

**Natural Triggers:**
```
@Ash can you help me with...
Ash, I'm still struggling...
Hey ash, what if I...
I need to talk to someone...
Can you help me understand...
```

**Conversation Flow:**
1. **Initial Response** - Ash provides crisis-appropriate support
2. **5-Minute Window** - User can continue conversation naturally
3. **Context Preservation** - Ash remembers conversation context
4. **Graceful Conclusion** - Smooth transition to resources when conversation ends

**Crisis Team Integration:**
- **Natural Entry Points** - Team members can join conversations organically
- **Context Sharing** - Use `/active_conversations` to see ongoing support
- **Handoff Support** - Ash facilitates smooth handoff to human support
- **Documentation** - Conversation outcomes tracked for effectiveness

### Supporting Active Conversations

**When to Join:**
- High crisis situations requiring human intervention
- Medium crisis when user requests additional support
- Low crisis if pattern indicates escalation

**How to Join Naturally:**
```
"I see you're talking with Ash - I'm here too if you'd like to chat with a person."
"Ash mentioned you might benefit from talking with someone from our team."
"I noticed you're having a tough time - would you like some additional support?"
```

**Conversation Best Practices:**
- **Respect Ash's role** - Don't override or contradict bot responses
- **Build on support** - Enhance rather than replace bot's guidance
- **Maintain context** - Reference conversation history appropriately
- **Document outcomes** - Record successful interventions for system improvement

---

## 🛠️ Crisis Management Commands

### Keyword Management
**(Requires CrisisResponse Role)**

#### `/add_keyword crisis_level:[level] keyword:[phrase]`
Add custom crisis detection phrases to improve detection accuracy.

**Usage Examples:**
```
/add_keyword crisis_level:High Crisis keyword:ready to give up
/add_keyword crisis_level:Medium Crisis keyword:everything is pointless
/add_keyword crisis_level:Low Crisis keyword:having a hard time
```

**Best Practices:**
- **Use complete phrases** rather than single words when possible
- **Consider context** - avoid phrases that could be false positives
- **Test with `/analyze_message`** before adding to production *[Planned v3.1]*
- **Regular review** - periodically audit keywords for effectiveness

#### `/remove_keyword crisis_level:[level] keyword:[phrase]`
Remove keywords that are causing false positives or are no longer needed.

#### `/list_keywords crisis_level:[level]`
View all current keywords for a specific crisis level.

**Use for:**
- Regular keyword audits
- Training new team members
- Understanding detection logic
- Identifying gaps in coverage

#### `/keyword_stats`
View comprehensive statistics about keyword system performance.

**Metrics Included:**
- Total keywords by crisis level
- Custom vs. built-in keyword counts
- Recent additions and modifications
- Effectiveness indicators

### Learning & Improvement Commands

#### `/report_false_positive message_link:[link] detected_level:[level] correct_level:[level] context:[explanation]`
Report when bot incorrectly flagged a message as crisis.

**Example:**
```
/report_false_positive 
message_link:https://discord.com/channels/123/456/789
detected_level:Medium Crisis
correct_level:No Crisis
context:User was talking about video game character death, not real crisis
```

**Impact:**
- Improves detection accuracy
- Reduces future false positives
- Enhances context understanding
- Builds community-specific intelligence

#### `/report_false_negative message_link:[link] correct_level:[level] context:[explanation]`
Report when bot missed a crisis situation that should have been detected.

**Why This Matters:**
- Prevents future missed crises
- Expands detection patterns
- Improves community safety
- Enhances system learning

#### `/learning_stats`
View how system learning is improving detection accuracy over time.

### System Monitoring Commands

#### `/crisis_stats`
Comprehensive overview of crisis response system performance.

**Information Provided:**
- Crisis interventions by level (daily, weekly, monthly)
- Response time statistics
- Resolution rate tracking
- Team performance metrics
- Community impact indicators

#### `/conversation_stats`
Detailed metrics about conversation system engagement and effectiveness.

**Metrics Include:**
- Conversation initiation rates
- Average conversation duration
- User engagement percentages
- Successful resource connections
- Follow-up conversation rates

#### `/active_conversations`
Monitor all currently active crisis conversations.

**Use Cases:**
- Identify conversations that may need human intervention
- Coordinate team response to multiple simultaneous crises
- Monitor conversation quality and outcomes
- Plan team coverage during high-activity periods

#### `/test_mention message:[test message]`
Test how bot would respond to a specific message for training and debugging.

**Training Uses:**
- Verify detection accuracy
- Test new keyword effectiveness
- Train team members on system behavior
- Debug unexpected responses

---

## 📊 Analytics & Performance Monitoring

### Daily Team Workflow

#### Morning Briefing (Recommended)
```bash
# Check overnight activity
/crisis_stats

# Review any active conversations
/active_conversations

# Check system health
/conversation_stats

# Review any learning suggestions
/learning_stats
```

#### Ongoing Monitoring
- **Crisis channel monitoring** - Watch for alerts throughout day
- **Pattern recognition** - Notice trends in community crisis patterns
- **Response coordination** - Ensure team coverage for crisis response
- **Documentation** - Record successful interventions and outcomes

#### Weekly Review (Recommended)
```bash
# Review false positive reports
/learning_stats

# Audit keyword effectiveness
/keyword_stats

# Analyze crisis trends
/crisis_stats

# Plan system improvements
# Team discussion of patterns and improvements needed
```

### Key Performance Indicators (KPIs)

#### Crisis Response Effectiveness
- **Response Time**: Average time from detection to team acknowledgment
- **Resolution Rate**: Percentage of crises successfully de-escalated
- **False Positive Rate**: Unnecessary alerts that consume team resources
- **Coverage Quality**: Percentage of actual crises detected by system

#### Community Impact
- **Help-Seeking Increase**: Users more comfortable reaching out
- **Conversation Engagement**: Users continuing discussions after initial response
- **Resource Connection**: Successful connections to mental health resources
- **Community Safety**: Overall reduction in crisis escalation

#### System Learning
- **Detection Accuracy Improvement**: Week-over-week improvement in accuracy
- **False Positive Reduction**: Decline in false alarms over time
- **Community Adaptation**: System learning community-specific patterns
- **Team Efficiency**: Crisis team spending more time on real crises

---

## 🎓 Training & Best Practices

### Crisis Response Best Practices

#### Immediate Response (High Crisis)
1. **Acknowledge urgency** - Respond within 2-5 minutes of alert
2. **Assess situation** - Read full context and bot's analysis
3. **Coordinate team** - Use crisis channel to coordinate response
4. **Direct engagement** - Reach out to user immediately
5. **Follow protocol** - Follow your community's established crisis procedures
6. **Document outcome** - Record intervention success and lessons learned

#### Supportive Response (Medium Crisis)
1. **Timely acknowledgment** - Respond within 10-15 minutes
2. **Natural engagement** - Join conversation organically if appropriate
3. **Resource connection** - Help connect user with appropriate support
4. **Monitor escalation** - Watch for signs of increasing crisis
5. **Team communication** - Keep team informed of support provided
6. **Follow-up planning** - Consider need for ongoing check-ins

#### Monitoring Response (Low Crisis)
1. **Awareness maintenance** - Stay aware of user's situation
2. **Pattern recognition** - Watch for repeated low-crisis indicators
3. **Proactive outreach** - Consider gentle check-in if patterns emerge
4. **Resource preparation** - Be ready to escalate support if needed
5. **Trend documentation** - Note patterns for community health insights

### Training New Team Members

#### System Understanding
- **How detection works** - Keyword + NLP hybrid system
- **Crisis level meanings** - What each level means and requires
- **Response expectations** - Team response times and procedures
- **Command familiarity** - Practice with all crisis management commands

#### Practical Training
- **Shadow experienced members** - Learn from seasoned crisis responders
- **Practice scenarios** - Use test messages to practice responses
- **Role-play conversations** - Practice natural conversation entry
- **Review case studies** - Learn from past successful interventions

#### Ongoing Development
- **Weekly team meetings** - Discuss patterns, improvements, challenges
- **Monthly system reviews** - Analyze effectiveness and plan improvements
- **Quarterly training updates** - Stay current with system enhancements
- **Community feedback** - Incorporate user feedback into practices

### Common Scenarios & Responses

#### Gaming False Positives
**Scenario**: User says "I want to kill this boss, it's driving me crazy"
**Why it's detected**: Keywords "kill" and "driving me crazy"
**Proper response**: 
- Recognize gaming context
- Use `/report_false_positive` to improve system
- No crisis team action needed

#### Creative Writing Triggers
**Scenario**: User writing fiction with crisis themes
**System handling**: Context detection should reduce false positives
**Team response**: Monitor but typically no intervention needed

#### Identity Crisis (LGBTQIA+ Specific)
**Scenario**: User expressing distress about identity, coming out, family rejection
**System strength**: Community-aware patterns detect identity-related crisis
**Team response**: 
- Specialized LGBTQIA+ crisis resources
- Understanding of identity-specific challenges
- Connection to community-specific support

#### Relationship Crisis
**Scenario**: User expressing distress about breakup, rejection, isolation
**Detection pattern**: Often medium-crisis level detection
**Team approach**:
- Validate emotional experience
- Distinguish between heartbreak and crisis
- Provide appropriate level of support

---

## 🔧 Troubleshooting Common Issues

### System Issues

#### Bot Not Responding to Crisis
**Symptoms**: No crisis detection on obvious crisis messages
**Possible Causes**:
- NLP service connection issues
- Keyword system not loaded
- Bot permissions insufficient
- Message too long for analysis

**Troubleshooting Steps**:
1. Check bot health: Verify bot is online and responding
2. Test NLP connection: Use monitoring commands to verify NLP service
3. Review message content: Check if message exceeds length limits
4. Check permissions: Ensure bot can read messages in channel
5. Manual escalation: If system fails, manually escalate crisis

**Resolution**:
- Use `/test_mention` to verify system function
- Contact technical support if issues persist
- Always manually handle crisis if system unavailable

#### Too Many False Positives
**Symptoms**: Bot alerting on non-crisis messages frequently
**Common Causes**:
- Gaming discussions triggering "kill" or "die" keywords
- Creative writing or roleplay containing crisis language
- Hyperbolic expressions being taken literally

**Solutions**:
1. **Report false positives**: Use `/report_false_positive` for each incident
2. **Review keywords**: Use `/list_keywords` to identify problematic patterns
3. **Remove problematic keywords**: Use `/remove_keyword` for consistently false triggers
4. **Context training**: System learns to recognize gaming/creative contexts

#### Missing Crisis Situations
**Symptoms**: Team noticing crises that bot didn't detect
**Investigation Steps**:
1. **Review message content**: Check if crisis was expressed in detectable language
2. **Check keyword coverage**: See if crisis language matches current keywords
3. **Report false negative**: Use `/report_false_negative` to improve system
4. **Expand keywords**: Add relevant crisis expressions to keyword system

### Team Coordination Issues

#### Response Time Problems
**Issue**: Team not responding quickly enough to crisis alerts
**Solutions**:
- **Notification settings**: Ensure team has proper Discord notifications enabled
- **Coverage planning**: Establish team schedules for crisis coverage
- **Escalation procedures**: Clear procedures for when primary responder unavailable
- **Backup systems**: Secondary alert methods for critical situations

#### Role Confusion
**Issue**: Team members unsure when to respond or how
**Solutions**:
- **Clear role definitions**: Document who responds to what crisis levels
- **Response training**: Regular practice with different crisis scenarios
- **Decision trees**: Clear flowcharts for crisis response decisions
- **Team communication**: Use crisis channel for coordination

### User Experience Issues

#### Users Complaining About Bot Responses
**Issue**: Community members finding bot responses inappropriate or intrusive
**Investigation**:
1. **Review specific incidents**: Get details about concerning responses
2. **Check context detection**: Verify if context was properly understood
3. **Gather feedback**: Use community input to identify patterns
4. **Adjust system**: Use learning commands to improve responses

**Solutions**:
- **Community education**: Help users understand bot's purpose and limitations
- **Response customization**: Work with technical team to adjust response tone
- **Opt-out options**: Ensure users can request exclusion if needed
- **Continuous improvement**: Regular feedback collection and system updates

---

## 📞 Support & Resources

### Technical Support
- **GitHub Issues**: [Report bugs and request features](https://github.com/the-alphabet-cartel/ash-bot/issues)
- **Community Discord**: [Join support discussions](https://discord.gg/alphabetcartel)
- **Documentation**: Comprehensive technical documentation in `docs/` folder
- **Emergency Contact**: Direct contact for critical system issues

### Crisis Resources for Team Reference

#### Immediate Crisis Resources
- **US Crisis Hotline**: 988 (Call or text, 24/7)
- **Crisis Text Line**: Text HOME to 741741
- **International Crisis Lines**: https://www.iasp.info/resources/Crisis_Centres/

#### LGBTQIA+ Specific Resources
- **LGBTQ National Hotline**: 1-888-843-4564
- **Trans Lifeline**: 877-565-8860 (US), 877-330-6366 (Canada)
- **The Trevor Project**: 1-866-488-7386 (Under 25, LGBTQ crisis support)

#### Professional Resources
- **SAMHSA National Helpline**: 1-800-662-4357 (Mental health and substance abuse)
- **National Alliance on Mental Illness**: https://www.nami.org/
- **Crisis Intervention Specialists**: Local professional crisis intervention services

### Training Resources
- **Crisis Intervention Training**: Recommended courses for team members
- **LGBTQIA+ Cultural Competency**: Understanding community-specific needs
- **Mental Health First Aid**: General mental health crisis response training
- **Discord Community Management**: Best practices for online community crisis response

---

## 🏳️‍🌈 Community-Specific Considerations

### LGBTQIA+ Crisis Patterns

#### Coming Out Crisis
**Common triggers**: Family rejection, identity questioning, fear of loss
**Detection patterns**: Identity-specific language, family conflict, self-doubt
**Response approach**: Validate identity, provide LGBTQIA+ specific resources, connect with community support

#### Transition-Related Distress
**Common triggers**: Medical access barriers, social rejection, dysphoria
**Detection patterns**: Body image distress, medical frustration, social isolation
**Response approach**: Trans-specific resources, medical support information, peer connection

#### Community Rejection
**Common triggers**: Exclusion from LGBTQIA+ spaces, identity policing, discrimination
**Detection patterns**: Belonging concerns, identity invalidation, community isolation
**Response approach**: Alternative community connections, identity validation, inclusive resources

### Cultural Sensitivity Guidelines

#### Language Awareness
- **Inclusive pronouns**: Always respect and use correct pronouns
- **Identity terminology**: Stay current with evolving community language
- **Avoid assumptions**: Don't assume identity, relationships, or experiences
- **Cultural competency**: Understand diverse LGBTQIA+ experiences and challenges

#### Resource Appropriateness
- **LGBTQIA+ specific**: Prioritize community-specific crisis resources
- **Intersectional support**: Consider multiple identity factors (race, disability, age)
- **Geographic considerations**: Provide resources appropriate to user's location
- **Accessibility**: Ensure resources are accessible to users with disabilities

### Building Community Trust

#### Transparency
- **System explanation**: Help community understand how detection works
- **Privacy assurance**: Clearly communicate privacy protections
- **Feedback incorporation**: Show how community input improves system
- **Decision transparency**: Explain why certain responses or escalations happen

#### Community Autonomy
- **Respect boundaries**: Honor community and individual boundaries
- **Support self-determination**: Empower rather than override community decisions
- **Cultural responsiveness**: Adapt to community-specific needs and preferences
- **Collaborative improvement**: Work with community to enhance system effectiveness

---

**Remember: Technology serves community wellbeing. Your role as a crisis response team member is to bridge the gap between automated detection and human compassion, ensuring that every community member receives appropriate, timely, and culturally competent crisis support.**

**For additional support or questions about this guide, reach out to:**
- **Community Discord**: [https://discord.gg/alphabetcartel](https://discord.gg/alphabetcartel)
- **Documentation Team**: Available through GitHub issues
- **Crisis Response Coordination**: Direct contact through established community channels

*Built with ❤️ for chosen family, one crisis response at a time.*