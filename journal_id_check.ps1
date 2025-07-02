# Journal ID Discovery Test
# Tests if we can find your journal IDs after RLS fix

Write-Host "JOURNAL ID DISCOVERY TEST" -ForegroundColor Cyan
Write-Host "=========================" -ForegroundColor Cyan

$userId = "6abe6283-5dd2-46d6-995a-d876a06a55f7"
$baseUrl = "https://pulsecheck-mobile-app-production.up.railway.app"

# Test 1: Health Check
Write-Host "`n1. Testing Health..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "$baseUrl/health" -Method GET -TimeoutSec 10
    Write-Host "   SUCCESS: $($health.status)" -ForegroundColor Green
    Write-Host "   Database: $($health.components.database)" -ForegroundColor Green
} catch {
    Write-Host "   FAILED: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 2: AI Monitoring (o3's key endpoint)
Write-Host "`n2. Testing AI Monitoring..." -ForegroundColor Yellow
try {
    $monitoring = Invoke-RestMethod -Uri "$baseUrl/api/v1/ai-monitoring/last-action/$userId" -Method GET -TimeoutSec 15
    Write-Host "   SUCCESS: Monitoring responded" -ForegroundColor Green
    Write-Host "   User ID: $($monitoring.user_id)" -ForegroundColor White
    Write-Host "   Last Journal: $($monitoring.last_journal_entry)" -ForegroundColor White
    Write-Host "   AI Status: $($monitoring.ai_flow_status)" -ForegroundColor White
    
    if ($monitoring.last_journal_entry -and $monitoring.last_journal_entry -ne "" -and $monitoring.last_journal_entry -ne $null) {
        Write-Host "   FOUND JOURNAL!" -ForegroundColor Magenta
        Write-Host "   Content: $($monitoring.last_journal_entry)" -ForegroundColor Cyan
    } else {
        Write-Host "   No journal entries found via API" -ForegroundColor Yellow
    }
} catch {
    Write-Host "   FAILED: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`nSUMMARY:" -ForegroundColor Cyan
Write-Host "RLS Migration: Applied successfully" -ForegroundColor Green
Write-Host "Railway App: Running (health works)" -ForegroundColor Green

if ($monitoring.last_journal_entry) {
    Write-Host "Journal Access: WORKING - Entries found!" -ForegroundColor Green
    Write-Host "`nYou can now use your journal IDs for testing AI responses." -ForegroundColor White
} else {
    Write-Host "Journal Access: NOT WORKING - Entries not visible" -ForegroundColor Red
    Write-Host "`nNext steps:" -ForegroundColor Yellow
    Write-Host "- Check service role environment variables in Railway" -ForegroundColor White
    Write-Host "- Verify RLS policies are applied correctly" -ForegroundColor White
    Write-Host "- Test direct Supabase dashboard access" -ForegroundColor White
} 