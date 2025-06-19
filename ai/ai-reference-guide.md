# AI Reference Guide - PulseCheck Project

## 🎯 **Project Overview**

**PulseCheck** is an AI-powered burnout prevention app targeting busy tech workers. The app provides emotionally intelligent wellness insights through a "Pulse" AI companion that analyzes journal entries and behavioral patterns.

### **Core Architecture**
- **Backend**: FastAPI + Supabase PostgreSQL + OpenAI GPT-4
- **Frontend**: React Native (Expo) + TypeScript + Builder.io
- **AI**: Custom Pulse personality with emotional intelligence prompts
- **Testing**: Jest + React Native Testing Library (Backend: 8/8, Frontend: 9/9 passing)

---

## 🔑 **Critical API Keys & Configuration**

### **Builder.io**
- **Public API Key**: `93b18bce96bf4218884de91289488848`
- **Status**: ✅ Connected to GitHub account
- **Configuration**: Hardcoded in components (React Native limitation)
- **Dev Tools**: Available at `http://localhost:1234` when running `npm run dev`

### **Supabase**
- **URL**: `https://qwpwlubxhtuzvmvajjjr.supabase.co`
- **Status**: ✅ Connected, schema ready for manual execution
- **Environment**: Configured in `backend/.env`
- **Schema**: SQL file ready for manual execution in dashboard

### **OpenAI**
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