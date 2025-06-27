#!/usr/bin/env powershell

# Test Create and Fetch Journal - Full Flow Test
# Creates a journal entry with real user JWT, then tests AI response
# Usage: .\test_create_and_fetch_journal.ps1

Write-Host "Testing Full Journal Creation and AI Response Flow..." -ForegroundColor Green
Write-Host "===================================================" -ForegroundColor Green
Write-Host ""

$baseUrl = "https://pulsecheck-mobile-app-production.up.railway.app"
$jwtToken = "eyJhbGciOiJIUzI1NiIsImtpZCI6Ik4yRzUyWTEzNHViM2gzOHUiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL3F3cHdsdWJ4aHR1enZtdmFqampyLnN1cGFiYXNlLmNvL2F1dGgvdjEiLCJzdWIiOiI2MWU2N2EzNC1iMWU2LTRlYmItOTFiOC1hMjQ0YjFjYTAzMTQiLCJhdWQiOiJhdXRoZW50aWNhdGVkIiwiZXhwIjoxNzUwOTAyNjY0LCJpYXQiOjE3NTA4OTkwNjQsImVtYWlsIjoicmVpLmFsZTAxKzVAZ21haWwuY29tIiwicGhvbmUiOiIiLCJhcHBfbWV0YWRhdGEiOnsicHJvdmlkZXIiOiJlbWFpbCIsInByb3ZpZGVycyI6WyJlbWFpbCJdfSwidXNlcl9tZXRhZGF0YSI6eyJlbWFpbCI6InJlaS5hbGUwMSs1QGdtYWlsLmNvbSIsImVtYWlsX3ZlcmlmaWVkIjp0cnVlLCJuYW1lIjoiUmVpNSIsInBob25lX3ZlcmlmaWVkIjpmYWxzZSwic3ViIjoiNjFlNjdhMzQtYjFlNi00ZWJiLTkxYjgtYTI0NGIxY2EwMzE0IiwidGVjaF9yb2xlIjoidXNlciJ9LCJyb2xlIjoiYXV0aGVudGljYXRlZCIsImFhbCI6ImFhbDEiLCJhbXIiOlt7Im1ldGhvZCI6InBhc3N3b3JkIiwidGltZXN0YW1wIjoxNzUwODg5NDgyfV0sInNlc3Npb25faWQiOiJjMmE3NmY0ZC04MDg5LTQ2NWItOGI2Yy1hOWQzMzhhNmE4MTMiLCJpc19hbm9ueW1vdXMiOmZhbHNlfQ.hJauRWvbjS3PshgRWo3kfS3ToFYv0GUZyU29p0n-0sA"

$headers = @{
    "Content-Type" = "application/json"
    "Authorization" = "Bearer $jwtToken"
}

# Step 1: Create a new journal entry
Write-Host "1. Creating new journal entry..." -ForegroundColor Yellow
$journalData = @{
    content = "Testing the AI response generation flow. I'm feeling excited about debugging this issue!"
    mood_level = 8
    energy_level = 7
    stress_level = 3
    tags = @("debugging", "development")
} | ConvertTo-Json

try {
    $createResponse = Invoke-WebRequest -Uri "$baseUrl/api/v1/journal/entries" -Method POST -Headers $headers -Body $journalData
    Write-Host "   [SUCCESS] Journal Created: $($createResponse.StatusCode)" -ForegroundColor Green
    
    $journalEntry = $createResponse.Content | ConvertFrom-Json
    $entryId = $journalEntry.id
    Write-Host "   Entry ID: $entryId" -ForegroundColor Cyan
    
    # Wait a moment for database consistency
    Start-Sleep -Seconds 2
    
    # Step 2: Fetch the journal entry
    Write-Host "2. Fetching journal entry..." -ForegroundColor Yellow
    $fetchResponse = Invoke-WebRequest -Uri "$baseUrl/api/v1/journal/entries/$entryId" -Method GET -Headers $headers
    Write-Host "   [SUCCESS] Journal Fetched: $($fetchResponse.StatusCode)" -ForegroundColor Green
    
    # Step 3: Generate AI response
    Write-Host "3. Generating AI response..." -ForegroundColor Yellow
    $aiResponse = Invoke-WebRequest -Uri "$baseUrl/api/v1/journal/entries/$entryId/pulse" -Method POST -Headers $headers
    Write-Host "   [SUCCESS] AI Response: $($aiResponse.StatusCode)" -ForegroundColor Green
    
    $aiData = $aiResponse.Content | ConvertFrom-Json
    Write-Host ""
    Write-Host "AI Response Preview:" -ForegroundColor Green
    Write-Host "Title: $($aiData.title)" -ForegroundColor Cyan
    Write-Host "Message: $($aiData.message.Substring(0, [Math]::Min(100, $aiData.message.Length)))..." -ForegroundColor Cyan
    
} catch {
    Write-Host "   [ERROR] Status: $($_.Exception.Response.StatusCode)" -ForegroundColor Red
    Write-Host "   [ERROR] Message: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.Exception.Response) {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $responseBody = $reader.ReadToEnd()
        Write-Host "   [ERROR] Response: $responseBody" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "Test complete. Check Railway logs for any server-side issues." -ForegroundColor Green 