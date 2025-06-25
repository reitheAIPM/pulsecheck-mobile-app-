# 🚀 AI Debug Strategy - Quick Reference

**Status**: ✅ ACTIVE  
**Purpose**: Eliminate 10-15 tool call investigations with 1-3 structured API calls

---

## 🎯 **MANDATORY WORKFLOW**

### **For ANY User Issue - Use This FIRST:**

```bash
# 1. System Overview (1 call - replaces railway logs + manual testing)
curl https://pulsecheck-mobile-app-production.up.railway.app/api/v1/debug/summary

# 2. Error Focus (1 call - if issues found)
curl https://pulsecheck-mobile-app-production.up.railway.app/api/v1/debug/requests?filter_type=errors

# 3. Deep Dive (1 call - if specific request needs analysis)
curl https://pulsecheck-mobile-app-production.up.railway.app/api/v1/debug/requests/{request_id}
```

**Result**: Complete debugging context in 1-3 calls instead of 10-15

---

## 📋 **WHAT EACH ENDPOINT PROVIDES**

### `/debug/summary`
- ✅ Recent requests with performance scores
- ✅ Error requests with full context
- ✅ Database operation statistics  
- ✅ Performance analysis with grades
- ✅ Automatic recommendations

### `/debug/requests?filter_type=errors`
- ✅ All recent errors with request context
- ✅ Response times and database operations
- ✅ User authentication status
- ✅ Complete request/response data

### `/debug/requests/{request_id}`
- ✅ Complete request lifecycle analysis
- ✅ All database operations for that request
- ✅ Performance metrics and error context
- ✅ Headers, body, timing data

---

## 🚨 **WHEN TO USE NEW vs OLD DEBUGGING**

### ✅ **USE MIDDLEWARE DEBUG FOR:**
- User reports errors, slow performance, login issues
- Authentication problems
- Database performance issues
- CORS errors  
- API endpoint problems
- Any operational issue

### ❌ **ONLY USE MANUAL FOR:**
- Initial project setup
- New feature architecture
- Configuration file creation (first time)
- Code review and refactoring

---

## 🏆 **SUCCESS TARGETS**

- **80% reduction** in debugging tool calls (10-15 → 1-3)
- **70% faster** issue resolution (10-15 min → 2-3 min)  
- **Structured JSON data** instead of log parsing
- **Complete request context** instead of guesswork

---

## 🔧 **INTEGRATION BENEFITS**

### **Automatic Capture:**
- Every request gets unique ID
- All database operations tracked
- Performance metrics calculated
- Error context preserved

### **AI-Ready Data:**
- Structured JSON responses
- Performance scoring
- Automatic recommendations
- Request correlation

### **Debug Headers:**
- `X-Request-ID`: Unique identifier
- `X-Response-Time`: Actual timing
- `X-DB-Operations`: Database usage count

---

**Remember**: This middleware transforms debugging from investigation to analysis. Always start here before manual debugging. 

# Railway CLI Debugging Protocol 🚂

## **Proper Railway Logs Usage**

### **1. Service-Specific Log Monitoring**
```bash
# Monitor backend service logs specifically
railway logs --service pulsecheck-mobile-app-

# Monitor with real-time filtering (PowerShell)
railway logs --service pulsecheck-mobile-app- | Select-String "ERROR|DEBUG|INFO"
```

### **2. Triggering Endpoint Activity for Live Debugging**

#### **Health Check (Basic)**
```bash
curl -s https://pulsecheck-mobile-app-production.up.railway.app/health
```

#### **Test Debug Endpoints**
```bash
# Test debug router (should work if import fixed)
curl -s "https://pulsecheck-mobile-app-production.up.railway.app/api/v1/debug/summary"

# Test enhanced AI insights
curl -s "https://pulsecheck-mobile-app-production.up.railway.app/api/v1/debug/ai-insights/comprehensive"

# Test edge testing suite
curl -s "https://pulsecheck-mobile-app-production.up.railway.app/api/v1/debug/edge-testing/comprehensive"
```

#### **Test Authentication Endpoints**
```bash
# Test auth endpoint (triggers logs)
curl -X POST https://pulsecheck-mobile-app-production.up.railway.app/api/v1/auth/signin \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}'
```

### **3. Live Debugging Workflow**

1. **Start Log Monitoring**
   ```bash
   railway logs --service backend
   ```

2. **In Another Terminal, Trigger Endpoints**
   ```bash
   # Test the specific endpoint causing issues
   curl -s "https://pulsecheck-mobile-app-production.up.railway.app/api/v1/debug/ai-insights/comprehensive"
   ```

3. **Watch for Log Patterns**
   - ✅ `INFO:main:Debug middleware router loaded successfully`
   - ❌ `ERROR:main:Failed to import debug router:`
   - ❌ `404 Not Found` responses
   - ✅ Successful endpoint hits with response data

### **4. Log Analysis Checklist**

#### **Router Import Issues**
Look for:
```
ERROR:main:Error registering routers: attempted relative import with no known parent package
ERROR:main:Failed to import debug router: [error details]
```

#### **Successful Router Loading**
Look for:
```
INFO:main:Debug middleware router loaded successfully
INFO:main:AI debug router loaded successfully
```

#### **Endpoint Access Logs**
Look for:
```
INFO: 100.64.0.x:xxxx - "GET /api/v1/debug/ai-insights/comprehensive HTTP/1.1" 200 OK
```

### **5. Code Enhancement for Better Debugging**

If logs are insufficient, add these to key endpoints:

#### **Enhanced Logging in main.py**
```python
# In router registration section
try:
    import app.routers.debug as debug_module
    app.include_router(debug_module.router, prefix="/api/v1")
    logger.info("✅ Debug middleware router loaded successfully")
    logger.info(f"Debug router endpoints: {[route.path for route in debug_module.router.routes]}")
except Exception as e:
    logger.error(f"❌ Failed to import debug router: {e}")
    logger.error(f"Error type: {type(e).__name__}")
    import traceback
    logger.error(f"Traceback: {traceback.format_exc()}")
```

#### **Enhanced Logging in Debug Router**
```python
# In app/routers/debug.py
@router.get("/ai-insights/comprehensive")
async def get_comprehensive_ai_insights(request: Request):
    logger.info("🎯 AI Insights endpoint called")
    try:
        # ... existing code ...
        logger.info(f"✅ AI Insights generated successfully: {len(insights)} insights")
        return {"status": "success", "ai_insights": insights}
    except Exception as e:
        logger.error(f"❌ AI Insights failed: {e}")
        logger.error(f"Error details: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"AI insights failed: {str(e)}")
```

---

## **Current Issue Analysis Protocol**

### **Step 1: Monitor Live Logs**
```bash
railway logs --service pulsecheck-mobile-app-
```

### **Step 2: Test Current Debug Router Status**
```bash
# Test if debug router is working
curl -s "https://pulsecheck-mobile-app-production.up.railway.app/api/v1/debug/summary"

# Expected: JSON response OR 404 with logs showing the attempt
```

### **Step 3: Analyze Log Output**
- ✅ **Success**: `INFO:main:Debug middleware router loaded successfully`
- ❌ **Failure**: `ERROR:main:Failed to import debug router:`

### **Step 4: If Still Failing, Add Enhanced Logging**
1. Add detailed import logging to main.py
2. Add endpoint-level logging to debug router
3. Deploy and test again

---

## **External Logging Setup (Future Enhancement)**

For persistent log history and advanced filtering:

### **Logtail Integration**
```bash
# In Railway dashboard
1. Go to project settings
2. Add Logtail integration
3. Configure log forwarding
4. Access historical logs via Logtail dashboard
```

### **Benefits of External Logging**
- ✅ **Persistent History**: View logs from hours/days ago
- ✅ **Advanced Filtering**: Search by endpoint, error type, user ID
- ✅ **Real-time Alerts**: Get notified of critical errors
- ✅ **Performance Metrics**: Track response times and patterns

---

*This protocol ensures systematic debugging with proper log monitoring and detailed error analysis.* 

# Full-Stack Debugging Protocol 🚀

## **Overview**
Comprehensive debugging strategy for our stack:
- **Railway** (backend service + logs)
- **Supabase** (auth + database + RLS)  
- **Vercel** (frontend hosting)
- **Enhanced AI Debug System v2.0** (our custom solution)

---

## 🎯 **Automated Debugging Workflow**

### **Step 1: Railway Backend Debugging**

#### **1.1 Automated Log Capture (No Manual Ctrl+C)**
```bash
# Stream logs for 10 seconds and auto-stop
timeout 10s railway logs --service pulsecheck-mobile-app-

# Snapshot last 50 lines
railway logs --service pulsecheck-mobile-app- | head -n 50

# For Windows PowerShell - Use Select-Object instead of head
railway logs --service pulsecheck-mobile-app- | Select-Object -First 50
```

#### **1.2 Trigger API Traffic for Log Generation**
```bash
# Health check (basic connectivity)
curl.exe -s https://pulsecheck-mobile-app-production.up.railway.app/health

# Auth endpoint (triggers backend logic)
curl.exe -X POST "https://pulsecheck-mobile-app-production.up.railway.app/api/v1/auth/signin" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}'

# Debug endpoints (our enhanced system)
curl.exe -s "https://pulsecheck-mobile-app-production.up.railway.app/api/v1/debug/ai-insights/comprehensive"
```

#### **1.3 Router Import Debugging Protocol**
```python
# Enhanced logging for router imports (add to main.py)
try:
    logger.info("🔄 Attempting to import debug router...")
    import app.routers.debug as debug_module
    logger.info("✅ Debug module imported successfully")
    
    app.include_router(debug_module.router, prefix="/api/v1")
    logger.info("✅ Debug middleware router loaded successfully")
    
    # Log available routes for verification
    debug_routes = [route.path for route in debug_module.router.routes]
    logger.info(f"📋 Debug router endpoints: {debug_routes}")
    
except Exception as e:
    logger.error(f"❌ Failed to import debug router: {e}")
    logger.error(f"❌ Error type: {type(e).__name__}")
    import traceback
    logger.error(f"❌ Full traceback: {traceback.format_exc()}")
```

### **Step 2: Vercel Frontend Debugging**

#### **2.1 Frontend Build/Runtime Logs**
```bash
# Check frontend logs (update project name as needed)
vercel logs pulsecheck-mobile-app.vercel.app --since 1h

# Local development debugging
vercel dev
```

#### **2.2 Client-Side API Call Debugging**
```javascript
// Add to frontend API calls
console.log("🔄 Making API request to:", endpoint);
try {
  const response = await fetch(endpoint, options);
  console.log("✅ API Response:", response.status, response.statusText);
  const data = await response.json();
  console.log("📊 Response data:", data);
  return data;
} catch (error) {
  console.error("❌ API Error:", error);
  console.error("❌ Endpoint:", endpoint);
  console.error("❌ Options:", options);
  throw error;
}
```

### **Step 3: Supabase Debugging**

#### **3.1 Authentication Debugging**
```python
# Backend JWT verification
import jwt
try:
    decoded = jwt.decode(token, verify=False)  # For debugging only
    logger.info(f"🔑 JWT Claims: {decoded}")
    logger.info(f"🔑 User ID: {decoded.get('sub')}")
    logger.info(f"🔑 Token expires: {decoded.get('exp')}")
except Exception as e:
    logger.error(f"❌ JWT decode error: {e}")
```

#### **3.2 RLS (Row-Level Security) Debugging**
```sql
-- Temporary debug policy (REMOVE after debugging)
CREATE POLICY "debug_allow_all" 
ON your_table FOR ALL 
USING (true);

-- Check existing policies
SELECT * FROM pg_policies WHERE tablename = 'your_table';
```

#### **3.3 Database Query Debugging**
```python
# Enhanced database operation logging
async def debug_query(query: str, params: dict = None):
    start_time = time.time()
    try:
        logger.info(f"🔍 Executing query: {query}")
        logger.info(f"🔍 Parameters: {params}")
        
        result = await database.fetch_all(query, params)
        execution_time = (time.time() - start_time) * 1000
        
        logger.info(f"✅ Query success: {len(result)} rows in {execution_time:.2f}ms")
        return result
    except Exception as e:
        execution_time = (time.time() - start_time) * 1000
        logger.error(f"❌ Query failed after {execution_time:.2f}ms: {e}")
        raise
```

---

## 🤖 **Enhanced AI Debug System Integration**

### **4.1 Our Custom Debug Endpoints**
```bash
# Comprehensive system analysis (1 call instead of 10-15)
curl.exe -s "https://pulsecheck-mobile-app-production.up.railway.app/api/v1/debug/ai-insights/comprehensive"

# Edge testing suite
curl.exe -s "https://pulsecheck-mobile-app-production.up.railway.app/api/v1/debug/edge-testing/comprehensive"

# Failure point prediction
curl.exe -s "https://pulsecheck-mobile-app-production.up.railway.app/api/v1/debug/failure-points/analysis"

# Current risk assessment
curl.exe -s "https://pulsecheck-mobile-app-production.up.railway.app/api/v1/debug/risk-analysis/current"
```

### **4.2 AI Learning Feedback Loop**
```bash
# Record debugging session results
curl.exe -X POST "https://pulsecheck-mobile-app-production.up.railway.app/api/v1/debug/ai-learning/feedback" \
  -H "Content-Type: application/json" \
  -d '{
    "ai_model": "claude-sonnet-4",
    "issue_type": "router_import_failure", 
    "approach_used": "enhanced_logging_first",
    "tools_used": ["railway_logs", "curl_testing"],
    "success": true,
    "time_to_resolution": "15_minutes"
  }'
```

---

## 🔧 **Automated Debugging Scripts**

### **Railway Health Check Script**
```bash
#!/bin/bash
echo "🔄 Testing Railway backend health..."
health_response=$(curl.exe -s https://pulsecheck-mobile-app-production.up.railway.app/health)
echo "✅ Health Response: $health_response"

echo "🔄 Testing debug endpoints..."
debug_response=$(curl.exe -s https://pulsecheck-mobile-app-production.up.railway.app/api/v1/debug/summary)
if [[ $debug_response == *"404"* ]]; then
  echo "❌ Debug router not loaded - checking logs..."
  timeout 5s railway logs --service pulsecheck-mobile-app-
else
  echo "✅ Debug router working: $debug_response"
fi
```

### **Full Stack Test Script**
```bash
#!/bin/bash
echo "🚀 Full Stack Debugging Test"

# 1. Backend health
echo "1️⃣ Backend Health Check..."
curl.exe -s https://pulsecheck-mobile-app-production.up.railway.app/health

# 2. Auth endpoint
echo "2️⃣ Auth Endpoint Test..."
curl.exe -X POST https://pulsecheck-mobile-app-production.up.railway.app/api/v1/auth/signin \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}'

# 3. Database-dependent endpoint
echo "3️⃣ Database Connection Test..."
curl.exe -s https://pulsecheck-mobile-app-production.up.railway.app/api/v1/journal/stats

# 4. Enhanced debug system
echo "4️⃣ AI Debug System Test..."
curl.exe -s https://pulsecheck-mobile-app-production.up.railway.app/api/v1/debug/ai-insights/comprehensive

echo "5️⃣ Checking logs..."
timeout 5s railway logs --service pulsecheck-mobile-app-
```

---

## 📊 **Long-Term Observability**

### **External Logging Integration**
```bash
# Recommended: Logtail integration for persistent logs
1. Railway Dashboard → Project Settings
2. Add Logtail integration  
3. Configure log forwarding
4. Access historical logs via Logtail dashboard
```

### **Monitoring Alerts**
```yaml
# Example monitoring setup
alerts:
  - name: "High Error Rate"
    condition: "error_rate > 5%"
    notification: "slack_webhook"
  
  - name: "Debug Router Down"
    condition: "404 on /api/v1/debug/*"
    notification: "immediate_alert"
```

---

## 🎯 **Debugging Decision Tree**

### **Authentication Issues**
1. `curl.exe auth endpoint` → Check response
2. `railway logs` → Look for JWT errors
3. `supabase dashboard` → Check auth logs
4. **Our AI System**: `/debug/ai-insights/comprehensive`

### **Database Issues**  
1. `curl.exe database endpoint` → Check connectivity
2. `railway logs` → Look for Supabase errors
3. `supabase dashboard` → Check RLS policies
4. **Our AI System**: `/debug/failure-points/analysis`

### **Router Import Issues**
1. `railway logs` → Look for import errors
2. Enhanced logging (as shown above)
3. Check file structure and imports
4. **Our AI System**: `/debug/edge-testing/comprehensive`

### **Unknown Issues**
1. **Start with our AI system**: `/debug/ai-insights/comprehensive`
2. Follow AI recommendations with confidence scores
3. Use traditional tools only if AI system unavailable

---

**🏆 Goal: 80% reduction in debugging time through automation and AI-powered analysis**

*This protocol transforms debugging from manual investigation to intelligent, automated analysis.* 