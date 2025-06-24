# AI Master Context - PulseCheck Project

**Purpose**: Primary reference for AI development - consolidated core project information  
**Last Updated**: January 27, 2025  
**Status**: ✅ **PRODUCTION READY** - All core systems operational

---

## 🎯 **PROJECT ESSENTIALS**

### **What PulseCheck Is**
- **Product**: AI-powered wellness journaling app with interactive calendar history
- **Core Innovation**: Calendar-based mood visualization + 4 distinct AI personas + dynamic personalization
- **Target Market**: All wellness-seeking individuals (expanded from tech workers only)
- **Unique Value**: "Therapy in disguise" with smart AI that learns and adapts

### **Current Status: PRODUCTION READY**
**✅ OPERATIONAL**: All core systems functioning correctly
- Users can save journal entries successfully
- AI features fully operational with 4-persona system
- Backend service running with all routers mounted
- **Recent Achievement**: Complete crisis resolution and system stabilization

### **Technical Stack**
- **Backend**: FastAPI + Supabase + Railway deployment
- **Frontend**: React (converting to React Native for iOS)
- **AI**: OpenAI GPT-4 with 4-persona system
- **Database**: PostgreSQL with comprehensive schemas

---

## 🧠 **AI SYSTEM ARCHITECTURE**

### **4-Persona System (Core Feature)**
1. **Pulse** (Free): Emotionally intelligent wellness companion
2. **Sage** (Premium): Wise mentor for strategic guidance  
3. **Spark** (Premium): Energetic motivator for action
4. **Anchor** (Premium): Steady presence for stability

### **AI Features**
- **Dynamic Persona Selection**: AI chooses persona based on content analysis
- **Topic Classification**: Real-time journal theme detection
- **Pattern Recognition**: User behavior analysis and adaptation
- **Smart Nudging**: Contextual re-engagement prompts
- **Cost Optimization**: Usage limits and fallback strategies

### **AI Configuration Notes**
- **OpenAI Status**: Intentionally disabled during MVP (billing setup)
- **Fallback Behavior**: All AI endpoints must return default responses, never error
- **Cost Control**: Free tier (5/day), Premium tier (50/day), Beta tier (20/day)

---

## 📊 **CRITICAL API ENDPOINTS**

### **Core API Endpoints (All Operational)**
```bash
GET  /health                              # Backend health - ✅ WORKING
GET  /api/v1/journal/test                 # Router health - ✅ WORKING  
POST /api/v1/journal/entries              # Journal creation - ✅ WORKING
POST /api/v1/journal/ai/topic-classification  # AI features - ✅ WORKING
GET  /api/v1/journal/entries              # Journal retrieval - ✅ WORKING
```

### **AI Endpoints (When Working)**
```bash
GET    /api/v1/adaptive-ai/personas       # Get available personas
POST   /api/v1/adaptive-ai/generate-response  # Generate adaptive response
POST   /api/v1/adaptive-ai/analyze-patterns   # Analyze user patterns
```

---

## 🔧 **DEVELOPMENT CONTEXT**

### **Environment Variables**
```
SUPABASE_URL=https://qwpwlubxhtuzvmvajjjr.supabase.co
OPENAI_API_KEY=[intentionally not set - disabled for MVP]
Railway Production: https://pulsecheck-mobile-app-production.up.railway.app
```

### **Database Schema Key Tables**
- **users**: Authentication, subscription status, focus areas
- **journal_entries**: Content, mood metrics, tags, topic flags
- **ai_responses**: Insights, actions, questions, persona used
- **user_patterns**: Writing style, topics, preferences

### **Common Mistakes to Avoid**
- Don't reference deleted schema files (only use `FINAL_FIX_FOR_EXISTING_DB.sql`)
- Health checks should validate schema AND endpoints, not just service status
- Always handle OpenAI disabled state gracefully (log warning, not error)
- Router mounting failures often caused by circular dependencies

---

## 🎯 **STRATEGIC DIRECTION**

### **Market Expansion (5x Growth)**
- **Old Target**: Tech workers with burnout (10M users)
- **New Target**: All wellness-seeking individuals (50M+ users)
- **Key Strategy**: Multi-theme journaling + universal approach

### **Revenue Model**
- **Free Tier**: Basic journaling + Pulse persona (5 AI interactions/day)
- **Premium Tier**: All personas + advanced features ($9.99/month)
- **Break-even**: 13 premium users needed

### **Next Milestones**
1. **IMMEDIATE**: Fix journal router 404 crisis
2. **Week 1**: Implement AI personalization engine
3. **Week 2-3**: Convert to React Native for iOS TestFlight
4. **Month 1**: Launch iOS beta with 10-20 users

---

## 🚨 **CURRENT CRISIS DETAILS**

### **Root Cause Analysis**
**Most Likely Issue**: Router mounting failure due to authentication dependencies

**Evidence**:
- ✅ Backend service healthy (health endpoint works)
- ❌ ALL journal endpoints 404 (router-level failure)
- ✅ Code exists and looks correct
- ❌ Deployment successful but endpoints still broken

### **Investigation Needed**
1. **Railway Logs**: Check for import/dependency errors during startup
2. **Router Registration**: Verify journal router properly mounted in main.py
3. **Authentication Dependencies**: Test if `get_current_user` imports cause circular dependencies
4. **Environment Variables**: Confirm all required services available

### **Quick Fix Strategy**
1. Create minimal journal router without complex dependencies
2. Test basic endpoint restoration
3. Gradually add back authentication and features
4. Full dependency analysis and resolution

---

## 📋 **AI DEVELOPMENT GUIDELINES**

### **For Crisis Resolution**
- Focus on systematic debugging (health → routers → dependencies)
- Always test fixes with actual endpoint calls
- Check Railway logs for import/startup errors
- Implement fallback patterns for critical failures

### **For Feature Development**
- Multi-theme journaling approach (universal prompt)
- Dynamic persona selection based on content analysis
- Pattern recognition for user adaptation
- Cost-conscious AI usage with limits and fallbacks

### **Code Quality Standards**
- TypeScript strict mode for frontend
- FastAPI async patterns for backend
- Comprehensive error handling with AI debugging context
- Mobile-first responsive design

---

## 🔍 **QUICK REFERENCE COMMANDS**

### **Testing Endpoints**
```bash
# Test health
curl https://pulsecheck-mobile-app-production.up.railway.app/health

# Test journal (currently broken)
curl https://pulsecheck-mobile-app-production.up.railway.app/api/v1/journal/test
```

### **Development Commands**
```bash
# Backend
cd backend && uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Frontend  
cd spark-realm && npm run dev

# Testing
cd backend && python test_deployment.py
```

### **Crisis Recovery Commands**
```bash
# Check Railway logs
railway logs --tail 100

# Validate imports
cd backend && python -c "from app.routers import journal; print('Success')"

# Test database connection
cd backend && python -c "from app.core.database import get_database; print('DB OK')"
```

---

**This file consolidates: ai-alignment-guide.md, project-overview.md, PROJECT_SUMMARY_FOR_CHATGPT.md, quick-reference.md** 