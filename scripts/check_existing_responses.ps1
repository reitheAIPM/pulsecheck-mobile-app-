# PowerShell script to check existing AI responses for journal entries

Write-Host "Checking existing AI responses for journal entries..." -ForegroundColor Yellow

# This script would need authentication to check the database directly
# For now, let's create a new journal entry to test with

Write-Host "`nSince we can't directly query the database without authentication," -ForegroundColor Cyan
Write-Host "let's create a new journal entry to test the AI response system." -ForegroundColor Cyan

Write-Host "`nRecommendations:" -ForegroundColor Green
Write-Host "1. Create a NEW journal entry with > 10 characters" -ForegroundColor White
Write-Host "2. Make sure it doesn't start with AI-like phrases" -ForegroundColor White
Write-Host "3. Wait 5 minutes for the next scheduler cycle" -ForegroundColor White
Write-Host "4. Check if AI responses appear" -ForegroundColor White

Write-Host "`nThe issue is likely that all personas have already responded to your existing entries." -ForegroundColor Yellow
Write-Host "Creating a new entry will give the AI personas a fresh opportunity to respond." -ForegroundColor Yellow

Write-Host "`nTesting scheduler status..." -ForegroundColor Cyan

try {
    $schedulerStatus = Invoke-RestMethod -Uri "https://pulsecheck-mobile-app-production.up.railway.app/api/v1/scheduler/status" -Method GET
    
    Write-Host "Scheduler Status: $($schedulerStatus.status)" -ForegroundColor White
    Write-Host "Running: $($schedulerStatus.running)" -ForegroundColor White
    Write-Host "Total Cycles: $($schedulerStatus.metrics.total_cycles)" -ForegroundColor White
    Write-Host "Last Cycle: $($schedulerStatus.metrics.last_cycle_timestamp)" -ForegroundColor White
    
    if ($schedulerStatus.jobs) {
        Write-Host "`nNext scheduled runs:" -ForegroundColor Green
        $schedulerStatus.jobs | ForEach-Object {
            Write-Host "  - $($_.name): $($_.next_run)" -ForegroundColor White
        }
    }
    
} catch {
    Write-Host "Error getting scheduler status: $($_.Exception.Message)" -ForegroundColor Red
} 