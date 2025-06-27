# Quick Journal RLS Test
Write-Host "TESTING JOURNAL RLS FUNCTIONALITY" -ForegroundColor Magenta
Write-Host "=" * 35

$BaseUrl = "https://pulsecheck-mobile-app-production.up.railway.app"

# Step 1: Create test user
Write-Host "`n1. Creating test user..." -ForegroundColor Yellow
$testUser = @{
    email = "quick-test-$(Get-Random -Maximum 999)@test.com"
    password = "testpass123"
} | ConvertTo-Json

try {
    $authResponse = Invoke-RestMethod "$BaseUrl/api/v1/auth/signup" -Method POST -Body $testUser -ContentType "application/json" -TimeoutSec 15
    $token = $authResponse.access_token
    
    if ($token) {
        Write-Host "  SUCCESS: User created, token received" -ForegroundColor Green
        Write-Host "  Token length: $($token.Length)" -ForegroundColor Gray
        
        # Step 2: Create journal entry
        Write-Host "`n2. Creating journal entry..." -ForegroundColor Yellow
        $journalData = @{
            content = "Quick test entry at $(Get-Date)"
            mood_level = 7
            energy_level = 6
            stress_level = 4
        } | ConvertTo-Json
        
        $createResponse = Invoke-RestMethod "$BaseUrl/api/v1/journal/entries" -Method POST -Body $journalData -ContentType "application/json" -Headers @{ Authorization = "Bearer $token" } -TimeoutSec 15
        
        if ($createResponse.id) {
            Write-Host "  SUCCESS: Journal entry created with ID: $($createResponse.id)" -ForegroundColor Green
            
            # Step 3: Retrieve entries
            Write-Host "`n3. Retrieving journal entries..." -ForegroundColor Yellow
            $entriesResponse = Invoke-RestMethod "$BaseUrl/api/v1/journal/entries" -Headers @{ Authorization = "Bearer $token" } -TimeoutSec 15
            
            Write-Host "  Total entries returned: $($entriesResponse.total)" -ForegroundColor Cyan
            Write-Host "  Entries array length: $($entriesResponse.entries.Count)" -ForegroundColor Cyan
            
            if ($entriesResponse.total -gt 0) {
                Write-Host "  SUCCESS: Journal RLS is working correctly!" -ForegroundColor Green
                Write-Host "  Latest entry content: $($entriesResponse.entries[0].content.Substring(0, [Math]::Min(50, $entriesResponse.entries[0].content.Length)))" -ForegroundColor Gray
            } else {
                Write-Host "  FAILED: Journal RLS BROKEN - No entries returned despite creation" -ForegroundColor Red
                Write-Host "  This indicates an RLS authentication issue" -ForegroundColor Red
            }
        } else {
            Write-Host "  FAILED: Journal entry creation failed" -ForegroundColor Red
        }
    } else {
        Write-Host "  FAILED: No token received from signup" -ForegroundColor Red
    }
} catch {
    Write-Host "  FAILED: Error in journal test - $($_.Exception.Message)" -ForegroundColor Red
    if ($_.Exception.Response) {
        Write-Host "  Status Code: $($_.Exception.Response.StatusCode)" -ForegroundColor Red
    }
}

Write-Host "`nQuick journal test complete!" -ForegroundColor Green 