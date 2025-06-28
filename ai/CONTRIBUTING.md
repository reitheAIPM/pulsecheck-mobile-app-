# Contributing to PulseCheck - AI-Only Development Environment

**Purpose**: Master directory and guidelines for **AI-ONLY** development and debugging  
**Last Updated**: June 27, 2025  
**Critical Reality**: ❌ **NOT PRODUCTION READY** - Failed initial beta launch with bugs

---

## 🚨 **CRITICAL: AI-ONLY DEVELOPMENT REALITY**

### **🤖 PRIMARY CONSTRAINT: CURSOR AI IS SOLE DEVELOPER**
**❗ ABSOLUTE REQUIREMENT**: All systems must be designed for **AI-only operation**

- **NO HUMAN DEBUGGING ASSISTANCE**: AI must diagnose and fix all issues independently
- **MAXIMUM AI EFFICIENCY**: All tools optimized for minimal tool calls
- **COMPLETE CONTEXT PROVISION**: Every debugging scenario must provide full context
- **ERROR RECOVERY**: AI must understand and fix errors without human interpretation
- **DOCUMENTATION**: All notes, tools, and guides written specifically for AI understanding

### **🎯 PRIMARY GOAL: AI AUTONOMOUS PROBLEM SOLVING**
```
When something fails → AI gets complete context → AI fixes issue → AI validates fix
```

### **⚡ SECONDARY GOAL: MINIMAL TOOL CALLS**
- **1-3 calls maximum** for issue diagnosis
- **Single file references** provide complete context
- **Parallel tool calls** when gathering information
- **Comprehensive endpoints** eliminate investigation loops

---

## 🚨 **CRITICAL: PRODUCTION READINESS REALITY CHECK**

### **❌ CURRENT STATUS: FAILED BETA LAUNCH**
- **Beta Testers**: 3-6 users experienced constant bugs
- **Launch Result**: Failed due to overlooked issues
- **User Experience**: Poor - bugs disrupted core functionality
- **Production Readiness**: ❌ **NOT READY** despite previous optimistic assessments

### **🎯 USER EXPERIENCE IS PRIMARY PRIORITY**
- **User experience supersedes all technical considerations**
- **Bug-free operation is mandatory before any launch**
- **Beta tester feedback must be addressed comprehensively**
- **Launch readiness requires thorough testing and validation**

### **📊 HONEST ASSESSMENT REQUIREMENTS**
- **NO SUGARCOATING**: Distinguish between "working" vs "tested"
- **REALISTIC CONFIDENCE LEVELS**: Based on actual user validation
- **COMPREHENSIVE TESTING**: End-to-end user flows must be validated
- **ERROR SCENARIOS**: All failure modes must be tested and handled
- **LAUNCH READINESS**: See `LAUNCH-READINESS-ASSESSMENT.md` for comprehensive criteria

---

## 🚨 **CRITICAL: ENVIRONMENT STRATEGY**

### **CURRENT: PRODUCTION-ONLY DEVELOPMENT**
**We are currently using PRODUCTION infrastructure for all development:**

- **Frontend**: Vercel deployment (spark-realm) - **LIVE PRODUCTION DATA**
- **Backend**: Railway deployment (FastAPI) - **LIVE PRODUCTION API**  
- **Database**: Supabase production instance - **LIVE USER DATA**
- **AI Services**: OpenAI production API - **LIVE PROCESSING & COSTS**
- **Environment**: Windows PowerShell - **PRODUCTION DEBUGGING ONLY**

### **FUTURE: DEVELOPMENT BRANCH STRATEGY**
**When we create development branches (NOT YET):**
- **GitHub**: dev branch → triggers Railway/Vercel dev deployments
- **Railway**: Separate dev environment with mock data
- **Vercel**: Separate dev preview with test configurations
- **Database**: Separate dev Supabase project or staging tables
- **Testing**: Mock data and local testing allowed

### **⚠️ UNTIL DEV BRANCHES: NO LOCAL/MOCK DATA**
- **NO localhost references** in any code
- **NO mock data** in any debugging tools
- **NO local development** environment setup
- **ALL debugging** uses production endpoints
- **ALL testing** affects live user experience

---

## 🚨 **PRODUCTION ENVIRONMENT OVERVIEW**

### **Current Architecture (PRODUCTION)**
PulseCheck operates in a **full production environment** with the following stack:

- **Frontend**: Vercel deployment (spark-realm) - **LIVE PRODUCTION**
- **Backend**: Railway deployment (FastAPI) - **LIVE PRODUCTION**  
- **Database**: Supabase production instance - **LIVE DATA**
- **AI Services**: OpenAI production API - **LIVE PROCESSING**
- **Authentication**: Supabase Auth with RLS security - **LIVE USERS**
- **File Storage**: Supabase Storage with user isolation - **LIVE FILES**
- **Real-time**: Supabase Realtime with user-scoped subscriptions - **LIVE UPDATES**

### **⚠️ CRITICAL: No Local Development**
- **NO localhost references** - everything uses production URLs
- **NO mock data** - all data comes from live Supabase production
- **NO development fallbacks** - ENVIRONMENT=production enforced
- **NO fake responses** - AI uses real OpenAI API or fallback notifications

---

## 🔧 **AI DEBUGGING SYSTEM FOR CLAUDE**

### **🎯 PURPOSE: EFFICIENT PRODUCTION DEBUGGING**
This system enables Claude to debug the live production platform with minimal tool calls and maximum insight.

### **📋 COMPLETE SYSTEM DOCUMENTATION**
**🔗 [AI-DEBUGGING-SYSTEM.md](AI-DEBUGGING-SYSTEM.md)** - **READ THIS FIRST FOR ALL DEBUGGING**

Our comprehensive debugging system includes:
- **Sentry Error Tracking**: Real-time error capture with AI context
- **Observability Middleware**: Request correlation and performance tracking  
- **OpenAI Observability**: AI-specific monitoring and cost tracking
- **Debug Endpoints**: Production-safe investigation routes
- **False Positive Prevention**: Clear warnings and empty data handling

### **🚨 FALSE POSITIVE PREVENTION**
Our debug system is designed to **prevent false positives** that could mislead AI debugging:

- **Production-Safe Data**: No mock data that could indicate false "healthy" status
- **Clear Warnings**: All endpoints explicitly warn when real data is unavailable  
- **Empty Result Identification**: Empty arrays are flagged as "not representative of system health"
- **Middleware Status**: Clear indicators when debug middleware isn't capturing real traffic

**⚠️ CRITICAL**: Always read [AI-DEBUGGING-SYSTEM.md](AI-DEBUGGING-SYSTEM.md) to understand the complete system structure before debugging.

---

## 🤖 **CLAUDE DEBUGGING PROTOCOL**

### **🚨 CRITICAL: PRODUCTION TECH STACK CONTEXT**
**❗ ALWAYS REMEMBER**: We are running **PRODUCTION INFRASTRUCTURE**:
- **Frontend**: Vercel deployment (spark-realm) - **NOT localhost**
- **Backend**: Railway deployment (FastAPI) - **NOT local development**  
- **Database**: Supabase production instance - **NOT local database**
- **AI Services**: OpenAI production API - **NOT mock responses**
- **Environment**: Windows PowerShell - **NOT Unix/Linux**

### **🚨 CRITICAL: PowerShell Compatibility Requirements**
**❗ ALWAYS Use curl.exe in PowerShell (NOT curl)**
```powershell
# ✅ CORRECT - Use curl.exe for PowerShell compatibility
curl.exe -s "https://pulsecheck-mobile-app-production.up.railway.app/api/v1/debug/summary"

# ❌ WRONG - Don't use curl (causes PowerShell issues)
curl -s "https://pulsecheck-mobile-app-production.up.railway.app/api/v1/debug/summary"
```

### **📋 CONFIRMED ENVIRONMENT VARIABLES STATUS**
**❗ CRITICAL FOR AI DEBUGGING**: All environment variables are properly configured!
- **Backend (Railway)**: OPENAI_API_KEY, SUPABASE_*, JWT_SECRET_KEY, etc. ✅ ALL SET
- **Frontend (Vercel)**: REACT_APP_*, VITE_*, etc. ✅ ALL SET
- **If you see "0 AI companions" or 500 errors, it's a CODE issue, NOT missing env vars**
- **Full list**: See [ai/RAILWAY_ENVIRONMENT_SETUP.md](RAILWAY_ENVIRONMENT_SETUP.md) for complete confirmed variable list

Why this matters:
- Don't waste time checking environment variables that are already configured
- Focus on code bugs, API connectivity, and service logic issues first
- All critical integrations (OpenAI, Supabase, JWT) have proper credentials

### **🎯 CRITICAL: AI PERSONA BEHAVIOR REQUIREMENTS**

**❗ ESSENTIAL UNDERSTANDING**: AI personas must behave like **caring friends commenting on social media posts**.

### **Core Behavior Pattern**
1. **Immediate Response**: Automatic AI response when journal entry is created
2. **Proactive Follow-ups**: Additional personas comment 5 minutes to 12 hours later based on patterns
3. **Collaborative Team Approach**: Multiple personas work together, complementing each other's insights
4. **Pattern Recognition**: Identify recurring themes and provide actionable advice
5. **Social Media Feel**: Multiple caring friends naturally checking in over time

### **Sophisticated Timing Logic**
- **Initial comments**: 5 minutes to 1 hour after journal entry
- **User engagement-based timing**: Immediate responses (1-2 mins) for actively engaging users
- **Bombardment prevention**: 30 minutes minimum between any responses
- **Daily limits**: 2-10 responses based on free/premium + AI interaction settings
- **Active user detection**: Only users with journal entries OR AI interactions in last 7 days

### **Collaborative Personas (No Expertise Areas)**
**Personas work as a team, not specialists:**
- **Pulse**: Emotionally intelligent wellness companion
- **Sage**: Big-picture thinking and strategic insights  
- **Spark**: Motivational energy and positive reinforcement
- **Anchor**: Grounding presence and practical support

**Key Principle**: Any persona can comment on any topic, but with their unique personality and perspective.

### **Quality Standards for AI Development**
- **Natural**: Feel like a caring friend, not a clinical bot
- **Specific**: Reference actual content from user's entries
- **Helpful**: Provide actionable insights, not generic responses
- **Timely**: Respond when the insight would be most valuable
- **Pattern-aware**: Recognize recurring themes across entries
- **Collaborative**: Build on other personas' responses when appropriate

### **Commenting Style Examples**

**Good Examples** (like caring friends on social media):
- "Hey, I've noticed you've been dealing with work stress this week. Have you tried taking short breaks between tasks?"
- "That's a really thoughtful reflection on your relationship. It sounds like you're growing and learning from this experience."
- "I love how you're being honest about feeling overwhelmed. That takes courage."

**Bad Examples** (avoid these):
- ❌ "I notice you mentioned work stress" (too robotic)
- ❌ "Based on your entry, you should..." (too clinical)
- ❌ "Here are 5 tips for stress management..." (too generic)

---

## **🚀 COMPREHENSIVE PROACTIVE AI SYSTEM IMPLEMENTATION**

### **System Architecture Overview**

#### **Core Services**
1. **ComprehensiveProactiveAIService** (`backend/app/services/comprehensive_proactive_ai_service.py`)
   - Sophisticated engagement logic with timing optimization
   - User activity tracking and pattern recognition
   - Bombardment prevention and daily limits
   - Collaborative persona coordination

2. **AdvancedSchedulerService** (`backend/app/services/advanced_scheduler_service.py`)
   - Background task orchestration with APScheduler
   - Multiple timing cycles for different user types
   - Performance monitoring and analytics
   - Error handling and recovery

3. **Advanced Scheduler Router** (`backend/app/routers/advanced_scheduler.py`)
   - API endpoints for scheduler control and monitoring
   - Real-time status and performance analytics
   - Manual cycle triggers for debugging
   - Health monitoring and configuration management

#### **Key Features Implemented**

**🎯 Sophisticated Timing Logic:**
- Initial comments: 5 minutes to 1 hour (vs previous 2-12 hours)
- User engagement-based timing for active users
- Bombardment prevention with 30-minute minimums
- Daily limits based on user tier and AI interaction settings

**🤝 Collaborative Personas:**
- Team-based approach instead of expertise areas
- Natural, human-like language (removed robotic style)
- Pattern recognition across related journal entries
- Complementary responses building on each other

**👥 Advanced User Engagement Tracking:**
- Active users: Journal entries OR AI interactions in last 7 days
- Engagement detection: Reactions, replies, app usage
- Success metrics: Daily/weekly journaling + AI interactions
- User tiers and AI interaction levels

**🔧 Comprehensive Scheduler System:**
- Main cycle: Every 5 minutes for all active users
- Immediate cycle: Every 1 minute for high-engagement users
- Analytics cycle: Every 15 minutes for performance monitoring
- Daily cleanup: Automated maintenance at 2 AM

**📊 Real-Time Analytics & Monitoring:**
- Performance metrics and trend analysis
- A/B testing framework for optimization
- Error tracking and recovery
- Manual cycle triggers for debugging

### **API Endpoints**

#### **Scheduler Management**
- `POST /api/v1/scheduler/start` - Start the advanced scheduler
- `POST /api/v1/scheduler/stop` - Stop the scheduler
- `GET /api/v1/scheduler/status` - Real-time status and metrics
- `GET /api/v1/scheduler/health` - Health monitoring
- `GET /api/v1/scheduler/analytics` - Performance analytics
- `POST /api/v1/scheduler/manual-cycle` - Manual cycle triggers
- `GET /api/v1/scheduler/config` - Configuration settings
- `POST /api/v1/scheduler/config/update` - Update configuration

#### **Proactive AI Engagement**
- `GET /api/v1/proactive-ai/opportunities` - Check engagement opportunities
- `POST /api/v1/proactive-ai/engage` - Trigger proactive engagement
- `GET /api/v1/proactive-ai/history` - View engagement history
- `GET /api/v1/proactive-ai/stats` - Engagement statistics

### **Development Guidelines**

#### **Adding New Personas**
1. Update persona definitions in `ComprehensiveProactiveAIService`
2. Add persona selection logic in `_select_optimal_persona_for_entry`
3. Update timing configurations if needed
4. Test with manual cycle triggers

#### **Modifying Timing Logic**
1. Update `timing_configs` in `ComprehensiveProactiveAIService`
2. Adjust `daily_limits` for different user tiers
3. Modify `_calculate_initial_delay` for timing variations
4. Test with different user engagement profiles

#### **Enhancing Pattern Recognition**
1. Add new topic keywords in `topic_keywords`
2. Update `_find_related_entries` logic
3. Enhance `_classify_entry_topics` classification
4. Test pattern detection with sample data

#### **Performance Optimization**
1. Monitor scheduler metrics via `/api/v1/scheduler/analytics`
2. Adjust cycle intervals based on user load
3. Optimize database queries in engagement services
4. Use manual cycle triggers for testing

### **Testing and Debugging**

#### **Manual Testing**
```bash
# Test scheduler endpoints
curl -X POST https://your-app.railway.app/api/v1/scheduler/start
curl -X GET https://your-app.railway.app/api/v1/scheduler/status
curl -X POST https://your-app.railway.app/api/v1/scheduler/manual-cycle?cycle_type=main
```

#### **PowerShell Testing Scripts**
- `test_scheduler_final.ps1` - Basic scheduler functionality
- `test_comprehensive_proactive_ai.ps1` - Full system testing
- `test_simple_scheduler.ps1` - Quick health checks

#### **Monitoring and Debugging**
1. Check scheduler status via `/api/v1/scheduler/status`
2. Monitor health via `/api/v1/scheduler/health`
3. View analytics via `/api/v1/scheduler/analytics`
4. Use manual cycle triggers for debugging

### **Deployment Considerations**

#### **Railway Deployment**
- **Auto-start**: Scheduler starts automatically in production
- **Resource limits**: Designed for 100+ users efficiently
- **Error recovery**: Automatic restart and monitoring
- **Performance**: Real-time analytics and optimization

#### **Environment Variables**
- `ENVIRONMENT=production` - Enables auto-start
- `AUTO_START_SCHEDULER=true` - Controls auto-start behavior
- `SUPABASE_URL` and `SUPABASE_ANON_KEY` - Database configuration

#### **Dependencies**
- `APScheduler==3.10.4` - Background task scheduling
- `FastAPI` - API framework
- `Supabase` - Database integration

### **Quality Assurance**

#### **Code Standards**
- Follow existing code patterns and naming conventions
- Add comprehensive error handling and logging
- Include docstrings for all public methods
- Test with manual cycle triggers before deployment

#### **Performance Standards**
- Scheduler cycles should complete within 30 seconds
- Database queries should be optimized for user load
- Error rates should remain below 5%
- Response times should be under 2 seconds

#### **User Experience Standards**
- AI responses should feel natural and conversational
- Timing should respect user preferences and limits
- Pattern recognition should be accurate and helpful
- Collaborative responses should complement each other

### **Future Development Roadmap**

#### **Phase 1: Core System (✅ COMPLETED)**
- ✅ Advanced scheduler with multiple cycles
- ✅ Comprehensive proactive AI service
- ✅ Collaborative personas without expertise areas
- ✅ Sophisticated timing logic
- ✅ User engagement tracking

#### **Phase 2: Enhancement (🔄 PLANNED)**
- 🔄 A/B testing framework for engagement optimization
- 🔄 Machine learning for timing and content optimization
- 🔄 Advanced personalization based on user preferences
- 🔄 Integration with external wellness apps

#### **Phase 3: Advanced Features (📋 FUTURE)**
- 📋 Real-time user behavior analysis
- 📋 Predictive engagement modeling
- 📋 Multi-language support
- 📋 Advanced analytics dashboard

---

**This comprehensive proactive AI system transforms the app from simple reactive responses to a sophisticated "AI friends checking in" experience that adapts to user behavior and creates genuine, ongoing engagement.**

---

## 🗄️ **SUPABASE DATABASE MIGRATIONS**

### **Supabase CLI Setup and Migration Process**

Our project uses Supabase CLI for database schema management. Here's the complete process:

**✅ CLI Available:** `npx supabase --version` (version 2.26.9 confirmed)

### **🔧 MIGRATION WORKFLOW**

#### **1. Check Project Status**
```powershell
# List available projects
npx supabase projects list

# Check current link status
npx supabase status
```

#### **2. Link to Remote Project**
```powershell
# Link to production project (use your actual project-ref)
npx supabase link --project-ref qwpwlubxhtuzvmvajjjr --password "YOUR_DB_PASSWORD"
```

#### **3. Check Migration Status**
```powershell
# See which migrations are applied locally vs remotely
npx supabase migration list
```

#### **4. Apply Migrations**
```powershell
# Push all pending migrations (preferred)
npx supabase db push --include-all

# Push specific migration
npx supabase db push

# Dry run to preview changes
npx supabase db push --dry-run
```

### **🚨 COMMON MIGRATION ISSUES & SOLUTIONS**

#### **Issue: "Found local migration files to be inserted before the last migration"**
**Solution:** Use `--include-all` flag
```powershell
npx supabase db push --include-all
```

#### **Issue: "functions in index predicate must be marked IMMUTABLE"**
**Cause:** PostgreSQL doesn't allow volatile functions like `NOW()`, `CURRENT_TIMESTAMP` in index predicates  
**Example Error:**
```
ERROR: functions in index predicate must be marked IMMUTABLE (SQLSTATE 42P17)
At statement: CREATE INDEX WHERE created_at > (NOW() - INTERVAL '90 days')
```

**Solutions:**
```sql
-- ❌ WRONG - Volatile function in WHERE clause
CREATE INDEX idx_recent_entries ON journal_entries(user_id, created_at DESC) 
WHERE created_at > (NOW() - INTERVAL '90 days');

-- ✅ CORRECT - Remove WHERE clause with volatile function
CREATE INDEX idx_recent_entries ON journal_entries(user_id, created_at DESC);

-- ✅ ALTERNATIVE - Use static timestamp (but requires updates)
CREATE INDEX idx_recent_entries ON journal_entries(user_id, created_at DESC) 
WHERE created_at > '2024-01-01'::timestamp;

-- ✅ BEST - Create partial index with IMMUTABLE function
CREATE INDEX idx_recent_entries ON journal_entries(user_id, created_at DESC) 
WHERE created_at > (CURRENT_DATE - INTERVAL '90 days');
```

**Real-world Fix Example:**
In our `20250127000002_optimize_rls_performance.sql`, we had to change:
```sql
-- Before (failed)
CREATE INDEX WHERE created_at > (NOW() - INTERVAL '90 days')

-- After (success)  
CREATE INDEX ON journal_entries(user_id, created_at DESC);
```

#### **Issue: "migration history does not match local files"**
**Solution:** Repair migration status
```powershell
npx supabase migration repair --status applied MIGRATION_ID
```

#### **Issue: "permission denied for table"**
**Cause:** Tables created via Dashboard owned by `supabase_admin`, not `postgres`
**Solution:** Reassign ownership
```sql
ALTER TABLE table_name OWNER TO postgres;
```

### **🔍 MIGRATION DEBUGGING WORKFLOW**

When migrations fail, follow this systematic approach:

#### **1. Identify the Problem**
```powershell
# Check what migrations are pending
npx supabase migration list

# Dry run to see what would be applied
npx supabase db push --dry-run

# Check for specific errors
npx supabase db push --include-all --debug
```

#### **2. Analyze Error Messages**
- **SQLSTATE 42P17**: IMMUTABLE function error → Fix volatile functions in indexes
- **SQLSTATE 42501**: Permission denied → Check table ownership  
- **SQLSTATE 42P01**: Relation does not exist → Missing dependencies
- **Migration ordering**: Files inserted before last migration → Use `--include-all`

#### **3. Fix and Retry**
```powershell
# After fixing migration files
git add supabase/migrations/
git commit -m "FIX: [specific issue description]"
npx supabase db push --include-all
```

#### **4. Verify Success**
```powershell
# Confirm migrations applied
npx supabase migration list

# Test database functionality  
curl.exe -s "https://pulsecheck-mobile-app-production.up.railway.app/api/v1/database/comprehensive-status"
```

### **📋 MANUAL MIGRATION (Supabase Dashboard)**

When CLI migration fails, use Supabase Dashboard:

1. Go to [Supabase Dashboard](https://supabase.com/dashboard)
2. Select your project  
3. Navigate to **SQL Editor**
4. Create new query
5. Paste migration SQL
6. Click **Run**

### **🎯 ESSENTIAL PROFILES TABLE MIGRATION**

**Issue:** Missing `profiles` table causes database queries to fail  
**Error:** `relation "public.profiles" does not exist`

**Quick Fix SQL (run in Supabase Dashboard):**
```sql
-- Create a table for public profiles
CREATE TABLE IF NOT EXISTS public.profiles (
  id uuid references auth.users not null primary key,
  created_at timestamp with time zone DEFAULT NOW(),
  updated_at timestamp with time zone DEFAULT NOW(),
  email text,
  full_name text,
  avatar_url text,
  username text unique,
  
  -- PulseCheck specific fields
  wellness_score integer DEFAULT 50 CHECK (wellness_score >= 0 AND wellness_score <= 100),
  streak_days integer DEFAULT 0,
  total_entries integer DEFAULT 0,
  last_checkin timestamp with time zone,
  ai_persona_preference text DEFAULT 'balanced',
  notification_preferences jsonb DEFAULT '{"daily_reminder": true, "weekly_summary": true}',
  
  constraint username_length check (char_length(username) >= 3)
);

-- Set up Row Level Security (RLS)
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;

-- RLS Policies for profiles
CREATE POLICY "Public profiles are viewable by everyone" ON public.profiles
  FOR SELECT USING (true);

CREATE POLICY "Users can insert their own profile" ON public.profiles
  FOR INSERT WITH CHECK (auth.uid() = id);

CREATE POLICY "Users can update their own profile" ON public.profiles
  FOR UPDATE USING (auth.uid() = id);

-- Trigger to automatically create profile when user signs up
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS trigger AS $$
BEGIN
  INSERT INTO public.profiles (id, email, full_name, avatar_url)
  VALUES (
    NEW.id, 
    NEW.email,
    NEW.raw_user_meta_data->>'full_name', 
    NEW.raw_user_meta_data->>'avatar_url'
  );
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Drop trigger if exists and recreate
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- Create updated_at trigger
CREATE OR REPLACE FUNCTION public.handle_updated_at()
RETURNS trigger AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER profiles_updated_at
  BEFORE UPDATE ON public.profiles
  FOR EACH ROW EXECUTE FUNCTION public.handle_updated_at();
```

### **✅ VERIFY MIGRATION SUCCESS**

After applying the profiles table migration:

```powershell
# Test database connectivity
curl.exe -s "https://pulsecheck-mobile-app-production.up.railway.app/api/v1/database/comprehensive-status"
```

**Expected Result:**
```json
"database_query": "✅ SUCCESS"
"overall_status": "✅ HEALTHY"
```

### **🔧 ENHANCED DEBUGGING ENDPOINTS**

Our system now includes specialized migration and deployment validation:

#### **Migration Validation (Proactive)**
```powershell
# Validate migration files before deployment
curl.exe -s "https://pulsecheck-mobile-app-production.up.railway.app/api/v1/database/migration-validation"
```

**What it catches:**
- ✅ PostgreSQL IMMUTABLE function violations (SQLSTATE 42P17)
- ✅ Missing RLS policies on new tables
- ✅ Syntax errors and missing semicolons
- ✅ Volatile functions in index predicates

**Example Output:**
```json
{
  "overall_status": "❌ ISSUES_FOUND",
  "issues_found": [
    {
      "type": "IMMUTABLE_VIOLATION",
      "issue": "NOW() function used in index predicate", 
      "sqlstate": "42P17",
      "fix": "Remove WHERE clause or use CURRENT_DATE instead of NOW()"
    }
  ],
  "recommendations": [
    {
      "priority": "HIGH",
      "action": "Fix IMMUTABLE function violations before deployment"
    }
  ]
}
```

#### **Deployment Readiness Check**
```powershell
# Comprehensive pre-deployment validation
curl.exe -s "https://pulsecheck-mobile-app-production.up.railway.app/api/v1/database/deployment-readiness"
```

**What it validates:**
- ✅ Migration file analysis
- ✅ Environment variables
- ✅ Database connectivity
- ✅ Schema integrity

**Example Output:**
```json
{
  "overall_status": "✅ DEPLOYMENT_READY",
  "risk_level": "LOW", 
  "deployment_confidence": "100.0%",
  "checks_passed": 3,
  "checks_total": 3
}
```

#### **Monitoring Integration**

Our enhanced monitoring system now captures:

- **Migration Errors**: SQLSTATE codes, specific SQL statements, fix suggestions
- **Deployment Failures**: Stage-specific context, environment details
- **Schema Validation**: Proactive warnings before deployment

**Sentry Error Categories:**
- `MIGRATION`: Database migration failures
- `SCHEMA_VALIDATION`: Schema validation warnings  
- `DEPLOYMENT`: Deployment-related errors
- `MIGRATION_BLOCKING`: Critical errors that prevent deployment