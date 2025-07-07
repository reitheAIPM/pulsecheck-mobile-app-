# PowerShell script to manually trigger a scheduler cycle for testing

Write-Host "Manually triggering a scheduler cycle..." -ForegroundColor Yellow

try {
    # Trigger a manual cycle using the correct endpoint
    $response = Invoke-RestMethod -Uri "https://pulsecheck-mobile-app-production.up.railway.app/api/v1/scheduler/manual-cycle?cycle_type=main" -Method POST
    
    Write-Host "Manual cycle triggered successfully!" -ForegroundColor Green
    Write-Host "Response: $($response | ConvertTo-Json)" -ForegroundColor White
    
} catch {
    Write-Host "Error triggering manual cycle: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "This endpoint might not exist yet" -ForegroundColor Yellow
}

Write-Host "`nChecking scheduler status after manual trigger..." -ForegroundColor Yellow

try {
    $schedulerStatus = Invoke-RestMethod -Uri "https://pulsecheck-mobile-app-production.up.railway.app/api/v1/scheduler/status" -Method GET
    
    Write-Host "Scheduler Status: $($schedulerStatus.status)" -ForegroundColor Green
    Write-Host "Running: $($schedulerStatus.running)" -ForegroundColor Green
    Write-Host "Total Cycles: $($schedulerStatus.metrics.total_cycles)" -ForegroundColor Green
    Write-Host "Last Cycle: $($schedulerStatus.metrics.last_cycle_timestamp)" -ForegroundColor Green
    
} catch {
    Write-Host "Error getting scheduler status: $($_.Exception.Message)" -ForegroundColor Red
} 