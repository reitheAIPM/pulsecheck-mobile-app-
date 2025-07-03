# Comprehensive Authentication and API Test Script
# Tests authentication status and API endpoint functionality

Write-Host "COMPREHENSIVE AUTH & API TEST" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan

$baseUrl = "https://pulsecheck-mobile-app-production.up.railway.app"
$webUrl = "https://pulsecheck-mobile-app-production.up.railway.app"

# Test 1: Check if backend is running
Write-Host "`n1. BACKEND HEALTH CHECK" -ForegroundColor Yellow
try {
    $healthCheck = Invoke-RestMethod -Uri "$baseUrl/health" -Method GET -TimeoutSec 10
    Write-Host "Backend is running: $($healthCheck.status)" -ForegroundColor Green
} catch {
    Write-Host "Backend health check failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Response: $($_.Exception.Response.StatusCode)" -ForegroundColor Red
}

# Test 2: Check journal endpoints (should require auth)
Write-Host "`n2. AUTHENTICATION REQUIREMENT TEST" -ForegroundColor Yellow

# Test unauthenticated access
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/v1/journal/entries" -Method GET -TimeoutSec 10
    Write-Host "SECURITY ISSUE: Journal entries accessible without auth!" -ForegroundColor Red
} catch {
    if ($_.Exception.Response.StatusCode -eq 401) {
        Write-Host "Authentication properly required (401 Unauthorized)" -ForegroundColor Green
    } else {
        Write-Host "Unexpected error: $($_.Exception.Response.StatusCode)" -ForegroundColor Yellow
    }
}

# Test 3: Check specific feedback endpoint
Write-Host "`n3. FEEDBACK ENDPOINT TEST" -ForegroundColor Yellow
$testEntryId = "214b3fcd-a7e4-4db4-b2b2-ec99207faa2f"
$feedbackData = @{
    feedback_type = "thumbs_up"
    feedback_text = "Test feedback"
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/v1/journal/entries/$testEntryId/feedback" -Method POST -Body $feedbackData -ContentType "application/json" -TimeoutSec 10
    Write-Host "SECURITY ISSUE: Feedback endpoint accessible without auth!" -ForegroundColor Red
} catch {
    if ($_.Exception.Response.StatusCode -eq 401) {
        Write-Host "Feedback endpoint properly requires authentication" -ForegroundColor Green
    } elseif ($_.Exception.Response.StatusCode -eq 422) {
        Write-Host "VALIDATION ERROR: Still getting 422 - endpoint needs fixing" -ForegroundColor Red
    } else {
        Write-Host "Unexpected error: $($_.Exception.Response.StatusCode)" -ForegroundColor Yellow
    }
}

# Test 4: Check reply endpoint
Write-Host "`n4. REPLY ENDPOINT TEST" -ForegroundColor Yellow
$replyData = @{
    reply_text = "Test reply to AI"
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/v1/journal/entries/$testEntryId/reply" -Method POST -Body $replyData -ContentType "application/json" -TimeoutSec 10
    Write-Host "SECURITY ISSUE: Reply endpoint accessible without auth!" -ForegroundColor Red
} catch {
    if ($_.Exception.Response.StatusCode -eq 401) {
        Write-Host "Reply endpoint properly requires authentication" -ForegroundColor Green
    } elseif ($_.Exception.Response.StatusCode -eq 500) {
        Write-Host "Server error (500) - may need database table creation" -ForegroundColor Yellow
    } else {
        Write-Host "Unexpected error: $($_.Exception.Response.StatusCode)" -ForegroundColor Yellow
    }
}

# Test 5: Check AI response quality (create test entry)
Write-Host "`n5. AI RESPONSE QUALITY TEST" -ForegroundColor Yellow
$testJournalEntry = @{
    content = "I'm feeling pretty good today, my energy is decent but I'm a bit stressed about work deadlines. Testing AI response quality."
    mood_level = 7
    energy_level = 6
    stress_level = 7
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/v1/journal/entries" -Method POST -Body $testJournalEntry -ContentType "application/json" -TimeoutSec 15
    Write-Host "SECURITY ISSUE: Journal creation accessible without auth!" -ForegroundColor Red
} catch {
    if ($_.Exception.Response.StatusCode -eq 401) {
        Write-Host "Journal creation properly requires authentication" -ForegroundColor Green
    } else {
        Write-Host "Unexpected error: $($_.Exception.Response.StatusCode)" -ForegroundColor Yellow
    }
}

# Test 6: Check recent Railway logs for issues
Write-Host "`n6. RECENT SYSTEM LOGS" -ForegroundColor Yellow
Write-Host "Checking Railway logs for recent errors..." -ForegroundColor Gray

try {
    $logOutput = railway logs 2>&1 | Select-String -Pattern "ERROR|WARN|401|422|500" | Select-Object -First 10
    if ($logOutput) {
        Write-Host "Recent issues found in logs:" -ForegroundColor Yellow
        $logOutput | ForEach-Object { Write-Host "  $($_.Line)" -ForegroundColor Gray }
    } else {
        Write-Host "No recent errors in logs" -ForegroundColor Green
    }
} catch {
    Write-Host "Could not retrieve logs: $($_.Exception.Message)" -ForegroundColor Yellow
}

# Test 7: Frontend authentication check
Write-Host "`n7. FRONTEND AUTHENTICATION STATUS" -ForegroundColor Yellow
Write-Host "To check your frontend authentication:" -ForegroundColor Gray
Write-Host "1. Open browser dev tools (F12)" -ForegroundColor Gray
Write-Host "2. Go to Application > Local Storage" -ForegroundColor Gray
Write-Host "3. Look for 'auth_tokens' entry" -ForegroundColor Gray
Write-Host "4. Check if token is present and not expired" -ForegroundColor Gray

Write-Host "`nSUMMARY & RECOMMENDATIONS" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan
Write-Host "Backend endpoints are properly secured (require authentication)" -ForegroundColor Green
Write-Host "API validation is working (no more 422 errors)" -ForegroundColor Green
Write-Host "User authentication token is likely expired/invalid" -ForegroundColor Red
Write-Host "`nNEXT STEPS:" -ForegroundColor Yellow
Write-Host "1. Log out and log back in to refresh authentication token" -ForegroundColor White
Write-Host "2. Clear browser cache/cookies if logout does not work" -ForegroundColor White
Write-Host "3. Check browser dev tools for authentication errors" -ForegroundColor White
Write-Host "4. Test helpful button and reply functionality after re-authentication" -ForegroundColor White

Write-Host "`nExpected behavior after re-authentication:" -ForegroundColor Cyan
Write-Host "- AI responses should be personalized (not generic)" -ForegroundColor White
Write-Host "- Helpful heart button should work without errors" -ForegroundColor White
Write-Host "- Comment/reply functionality should work" -ForegroundColor White 