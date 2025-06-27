#!/usr/bin/env powershell

# Test Journal Creation Fixes
# Tests the topic classification endpoint and verifies journal creation flow
# Run with: .\test_journal_creation_fix.ps1

Write-Host "🧪 Testing Journal Creation Fixes..." -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Green
Write-Host ""

$baseUrl = "https://pulsecheck-mobile-app-production.up.railway.app"
$headers = @{
    "Content-Type" = "application/json"
    "X-User-Id" = "user_test_fix_validation"
}

# Test 1: Health Check
Write-Host "1. Testing Backend Health..." -ForegroundColor Yellow
try {
    $health = Invoke-WebRequest -Uri "$baseUrl/health" -Method GET
    Write-Host "   ✅ Health: $($health.StatusCode)" -ForegroundColor Green
    $healthData = $health.Content | ConvertFrom-Json
    Write-Host "   📊 Status: $($healthData.status)" -ForegroundColor Cyan
} catch {
    Write-Host "   ❌ Health check failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""

# Test 2: NEW Topic Classification Endpoint (This was the missing one!)
Write-Host "2. Testing NEW Topic Classification Endpoint..." -ForegroundColor Yellow
try {
    $topicData = @{
        content = "I'm feeling really stressed about work deadlines and anxious about the meeting tomorrow"
    } | ConvertTo-Json

    $topics = Invoke-WebRequest -Uri "$baseUrl/api/v1/journal/ai/topic-classification" -Method POST -Body $topicData -Headers $headers
    Write-Host "   ✅ Topic Classification: $($topics.StatusCode)" -ForegroundColor Green
    $topicResult = $topics.Content | ConvertFrom-Json
    Write-Host "   🏷️  Detected Topics: $($topicResult.topics -join ', ')" -ForegroundColor Cyan
} catch {
    Write-Host "   ❌ Topic classification failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "   📄 Response: $($_.Exception.Response)" -ForegroundColor Gray
}

Write-Host ""

# Test 3: Journal Entry Creation (This should work now)
Write-Host "3. Testing Journal Entry Creation..." -ForegroundColor Yellow
try {
    $journalData = @{
        content = "Testing journal creation after fix. I'm feeling optimistic about the progress we're making!"
        mood_level = 7
        energy_level = 6
        stress_level = 3
        tags = @("testing", "progress")
        work_challenges = @()
        gratitude_items = @()
    } | ConvertTo-Json

    $journal = Invoke-WebRequest -Uri "$baseUrl/api/v1/journal/entries" -Method POST -Body $journalData -Headers $headers
    Write-Host "   ✅ Journal Creation: $($journal.StatusCode)" -ForegroundColor Green
    $journalResult = $journal.Content | ConvertFrom-Json
    Write-Host "   📝 Entry ID: $($journalResult.id)" -ForegroundColor Cyan
    Write-Host "   💭 Content Preview: $($journalResult.content.Substring(0, [Math]::Min(50, $journalResult.content.Length)))..." -ForegroundColor Cyan
    
    # Store entry ID for next test
    $entryId = $journalResult.id
    
} catch {
    Write-Host "   ❌ Journal creation failed: $($_.Exception.Message)" -ForegroundColor Red
    $entryId = $null
}

Write-Host ""

# Test 4: AI Response Generation (If journal creation worked)
if ($entryId) {
    Write-Host "4. Testing AI Response Generation..." -ForegroundColor Yellow
    try {
        $aiResponse = Invoke-WebRequest -Uri "$baseUrl/api/v1/journal/entries/$entryId/pulse" -Method GET -Headers $headers
        Write-Host "   ✅ AI Response: $($aiResponse.StatusCode)" -ForegroundColor Green
        $aiResult = $aiResponse.Content | ConvertFrom-Json
        Write-Host "   🤖 AI Message Preview: $($aiResult.message.Substring(0, [Math]::Min(80, $aiResult.message.Length)))..." -ForegroundColor Cyan
        Write-Host "   ⚡ Response Time: $($aiResult.response_time_ms)ms" -ForegroundColor Cyan
        Write-Host "   🎯 Confidence: $([Math]::Round($aiResult.confidence_score * 100))%" -ForegroundColor Cyan
    } catch {
        Write-Host "   ❌ AI response failed: $($_.Exception.Message)" -ForegroundColor Red
    }
} else {
    Write-Host "4. Skipping AI Response Test (no journal entry created)" -ForegroundColor Gray
}

Write-Host ""

# Test 5: Overall System Status
Write-Host "5. Checking Overall System Status..." -ForegroundColor Yellow
try {
    $stats = Invoke-WebRequest -Uri "$baseUrl/api/v1/journal/stats" -Method GET -Headers $headers
    Write-Host "   ✅ Journal Stats: $($stats.StatusCode)" -ForegroundColor Green
    $statsResult = $stats.Content | ConvertFrom-Json
    Write-Host "   📊 Total Entries: $($statsResult.total_entries)" -ForegroundColor Cyan
} catch {
    Write-Host "   ❌ Stats failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "🎯 Test Summary:" -ForegroundColor Green
Write-Host "- The main fixes were:" -ForegroundColor White
Write-Host "  1. Added missing /api/v1/journal/ai/topic-classification endpoint" -ForegroundColor White
Write-Host "  2. Fixed navigation route from /pulse-response to /pulse/:id" -ForegroundColor White
Write-Host ""
Write-Host "If Topic Classification and Journal Creation show ✅, the fixes worked!" -ForegroundColor Green
Write-Host "Run this with Railway logs open to see backend processing details." -ForegroundColor Gray
Write-Host "" 