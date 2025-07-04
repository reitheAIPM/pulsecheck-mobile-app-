# Verify Premium Account Status
Write-Host "🔍 Verifying Premium Account Status" -ForegroundColor Green
Write-Host "====================================" -ForegroundColor Green

Write-Host "`nStep 1: Check if user_ai_preferences table exists" -ForegroundColor Yellow
Write-Host "Go to Supabase Dashboard → SQL Editor and run:" -ForegroundColor Cyan
Write-Host "SELECT table_name FROM information_schema.tables WHERE table_name = 'user_ai_preferences';" -ForegroundColor Gray

Write-Host "`nStep 2: Check if ai_interaction_level column exists" -ForegroundColor Yellow
Write-Host "SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'user_ai_preferences' AND column_name = 'ai_interaction_level';" -ForegroundColor Gray

Write-Host "`nStep 3: Check your account settings" -ForegroundColor Yellow
Write-Host "SELECT user_id, ai_interaction_level, created_at FROM user_ai_preferences WHERE user_id = '6abe6283-5dd2-46d6-995a-d876a06a55f7';" -ForegroundColor Gray

Write-Host "`nStep 4: If no results, insert your premium account" -ForegroundColor Yellow
Write-Host "INSERT INTO user_ai_preferences (user_id, ai_interaction_level, created_at, updated_at)" -ForegroundColor Green
Write-Host "VALUES ('6abe6283-5dd2-46d6-995a-d876a06a55f7', 'HIGH', NOW(), NOW())" -ForegroundColor Green
Write-Host "ON CONFLICT (user_id) DO UPDATE SET ai_interaction_level = 'HIGH', updated_at = NOW();" -ForegroundColor Green

Write-Host "`nStep 5: Test again" -ForegroundColor Yellow
Write-Host ".\scripts\test_ai_multi_persona_simple.ps1" -ForegroundColor White

Write-Host "`n✅ Expected: Premium personalized responses instead of fallback messages" -ForegroundColor Green 