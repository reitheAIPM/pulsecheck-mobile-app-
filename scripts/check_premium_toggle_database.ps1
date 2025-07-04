# Check Premium Toggle Database Update
# This script helps verify if the premium toggle actually updated the database

$testUserId = "6abe6283-5dd2-46d6-995a-d876a06a55f7"

Write-Host "🔍 Checking Premium Toggle Database Update" -ForegroundColor Green
Write-Host "===========================================" -ForegroundColor Green

Write-Host "`nStep 1: Check Current Database State" -ForegroundColor Yellow
Write-Host "Go to Supabase Dashboard → SQL Editor and run:" -ForegroundColor Cyan
Write-Host ""
Write-Host "SELECT user_id, ai_interaction_level, created_at, updated_at" -ForegroundColor Gray
Write-Host "FROM user_ai_preferences" -ForegroundColor Gray
Write-Host "WHERE user_id = '$testUserId';" -ForegroundColor Gray
Write-Host ""
Write-Host "Expected Results:" -ForegroundColor Green
Write-Host "- ai_interaction_level = 'HIGH' (Premium enabled)" -ForegroundColor Green
Write-Host "- updated_at should be recent (within last few minutes)" -ForegroundColor Green

Write-Host "`nStep 2: If No Results Found" -ForegroundColor Yellow
Write-Host "If the query returns no results, run this to create the record:" -ForegroundColor Cyan
Write-Host ""
Write-Host "INSERT INTO user_ai_preferences (user_id, ai_interaction_level, created_at, updated_at)" -ForegroundColor Gray
Write-Host "VALUES ('$testUserId', 'HIGH', NOW(), NOW());" -ForegroundColor Gray

Write-Host "`nStep 3: If Results Show 'MODERATE' Instead of 'HIGH'" -ForegroundColor Yellow
Write-Host "If ai_interaction_level = 'MODERATE', manually update it:" -ForegroundColor Cyan
Write-Host ""
Write-Host "UPDATE user_ai_preferences" -ForegroundColor Gray
Write-Host "SET ai_interaction_level = 'HIGH', updated_at = NOW()" -ForegroundColor Gray
Write-Host "WHERE user_id = '$testUserId';" -ForegroundColor Gray

Write-Host "`nStep 4: Verify All Required Columns Exist" -ForegroundColor Yellow
Write-Host "Check if the table has the right structure:" -ForegroundColor Cyan
Write-Host ""
Write-Host "SELECT column_name, data_type, is_nullable" -ForegroundColor Gray
Write-Host "FROM information_schema.columns" -ForegroundColor Gray
Write-Host "WHERE table_name = 'user_ai_preferences'" -ForegroundColor Gray
Write-Host "ORDER BY ordinal_position;" -ForegroundColor Gray

Write-Host "`nStep 5: Test Premium Toggle API Again" -ForegroundColor Yellow
Write-Host "After verifying the database, test the toggle again:" -ForegroundColor Cyan
Write-Host ""
Write-Host ".\scripts\test_premium_toggle_fix.ps1" -ForegroundColor Gray

Write-Host "`nStep 6: Test AI Response Quality" -ForegroundColor Yellow
Write-Host "After confirming premium is enabled, test AI responses:" -ForegroundColor Cyan
Write-Host ""
Write-Host ".\scripts\test_ai_multi_persona_simple.ps1" -ForegroundColor Gray

Write-Host "`n🎯 What We're Looking For:" -ForegroundColor Yellow
Write-Host "1. Database record exists with ai_interaction_level = 'HIGH'" -ForegroundColor White
Write-Host "2. Recent updated_at timestamp (shows toggle worked)" -ForegroundColor White
Write-Host "3. AI responses are personalized, not generic fallbacks" -ForegroundColor White
Write-Host "4. No more 'I'm here to listen...' fallback responses" -ForegroundColor White

Write-Host "`n🚀 Expected Premium Experience:" -ForegroundColor Green
Write-Host "- Detailed, personalized AI responses" -ForegroundColor White
Write-Host "- Multiple personas responding (Pulse, Sage, Spark, Anchor)" -ForegroundColor White
Write-Host "- Contextual responses based on your journal entries" -ForegroundColor White
Write-Host "- No generic fallback messages" -ForegroundColor White

Write-Host "`n⚠️ Troubleshooting:" -ForegroundColor Red
Write-Host "If you're still getting fallbacks after database shows 'HIGH':" -ForegroundColor White
Write-Host "1. Check Railway logs for any database connection errors" -ForegroundColor White
Write-Host "2. Verify the backend deployment completed successfully" -ForegroundColor White
Write-Host "3. Try restarting the Railway service" -ForegroundColor White
Write-Host "4. Test with a fresh journal entry" -ForegroundColor White