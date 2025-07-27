# 🖤 Ash Bot v2.0 Team Guide - "Adaptive Crisis Intelligence"

> *How to use Ash's enhanced learning system for better crisis detection*

## What is Ash?

Ash is an intelligent Discord bot designed to detect mental health crises in your community and coordinate team responses. **Version 2.0 introduces revolutionary learning capabilities** that adapt to your community's unique language patterns.

### 🧠 **What's New in v2.0**
- **Enhanced Learning System** - Ash learns from your corrections to improve detection accuracy
- **Advanced AI Integration** - Multi-model analysis with depression detection + sentiment analysis
- **Smart Cost Optimization** - 80-90% reduction in AI costs while improving accuracy
- **Real-time Adaptation** - System adjusts immediately based on your feedback
- **Comprehensive Analytics** - Detailed statistics on detection improvements

---

## 🎯 How Crisis Detection Works

### **Three Crisis Levels**

**🔴 HIGH Crisis** - *Immediate Response Required*
- **Detected Language**: Suicidal ideation, self-harm plans, severe despair
- **Ash Response**: Immediate support + crisis resources
- **Team Alert**: Red alert in crisis response channel + role ping
- **Staff DM**: PapaBearDoes receives detailed private message
- **Examples**: "want to die," "kill myself," "have a plan," "better off without me"

**🟡 MEDIUM Crisis** - *Team Awareness Needed*
- **Detected Language**: Significant distress, hopelessness, struggling language
- **Ash Response**: Supportive reply + gentle resource suggestions
- **Team Alert**: Orange alert in crisis response channel 
- **Examples**: "everything feels pointless," "can't handle this," "really struggling"

**🟢 LOW Crisis** - *Gentle Support*
- **Detected Language**: Mild distress, sadness, emotional difficulty
- **Ash Response**: Validation + encouragement
- **Team Alert**: None (handled by Ash)
- **Examples**: "feeling down," "rough day," "overwhelmed"

### **🤖 Enhanced Detection System**

Ash v2.0 uses a sophisticated multi-layered approach:

1. **Keyword Matching** - Built-in + your custom keywords
2. **AI Analysis** - Depression detection + sentiment analysis (runs on 10.20.30.16)
3. **Context Intelligence** - Distinguishes jokes, movies, games from real crisis language
4. **Learning Adjustments** - Applies community-trained sensitivity modifications
5. **Smart Filtering** - Advanced protection against false positives

---

## 🛠️ Slash Commands for Crisis Response Team

### **Custom Keyword Management** *(Existing)*

**`/add_keyword`**
- **Purpose**: Add community-specific crisis language
- **Usage**: `/add_keyword crisis_level:Medium Crisis keyword:dysphoria hitting hard`
- **Effect**: Keyword immediately becomes active

**`/remove_keyword`**
- **Purpose**: Remove problematic keywords causing false positives
- **Usage**: `/remove_keyword crisis_level:Low Crisis keyword:old phrase`
- **Effect**: Keyword immediately deactivated

**`/list_keywords`**
- **Purpose**: View all custom keywords for a crisis level
- **Usage**: `/list_keywords crisis_level:High Crisis`

**`/keyword_stats`**
- **Purpose**: Overview statistics for all custom keywords
- **Usage**: `/keyword_stats`

### **🧠 Enhanced Learning Commands** *(NEW in v2.0)*

**`/report_false_positive`**
- **Purpose**: Report when Ash incorrectly flagged something as a crisis
- **Usage**: `/report_false_positive message_link:https://discord.com/... detected_level:High Crisis correct_level:None context:User was talking about a video game`
- **Effect**: System learns to be less sensitive to similar language
- **Example**: Ash flagged "that boss fight killed me" as High Crisis, but it was gaming talk

**`/report_missed_crisis`** *(Previously `/report_false_negative`)*
- **Purpose**: Report when Ash missed a real crisis situation
- **Usage**: `/report_missed_crisis message_link:https://discord.com/... missed_level:Medium Crisis actual_detected:None context:Clear distress in community-specific language`
- **Effect**: System learns to be more sensitive to similar patterns
- **Example**: Someone said "not doing so hot today" (community language for distress) but Ash didn't respond

**`/learning_stats`**
- **Purpose**: View comprehensive learning system performance
- **Usage**: `/learning_stats`
- **Shows**: False positive/negative reports, learning trends, system balance

---

## 🆘 Crisis Response Workflows

### **When You Get a HIGH Crisis Alert (🔴)**

1. **⚡ Immediate Response Required**
   - Check crisis response channel for team coordination
   - **Say**: "I see this alert, responding now" (in crisis channel)

2. **📊 Assess Accuracy**
   - If the alert seems inappropriate, use `/report_false_positive`
   - If it's accurate, proceed with response

3. **🤝 Coordinate Response**
   - **One primary responder** reaches out directly to the person
   - Others provide support in crisis channel
   - Avoid overwhelming the person with multiple responders

4. **📞 Escalate if Needed**
   - Professional resources in #resources channel
   - Emergency services if immediate physical danger

5. **📋 Staff Notification**
   - PapaBearDoes automatically receives detailed DM with full context

### **When You Get a MEDIUM Crisis Alert (🟡)**

1. **👀 Monitor the Situation**
   - Review the message and context
   - Watch for signs of escalation

2. **📊 Assess Accuracy**
   - If inappropriate, use `/report_false_positive`
   - Note if similar language should be higher/lower priority

3. **🤗 Provide Additional Support**
   - If the person needs more than Ash's initial response
   - Gentle check-in or additional resources

4. **📈 Watch for Patterns**
   - Notice community-specific language that might need keywords

### **When You Notice Missed Crises**

1. **🚨 Report Immediately**
   - Use `/report_missed_crisis` for any crisis Ash should have caught
   - Include context about why it was a crisis

2. **➕ Add Keywords**
   - Use `/add_keyword` for community-specific language patterns
   - Consider LGBTQIA+ specific terminology

3. **📊 Monitor Improvement**
   - Check `/learning_stats` to see how the system adapts
   - Watch for similar situations to see if detection improves

---

## 🧠 Understanding the Learning System

### **How Learning Works**

The v2.0 learning system operates on two levels:

**Local Learning (Bot)**
- Tracks your reports in local database
- Immediate pattern recognition
- Statistics and trend analysis

**AI Learning (NLP Server at 10.20.30.16)**
- Advanced pattern analysis using depression + sentiment models
- Real-time sensitivity adjustments
- Context-aware improvements

### **Learning Limits & Safety**
- **Maximum 50 learning adjustments per day** (prevents over-tuning)
- **Confidence threshold 0.6** (only high-confidence adjustments applied)
- **Human oversight required** (all changes tracked and logged)

### **Learning Statistics Example**
```
📊 Comprehensive Learning Statistics
├── Overall Learning Progress
│   ├── False Positives: 154 (over-detection)
│   ├── Missed Crises: 93 (under-detection)
│   ├── Total Reports: 247
│   └── Improvements Made: 89 detection adjustments
├── Recent Trends (30 Days)
│   ├── Over-Detection Rate: 12.3%
│   ├── Under-Detection Rate: 8.1%
│   ├── Learning Rate: 2.3 reports/day
│   └── Balance: Slightly over-sensitive
└── Learning System Status
    ├── NLP Server: ✅ Connected
    ├── Real-time Learning: Enabled
    └── Patterns Learned: 47 community-specific
```

---

## 📊 Advanced Analytics & Monitoring

### **What to Monitor**

**Detection Accuracy Trends**
- Are false positives decreasing over time?
- Are we catching more real crises?
- Is the system balanced or too sensitive in either direction?

**Community Language Evolution**
- New phrases emerging in your community
- LGBTQIA+ specific terminology not being caught
- Generational language changes

**Team Response Effectiveness**
- Response times to alerts
- Coordination efficiency
- Member feedback on support quality

### **Using Learning Data for Improvements**

**If Over-Detection Rate is High (>15%)**
- Focus on reporting false positives
- Look for common patterns in inappropriate alerts
- Consider context clues (gaming, movies, work stress)

**If Under-Detection Rate is High (>10%)**
- Focus on reporting missed crises
- Add community-specific keywords
- Pay attention to subtle distress language

**If System is Balanced (5-10% each)**
- Continue current approach
- Fine-tune specific edge cases
- Focus on community-specific adaptations

---

## 🎯 Best Practices for v2.0

### **Keyword Management**

**✅ Good Keywords to Add:**
- Community-specific language: "dysphoria overwhelming," "family rejected me"
- Generational terminology: "no cap feeling hopeless," "lowkey suicidal"
- Identity-specific distress: "closet suffocating," "transition regret"
- Subtle crisis language: "not doing great," "pretty rough"

**❌ Keywords to Avoid:**
- Common gaming terms: "killed," "destroyed," "murdered"
- Movie/entertainment language: "dead," "dying," "killed me"
- Work stress without crisis context: "overwhelming project"
- Casual expressions: "I'm dead" (from laughter)

### **Learning System Usage**

**Report False Positives When:**
- Ash flagged gaming, movie, or entertainment discussion
- Common expressions were misinterpreted (e.g., "I'm dead tired")
- Work stress or school pressure was over-flagged
- Jokes or humor were detected as crisis

**Report Missed Crises When:**
- Clear distress signals went unnoticed
- Community-specific crisis language wasn't caught
- Subtle but genuine crisis expressions were missed
- Identity-specific distress wasn't recognized

**Use Learning Stats to:**
- Track improvement trends monthly
- Identify if system is too sensitive or not sensitive enough
- Understand which types of errors are most common
- Guide team training and awareness

---

## 🚫 What NOT to Do

### **Common Mistakes**
- **Don't ignore alerts** - even if no immediate action needed, awareness is important
- **Don't assume others will respond** - coordinate in crisis channel
- **Don't overwhelm the person** - one primary responder, others support
- **Don't report learning errors hastily** - consider context carefully
- **Don't add keywords without team discussion** - might increase false positives

### **Learning System Cautions**
- **Don't report every minor issue** - focus on clear errors
- **Don't expect instant perfection** - learning takes time and data
- **Don't over-report the same pattern** - one report per pattern type is usually enough
- **Don't ignore the daily learning limits** - system prevents over-tuning for stability

---

## 🔧 Technical Features Team Should Know

### **Always Available**
- Runs 24/7 in Docker containers on Linux server
- NLP analysis server runs on Windows 11 with RTX 3050 GPU
- Automatic restarts and health monitoring

### **Enhanced Security**
- All slash commands restricted to Crisis Response role
- Complete audit trail of all changes with user attribution
- Learning data encrypted and stored locally
- No external data sharing beyond Claude API

### **Cost Optimization**
- 80-90% reduction in expensive AI API calls
- Most analysis runs locally on your hardware
- Smart routing for complex cases only
- Daily limits prevent cost overruns

### **Real-time Updates**
- Keyword changes effective immediately
- Learning adjustments applied in real-time
- No restart required for most changes
- Configuration validation prevents errors

---

## 📞 Emergency Protocols

### **If Ash is Down**
1. Monitor channels manually for crisis language
2. Use existing crisis response procedures
3. Report technical issues to administration
4. Document missed cases for later analysis

### **If Learning System Malfunctions**
1. Continue using regular keyword management
2. Report technical issues immediately
3. Use manual crisis detection procedures
4. Save examples for system repair

### **If Crisis Response Channel Unavailable**
1. Use direct messages for coordination
2. Alert staff lead directly
3. Continue individual crisis responses
4. Document actions for later review

---

## 🎓 Slash Commands Reference

### **Keyword Management**
```bash
/add_keyword crisis_level:High Crisis keyword:transition regret overwhelming
/remove_keyword crisis_level:Medium Crisis keyword:old phrase
/list_keywords crisis_level:Low Crisis
/keyword_stats
```

### **Learning System**
```bash
/report_false_positive 
  message_link:https://discord.com/channels/...
  detected_level:High Crisis
  correct_level:None
  context:User discussing video game boss fight

/report_missed_crisis
  message_link:https://discord.com/channels/...
  missed_level:Medium Crisis
  actual_detected:None
  context:Clear distress in community-specific language

/learning_stats
```

**Notes:**
- All commands restricted to Crisis Response role
- Changes take effect immediately  
- All modifications logged with user and timestamp
- Responses are private (only you see them)

---

## 📈 Success Metrics for v2.0

### **Detection Improvements**
- **Accuracy**: Target 85%+ (up from 75% baseline)
- **False Positive Rate**: Target <8% (down from 15%)
- **False Negative Rate**: Target <5% (missed crises)
- **Response Time**: <500ms for full analysis

### **Team Efficiency**
- **Faster crisis response times** compared to manual-only detection
- **Increased crisis intervention rates** (catching more situations)
- **Reduced false alert fatigue** through learning
- **Better community adaptation** through custom keywords and learning

### **Community Benefits**
- **Community feedback** on feeling supported
- **Reduced burnout** from 24/7 monitoring burden
- **Better LGBTQIA+ support** through community-specific language learning
- **Evolved support** as detection improves with community growth

---

## 🤔 Questions & Support

### **Common Questions**

**Q: How long does it take for learning to take effect?**
A: Learning adjustments are applied in real-time. You should see improvements immediately for similar patterns.

**Q: What if I make a mistake reporting a false positive/negative?**
A: Contact administration. Learning data can be reviewed and corrected if needed.

**Q: How do I know if my reports are making a difference?**
A: Use `/learning_stats` to see learning trends and improvements over time.

**Q: Can I see what the NLP server is learning?**
A: The system tracks patterns but doesn't expose raw learning data. Use stats commands for insights.

### **Getting Help**

**For Technical Issues:**
- Report in development/admin channels
- Include error messages and steps to reproduce
- Mention if it affects crisis response capability

**For Learning System Questions:**
- Check `/learning_stats` first for trends
- Discuss patterns with other team members
- Contact administration for system-level issues

**For Crisis Response Guidance:**
- Use team coordination channels
- Escalate to professional resources when needed
- Follow existing crisis response protocols

---

## 🔮 Future Improvements (Roadmap)

### **v2.1 (Planned)**
- **Analytics Dashboard** - Web interface for learning metrics visualization
- **Bulk Keyword Management** - Import/export capabilities
- **Advanced Pattern Recognition** - More sophisticated community language learning
- **Multi-Language Support** - Spanish and other languages

### **v2.5 (Future)**
- **Conversation Tracking** - Multi-message crisis monitoring
- **Predictive Analytics** - Early warning systems
- **External Resource Integration** - Direct connections to crisis services
- **Advanced Personalization** - User-specific support patterns

---

## 🙏 Remember

### **Core Principles**
- **Human connection remains central** - Ash enhances but doesn't replace human care
- **Community language evolves** - The learning system helps Ash grow with you
- **Every report matters** - Your feedback directly improves detection for everyone
- **Collaboration is key** - Crisis response is a team effort

### **Team Support**
- **You're not alone** - The team supports each other through difficult cases
- **Self-care is crucial** - Crisis response work can be emotionally demanding
- **Every intervention matters** - Even small responses can save lives
- **Learning never stops** - Both Ash and the team continuously improve

---

**We're building chosen family, one conversation at a time. With v2.0's learning capabilities, Ash grows smarter and more attuned to our community's unique needs with every interaction.**

---

*For technical documentation, see the main README.md files for both the bot and NLP server repositories.*