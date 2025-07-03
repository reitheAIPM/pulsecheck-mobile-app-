param(
    [string]$BaseUrl = "https://pulsecheck-mobile-app-production.up.railway.app",
    [switch]$Detailed,
    [switch]$FixIssues
)

Write-Host "🔍 AI SYSTEM HEALTH DIAGNOSTIC" -ForegroundColor Magenta
Write-Host "==============================" -ForegroundColor Magenta
Write-Host "Comprehensive health check of all AI system components" -ForegroundColor Cyan
Write-Host ""

# Global counters
$script:TestsPassed = 0
$script:TestsFailed = 0
$script:WarningsFound = 0
$script:IssuesFixed = 0

function Test-Component {
    param(
        [string]$Name,
        [string]$Url,
        [string]$ExpectedResponse = $null,
        [scriptblock]$ValidationScript = $null,
        [string]$FixAction = $null
    )
    
    Write-Host "Testing: $Name" -ForegroundColor Yellow
    
    try {
        $response = Invoke-RestMethod -Uri "$BaseUrl$Url" -TimeoutSec 10 -ErrorAction Stop
        
        $isValid = $true
        $details = ""
        
        # Run custom validation if provided
        if ($ValidationScript) {
            $validationResult = & $ValidationScript $response
            $isValid = $validationResult.IsValid
            $details = $validationResult.Details
        }
        
        # Check expected response pattern
        if ($ExpectedResponse -and $response -notmatch $ExpectedResponse) {
            $isValid = $false
            $details = "Response doesn't match expected pattern: $ExpectedResponse"
        }
        
        if ($isValid) {
            Write-Host "   ✅ PASSED" -ForegroundColor Green
            if ($details) { Write-Host "   $details" -ForegroundColor Gray }
            $script:TestsPassed++
        } else {
            Write-Host "   ⚠️ WARNING" -ForegroundColor Yellow
            Write-Host "   $details" -ForegroundColor Yellow
            $script:WarningsFound++
            
            # Attempt to fix if requested and fix action provided
            if ($FixIssues -and $FixAction) {
                Write-Host "   🔧 Attempting fix..." -ForegroundColor Cyan
                try {
                    Invoke-Expression $FixAction
                    Write-Host "   ✅ Fix applied" -ForegroundColor Green
                    $script:IssuesFixed++
                } catch {
                    Write-Host "   ❌ Fix failed: $($_.Exception.Message)" -ForegroundColor Red
                }
            }
        }
        
        return @{ Success = $isValid; Response = $response }
        
    } catch {
        Write-Host "   ❌ FAILED: $($_.Exception.Message)" -ForegroundColor Red
        $script:TestsFailed++
        
        # Attempt to fix if it's a 404 (router registration issue)
        if ($_.Exception.Message -match "404" -and $FixIssues) {
            Write-Host "   🔧 Attempting to restart services..." -ForegroundColor Cyan
            # This would trigger a service restart, but we'll just log it for now
            Write-Host "   ⚠️ Router registration issue detected - requires service restart" -ForegroundColor Yellow
        }
        
        return @{ Success = $false; Response = $null }
    }
}

# Test 1: Basic System Health
Write-Host "1️⃣ BASIC SYSTEM HEALTH" -ForegroundColor Cyan
Write-Host "------------------------" -ForegroundColor Cyan

$healthResult = Test-Component -Name "System Health" -Url "/health" -ValidationScript {
    param($response)
    return @{
        IsValid = $response.status -eq "healthy"
        Details = "Status: $($response.status)"
    }
}

# Test 2: Router Registration
Write-Host "`n2️⃣ ROUTER REGISTRATION" -ForegroundColor Cyan
Write-Host "-----------------------" -ForegroundColor Cyan

$routerTests = @(
    @{ Name = "Scheduler Router"; Url = "/api/v1/scheduler/status" },
    @{ Name = "AI Monitoring Router"; Url = "/api/v1/ai-monitoring/last-action/test-user" },
    @{ Name = "Manual AI Router"; Url = "/api/v1/manual-ai/debug-database/test-user" },
    @{ Name = "Adaptive AI Router"; Url = "/api/v1/adaptive-ai/health" }
)

$routerResults = @{}
foreach ($test in $routerTests) {
    $result = Test-Component -Name $test.Name -Url $test.Url
    $routerResults[$test.Name] = $result
}

# Test 3: Service Synchronization
Write-Host "`n3️⃣ SERVICE SYNCHRONIZATION" -ForegroundColor Cyan
Write-Host "---------------------------" -ForegroundColor Cyan

$schedulerResult = Test-Component -Name "Scheduler Status Consistency" -Url "/api/v1/scheduler/status" -ValidationScript {
    param($response)
    
    # Get AI monitoring view of scheduler
    try {
        $monitorResponse = Invoke-RestMethod -Uri "$BaseUrl/api/v1/ai-monitoring/last-action/test-user" -TimeoutSec 5
        
        $directStatus = $response.status -eq "running"
        $monitorStatus = $monitorResponse.scheduler_running
        
        $isConsistent = $directStatus -eq $monitorStatus
        
        return @{
            IsValid = $isConsistent
            Details = "Direct: $directStatus, Monitor: $monitorStatus $(if (-not $isConsistent) { '⚠️ INCONSISTENT' } else { '✅ CONSISTENT' })"
        }
    } catch {
        return @{
            IsValid = $false
            Details = "Unable to compare with monitoring endpoint"
        }
    }
}

# Test 4: Testing Mode Validation
Write-Host "`n4️⃣ TESTING MODE VALIDATION" -ForegroundColor Cyan
Write-Host "---------------------------" -ForegroundColor Cyan

$testingResult = Test-Component -Name "Testing Mode Status" -Url "/api/v1/scheduler/testing/status" -ValidationScript {
    param($response)
    
    $testingEnabled = $response.testing_mode -eq $true
    $schedulerStatus = $response.scheduler_status
    
    return @{
        IsValid = $true  # Testing mode can be on or off
        Details = "Testing Mode: $testingEnabled, Scheduler: $schedulerStatus"
    }
} -FixAction 'Invoke-WebRequest -Uri "$BaseUrl/api/v1/scheduler/testing/enable" -Method POST'

# Test 5: Database Connectivity
Write-Host "`n5️⃣ DATABASE CONNECTIVITY" -ForegroundColor Cyan
Write-Host "-------------------------" -ForegroundColor Cyan

$dbResult = Test-Component -Name "Database Status" -Url "/api/v1/database/comprehensive-status" -ValidationScript {
    param($response)
    
    $dbHealthy = $response.overall_status -eq "healthy"
    
    return @{
        IsValid = $dbHealthy
        Details = "Database: $($response.overall_status), Connection: $($response.connection_status)"
    }
}

# Test 6: AI Flow Validation
Write-Host "`n6️⃣ AI FLOW VALIDATION" -ForegroundColor Cyan
Write-Host "----------------------" -ForegroundColor Cyan

$aiFlowResult = Test-Component -Name "AI Flow Status" -Url "/api/v1/ai-monitoring/last-action/test-user" -ValidationScript {
    param($response)
    
    $flowStatus = $response.ai_flow_status
    $isHealthy = $flowStatus -notin @("monitoring_error", "scheduler_stopped")
    
    return @{
        IsValid = $isHealthy
        Details = "AI Flow: $flowStatus, Expected Response: $($response.expected_response_time)"
    }
}

# COMPREHENSIVE RESULTS
Write-Host "`n📊 DIAGNOSTIC RESULTS" -ForegroundColor Magenta
Write-Host "=====================" -ForegroundColor Magenta

Write-Host "Tests Passed: $script:TestsPassed" -ForegroundColor Green
Write-Host "Tests Failed: $script:TestsFailed" -ForegroundColor Red
Write-Host "Warnings: $script:WarningsFound" -ForegroundColor Yellow
if ($FixIssues) {
    Write-Host "Issues Fixed: $script:IssuesFixed" -ForegroundColor Cyan
}

$totalTests = $script:TestsPassed + $script:TestsFailed + $script:WarningsFound
$successRate = if ($totalTests -gt 0) { [math]::Round(($script:TestsPassed / $totalTests) * 100, 1) } else { 0 }

Write-Host "`nOverall Health Score: $successRate%" -ForegroundColor $(
    if ($successRate -ge 90) { 'Green' }
    elseif ($successRate -ge 70) { 'Yellow' }
    else { 'Red' }
)

# RECOMMENDATIONS
Write-Host "`n🎯 RECOMMENDATIONS" -ForegroundColor Magenta
Write-Host "==================" -ForegroundColor Magenta

if ($script:TestsFailed -gt 0) {
    Write-Host "❌ CRITICAL ISSUES DETECTED" -ForegroundColor Red
    Write-Host "   1. Check router registration" -ForegroundColor Yellow
    Write-Host "   2. Verify all dependencies in requirements.txt" -ForegroundColor Yellow
    Write-Host "   3. Restart Railway service if needed" -ForegroundColor Yellow
}

if ($script:WarningsFound -gt 0) {
    Write-Host "⚠️ WARNINGS FOUND" -ForegroundColor Yellow
    Write-Host "   1. Service synchronization may be inconsistent" -ForegroundColor Gray
    Write-Host "   2. Some services may be in suboptimal state" -ForegroundColor Gray
}

if ($script:TestsPassed -eq $totalTests) {
    Write-Host "✅ ALL SYSTEMS OPERATIONAL" -ForegroundColor Green
    Write-Host "   AI system ready for production use" -ForegroundColor Green
}

# QUICK FIX SUGGESTIONS
if ($script:TestsFailed -gt 0 -or $script:WarningsFound -gt 0) {
    Write-Host "`n🚀 QUICK FIX COMMANDS" -ForegroundColor Magenta
    Write-Host "=====================" -ForegroundColor Magenta
    
    if ($routerResults["Scheduler Router"].Success -eq $false) {
        Write-Host "# Start Scheduler:" -ForegroundColor Yellow
        Write-Host "Invoke-WebRequest -Uri '$BaseUrl/api/v1/scheduler/start' -Method POST" -ForegroundColor White
    }
    
    if ($testingResult.Response.testing_mode -ne $true) {
        Write-Host "# Enable Testing Mode:" -ForegroundColor Yellow
        Write-Host "Invoke-WebRequest -Uri '$BaseUrl/api/v1/scheduler/testing/enable' -Method POST" -ForegroundColor White
    }
    
    Write-Host "# Rerun with auto-fix:" -ForegroundColor Yellow
    Write-Host ".\system_health_diagnostic.ps1 -FixIssues" -ForegroundColor White
}

Write-Host ""
Write-Host "🎯 NEXT STEPS:" -ForegroundColor Magenta
Write-Host "1. Address any critical issues found" -ForegroundColor White
Write-Host "2. Run service sync validator if sync issues detected" -ForegroundColor White
Write-Host "3. Test AI responses with real journal entries" -ForegroundColor White
Write-Host "" 