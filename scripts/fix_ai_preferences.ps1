# Fix AI preferences for current user
# This script enables AI interactions by creating the necessary user_ai_preferences record

$baseUrl = "https://your-backend-url.railway.app"  # UPDATE THIS!

Write-Host "IMPORTANT: Please update the baseUrl with your Railway backend URL!" -ForegroundColor Yellow
Write-Host "You can find it in your Railway dashboard." -ForegroundColor Yellow
Write-Host "`nPress Enter to continue after updating the URL, or Ctrl+C to exit..." -ForegroundColor Cyan
Read-Host

# Get auth token
Write-Host "`nPlease provide your auth token (from browser DevTools):" -ForegroundColor Cyan
Write-Host "1. Open your app in the browser" -ForegroundColor Gray
Write-Host "2. Open DevTools (F12)" -ForegroundColor Gray
Write-Host "3. Go to Application/Storage -> Local Storage" -ForegroundColor Gray
Write-Host "4. Find and copy your auth token" -ForegroundColor Gray
Write-Host "`nPaste your auth token here: " -NoNewline -ForegroundColor Yellow
$authToken = Read-Host

$headers = @{
    "Authorization" = "Bearer $authToken"
    "Content-Type" = "application/json"
}

# Get current user info
Write-Host "`nGetting current user info..." -ForegroundColor Cyan
try {
    $userResponse = Invoke-RestMethod -Uri "$baseUrl/auth/me" -Headers $headers -Method Get
    $userId = $userResponse.id
    Write-Host "✅ User ID: $userId" -ForegroundColor Green
    Write-Host "✅ Email: $($userResponse.email)" -ForegroundColor Green
} catch {
    Write-Host "❌ Error getting user info: $_" -ForegroundColor Red
    Write-Host "Please check your auth token and try again." -ForegroundColor Yellow
    exit
}

# Enable AI for the user using the debug endpoint
Write-Host "`nEnabling AI for user..." -ForegroundColor Cyan
$enableData = @{
    user_id = $userId
    enable = $true
} | ConvertTo-Json

try {
    $enableResponse = Invoke-RestMethod -Uri "$baseUrl/journal/debug/enable-ai-for-user" `
        -Headers $headers `
        -Method Post `
        -Body $enableData
    
    Write-Host "✅ AI enabled successfully!" -ForegroundColor Green
    
    if ($enableResponse.preferences) {
        Write-Host "`nAI Preferences:" -ForegroundColor Cyan
        Write-Host "- AI Interactions Enabled: $($enableResponse.preferences.ai_interactions_enabled)" -ForegroundColor Green
        Write-Host "- AI Interaction Level: $($enableResponse.preferences.ai_interaction_level)" -ForegroundColor Green
        Write-Host "- User Tier: $($enableResponse.preferences.user_tier)" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ Error enabling AI: $_" -ForegroundColor Red
    Write-Host "`nTrying alternative approach..." -ForegroundColor Yellow
    
    # If debug endpoint fails, we might need to use Supabase directly
    Write-Host "`nThe debug endpoint might not be available. You'll need to manually insert the record in Supabase." -ForegroundColor Yellow
    Write-Host "`nRun this SQL in your Supabase SQL editor:" -ForegroundColor Cyan
    Write-Host @"

-- Enable AI for your user
INSERT INTO user_ai_preferences (
    user_id,
    ai_interactions_enabled,
    ai_interaction_level,
    user_tier,
    ai_engagement_score,
    response_frequency,
    preferred_personas,
    blocked_personas,
    max_response_length,
    tone_preference,
    premium_enabled
) VALUES (
    '$userId',
    true,
    'high',
    'premium',
    5.0,
    'active',
    ARRAY['pulse', 'sage', 'spark', 'anchor'],
    ARRAY[]::text[],
    'medium',
    'balanced',
    true
)
ON CONFLICT (user_id) 
DO UPDATE SET
    ai_interactions_enabled = true,
    ai_interaction_level = 'high',
    user_tier = 'premium',
    updated_at = NOW();

"@ -ForegroundColor White
}

# Test if AI is now working
Write-Host "`n`nTesting AI response generation..." -ForegroundColor Cyan
Write-Host "Creating a test journal entry..." -ForegroundColor Gray

$testEntry = @{
    content = "Testing AI responses - feeling hopeful about getting the AI personas working again!"
    mood_level = 7
    energy_level = 6
    stress_level = 4
    tags = @("test", "ai-fix")
} | ConvertTo-Json

try {
    $journalResponse = Invoke-RestMethod -Uri "$baseUrl/journal/entries" `
        -Headers $headers `
        -Method Post `
        -Body $testEntry
    
    Write-Host "✅ Journal entry created: $($journalResponse.id)" -ForegroundColor Green
    
    # Check if AI response was generated
    if ($journalResponse.ai_insights) {
        Write-Host "`n🎉 AI RESPONSE GENERATED!" -ForegroundColor Green
        Write-Host "Persona: $($journalResponse.ai_insights.persona_used)" -ForegroundColor Cyan
        Write-Host "Response: $($journalResponse.ai_insights.insight)" -ForegroundColor White
    } else {
        Write-Host "`n⚠️ No AI response in journal entry" -ForegroundColor Yellow
        
        # Try to fetch AI insights separately
        Start-Sleep -Seconds 2
        try {
            $insightsResponse = Invoke-RestMethod -Uri "$baseUrl/journal/entries/$($journalResponse.id)/ai-insights" `
                -Headers $headers `
                -Method Get
            
            Write-Host "`n🎉 AI INSIGHTS FOUND!" -ForegroundColor Green
            Write-Host "Persona: $($insightsResponse.persona_used)" -ForegroundColor Cyan
            Write-Host "Response: $($insightsResponse.ai_response)" -ForegroundColor White
        } catch {
            Write-Host "No AI insights found for entry" -ForegroundColor Yellow
        }
    }
} catch {
    Write-Host "❌ Error creating test entry: $_" -ForegroundColor Red
}

Write-Host "`n✅ Done! Try creating a new journal entry in your app." -ForegroundColor Green
Write-Host "If AI still doesn't work, check the Railway logs for errors." -ForegroundColor Yellow 