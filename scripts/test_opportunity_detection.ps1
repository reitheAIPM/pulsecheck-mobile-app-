# PowerShell script to test opportunity detection for a specific user

# Test opportunity detection for a specific user
$userId = "6abe6283-5dd2-46d6-995a-d876a06a55f7"  # Replace with your user ID

Write-Host "Testing opportunity detection for user: $userId" -ForegroundColor Yellow

try {
    # Test the opportunity detection endpoint
    $response = Invoke-RestMethod -Uri "https://pulsecheck-mobile-app-production.up.railway.app/api/v1/proactive/opportunities" -Method GET -Headers @{"Authorization"="Bearer YOUR_TOKEN_HERE"}
    
    Write-Host "Opportunities found: $($response.Count)" -ForegroundColor Green
    
    if ($response.Count -gt 0) {
        Write-Host "Opportunities:" -ForegroundColor Green
        $response | ForEach-Object {
            Write-Host "  - Entry: $($_.entry_id), Persona: $($_.persona), Reason: $($_.reason)" -ForegroundColor White
        }
    } else {
        Write-Host "No opportunities found" -ForegroundColor Red
    }
    
} catch {
    Write-Host "Error testing opportunity detection: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`nTesting scheduler status..." -ForegroundColor Yellow

try {
    $schedulerStatus = Invoke-RestMethod -Uri "https://pulsecheck-mobile-app-production.up.railway.app/api/v1/scheduler/status" -Method GET
    
    Write-Host "Scheduler Status: $($schedulerStatus.status)" -ForegroundColor Green
    Write-Host "Running: $($schedulerStatus.running)" -ForegroundColor Green
    Write-Host "Total Cycles: $($schedulerStatus.metrics.total_cycles)" -ForegroundColor Green
    Write-Host "Last Cycle: $($schedulerStatus.metrics.last_cycle_timestamp)" -ForegroundColor Green
    
} catch {
    Write-Host "Error getting scheduler status: $($_.Exception.Message)" -ForegroundColor Red
} 