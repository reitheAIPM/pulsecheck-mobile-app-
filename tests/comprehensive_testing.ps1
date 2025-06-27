# COMPREHENSIVE END-TO-END TESTING SCRIPT
# Tests ALL critical paths: Auth, Database, User Flows, AI Systems

$BASE_URL = "https://pulsecheck-mobile-app-production.up.railway.app"
$TOTAL_TESTS = 0
$PASSED_TESTS = 0
$FAILED_TESTS = @()

function Test-Endpoint {
    param(
        [string]$Name,
        [string]$Url,
        [string]$Method = "GET",
        [string]$Body = $null,
        [hashtable]$Headers = @{},
        [bool]$ShouldFail = $false
    )
    
    $global:TOTAL_TESTS++
    Write-Host "Testing: $Name" -ForegroundColor Yellow
    
    try {
        $params = @{
            Uri = $Url
            Method = $Method
            TimeoutSec = 15
            Headers = $Headers
        }
        
        if ($Body) {
            $params.Body = $Body
            $params.ContentType = "application/json"
        }
        
        $response = Invoke-WebRequest @params -ErrorAction Stop
        
        if ($ShouldFail) {
            Write-Host "  ❌ UNEXPECTED SUCCESS (should have failed)" -ForegroundColor Red
            $global:FAILED_TESTS += "$Name - Should have failed but succeeded"
            return $false
        } else {
            Write-Host "  ✅ SUCCESS ($($response.StatusCode))" -ForegroundColor Green
            $global:PASSED_TESTS++
            return $true
        }
    }
    catch {
        if ($ShouldFail) {
            Write-Host "  ✅ EXPECTED FAILURE ($($_.Exception.Response.StatusCode))" -ForegroundColor Green
            $global:PASSED_TESTS++
            return $true
        } else {
            Write-Host "  ❌ FAILED - $($_.Exception.Message)" -ForegroundColor Red
            $global:FAILED_TESTS += "$Name - $($_.Exception.Message)"
            return $false
        }
    }
}

Write-Host "🧪 COMPREHENSIVE PULSECHECK TESTING" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan
Write-Host "Testing Date: $(Get-Date)" -ForegroundColor Gray
Write-Host "Target: $BASE_URL" -ForegroundColor Gray
Write-Host ""

# PHASE 1: BASIC INFRASTRUCTURE
Write-Host "📡 PHASE 1: Infrastructure Health" -ForegroundColor Magenta
Write-Host "=================================" -ForegroundColor Magenta

Test-Endpoint -Name "Backend Health Check" -Url "$BASE_URL/health"
Test-Endpoint -Name "Root Endpoint" -Url "$BASE_URL/"
Test-Endpoint -Name "API Status" -Url "$BASE_URL/api/status"

# PHASE 2: AUTHENTICATION SYSTEM
Write-Host "`n🔐 PHASE 2: Authentication Testing" -ForegroundColor Magenta
Write-Host "==================================" -ForegroundColor Magenta

# Test auth endpoints (should fail without credentials)
Test-Endpoint -Name "Auth Me (No Token)" -Url "$BASE_URL/api/v1/auth/me" -ShouldFail $true
Test-Endpoint -Name "Auth Profile (No Token)" -Url "$BASE_URL/api/v1/auth/profile" -ShouldFail $true

# Test invalid auth
$invalidHeaders = @{"Authorization" = "Bearer invalid_token_12345"}
Test-Endpoint -Name "Auth Me (Invalid Token)" -Url "$BASE_URL/api/v1/auth/me" -Headers $invalidHeaders -ShouldFail $true

# Test auth signin endpoint (should accept request but fail auth)
$authBody = @{
    email = "test@example.com"
    password = "invalid_password"
} | ConvertTo-Json

Test-Endpoint -Name "Auth Signin (Invalid Creds)" -Url "$BASE_URL/api/v1/auth/signin" -Method "POST" -Body $authBody -ShouldFail $true

# PHASE 3: CORE JOURNAL FUNCTIONALITY  
Write-Host "`n📔 PHASE 3: Journal System Testing" -ForegroundColor Magenta
Write-Host "==================================" -ForegroundColor Magenta

# These should fail due to authentication requirements
Test-Endpoint -Name "Journal Entries (No Auth)" -Url "$BASE_URL/api/v1/journal/entries" -ShouldFail $true
Test-Endpoint -Name "Journal Stats (No Auth)" -Url "$BASE_URL/api/v1/journal/stats" -ShouldFail $true

# Test with mock headers (development fallback)
$mockHeaders = @{
    "X-User-Id" = "test_user_123"
    "Content-Type" = "application/json"
}

Test-Endpoint -Name "Journal Stats (Mock User)" -Url "$BASE_URL/api/v1/journal/stats" -Headers $mockHeaders
Test-Endpoint -Name "Journal Entries (Mock User)" -Url "$BASE_URL/api/v1/journal/entries" -Headers $mockHeaders

# PHASE 4: AI SYSTEM TESTING
Write-Host "`n🤖 PHASE 4: AI System Testing" -ForegroundColor Magenta
Write-Host "=============================" -ForegroundColor Magenta

Test-Endpoint -Name "AI Insights Comprehensive" -Url "$BASE_URL/api/v1/debug/ai-insights/comprehensive"
Test-Endpoint -Name "AI Failure Analysis" -Url "$BASE_URL/api/v1/debug/failure-points/analysis"
Test-Endpoint -Name "AI Risk Assessment" -Url "$BASE_URL/api/v1/debug/risk-analysis/current"
Test-Endpoint -Name "AI Performance Analysis" -Url "$BASE_URL/api/v1/debug/performance/analysis"

# Test AI classification endpoint
$aiTestBody = @{
    content = "I'm feeling stressed about work and need some guidance"
} | ConvertTo-Json

Test-Endpoint -Name "AI Topic Classification" -Url "$BASE_URL/api/v1/journal/ai/topic-classification" -Method "POST" -Body $aiTestBody -Headers $mockHeaders

# PHASE 5: DATABASE TESTING
Write-Host "`n🗄️  PHASE 5: Database System Testing" -ForegroundColor Magenta
Write-Host "===================================" -ForegroundColor Magenta

Test-Endpoint -Name "Database Stats" -Url "$BASE_URL/api/v1/debug/database/stats"
Test-Endpoint -Name "Database Performance" -Url "$BASE_URL/api/v1/debug/database/performance"
Test-Endpoint -Name "RLS Configuration Audit" -Url "$BASE_URL/api/v1/debug/configuration-audit"

# PHASE 6: ADAPTIVE AI SYSTEM
Write-Host "`n🎯 PHASE 6: Adaptive AI Testing" -ForegroundColor Magenta
Write-Host "===============================" -ForegroundColor Magenta

$testUserId = "test_user_123"
Test-Endpoint -Name "AI Preferences Debug" -Url "$BASE_URL/api/v1/adaptive-ai/debug/test-rls/$testUserId"
Test-Endpoint -Name "AI Preferences (No Auth)" -Url "$BASE_URL/api/v1/adaptive-ai/preferences/$testUserId" -ShouldFail $true

# PHASE 7: EDGE CASE TESTING
Write-Host "`n⚡ PHASE 7: Edge Case Testing" -ForegroundColor Magenta
Write-Host "============================" -ForegroundColor Magenta

Test-Endpoint -Name "Edge Testing Comprehensive" -Url "$BASE_URL/api/v1/debug/edge-testing/comprehensive"

# Test malformed requests
Test-Endpoint -Name "Invalid JSON" -Url "$BASE_URL/api/v1/journal/entries" -Method "POST" -Body "invalid json" -ShouldFail $true

# Test non-existent endpoints
Test-Endpoint -Name "Non-existent Endpoint" -Url "$BASE_URL/api/v1/does-not-exist" -ShouldFail $true

# PHASE 8: ADMIN FUNCTIONALITY
Write-Host "`n👑 PHASE 8: Admin System Testing" -ForegroundColor Magenta
Write-Host "===============================" -ForegroundColor Magenta

Test-Endpoint -Name "Admin Stats (No Auth)" -Url "$BASE_URL/api/v1/admin/stats" -ShouldFail $true
Test-Endpoint -Name "Admin Beta Metrics (No Auth)" -Url "$BASE_URL/api/v1/admin/beta-metrics/health" -ShouldFail $true

# PHASE 9: MONITORING & DEBUG
Write-Host "`n📊 PHASE 9: Monitoring Systems" -ForegroundColor Magenta
Write-Host "==============================" -ForegroundColor Magenta

Test-Endpoint -Name "Debug Summary" -Url "$BASE_URL/api/v1/debug/summary"
Test-Endpoint -Name "Debug Requests" -Url "$BASE_URL/api/v1/debug/requests"
Test-Endpoint -Name "Live Stream Debug" -Url "$BASE_URL/api/v1/debug/live/stream"
Test-Endpoint -Name "Monitoring Errors" -Url "$BASE_URL/monitoring/errors"

# FINAL RESULTS
Write-Host "`n🎯 COMPREHENSIVE TEST RESULTS" -ForegroundColor Green
Write-Host "=============================" -ForegroundColor Green
Write-Host "Total Tests: $TOTAL_TESTS" -ForegroundColor White
Write-Host "Passed: $PASSED_TESTS" -ForegroundColor Green
Write-Host "Failed: $($TOTAL_TESTS - $PASSED_TESTS)" -ForegroundColor Red

$successRate = [math]::Round(($PASSED_TESTS / $TOTAL_TESTS) * 100, 1)
Write-Host "Success Rate: $successRate%" -ForegroundColor $(if ($successRate -gt 80) { "Green" } elseif ($successRate -gt 60) { "Yellow" } else { "Red" })

if ($FAILED_TESTS.Count -gt 0) {
    Write-Host "`n❌ Failed Tests:" -ForegroundColor Red
    foreach ($failure in $FAILED_TESTS) {
        Write-Host "  - $failure" -ForegroundColor Red
    }
}

Write-Host "`n📋 Testing Analysis:" -ForegroundColor Cyan
if ($successRate -gt 90) {
    Write-Host "🎉 EXCELLENT - System is highly stable" -ForegroundColor Green
} elseif ($successRate -gt 80) {
    Write-Host "✅ GOOD - System is mostly functional with minor issues" -ForegroundColor Green
} elseif ($successRate -gt 60) {
    Write-Host "⚠️  CONCERNING - Multiple issues detected" -ForegroundColor Yellow
} else {
    Write-Host "🚨 CRITICAL - Major system problems detected" -ForegroundColor Red
}

Write-Host "`nTesting completed at $(Get-Date)" -ForegroundColor Gray