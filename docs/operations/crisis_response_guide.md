# Crisis Response Team Guide

## Welcome, CRT Member! 💜

Thank you for being part of our Crisis Response Team. Your role is vital to keeping our community safe. This guide will help you understand how Ash-Bot works and how to use it effectively.

---

## Table of Contents

1. [What is Ash-Bot?](#what-is-ash-bot)
2. [Understanding Alerts](#understanding-alerts)
3. [Alert Channels](#alert-channels)
4. [Reading an Alert](#reading-an-alert)
5. [Responding to Alerts](#responding-to-alerts)
6. [Working with Ash AI](#working-with-ash-ai)
7. [Using the History Button](#using-the-history-button)
8. [Best Practices](#best-practices)
9. [Quick Reference Card](#quick-reference-card)
10. [Getting Help](#getting-help)

---

## What is Ash-Bot?

Ash-Bot is our community's crisis detection system. It works quietly in the background, reading messages in monitored channels and looking for signs that someone might be struggling.

### How It Works (Simple Version)

```
Community Member Posts Message
           ↓
    Ash-Bot Reads It
           ↓
   AI Analyzes for Crisis Signs
           ↓
  If Concerning → Alert Sent to CRT
           ↓
     You Respond & Help
```

### What Ash-Bot Does NOT Do

- ❌ Read DMs (private messages)
- ❌ Monitor every channel (only approved channels)
- ❌ Replace human judgment
- ❌ Automatically ban or punish anyone
- ❌ Share information outside our team

---

## Understanding Alerts

Ash-Bot categorizes alerts by how urgent they are:

### Severity Levels

| Level | Color | What It Means | Your Response |
|-------|-------|---------------|---------------|
| 🔴 **CRITICAL** | Red | Immediate danger signs detected | Drop everything - respond NOW |
| 🟠 **HIGH** | Orange | Serious concern detected | Respond within minutes |
| 🟡 **MEDIUM** | Yellow | Moderate concern detected | Check in when you can |

### What Triggers Each Level

**🔴 CRITICAL** - May include:
- Direct statements about self-harm
- Goodbye messages
- Immediate crisis language

**🟠 HIGH** - May include:
- Strong emotional distress
- Hopelessness expressions
- Escalating concerning behavior

**🟡 MEDIUM** - May include:
- Negative emotional patterns
- Vague concerning statements
- Early warning signs

---

## Alert Channels

Alerts go to different channels based on severity:

| Severity | Channel | Who Gets Pinged |
|----------|---------|-----------------|
| 🔴 CRITICAL | #crisis-critical | @CrisisResponse + DMs to leads |
| 🟠 HIGH | #crisis-response | @CrisisResponse |
| 🟡 MEDIUM | #crisis-monitor | No ping (check periodically) |

### Your Responsibility

- **#crisis-critical**: Check immediately when pinged
- **#crisis-response**: Check immediately when pinged
- **#crisis-monitor**: Check at least every few hours during your shift

---

## Reading an Alert

When you see an alert, here's what each part means:

```
┌────────────────────────────────────────────────────────────┐
│ 🚨 CRISIS DETECTED - HIGH                          🟠     │
├────────────────────────────────────────────────────────────┤
│                                                            │
│ 👤 User: @JaneDoe                                          │  ← Who needs help
│ 📍 Channel: #venting                                       │  ← Where they posted
│ 🕐 Time: January 4, 2026 at 2:30 PM                       │  ← When it happened
│                                                            │
├────────────────────────────────────────────────────────────┤
│ Analysis Results                                           │
│                                                            │
│ Crisis Score: 0.78 │ Confidence: 87%                       │  ← How sure the AI is
│ Pattern: Escalating (3 msgs in 2 hours)                    │  ← Getting worse?
│                                                            │
├────────────────────────────────────────────────────────────┤
│ Key Signals                                                │
│                                                            │
│ • 🔴 emotional distress detected                           │  ← What the AI noticed
│ • 🟠 negative sentiment                                    │
│ • 🟢 message is sincere (not sarcastic)                    │
│                                                            │
├────────────────────────────────────────────────────────────┤
│ Recommendation                                             │
│                                                            │
│ ⚠️ Priority response recommended                           │  ← What to do
│                                                            │
├────────────────────────────────────────────────────────────┤
│                                                            │
│ [🙋 Acknowledge] [💬 Talk to Ash] [📜 History]             │  ← Your action buttons
│                                                            │
└────────────────────────────────────────────────────────────┘
```

### Understanding the Score

- **Crisis Score**: 0.0 (no concern) to 1.0 (extreme concern)
- **Confidence**: How sure the AI is about its assessment
- **Pattern**: Whether this person's messages are getting more concerning over time

---

## Responding to Alerts

### Step 1: Click "Acknowledge"

**Always click this first!** It tells the team:
- You've seen the alert
- You're handling it
- Others don't need to duplicate effort

The alert will update to show your name and timestamp.

### Step 2: Go to the User

1. Click on the channel name in the alert (e.g., #general-chat)
2. Find the user's recent messages
3. Read what they wrote to understand the context

### Step 3: Reach Out

You have several options:

**Option A: Reply in Channel**
- Good for: General support, when others might benefit
- Example: "Hey @JaneDoe, I noticed you might be having a rough time. Want to talk?"

**Option B: Send a DM**
- Good for: Private matters, more serious situations
- Example: "Hey, I saw your message in #general-chat. I'm here if you want to talk privately."

**Option C: Let Ash Help First**
- Click "Talk to Ash" button
- Ash AI will send a supportive message to start the conversation
- You can jump in whenever you're ready

### Step 4: Document (If Needed)

For serious situations, make a note in #crt-logs including:
- User's name
- Brief summary
- Actions taken
- Follow-up needed?

---

## Working with Ash AI

Ash is our AI support companion. When activated, Ash can:

- Send an initial supportive message
- Keep the person engaged while you get there
- Provide compassionate responses

### Activating Ash

Click the **"Talk to Ash"** button on an alert. Ash will:
1. Send a gentle opening message to the user
2. Continue the conversation if they respond
3. Keep you updated on what's happening

### Taking Over from Ash

When you're ready to handle things personally, simply say in the channel:

> "Ash, I've got this"

or

> "Ash, I'll take over"

Ash will acknowledge and step back, letting you continue.

### When Ash Helps Most

- ✅ When you need a moment to read the situation
- ✅ During busy times when response might be delayed
- ✅ For initial engagement while you prepare
- ✅ When the person might respond better to a gentle AI first

### When to Skip Ash

- ⚠️ When you know the person well personally
- ⚠️ For CRITICAL alerts (jump in immediately)
- ⚠️ When the situation needs human judgment right away

---

## Using the History Button

The **📜 History** button shows you the person's recent patterns:

```
┌────────────────────────────────────────────────────────────┐
│ 📊 History for @JaneDoe                                    │
├────────────────────────────────────────────────────────────┤
│                                                            │
│ Summary                                                    │
│ Total Messages Analyzed: 45                                │
│ Previous Crisis Events: 2                                  │
│ Highest Past Severity: HIGH                                │
│ Pattern: Occasional struggles, usually recovers well       │
│                                                            │
├────────────────────────────────────────────────────────────┤
│ Recent Activity                                            │
│                                                            │
│ Today 2:30 PM - #venting - HIGH (0.78)                     │
│   "emotional distress detected"                            │
│                                                            │
│ Today 1:15 PM - #venting - MEDIUM (0.52)                   │
│   "negative sentiment"                                     │
│                                                            │
│ Yesterday - #general - SAFE (0.12)                         │
│   "normal conversation"                                    │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

### Why History Matters

- **Escalating Pattern**: If scores are increasing → more urgent
- **First-Time Alert**: Be extra gentle, they may not know we're watching
- **Repeat Concern**: May need longer-term support discussion
- **Recovery Pattern**: They've been through this before and recovered

---

## Best Practices

### Do ✅

- **Acknowledge alerts quickly** - Even if you can't respond right away
- **Be genuine** - People can tell when you care
- **Listen first** - Let them share before offering advice
- **Validate feelings** - "That sounds really hard" goes a long way
- **Know your limits** - It's okay to tag in another CRT member
- **Take care of yourself** - This work can be heavy

### Don't ❌

- **Don't ignore alerts** - Even MEDIUM alerts deserve attention
- **Don't dismiss feelings** - "It's not that bad" doesn't help
- **Don't promise confidentiality you can't keep** - Be honest about team awareness
- **Don't diagnose** - We're supporters, not doctors
- **Don't force conversation** - Respect if they don't want to talk

### For CRITICAL Alerts

1. **Stop what you're doing**
2. **Click Acknowledge immediately**
3. **Go to the user NOW**
4. **If immediate danger**: Contact server leadership
5. **Stay with them** until the situation stabilizes

### Self-Care Reminders

- It's okay to step back if you're overwhelmed
- Tag another CRT member if you need a break
- Debrief with the team after difficult situations
- Your mental health matters too 💜

---

## Quick Reference Card

### Alert Response Flowchart

```
Alert Received
      ↓
Is it CRITICAL? ──Yes──→ DROP EVERYTHING → Respond Immediately
      ↓ No
Is it HIGH? ──Yes──→ Respond within minutes
      ↓ No
Is it MEDIUM? ──Yes──→ Check in when available
      ↓
Click "Acknowledge" → Read Context → Reach Out → Document if needed
```

### Button Quick Guide

| Button | When to Use |
|--------|-------------|
| 🙋 **Acknowledge** | ALWAYS click first |
| 💬 **Talk to Ash** | Want AI to start conversation |
| 📜 **History** | Need context on this person |

### Handoff Phrases (to take over from Ash)

- "Ash, I've got this"
- "Ash, I'll take over"
- "Ash, step back please"

### Severity Response Times

| Severity | Target Response |
|----------|-----------------|
| 🔴 CRITICAL | Immediate (< 2 minutes) |
| 🟠 HIGH | Within 5-10 minutes |
| 🟡 MEDIUM | Within 1-2 hours |

---

## Getting Help

### Questions About Ash-Bot?

- Ask in #crt-discussion
- Tag @TechTeam for technical issues
- Check #project-details for updates

### Difficult Situations?

- Tag senior CRT member
- Post in #crt-urgent
- Contact server leadership for emergencies

### Technical Problems?

If Ash-Bot isn't working:
1. Check #bot-alerts for announcements
2. Tag @TechTeam
3. Continue monitoring manually until fixed

---

## Remember

You're not alone in this. The whole CRT team has your back. When in doubt, reach out to a fellow team member. 

Our community trusts us to be there when they need support. By being part of this team, you're making a real difference in people's lives.

Thank you for everything you do. 💜

---

## Emergency Resources

If someone is in **immediate danger**, these resources can help:

- **988 Suicide & Crisis Lifeline**: Call or text 988 (US and Canada)
- **Crisis Text Line**: Text HOME to 741741 (US)
- **Trevor Project** (LGBTQ+): 1-866-488-7386
- **Trans Lifeline**: 877-565-8860

*Always prioritize safety. It's okay to share these resources.*

---

**Built with care for chosen family** 🏳️‍🌈
