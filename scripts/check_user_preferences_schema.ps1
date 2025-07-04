# Check User AI Preferences Table Schema
Write-Host "🔍 Database Schema Fix Guide" -ForegroundColor Green
Write-Host "============================" -ForegroundColor Green

Write-Host "`n1. Go to Supabase Dashboard → SQL Editor" -ForegroundColor Yellow
Write-Host "2. Run this query to check if table exists:" -ForegroundColor Cyan
Write-Host "   SELECT table_name FROM information_schema.tables WHERE table_name = 'user_ai_preferences';" -ForegroundColor Gray

Write-Host "`n3. If table exists, check columns:" -ForegroundColor Cyan
Write-Host "   SELECT column_name FROM information_schema.columns WHERE table_name = 'user_ai_preferences';" -ForegroundColor Gray

Write-Host "`n4. If missing 'ai_interaction_level' column, add it:" -ForegroundColor Yellow
Write-Host "   ALTER TABLE user_ai_preferences ADD COLUMN ai_interaction_level TEXT DEFAULT 'MODERATE';" -ForegroundColor Gray

Write-Host "`n5. If table doesn't exist, create it:" -ForegroundColor Yellow
Write-Host "   Copy this SQL block and paste it in SQL Editor:" -ForegroundColor Gray
Write-Host "   =============================================" -ForegroundColor Gray
Write-Host ""
Write-Host "   CREATE TABLE user_ai_preferences ("
Write-Host "       id UUID DEFAULT gen_random_uuid() PRIMARY KEY,"
Write-Host "       user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,"
Write-Host "       ai_interaction_level TEXT DEFAULT 'MODERATE',"
Write-Host "       created_at TIMESTAMPTZ DEFAULT NOW(),"
Write-Host "       updated_at TIMESTAMPTZ DEFAULT NOW(),"
Write-Host "       UNIQUE(user_id)"
Write-Host "   );"
Write-Host ""
Write-Host "   ALTER TABLE user_ai_preferences ENABLE ROW LEVEL SECURITY;"
Write-Host ""

Write-Host "`n6. Set your account to premium:" -ForegroundColor Green
Write-Host "   INSERT INTO user_ai_preferences (user_id, ai_interaction_level)" -ForegroundColor Gray
Write-Host "   VALUES ('6abe6283-5dd2-46d6-995a-d876a06a55f7', 'HIGH')" -ForegroundColor Gray
Write-Host "   ON CONFLICT (user_id) DO UPDATE SET ai_interaction_level = 'HIGH';" -ForegroundColor Gray

Write-Host "`n7. Test the fix:" -ForegroundColor Green
Write-Host "   .\scripts\test_ai_multi_persona_simple.ps1" -ForegroundColor White

Write-Host "`n✅ Expected Result: Premium personalized responses instead of fallback messages" -ForegroundColor Green 