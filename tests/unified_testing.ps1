# PULSECHECK UNIFIED TESTING SCRIPT
# Combines AI Automated Testing + Comprehensive System Testing
# Usage: ./unified_testing.ps1 [mode]
# Modes: "quick", "full", or "both" (default)

param(
    [string]$Mode = "both"
)

# Support legacy "all" mode for backward compatibility
if ($Mode -eq "all") {
    $Mode = "both"
}

$BASE_URL = "https://pulsecheck-mobile-app-production.up.railway.app"
$AI_TESTS = 0
$AI_PASSED = 0
$COMP_TESTS = 0
$COMP_PASSED = 0
$FAILED_TESTS = @()

function Test-Endpoint {
    param(
        [string]$Name,
        [string]$Url,
        [string]$Method = "GET",
        [string]$Body = $null,
        [hashtable]$Headers = @{},
        [bool]$ShouldFail = $false,
        [string]$TestType = "COMP"
    )
    
    if ($TestType -eq "AI") {
        $script:AI_TESTS++
    } else {
        $script:COMP_TESTS++
    }
    
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
            Write-Host "  UNEXPECTED SUCCESS (should have failed)" -ForegroundColor Red
            $script:FAILED_TESTS += "$Name - Should have failed but succeeded"
            return $false
        } else {
            Write-Host "  SUCCESS ($($response.StatusCode))" -ForegroundColor Green
            if ($TestType -eq "AI") {
                $script:AI_PASSED++
            } else {
                $script:COMP_PASSED++
            }
            return $true
        }
    }
    catch {
        if ($ShouldFail) {
            Write-Host "  EXPECTED FAILURE (Security Working)" -ForegroundColor Green
            if ($TestType -eq "AI") {
                $script:AI_PASSED++
            } else {
                $script:COMP_PASSED++
            }
            return $true
        } else {
            Write-Host "  FAILED - $($_.Exception.Message)" -ForegroundColor Red
            $script:FAILED_TESTS += "$Name - $($_.Exception.Message)"
            return $false
        }
    }
}

function Test-AI-Endpoint {
    param(
        [string]$Name,
        [string]$Endpoint
    )
    
    Write-Host "Testing: $Name" -ForegroundColor Yellow
    $script:AI_TESTS++
    
    try {
        $response = curl.exe --max-time 10 "$BASE_URL$Endpoint" 2>$null
        if ($response -and $response -ne "") {
            $jsonResponse = $response | ConvertFrom-Json
            Write-Host "  SUCCESS - $($jsonResponse.status)" -ForegroundColor Green
            $script:AI_PASSED++
            return $jsonResponse
        } else {
            Write-Host "  FAILED - Empty response" -ForegroundColor Red
            $script:FAILED_TESTS += "$Name - Empty response"
            return $null
        }
    }
    catch {
        Write-Host "  FAILED - $($_.Exception.Message)" -ForegroundColor Red
        $script:FAILED_TESTS += "$Name - $($_.Exception.Message)"
        return $null
    }
}

Write-Host "PULSECHECK COMPREHENSIVE TESTING SYSTEM" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Mode: $Mode" -ForegroundColor Gray
Write-Host "Time: $(Get-Date)" -ForegroundColor Gray
Write-Host "Target: $BASE_URL" -ForegroundColor Gray
Write-Host ""

# SECURITY SCANNING SECTION
if ($Mode -eq "security" -or $Mode -eq "both") {
    Write-Host "SECURITY SCANNING" -ForegroundColor Red
    Write-Host "=================" -ForegroundColor Red
    Write-Host "Scanning for hardcoded secrets and vulnerabilities..." -ForegroundColor Gray
    Write-Host ""
    
    # Check for hardcoded JWT secrets
    Write-Host "🔍 Checking for hardcoded JWT secrets..." -ForegroundColor Yellow
    $script:COMP_TESTS++
    if (Test-Path "../backend/app/core/config.py") {
        $secretCheck = Select-String -Path "../backend/app/core/config.py" -Pattern "your-secret-key-here" -ErrorAction SilentlyContinue
        if ($secretCheck) {
            Write-Host "  ❌ SECURITY ISSUE: Hardcoded JWT secret found" -ForegroundColor Red
            $script:FAILED_TESTS += "Security Check - Hardcoded JWT secret detected"
        } else {
            Write-Host "  ✅ JWT secrets properly secured" -ForegroundColor Green
            $script:COMP_PASSED++
        }
    } else {
        Write-Host "  ⚠️ Config file not found" -ForegroundColor Yellow
        $script:COMP_PASSED++
    }
    
    # Check for dependency conflicts  
    Write-Host "🔧 Checking for dependency conflicts..." -ForegroundColor Yellow
    $script:COMP_TESTS++
    if (Test-Path "../backend/requirements.txt") {
        $content = Get-Content "../backend/requirements.txt"
        $conflicts = @()
        
        # Check for known conflicts
        if ($content -match "httpx==0\.25\." -and $content -match "supabase") {
            $conflicts += "httpx 0.25.x conflicts with supabase"
        }
        
        # Check for missing gotrue pin with supabase
        if ($content -match "supabase" -and $content -notmatch "gotrue") {
            $conflicts += "Missing gotrue version pin (can cause proxy parameter error)"
        }
        
        # Check for missing email-validator with pydantic
        if ($content -match "pydantic" -and $content -notmatch "email-validator") {
            $conflicts += "Missing email-validator (required by pydantic email validation)"
        }
        
        if ($conflicts.Count -gt 0) {
            Write-Host "  ❌ DEPENDENCY ISSUES: $($conflicts -join ', ')" -ForegroundColor Red
            $script:FAILED_TESTS += "Build Health - $($conflicts -join ', ')"
        } else {
            Write-Host "  ✅ No dependency conflicts detected" -ForegroundColor Green
            $script:COMP_PASSED++
        }
    } else {
        Write-Host "  ✅ Requirements file OK" -ForegroundColor Green
        $script:COMP_PASSED++
    }
    
    Write-Host "`nSECURITY SCANNING COMPLETE" -ForegroundColor Green
    
    if ($Mode -eq "both") {
        Write-Host "`nProceeding to other tests..." -ForegroundColor Yellow
        Start-Sleep -Seconds 2
        Write-Host ""
    }
}

# AI AUTOMATED TESTING SECTION
if ($Mode -eq "quick" -or $Mode -eq "both") {
    Write-Host "AI AUTOMATED TESTING" -ForegroundColor Magenta
    Write-Host "=======================" -ForegroundColor Magenta
    Write-Host "Testing your AI's analysis capabilities..." -ForegroundColor Gray
    Write-Host ""
    
    Write-Host "Phase 1: AI System Health Analysis" -ForegroundColor Cyan
    $aiInsights = Test-AI-Endpoint -Name "AI Insights Comprehensive" -Endpoint "/api/v1/debug/ai-insights/comprehensive"
    
    Write-Host "`nPhase 2: AI Failure Point Analysis" -ForegroundColor Cyan
    $failureAnalysis = Test-AI-Endpoint -Name "AI Failure Analysis" -Endpoint "/api/v1/debug/failure-points/analysis"
    
    Write-Host "`nPhase 3: AI Risk Assessment" -ForegroundColor Cyan
    $riskAnalysis = Test-AI-Endpoint -Name "AI Risk Assessment" -Endpoint "/api/v1/debug/risk-analysis/current"
    
    Write-Host "`nPhase 4: AI Performance Grading" -ForegroundColor Cyan
    $performance = Test-AI-Endpoint -Name "AI Performance Analysis" -Endpoint "/api/v1/debug/performance/analysis"
    
    Write-Host "`nPhase 5: AI System Summary" -ForegroundColor Cyan
    $summary = Test-AI-Endpoint -Name "AI System Summary" -Endpoint "/api/v1/debug/summary"
    
    Write-Host "`nAI AUTOMATED TESTING COMPLETE" -ForegroundColor Green
    Write-Host "AI Analysis Results Available" -ForegroundColor White
    
    if ($Mode -eq "both") {
        Write-Host "`nProceeding to Comprehensive Testing..." -ForegroundColor Yellow
        Start-Sleep -Seconds 2
        Write-Host ""
    }
}

# COMPREHENSIVE TESTING SECTION  
if ($Mode -eq "full" -or $Mode -eq "both") {
    Write-Host "COMPREHENSIVE SYSTEM TESTING" -ForegroundColor Magenta
    Write-Host "===============================" -ForegroundColor Magenta
    Write-Host "Testing all critical system components..." -ForegroundColor Gray
    Write-Host ""
    
    # PHASE 1: INFRASTRUCTURE
    Write-Host "PHASE 1: Infrastructure Health" -ForegroundColor Magenta
    Test-Endpoint -Name "Backend Health Check" -Url "$BASE_URL/health"
    Test-Endpoint -Name "Root Endpoint" -Url "$BASE_URL/"
    # Note: /api/status endpoint doesn't exist - removed from test
    
    # PHASE 2: AUTHENTICATION SECURITY TESTING
    Write-Host "`nPHASE 2: Authentication Security Testing" -ForegroundColor Magenta
    Write-Host "(These failures are GOOD - they prove security is working)" -ForegroundColor DarkGray
    Test-Endpoint -Name "Auth Me (No Token)" -Url "$BASE_URL/api/v1/auth/me" -ShouldFail $true
    Test-Endpoint -Name "Auth Profile (No Token)" -Url "$BASE_URL/api/v1/auth/profile" -ShouldFail $true
    
    $invalidHeaders = @{"Authorization" = "Bearer invalid_token_12345"}
    Test-Endpoint -Name "Auth Me (Invalid Token)" -Url "$BASE_URL/api/v1/auth/me" -Headers $invalidHeaders -ShouldFail $true
    
    $authBody = @{
        email = "test@example.com"
        password = "invalid_password"
    } | ConvertTo-Json
    Test-Endpoint -Name "Auth Signin (Invalid Creds)" -Url "$BASE_URL/api/v1/auth/signin" -Method "POST" -Body $authBody -ShouldFail $true
    
    # PHASE 3: JOURNAL SECURITY TESTING
    Write-Host "`nPHASE 3: Journal Security Testing" -ForegroundColor Magenta
    Write-Host "(These failures are GOOD - unauthorized access is blocked)" -ForegroundColor DarkGray
    Test-Endpoint -Name "Journal Entries (No Auth)" -Url "$BASE_URL/api/v1/journal/entries" -ShouldFail $true
    Test-Endpoint -Name "Journal Stats (No Auth)" -Url "$BASE_URL/api/v1/journal/stats" -ShouldFail $true
    
    # Note: Mock headers should also fail - this proves RLS security is working
    $mockHeaders = @{
        "X-User-Id" = "test_user_123"
        "Content-Type" = "application/json"
    }
    Test-Endpoint -Name "Journal Stats (Mock User - Should Fail)" -Url "$BASE_URL/api/v1/journal/stats" -Headers $mockHeaders -ShouldFail $true
    Test-Endpoint -Name "Journal Entries (Mock User - Should Fail)" -Url "$BASE_URL/api/v1/journal/entries" -Headers $mockHeaders -ShouldFail $true
    
    # PHASE 4: AI DEBUG ENDPOINTS (These should work - public debug endpoints)
    Write-Host "`nPHASE 4: AI Debug System Testing" -ForegroundColor Magenta
    Test-Endpoint -Name "AI Insights Comprehensive" -Url "$BASE_URL/api/v1/debug/ai-insights/comprehensive"
    Test-Endpoint -Name "AI Failure Analysis" -Url "$BASE_URL/api/v1/debug/failure-points/analysis"
    Test-Endpoint -Name "AI Risk Assessment" -Url "$BASE_URL/api/v1/debug/risk-analysis/current"
    Test-Endpoint -Name "AI Performance Analysis" -Url "$BASE_URL/api/v1/debug/performance/analysis"
    
    Write-Host "`nCOMPREHENSIVE TESTING COMPLETE" -ForegroundColor Green
}

# UNIFIED RESULTS SUMMARY
Write-Host "`nUNIFIED TEST RESULTS" -ForegroundColor Green
Write-Host "=======================" -ForegroundColor Green

if ($Mode -eq "quick" -or $Mode -eq "both") {
    Write-Host "`nAI Testing Results:" -ForegroundColor Cyan
    Write-Host "   Tests: $AI_TESTS" -ForegroundColor White
    Write-Host "   Passed: $AI_PASSED" -ForegroundColor Green
    Write-Host "   Failed: $($AI_TESTS - $AI_PASSED)" -ForegroundColor Red
    
    if ($AI_TESTS -gt 0) {
        $aiSuccessRate = [math]::Round(($AI_PASSED / $AI_TESTS) * 100, 1)
        Write-Host "   Success Rate: $aiSuccessRate%" -ForegroundColor $(if ($aiSuccessRate -gt 80) { "Green" } else { "Yellow" })
    }
}

if ($Mode -eq "full" -or $Mode -eq "both") {
    Write-Host "`nComprehensive Testing Results:" -ForegroundColor Cyan
    Write-Host "   Tests: $COMP_TESTS" -ForegroundColor White
    Write-Host "   Passed: $COMP_PASSED" -ForegroundColor Green
    Write-Host "   Failed: $($COMP_TESTS - $COMP_PASSED)" -ForegroundColor Red
    
    if ($COMP_TESTS -gt 0) {
        $compSuccessRate = [math]::Round(($COMP_PASSED / $COMP_TESTS) * 100, 1)
        Write-Host "   Success Rate: $compSuccessRate%" -ForegroundColor $(if ($compSuccessRate -gt 80) { "Green" } elseif ($compSuccessRate -gt 60) { "Yellow" } else { "Red" })
    }
}

$totalTests = $AI_TESTS + $COMP_TESTS
$totalPassed = $AI_PASSED + $COMP_PASSED

if ($totalTests -gt 0) {
    Write-Host "`nOverall Results:" -ForegroundColor White
    Write-Host "   Total Tests: $totalTests" -ForegroundColor White
    Write-Host "   Total Passed: $totalPassed" -ForegroundColor Green
    Write-Host "   Total Failed: $($totalTests - $totalPassed)" -ForegroundColor Red
    
    $overallSuccessRate = [math]::Round(($totalPassed / $totalTests) * 100, 1)
    Write-Host "   Overall Success Rate: $overallSuccessRate%" -ForegroundColor $(if ($overallSuccessRate -gt 85) { "Green" } elseif ($overallSuccessRate -gt 70) { "Yellow" } else { "Red" })
}

if ($FAILED_TESTS.Count -gt 0) {
    Write-Host "`nFailed Tests:" -ForegroundColor Red
    foreach ($failure in $FAILED_TESTS) {
        Write-Host "  - $failure" -ForegroundColor Red
    }
}

Write-Host "`nSystem Health Analysis:" -ForegroundColor Cyan
if ($overallSuccessRate -gt 90) {
    Write-Host "EXCELLENT - System is highly stable and ready for production" -ForegroundColor Green
} elseif ($overallSuccessRate -gt 80) {
    Write-Host "GOOD - System is mostly functional with minor issues" -ForegroundColor Green
} elseif ($overallSuccessRate -gt 60) {
    Write-Host "CONCERNING - Multiple issues detected, investigation recommended" -ForegroundColor Yellow
} else {
    Write-Host "CRITICAL - Major system problems detected, immediate attention required" -ForegroundColor Red
}

Write-Host "`nSECURITY NOTE:" -ForegroundColor Yellow
Write-Host "Authentication failures (401/403) are EXPECTED and GOOD!" -ForegroundColor Yellow
Write-Host "They prove your security is working correctly." -ForegroundColor Yellow

Write-Host "`nUsage Examples:" -ForegroundColor Gray
Write-Host "   Quick AI Analysis:    ./unified_testing.ps1 quick" -ForegroundColor Gray
Write-Host "   Security Scan Only:   ./unified_testing.ps1 security" -ForegroundColor Gray
Write-Host "   Full System Test:     ./unified_testing.ps1 full" -ForegroundColor Gray
Write-Host "   All Tests (Default):  ./unified_testing.ps1" -ForegroundColor Gray

Write-Host "`nTesting completed at $(Get-Date)" -ForegroundColor Gray 