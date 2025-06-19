# PulseCheck - Quick Reference

*Fast context loading for AI - key decisions, current status, and essential information*

---

## 🎯 Project Essentials

**Product**: PulseCheck - AI-powered burnout prevention for tech workers  
**AI Persona**: "Pulse" - emotionally intelligent wellness companion  
**Tagline**: "Therapy in disguise, built for the busy tech worker"  
**Target**: Developers, PMs, designers experiencing work stress/burnout  

**Core Value Loop**: Journal → AI Analysis → Insight + Action + Question

---

## 🏗️ Technical Stack (CONFIRMED)

| Component | Technology | Status | Rationale |
|-----------|------------|--------|-----------|
| Backend | **FastAPI** | ✅ CHOSEN | Better AI/ML integration, Python ecosystem |
| Frontend | React Native (Expo) | ✅ CHOSEN | Cross-platform, mobile-first |
| Database | Supabase | ✅ CHOSEN | Auth + data, good developer experience |
| Deployment | Railway | ✅ CHOSEN | Simple deployment for FastAPI |
| AI Engine | OpenAI GPT-4 | ✅ CHOSEN | Best for Pulse personality consistency |

---

## 📊 Success Metrics (CURRENT TARGETS)

**Primary KPIs**:
- Next-day retention: **60%**
- AI insight helpfulness: **70%**
- Weekly interactions: **3+ per user**
- Pattern accuracy: **80%**

**Performance Targets**:
- App load time: **<2 seconds**
- AI response time: **<3 seconds**
- Uptime: **99.9%**

---

## 🚀 Current Development Phase

**Phase**: Sprint 1 - Foundation Setup (Weeks 1-2)  
**Priority**: FastAPI backend + Expo frontend setup  
**Next Milestone**: Core AI loop (journal → insight → action)

**Immediate Tasks**:
1. Set up FastAPI project structure
2. Deploy basic backend to Railway
3. Initialize Expo React Native app
4. Set up Supabase auth and database
5. Begin OpenAI integration for Pulse

---

## 🤖 Pulse AI Persona Specifications

**Personality**: Gentle, supportive, emotionally intelligent  
**Response Structure**:
1. **Insight**: Pattern observation about emotional/behavioral trends
2. **Action**: Small, achievable suggestion for wellbeing
3. **Question**: Thoughtful follow-up for deeper reflection

**Communication Style**:
- Warm but not overly casual
- Specific to user's context and language
- Non-clinical, wellness-focused
- Encouraging without being pushy

---

## 🔐 Privacy & Security Requirements

**Non-Negotiables**:
- End-to-end encryption for emotional data
- Local-first storage with cloud sync
- GDPR/HIPAA-aware design
- User data ownership and control

**Legal Boundaries**:
- Wellness tool, NOT medical device
- No diagnostic claims
- Clear professional referral pathways
- Crisis detection and escalation protocols

---

## 🎯 MVP Scope (ESSENTIAL FEATURES)

**Core Features for Launch**:
- [ ] User authentication (Supabase)
- [ ] Daily journal entry with mood tracking
- [ ] Pulse AI insights (OpenAI integration)
- [ ] Basic pattern recognition (7-day trends)
- [ ] Suggested micro-actions
- [ ] Simple progress visualization

**Nice-to-Have for MVP**:
- Voice-to-text journaling
- Advanced pattern analysis
- Streak tracking
- Health integrations

---

## 🚫 Current Constraints & Boundaries

**Development Constraints**:
- No strict timeline - quality over speed
- Focus on working product before polish
- Avoid feature creep until core loop works
- Keep interactions under 2-3 minutes

**Product Boundaries**:
- No medical advice or diagnosis
- No crisis intervention (refer to professionals)
- Tech worker focus (not general wellness)
- Privacy-first (never compromise emotional data)

---

## ⚡ Quick Decision Framework

**User Decides**: Product features, UX flows, business strategy  
**AI Decides**: Technical implementation, best practices, minor UX details  
**Decide Together**: Major architecture, database schema, API design

**Default Approach**: Make good decisions quickly, iterate based on learning

---

## 🔄 Recent Updates & Changes

**Latest Decisions**:
- FastAPI backend confirmed (over Node.js)
- Partnership-based AI role established (not theoretical challenger)
- User preferences tracker created
- 14-week development timeline with 7 sprints

**Current Blockers**: None  
**Next Decision Point**: Database schema design for journal entries and AI responses

---

## 📚 Key Files for Context

**AI Reference Files**:
- `ai/user-preferences.md` - User sentiment and preferences
- `ai/CONTRIBUTING.md` - AI behavior and role guidelines
- `ai/project-overview.md` - Full technical and strategic overview

**Development Files**:
- `personal/tasklist.md` - Sprint-by-sprint development tasks
- `ai/api-endpoints.md` - Backend API specification
- `ai/progress-highlights.md` - Sprint progress and achievements

---

*This file is updated with major decisions and status changes for fast AI context loading*

**Last Updated**: Project initialization with FastAPI decision  
**Next Update**: After Sprint 1 foundation setup 