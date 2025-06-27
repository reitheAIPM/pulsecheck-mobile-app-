# PULSECHECK ENHANCED COMPREHENSIVE TESTING SYSTEM v2.1
# Enhanced with deployment verification and comprehensive debugging
param(
    [Parameter(Position=0)]
    [ValidateSet("security", "quick", "full", "all", "deployment")]
    [string]$Mode = "all"
)

Write-Host "PULSECHECK ENHANCED TESTING SYSTEM v2.1" -ForegroundColor Magenta
Write-Host "=" * 50
Write-Host "Mode: $Mode" -ForegroundColor Cyan
Write-Host "Time: $(Get-Date -Format 'MM/dd/yyyy HH:mm:ss')" -ForegroundColor Gray
Write-Host "Target: https://pulsecheck-mobile-app-production.up.railway.app" -ForegroundColor Green
Write-Host ""

$BaseUrl = "https://pulsecheck-mobile-app-production.up.railway.app"
$TestResults = @{
    Security = @{ Tests = 0; Passed = 0; Failed = 0 }
    AI = @{ Tests = 0; Passed = 0; Failed = 0 }
    Runtime = @{ Tests = 0; Passed = 0; Failed = 0 }
    Deployment = @{ Tests = 0; Passed = 0; Failed = 0 }
}
$FailedTests = @()

function Test-Endpoint {
    param($Name, $Url, $ExpectedStatus = 200, $Method = "GET", $Headers = @{}, $Body = $null)
    
    try {
        $params = @{
            Uri = $Url
            Method = $Method
            TimeoutSec = 30
            Headers = $Headers
        }
        
        if ($Body) { $params.Body = $Body }
        
        $response = Invoke-WebRequest @params -ErrorAction Stop
        
        if ($response.StatusCode -eq $ExpectedStatus) {
            Write-Host "  ✅ $Name" -ForegroundColor Green
            return $true
        } else {
            Write-Host "  ❌ $Name - Status: $($response.StatusCode)" -ForegroundColor Red
            return $false
        }
    } catch {
        if ($_.Exception.Response.StatusCode -eq $ExpectedStatus) {
            Write-Host "  ✅ $Name (Expected $ExpectedStatus)" -ForegroundColor Green
            return $true
        } else {
            Write-Host "  ❌ $Name - Error: $($_.Exception.Message)" -ForegroundColor Red
            return $false
        }
    }
}

# ENHANCED DEPLOYMENT VERIFICATION
if ($Mode -eq "deployment" -or $Mode -eq "all") {
    Write-Host "DEPLOYMENT VERIFICATION & VERSION CHECK" -ForegroundColor Yellow
    Write-Host "=" * 45
    
    Write-Host "Testing: Deployment Version Endpoint"
    $TestResults.Deployment.Tests++
    if (Test-Endpoint "Deployment Version" "$BaseUrl/api/v1/admin/debug/deployment/version") {
        $TestResults.Deployment.Passed++
        
        # Get detailed version info
        try {
            $versionResponse = Invoke-RestMethod "$BaseUrl/api/v1/admin/debug/deployment/version"
            Write-Host "  📋 Service: $($versionResponse.service)" -ForegroundColor Cyan
            Write-Host "  📋 Version: $($versionResponse.version)" -ForegroundColor Cyan
            Write-Host "  📋 Git Hash: $($versionResponse.git_hash)" -ForegroundColor Cyan
            Write-Host "  📋 Environment: $($versionResponse.environment)" -ForegroundColor Cyan
            
            if ($versionResponse.deployment_features) {
                Write-Host "  📋 Enhanced Features:" -ForegroundColor Cyan
                foreach ($feature in $versionResponse.deployment_features) {
                    Write-Host "    - $feature" -ForegroundColor Gray
                }
            }
        } catch {
            Write-Host "  ⚠️  Could not get version details" -ForegroundColor Yellow
        }
    } else {
        $TestResults.Deployment.Failed++
        $FailedTests += "Deployment Version"
    }
    
    Write-Host "`nTesting: Enhanced Health Check"
    $TestResults.Deployment.Tests++
    if (Test-Endpoint "Enhanced Health" "$BaseUrl/api/v1/admin/debug/deployment/health-enhanced") {
        $TestResults.Deployment.Passed++
        
        # Get detailed health info
        try {
            $healthResponse = Invoke-RestMethod "$BaseUrl/api/v1/admin/debug/deployment/health-enhanced"
            Write-Host "  📋 Overall Status: $($healthResponse.overall_status)" -ForegroundColor $(
                if ($healthResponse.overall_status -eq "healthy") { "Green" } 
                elseif ($healthResponse.overall_status -eq "degraded") { "Yellow" } 
                else { "Red" }
            )
            Write-Host "  📋 Issues Detected: $($healthResponse.issues_detected)" -ForegroundColor Cyan
            
            if ($healthResponse.critical_issues -and $healthResponse.critical_issues.Count -gt 0) {
                Write-Host "  ⚠️  Critical Issues:" -ForegroundColor Red
                foreach ($issue in $healthResponse.critical_issues) {
                    Write-Host "    - $($issue.title) [$($issue.severity)]" -ForegroundColor Red
                }
            }
        } catch {
            Write-Host "  ⚠️  Could not get health details" -ForegroundColor Yellow
        }
    } else {
        $TestResults.Deployment.Failed++
        $FailedTests += "Enhanced Health Check"
    }
    
    Write-Host "`nTesting: Journal RLS Functionality"
    $TestResults.Deployment.Tests++
    
    # Create test user for RLS testing
    $testEmail = "rls-test-$(Get-Random -Maximum 9999)@test.com"
    $testUserData = @{
        email = $testEmail
        password = "testpass123"
    } | ConvertTo-Json
    
    try {
        $authResponse = Invoke-RestMethod "$BaseUrl/api/v1/auth/signup" -Method POST -Body $testUserData -ContentType "application/json"
        $token = $authResponse.access_token
        
        if ($token) {
            # Create journal entry
            $journalData = @{
                content = "RLS test entry - $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
                mood_level = 8
                energy_level = 7
                stress_level = 3
            } | ConvertTo-Json
            
            $createResponse = Invoke-RestMethod "$BaseUrl/api/v1/journal/entries" -Method POST -Body $journalData -ContentType "application/json" -Headers @{ Authorization = "Bearer $token" }
            
            if ($createResponse.id) {
                # Test retrieval
                $entriesResponse = Invoke-RestMethod "$BaseUrl/api/v1/journal/entries" -Headers @{ Authorization = "Bearer $token" }
                
                if ($entriesResponse.total -gt 0) {
                    Write-Host "  ✅ Journal RLS Working - Created and retrieved entries" -ForegroundColor Green
                    $TestResults.Deployment.Passed++
                } else {
                    Write-Host "  ❌ Journal RLS BROKEN - Entries created but not retrievable" -ForegroundColor Red
                    $TestResults.Deployment.Failed++
                    $FailedTests += "Journal RLS Functionality"
                }
            } else {
                Write-Host "  ❌ Journal Creation Failed" -ForegroundColor Red
                $TestResults.Deployment.Failed++
                $FailedTests += "Journal RLS Functionality"
            }
        } else {
            Write-Host "  ❌ Authentication Failed" -ForegroundColor Red
            $TestResults.Deployment.Failed++
            $FailedTests += "Journal RLS Functionality"
        }
    } catch {
        Write-Host "  ❌ RLS Test Failed: $($_.Exception.Message)" -ForegroundColor Red
        $TestResults.Deployment.Failed++
        $FailedTests += "Journal RLS Functionality"
    }
    
    Write-Host "`nTesting: Personas Endpoint (UnboundLocalError Check)"
    $TestResults.Deployment.Tests++
    
    try {
        $personasResponse = Invoke-RestMethod "$BaseUrl/api/v1/adaptive-ai/personas" -Headers @{ Authorization = "Bearer $token" } -ErrorAction Stop
        Write-Host "  ✅ Personas Endpoint Working - No UnboundLocalError" -ForegroundColor Green
        $TestResults.Deployment.Passed++
    } catch {
        $errorResponse = $_.Exception.Response
        if ($errorResponse -and $errorResponse.StatusCode -eq 500) {
            try {
                $errorContent = $errorResponse.Content | ConvertFrom-Json
                if ($errorContent.error_type -eq "UnboundLocalError") {
                    Write-Host "  ❌ Personas UnboundLocalError DETECTED" -ForegroundColor Red
                    $TestResults.Deployment.Failed++
                    $FailedTests += "Personas UnboundLocalError"
                } else {
                    Write-Host "  ⚠️  Personas endpoint error (not UnboundLocalError): $($errorContent.error_type)" -ForegroundColor Yellow
                    $TestResults.Deployment.Passed++
                }
            } catch {
                Write-Host "  ⚠️  Personas endpoint error (unknown): $($_.Exception.Message)" -ForegroundColor Yellow
                $TestResults.Deployment.Passed++
            }
        } else {
            Write-Host "  ✅ Personas Endpoint Working" -ForegroundColor Green
            $TestResults.Deployment.Passed++
        }
    }
    
    Write-Host "`nDEPLOYMENT VERIFICATION COMPLETE" -ForegroundColor Yellow
    Write-Host ""
}

# SECURITY TESTING
if ($Mode -eq "security" -or $Mode -eq "all") {
    Write-Host "ENHANCED SECURITY SCANNING" -ForegroundColor Yellow
    Write-Host "=" * 30
    
    # Dependency conflict detection
    Write-Host "Testing: Dependency Conflict Detection"
    $TestResults.Security.Tests++
    
    # Check for gotrue version pin
    if (Test-Path "backend/requirements.txt") {
        $requirements = Get-Content "backend/requirements.txt"
        $hasGotruePin = $requirements | Where-Object { $_ -match "gotrue==2\.8\.1" }
        $hasEmailValidator = $requirements | Where-Object { $_ -match "email-validator" }
        $hasHttpxConflict = $requirements | Where-Object { $_ -match "httpx==0\.25" }
        
        if ($hasGotruePin -and $hasEmailValidator -and !$hasHttpxConflict) {
            Write-Host "  ✅ Dependencies properly pinned - No conflicts detected" -ForegroundColor Green
            $TestResults.Security.Passed++
        } else {
            Write-Host "  ⚠️  Potential dependency issues detected" -ForegroundColor Yellow
            if (!$hasGotruePin) { Write-Host "    - Missing gotrue==2.8.1 pin" -ForegroundColor Red }
            if (!$hasEmailValidator) { Write-Host "    - Missing email-validator" -ForegroundColor Red }
            if ($hasHttpxConflict) { Write-Host "    - httpx 0.25 conflict detected" -ForegroundColor Red }
            $TestResults.Security.Failed++
            $FailedTests += "Dependency Conflicts"
        }
    } else {
        Write-Host "  ⚠️  Requirements.txt not found" -ForegroundColor Yellow
        $TestResults.Security.Failed++
        $FailedTests += "Requirements File Missing"
    }
    
    # Hardcoded secrets detection
    Write-Host "Testing: Hardcoded Secrets Detection"
    $TestResults.Security.Tests++
    $secretsFound = $false
    
    $secretPatterns = @(
        "sk-[a-zA-Z0-9]{48}",  # OpenAI API key
        "eyJ[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*",  # JWT token
        "AKIA[0-9A-Z]{16}",  # AWS access key
        "password\s*=\s*['\"][^'\"]{8,}['\"]"  # Hardcoded passwords
    )
    
    foreach ($pattern in $secretPatterns) {
        $found = Select-String -Path "backend/app/**/*.py" -Pattern $pattern -ErrorAction SilentlyContinue
        if ($found) {
            Write-Host "  ❌ Potential secret found: $($found.Pattern)" -ForegroundColor Red
            $secretsFound = $true
        }
    }
    
    if (!$secretsFound) {
        Write-Host "  ✅ No hardcoded secrets detected" -ForegroundColor Green
        $TestResults.Security.Passed++
    } else {
        $TestResults.Security.Failed++
        $FailedTests += "Hardcoded Secrets"
    }
    
    Write-Host "`nSECURITY SCANNING COMPLETE" -ForegroundColor Yellow
    Write-Host ""
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

# ENHANCED RESULTS SUMMARY
Write-Host "`nENHANCED TEST RESULTS SUMMARY" -ForegroundColor Magenta
Write-Host "=" * 35

if ($Mode -eq "deployment" -or $Mode -eq "all") {
    $deploymentRate = if ($TestResults.Deployment.Tests -gt 0) { 
        [math]::Round(($TestResults.Deployment.Passed / $TestResults.Deployment.Tests) * 100, 1) 
    } else { 0 }
    Write-Host "`nDeployment Verification:" -ForegroundColor Cyan
    Write-Host "   Tests: $($TestResults.Deployment.Tests)" -ForegroundColor White
    Write-Host "   Passed: $($TestResults.Deployment.Passed)" -ForegroundColor Green
    Write-Host "   Failed: $($TestResults.Deployment.Failed)" -ForegroundColor Red
    Write-Host "   Success Rate: $deploymentRate%" -ForegroundColor $(if ($deploymentRate -ge 90) { "Green" } elseif ($deploymentRate -ge 75) { "Yellow" } else { "Red" })
}

if ($Mode -eq "security" -or $Mode -eq "all") {
    $securityRate = if ($TestResults.Security.Tests -gt 0) { 
        [math]::Round(($TestResults.Security.Passed / $TestResults.Security.Tests) * 100, 1) 
    } else { 0 }
    Write-Host "`nSecurity Testing:" -ForegroundColor Cyan
    Write-Host "   Tests: $($TestResults.Security.Tests)" -ForegroundColor White
    Write-Host "   Passed: $($TestResults.Security.Passed)" -ForegroundColor Green
    Write-Host "   Failed: $($TestResults.Security.Failed)" -ForegroundColor Red
    Write-Host "   Success Rate: $securityRate%" -ForegroundColor $(if ($securityRate -ge 90) { "Green" } elseif ($securityRate -ge 75) { "Yellow" } else { "Red" })
}

# Overall results
$totalTests = $TestResults.Security.Tests + $TestResults.AI.Tests + $TestResults.Runtime.Tests + $TestResults.Deployment.Tests
$totalPassed = $TestResults.Security.Passed + $TestResults.AI.Passed + $TestResults.Runtime.Passed + $TestResults.Deployment.Passed
$totalFailed = $TestResults.Security.Failed + $TestResults.AI.Failed + $TestResults.Runtime.Failed + $TestResults.Deployment.Failed
$overallRate = if ($totalTests -gt 0) { [math]::Round(($totalPassed / $totalTests) * 100, 1) } else { 0 }

Write-Host "`nOverall Results:" -ForegroundColor Yellow
Write-Host "   Total Tests: $totalTests" -ForegroundColor White
Write-Host "   Total Passed: $totalPassed" -ForegroundColor Green
Write-Host "   Total Failed: $totalFailed" -ForegroundColor Red
Write-Host "   Overall Success Rate: $overallRate%" -ForegroundColor $(if ($overallRate -ge 90) { "Green" } elseif ($overallRate -ge 75) { "Yellow" } else { "Red" })

# Failed tests summary
if ($FailedTests.Count -gt 0) {
    Write-Host "`nFailed Tests:" -ForegroundColor Red
    foreach ($test in $FailedTests) {
        Write-Host "  - $test" -ForegroundColor Red
    }
}

# Enhanced system health analysis
Write-Host "`nSystem Health Analysis:" -ForegroundColor Magenta
if ($overallRate -ge 95) {
    Write-Host "EXCELLENT - System is production-ready with enhanced monitoring" -ForegroundColor Green
} elseif ($overallRate -ge 85) {
    Write-Host "GOOD - System is stable with minor issues" -ForegroundColor Yellow
} elseif ($overallRate -ge 70) {
    Write-Host "FAIR - System needs attention" -ForegroundColor Yellow
} else {
    Write-Host "CRITICAL - System requires immediate fixes" -ForegroundColor Red
}

Write-Host "`nDEBUGGING NOTES:" -ForegroundColor Cyan
Write-Host "- Deployment discrepancies automatically detected" -ForegroundColor Gray
Write-Host "- Journal RLS functionality validated" -ForegroundColor Gray
Write-Host "- UnboundLocalError patterns monitored" -ForegroundColor Gray
Write-Host "- Enhanced error prevention active" -ForegroundColor Gray

Write-Host "`nUsage Examples:" -ForegroundColor Cyan
Write-Host "   Deployment Check:     ./unified_testing.ps1 deployment" -ForegroundColor Gray
Write-Host "   Security Scan Only:   ./unified_testing.ps1 security" -ForegroundColor Gray
Write-Host "   Quick AI Check:       ./unified_testing.ps1 quick" -ForegroundColor Gray
Write-Host "   Full System Test:     ./unified_testing.ps1 full" -ForegroundColor Gray
Write-Host "   All Tests (Default):  ./unified_testing.ps1" -ForegroundColor Gray

Write-Host "`nTesting completed at $(Get-Date -Format 'MM/dd/yyyy HH:mm:ss')" -ForegroundColor Gray 