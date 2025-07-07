# PowerShell script to restart the scheduler with proper event loop integration

Write-Host "Restarting the scheduler with proper event loop integration..." -ForegroundColor Yellow

try {
    # Restart the scheduler
    $response = Invoke-RestMethod -Uri "https://pulsecheck-mobile-app-production.up.railway.app/api/v1/scheduler/restart" -Method POST
    
    Write-Host "Scheduler restart response:" -ForegroundColor Green
    Write-Host ($response | ConvertTo-Json) -ForegroundColor White
    
} catch {
    Write-Host "Error restarting scheduler: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`nChecking scheduler status after restart..." -ForegroundColor Yellow

try {
    $schedulerStatus = Invoke-RestMethod -Uri "https://pulsecheck-mobile-app-production.up.railway.app/api/v1/scheduler/status" -Method GET
    
    Write-Host "Scheduler Status: $($schedulerStatus.status)" -ForegroundColor Green
    Write-Host "Running: $($schedulerStatus.running)" -ForegroundColor Green
    Write-Host "Total Cycles: $($schedulerStatus.metrics.total_cycles)" -ForegroundColor Green
    Write-Host "Last Cycle: $($schedulerStatus.metrics.last_cycle_timestamp)" -ForegroundColor Green
    
    if ($schedulerStatus.jobs) {
        Write-Host "`nActive Jobs:" -ForegroundColor Green
        $schedulerStatus.jobs | ForEach-Object {
            Write-Host "  - $($_.name): Next run at $($_.next_run)" -ForegroundColor White
        }
    }
    
} catch {
    Write-Host "Error getting scheduler status: $($_.Exception.Message)" -ForegroundColor Red
} 