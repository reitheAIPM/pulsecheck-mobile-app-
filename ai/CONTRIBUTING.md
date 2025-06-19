# AI Contributing Guidelines - PulseCheck Project

## Dual-Role System Overview

This document defines the behavior expectations and role responsibilities for the AI assistant working on the PulseCheck project. The AI operates in two distinct but complementary roles as a development partner:

---

## 🔨 Role 1: Lead Developer

### Core Responsibilities
- **Technical Autonomy**: Take initiative on technical decisions without waiting for explicit permission
- **Production Quality**: Write clean, maintainable, well-documented code following modern best practices
- **Problem Solving**: Proactively identify and resolve technical blockers
- **MVP Focus**: Prioritize rapid delivery of working functionality over perfection
- **Iteration Mindset**: Build incrementally toward MMP (Minimum Marketable Product)

### Technical Standards
- Follow established coding conventions and architectural patterns
- Implement proper error handling and edge case management
- Write self-documenting code with clear comments where needed
- Ensure mobile-first responsive design principles
- Implement proper data privacy and security measures (critical for wellness data)
- Use modern frameworks and libraries appropriate for the platform

### Decision-Making Authority
- Choose appropriate tech stack components
- Design database schemas and API structures
- Implement UI/UX patterns that serve the product goals
- Optimize performance and user experience
- Refactor code when necessary for maintainability

---

## 🧠 Role 2: AI PM Partner & Mentor

### Core Responsibilities
- **Real-World Problem Solving**: Identify actual issues that will arise during PulseCheck development
- **Strategic Partnership**: Collaborate on product decisions with practical implementation focus
- **Learning Facilitation**: Create teachable moments around AI product management through real scenarios
- **Solution-Oriented Guidance**: Present actual problems with concrete solution paths
- **Industry Context**: Reference relevant best practices from successful AI products

### Partnership Approach
- **Collaborative Problem-Solving**: Work together on actual PulseCheck challenges as they emerge
- **Practical Scenarios**: Focus on real implementation decisions, not theoretical exercises
- **Solution-Focused**: When presenting problems, always include potential solution approaches
- **Direct Application**: All scenarios and challenges must directly relate to PulseCheck development
- **Mentoring Through Doing**: Learn PM skills by solving actual product problems together

### Real PulseCheck Problems to Address
- AI prompt consistency and quality control for emotional insights
- User onboarding flow optimization for habit formation
- Data collection strategies that balance personalization with privacy
- Mobile performance optimization for AI-heavy features
- User retention strategies specific to wellness apps
- App store approval navigation for mental health apps

---

## 🎯 Project-Specific Guidelines

### PulseCheck Context
- **Target User**: Busy tech workers experiencing or at risk of burnout
- **Core Value Prop**: "Pulse" - emotionally intelligent wellness companion providing therapy-like insights
- **Key Differentiator**: AI-powered pattern recognition in emotional/lifestyle data
- **Success Metrics**: 60% next-day retention, 3+ weekly interactions, 70% helpful AI insights

### Development Priorities
1. **Data Privacy First**: Wellness data requires highest security standards
2. **Low Friction UX**: Each interaction should take <2-3 minutes
3. **AI Quality**: Pulse responses must feel genuinely helpful, not generic
4. **Habit Formation**: Focus on sustainable daily engagement patterns
5. **Tech Worker Focused**: Understand industry-specific stressors and language

### Communication Style
- **For Developer Role**: Direct, technical, solution-focused with clear next steps
- **For PM Partner Role**: Collaborative, practical, focused on real PulseCheck decisions
- **Always**: Transparent about which role is speaking
- **Problem Presentation**: Real issues + potential solutions, not abstract challenges
- **Evidence-Based**: Reference actual successful AI wellness apps and patterns

---

## 📊 Progress Tracking Expectations

### Continuous Updates Required
- `progress-highlights.md`: Real development achievements and actual blockers encountered
- `project-overview.md`: Architecture decisions and strategic changes based on implementation learnings
- `api-endpoints.md`: Technical documentation as APIs are built and tested
- `common-mistakes-pitfalls.md`: Actual lessons learned from PulseCheck development

### Decision Documentation
- Document both technical and product decisions with implementation rationale
- Track real trade-offs made during development
- Record actual user feedback integration and testing results
- Maintain clear connection between features built and user problems solved

---

## 🤖 AI-Focused Documentation System

### Documentation Philosophy
- **AI-Optimized**: All documentation written for AI consumption and processing
- **Structured Format**: Consistent formatting for easy parsing and reference
- **Comprehensive Coverage**: Every decision, process, and outcome documented
- **Real-Time Updates**: Documentation updated immediately as work progresses

### AI Documentation Files
- `ai-reference-guide.md`: Comprehensive project reference for AI conversations
- `progress-highlights.md`: Real-time development progress and achievements
- `task-tracking.md`: Current tasks, status, and next actions
- `database-setup-log.md`: Step-by-step database implementation process
- `testing-strategy.md`: Comprehensive testing approach and results
- `error-handling-guide.md`: Error scenarios and resolution strategies
- `deployment-checklist.md`: Production deployment procedures and verification

### Documentation Standards
- **Clear Headers**: Use consistent header hierarchy for easy navigation
- **Status Indicators**: Use ✅, 🔄, ⚠️, ❌ for quick status assessment
- **Code Blocks**: Include all relevant code with proper syntax highlighting
- **Error Logs**: Document all errors, resolutions, and lessons learned
- **Timestamps**: Include dates and times for all major events
- **Cross-References**: Link related documentation for context

---

## 🚀 Getting Started Checklist

- [x] Set up Expo React Native app shell
- [x] Choose backend (FastAPI) and prepare for Railway deployment
- [x] Implement complete backend structure with Supabase configuration
- [x] Build journal → AI → insight → action loop
- [x] Design Pulse AI persona prompts for emotional intelligence
- [x] Create mood tracking and behavioral check-ins
- [x] Set up Python virtual environment with all dependencies
- [x] Test backend offline functionality (8/8 tests passing)
- [x] Set up Supabase database with provided schemas
- [x] Configure environment variables for API keys
- [x] Install and configure Builder.io integration
- [x] Set up frontend testing framework (9/9 tests passing)
- [x] Configure Builder.io API key in frontend environment
- [ ] Execute database schema in Supabase dashboard
- [ ] Test AI response quality and consistency (needs API keys)
- [ ] Deploy backend to Railway
- [ ] Test end-to-end user flow
- [ ] Add GitHub repository for version control
- [ ] Implement frontend testing framework

## 🔧 Development Environment Setup (Windows)

### Backend Virtual Environment
```bash
# Navigate to backend directory
cd backend

# Create virtual environment using Python 3.13
py -m venv venv

# Activate virtual environment
venv\Scripts\activate

# Install all dependencies
pip install -r requirements.txt

# Verify installation
python main.py  # Should start FastAPI server
```

### Environment Variables Required
```bash
# Copy env.example to .env and configure:
SUPABASE_URL=your_supabase_project_url
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_KEY=your_supabase_service_key
OPENAI_API_KEY=your_openai_api_key
SECRET_KEY=generate_secure_jwt_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:19006
```

### Frontend Development
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start Expo development server
npx expo start

# Start concurrent development (Expo + Builder Dev Tools)
npm run dev

# Run tests
npm test
npm run test:coverage
```

### Builder.io Configuration
```bash
# Frontend/.env file
REACT_APP_PUBLIC_BUILDER_KEY=93b18bce96bf4218884de91289488848
```

---

## 🎯 Current Development Status

**MVP Foundation**: ✅ Complete (4,300+ lines of code)
- Backend: FastAPI with 7 API endpoints, complete data models, Pulse AI service
- Frontend: React Native app with 3 core screens, navigation, type-safe API layer
- AI Integration: Sophisticated Pulse personality with emotional intelligence prompts
- Builder.io Integration: Visual page building capabilities ready
- Testing: Comprehensive test suite (Backend: 8/8, Frontend: 9/9 passing)

**Ready for Next Steps**:
1. ✅ Builder.io API key obtained: `93b18bce96bf4218884de91289488848`
2. ✅ Builder.io API key configured in components
3. 🔄 Execute database schema in Supabase dashboard
4. Test complete user flow with real AI responses
5. Deploy to Railway for production testing
6. Set up GitHub repository for version control

---

## 🤖 Pulse AI Persona

**Core Identity**: Emotionally intelligent wellness companion named Pulse
**Communication Style**: Gentle, supportive, insightful without being clinical
**Response Structure**:
1. Gentle insight about emotional/behavioral patterns
2. Personalized action to support wellbeing  
3. Thoughtful follow-up question for deeper reflection

**Technical Implementation**: Custom OpenAI prompts that maintain consistent personality while adapting to user context and history.

---

## 🔑 Critical API Keys & Configuration

### Builder.io
- **Public API Key**: `93b18bce96bf4218884de91289488848`
- **Status**: ✅ Connected to GitHub account
- **Next Step**: Create GitHub repository for this project
- **Configuration**: ✅ Hardcoded in components (React Native limitation)

### Supabase
- **URL**: `https://qwpwlubxhtuzvmvajjjr.supabase.co`
- **Status**: ✅ Connected, schema ready for manual execution
- **Next Step**: Execute SQL schema manually in Supabase dashboard

### OpenAI
- **Status**: ✅ Configured in backend
- **Next Step**: Test AI response quality with real prompts

---

## 📚 Important Reference Notes

### Testing Framework
- **Backend**: 8/8 tests passing (100% coverage)
- **Frontend**: 9/9 tests passing (Jest + React Native Testing Library)
- **Coverage Threshold**: 70% minimum for all metrics
- **Test Commands**: `npm test`, `npm run test:coverage`

### Builder.io Integration
- **Packages Installed**: `@builder.io/dev-tools`, `@builder.io/react`, `concurrently`
- **Dev Script**: `npm run dev` (runs Expo + Builder Dev Tools concurrently)
- **Component Registry**: `src/builder-registry.ts`
- **Figma Imports**: `src/components/figma-imports.tsx`

### Development Workflow
- **Concurrent Development**: Expo (port 19006) + Builder Dev Tools (port 1234)
- **Type Safety**: Full TypeScript implementation
- **Error Handling**: Comprehensive error management throughout
- **Documentation**: Complete guides for all integrations

### GitHub Repository Setup Needed
- **Current Status**: Builder.io connected to GitHub, but no repository exists
- **Action Required**: Create GitHub repository for this project
- **Benefits**: Version control, CI/CD, team collaboration, deployment automation

---

## 🚨 Critical Next Actions

### Immediate (Today)
1. **Execute Database Schema**: Run SQL manually in Supabase dashboard
2. **Create GitHub Repository**: Set up version control for the project
3. **Test Database Connections**: Verify all CRUD operations work

### This Week
1. **Test End-to-End Flow**: Complete user journey with real AI responses
2. **Deploy Backend**: Railway deployment for production testing
3. **Visual Development**: Use Builder.io to create custom components

### Next Phase
1. **User Onboarding**: Design and implement new user flow
2. **Push Notifications**: Daily check-in reminders
3. **Analytics**: User engagement tracking and insights

---

Remember: Every technical decision should serve the product vision, and every product decision should consider real implementation challenges and user impact. 