# Test script for AI multi-persona functionality
# This script tests both reply threading and multi-persona responses

$baseUrl = "https://pulsecheck-mobile-app-production.up.railway.app"
$testUserId = "6abe6283-5dd2-46d6-995a-d876a06a55f7"

Write-Host "🧪 Testing AI Multi-Persona Functionality" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green

# Test 1: Create a new journal entry
Write-Host "`n1. Creating test journal entry..." -ForegroundColor Yellow
$journalData = @{
    content = "I'm feeling really stressed about work today. There's so much pressure and I'm not sure how to handle it all. My energy is low and I'm feeling overwhelmed."
    mood_level = 3
    energy_level = 2
    stress_level = 8
    focus_areas = @("work_stress", "overwhelm")
} | ConvertTo-Json

try {
    $journalResponse = Invoke-RestMethod -Uri "$baseUrl/api/v1/journal/entries" -Method Post -Body $journalData -ContentType "application/json"
    $journalId = $journalResponse.id
    Write-Host "✅ Journal entry created: $journalId" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to create journal entry: $_" -ForegroundColor Red
    exit 1
}

# Test 2: Trigger multi-persona AI responses
Write-Host "`n2. Triggering multi-persona AI responses..." -ForegroundColor Yellow
try {
    $aiResponse = Invoke-RestMethod -Uri "$baseUrl/api/v1/manual-ai-response/respond-to-journal/$journalId" -Method Post -Body (@{user_id = $testUserId} | ConvertTo-Json) -ContentType "application/json"
    Write-Host "✅ AI responses generated:" -ForegroundColor Green
    
    if ($aiResponse.ai_responses) {
        foreach ($response in $aiResponse.ai_responses) {
            Write-Host "  - $($response.persona_name): $($response.text.Substring(0, [Math]::Min(100, $response.text.Length)))..." -ForegroundColor Cyan
        }
    } else {
        Write-Host "  - Single response: $($aiResponse.ai_comment.text.Substring(0, [Math]::Min(100, $aiResponse.ai_comment.text.Length)))..." -ForegroundColor Cyan
    }
} catch {
    Write-Host "❌ Failed to generate AI responses: $_" -ForegroundColor Red
    exit 1
}

# Test 3: Submit a user reply
Write-Host "`n3. Submitting user reply to AI..." -ForegroundColor Yellow
$replyData = @{
    reply_text = "Thank you for the support! What would you say are key ways to help myself find balance in days with unexpected moments?"
} | ConvertTo-Json

try {
    $replyResponse = Invoke-RestMethod -Uri "$baseUrl/api/v1/journal/entries/$journalId/reply" -Method Post -Body $replyData -ContentType "application/json"
    Write-Host "✅ User reply submitted: $($replyResponse.reply_id)" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to submit user reply: $_" -ForegroundColor Red
    exit 1
}

# Test 4: Check for AI response to user comment
Write-Host "`n4. Checking for AI response to user comment..." -ForegroundColor Yellow
Start-Sleep -Seconds 3  # Wait for AI response

try {
    $repliesResponse = Invoke-RestMethod -Uri "$baseUrl/api/v1/journal/entries/$journalId/replies" -Method Get
    Write-Host "✅ Retrieved replies:" -ForegroundColor Green
    
    $userReplies = $repliesResponse.replies | Where-Object { $_.is_ai_response -eq $false }
    $aiReplies = $repliesResponse.replies | Where-Object { $_.is_ai_response -eq $true }
    
    Write-Host "  - User replies: $($userReplies.Count)" -ForegroundColor Cyan
    Write-Host "  - AI replies: $($aiReplies.Count)" -ForegroundColor Cyan
    
    if ($aiReplies.Count -gt 0) {
        foreach ($aiReply in $aiReplies) {
            Write-Host "  - AI ($($aiReply.ai_persona)): $($aiReply.reply_text.Substring(0, [Math]::Min(100, $aiReply.reply_text.Length)))..." -ForegroundColor Magenta
        }
    }
} catch {
    Write-Host "❌ Failed to retrieve replies: $_" -ForegroundColor Red
    exit 1
}

# Test 5: Check AI monitoring status
Write-Host "`n5. Checking AI monitoring status..." -ForegroundColor Yellow
try {
    $monitoringResponse = Invoke-RestMethod -Uri "$baseUrl/api/v1/ai-monitoring/last-action/$testUserId" -Method Get
    Write-Host "✅ AI monitoring status:" -ForegroundColor Green
    Write-Host "  - Last action: $($monitoringResponse.last_ai_action)" -ForegroundColor Cyan
    Write-Host "  - Status: $($monitoringResponse.status)" -ForegroundColor Cyan
} catch {
    Write-Host "❌ Failed to get monitoring status: $_" -ForegroundColor Red
}

Write-Host "`n🎉 Multi-persona AI test completed!" -ForegroundColor Green
Write-Host "Journal ID for manual testing: $journalId" -ForegroundColor Yellow 