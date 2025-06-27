# Simple Journal Test Script
param(
    [string]$BaseUrl = "https://passionate-project-v6-mobile-app-production.up.railway.app"
)

Write-Host "Testing Journal Functionality..." -ForegroundColor Yellow
Write-Host "Base URL: $BaseUrl" -ForegroundColor Cyan

# Test 1: Check API connectivity
Write-Host "`n1. Testing API connectivity..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "$BaseUrl/api/v1/debug/system/status" -Method GET -TimeoutSec 10
    Write-Host "   SUCCESS: API is accessible (Status: $($response.StatusCode))" -ForegroundColor Green
    
    $systemData = $response.Content | ConvertFrom-Json
    if ($systemData.database_status) {
        Write-Host "   Database Status: $($systemData.database_status)" -ForegroundColor Green
    }
} catch {
    Write-Host "   ERROR: API connectivity failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Test 2: Authentication
Write-Host "`n2. Testing authentication..." -ForegroundColor Yellow
$testUser = @{
    email = "test@example.com"
    password = "testpassword123"
}

$accessToken = $null
try {
    $authBody = $testUser | ConvertTo-Json
    $authResponse = Invoke-WebRequest -Uri "$BaseUrl/api/v1/auth/signin" -Method POST -Body $authBody -ContentType "application/json" -ErrorAction Stop
    
    if ($authResponse.StatusCode -eq 200) {
        $authData = $authResponse.Content | ConvertFrom-Json
        if ($authData.access_token) {
            Write-Host "   SUCCESS: Authentication successful" -ForegroundColor Green
            $accessToken = $authData.access_token
            $headers = @{
                "Authorization" = "Bearer $accessToken"
                "Content-Type" = "application/json"
            }
        } else {
            Write-Host "   ERROR: No access token in response" -ForegroundColor Red
        }
    }
} catch {
    Write-Host "   INFO: Authentication failed, trying to create user..." -ForegroundColor Yellow
    try {
        $signupResponse = Invoke-WebRequest -Uri "$BaseUrl/api/v1/auth/signup" -Method POST -Body $authBody -ContentType "application/json" -ErrorAction Stop
        Write-Host "   SUCCESS: Test user created" -ForegroundColor Green
        
        Start-Sleep -Seconds 2
        $authResponse = Invoke-WebRequest -Uri "$BaseUrl/api/v1/auth/signin" -Method POST -Body $authBody -ContentType "application/json" -ErrorAction Stop
        $authData = $authResponse.Content | ConvertFrom-Json
        $accessToken = $authData.access_token
        $headers = @{
            "Authorization" = "Bearer $accessToken"
            "Content-Type" = "application/json"
        }
        Write-Host "   SUCCESS: Authentication with new user successful" -ForegroundColor Green
    } catch {
        Write-Host "   ERROR: Could not authenticate: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Test 3: Create journal entry
Write-Host "`n3. Testing journal entry creation..." -ForegroundColor Yellow
$entryId = $null
if ($accessToken) {
    $testEntry = @{
        content = "Test journal entry created at $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss'). Testing journal functionality."
        mood_level = 7
        energy_level = 6
        stress_level = 4
        tags = @("test", "debug")
    }
    
    try {
        $entryBody = $testEntry | ConvertTo-Json
        $createResponse = Invoke-WebRequest -Uri "$BaseUrl/api/v1/journal/entries" -Method POST -Body $entryBody -Headers $headers -ErrorAction Stop
        
        Write-Host "   SUCCESS: Journal entry created (Status: $($createResponse.StatusCode))" -ForegroundColor Green
        $createdEntry = $createResponse.Content | ConvertFrom-Json
        $entryId = $createdEntry.id
        Write-Host "   Entry ID: $entryId" -ForegroundColor Cyan
    } catch {
        Write-Host "   ERROR: Journal creation failed: $($_.Exception.Message)" -ForegroundColor Red
        if ($_.Exception.Response) {
            $errorStream = $_.Exception.Response.GetResponseStream()
            $reader = New-Object System.IO.StreamReader($errorStream)
            $errorBody = $reader.ReadToEnd()
            Write-Host "   Error details: $errorBody" -ForegroundColor Gray
        }
    }
} else {
    Write-Host "   SKIPPED: No authentication token" -ForegroundColor Yellow
}

# Test 4: Retrieve journal entries
Write-Host "`n4. Testing journal entry retrieval..." -ForegroundColor Yellow
if ($accessToken) {
    try {
        $entriesUrl = $BaseUrl + "/api/v1/journal/entries?page=1" + "&" + "per_page=10"
        $listResponse = Invoke-WebRequest -Uri $entriesUrl -Method GET -Headers $headers -ErrorAction Stop
        
        Write-Host "   SUCCESS: Journal entries retrieved (Status: $($listResponse.StatusCode))" -ForegroundColor Green
        $entriesData = $listResponse.Content | ConvertFrom-Json
        
        if ($entriesData.entries) {
            Write-Host "   Found $($entriesData.entries.Count) entries (Total: $($entriesData.total))" -ForegroundColor Green
            if ($entriesData.entries.Count -gt 0) {
                $latestEntry = $entriesData.entries[0]
                Write-Host "   Latest entry ID: $($latestEntry.id)" -ForegroundColor Cyan
                Write-Host "   Latest entry created: $($latestEntry.created_at)" -ForegroundColor Cyan
            }
        } else {
            Write-Host "   WARNING: No entries found in response" -ForegroundColor Yellow
            Write-Host "   Response: $($entriesData | ConvertTo-Json -Depth 2)" -ForegroundColor Gray
        }
    } catch {
        Write-Host "   ERROR: Journal retrieval failed: $($_.Exception.Message)" -ForegroundColor Red
        if ($_.Exception.Response) {
            $errorStream = $_.Exception.Response.GetResponseStream()
            $reader = New-Object System.IO.StreamReader($errorStream)
            $errorBody = $reader.ReadToEnd()
            Write-Host "   Error details: $errorBody" -ForegroundColor Gray
        }
    }
} else {
    Write-Host "   SKIPPED: No authentication token" -ForegroundColor Yellow
}

# Test 5: Journal stats
Write-Host "`n5. Testing journal stats..." -ForegroundColor Yellow
if ($accessToken) {
    try {
        $statsResponse = Invoke-WebRequest -Uri "$BaseUrl/api/v1/journal/stats" -Method GET -Headers $headers -ErrorAction Stop
        
        Write-Host "   SUCCESS: Journal stats retrieved (Status: $($statsResponse.StatusCode))" -ForegroundColor Green
        $stats = $statsResponse.Content | ConvertFrom-Json
        Write-Host "   Total entries: $($stats.total_entries)" -ForegroundColor Cyan
        Write-Host "   Average mood: $($stats.average_mood)" -ForegroundColor Cyan
        Write-Host "   Last entry: $($stats.last_entry_date)" -ForegroundColor Cyan
    } catch {
        Write-Host "   ERROR: Journal stats failed: $($_.Exception.Message)" -ForegroundColor Red
    }
} else {
    Write-Host "   SKIPPED: No authentication token" -ForegroundColor Yellow
}

Write-Host "`nTest completed!" -ForegroundColor Magenta
if ($accessToken) {
    Write-Host "Authentication: WORKING" -ForegroundColor Green
} else {
    Write-Host "Authentication: FAILED" -ForegroundColor Red
} 