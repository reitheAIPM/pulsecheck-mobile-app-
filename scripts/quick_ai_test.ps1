# Quick AI System Test
Write-Host "=== Quick AI System Test ===" -ForegroundColor Cyan

$baseUrl = "https://pulsecheck-mobile-app-production.up.railway.app"

# Test 1: System Health
Write-Host "`n1. Testing system health..." -ForegroundColor Green
try {
    $health = Invoke-RestMethod -Uri "$baseUrl/health" -Method GET
    Write-Host "   ✓ System is healthy" -ForegroundColor Green
} catch {
    Write-Host "   ✗ System health check failed: $_" -ForegroundColor Red
}

# Test 2: Scheduler Status
Write-Host "`n2. Testing scheduler status..." -ForegroundColor Green
try {
    $scheduler = Invoke-RestMethod -Uri "$baseUrl/api/v1/scheduler/status" -Method GET
    Write-Host "   Status: $($scheduler.status)" -ForegroundColor Yellow
    Write-Host "   Total cycles: $($scheduler.metrics.total_cycles)" -ForegroundColor Yellow
    Write-Host "   Opportunities found: $($scheduler.metrics.opportunities_found)" -ForegroundColor Yellow
    Write-Host "   Engagements executed: $($scheduler.metrics.engagements_executed)" -ForegroundColor Yellow
} catch {
    Write-Host "   ✗ Scheduler status check failed: $_" -ForegroundColor Red
}

# Test 3: Enable Testing Mode
Write-Host "`n3. Enabling testing mode..." -ForegroundColor Green
try {
    $testing = Invoke-RestMethod -Uri "$baseUrl/api/v1/scheduler/testing/enable" -Method POST
    Write-Host "   ✓ Testing mode enabled" -ForegroundColor Green
} catch {
    Write-Host "   ✗ Failed to enable testing mode: $_" -ForegroundColor Red
}

# Test 4: Trigger Manual Cycle
Write-Host "`n4. Triggering manual cycle..." -ForegroundColor Green
try {
    $cycle = Invoke-RestMethod -Uri "$baseUrl/api/v1/scheduler/manual-cycle?cycle_type=main" -Method POST
    Write-Host "   ✓ Manual cycle triggered" -ForegroundColor Green
    Write-Host "   Active users: $($cycle.active_users)" -ForegroundColor Yellow
    Write-Host "   Opportunities found: $($cycle.opportunities_found)" -ForegroundColor Yellow
    Write-Host "   Engagements executed: $($cycle.engagements_executed)" -ForegroundColor Yellow
} catch {
    Write-Host "   ✗ Failed to trigger manual cycle: $_" -ForegroundColor Red
}

Write-Host "`n=== Test Complete ===" -ForegroundColor Cyan
Write-Host "Check the frontend to see if AI responses are working correctly." -ForegroundColor Yellow
} 