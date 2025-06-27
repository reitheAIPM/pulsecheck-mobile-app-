#!/usr/bin/env powershell

# Test AI Response Debug - Trigger the exact failing flow
# Run this while monitoring Railway logs to see server errors
# Usage: .\test_ai_response_debug.ps1

Write-Host "Testing AI Response Generation Flow..." -ForegroundColor Green
Write-Host "====================================" -ForegroundColor Green
Write-Host ""

$baseUrl = "https://pulsecheck-mobile-app-production.up.railway.app"
$jwtToken = "eyJhbGciOiJIUzI1NiIsImtpZCI6Ik4yRzUyWTEzNHViM2gzOHUiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL3F3cHdsdWJ4aHR1enZtdmFqampyLnN1cGFiYXNlLmNvL2F1dGgvdjEiLCJzdWIiOiI2MWU2N2EzNC1iMWU2LTRlYmItOTFiOC1hMjQ0YjFjYTAzMTQiLCJhdWQiOiJhdXRoZW50aWNhdGVkIiwiZXhwIjoxNzUwOTAyNjY0LCJpYXQiOjE3NTA4OTkwNjQsImVtYWlsIjoicmVpLmFsZTAxKzVAZ21haWwuY29tIiwicGhvbmUiOiIiLCJhcHBfbWV0YWRhdGEiOnsicHJvdmlkZXIiOiJlbWFpbCIsInByb3ZpZGVycyI6WyJlbWFpbCJdfSwidXNlcl9tZXRhZGF0YSI6eyJlbWFpbCI6InJlaS5hbGUwMSs1QGdtYWlsLmNvbSIsImVtYWlsX3ZlcmlmaWVkIjp0cnVlLCJuYW1lIjoiUmVpNSIsInBob25lX3ZlcmlmaWVkIjpmYWxzZSwic3ViIjoiNjFlNjdhMzQtYjFlNi00ZWJiLTkxYjgtYTI0NGIxY2EwMzE0IiwidGVjaF9yb2xlIjoidXNlciJ9LCJyb2xlIjoiYXV0aGVudGljYXRlZCIsImFhbCI6ImFhbDEiLCJhbXIiOlt7Im1ldGhvZCI6InBhc3N3b3JkIiwidGltZXN0YW1wIjoxNzUwODg5NDgyfV0sInNlc3Npb25faWQiOiJjMmE3NmY0ZC04MDg5LTQ2NWItOGI2Yy1hOWQzMzhhNmE4MTMiLCJpc19hbm9ueW1vdXMiOmZhbHNlfQ.hJauRWvbjS3PshgRWo3kfS3ToFYv0GUZyU29p0n-0sA"
$entryId = "3f2728af-fe96-4825-b612-d43b3f9a5801"

$headers = @{
    "Content-Type" = "application/json"
    "Authorization" = "Bearer $jwtToken"
}

Write-Host "Entry ID: $entryId" -ForegroundColor Cyan
Write-Host "Testing with real user JWT token..." -ForegroundColor Cyan
Write-Host ""

# Step 1: Try to fetch the journal entry (this was failing with 500)
Write-Host "1. Fetching journal entry..." -ForegroundColor Yellow
try {
    $journalResponse = Invoke-WebRequest -Uri "$baseUrl/api/v1/journal/entries/$entryId" -Method GET -Headers $headers
    Write-Host "   [SUCCESS] Journal Entry: $($journalResponse.StatusCode)" -ForegroundColor Green
    
    # Step 2: Try to generate AI response (this is what should happen next)
    Write-Host "2. Generating AI response..." -ForegroundColor Yellow
    $aiResponse = Invoke-WebRequest -Uri "$baseUrl/api/v1/journal/entries/$entryId/pulse" -Method POST -Headers $headers
    Write-Host "   [SUCCESS] AI Response: $($aiResponse.StatusCode)" -ForegroundColor Green
    
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
Write-Host "Test complete. Check Railway logs for server-side errors." -ForegroundColor Green 