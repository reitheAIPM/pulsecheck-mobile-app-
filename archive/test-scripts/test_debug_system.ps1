#!/usr/bin/env pwsh
# Comprehensive Debug System Test Script
# Tests all debug endpoints and generates comprehensive logs

Write-Host "COMPREHENSIVE DEBUG SYSTEM TEST STARTING" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green
Write-Host "This script will test all debug endpoints and generate logs for analysis" -ForegroundColor Yellow
Write-Host ""

$BASE_URL = "https://pulsecheck-mobile-app-production.up.railway.app"
$TEST_RESULTS = @()

function Test-Endpoint {
    param(
        [string]$Name,
        [string]$Url,
        [string]$Method = "GET",
        [string]$Body = $null
    )
    
    Write-Host "Testing: $Name" -ForegroundColor Cyan
    Write-Host "   URL: $Url" -ForegroundColor Gray
    
    try {
        $startTime = Get-Date
        
        if ($Method -eq "GET") {
            $response = curl.exe -s -w "%{http_code}" $Url
        } elseif ($Method -eq "POST" -and $Body) {
            $response = curl.exe -s -w "%{http_code}" -X POST -H "Content-Type: application/json" -d $Body $Url
        } else {
            $response = curl.exe -s -w "%{http_code}" -X $Method $Url
        }
        
        $endTime = Get-Date
        $duration = [Math]::Round(($endTime - $startTime).TotalMilliseconds, 0)
        
        # Extract status code (last 3 characters)
        if ($response.Length -ge 3) {
            $statusCode = $response.Substring($response.Length - 3, 3)
            $responseBody = $response.Substring(0, $response.Length - 3)
        } else {
            $statusCode = "000"
            $responseBody = $response
        }
        
        if ($statusCode -eq "200") {
            Write-Host "   SUCCESS ($statusCode) - ${duration}ms" -ForegroundColor Green
            $status = "SUCCESS"
        } elseif ($statusCode -eq "404") {
            Write-Host "   NOT FOUND ($statusCode) - ${duration}ms" -ForegroundColor Red
            $status = "NOT_FOUND"
        } elseif ($statusCode -match "^[45]") {
            Write-Host "   ERROR ($statusCode) - ${duration}ms" -ForegroundColor Yellow
            $status = "ERROR"
        } else {
            Write-Host "   RESPONSE ($statusCode) - ${duration}ms" -ForegroundColor Blue
            $status = "OTHER"
        }
        
        # Show response preview if not too long
        if ($responseBody.Length -lt 200 -and $responseBody.Length -gt 0) {
            Write-Host "   Response: $responseBody" -ForegroundColor Gray
        } elseif ($responseBody.Length -gt 0) {
            $preview = $responseBody.Substring(0, [Math]::Min(100, $responseBody.Length))
            Write-Host "   Response: $preview..." -ForegroundColor Gray
        }
        
        return @{
            Name = $Name
            Url = $Url
            StatusCode = $statusCode
            Status = $status
            Duration = $duration
            ResponseLength = $responseBody.Length
        }
        
    } catch {
        Write-Host "   EXCEPTION: $($_.Exception.Message)" -ForegroundColor Red
        return @{
            Name = $Name
            Url = $Url
            StatusCode = "ERROR"
            Status = "EXCEPTION"
            Duration = 0
            ResponseLength = 0
        }
    }
    
    Write-Host ""
}

Write-Host "Phase 1: Basic Connectivity Tests" -ForegroundColor Magenta
Write-Host "==================================" -ForegroundColor Magenta

# Test 1: Basic Health Check
$TEST_RESULTS += Test-Endpoint -Name "Health Check" -Url "$BASE_URL/health"

# Test 2: Root endpoint  
$TEST_RESULTS += Test-Endpoint -Name "Root Endpoint" -Url "$BASE_URL/"

# Test 3: CORS preflight
$TEST_RESULTS += Test-Endpoint -Name "CORS Preflight" -Url "$BASE_URL/health" -Method "OPTIONS"

Write-Host "Phase 2: Debug Router Tests (Our Main Focus)" -ForegroundColor Magenta
Write-Host "=============================================" -ForegroundColor Magenta

# Test 4: Main debug summary endpoint
$TEST_RESULTS += Test-Endpoint -Name "Debug Summary (MAIN)" -Url "$BASE_URL/api/v1/debug/summary"

# Test 5: Debug health check
$TEST_RESULTS += Test-Endpoint -Name "Debug Health" -Url "$BASE_URL/api/v1/debug/health"

# Test 6: Debug requests endpoint
$TEST_RESULTS += Test-Endpoint -Name "Debug Requests" -Url "$BASE_URL/api/v1/debug/requests"

# Test 7: Debug database stats
$TEST_RESULTS += Test-Endpoint -Name "Debug Database Stats" -Url "$BASE_URL/api/v1/debug/database/stats"

# Test 8: Debug performance analysis
$TEST_RESULTS += Test-Endpoint -Name "Debug Performance" -Url "$BASE_URL/api/v1/debug/performance/analysis"

# Test 9: Debug live stream
$TEST_RESULTS += Test-Endpoint -Name "Debug Live Stream" -Url "$BASE_URL/api/v1/debug/live/stream"

Write-Host "Phase 3: AI-Enhanced Debug Endpoints" -ForegroundColor Magenta
Write-Host "====================================" -ForegroundColor Magenta

# Test 10: AI Insights Comprehensive
$TEST_RESULTS += Test-Endpoint -Name "AI Insights Comprehensive" -Url "$BASE_URL/api/v1/debug/ai-insights/comprehensive"

# Test 11: Edge Testing Comprehensive
$TEST_RESULTS += Test-Endpoint -Name "Edge Testing" -Url "$BASE_URL/api/v1/debug/edge-testing/comprehensive"

# Test 12: Failure Points Analysis
$TEST_RESULTS += Test-Endpoint -Name "Failure Points Analysis" -Url "$BASE_URL/api/v1/debug/failure-points/analysis"

# Test 13: Risk Analysis
$TEST_RESULTS += Test-Endpoint -Name "Risk Analysis" -Url "$BASE_URL/api/v1/debug/risk-analysis/current"

Write-Host "Phase 4: Other API Endpoints (For Comparison)" -ForegroundColor Magenta
Write-Host "===============================================" -ForegroundColor Magenta

# Test 14: Auth endpoint (should fail without auth)
$TEST_RESULTS += Test-Endpoint -Name "Auth Test (should fail)" -Url "$BASE_URL/api/v1/auth/me"

# Test 15: Journal endpoint (should fail without auth)
$TEST_RESULTS += Test-Endpoint -Name "Journal Test (should fail)" -Url "$BASE_URL/api/v1/journal/entries"

# Test 16: Admin endpoint (should fail without auth)
$TEST_RESULTS += Test-Endpoint -Name "Admin Test (should fail)" -Url "$BASE_URL/api/v1/admin/stats"

Write-Host "Phase 5: Legacy Debug Endpoints (From main.py)" -ForegroundColor Magenta
Write-Host "===============================================" -ForegroundColor Magenta

# Test 17: Legacy AI debug endpoints
$TEST_RESULTS += Test-Endpoint -Name "Legacy AI Debug Active Issues" -Url "$BASE_URL/ai-debug/active-issues"

# Test 18: Legacy AI debug error patterns
$TEST_RESULTS += Test-Endpoint -Name "Legacy AI Debug Patterns" -Url "$BASE_URL/ai-debug/error-patterns"

# Test 19: Monitoring errors
$TEST_RESULTS += Test-Endpoint -Name "Monitoring Errors" -Url "$BASE_URL/monitoring/errors"

Write-Host "Phase 6: POST Endpoints (Triggering Activity)" -ForegroundColor Magenta
Write-Host "=============================================" -ForegroundColor Magenta

# Test 20: Test auth signin (triggers backend logic)
$authBody = '{"email":"test@example.com","password":"test123"}'
$TEST_RESULTS += Test-Endpoint -Name "Auth Signin (trigger activity)" -Url "$BASE_URL/api/v1/auth/signin" -Method "POST" -Body $authBody

# Test 21: AI Learning Feedback
$feedbackBody = '{"ai_model":"claude-sonnet-4","issue_type":"router_import_failure","success":false}'
$TEST_RESULTS += Test-Endpoint -Name "AI Learning Feedback" -Url "$BASE_URL/api/v1/debug/ai-learning/feedback" -Method "POST" -Body $feedbackBody

Write-Host "COMPREHENSIVE TEST RESULTS SUMMARY" -ForegroundColor Green
Write-Host "===================================" -ForegroundColor Green

$successCount = ($TEST_RESULTS | Where-Object { $_.Status -eq "SUCCESS" }).Count
$notFoundCount = ($TEST_RESULTS | Where-Object { $_.Status -eq "NOT_FOUND" }).Count
$errorCount = ($TEST_RESULTS | Where-Object { $_.Status -eq "ERROR" }).Count
$exceptionCount = ($TEST_RESULTS | Where-Object { $_.Status -eq "EXCEPTION" }).Count

Write-Host ""
Write-Host "SUMMARY STATISTICS:" -ForegroundColor Yellow
Write-Host "  Successful (200): $successCount" -ForegroundColor Green
Write-Host "  Not Found (404): $notFoundCount" -ForegroundColor Red  
Write-Host "  Errors (4xx/5xx): $errorCount" -ForegroundColor Yellow
Write-Host "  Exceptions: $exceptionCount" -ForegroundColor Red
Write-Host "  Total Tests: $($TEST_RESULTS.Count)" -ForegroundColor Cyan

Write-Host ""
Write-Host "DEBUG ROUTER STATUS:" -ForegroundColor Yellow
$debugTests = $TEST_RESULTS | Where-Object { $_.Name -like "*Debug*" }
$debugSuccess = ($debugTests | Where-Object { $_.Status -eq "SUCCESS" }).Count
$debugTotal = $debugTests.Count

if ($debugSuccess -eq 0) {
    Write-Host "  DEBUG ROUTER: COMPLETELY DOWN - 0/$debugTotal endpoints working" -ForegroundColor Red
} elseif ($debugSuccess -eq $debugTotal) {
    Write-Host "  DEBUG ROUTER: FULLY OPERATIONAL - $debugSuccess/$debugTotal endpoints working" -ForegroundColor Green
} else {
    Write-Host "  DEBUG ROUTER: PARTIALLY WORKING - $debugSuccess/$debugTotal endpoints working" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "DETAILED BREAKDOWN:" -ForegroundColor Yellow
foreach ($result in $TEST_RESULTS) {
    $statusIcon = "INFO"
    if ($result.Status -eq "SUCCESS") { $statusIcon = "OK" }
    elseif ($result.Status -eq "NOT_FOUND") { $statusIcon = "404" }
    elseif ($result.Status -eq "ERROR") { $statusIcon = "ERR" }
    elseif ($result.Status -eq "EXCEPTION") { $statusIcon = "EXC" }
    
    Write-Host "  [$statusIcon] $($result.Name): $($result.StatusCode) ($($result.Duration)ms)" -ForegroundColor Gray
}

Write-Host ""
Write-Host "NEXT STEPS FOR DEBUGGING:" -ForegroundColor Yellow
if ($notFoundCount -gt 0) {
    Write-Host "  1. Check Railway logs for router import errors" -ForegroundColor Cyan
    Write-Host "  2. Verify debug router is being registered in main.py" -ForegroundColor Cyan
    Write-Host "  3. Check middleware import issues in debug.py" -ForegroundColor Cyan
}
if ($successCount -gt 0) {
    Write-Host "  1. Some endpoints working - check which ones succeed" -ForegroundColor Cyan
    Write-Host "  2. Compare successful vs failed endpoint patterns" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "TEST COMPLETED - Check Railway logs for detailed startup/request info!" -ForegroundColor Green
Write-Host "=========================================================" -ForegroundColor Green 