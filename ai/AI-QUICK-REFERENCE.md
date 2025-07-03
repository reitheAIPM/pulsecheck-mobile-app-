# AI Quick Reference Guide

**Purpose**: Fast access to essential debugging commands and fixes for AI development  
**Updated**: January 30, 2025  
**Environment**: Production-only (Railway + Vercel + Supabase)

---

## 🚀 **QUICK DEBUGGING COMMANDS**

### **System Health Checks**
```powershell
# Overall system health
curl.exe -s "https://pulsecheck-mobile-app-production.up.railway.app/health"

# AI scheduler status
curl.exe -s "https://pulsecheck-mobile-app-production.up.railway.app/api/v1/scheduler/status"

# Database connectivity
curl.exe -s "https://pulsecheck-mobile-app-production.up.railway.app/api/v1/database/comprehensive-status"

# Database client validation (CRITICAL - prevents AI failures)
curl.exe -s "https://pulsecheck-mobile-app-production.up.railway.app/api/v1/debug/database/client-validation"

# Environment variables check
curl.exe -s "https://pulsecheck-mobile-app-production.up.railway.app/api/v1/debug/environment"
```

### **AI Testing Mode Control**
```powershell
# Enable testing mode (immediate AI responses)
Invoke-WebRequest -Uri "https://pulsecheck-mobile-app-production.up.railway.app/api/v1/scheduler/testing/enable" -Method POST

# Disable testing mode (restore production timing)
Invoke-WebRequest -Uri "https://pulsecheck-mobile-app-production.up.railway.app/api/v1/scheduler/testing/disable" -Method POST

# Check testing status
Invoke-WebRequest -Uri "https://pulsecheck-mobile-app-production.up.railway.app/api/v1/scheduler/testing/status" -Method GET

# Parse JSON response
(Invoke-WebRequest -Uri "https://pulsecheck-mobile-app-production.up.railway.app/api/v1/scheduler/testing/status" -Method GET).Content | ConvertFrom-Json | ConvertTo-Json -Depth 10
```

### **Manual AI Cycle Triggers**
```powershell
# Trigger immediate AI engagement cycle
Invoke-WebRequest -Uri "https://pulsecheck-mobile-app-production.up.railway.app/api/v1/scheduler/manual-cycle?cycle_type=main" -Method POST

# Trigger analytics cycle
Invoke-WebRequest -Uri "https://pulsecheck-mobile-app-production.up.railway.app/api/v1/scheduler/manual-cycle?cycle_type=analytics" -Method POST
```

---

## ⚠️ **COMMON ISSUES & QUICK FIXES**

### **PowerShell Command Errors**
**Issue**: `curl -X POST` fails with "parameter cannot be found"  
**Fix**: Use `Invoke-WebRequest` for POST requests
```powershell
# ❌ WRONG
curl -X POST https://your-app/api/endpoint

# ✅ CORRECT
Invoke-WebRequest -Uri "https://your-app/api/endpoint" -Method POST
```

### **AI Testing Mode Not Working**
**Issue**: Testing mode shows as disabled when it should be enabled  
**Diagnosis**: Check actual status with GET request
```powershell
Invoke-WebRequest -Uri "https://pulsecheck-mobile-app-production.up.railway.app/api/v1/scheduler/testing/status" -Method GET
```
**Expected Response**: `"testing_mode": true` and `"status": "enabled"`

### **Scheduler Showing as Stopped**
**Issue**: Scheduler status shows "stopped" after deployments  
**Fix**: This is normal after Railway deployments, testing mode works independently
```powershell
# Check if testing mode still works regardless of scheduler status
Invoke-WebRequest -Uri "https://pulsecheck-mobile-app-production.up.railway.app/api/v1/scheduler/testing/enable" -Method POST
```

### **AI Reports "0 Journal Entries Found" (CRITICAL)**
**Issue**: AI system reports no journal entries despite data existing in mobile app  
**Cause**: Using anon client instead of service role client for AI operations  
**Diagnosis**: Check database client type
```powershell
curl.exe -s "https://pulsecheck-mobile-app-production.up.railway.app/api/v1/debug/database/client-validation"
```
**Expected Response**: `"service_client_status": "✅ Working"` and `"journal_entries_accessible": true`

**If service client fails:**
1. Check `SUPABASE_SERVICE_ROLE_KEY` environment variable
2. Verify `get_service_client()` function exists in database.py
3. Check RLS policies allow service role access
4. Test with: `GET /api/v1/debug/database/service-role-test`

### **System Health Shows "Degraded"**
**Issue**: Health endpoint returns degraded status  
**Diagnosis**: Check specific error rates and components
```json
{
  "status": "degraded",
  "alerts": ["High error rate: 16.67%"],
  "components": {
    "error_rate": "degraded",
    "response_time": "healthy", 
    "memory": "healthy",
    "disk": "healthy"
  }
}
```
**Action**: Monitor and investigate if error rate is consistently high

---

## 📋 **TESTING WORKFLOWS**

### **AI Response Testing Workflow**
1. **Enable testing mode**:
   ```powershell
   Invoke-WebRequest -Uri "https://pulsecheck-mobile-app-production.up.railway.app/api/v1/scheduler/testing/enable" -Method POST
   ```

2. **Verify testing mode enabled**:
   ```powershell
   Invoke-WebRequest -Uri "https://pulsecheck-mobile-app-production.up.railway.app/api/v1/scheduler/testing/status" -Method GET
   ```
   Expected: `"testing_mode": true`

3. **Test AI interactions** (create journal entries, trigger responses)

4. **Disable testing mode** when finished:
   ```powershell
   Invoke-WebRequest -Uri "https://pulsecheck-mobile-app-production.up.railway.app/api/v1/scheduler/testing/disable" -Method POST
   ```

### **System Health Validation Workflow**
1. **Check overall health**:
   ```powershell
   curl.exe -s "https://pulsecheck-mobile-app-production.up.railway.app/health"
   ```

2. **Check database connectivity**:
   ```powershell
   curl.exe -s "https://pulsecheck-mobile-app-production.up.railway.app/api/v1/database/comprehensive-status"
   ```

3. **Check AI scheduler status**:
   ```powershell
   curl.exe -s "https://pulsecheck-mobile-app-production.up.railway.app/api/v1/scheduler/status"
   ```

---

## 🎯 **PERFORMANCE BENCHMARKS**

### **Response Time Targets**
- **Health endpoint**: < 100ms
- **Testing mode toggle**: < 5ms
- **Database status**: < 100ms
- **Scheduler status**: < 50ms

### **Expected System States**

**Healthy System:**
```json
{
  "status": "healthy",
  "components": {
    "error_rate": "healthy",
    "response_time": "healthy",
    "memory": "healthy", 
    "disk": "healthy"
  },
  "alerts": []
}
```

**Testing Mode Enabled:**
```json
{
  "testing_mode": true,
  "status": "enabled",
  "testing_behavior": {
    "all_delays_bypassed": true,
    "bombardment_prevention_disabled": true,
    "immediate_responses": true
  }
}
```

**Scheduler Running:**
```json
{
  "status": "running",
  "running": true,
  "error_rate": 0.0,
  "current_status": "running"
}
```

---

## 🚨 **EMERGENCY PROCEDURES**

### **If AI Responses Stop Working**
1. **FIRST**: Check database client validation: `GET /api/v1/debug/database/client-validation`
2. Check testing mode status
3. Verify scheduler is running
4. Check system health for errors
5. Try manual cycle trigger
6. Enable testing mode for immediate debugging

### **If AI Reports "0 Journal Entries Found" (CRITICAL)**
1. **Immediate check**: `GET /api/v1/debug/database/client-validation`
2. **If service client fails**: Check SUPABASE_SERVICE_ROLE_KEY environment variable
3. **Verify RLS policies**: `GET /api/v1/debug/database/rls-analysis`
4. **Check schema**: `GET /api/v1/debug/database/schema-validation`
5. **Test service role access**: `GET /api/v1/debug/database/service-role-test`

### **If System Shows Multiple Errors**
1. Check Railway deployment status
2. Verify environment variables are set
3. Check Supabase connectivity
4. Monitor error rates over time
5. Consider redeployment if persistent

### **If PowerShell Commands Fail**
1. Verify URL is correct and accessible
2. Use `Invoke-WebRequest` for POST requests
3. Use `curl.exe` for GET requests
4. Check for network connectivity issues
5. Try parsing JSON responses for detailed error info

---

## 📚 **RELATED DOCUMENTATION**

- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Complete development guidelines
- **[AI-DEBUGGING-SYSTEM.md](AI-DEBUGGING-SYSTEM.md)** - Comprehensive debugging system
- **[TASK-STATUS-CONSOLIDATED.md](TASK-STATUS-CONSOLIDATED.md)** - Current tasks and status 