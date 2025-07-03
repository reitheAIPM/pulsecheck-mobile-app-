# AI System Debugging Toolkit
## Comprehensive Diagnostic System for PulseCheck AI Services

### 🎯 Purpose
This toolkit provides rapid diagnosis and resolution of AI system issues, designed to prevent and quickly resolve problems like the recent "requests dependency" failure that caused complete AI service outages.

### 🔍 Root Cause Analysis: Recent Issue
**Problem**: AI interactions completely stopped working
**Symptoms**: 
- Journal entries created but no AI responses
- AI service endpoints returning 404 errors
- Scheduler appeared stopped in monitoring but showed running in direct calls

**Root Cause**: Missing `requests` dependency in `requirements.txt` caused:
1. Import failures during Railway startup
2. Silent router registration failures 
3. Partial service availability (basic endpoints worked, AI-specific failed)
4. Service synchronization issues

**Solution**: Added `requests==2.31.0` to `backend/requirements.txt`

### 🚨 Early Warning System
The following patterns indicate similar issues:

#### 1. Router Registration Failures
**Symptoms**:
- 404 errors on specific service endpoints
- Some endpoints work, others fail
- No clear error messages in logs

**Quick Test**:
```powershell
# Test all critical AI endpoints
$endpoints = @(
    "/api/v1/scheduler/status",
    "/api/v1/adaptive-ai/health", 
    "/api/v1/ai-monitoring/last-action/test-user",
    "/api/v1/manual-ai/debug-database/test-user"
)

foreach ($endpoint in $endpoints) {
    try {
        $response = Invoke-RestMethod "https://pulsecheck-mobile-app-production.up.railway.app$endpoint"
        Write-Host "✅ $endpoint - Working" -ForegroundColor Green
    } catch {
        Write-Host "❌ $endpoint - FAILED" -ForegroundColor Red
    }
}
```

#### 2. Dependency Import Failures
**Symptoms**:
- Partial service availability
- Health endpoint works but feature endpoints fail
- No explicit error messages

**Quick Test**:
```powershell
# Check if dependency imports are working
$healthResponse = Invoke-RestMethod "https://pulsecheck-mobile-app-production.up.railway.app/health"
if ($healthResponse.status -eq "healthy") {
    Write-Host "✅ Basic imports working" -ForegroundColor Green
} else {
    Write-Host "❌ Basic system failure" -ForegroundColor Red
}
```

#### 3. Service Synchronization Issues
**Symptoms**:
- Different endpoints report different status
- AI monitoring shows different state than direct service calls
- Scheduler running but not processing

**Quick Test**:
```powershell
# Compare scheduler status from different sources
$directStatus = Invoke-RestMethod "https://pulsecheck-mobile-app-production.up.railway.app/api/v1/scheduler/status"
$monitorStatus = Invoke-RestMethod "https://pulsecheck-mobile-app-production.up.railway.app/api/v1/ai-monitoring/last-action/test-user"

Write-Host "Direct Scheduler Status: $($directStatus.status)" -ForegroundColor Cyan
Write-Host "Monitor Scheduler Status: $($monitorStatus.scheduler_running)" -ForegroundColor Cyan

if ($directStatus.status -eq "running" -and $monitorStatus.scheduler_running -eq $false) {
    Write-Host "⚠️ SYNC ISSUE DETECTED" -ForegroundColor Yellow
}
```

### 🛠️ Diagnostic Toolkit

#### 1. Comprehensive System Health Check
**File**: `system_health_diagnostic.ps1`
**Purpose**: Single command to check all AI system components

#### 2. Router Registration Validator  
**File**: `router_validation_diagnostic.ps1`
**Purpose**: Validate all router endpoints are properly registered

#### 3. Dependency Checker
**File**: `dependency_diagnostic.ps1` 
**Purpose**: Check for missing dependencies before they cause failures

#### 4. Service Sync Validator
**File**: `service_sync_diagnostic.ps1`
**Purpose**: Detect synchronization issues between services

### 📊 Monitoring Dashboard
**File**: `ai_monitoring_dashboard.ps1`
**Purpose**: Real-time status of all AI services with actionable insights

### 🔧 Quick Fix Commands

#### Start Scheduler
```powershell
Invoke-WebRequest -Uri "https://pulsecheck-mobile-app-production.up.railway.app/api/v1/scheduler/start" -Method POST
```

#### Enable Testing Mode
```powershell
Invoke-WebRequest -Uri "https://pulsecheck-mobile-app-production.up.railway.app/api/v1/scheduler/testing/enable" -Method POST
```

#### Check Service Health
```powershell
Invoke-RestMethod "https://pulsecheck-mobile-app-production.up.railway.app/health"
```

### 📈 Success Metrics
- **Router Registration**: 100% of endpoints responding (not 404)
- **Service Synchronization**: All services report consistent status
- **Dependency Resolution**: No import failures
- **AI Response Generation**: Working within expected timeframes

### 🎯 Future Prevention
1. **Automated Testing**: Run diagnostic toolkit before each deployment
2. **Dependency Validation**: Check requirements.txt completeness
3. **Router Registration Tests**: Validate all endpoints after deployment
4. **Service Sync Monitoring**: Alert on status discrepancies

### 📝 Escalation Process
1. **Level 1**: Run comprehensive diagnostic
2. **Level 2**: Check router registration and dependencies  
3. **Level 3**: Investigate service synchronization
4. **Level 4**: Manual intervention and code fixes 