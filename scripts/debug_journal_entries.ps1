# PowerShell script to debug journal entries and opportunity detection

Write-Host "Debugging journal entries and opportunity detection..." -ForegroundColor Yellow

# Test the opportunity detection with detailed logging
try {
    # First, let's check if there are any recent journal entries
    Write-Host "`n1. Checking for recent journal entries..." -ForegroundColor Cyan
    
    # This would require authentication, but let's check the scheduler logs
    Write-Host "   (Note: Journal entry check requires authentication)" -ForegroundColor Gray
    
    # Check scheduler status
    Write-Host "`n2. Checking scheduler status..." -ForegroundColor Cyan
    $schedulerStatus = Invoke-RestMethod -Uri "https://pulsecheck-mobile-app-production.up.railway.app/api/v1/scheduler/status" -Method GET
    
    Write-Host "   Scheduler Status: $($schedulerStatus.status)" -ForegroundColor White
    Write-Host "   Running: $($schedulerStatus.running)" -ForegroundColor White
    Write-Host "   Total Cycles: $($schedulerStatus.metrics.total_cycles)" -ForegroundColor White
    Write-Host "   Last Cycle: $($schedulerStatus.metrics.last_cycle_timestamp)" -ForegroundColor White
    
    # Check if there are any recent cycles with details
    if ($schedulerStatus.recent_cycles) {
        Write-Host "`n3. Recent cycles:" -ForegroundColor Cyan
        $schedulerStatus.recent_cycles | ForEach-Object {
            Write-Host "   - Cycle: $($_.cycle_id), Users: $($_.users_processed), Opportunities: $($_.opportunities_found), Engagements: $($_.engagements_executed)" -ForegroundColor White
        }
    } else {
        Write-Host "`n3. No recent cycles found" -ForegroundColor Yellow
    }
    
    # Check testing mode status
    Write-Host "`n4. Checking testing mode status..." -ForegroundColor Cyan
    try {
        $testingStatus = Invoke-RestMethod -Uri "https://pulsecheck-mobile-app-production.up.railway.app/api/v1/proactive/testing-status" -Method GET
        Write-Host "   Testing Mode: $($testingStatus.testing_mode)" -ForegroundColor White
        Write-Host "   Status: $($testingStatus.status)" -ForegroundColor White
    } catch {
        Write-Host "   Testing status endpoint not available" -ForegroundColor Yellow
    }
    
} catch {
    Write-Host "Error during debugging: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n5. Common issues that cause 0 opportunities:" -ForegroundColor Cyan
Write-Host "   - Journal entries are too short (< 10 characters)" -ForegroundColor White
Write-Host "   - Journal entries look like AI responses (filtered out)" -ForegroundColor White
Write-Host "   - All personas have already responded to the entry" -ForegroundColor White
Write-Host "   - Daily AI response limits reached (but testing mode should bypass this)" -ForegroundColor White
Write-Host "   - User tier restrictions (FREE tier limited to 1 persona)" -ForegroundColor White
Write-Host "   - Bombardment prevention (10-minute cooldown between responses)" -ForegroundColor White

Write-Host "`n6. Recommendations:" -ForegroundColor Cyan
Write-Host "   - Create a new journal entry with > 10 characters" -ForegroundColor White
Write-Host "   - Make sure it doesn't start with AI-like phrases" -ForegroundColor White
Write-Host "   - Wait 5 minutes for the next cycle" -ForegroundColor White
Write-Host "   - Check if you're on FREE tier (limited to Pulse persona)" -ForegroundColor White 