# Enable Premium Override - Direct Database Update
# This script provides SQL to directly update user preferences to disable fallback responses

$testUserId = "6abe6283-5dd2-46d6-995a-d876a06a55f7"

Write-Host "🚀 Premium Override Database Update" -ForegroundColor Green
Write-Host "====================================" -ForegroundColor Green

Write-Host "`nTo disable fallback responses for your account:" -ForegroundColor Yellow
Write-Host "1. Go to your Supabase Dashboard: https://app.supabase.com" -ForegroundColor Cyan
Write-Host "2. Navigate to your project → SQL Editor" -ForegroundColor Cyan
Write-Host "3. Run the following SQL commands:" -ForegroundColor Cyan

Write-Host "`n-- SQL to enable premium override and disable fallbacks --" -ForegroundColor Green

$sql1 = @"
-- First, check if user preferences exist
SELECT * FROM user_ai_preferences WHERE user_id = '$testUserId';
"@

$sql2 = @"
-- If the user exists, update their preferences
UPDATE user_ai_preferences 
SET 
    ai_interaction_level = 'HIGH',
    updated_at = NOW()
WHERE user_id = '$testUserId';
"@

$sql3 = @"
-- If the user doesn't exist, create new preferences
INSERT INTO user_ai_preferences (
    user_id, 
    ai_interaction_level, 
    created_at, 
    updated_at
) VALUES (
    '$testUserId',
    'HIGH',
    NOW(),
    NOW()
) ON CONFLICT (user_id) DO UPDATE SET
    ai_interaction_level = 'HIGH',
    updated_at = NOW();
"@

$sql4 = @"
-- Add custom settings to disable fallbacks (if you have a settings table)
-- Note: The backend code I added will check for premium_override = true
-- For now, setting ai_interaction_level = 'HIGH' should enable premium features
"@

Write-Host $sql1 -ForegroundColor White
Write-Host "`n" + $sql2 -ForegroundColor White  
Write-Host "`n" + $sql3 -ForegroundColor White
Write-Host "`n" + $sql4 -ForegroundColor Gray

Write-Host "`n✨ What This Does:" -ForegroundColor Yellow
Write-Host "  - Sets your AI interaction level to HIGH (maximum)" -ForegroundColor White
Write-Host "  - Enables multi-persona responses" -ForegroundColor White
Write-Host "  - The backend will check for HIGH level and provide premium service" -ForegroundColor White

Write-Host "`n🔍 Alternative Method - Quick Test:" -ForegroundColor Green
Write-Host "If you want to test without database changes, run:" -ForegroundColor Cyan
Write-Host ".\scripts\test_ai_multi_persona_simple.ps1" -ForegroundColor White
Write-Host "This will test if the current setup works for premium responses" -ForegroundColor Gray

Write-Host "`n📋 After running the SQL:" -ForegroundColor Green
Write-Host "1. Test AI responses in your mobile app" -ForegroundColor White
Write-Host "2. Check if you get detailed, personalized responses (not generic fallbacks)" -ForegroundColor White
Write-Host "3. Look for multiple AI personas responding to journal entries" -ForegroundColor White
Write-Host "4. Monitor Railway logs for 'premium' or 'HIGH interaction' messages" -ForegroundColor White

Write-Host "`n⚠️  Note:" -ForegroundColor Yellow
Write-Host "The full premium override features require a backend deployment." -ForegroundColor White
Write-Host "For now, setting ai_interaction_level = 'HIGH' should reduce fallback usage." -ForegroundColor White 