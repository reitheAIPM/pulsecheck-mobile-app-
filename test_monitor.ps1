# Simple AI System Test
param([string]$BaseUrl = "https://pulsecheck-mobile-app-production.up.railway.app")

Write-Host "Testing AI System..." -ForegroundColor Green

# Test system health
try {
    $health = Invoke-RestMethod -Uri "$BaseUrl/health" -Method GET
    Write-Host "✅ System Health: $($health.status)" -ForegroundColor Green
} catch {
    Write-Host "❌ Health check failed" -ForegroundColor Red
}

# Check testing mode
try {
    $testingStatus = Invoke-RestMethod -Uri "$BaseUrl/api/v1/scheduler/testing/status" -Method GET
    Write-Host "Testing Mode: $($testingStatus.testing_mode)" -ForegroundColor Cyan
    
    if (-not $testingStatus.testing_mode) {
        Write-Host "Enabling testing mode..." -ForegroundColor Yellow
        $enable = Invoke-RestMethod -Uri "$BaseUrl/api/v1/scheduler/testing/enable" -Method POST
        Write-Host "✅ Testing mode enabled!" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ Testing mode check failed" -ForegroundColor Red
}

# Check scheduler
try {
    $scheduler = Invoke-RestMethod -Uri "$BaseUrl/api/v1/scheduler/status" -Method GET
    Write-Host "✅ Scheduler: $($scheduler.status) - $($scheduler.metrics.total_cycles) cycles" -ForegroundColor Green
} catch {
    Write-Host "❌ Scheduler check failed" -ForegroundColor Red
}

Write-Host ""
Write-Host "🎯 NOW TEST AI RESPONSES:" -ForegroundColor Yellow
Write-Host "1. Go to: https://pulsecheck-mobile.vercel.app/" -ForegroundColor White
Write-Host "2. Login with your account" -ForegroundColor White
Write-Host "3. Create a journal entry" -ForegroundColor White
Write-Host "4. Wait 30-60 seconds for AI response" -ForegroundColor White 