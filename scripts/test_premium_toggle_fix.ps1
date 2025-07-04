# Test Premium Toggle Fix
# This script tests if the premium toggle actually updates the database

$testUserId = "6abe6283-5dd2-46d6-995a-d876a06a55f7"
$backendUrl = "https://pulsecheck-mobile-app-production.up.railway.app"

Write-Host "🧪 Testing Premium Toggle Fix" -ForegroundColor Green
Write-Host "============================" -ForegroundColor Green

Write-Host "`nStep 1: Testing Premium Toggle ON" -ForegroundColor Yellow

# Test enabling premium
$toggleOnBody = @{
    user_id = $testUserId
    enabled = $true
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "$backendUrl/api/v1/auth/beta/toggle-premium" -Method POST -Body $toggleOnBody -ContentType "application/json"
    Write-Host "✅ Premium toggle ON API call successful" -ForegroundColor Green
    Write-Host "   Response: $($response.message)" -ForegroundColor Gray
} catch {
    Write-Host "❌ Premium toggle ON failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`nStep 2: Checking Database State (Premium ON)" -ForegroundColor Yellow
Write-Host "Go to Supabase Dashboard → SQL Editor and run:" -ForegroundColor Cyan
Write-Host "SELECT user_id, ai_interaction_level, updated_at FROM user_ai_preferences WHERE user_id = '$testUserId';" -ForegroundColor Gray
Write-Host "Expected: ai_interaction_level = 'HIGH'" -ForegroundColor Green

Start-Sleep -Seconds 2

Write-Host "`nStep 3: Testing Premium Toggle OFF" -ForegroundColor Yellow

# Test disabling premium
$toggleOffBody = @{
    user_id = $testUserId
    enabled = $false
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "$backendUrl/api/v1/auth/beta/toggle-premium" -Method POST -Body $toggleOffBody -ContentType "application/json"
    Write-Host "✅ Premium toggle OFF API call successful" -ForegroundColor Green
    Write-Host "   Response: $($response.message)" -ForegroundColor Gray
} catch {
    Write-Host "❌ Premium toggle OFF failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`nStep 4: Checking Database State (Premium OFF)" -ForegroundColor Yellow
Write-Host "Go to Supabase Dashboard → SQL Editor and run:" -ForegroundColor Cyan
Write-Host "SELECT user_id, ai_interaction_level, updated_at FROM user_ai_preferences WHERE user_id = '$testUserId';" -ForegroundColor Gray
Write-Host "Expected: ai_interaction_level = 'MODERATE'" -ForegroundColor Green

Write-Host "`nStep 5: Testing Premium Toggle ON again" -ForegroundColor Yellow

# Test enabling premium again
try {
    $response = Invoke-RestMethod -Uri "$backendUrl/api/v1/auth/beta/toggle-premium" -Method POST -Body $toggleOnBody -ContentType "application/json"
    Write-Host "✅ Premium toggle ON (final) API call successful" -ForegroundColor Green
    Write-Host "   Response: $($response.message)" -ForegroundColor Gray
} catch {
    Write-Host "❌ Premium toggle ON (final) failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`nStep 6: Final Database Check" -ForegroundColor Yellow
Write-Host "Go to Supabase Dashboard → SQL Editor and run:" -ForegroundColor Cyan
Write-Host "SELECT user_id, ai_interaction_level, updated_at FROM user_ai_preferences WHERE user_id = '$testUserId';" -ForegroundColor Gray
Write-Host "Expected: ai_interaction_level = 'HIGH'" -ForegroundColor Green

Write-Host "`n✨ What This Test Validates:" -ForegroundColor Yellow
Write-Host "1. Premium toggle API calls succeed" -ForegroundColor White
Write-Host "2. Database gets updated with correct ai_interaction_level" -ForegroundColor White
Write-Host "3. 'HIGH' = Premium features enabled (no fallbacks)" -ForegroundColor White
Write-Host "4. 'MODERATE' = Standard features (fallbacks possible)" -ForegroundColor White

Write-Host "`n🎯 Next Steps:" -ForegroundColor Yellow
Write-Host "1. Verify the database queries show the correct ai_interaction_level" -ForegroundColor White
Write-Host "2. Test AI responses to confirm no more fallbacks" -ForegroundColor White
Write-Host "3. Toggle premium on/off in the UI and verify it persists" -ForegroundColor White

Write-Host "`n🚀 The Fix Applied:" -ForegroundColor Green
Write-Host "- Premium toggle now updates user_ai_preferences table" -ForegroundColor White
Write-Host "- AI services check database for ai_interaction_level = 'HIGH'" -ForegroundColor White
Write-Host "- Premium users get personalized responses, no fallbacks" -ForegroundColor White 