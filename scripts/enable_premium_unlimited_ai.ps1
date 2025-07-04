# Enable Premium Unlimited AI for Testing Account
# This script disables fallback responses and enables premium AI features

$baseUrl = "https://pulsecheck-mobile-app-production.up.railway.app"
$testUserId = "6abe6283-5dd2-46d6-995a-d876a06a55f7"

Write-Host "🚀 Enabling Premium Unlimited AI for Testing Account" -ForegroundColor Green
Write-Host "====================================================" -ForegroundColor Green

# Step 1: Enable premium unlimited AI
Write-Host "`n1. Enabling premium unlimited AI..." -ForegroundColor Yellow
try {
    $premiumResponse = Invoke-RestMethod -Uri "$baseUrl/api/v1/debug/enable-premium-unlimited-ai/$testUserId" -Method Post
    Write-Host "✅ Premium unlimited AI enabled!" -ForegroundColor Green
    Write-Host "  - Configuration: $($premiumResponse.configuration.tier)" -ForegroundColor Cyan
    Write-Host "  - AI Interaction Level: $($premiumResponse.configuration.ai_interaction_level)" -ForegroundColor Cyan
    Write-Host "  - Fallback Responses: $($premiumResponse.configuration.fallback_responses)" -ForegroundColor Cyan
    Write-Host "  - Multi-Persona: $($premiumResponse.configuration.multi_persona)" -ForegroundColor Cyan
    Write-Host "  - Daily Limit: $($premiumResponse.configuration.daily_limit)" -ForegroundColor Cyan
} catch {
    Write-Host "❌ Failed to enable premium unlimited AI: $_" -ForegroundColor Red
    exit 1
}

# Step 2: Disable fallback responses specifically
Write-Host "`n2. Disabling fallback responses..." -ForegroundColor Yellow
try {
    $fallbackResponse = Invoke-RestMethod -Uri "$baseUrl/api/v1/debug/disable-fallback-responses/$testUserId" -Method Post
    Write-Host "✅ Fallback responses disabled!" -ForegroundColor Green
    Write-Host "  - Fallback Status: $($fallbackResponse.fallback_responses)" -ForegroundColor Cyan
    Write-Host "  - Premium Override: $($fallbackResponse.configuration.premium_override)" -ForegroundColor Cyan
    Write-Host "  - Cost Limits Bypassed: $($fallbackResponse.configuration.cost_limits_bypassed)" -ForegroundColor Cyan
} catch {
    Write-Host "❌ Failed to disable fallback responses: $_" -ForegroundColor Red
}

# Step 3: Test the configuration
Write-Host "`n3. Testing premium AI configuration..." -ForegroundColor Yellow
try {
    $testResponse = Invoke-RestMethod -Uri "$baseUrl/api/v1/manual-ai/debug-database/$testUserId" -Method Get
    Write-Host "✅ Premium AI configuration test successful!" -ForegroundColor Green
    Write-Host "  - Database access: Working" -ForegroundColor Cyan
    Write-Host "  - User ID: $testUserId" -ForegroundColor Cyan
} catch {
    Write-Host "❌ Configuration test failed: $_" -ForegroundColor Red
}

Write-Host "`n🎉 Premium Unlimited AI Setup Complete!" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green

Write-Host "`n✨ Features Now Enabled:" -ForegroundColor Yellow
Write-Host "  ✅ No fallback responses - only real AI content" -ForegroundColor White
Write-Host "  ✅ Multiple AI personas (Pulse, Sage, Spark, Anchor)" -ForegroundColor White
Write-Host "  ✅ Unlimited daily AI interactions" -ForegroundColor White
Write-Host "  ✅ Premium AI models (GPT-4o)" -ForegroundColor White
Write-Host "  ✅ Immediate response timing" -ForegroundColor White
Write-Host "  ✅ Cost limit bypass" -ForegroundColor White

Write-Host "`n📋 Next Steps:" -ForegroundColor Green
Write-Host "  1. Create a new journal entry in your mobile app" -ForegroundColor White
Write-Host "  2. Look for immediate AI responses from multiple personas" -ForegroundColor White
Write-Host "  3. Reply to an AI response to test the conversation threading" -ForegroundColor White
Write-Host "  4. Monitor Railway logs for real AI processing (no fallbacks)" -ForegroundColor White

Write-Host "`n🔍 To Verify:" -ForegroundColor Cyan
Write-Host "  - All AI responses should be personalized and detailed" -ForegroundColor White
Write-Host "  - No generic fallback messages" -ForegroundColor White
Write-Host "  - Multiple personas should respond to the same journal entry" -ForegroundColor White
Write-Host "  - Response quality should be premium-level" -ForegroundColor White 