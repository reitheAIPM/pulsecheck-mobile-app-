#!/usr/bin/env powershell

# Direct AI Response Test
# Tests the Pulse AI response generation with a real journal entry
# Run with: .\test_ai_response_direct.ps1

param(
    [Parameter(Mandatory=$true)]
    [string]$JwtToken,
    
    [Parameter(Mandatory=$true)]
    [string]$EntryId
)

Write-Host "Testing AI Response Generation Directly..." -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Entry ID: $EntryId" -ForegroundColor Cyan
Write-Host ""

$baseUrl = "https://pulsecheck-mobile-app-production.up.railway.app"
$headers = @{
    "Content-Type" = "application/json"
    "Authorization" = "Bearer $JwtToken"
}

# Test 1: Verify the journal entry exists
Write-Host "1. Verifying journal entry exists..." -ForegroundColor Yellow
try {
    $entry = Invoke-WebRequest -Uri "$baseUrl/api/v1/journal/entries/$EntryId" -Method GET -Headers $headers
    Write-Host "   [SUCCESS] Journal entry found: $($entry.StatusCode)" -ForegroundColor Green
    $entryData = $entry.Content | ConvertFrom-Json
    Write-Host "   Content: $($entryData.content.Substring(0, [Math]::Min(50, $entryData.content.Length)))..." -ForegroundColor Cyan
    Write-Host "   Created: $($entryData.created_at)" -ForegroundColor Cyan
} catch {
    Write-Host "   [FAILED] Journal entry not found: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "   Status Code: $($_.Exception.Response.StatusCode.value__)" -ForegroundColor Gray
    exit 1
}

Write-Host ""

# Test 2: Try to get AI response
Write-Host "2. Testing AI Response Generation..." -ForegroundColor Yellow
Write-Host "   Calling: GET $baseUrl/api/v1/journal/entries/$EntryId/pulse" -ForegroundColor Gray
$stopwatch = [System.Diagnostics.Stopwatch]::StartNew()

try {
    $aiResponse = Invoke-WebRequest -Uri "$baseUrl/api/v1/journal/entries/$EntryId/pulse" -Method GET -Headers $headers
    $stopwatch.Stop()
    
    Write-Host "   [SUCCESS] AI Response generated: $($aiResponse.StatusCode)" -ForegroundColor Green
    Write-Host "   Time taken: $($stopwatch.ElapsedMilliseconds)ms" -ForegroundColor Cyan
    
    $aiData = $aiResponse.Content | ConvertFrom-Json
    Write-Host "   Message: $($aiData.message.Substring(0, [Math]::Min(100, $aiData.message.Length)))..." -ForegroundColor Cyan
    Write-Host "   Confidence: $([Math]::Round($aiData.confidence_score * 100))%" -ForegroundColor Cyan
    Write-Host "   Response Time: $($aiData.response_time_ms)ms" -ForegroundColor Cyan
    
    if ($aiData.follow_up_question) {
        Write-Host "   Follow-up: $($aiData.follow_up_question)" -ForegroundColor Cyan
    }
    
    if ($aiData.suggested_actions -and $aiData.suggested_actions.Count -gt 0) {
        Write-Host "   Actions: $($aiData.suggested_actions -join ', ')" -ForegroundColor Cyan
    }
    
} catch {
    $stopwatch.Stop()
    Write-Host "   [FAILED] AI response generation failed after $($stopwatch.ElapsedMilliseconds)ms" -ForegroundColor Red
    Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Red
    
    if ($_.Exception.Response.StatusCode.value__ -eq 429) {
        Write-Host "   [RATE LIMIT] You've reached your daily AI response limit" -ForegroundColor Yellow
    } elseif ($_.Exception.Response.StatusCode.value__ -eq 500) {
        Write-Host "   [SERVER ERROR] The AI service encountered an error" -ForegroundColor Yellow
    } elseif ($_.Exception.Response.StatusCode.value__ -eq 504) {
        Write-Host "   [TIMEOUT] The AI response took too long to generate" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Instructions to get JWT Token:" -ForegroundColor Yellow
Write-Host "1. Open browser DevTools (F12) on the PulseCheck website" -ForegroundColor White
Write-Host "2. Go to Network tab" -ForegroundColor White
Write-Host "3. Create a journal entry or refresh the page" -ForegroundColor White
Write-Host "4. Look for any API request to the backend" -ForegroundColor White
Write-Host "5. Check the Request Headers for 'Authorization: Bearer <token>'" -ForegroundColor White
Write-Host "6. Copy the token (without 'Bearer ')" -ForegroundColor White
Write-Host ""
Write-Host "Example usage:" -ForegroundColor Yellow
Write-Host '.\test_ai_response_direct.ps1 -JwtToken "your-jwt-token-here" -EntryId "entry-id-here"' -ForegroundColor White
Write-Host "" 