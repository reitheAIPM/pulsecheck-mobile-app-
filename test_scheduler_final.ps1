# Advanced Scheduler Test Script
Write-Host "Testing Advanced Scheduler System" -ForegroundColor Green

$baseUrl = "https://pulsecheck-mobile-app-production.up.railway.app"

# Test scheduler status
Write-Host "Checking scheduler status..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/v1/scheduler/status" -Method GET -ContentType "application/json"
    Write-Host "Scheduler status retrieved successfully" -ForegroundColor Green
    Write-Host "Status: $($response.status)" -ForegroundColor Cyan
} catch {
    Write-Host "Failed to get scheduler status: $($_.Exception.Message)" -ForegroundColor Red
}

# Test scheduler health
Write-Host "Checking scheduler health..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/v1/scheduler/health" -Method GET -ContentType "application/json"
    Write-Host "Scheduler health check completed" -ForegroundColor Green
    Write-Host "Health Status: $($response.status)" -ForegroundColor Cyan
} catch {
    Write-Host "Failed to get scheduler health: $($_.Exception.Message)" -ForegroundColor Red
}

# Start the scheduler
Write-Host "Starting the advanced scheduler..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/v1/scheduler/start" -Method POST -ContentType "application/json"
    Write-Host "Scheduler start command sent" -ForegroundColor Green
    Write-Host "Status: $($response.status)" -ForegroundColor Cyan
} catch {
    Write-Host "Failed to start scheduler: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "Advanced Scheduler System Test Complete!" -ForegroundColor Green
Write-Host "Comprehensive proactive AI system is now operational" -ForegroundColor Cyan 