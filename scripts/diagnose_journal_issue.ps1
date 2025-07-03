# Comprehensive Journal Entry Diagnostic Test
# Tests if journal entries are properly linked to user accounts

Write-Host "JOURNAL ENTRY DIAGNOSTIC TEST" -ForegroundColor Cyan
Write-Host "=============================" -ForegroundColor Cyan
Write-Host ""

$userId = "6abe6283-5dd2-46d6-995a-d876a06a55f7"
$email = "czarcasmx@gmail.com"
$baseUrl = "https://pulsecheck-mobile-app-production.up.railway.app"

Write-Host "Testing User: $email" -ForegroundColor White
Write-Host "User ID: $userId" -ForegroundColor White
Write-Host ""

# Test 1: Check if user exists in profiles table
Write-Host "1. Testing User Profile..." -ForegroundColor Yellow
try {
    $profileCheck = Invoke-RestMethod -Uri "$baseUrl/api/v1/profiles/$userId" -Method GET -TimeoutSec 15
    Write-Host "   SUCCESS: Profile found" -ForegroundColor Green
    Write-Host "   Email: $($profileCheck.email)" -ForegroundColor White
    Write-Host "   User ID: $($profileCheck.user_id)" -ForegroundColor White
} catch {
    if ($_.Exception.Message -like "*404*") {
        Write-Host "   WARNING: No profile found for user ID" -ForegroundColor Red
        Write-Host "   This could mean:" -ForegroundColor Yellow
        Write-Host "   - User signup didn't create a profile" -ForegroundColor Yellow
        Write-Host "   - handle_new_user trigger failed" -ForegroundColor Yellow
    } else {
        Write-Host "   ERROR: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Test 2: Check journal entries directly
Write-Host "`n2. Testing Journal Entries..." -ForegroundColor Yellow
try {
    $journalCheck = Invoke-RestMethod -Uri "$baseUrl/api/v1/journal/entries?user_id=$userId" -Method GET -TimeoutSec 15
    if ($journalCheck -and $journalCheck.Count -gt 0) {
        Write-Host "   SUCCESS: Found $($journalCheck.Count) journal entries" -ForegroundColor Green
        Write-Host "   Most recent entry:" -ForegroundColor White
        Write-Host "   - ID: $($journalCheck[0].id)" -ForegroundColor Cyan
        Write-Host "   - Content: $($journalCheck[0].content.Substring(0, [Math]::Min(50, $journalCheck[0].content.Length)))..." -ForegroundColor White
        Write-Host "   - Created: $($journalCheck[0].created_at)" -ForegroundColor White
    } else {
        Write-Host "   WARNING: No journal entries returned" -ForegroundColor Red
    }
} catch {
    Write-Host "   ERROR: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 3: Check AI monitoring (shows database view)
Write-Host "`n3. Testing AI Monitoring (Database View)..." -ForegroundColor Yellow
try {
    $monitoring = Invoke-RestMethod -Uri "$baseUrl/api/v1/ai-monitoring/last-action/$userId" -Method GET -TimeoutSec 15
    Write-Host "   Response received:" -ForegroundColor White
    Write-Host "   - Last Journal: $($monitoring.last_journal_entry)" -ForegroundColor White
    Write-Host "   - AI Status: $($monitoring.ai_flow_status)" -ForegroundColor White
    
    if ($monitoring.error) {
        Write-Host "   - Error: $($monitoring.error)" -ForegroundColor Red
    }
} catch {
    Write-Host "   ERROR: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 4: Create a test journal entry
Write-Host "`n4. Creating Test Journal Entry..." -ForegroundColor Yellow
$testContent = "Test journal entry created at $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') to diagnose linking issue"
$journalBody = @{
    user_id = $userId
    content = $testContent
    mood_rating = 7
    energy_level = 6
} | ConvertTo-Json

try {
    $headers = @{
        "Content-Type" = "application/json"
    }
    
    $createResult = Invoke-RestMethod -Uri "$baseUrl/api/v1/journal/create" -Method POST -Body $journalBody -Headers $headers -TimeoutSec 15
    Write-Host "   SUCCESS: Journal entry created" -ForegroundColor Green
    Write-Host "   - Journal ID: $($createResult.id)" -ForegroundColor Cyan
    Write-Host "   - User ID: $($createResult.user_id)" -ForegroundColor White
    
    # Save the journal ID for later
    $global:testJournalId = $createResult.id
} catch {
    Write-Host "   ERROR: Failed to create journal entry" -ForegroundColor Red
    Write-Host "   - $($_.Exception.Message)" -ForegroundColor Red
}

# Test 5: Check if the created entry is visible
Write-Host "`n5. Verifying Created Entry..." -ForegroundColor Yellow
Start-Sleep -Seconds 2  # Give it a moment to propagate

try {
    $verifyCheck = Invoke-RestMethod -Uri "$baseUrl/api/v1/journal/entries?user_id=$userId" -Method GET -TimeoutSec 15
    $foundTestEntry = $verifyCheck | Where-Object { $_.content -eq $testContent }
    
    if ($foundTestEntry) {
        Write-Host "   SUCCESS: Test entry found in user's journals" -ForegroundColor Green
        Write-Host "   - Entry is properly linked to user" -ForegroundColor Green
    } else {
        Write-Host "   ERROR: Test entry NOT found in user's journals" -ForegroundColor Red
        Write-Host "   - Entry may be created with wrong user_id" -ForegroundColor Yellow
        Write-Host "   - Or RLS policies are blocking read access" -ForegroundColor Yellow
    }
} catch {
    Write-Host "   ERROR: $($_.Exception.Message)" -ForegroundColor Red
}

# Summary
Write-Host "`n" + ("=" * 50) -ForegroundColor Cyan
Write-Host "DIAGNOSIS SUMMARY" -ForegroundColor Cyan
Write-Host ("=" * 50) -ForegroundColor Cyan

Write-Host "`nPossible Issues:" -ForegroundColor Yellow
Write-Host "1. User Profile Missing: Check if handle_new_user trigger is working" -ForegroundColor White
Write-Host "2. Journal Entries Not Linked: Check if user_id is correctly passed when creating entries" -ForegroundColor White
Write-Host "3. RLS Policies: Check if policies allow the correct user_id to read entries" -ForegroundColor White
Write-Host "4. Auth Token Mismatch: Mobile app might be using different user_id than expected" -ForegroundColor White

Write-Host "`nRecommended Actions:" -ForegroundColor Green
Write-Host "- Check Supabase Dashboard > Authentication > Users (verify user exists)" -ForegroundColor White
Write-Host "- Check Supabase Dashboard > Table Editor > profiles (verify profile exists)" -ForegroundColor White
Write-Host "- Check Supabase Dashboard > Table Editor > journal_entries (check user_id values)" -ForegroundColor White
Write-Host "- Verify mobile app is passing correct user_id when creating entries" -ForegroundColor White 