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

**❗ ESSENTIAL UNDERSTANDING**: AI personas must behave like **expert friends commenting on social media posts**.

#### **Core Behavior Pattern**
1. **Immediate Response**: Automatic AI response when journal entry is created
2. **Proactive Follow-ups**: Additional personas comment 2-12 hours later based on patterns
3. **Expert-Level Insights**: Like professionals commenting on Twitter with valuable tips
4. **Pattern Recognition**: Identify recurring themes and provide actionable advice
5. **Social Media Feel**: Multiple caring experts naturally checking in over time

#### **Quality Standards for AI Development**
- **Specific**: Reference actual content from user's entries
- **Helpful**: Provide actionable tips or insights, not generic responses  
- **Natural**: Feel like a caring friend, not a clinical bot
- **Timely**: Respond when the insight would be most valuable
- **Pattern-Aware**: Connect current entry to user's history and trends

#### **Implementation Requirements**
- **Proactive AI Service**: Must analyze recent entries for engagement opportunities
- **Smart Timing**: Delays of 2-12 hours to feel natural, not immediate
- **Persona Selection**: Different personas respond based on content (stress → Anchor, low mood → Spark)
- **Pattern Detection**: System must identify recurring themes across multiple entries
- **Multiple Perspectives**: Users should get responses from different personas over time

**Reference**: See [USER-INSIGHTS.md](USER-INSIGHTS.md) for complete AI persona behavioral philosophy and examples.

### **⚠️ CRITICAL: PowerShell Command Limitations**
**❗ MAJOR CONSTRAINT: Long commands cause terminal hangs/crashes**

**FAILED COMMANDS - DO NOT USE:**
- **Long commands (>500 characters)**: Cause PowerShell to freeze indefinitely
- **Complex inline JSON**: Multi-line JSON in command line causes parser errors  
- **Token separators**: `&&` not supported, causes parsing failures
- **Python -c with long strings**: Extremely long single-line Python commands hang terminal

**✅ EFFICIENT ALTERNATIVES:**
```powershell
# ✅ SHORT commands with timeouts
curl.exe --max-time 5 "https://api-url/endpoint"

# ✅ SIMPLE data - avoid complex JSON
curl.exe -d "{'simple':'data'}" -H "Content-Type: application/json"

# ✅ CREATE .ps1 scripts for complex operations
# Write to file, then execute

# ✅ SEPARATE commands instead of &&
curl.exe -s "url1"
curl.exe -s "url2"
```

**Why this matters:**
- PowerShell has its own `curl` alias that conflicts with standard curl behavior
- Using `curl.exe` directly ensures consistent results
- Prevents PowerShell parsing issues and command failures
- **Long commands literally freeze the terminal requiring manual intervention**

### **🔍 STEP 1: INITIAL SYSTEM ASSESSMENT**
**Use these endpoints first to understand system state:**

```bash
# Primary health check (ALWAYS START HERE)
curl.exe -s https://pulsecheck-mobile-app-production.up.railway.app/api/v1/health

# Production debug overview (CRITICAL CONTEXT)
curl.exe -s https://pulsecheck-mobile-app-production.up.railway.app/api/v1/debug/summary

# OpenAI system status (AI-SPECIFIC)
curl.exe -s https://pulsecheck-mobile-app-production.up.railway.app/api/v1/openai/debug/summary
```

**⚠️ INTERPRET RESULTS CAREFULLY:**
- **Empty data** = Debug middleware not capturing real traffic (NOT healthy system)
- **"production_warning" present** = No real performance data available  
- **"middleware_status": "not_available"** = Limited debugging capabilities

### **🔍 STEP 2: TARGETED INVESTIGATION**
**Based on issue type, use specific endpoints:**

#### **🚨 Error Debugging**
```bash
# Error pattern analysis
curl.exe -s "https://pulsecheck-mobile-app-production.up.railway.app/api/v1/debug/requests?filter_type=errors&limit=20"

# Claude-optimized context
curl.exe -s "https://pulsecheck-mobile-app-production.up.railway.app/api/v1/debug/claude/context?issue_type=error&time_window=30"
```

#### **⚡ Performance Issues**
```bash
# Slow request analysis  
curl.exe -s "https://pulsecheck-mobile-app-production.up.railway.app/api/v1/debug/requests?filter_type=slow&min_time_ms=1000"

# Performance trends
curl.exe -s "https://pulsecheck-mobile-app-production.up.railway.app/api/v1/debug/performance/analysis"
```

#### **🔐 Authentication Problems**
```bash
# Auth pattern validation
curl.exe -s "https://pulsecheck-mobile-app-production.up.railway.app/api/v1/debug/claude/context?issue_type=auth"

# RLS security audit
curl.exe -s "https://pulsecheck-mobile-app-production.up.railway.app/api/v1/debug/configuration-audit"
```

#### **🤖 AI Service Issues**
```bash
# OpenAI connectivity & cost tracking
curl.exe -s "https://pulsecheck-mobile-app-production.up.railway.app/api/v1/openai/debug/test-connection"

# AI persona functionality
curl.exe -s "https://pulsecheck-mobile-app-production.up.railway.app/api/v1/openai/debug/test-personas"

# Error pattern analysis
curl.exe -s "https://pulsecheck-mobile-app-production.up.railway.app/api/v1/openai/debug/error-patterns"
```

### **🔍 STEP 3: PREDICTIVE ANALYSIS**
**Use AI-enhanced endpoints for deeper insights:**

```bash
# Comprehensive system analysis
curl.exe -s "https://pulsecheck-mobile-app-production.up.railway.app/api/v1/debug/ai-insights/comprehensive"

# Failure point prediction
curl.exe -s "https://pulsecheck-mobile-app-production.up.railway.app/api/v1/debug/failure-points/analysis"

# Risk assessment
curl.exe -s "https://pulsecheck-mobile-app-production.up.railway.app/api/v1/debug/risk-analysis/current?time_window=60"
```

---

## 🎯 **EFFICIENT DEBUGGING GUIDELINES FOR CLAUDE**

### **✅ OPTIMAL DEBUGGING APPROACH**

#### **1. PARALLEL TOOL CALLS**
**Always use multiple debug endpoints simultaneously:**
```
// Example: Investigate performance issue
GET /api/v1/health (basic status)
GET /api/v1/debug/summary (system overview)  
GET /api/v1/debug/requests?filter_type=slow (performance data)
GET /api/v1/debug/claude/context?issue_type=performance (AI analysis)
```

#### **2. CONTEXT-AWARE INTERPRETATION**
**Always check for these key indicators:**
- `middleware_status`: "not_available" = Limited real data
- `production_warning`: Present = Interpret empty results as "unknown" not "healthy"
- `false_positive_risk`: "HIGH" = Don't assume empty results mean no issues

#### **3. ESCALATION TRIGGERS**
**Escalate to user when:**
- All debug endpoints return empty data AND no production_warning
- Authentication errors prevent access to debug endpoints
- Multiple 500 errors from debug system itself
- OpenAI API showing authentication failures

### **❌ AVOID THESE DEBUGGING MISTAKES**

1. **DON'T assume empty results = healthy system**
2. **DON'T use localhost URLs for testing**
3. **DON'T interpret mock data as real system state**
4. **DON'T make sequential debug calls when parallel calls work**
5. **DON'T skip checking production_warning flags**

---

## 🔧 **DEBUGGING IN PRODUCTION**
Since we're in production, use production-safe debugging methods:

#### **✅ SAFE PRODUCTION DEBUGGING**
```bash
# Use production debug endpoints
curl.exe -s https://pulsecheck-mobile-app-production.up.railway.app/api/v1/health
curl.exe -s https://pulsecheck-mobile-app-production.up.railway.app/api/v1/openai/debug/summary
curl.exe -s https://pulsecheck-mobile-app-production.up.railway.app/api/v1/debug/summary
```

#### **❌ AVOID IN PRODUCTION**
- Local server testing
- Mock data insertion  
- Development mode flags
- Localhost API calls
- **False positive risks**: Empty debug results interpreted as "healthy"
- **Misleading mock data**: Any endpoint returning fake successful data

**🚨 CRITICAL WARNING**: Always check for `production_warning` in debug responses. Empty results without warnings may indicate debug middleware not capturing real traffic.

---

## 🌐 **ENVIRONMENT CONFIGURATION STATUS**

### **✅ CONFIRMED PRODUCTION SETUP**

#### **Backend (.env) - VERIFIED ✅**
```bash
ENVIRONMENT=production
SUPABASE_URL=https://qwpwlubxhtuzvmvajjjr.supabase.co  
SUPABASE_ANON_KEY=[PRODUCTION_KEY]
SUPABASE_SERVICE_KEY=[ADMIN_KEY]
OPENAI_API_KEY=[LIVE_API_KEY]
```

#### **Frontend (.env) - VERIFIED ✅**  
```bash
REACT_APP_API_URL=https://pulsecheck-mobile-app-production.up.railway.app
REACT_APP_SUPABASE_URL=https://qwpwlubxhtuzvmvajjjr.supabase.co
REACT_APP_SUPABASE_ANON_KEY=[PUBLIC_KEY]
```

#### **⚠️ AI ASSISTANT PROTOCOL**
- **DO NOT ask about missing .env files** - Both backend and frontend .env files exist and are properly configured
- **DO NOT suggest creating .env files** - They are already set up for production
- **DO NOT ask for environment variable values** - All required variables are configured

---

## 🚀 **PRODUCTION READINESS STATUS**

### **✅ SYSTEMS OPERATIONAL**
- **Authentication & Security**: RLS properly configured
- **AI Services**: 4 personas with OpenAI observability
- **Database**: Supabase production instance connected
- **Real-time**: User-scoped subscriptions active
- **File Storage**: RLS-secured with user isolation
- **Error Handling**: Comprehensive debugging system
- **Performance Monitoring**: OpenAI cost tracking active

### **🔮 FUTURE DEVELOPMENT ENVIRONMENT**
When development branches are created:
- **GitHub**: dev branch → triggers Railway/Vercel dev deployments
- **Railway**: Separate dev environment with mock data
- **Vercel**: Separate dev preview with test configurations
- **Database**: Separate dev Supabase project or staging tables

---

## 📊 **DEBUGGING DECISION TREE FOR CLAUDE**

### **START HERE: Health Check**
```
1. GET /health → 200 OK?
   ├─ YES: System operational, proceed to specific debugging
   └─ NO: Critical system failure, check infrastructure
```

### **🎯 SINGLE COMMAND VERIFICATION**
**Consolidated system verification (replaces 4 separate commands):**
```powershell
# Once deployed: All-in-one system check (COMING SOON)
curl.exe -s "https://pulsecheck-mobile-app-production.up.railway.app/api/v1/database/full-system-check"

# Current working verification commands:
curl.exe -s "https://pulsecheck-mobile-app-production.up.railway.app/api/v1/database/environment"
curl.exe -s "https://pulsecheck-mobile-app-production.up.railway.app/api/v1/database/comprehensive-status"
```

**What the consolidated check provides:**
- ✅ Environment variables (SUPABASE_SERVICE_ROLE_KEY status)
- ✅ Database client creation testing
- ✅ Database query functionality validation
- ✅ Auth methods availability check
- ✅ Overall status assessment with actionable recommendations
- ✅ Response time monitoring

**Efficiency Gain:** Reduces verification from 4 curl commands to 1

### **ISSUE-SPECIFIC DEBUGGING**

```
2. Issue Type Detection:
   ├─ AUTHENTICATION: Use /debug/claude/context?issue_type=auth
   ├─ PERFORMANCE: Use /debug/requests?filter_type=slow  
   ├─ AI_SERVICES: Use /openai/debug/test-personas
   ├─ ERRORS: Use /debug/requests?filter_type=errors
   └─ GENERAL: Use /debug/summary + /debug/ai-insights/comprehensive
```

### **INTERPRETATION GUIDELINES**

```
3. Result Analysis:
   ├─ Empty data + production_warning: Debug middleware not capturing traffic
   ├─ Empty data + NO warning: Potential system issue OR healthy system
   ├─ Error patterns found: Analyze with /debug/claude/context
   └─ Performance issues: Check /debug/failure-points/analysis
```

---

## 🚨 **RAILWAY ENVIRONMENT SETUP**

### **Critical Environment Variables**
Our production deployment requires specific environment variables in Railway:

**🔧 Quick Environment Diagnosis:**
```powershell
curl.exe -s "https://pulsecheck-mobile-app-production.up.railway.app/api/v1/database/environment"
```

**Required Variables:**
- ✅ `SUPABASE_URL` - Database connection endpoint
- ✅ `SUPABASE_ANON_KEY` - Public authentication key  
- ✅ `SUPABASE_SERVICE_ROLE_KEY` - Backend operations key (**Critical for auth signup/database operations**)
- ⚠️ `DB_PASSWORD` - Database password (optional but recommended)

### **Adding Missing Variables to Railway**
1. Go to [Railway Dashboard](https://railway.app/) 
2. Select your PulseCheck project
3. Navigate to **Variables** tab
4. Click **Add Variable**
5. Add missing variable with its value
6. Wait 2-3 minutes for automatic redeploy
7. Verify with environment check endpoint

### **🔗 Detailed Setup Documentation**
For comprehensive setup instructions: **[ai/RAILWAY_ENVIRONMENT_SETUP.md](RAILWAY_ENVIRONMENT_SETUP.md)**

**Contains:**
- Step-by-step Railway configuration
- Verification commands with expected results  
- Troubleshooting guide for deployment issues
- PowerShell-compatible curl.exe commands
- Before/after environment comparisons

---

## 🎯 **EFFICIENT DEBUGGING GUIDELINES FOR CLAUDE**

### **✅ OPTIMAL DEBUGGING APPROACH**

#### **1. PARALLEL TOOL CALLS**
**Always use multiple debug endpoints simultaneously:**
```
// Example: Investigate performance issue
GET /api/v1/health (basic status)
GET /api/v1/debug/summary (system overview)  
GET /api/v1/debug/requests?filter_type=slow (performance data)
GET /api/v1/debug/claude/context?issue_type=performance (AI analysis)
```

#### **2. CONTEXT-AWARE INTERPRETATION**
**Always check for these key indicators:**
- `middleware_status`: "not_available" = Limited real data
- `production_warning`: Present = Interpret empty results as "unknown" not "healthy"
- `false_positive_risk`: "HIGH" = Don't assume empty results mean no issues

#### **3. ESCALATION TRIGGERS**
**Escalate to user when:**
- All debug endpoints return empty data AND no production_warning
- Authentication errors prevent access to debug endpoints
- Multiple 500 errors from debug system itself
- OpenAI API showing authentication failures

### **❌ AVOID THESE DEBUGGING MISTAKES**

1. **DON'T assume empty results = healthy system**
2. **DON'T use localhost URLs for testing**
3. **DON'T interpret mock data as real system state**
4. **DON'T make sequential debug calls when parallel calls work**
5. **DON'T skip checking production_warning flags**

---

## 🔧 **DEBUGGING IN PRODUCTION**
Since we're in production, use production-safe debugging methods:

#### **✅ SAFE PRODUCTION DEBUGGING**
```bash
# Use production debug endpoints
curl.exe -s https://pulsecheck-mobile-app-production.up.railway.app/api/v1/health
curl.exe -s https://pulsecheck-mobile-app-production.up.railway.app/api/v1/openai/debug/summary
curl.exe -s https://pulsecheck-mobile-app-production.up.railway.app/api/v1/debug/summary
```

#### **❌ AVOID IN PRODUCTION**
- Local server testing
- Mock data insertion  
- Development mode flags
- Localhost API calls
- **False positive risks**: Empty debug results interpreted as "healthy"
- **Misleading mock data**: Any endpoint returning fake successful data

**🚨 CRITICAL WARNING**: Always check for `production_warning` in debug responses. Empty results without warnings may indicate debug middleware not capturing real traffic.

---

## 🎉 **MAJOR SUCCESS: AI-POWERED DEBUGGING SYSTEM OPERATIONAL**

### **🏆 BREAKTHROUGH ACHIEVED: Complete Infrastructure Issue Resolution**

**Date**: January 30, 2025  
**Achievement**: Successfully resolved critical routing issue affecting ALL `/api/v1/*` endpoints  
**Method**: AI-powered systematic debugging with comprehensive testing and log analysis  
**Result**: **All 7 routers now fully operational** with AI debugging system ready

### **🎯 PRIMARY DEBUGGING APPROACH - PROVEN WORKING**

**CONFIRMED**: The debugging middleware system successfully provides comprehensive data in 1-3 tool calls instead of 10-15, as demonstrated by our recent infrastructure resolution.

#### **Step 1: Quick System Health Check**
```bash
# Single command gives you complete system overview
curl https://pulsecheck-mobile-app-production.up.railway.app/api/v1/debug/summary
```

**This ONE call provides:**
- Recent requests with errors, timing, and performance scores
- Database operation statistics and bottlenecks  
- Error patterns and frequencies
- Performance analysis with recommendations
- System health indicators

#### **Step 2: Deep Dive (If Issues Found)**
```bash
# Get specific request details with full context
curl https://pulsecheck-mobile-app-production.up.railway.app/api/v1/debug/requests/{request_id}

# Or filter for specific issue types
curl https://pulsecheck-mobile-app-production.up.railway.app/api/v1/debug/requests?filter_type=errors
curl https://pulsecheck-mobile-app-production.up.railway.app/api/v1/debug/requests?filter_type=slow
```

**This provides:**
- Complete request/response cycle data
- All database operations for that request
- Performance metrics and scoring
- Error context and timing
- User authentication status

#### **Step 3: Performance Analysis**
```bash
# Get performance grades and recommendations
curl https://pulsecheck-mobile-app-production.up.railway.app/api/v1/debug/performance/analysis
```

### **🚨 WHEN TO USE OLD vs NEW DEBUGGING**

#### **✅ USE MIDDLEWARE DEBUG SYSTEM FOR:**
- User reports errors, slow performance, or functional issues
- Authentication problems  
- Database performance issues
- CORS errors
- API endpoint problems
- Response time investigations
- Error pattern analysis

#### **❌ ONLY USE MANUAL INVESTIGATION FOR:**
- Initial project setup
- Configuration file creation
- Environment variable setup (first time)
- Code architecture decisions
- Feature development planning

### **📋 AI DEBUGGING WORKFLOW - PROVEN SUCCESSFUL**

#### **For ANY User-Reported Issue - VALIDATED METHODOLOGY:**

**Step 1** (1 tool call): Check middleware debug summary ✅ **WORKING**
```bash
curl.exe -s "https://pulsecheck-mobile-app-production.up.railway.app/api/v1/debug/summary"
```

**Step 2** (1 tool call): If issues found, get specific details ✅ **WORKING**
```bash  
curl.exe -s "https://pulsecheck-mobile-app-production.up.railway.app/api/v1/debug/requests?filter_type=errors"
```

**Step 3** (Optional): Deep dive into specific problematic request ✅ **WORKING**
```bash
curl.exe -s "https://pulsecheck-mobile-app-production.up.railway.app/api/v1/debug/requests/{specific_request_id}"
```

## **DEPLOYMENT & TESTING LESSONS LEARNED**

### **✅ WHAT WORKS (Use These Approaches):**

**Commands & Tools:**
- `curl.exe` - Always use .exe extension on Windows
- `Invoke-RestMethod` - Reliable for PowerShell HTTP requests
- `git add`, `git commit`, `git push` - Standard git workflow works perfectly
- Railway deployment via git push - Automatic detection and rebuilding
- FastAPI with performance optimizations - Achieved 99.5% improvement

**Performance Optimizations (Proven Effective):**
- GZip compression middleware - Massive response time improvements
- Database connection pooling - Infrastructure optimization
- Horizontal scaling with Railway - 2 replicas working
- Resource limits (2 vCPU, 4GB RAM) - Stable performance
- Health endpoint monitoring - Real-time performance tracking

**Error Resolution Patterns:**
- Import errors: Add missing imports to requirements.txt immediately
- Dependency conflicts: Pin specific versions (e.g., gotrue==2.8.1)
- Supabase client: Remove unsupported options parameters

### **❌ WHAT DOESN'T WORK (Avoid These):**

**Commands & Tools:**
- `curl` without .exe - Fails on Windows PowerShell
- Complex PowerShell one-liners - Console buffer issues, unreliable
- Long PowerShell commands - Cause display errors and timeouts
- Multiple sequential curl calls - Leads to hanging

**Testing Approaches:**
- Running multiple separate test scripts - Inefficient, fragmented results
- Testing without timeout parameters - Causes indefinite hanging
- Complex PowerShell syntax in single commands - Parser errors

**Database Connection Issues (Still Investigating):**
- Supabase client with options parameter - Not supported in current version
- Long-running database operations without proper timeout handling
- Missing psycopg2 dependency - Causes SQLite fallback

### **🔧 RELIABLE PATTERNS TO FOLLOW:**

1. **Always use `curl.exe` on Windows**
2. **Keep PowerShell commands simple and short**
3. **Use timeouts on all HTTP requests (10-30 seconds)**
4. **Pin all dependency versions in requirements.txt**
5. **Test infrastructure endpoints first, then database endpoints**
6. **Use git workflow for all deployments - Railway auto-detects**
7. **Performance optimizations work - connection pooling, compression, scaling**

### **🚨 CURRENT KNOWN ISSUES:**

**RESOLVED:**
- ✅ GZipMiddleware import error - Fixed with proper import
- ✅ psycopg2 missing dependency - Added psycopg2-binary==2.9.9
- ✅ Supabase client options - Removed unsupported parameters
- ✅ Performance (27s→126ms) - Fixed with optimization stack

**ACTIVE INVESTIGATION:**
- ❌ Database endpoints timing out after 10-15 seconds
- ❌ Version endpoint returning 404 (partial deployment)
- ❌ Auth/Journal operations hanging despite infrastructure improvements

**DEPLOYMENT DISCREPANCY RESOLVED:**
- ✅ **RESOLVED 2025-06-27**: Railway deployment discrepancy fixed with force push
- ✅ Complete project synchronization completed to ensure Railway has latest code
- ✅ No longer running stale cached builds - all commits now deploy properly
- **NOTE**: If database endpoints still hang after this sync, it's a true connection issue, not old code

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