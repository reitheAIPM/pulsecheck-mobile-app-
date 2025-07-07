# PowerShell script to test duplicate prevention logic and debug opportunity filtering

Write-Host "Testing duplicate prevention logic and opportunity filtering..." -ForegroundColor Yellow

# Step 1: Check current testing mode status
Write-Host "`n1. Checking testing mode status..." -ForegroundColor Cyan
try {
    $testingStatus = Invoke-RestMethod -Uri "https://pulsecheck-mobile-app-production.up.railway.app/api/v1/proactive/testing-status" -Method GET
    Write-Host "Testing Mode: $($testingStatus.testing_mode)" -ForegroundColor Green
    Write-Host "Bombardment Prevention: $($testingStatus.testing_behavior.bombardment_prevention_disabled)" -ForegroundColor Green
} catch {
    Write-Host "Error checking testing status: $($_.Exception.Message)" -ForegroundColor Red
}

# Step 2: Trigger a manual cycle to see detailed logs
Write-Host "`n2. Triggering manual cycle to see detailed logs..." -ForegroundColor Cyan
try {
    $cycleResult = Invoke-RestMethod -Uri "https://pulsecheck-mobile-app-production.up.railway.app/api/v1/scheduler/manual-cycle?cycle_type=main" -Method POST
    Write-Host "Manual cycle result:" -ForegroundColor Green
    Write-Host ($cycleResult | ConvertTo-Json -Depth 3) -ForegroundColor White
} catch {
    Write-Host "Error triggering manual cycle: $($_.Exception.Message)" -ForegroundColor Red
}

# Step 3: Check scheduler status after manual cycle
Write-Host "`n3. Checking scheduler status after manual cycle..." -ForegroundColor Cyan
try {
    $schedulerStatus = Invoke-RestMethod -Uri "https://pulsecheck-mobile-app-production.up.railway.app/api/v1/scheduler/status" -Method GET
    Write-Host "Total Cycles: $($schedulerStatus.metrics.total_cycles)" -ForegroundColor Green
    Write-Host "Last Cycle: $($schedulerStatus.metrics.last_cycle_timestamp)" -ForegroundColor Green
    Write-Host "Current Status: $($schedulerStatus.current_status)" -ForegroundColor Green
} catch {
    Write-Host "Error checking scheduler status: $($_.Exception.Message)" -ForegroundColor Red
}

# Step 4: Recommendations for testing
Write-Host "`n4. Recommendations for testing duplicate prevention:" -ForegroundColor Cyan
Write-Host "   - Create a NEW journal entry (> 10 characters)" -ForegroundColor White
Write-Host "   - Make sure it doesn't start with AI-like phrases" -ForegroundColor White
Write-Host "   - Wait 5 minutes for the next scheduler cycle" -ForegroundColor White
Write-Host "   - Check if any AI responses are generated" -ForegroundColor White

Write-Host "`n5. If no AI responses are generated:" -ForegroundColor Cyan
Write-Host "   - The duplicate prevention logic is blocking all personas" -ForegroundColor Yellow
Write-Host "   - We may need to temporarily bypass duplicate prevention in testing mode" -ForegroundColor Yellow
Write-Host "   - Or check if existing AI responses exist for recent entries" -ForegroundColor Yellow

Write-Host "`n6. Next debugging steps:" -ForegroundColor Cyan
Write-Host "   - Add debug logging to _should_persona_respond method" -ForegroundColor White
Write-Host "   - Check database for existing AI responses" -ForegroundColor White
Write-Host "   - Consider temporary bypass of duplicate prevention" -ForegroundColor White 