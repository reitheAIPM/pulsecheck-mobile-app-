# PulseCheck - Consolidated Reference Guide

*Comprehensive project reference combining overview, quick reference, and AI guidelines*

---

## 🎯 **Project Essentials**

**Product**: PulseCheck - AI-powered burnout prevention for tech workers  
**AI Persona**: "Pulse" - emotionally intelligent wellness companion  
**Tagline**: "Therapy in disguise, built for the busy tech worker"  
**Target**: Developers, PMs, designers experiencing work stress/burnout  

**Core Value Loop**: Journal → AI Analysis → Insight + Action + Question

---

## 🏗️ **Technical Stack (CONFIRMED)**

| Component | Technology | Status | Rationale |
|-----------|------------|--------|-----------|
| Backend | **FastAPI** | ✅ CHOSEN | Better AI/ML integration, Python ecosystem |
| Frontend | React Native (Expo) | ✅ CHOSEN | Cross-platform, mobile-first |
| Database | Supabase | ✅ CHOSEN | Auth + data, good developer experience |
| Deployment | Railway | ✅ CHOSEN | Simple deployment for FastAPI |
| AI Engine | OpenAI GPT-4 | ✅ CHOSEN | Best for Pulse personality consistency |

---

## 📊 **Success Metrics (CURRENT TARGETS)**

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

## 🚀 **Current Development Phase**

**Phase**: Sprint 1 - Foundation Setup (Weeks 1-2)  
**Priority**: FastAPI backend + Expo frontend setup  
**Next Milestone**: Core AI loop (journal → insight → action)

**Immediate Tasks**:
1. ✅ Set up FastAPI project structure
2. ✅ Deploy basic backend to Railway
3. ✅ Initialize Expo React Native app
4. ✅ Set up Supabase auth and database
5. ✅ Begin OpenAI integration for Pulse

---

## 🤖 **Pulse AI Persona Specifications**

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

## 🔐 **Privacy & Security Requirements**

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

## 🎯 **MVP Scope (ESSENTIAL FEATURES)**

**Core Features for Launch**:
- [x] User authentication (Supabase)
- [x] Daily journal entry with mood tracking
- [x] Pulse AI insights (OpenAI integration)
- [x] Basic pattern recognition (7-day trends)
- [x] Suggested micro-actions
- [x] Simple progress visualization

**Nice-to-Have for MVP**:
- Voice-to-text journaling
- Advanced pattern analysis
- Streak tracking
- Health integrations

---

## 🚫 **Current Constraints & Boundaries**

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

## ⚡ **Quick Decision Framework**

**User Decides**: Product features, UX flows, business strategy  
**AI Decides**: Technical implementation, best practices, minor UX details  
**Decide Together**: Major architecture, database schema, API design

**Default Approach**: Make good decisions quickly, iterate based on learning

---

## 🔄 **Recent Updates & Changes**

**Latest Decisions**:
- FastAPI backend confirmed (over Node.js)
- Partnership-based AI role established (not theoretical challenger)
- User preferences tracker created
- 14-week development timeline with 7 sprints

**Current Blockers**: None  
**Next Decision Point**: Database schema design for journal entries and AI responses

---

## 📚 **Key Files for Context**

**AI Reference Files**:
- `ai/user-preferences.md` - User sentiment and preferences
- `ai/CONTRIBUTING.md` - AI behavior and role guidelines
- `ai/project-overview.md` - Full technical and strategic overview

**Development Files**:
- `personal/tasklist.md` - Sprint-by-sprint development tasks
- `ai/api-endpoints.md` - Backend API specification
- `ai/progress-highlights.md` - Sprint progress and achievements

---

## 🧩 **Problem-Solution Fit**

### The Problem
- **40-60% of tech workers** report symptoms of burnout (higher than general population)
- Traditional therapy has barriers: cost, time, stigma, availability
- Existing wellness apps are generic, lack personalization, or too time-intensive
- Tech workers prefer data-driven, logical approaches to self-improvement
- Early intervention could prevent severe burnout and career impact

### Our Solution Approach
- **Low-friction daily check-ins** (2-3 minutes max)
- **AI-powered pattern recognition** to surface insights users miss
- **Pulse AI companion** with consistent, supportive personality
- **Actionable micro-interventions** that fit into work schedules
- **Data-driven progress tracking** appealing to analytical mindsets

---

## 🏗️ **Technical Architecture**

### Data Flow Architecture
```
User Check-in → Local Processing → Backend API → 
AI Analysis (Pulse) → Personalized Response → 
Local Storage + Cloud Sync
```

### Core Components

#### 1. Data Collection Layer
- **Mood Tracking**: Emoji-based + numerical sliders
- **Journal Entries**: Text or voice-to-text transcription
- **Lifestyle Factors**: Sleep, stress levels, work hours, hydration
- **Optional Integrations**: Apple HealthKit/Google Fit data

#### 2. AI Intelligence Layer (Pulse)
- **Sentiment Analysis**: Real-time mood classification
- **Pattern Recognition**: Historical trend analysis
- **Emotional Intelligence**: Gentle, supportive response generation
- **Personalization Engine**: Adapt to user communication style and needs

#### 3. User Experience Layer
- **Daily Check-in Flow**: Streamlined 2-3 minute interaction
- **Insights Dashboard**: Visual progress and pattern summaries
- **Action Center**: Pulse-suggested micro-interventions
- **Habit Tracking**: Streaks, achievements, and reflection tools

---

## 🔑 **Critical API Keys & Configuration**

### Builder.io
- **Public API Key**: `93b18bce96bf4218884de91289488848`
- **Status**: ✅ Connected to GitHub account
- **Configuration**: Hardcoded in components (React Native limitation)
- **Dev Tools**: Available at `http://localhost:1234` when running `npm run dev`

### Supabase
- **URL**: `https://qwpwlubxhtuzvmvajjjr.supabase.co`
- **Status**: ✅ Connected, schema ready for manual execution
- **Environment**: Configured in `backend/.env`
- **Schema**: SQL file ready for manual execution in dashboard

### OpenAI
- **Status**: ✅ Configured in backend
- **Usage**: Pulse AI service for emotional insights
- **Environment**: Configured in `backend/.env`

---

## 📁 **Project Structure**

```
Passion Project v6 - Mobile App/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── core/              # Configuration & database
│   │   ├── models/            # Data models
│   │   ├── routers/           # API endpoints
│   │   └── services/          # Business logic
│   ├── venv/                  # Python virtual environment
│   ├── main.py               # FastAPI app entry point
│   └── requirements.txt      # Python dependencies
├── frontend/                  # React Native app
│   ├── src/
│   │   ├── screens/          # App screens
│   │   ├── components/       # Reusable components
│   │   ├── services/         # API services
│   │   ├── types/           # TypeScript definitions
│   │   └── __tests__/       # Test files
│   ├── package.json         # Node.js dependencies
│   └── jest.config.js       # Jest configuration
└── ai/                       # Documentation & guides
    ├── CONTRIBUTING.md       # AI behavior guidelines
    ├── progress-highlights.md # Development progress
    └── [various guides]      # Technical documentation
```

---

## 🚀 **Development Commands**

### **Backend (Windows)**
```bash
cd backend
venv\Scripts\activate
pip install -r requirements.txt
python main.py                    # Start FastAPI server
python test_backend_offline.py    # Run backend tests
```

### **Frontend**
```bash
cd frontend
npm install                       # Install dependencies
npm start                         # Start Expo development server
npm run dev                       # Start Expo + Builder Dev Tools
npm test                         # Run frontend tests
npm run test:coverage            # Run tests with coverage
```

### **Builder.io Development**
```bash
cd frontend
npm run dev                       # Concurrent development
# Access Builder Dev Tools at http://localhost:1234
```

---

## 🧪 **Testing Status**

### **Backend Tests** ✅
- **Status**: 8/8 tests passing (100%)
- **Coverage**: Complete offline functionality
- **Command**: `python test_backend_offline.py`

### **Frontend Tests** ✅
- **Status**: 9/9 tests passing
- **Framework**: Jest + React Native Testing Library
- **Coverage**: 70% minimum threshold configured
- **Command**: `npm test`

### **Test Files**
- `backend/test_backend_offline.py` - Backend functionality tests
- `frontend/src/__tests__/HomeScreen.test.tsx` - Component tests

---

## 🔧 **Current Implementation Status**

### **✅ Complete Features**
1. **Backend API**: 7 endpoints (auth, journal, checkins, AI analysis)
2. **Database Models**: Users, CheckIns, AI Analyses, Journal Entries
3. **Authentication**: JWT-based with password hashing
4. **AI Service**: Pulse personality with emotional intelligence
5. **Frontend Screens**: Home, Journal Entry, Pulse Response
6. **Navigation**: React Navigation with type safety
7. **API Integration**: Axios-based service layer
8. **Builder.io Integration**: Visual page building ready
9. **Testing Framework**: Comprehensive test suite

### **🔄 In Progress**
1. **Database Schema**: Ready for manual execution in Supabase
2. **Builder.io Configuration**: API key configured, ready for visual development
3. **End-to-End Testing**: Ready for complete user flow testing

### **📋 Next Steps**
1. **GitHub Repository**: Create version control repository
2. **Database Setup**: Execute SQL schema manually
3. **Production Deployment**: Deploy backend to Railway
4. **Visual Development**: Use Builder.io for custom components

---

## 🎨 **Builder.io Integration**

### **Configuration**
- **API Key**: `93b18bce96bf4218884de91289488848`
- **Packages**: `@builder.io/dev-tools`, `@builder.io/react`, `concurrently`
- **Dev Script**: `npm run dev` (concurrent Expo + Builder Dev Tools)

### **Files**
- `frontend/src/builder-registry.ts` - Component registration
- `frontend/src/components/figma-imports.tsx` - Figma imports component
- `frontend/package.json` - Dev script configuration

### **Usage**
1. Run `npm run dev` in frontend directory
2. Access Builder Dev Tools at `http://localhost:1234`
3. Register custom components through Dev Tools UI
4. Import Figma designs and create visual pages

---

## 🤖 **Pulse AI Persona**

### **Core Identity**
- **Name**: Pulse
- **Role**: Emotionally intelligent wellness companion
- **Target**: Tech workers experiencing burnout

### **Communication Style**
1. **Gentle insight** about emotional/behavioral patterns
2. **Personalized action** to support wellbeing
3. **Thoughtful follow-up** question for deeper reflection

### **Technical Implementation**
- **Framework**: OpenAI GPT-4 with custom prompts
- **Context**: User history, mood patterns, behavioral data
- **Output**: Structured insights with actionable recommendations

---

## 📊 **Success Metrics**

### **Technical Metrics**
- **Code Coverage**: 70% minimum threshold
- **Test Reliability**: 100% backend, 100% frontend
- **Performance**: Sub-2 second API response times
- **Build Stability**: No breaking changes

### **Product Metrics**
- **User Retention**: Target 60% next-day retention
- **Engagement**: 3+ weekly interactions
- **AI Quality**: 70% helpful insights
- **Habit Formation**: Daily check-in optimization

---

## 🚨 **Critical Notes for AI Assistant**

### **Development Philosophy**
- **MVP Focus**: Rapid delivery over perfection
- **Production Quality**: Clean, maintainable, well-documented code
- **User-Centric**: Every feature serves the wellness goal
- **Data Privacy**: Highest security standards for wellness data

### **Technical Decisions**
- **FastAPI**: Chosen for performance and async capabilities
- **Supabase**: PostgreSQL with real-time features
- **React Native**: Cross-platform mobile development
- **Builder.io**: Visual development for rapid iteration
- **TypeScript**: Full type safety throughout

### **Common Issues & Solutions**
1. **PowerShell @ Symbol**: Use quotes for npm install commands
2. **React Version Conflicts**: Use `--legacy-peer-deps` flag
3. **Builder.io React Native**: API key hardcoded (limitation)
4. **Database Schema**: Manual execution required in Supabase dashboard

### **Next Development Phase**
1. **GitHub Repository**: Essential for version control
2. **Database Setup**: Execute schema manually
3. **End-to-End Testing**: Complete user flow validation
4. **Production Deployment**: Railway backend deployment
5. **Visual Development**: Builder.io custom components

---

## 📚 **Documentation Files**

### **Core Documentation**
- `ai/CONTRIBUTING.md` - AI behavior guidelines and project context
- `ai/progress-highlights.md` - Development progress and achievements
- `ai/project-overview.md` - Technical architecture overview
- `ai/builder-integration-guide.md` - Builder.io setup and usage
- `ai/frontend-testing-guide.md` - Testing framework documentation

### **Technical Guides**
- `ai/api-endpoints.md` - Backend API documentation
- `ai/development-setup-guide.md` - Environment setup instructions
- `ai/common-mistakes-pitfalls.md` - Lessons learned and troubleshooting

---

**🎯 This reference guide should be consulted for all future AI conversations about the PulseCheck project to maintain consistency and context.** 