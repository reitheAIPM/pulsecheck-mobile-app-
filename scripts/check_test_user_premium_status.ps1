# Check Test User Premium Status
$testUserId = "6abe6283-5dd2-46d6-995a-d876a06a55f7"
$backendUrl = "https://pulsecheck-mobile-app-production.up.railway.app"

Write-Host "🔍 Checking Test User Premium Status" -ForegroundColor Green
Write-Host "====================================" -ForegroundColor Green

Write-Host "`nStep 1: Check Current Premium Status via API" -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$backendUrl/api/v1/auth/subscription-status/$testUserId" -Method GET
    Write-Host "✅ API Response:" -ForegroundColor Green
    Write-Host "   is_premium_active: $($response.is_premium_active)" -ForegroundColor Gray
    Write-Host "   beta_premium_enabled: $($response.beta_premium_enabled)" -ForegroundColor Gray
    Write-Host "   available_personas: $($response.available_personas -join ', ')" -ForegroundColor Gray
} catch {
    Write-Host "❌ API call failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`nStep 2: Check Database Directly" -ForegroundColor Yellow
Write-Host "Go to Supabase Dashboard → SQL Editor and run:" -ForegroundColor Cyan
Write-Host ""
Write-Host "SELECT user_id, ai_interaction_level, created_at, updated_at" -ForegroundColor Gray
Write-Host "FROM user_ai_preferences" -ForegroundColor Gray
Write-Host ("WHERE user_id = " + $testUserId + ";") -ForegroundColor Gray

Write-Host "`nStep 3: Fix Database Settings" -ForegroundColor Yellow
Write-Host "Run this SQL to ensure premium status:" -ForegroundColor Cyan
Write-Host ""
Write-Host "-- Fix test user premium status --" -ForegroundColor Green
Write-Host "INSERT INTO user_ai_preferences (" -ForegroundColor Gray
Write-Host "    user_id," -ForegroundColor Gray
Write-Host "    ai_interaction_level," -ForegroundColor Gray
Write-Host "    ai_interactions_enabled," -ForegroundColor Gray
Write-Host "    user_tier," -ForegroundColor Gray
Write-Host "    preferred_personas," -ForegroundColor Gray
Write-Host "    created_at," -ForegroundColor Gray
Write-Host "    updated_at" -ForegroundColor Gray
Write-Host ") VALUES (" -ForegroundColor Gray
Write-Host "    '$testUserId'," -ForegroundColor Gray
Write-Host "    'HIGH'," -ForegroundColor Gray
Write-Host "    TRUE," -ForegroundColor Gray
Write-Host "    'premium'," -ForegroundColor Gray
Write-Host "    ARRAY[pulse, sage, spark, anchor]," -ForegroundColor Gray
Write-Host "    NOW()," -ForegroundColor Gray
Write-Host "    NOW()" -ForegroundColor Gray
Write-Host ") ON CONFLICT (user_id) DO UPDATE SET" -ForegroundColor Gray
Write-Host "    ai_interaction_level = 'HIGH'," -ForegroundColor Gray
Write-Host "    ai_interactions_enabled = TRUE," -ForegroundColor Gray
Write-Host "    user_tier = 'premium'," -ForegroundColor Gray
Write-Host "    preferred_personas = ARRAY[pulse, sage, spark, anchor]," -ForegroundColor Gray
Write-Host "    updated_at = NOW();" -ForegroundColor Gray

Write-Host "`nStep 4: Test Premium Toggle API" -ForegroundColor Yellow
$toggleBody = @{
    user_id = $testUserId
    enabled = $true
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "$backendUrl/api/v1/auth/beta/toggle-premium" -Method POST -Body $toggleBody -ContentType "application/json"
    Write-Host "✅ Premium toggle API call successful" -ForegroundColor Green
    Write-Host "   Response: $($response.message)" -ForegroundColor Gray
} catch {
    Write-Host "❌ Premium toggle API failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`nStep 5: Verify Fix" -ForegroundColor Yellow
Write-Host "After running the SQL, check again:" -ForegroundColor Cyan
Write-Host ""
Write-Host "SELECT user_id, ai_interaction_level, user_tier, preferred_personas" -ForegroundColor Gray
Write-Host "FROM user_ai_preferences" -ForegroundColor Gray
Write-Host ("WHERE user_id = " + $testUserId + ";") -ForegroundColor Gray

Write-Host "`nExpected Results:" -ForegroundColor Green
Write-Host "- ai_interaction_level = HIGH" -ForegroundColor Green
Write-Host "- user_tier = premium" -ForegroundColor Green
Write-Host "- preferred_personas should include all 4 personas" -ForegroundColor Green

Write-Host "`nStep 6: Test AI Response" -ForegroundColor Yellow
Write-Host "Create a new journal entry and check if you get multiple personas instead of just Pulse" -ForegroundColor Cyan
Write-Host "Expected: You should now get Sage, Spark, and Anchor responses in addition to Pulse" -ForegroundColor Green 