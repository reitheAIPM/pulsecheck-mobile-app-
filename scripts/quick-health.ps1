#!/usr/bin/env pwsh

# Quick Health Check Script - o3 Optimization Implementation
# Chains all critical health checks with proper timeouts and clear status

Write-Host "🏥 Quick System Health Check - o3 Optimized" -ForegroundColor Yellow
Write-Host "=============================================" -ForegroundColor Yellow
Write-Host ""

$baseUrl = "https://pulsecheck-mobile-app-production.up.railway.app"
$testUser = "test.user@example.com"

# o3 Optimization: Standardized error handling with timeouts
function Invoke-HealthCheck {
    param (
        [string]$Url,
        [string]$Description,
        [string]$Method = "GET",
        [int]$TimeoutSec = 15
    )
    
    Write-Host "🔄 $Description..." -ForegroundColor Cyan -NoNewline
    
    try {
        if ($Method -eq "GET") {
            $response = curl.exe -s --max-time $TimeoutSec $Url
            $result = $response | ConvertFrom-Json
        } else {
            $response = Invoke-WebRequest -Uri $Url -Method $Method -TimeoutSec $TimeoutSec
            $result = $response.Content | ConvertFrom-Json
        }
        
        Write-Host " ✅" -ForegroundColor Green
        return $result
    } catch {
        Write-Host " ❌" -ForegroundColor Red
        Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Red
        return $null
    }
}

# 1. System Health Check
Write-Host "1️⃣ System Health" -ForegroundColor Magenta
$health = Invoke-HealthCheck -Url "$baseUrl/health" -Description "System health"
if ($health) {
    Write-Host "   Status: $($health.status)" -ForegroundColor Gray
    Write-Host "   Timestamp: $($health.timestamp)" -ForegroundColor Gray
}
Write-Host ""

# 2. Scheduler Status Check
Write-Host "2️⃣ AI Scheduler Status" -ForegroundColor Magenta
$schedulerStatus = Invoke-HealthCheck -Url "$baseUrl/api/v1/scheduler/status" -Description "Scheduler status"
if ($schedulerStatus) {
    $isRunning = $schedulerStatus.running -eq $true
    $statusColor = if ($isRunning) { "Green" } else { "Red" }
    Write-Host "   Running: $($schedulerStatus.running)" -ForegroundColor $statusColor
    Write-Host "   Total cycles: $($schedulerStatus.total_cycles)" -ForegroundColor Gray
    Write-Host "   Success rate: $($schedulerStatus.success_rate)%" -ForegroundColor Gray
    Write-Host "   Last run: $($schedulerStatus.last_successful_run)" -ForegroundColor Gray
}
Write-Host ""

# 3. Testing Mode Status Check
Write-Host "3️⃣ AI Testing Mode" -ForegroundColor Magenta
$testingStatus = Invoke-HealthCheck -Url "$baseUrl/api/v1/scheduler/testing/status" -Description "Testing mode status"
if ($testingStatus) {
    $testingEnabled = $testingStatus.testing_mode -eq $true
    $statusColor = if ($testingEnabled) { "Green" } else { "Yellow" }
    Write-Host "   Testing mode: $($testingStatus.testing_mode)" -ForegroundColor $statusColor
    Write-Host "   Status: $($testingStatus.status)" -ForegroundColor Gray
    Write-Host "   Message: $($testingStatus.message)" -ForegroundColor Gray
}
Write-Host ""

# 4. o3 Critical Check: Last AI Action for Test User
Write-Host "4️⃣ AI Flow Status (o3 Single Endpoint)" -ForegroundColor Magenta
$aiFlow = Invoke-HealthCheck -Url "$baseUrl/api/v1/ai-monitoring/last-action/$testUser" -Description "Complete AI flow status"
if ($aiFlow) {
    $flowStatusColor = switch ($aiFlow.ai_flow_status) {
        "up_to_date" { "Green" }
        "processing" { "Yellow" }
        "scheduler_stopped" { "Red" }
        "delayed_testing" { "Red" }
        "delayed_production" { "Red" }
        default { "Gray" }
    }
    
    Write-Host "   AI Flow Status: $($aiFlow.ai_flow_status)" -ForegroundColor $flowStatusColor
    Write-Host "   Last journal entry: $($aiFlow.last_journal_entry)" -ForegroundColor Gray
    Write-Host "   Last AI comment: $($aiFlow.last_ai_comment)" -ForegroundColor Gray
    Write-Host "   Next scheduled: $($aiFlow.next_scheduled_at)" -ForegroundColor Gray
    Write-Host "   Testing mode: $($aiFlow.testing_mode)" -ForegroundColor Gray
    Write-Host "   Scheduler running: $($aiFlow.scheduler_running)" -ForegroundColor Gray
    
    if ($aiFlow.status_details) {
        Write-Host "   Details: $($aiFlow.status_details -join '; ')" -ForegroundColor Gray
    }
}
Write-Host ""

# 5. Database Connectivity Check
Write-Host "5️⃣ Database Connectivity" -ForegroundColor Magenta
$dbStatus = Invoke-HealthCheck -Url "$baseUrl/api/v1/database/comprehensive-status" -Description "Database health"
if ($dbStatus) {
    Write-Host "   Overall status: $($dbStatus.overall_status)" -ForegroundColor Gray
    Write-Host "   Database query: $($dbStatus.database_query)" -ForegroundColor Gray
    Write-Host "   Connection: $($dbStatus.connection_status)" -ForegroundColor Gray
}
Write-Host ""

# 6. Overall System Assessment
Write-Host "📊 OVERALL SYSTEM ASSESSMENT" -ForegroundColor Magenta
Write-Host "=============================================" -ForegroundColor Magenta

# Calculate overall health score
$healthScore = 0
$maxScore = 5

if ($health) { $healthScore++ }
if ($schedulerStatus -and $schedulerStatus.running) { $healthScore++ }
if ($testingStatus) { $healthScore++ }
if ($aiFlow -and $aiFlow.ai_flow_status -ne "monitoring_error") { $healthScore++ }
if ($dbStatus) { $healthScore++ }

$healthPercentage = [math]::Round(($healthScore / $maxScore) * 100, 1)

$overallColor = if ($healthPercentage -ge 80) { "Green" } elseif ($healthPercentage -ge 60) { "Yellow" } else { "Red" }

Write-Host ""
Write-Host "🎯 Health Score: $healthScore/$maxScore ($healthPercentage%)" -ForegroundColor $overallColor
Write-Host ""

# Critical Status Summary
if ($schedulerStatus -and $testingStatus -and $aiFlow) {
    $schedulerRunning = $schedulerStatus.running -eq $true
    $testingEnabled = $testingStatus.testing_mode -eq $true
    
    if ($schedulerRunning -and $testingEnabled) {
        Write-Host "✅ READY FOR AI TESTING: Scheduler running + Testing mode enabled" -ForegroundColor Green
        Write-Host "   Expected AI response time: 30-60 seconds" -ForegroundColor Green
    } elseif ($schedulerRunning -and -not $testingEnabled) {
        Write-Host "⚠️  PRODUCTION MODE: Scheduler running, testing mode disabled" -ForegroundColor Yellow
        Write-Host "   Expected AI response time: 5 minutes to 1 hour" -ForegroundColor Yellow
        Write-Host "   Enable testing: Invoke-WebRequest -Uri '$baseUrl/api/v1/scheduler/testing/enable' -Method POST -TimeoutSec 15" -ForegroundColor Yellow
    } elseif (-not $schedulerRunning) {
        Write-Host "❌ AI RESPONSES DISABLED: Scheduler not running" -ForegroundColor Red
        Write-Host "   Start scheduler: Invoke-WebRequest -Uri '$baseUrl/api/v1/scheduler/start' -Method POST -TimeoutSec 15" -ForegroundColor Red
    }
} else {
    Write-Host "❌ INCOMPLETE STATUS: Unable to determine AI readiness" -ForegroundColor Red
}

Write-Host ""

# Quick Action Commands
Write-Host "🚀 QUICK ACTION COMMANDS" -ForegroundColor Magenta
Write-Host "=============================================" -ForegroundColor Magenta
Write-Host ""

if ($schedulerStatus -and -not $schedulerStatus.running) {
    Write-Host "📋 Start Scheduler:" -ForegroundColor White
    Write-Host "Invoke-WebRequest -Uri '$baseUrl/api/v1/scheduler/start' -Method POST -TimeoutSec 15" -ForegroundColor Gray
    Write-Host ""
}

if ($testingStatus -and -not $testingStatus.testing_mode) {
    Write-Host "⚡ Enable Testing Mode:" -ForegroundColor White
    Write-Host "Invoke-WebRequest -Uri '$baseUrl/api/v1/scheduler/testing/enable' -Method POST -TimeoutSec 15" -ForegroundColor Gray
    Write-Host ""
}

Write-Host "🧪 Create Test User:" -ForegroundColor White
Write-Host ".\create_simple_test_user.ps1" -ForegroundColor Gray
Write-Host ""

Write-Host "📊 Monitor AI Flow:" -ForegroundColor White
Write-Host "Invoke-WebRequest -Uri '$baseUrl/api/v1/ai-monitoring/last-action/$testUser' -Method GET -TimeoutSec 15" -ForegroundColor Gray
Write-Host ""

Write-Host "🔄 Re-run Health Check:" -ForegroundColor White
Write-Host ".\scripts\quick-health.ps1" -ForegroundColor Gray
Write-Host ""

Write-Host "✅ QUICK HEALTH CHECK COMPLETE" -ForegroundColor Green
Write-Host ""
Write-Host "💡 o3 Optimization Benefits Achieved:" -ForegroundColor Yellow
Write-Host "- Single script for complete system status" -ForegroundColor White
Write-Host "- 15-second timeouts prevent hanging" -ForegroundColor White
Write-Host "- Clear action commands for common issues" -ForegroundColor White
Write-Host "- Comprehensive AI flow visibility in one run" -ForegroundColor White 