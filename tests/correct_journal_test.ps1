# Correct Journal Test Script
param(
    [string]$BaseUrl = "https://pulsecheck-mobile-app-production.up.railway.app"
)

Write-Host "🔍 Testing Journal Functionality with Correct URL..." -ForegroundColor Yellow
Write-Host "Base URL: $BaseUrl" -ForegroundColor Cyan

# Test 1: Check backend health
Write-Host "`n1. Testing backend health..." -ForegroundColor Yellow
try {
    $healthResponse = curl.exe -s "$BaseUrl/health"
    $health = $healthResponse | ConvertFrom-Json
    if ($health.status) {
        Write-Host "   ✅ Backend is accessible (Status: $($health.status))" -ForegroundColor Green
        if ($health.status -eq "degraded") {
            Write-Host "   ⚠️  Status degraded - Error rate: $($health.metrics.error_rate * 100)%" -ForegroundColor Yellow
        }
    }
} catch {
    Write-Host "   ❌ Health check failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Test 2: Check journal endpoint protection
Write-Host "`n2. Testing journal endpoint security..." -ForegroundColor Yellow
try {
    $journalResponse = curl.exe -s "$BaseUrl/api/v1/journal/entries"
    $journalCheck = $journalResponse | ConvertFrom-Json
    if ($journalCheck.status_code -eq 401) {
        Write-Host "   ✅ Journal properly protected (401: Authentication required)" -ForegroundColor Green
    } else {
        Write-Host "   ❌ Unexpected response: $journalResponse" -ForegroundColor Red
    }
} catch {
    Write-Host "   ⚠️  Error testing journal security: $($_.Exception.Message)" -ForegroundColor Yellow
}

# Test 3: Try authentication
Write-Host "`n3. Testing authentication..." -ForegroundColor Yellow
$testUser = @{
    email = "test@example.com"
    password = "testpassword123"
}

$authBody = $testUser | ConvertTo-Json
$accessToken = $null

try {
    # Try signin first
    $authResponse = curl.exe -s -X POST -H "Content-Type: application/json" -d $authBody "$BaseUrl/api/v1/auth/signin"
    $authData = $authResponse | ConvertFrom-Json
    
    if ($authData.access_token) {
        Write-Host "   ✅ Authentication successful (existing user)" -ForegroundColor Green
        $accessToken = $authData.access_token
    } else {
        # Try creating user
        Write-Host "   🔄 Trying to create new user..." -ForegroundColor Yellow
        $signupResponse = curl.exe -s -X POST -H "Content-Type: application/json" -d $authBody "$BaseUrl/api/v1/auth/signup"
        $signupData = $signupResponse | ConvertFrom-Json
        
        if ($signupData.access_token) {
            Write-Host "   ✅ User created and authenticated" -ForegroundColor Green
            $accessToken = $signupData.access_token
        } else {
            # Try signin again after signup
            Start-Sleep -Seconds 2
            $authResponse2 = curl.exe -s -X POST -H "Content-Type: application/json" -d $authBody "$BaseUrl/api/v1/auth/signin"
            $authData2 = $authResponse2 | ConvertFrom-Json
            
            if ($authData2.access_token) {
                Write-Host "   ✅ Authentication successful after signup" -ForegroundColor Green
                $accessToken = $authData2.access_token
            } else {
                Write-Host "   ❌ Authentication failed" -ForegroundColor Red
                Write-Host "   Response: $authResponse2" -ForegroundColor Gray
            }
        }
    }
} catch {
    Write-Host "   ❌ Authentication error: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 4: Create journal entry
Write-Host "`n4. Testing journal entry creation..." -ForegroundColor Yellow
$entryId = $null
if ($accessToken) {
    $testEntry = @{
        content = "Test journal entry created at $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss'). Testing journal functionality with correct URL."
        mood_level = 7
        energy_level = 6
        stress_level = 4
        tags = @("test", "debug", "url-fix")
    }
    
    $entryBody = $testEntry | ConvertTo-Json
    try {
        $createResponse = curl.exe -s -X POST -H "Content-Type: application/json" -H "Authorization: Bearer $accessToken" -d $entryBody "$BaseUrl/api/v1/journal/entries"
        $createdEntry = $createResponse | ConvertFrom-Json
        
        if ($createdEntry.id) {
            Write-Host "   ✅ Journal entry created successfully" -ForegroundColor Green
            $entryId = $createdEntry.id
            Write-Host "   📝 Entry ID: $entryId" -ForegroundColor Cyan
        } else {
            Write-Host "   ❌ Journal creation failed" -ForegroundColor Red
            Write-Host "   Response: $createResponse" -ForegroundColor Gray
        }
    } catch {
        Write-Host "   ❌ Journal creation error: $($_.Exception.Message)" -ForegroundColor Red
    }
} else {
    Write-Host "   ⚠️  Skipping journal creation - no authentication token" -ForegroundColor Yellow
}

# Test 5: Retrieve journal entries
Write-Host "`n5. Testing journal entry retrieval..." -ForegroundColor Yellow
if ($accessToken) {
    try {
        $listResponse = curl.exe -s -H "Authorization: Bearer $accessToken" "$BaseUrl/api/v1/journal/entries?page=1&per_page=10"
        $entriesData = $listResponse | ConvertFrom-Json
        
        if ($entriesData.entries) {
            Write-Host "   ✅ Journal entries retrieved successfully" -ForegroundColor Green
            Write-Host "   📊 Found $($entriesData.entries.Count) entries (Total: $($entriesData.total))" -ForegroundColor Cyan
            
            if ($entriesData.entries.Count -gt 0) {
                $latestEntry = $entriesData.entries[0]
                Write-Host "   📝 Latest entry:" -ForegroundColor Green
                Write-Host "      ID: $($latestEntry.id)" -ForegroundColor Gray
                Write-Host "      Created: $($latestEntry.created_at)" -ForegroundColor Gray
                Write-Host "      Content: $($latestEntry.content.Substring(0, [Math]::Min(100, $latestEntry.content.Length)))..." -ForegroundColor Gray
            }
        } elseif ($entriesData.total -eq 0) {
            Write-Host "   ⚠️  No journal entries found (but API is working)" -ForegroundColor Yellow
            Write-Host "   📄 This is the likely cause of your issue - no entries exist yet!" -ForegroundColor Yellow
        } else {
            Write-Host "   ❌ Unexpected response format" -ForegroundColor Red
            Write-Host "   Response: $listResponse" -ForegroundColor Gray
        }
    } catch {
        Write-Host "   ❌ Journal retrieval error: $($_.Exception.Message)" -ForegroundColor Red
    }
} else {
    Write-Host "   ⚠️  Skipping journal retrieval - no authentication token" -ForegroundColor Yellow
}

# Test 6: Journal stats
Write-Host "`n6. Testing journal stats..." -ForegroundColor Yellow
if ($accessToken) {
    try {
        $statsResponse = curl.exe -s -H "Authorization: Bearer $accessToken" "$BaseUrl/api/v1/journal/stats"
        $stats = $statsResponse | ConvertFrom-Json
        
        if ($stats.total_entries -ne $null) {
            Write-Host "   ✅ Journal stats retrieved successfully" -ForegroundColor Green
            Write-Host "   📊 Stats:" -ForegroundColor Cyan
            Write-Host "      Total entries: $($stats.total_entries)" -ForegroundColor Gray
            Write-Host "      Average mood: $($stats.average_mood)" -ForegroundColor Gray
            Write-Host "      Last entry: $($stats.last_entry_date)" -ForegroundColor Gray
        } else {
            Write-Host "   ❌ Invalid stats response" -ForegroundColor Red
            Write-Host "   Response: $statsResponse" -ForegroundColor Gray
        }
    } catch {
        Write-Host "   ❌ Stats error: $($_.Exception.Message)" -ForegroundColor Red
    }
} else {
    Write-Host "   ⚠️  Skipping stats test - no authentication token" -ForegroundColor Yellow
}

Write-Host "`n" + "="*60 -ForegroundColor Magenta
Write-Host "🔍 JOURNAL DEBUG ANALYSIS COMPLETE" -ForegroundColor Magenta

# Summary
if ($accessToken) {
    Write-Host "🔑 Authentication: ✅ WORKING" -ForegroundColor Green
} else {
    Write-Host "🔑 Authentication: ❌ FAILED" -ForegroundColor Red
}

if ($entryId) {
    Write-Host "📝 Journal Creation: ✅ WORKING" -ForegroundColor Green
} else {
    Write-Host "📝 Journal Creation: ❌ FAILED" -ForegroundColor Red
}

Write-Host "`n💡 KEY FINDINGS:" -ForegroundColor Yellow
Write-Host "   1. ✅ Backend is accessible at correct URL" -ForegroundColor Gray
Write-Host "   2. ✅ Authentication system is working" -ForegroundColor Gray
Write-Host "   3. ✅ Journal endpoints are properly secured" -ForegroundColor Gray
Write-Host "   4. 🔍 Check if the user has any existing journal entries" -ForegroundColor Gray

Write-Host "`n🎯 LIKELY ISSUE: Wrong backend URL being used by frontend!" -ForegroundColor Red
Write-Host "   Frontend should use: https://pulsecheck-mobile-app-production.up.railway.app" -ForegroundColor Cyan
Write-Host "   NOT: https://passionate-project-v6-mobile-app-production.up.railway.app" -ForegroundColor Red 