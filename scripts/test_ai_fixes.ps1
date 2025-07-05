# Test AI Fixes - PowerShell Script
# Tests the new AI preference system and single persona responses

$BASE_URL = "https://pulsecheck-mobile-app-production.up.railway.app"
$TEST_USER_ID = "6abe6283-5dd2-46d6-995a-d876a06a55f7"

Write-Host "🔧 Testing AI System Fixes..." -ForegroundColor Yellow

# Test 1: Check AI diagnostic for test user
Write-Host "`n1. Checking AI diagnostic for test user..." -ForegroundColor Cyan
try {
    $diagnosticResponse = Invoke-RestMethod -Uri "$BASE_URL/api/v1/journal/debug/ai-diagnostic/$TEST_USER_ID" -Method GET
    Write-Host "✅ AI Diagnostic Response:" -ForegroundColor Green
    Write-Host "   - AI Enabled: $($diagnosticResponse.ai_enabled)" -ForegroundColor White
    Write-Host "   - AI Service Working: $($diagnosticResponse.ai_service_status.working)" -ForegroundColor White
    Write-Host "   - Generic Response Detected: $($diagnosticResponse.ai_service_status.is_generic)" -ForegroundColor White
    Write-Host "   - Today's Response Count: $($diagnosticResponse.today_response_count)" -ForegroundColor White
    
    if ($diagnosticResponse.ai_service_status.is_generic) {
        Write-Host "⚠️  Generic responses detected - PulseAI service needs debugging" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ Error checking AI diagnostic: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 2: Enable AI for test user (if not already enabled)
Write-Host "`n2. Enabling AI for test user..." -ForegroundColor Cyan
try {
    $enableAIBody = @{
        user_id = $TEST_USER_ID
        enable = $true
    } | ConvertTo-Json
    
    $enableResponse = Invoke-RestMethod -Uri "$BASE_URL/api/v1/journal/debug/enable-ai-for-user" -Method POST -Body $enableAIBody -ContentType "application/json"
    Write-Host "✅ AI Enabled: $($enableResponse.message)" -ForegroundColor Green
} catch {
    Write-Host "❌ Error enabling AI: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 3: Create a test journal entry to trigger AI response
Write-Host "`n3. Creating test journal entry to trigger AI response..." -ForegroundColor Cyan
try {
    $journalBody = @{
        content = "I've been feeling really overwhelmed with work lately, but I'm also excited about some new opportunities that are coming up. It's like I'm caught between stress and anticipation. I keep thinking about how everyone else seems to have their life figured out while I'm still trying to find my rhythm in this city."
        mood_level = 6
        energy_level = 7
        stress_level = 8
        tags = @("work_stress", "reflection")
    } | ConvertTo-Json
    
    $journalResponse = Invoke-RestMethod -Uri "$BASE_URL/api/v1/journal/entries" -Method POST -Body $journalBody -ContentType "application/json" -Headers @{
        "Authorization" = "Bearer YOUR_JWT_TOKEN_HERE"  # You'll need to add your actual JWT token
    }
    
    $entryId = $journalResponse.id
    Write-Host "✅ Journal entry created: $entryId" -ForegroundColor Green
    
    # Wait a few seconds for webhook processing
    Write-Host "   Waiting 5 seconds for AI response processing..." -ForegroundColor White
    Start-Sleep -Seconds 5
    
    # Check if AI response was generated
    $entryWithAI = Invoke-RestMethod -Uri "$BASE_URL/api/v1/journal/entries/$entryId" -Method GET -Headers @{
        "Authorization" = "Bearer YOUR_JWT_TOKEN_HERE"
    }
    
    if ($entryWithAI.ai_insights -and $entryWithAI.ai_insights.Count -gt 0) {
        Write-Host "✅ AI Response Generated!" -ForegroundColor Green
        Write-Host "   - Number of AI responses: $($entryWithAI.ai_insights.Count)" -ForegroundColor White
        Write-Host "   - Persona used: $($entryWithAI.ai_insights[0].persona_used)" -ForegroundColor White
        Write-Host "   - Response preview: $($entryWithAI.ai_insights[0].ai_response.Substring(0, [Math]::Min(100, $entryWithAI.ai_insights[0].ai_response.Length)))..." -ForegroundColor White
        
        if ($entryWithAI.ai_insights.Count -eq 1) {
            Write-Host "✅ FIXED: Only ONE persona responded (not 4)" -ForegroundColor Green
        } else {
            Write-Host "⚠️  Multiple personas still responding: $($entryWithAI.ai_insights.Count)" -ForegroundColor Yellow
        }
    } else {
        Write-Host "⚠️  No AI response generated - check logs" -ForegroundColor Yellow
    }
    
} catch {
    Write-Host "❌ Error creating journal entry: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "   Note: Make sure to add your JWT token to the script" -ForegroundColor Yellow
}

Write-Host "`n🔍 Fix Summary:" -ForegroundColor Yellow
Write-Host "✅ User preference checking: Implemented" -ForegroundColor Green
Write-Host "✅ Single persona response: Implemented" -ForegroundColor Green
Write-Host "✅ Engagement pattern detection: Implemented" -ForegroundColor Green
Write-Host "⚠️  Generic response issue: Still needs investigation" -ForegroundColor Yellow
Write-Host "✅ Debug endpoints: Available for troubleshooting" -ForegroundColor Green

Write-Host "`n🚀 Next Steps:" -ForegroundColor Cyan
Write-Host "1. Apply database migration: npx supabase db push --include-all" -ForegroundColor White
Write-Host "2. Deploy changes to Railway" -ForegroundColor White
Write-Host "3. Test with a real journal entry in the UI" -ForegroundColor White
Write-Host "4. Check AI diagnostic endpoint for detailed status" -ForegroundColor White

Write-Host "`n🔧 Debug Endpoints:" -ForegroundColor Cyan
Write-Host "- GET $BASE_URL/api/v1/journal/debug/ai-diagnostic/$TEST_USER_ID" -ForegroundColor White
Write-Host "- POST $BASE_URL/api/v1/journal/debug/enable-ai-for-user" -ForegroundColor White 