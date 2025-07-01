# AI Interaction Testing Script for PulseCheck
# Tests AI endpoints with sample data for debugging
# Run: .\test_ai_interactions.ps1

Write-Host "🤖 PulseCheck AI Interaction Testing" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""

$BASE_URL = "https://pulsecheck-mobile-app-production.up.railway.app"

# Test 1: Check if AI Services are available
Write-Host "🔍 Testing AI Service Availability..." -ForegroundColor Yellow
try {
    $health = curl.exe -s "$BASE_URL/health" | ConvertFrom-Json
    Write-Host "✅ Backend is healthy" -ForegroundColor Green
} catch {
    Write-Host "❌ Backend not accessible - stopping tests" -ForegroundColor Red
    exit
}

# Test 2: Check Scheduler Status
Write-Host ""
Write-Host "🔍 Testing AI Scheduler..." -ForegroundColor Yellow
try {
    $scheduler_status = curl.exe -s "$BASE_URL/api/v1/scheduler/status"
    if ($scheduler_status -match "running" -or $scheduler_status -match "active") {
        Write-Host "✅ Scheduler appears to be running" -ForegroundColor Green
    } elseif ($scheduler_status -match "Not Found" -or $scheduler_status -match "404") {
        Write-Host "⚠️  Scheduler endpoint not found - may need to be started" -ForegroundColor Orange
    } else {
        Write-Host "⚠️  Scheduler status: $scheduler_status" -ForegroundColor Orange
    }
} catch {
    Write-Host "❌ Scheduler endpoint failed" -ForegroundColor Red
}

# Test 3: Check AI Proactive Opportunities
Write-Host ""
Write-Host "🔍 Testing Proactive AI..." -ForegroundColor Yellow
try {
    $opportunities = curl.exe -s "$BASE_URL/api/v1/proactive-ai/opportunities"
    if ($opportunities -match "Not Found") {
        Write-Host "⚠️  AI Opportunities endpoint not found (needs auth?)" -ForegroundColor Orange
    } elseif ($opportunities -match "unauthorized" -or $opportunities -match "401") {
        Write-Host "⚠️  AI endpoint requires authentication" -ForegroundColor Orange
    } else {
        Write-Host "✅ AI Opportunities endpoint responding" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ AI Opportunities failed" -ForegroundColor Red
}

# Test 4: Test Journal Entry Creation (Mock)
Write-Host ""
Write-Host "🔍 Testing Journal Entry Creation..." -ForegroundColor Yellow
Write-Host "⚠️  Note: This requires valid authentication tokens" -ForegroundColor Orange
Write-Host "   For manual testing, use the frontend at:" -ForegroundColor Gray
Write-Host "   https://pulsecheck-mobile.vercel.app/" -ForegroundColor Gray

# Test 5: Environment Variables Check
Write-Host ""
Write-Host "🔍 Checking AI-related Environment..." -ForegroundColor Yellow
try {
    $db_status = curl.exe -s "$BASE_URL/api/v1/database/comprehensive-status" | ConvertFrom-Json
    if ($db_status.railway_environment.SUPABASE_SERVICE_ROLE_KEY -eq "✅ Set") {
        Write-Host "✅ Service Role Key available (needed for AI)" -ForegroundColor Green
    } else {
        Write-Host "❌ Service Role Key missing (AI won't work)" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Could not check environment" -ForegroundColor Red
}

Write-Host ""
Write-Host "=================================="
Write-Host "🎯 AI TESTING SUMMARY" -ForegroundColor Cyan
Write-Host ""
Write-Host "For full AI testing, you need:" -ForegroundColor Yellow
Write-Host "1. ✅ Backend healthy (confirmed)"
Write-Host "2. ⚠️  Valid user authentication"
Write-Host "3. ⚠️  Journal entries to trigger AI responses"
Write-Host "4. ⚠️  AI scheduler running"
Write-Host ""
Write-Host "💡 MANUAL TESTING STEPS:" -ForegroundColor Green
Write-Host "1. Go to: https://pulsecheck-mobile.vercel.app/"
Write-Host "2. Sign up/login with a test account"
Write-Host "3. Create a journal entry (>10 characters)"
Write-Host "4. Wait 5-10 minutes for AI response"
Write-Host "5. Check if AI personas commented"
Write-Host ""
Write-Host "🔧 DEBUGGING OPTIONS:" -ForegroundColor Cyan
Write-Host "- Check Railway logs for AI processing"
Write-Host "- Monitor Supabase realtime for new AI responses"
Write-Host "- Use browser dev tools to see API calls"
Write-Host "" 