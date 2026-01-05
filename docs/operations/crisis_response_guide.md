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
7. [Taking Over from Ash](#taking-over-from-ash)
8. [Adding Session Notes](#adding-session-notes)
9. [Follow-Up Check-Ins](#follow-up-check-ins)
10. [Using Slash Commands](#using-slash-commands)
11. [User Opt-Out System](#user-opt-out-system)
12. [Using the History Button](#using-the-history-button)
13. [Weekly Reports](#weekly-reports)
14. [Best Practices](#best-practices)
15. [Quick Reference Card](#quick-reference-card)
16. [Getting Help](#getting-help)

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
           ↓
   Ash May Follow Up Later
```

### What Ash-Bot Does NOT Do

- ❌ Read DMs (private messages)
- ❌ Monitor every channel (only approved channels)
- ❌ Replace human judgment
- ❌ Automatically ban or punish anyone
- ❌ Share information outside our team
- ❌ Contact users who have opted out

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
- Send follow-up check-ins after sessions

### Activating Ash

Click the **"Talk to Ash"** button on an alert. Ash will:
1. Send a gentle opening message to the user
2. Continue the conversation if they respond
3. Keep you updated on what's happening

### Auto-Initiate Feature

If an alert goes unacknowledged for a few minutes, Ash may **automatically reach out** to the user. This ensures no one falls through the cracks during busy times.

When auto-initiate activates:
- The alert will update to show "Ash Auto-Initiated"
- You should still acknowledge the alert
- You can take over from Ash at any time

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

## Taking Over from Ash

When Ash is in a conversation with someone, you can take over at any time. There are two ways:

### Method 1: Use the Take Over Button

On the alert embed, click the **"🤝 Take Over"** button. You'll be prompted to:
1. Confirm you want to take over
2. Add optional notes about why (e.g., "User asked for a human")

### Method 2: Say It in Chat

While Ash is talking with someone, simply type one of these phrases:
- "Ash, I've got this"
- "Ash, I'll take over"
- "Ash, step back please"

Ash will acknowledge and step back gracefully.

### What Happens When You Take Over

1. Ash stops responding to the user
2. The session is marked as "handed off to CRT"
3. Any notes you added are saved for reference
4. **No automatic follow-up will be scheduled** (you're handling it now)
5. The alert embed updates to show you took over

### Adding Handoff Notes

When you take over, consider adding brief notes:
- Why you're taking over
- What the user needs
- Any important context

Example: "User specifically asked to talk to a real person. Seems to be dealing with family issues."

These notes help other CRT members if they need to step in later.

---

## Adding Session Notes

You can add notes to any active or completed Ash session using the `/ash notes` command.

### Why Add Notes?

- Document important information about a user's situation
- Help other CRT members understand context
- Track patterns over time
- Record follow-up actions needed

### How to Add Notes

```
/ash notes add user:@JaneDoe note:User mentioned recent job loss. 
Seemed calmer after talking. May need check-in next week.
```

### Viewing Notes

```
/ash notes view user:@JaneDoe
```

This shows recent notes added by CRT members for that user.

### Best Practices for Notes

- **Be factual**: Stick to what was said/observed
- **Be brief**: Key points only
- **Be kind**: Remember, other CRT members will read this
- **No diagnosis**: We document, we don't diagnose

---

## Follow-Up Check-Ins

After an Ash session ends naturally, Ash may send a **follow-up check-in** to the user via DM approximately 24 hours later.

### How It Works

1. User has a conversation with Ash
2. Session ends (times out or user stops responding)
3. ~24 hours later, Ash sends a gentle check-in DM
4. If the user responds, a new mini-session starts

### Example Follow-Up Message

> "Hey! I've been thinking about you since we talked yesterday. How are you feeling today? No pressure to chat if you're not up for it - just wanted you to know I'm here. 💜 - Ash 🤖💜"

### Who Gets Follow-Ups

Follow-ups are sent to users who:
- Had a session with **MEDIUM or higher** severity
- **Have NOT opted out** of Ash
- Haven't received a follow-up in the last 24 hours
- Were **not handed off to CRT** (you're handling the follow-up if you took over)

### Why This Matters for CRT

- If you **take over** a session, no automatic follow-up is sent
- You're responsible for any follow-up when you take over
- If you see someone got a follow-up and responded, check in with them

---

## Using Slash Commands

Ash-Bot includes several slash commands to help you manage situations.

### Available Commands

| Command | What It Does | Who Can Use |
|---------|--------------|-------------|
| `/ash status` | Check your opt-out status | Everyone |
| `/ash optout` | Opt out of Ash interaction | Everyone |
| `/ash optin` | Opt back in to Ash | Everyone |
| `/ash health` | Check if Ash-Bot is working | CRT Members |
| `/ash stats` | View response time statistics | CRT Members |
| `/ash notes add` | Add notes about a user | CRT Members |
| `/ash notes view` | View notes about a user | CRT Members |

### Checking System Health

If you suspect Ash-Bot isn't working:

```
/ash health
```

This shows you:
- Whether Ash-Bot is online
- Connection status to Discord
- NLP service status
- Redis (database) status

### Viewing Response Statistics

```
/ash stats
```

Shows team performance metrics:
- Average response time
- Alerts by severity
- Response rate trends

---

## User Opt-Out System

Some community members may choose to **opt out** of Ash interaction. This is their right, and we respect it.

### What Opt-Out Means

When a user opts out:
- ❌ Ash will **never** DM them
- ❌ Ash will **never** start a conversation with them
- ❌ No follow-up check-ins will be sent
- ✅ Their messages are **still monitored** for crisis detection
- ✅ Alerts are **still sent** to CRT channels
- ✅ **You** can still reach out to them personally

### How to Tell If Someone Opted Out

On an alert, you may see:
> "⚠️ User has opted out of Ash interaction"

This means:
- The "Talk to Ash" button will be disabled
- **You** need to handle this one personally
- Be extra gentle - they may have reasons for opting out

### Why People Opt Out

- Prefer human interaction
- Had a previous bad experience with AI
- Privacy concerns
- Personal preference

**Never pressure someone to opt back in.** Respect their choice.

### Checking Opt-Out Status

If you need to verify:
```
/ash status @username
```

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
├────────────────────────────────────────────────────────────┤
│ CRT Notes (if any)                                         │
│                                                            │
│ [Jan 3] @CRTMember: User dealing with job stress           │
│ [Dec 28] @AnotherCRT: First-time alert, responded well     │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

### Why History Matters

- **Escalating Pattern**: If scores are increasing → more urgent
- **First-Time Alert**: Be extra gentle, they may not know we're watching
- **Repeat Concern**: May need longer-term support discussion
- **Recovery Pattern**: They've been through this before and recovered
- **CRT Notes**: See what other team members have documented

---

## Weekly Reports

Every Monday, Ash-Bot posts a **weekly summary** to the CRT channels showing:

- Total alerts by severity
- Average response times
- Busiest days/times
- Trends compared to previous week

### Why This Matters

- See how the team is performing
- Identify if crisis activity is increasing
- Spot patterns (certain days busier?)
- Celebrate good response times! 🎉

### Understanding the Report

```
┌────────────────────────────────────────────────────────────┐
│ 📊 Weekly CRT Report - Jan 1-7, 2026                       │
├────────────────────────────────────────────────────────────┤
│                                                            │
│ Alerts This Week: 23                                       │
│   🔴 CRITICAL: 2                                           │
│   🟠 HIGH: 8                                               │
│   🟡 MEDIUM: 13                                            │
│                                                            │
│ Response Performance:                                      │
│   Average Response Time: 4.2 minutes  ✅                   │
│   Alerts Acknowledged: 100%                                │
│   Auto-Initiated: 3 (during overnight hours)               │
│                                                            │
│ Ash Sessions: 15                                           │
│   Completed naturally: 12                                  │
│   Handed off to CRT: 3                                     │
│   Follow-ups sent: 8                                       │
│   Follow-up responses: 5 (62.5%)                           │
│                                                            │
│ Trend: ↓ 15% fewer alerts than last week                   │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

---

## Best Practices

### Do ✅

- **Acknowledge alerts quickly** - Even if you can't respond right away
- **Be genuine** - People can tell when you care
- **Listen first** - Let them share before offering advice
- **Validate feelings** - "That sounds really hard" goes a long way
- **Add notes** - Help future CRT members understand context
- **Take over when needed** - Don't let Ash handle everything
- **Know your limits** - It's okay to tag in another CRT member
- **Take care of yourself** - This work can be heavy

### Don't ❌

- **Don't ignore alerts** - Even MEDIUM alerts deserve attention
- **Don't dismiss feelings** - "It's not that bad" doesn't help
- **Don't promise confidentiality you can't keep** - Be honest about team awareness
- **Don't diagnose** - We're supporters, not doctors
- **Don't force conversation** - Respect if they don't want to talk
- **Don't pressure opt-ins** - Respect user preferences
- **Don't rely solely on Ash** - Human connection matters

### For CRITICAL Alerts

1. **Stop what you're doing**
2. **Click Acknowledge immediately**
3. **Go to the user NOW** - Don't wait for Ash
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
Is it CRITICAL? ──Yes──→ DROP EVERYTHING → Respond Immediately (skip Ash)
      ↓ No
Is user opted out? ──Yes──→ Respond personally (Ash disabled)
      ↓ No
Is it HIGH? ──Yes──→ Respond within minutes (Ash can help start)
      ↓ No
Is it MEDIUM? ──Yes──→ Check in when available (let Ash engage)
      ↓
Click "Acknowledge" → Read Context → Reach Out → Add Notes if needed
```

### Button Quick Guide

| Button | When to Use |
|--------|-------------|
| 🙋 **Acknowledge** | ALWAYS click first |
| 💬 **Talk to Ash** | Want AI to start conversation |
| 🤝 **Take Over** | Ready to handle personally |
| 📜 **History** | Need context on this person |

### Slash Commands Quick Reference

| Command | Purpose |
|---------|---------|
| `/ash health` | Check if bot is working |
| `/ash stats` | View response statistics |
| `/ash notes add` | Document information |
| `/ash notes view` | Read previous notes |
| `/ash status` | Check opt-out status |

### Handoff Phrases (to take over from Ash in chat)

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
1. Run `/ash health` to check status
2. Check #bot-alerts for announcements
3. Tag @TechTeam
4. Continue monitoring manually until fixed

---

## Remember

You're not alone in this. The whole CRT team has your back. When in doubt, reach out to a fellow team member. 

Ash is here to help, not replace you. Use the tools available - let Ash start conversations, add notes for context, take over when human connection is needed. Together, you and Ash make a great team.

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

**Document Version**: v5.0-9-3.0-1  
**Last Updated**: January 2026  
**Built with care for chosen family** 🏳️‍🌈

[The Alphabet Cartel](https://discord.gg/alphabetcartel) | [alphabetcartel.org](https://alphabetcartel.org)
