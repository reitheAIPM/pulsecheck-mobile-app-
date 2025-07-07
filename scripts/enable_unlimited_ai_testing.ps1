param(
    [string]$UserId = "",
    [string]$BaseUrl = "https://pulsecheck-mobile-app-production.up.railway.app/api/v1"
)

Write-Host "🧪 Enable Unlimited AI Testing Script" -ForegroundColor Yellow
Write-Host "====================================" -ForegroundColor Yellow

if (-not $UserId) {
    Write-Host "❌ Please provide your user ID" -ForegroundColor Red
    Write-Host "Usage: .\enable_unlimited_ai_testing.ps1 -UserId 'your-user-id-here'" -ForegroundColor White
    return
}

Write-Host "🔍 Checking current AI response count..." -ForegroundColor Green
try {
    # First, trigger a manual cycle to get current status
    $manualCycle = Invoke-WebRequest -Uri "$BaseUrl/scheduler/manual-cycle" -Method POST -Body '{"cycle_type": "main"}' -ContentType "application/json" | 
                  Select-Object -ExpandProperty Content | ConvertFrom-Json
    
    Write-Host "✅ Manual cycle triggered" -ForegroundColor Green
    
    # Wait for cycle to complete
    Start-Sleep -Seconds 5
    
    # Get scheduler status
    $schedulerStatus = Invoke-WebRequest -Uri "$BaseUrl/scheduler/status" -Method GET | 
                      Select-Object -ExpandProperty Content | ConvertFrom-Json
    
    $latestCycle = $schedulerStatus.recent_cycles | Sort-Object timestamp -Descending | Select-Object -First 1
    
    Write-Host "📊 Latest Cycle Results:" -ForegroundColor Cyan
    Write-Host "  - Users processed: $($latestCycle.users_processed)" -ForegroundColor White
    Write-Host "  - Opportunities found: $($latestCycle.opportunities_found)" -ForegroundColor White
    Write-Host "  - Engagements executed: $($latestCycle.engagements_executed)" -ForegroundColor White
    
    if ($latestCycle.opportunities_found -eq 0) {
        Write-Host "❌ No opportunities found - likely daily limit reached" -ForegroundColor Red
        Write-Host "📋 Current daily limits:" -ForegroundColor Yellow
        Write-Host "  - FREE/MINIMAL: 5 responses/day" -ForegroundColor White
        Write-Host "  - FREE/MODERATE: 10 responses/day" -ForegroundColor White
        Write-Host "  - FREE/HIGH: 15 responses/day" -ForegroundColor White
        Write-Host "  - PREMIUM/MINIMAL: 20 responses/day" -ForegroundColor White
        Write-Host "  - PREMIUM/MODERATE: 50 responses/day" -ForegroundColor White
        Write-Host "  - PREMIUM/HIGH: Unlimited" -ForegroundColor White
    } else {
        Write-Host "✅ Opportunities found - system is working!" -ForegroundColor Green
        return
    }
    
} catch {
    Write-Host "❌ Error checking scheduler: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n💡 Solutions:" -ForegroundColor Yellow
Write-Host "==============" -ForegroundColor Yellow
Write-Host "1. Add your user ID to the testing_user_ids list in the backend code" -ForegroundColor White
Write-Host "2. Upgrade your AI interaction level to HIGH (unlimited for premium users)" -ForegroundColor White
Write-Host "3. Wait until tomorrow for the daily limit to reset" -ForegroundColor White

Write-Host "`n🔧 To add your user ID to testing list:" -ForegroundColor Cyan
Write-Host "=======================================" -ForegroundColor Cyan
Write-Host "Edit: backend/app/services/comprehensive_proactive_ai_service.py" -ForegroundColor White
Write-Host "Find line ~128: self.testing_user_ids = {" -ForegroundColor White
Write-Host "Add: `"$UserId`"" -ForegroundColor White
Write-Host "Then redeploy the backend" -ForegroundColor White

Write-Host "`n🎯 Your User ID: $UserId" -ForegroundColor Yellow
Write-Host "Copy this ID and add it to the testing_user_ids list" -ForegroundColor White

Write-Host "`n✅ Script completed!" -ForegroundColor Green 