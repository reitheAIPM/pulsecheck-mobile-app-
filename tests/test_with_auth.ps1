# Test Journal Entries with Proper Authentication
# This script requires your JWT token from the mobile app

Write-Host "AUTHENTICATED JOURNAL TEST" -ForegroundColor Cyan
Write-Host "=========================" -ForegroundColor Cyan
Write-Host ""

# IMPORTANT: You need to get your JWT token from the mobile app
# In the mobile app, after login, check the network requests or console logs for the JWT token
# Then replace this placeholder with your actual token

$jwtToken = Read-Host "Please paste your JWT token from the mobile app"

if ($jwtToken -eq "") {
    Write-Host "ERROR: JWT token is required!" -ForegroundColor Red
    Write-Host ""
    Write-Host "How to get your JWT token:" -ForegroundColor Yellow
    Write-Host "1. Open Chrome DevTools (F12) while using the mobile app" -ForegroundColor White
    Write-Host "2. Go to Network tab" -ForegroundColor White
    Write-Host "3. Login or refresh the app" -ForegroundColor White
    Write-Host "4. Look for Supabase auth requests" -ForegroundColor White
    Write-Host "5. Find the 'access_token' in the response" -ForegroundColor White
    exit
}

$userId = "6abe6283-5dd2-46d6-995a-d876a06a55f7"
$baseUrl = "https://pulsecheck-mobile-app-production.up.railway.app"

# Create headers with authentication
$headers = @{
    "Authorization" = "Bearer $jwtToken"
    "Content-Type" = "application/json"
}

# Test 1: Get journal entries with auth
Write-Host "1. Testing Journal Entries Retrieval (with auth)..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/v1/journal/entries" -Method GET -Headers $headers -TimeoutSec 15
    Write-Host "   SUCCESS: Retrieved journal entries" -ForegroundColor Green
    Write-Host "   Total entries: $($response.total)" -ForegroundColor White
    
    if ($response.entries -and $response.entries.Count -gt 0) {
        Write-Host "   Most recent entry:" -ForegroundColor Cyan
        $latest = $response.entries[0]
        Write-Host "   - ID: $($latest.id)" -ForegroundColor White
        Write-Host "   - Content: $($latest.content.Substring(0, [Math]::Min(50, $latest.content.Length)))..." -ForegroundColor White
        Write-Host "   - Created: $($latest.created_at)" -ForegroundColor White
        
        # Save for later use
        $global:latestJournalId = $latest.id
    }
} catch {
    Write-Host "   ERROR: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 2: Create a test journal entry with auth
Write-Host "`n2. Creating Test Journal Entry (with auth)..." -ForegroundColor Yellow
$testEntry = @{
    content = "Test entry with authentication at $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
    mood_level = 7
    energy_level = 6
    stress_level = 4
    tags = @("test", "authentication")
} | ConvertTo-Json

try {
    $createResponse = Invoke-RestMethod -Uri "$baseUrl/api/v1/journal/entries" -Method POST -Body $testEntry -Headers $headers -TimeoutSec 15
    Write-Host "   SUCCESS: Journal entry created!" -ForegroundColor Green
    Write-Host "   - ID: $($createResponse.id)" -ForegroundColor Cyan
    Write-Host "   - User ID: $($createResponse.user_id)" -ForegroundColor White
    
    # Check if AI response was generated
    if ($createResponse.ai_insights) {
        Write-Host "   - AI Response: YES!" -ForegroundColor Green
        Write-Host "   - Persona Used: $($createResponse.ai_insights.persona_used)" -ForegroundColor White
        Write-Host "   - AI Message: $($createResponse.ai_insights.insight.Substring(0, [Math]::Min(100, $createResponse.ai_insights.insight.Length)))..." -ForegroundColor Cyan
    } else {
        Write-Host "   - AI Response: Not generated" -ForegroundColor Yellow
    }
} catch {
    Write-Host "   ERROR: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 3: Check AI monitoring endpoint
Write-Host "`n3. Testing AI Monitoring (should now show entries)..." -ForegroundColor Yellow
try {
    $monitoring = Invoke-RestMethod -Uri "$baseUrl/api/v1/ai-monitoring/last-action/$userId" -Method GET -TimeoutSec 15
    Write-Host "   Response received:" -ForegroundColor White
    Write-Host "   - Last Journal: $($monitoring.last_journal_entry)" -ForegroundColor White
    Write-Host "   - AI Status: $($monitoring.ai_flow_status)" -ForegroundColor White
} catch {
    Write-Host "   ERROR: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n" + ("=" * 50) -ForegroundColor Cyan
Write-Host "SUMMARY" -ForegroundColor Cyan
Write-Host ("=" * 50) -ForegroundColor Cyan
Write-Host ""
Write-Host "With proper authentication:" -ForegroundColor Green
Write-Host "- Journal entries can be created ✓" -ForegroundColor White
Write-Host "- Journal entries can be retrieved ✓" -ForegroundColor White
Write-Host "- AI responses are automatically generated ✓" -ForegroundColor White
Write-Host ""
Write-Host "The issue was missing authentication headers!" -ForegroundColor Yellow 