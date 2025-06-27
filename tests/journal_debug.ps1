#!/usr/bin/env pwsh
# ================================================
# JOURNAL DEBUG SCRIPT - Comprehensive Testing
# ================================================

param(
    [string]$BaseUrl = "https://passionate-project-v6-mobile-app-production.up.railway.app",
    [switch]$Verbose
)

$ErrorActionPreference = "Continue"

Write-Host "🔍 JOURNAL DEBUG ANALYSIS STARTING..." -ForegroundColor Magenta
Write-Host "Base URL: $BaseUrl" -ForegroundColor Cyan
Write-Host "="*60

# Test 1: Basic connectivity
Write-Host "`n1. TESTING BASIC CONNECTIVITY" -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "$BaseUrl/api/v1/debug/system/status" -Method GET -TimeoutSec 10
    Write-Host "   ✅ API is accessible (Status: $($response.StatusCode))" -ForegroundColor Green
    
    $systemData = $response.Content | ConvertFrom-Json
    if ($systemData.database_status) {
        Write-Host "   ✅ Database Status: $($systemData.database_status)" -ForegroundColor Green
    }
} catch {
    Write-Host "   ❌ API connectivity failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Test 2: Check journal endpoints without auth (should fail)
Write-Host "`n2. TESTING JOURNAL ENDPOINTS (NO AUTH - SHOULD FAIL)" -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "$BaseUrl/api/v1/journal/entries" -Method GET -ErrorAction Stop
    Write-Host "   ❌ SECURITY ISSUE: Journal accessible without auth!" -ForegroundColor Red
} catch {
    if ($_.Exception.Response.StatusCode -eq 401 -or $_.Exception.Response.StatusCode -eq 403) {
        Write-Host "   ✅ Security working: Unauthorized access blocked ($($_.Exception.Response.StatusCode))" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️  Unexpected error: $($_.Exception.Message)" -ForegroundColor Yellow
    }
}

# Test 3: Check authentication system
Write-Host "`n3. TESTING AUTHENTICATION SYSTEM" -ForegroundColor Yellow
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
        Write-Host "   ✅ Authentication successful" -ForegroundColor Green
        
        if ($authData.access_token) {
            Write-Host "   ✅ Access token received" -ForegroundColor Green
            $accessToken = $authData.access_token
            $headers = @{
                "Authorization" = "Bearer $accessToken"
                "Content-Type" = "application/json"
            }
        } else {
            Write-Host "   ❌ No access token in response" -ForegroundColor Red
            Write-Host "   Response: $($authResponse.Content)" -ForegroundColor Gray
        }
    }
} catch {
    Write-Host "   ❌ Authentication failed: $($_.Exception.Message)" -ForegroundColor Red
    
    # Try creating a test user
    Write-Host "   🔄 Attempting to create test user..." -ForegroundColor Yellow
    try {
        $signupResponse = Invoke-WebRequest -Uri "$BaseUrl/api/v1/auth/signup" -Method POST -Body $authBody -ContentType "application/json" -ErrorAction Stop
        Write-Host "   ✅ Test user created successfully" -ForegroundColor Green
        
        # Now try signing in again
        Start-Sleep -Seconds 2
        $authResponse = Invoke-WebRequest -Uri "$BaseUrl/api/v1/auth/signin" -Method POST -Body $authBody -ContentType "application/json" -ErrorAction Stop
        $authData = $authResponse.Content | ConvertFrom-Json
        $accessToken = $authData.access_token
        $headers = @{
            "Authorization" = "Bearer $accessToken"
            "Content-Type" = "application/json"
        }
        Write-Host "   ✅ Authentication with new user successful" -ForegroundColor Green
    } catch {
        Write-Host "   ❌ Could not create or authenticate test user: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "   🔍 Debugging without authentication..." -ForegroundColor Yellow
        $headers = @{ "Content-Type" = "application/json" }
    }
}

# Test 4: Test journal creation
Write-Host "`n4. TESTING JOURNAL ENTRY CREATION" -ForegroundColor Yellow
$entryId = $null
if ($accessToken) {
    $testEntry = @{
        content = "Debug test entry created at $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss'). Testing journal functionality."
        mood_level = 7
        energy_level = 6
        stress_level = 4
        tags = @("debug", "test")
    }
    
    try {
        $entryBody = $testEntry | ConvertTo-Json
        $createResponse = Invoke-WebRequest -Uri "$BaseUrl/api/v1/journal/entries" -Method POST -Body $entryBody -Headers $headers -ErrorAction Stop
        
        Write-Host "   ✅ Journal entry created (Status: $($createResponse.StatusCode))" -ForegroundColor Green
        $createdEntry = $createResponse.Content | ConvertFrom-Json
        $entryId = $createdEntry.id
        Write-Host "   📝 Entry ID: $entryId" -ForegroundColor Cyan
        
        if ($Verbose) {
            Write-Host "   📄 Created entry details:" -ForegroundColor Gray
            Write-Host "      Content: $($createdEntry.content.Substring(0, [Math]::Min(50, $createdEntry.content.Length)))..." -ForegroundColor Gray
            Write-Host "      Mood: $($createdEntry.mood_level), Energy: $($createdEntry.energy_level), Stress: $($createdEntry.stress_level)" -ForegroundColor Gray
        }
    } catch {
        Write-Host "   ❌ Journal creation failed: $($_.Exception.Message)" -ForegroundColor Red
        if ($_.Exception.Response) {
            $errorStream = $_.Exception.Response.GetResponseStream()
            $reader = New-Object System.IO.StreamReader($errorStream)
            $errorBody = $reader.ReadToEnd()
            Write-Host "   📄 Error details: $errorBody" -ForegroundColor Gray
        }
    }
} else {
    Write-Host "   ⚠️  Skipping journal creation - no authentication token" -ForegroundColor Yellow
}

# Test 5: Test journal retrieval
Write-Host "`n5. TESTING JOURNAL ENTRY RETRIEVAL" -ForegroundColor Yellow
if ($accessToken) {
    try {
        $entriesUrl = "$BaseUrl/api/v1/journal/entries?page=1&per_page=10"
        $listResponse = Invoke-WebRequest -Uri $entriesUrl -Method GET -Headers $headers -ErrorAction Stop
        
        Write-Host "   ✅ Journal entries retrieved (Status: $($listResponse.StatusCode))" -ForegroundColor Green
        $entriesData = $listResponse.Content | ConvertFrom-Json
        
        if ($entriesData.entries) {
            Write-Host "   📊 Found $($entriesData.entries.Count) entries (Total: $($entriesData.total))" -ForegroundColor Green
            
            if ($entriesData.entries.Count -gt 0) {
                $latestEntry = $entriesData.entries[0]
                Write-Host "   📝 Latest entry:" -ForegroundColor Cyan
                Write-Host "      ID: $($latestEntry.id)" -ForegroundColor Gray
                Write-Host "      Created: $($latestEntry.created_at)" -ForegroundColor Gray
                Write-Host "      Content: $($latestEntry.content.Substring(0, [Math]::Min(100, $latestEntry.content.Length)))..." -ForegroundColor Gray
            }
        } elseif ($entriesData -is [array]) {
            Write-Host "   📊 Found $($entriesData.Count) entries (direct array response)" -ForegroundColor Green
        } else {
            Write-Host "   ⚠️  No entries found in response" -ForegroundColor Yellow
            Write-Host "   📄 Response structure: $($entriesData | ConvertTo-Json -Depth 2)" -ForegroundColor Gray
        }
    } catch {
        Write-Host "   ❌ Journal retrieval failed: $($_.Exception.Message)" -ForegroundColor Red
        if ($_.Exception.Response) {
            $errorStream = $_.Exception.Response.GetResponseStream()
            $reader = New-Object System.IO.StreamReader($errorStream)
            $errorBody = $reader.ReadToEnd()
            Write-Host "   📄 Error details: $errorBody" -ForegroundColor Gray
        }
    }
} else {
    Write-Host "   ⚠️  Skipping journal retrieval - no authentication token" -ForegroundColor Yellow
}

# Test 6: Test individual entry retrieval
Write-Host "`n6. TESTING INDIVIDUAL ENTRY RETRIEVAL" -ForegroundColor Yellow
if ($accessToken -and $entryId) {
    try {
        $singleResponse = Invoke-WebRequest -Uri "$BaseUrl/api/v1/journal/entries/$entryId" -Method GET -Headers $headers -ErrorAction Stop
        
        Write-Host "   ✅ Individual entry retrieved (Status: $($singleResponse.StatusCode))" -ForegroundColor Green
        $singleEntry = $singleResponse.Content | ConvertFrom-Json
        Write-Host "   📝 Entry content: $($singleEntry.content.Substring(0, [Math]::Min(100, $singleEntry.content.Length)))..." -ForegroundColor Cyan
    } catch {
        Write-Host "   ❌ Individual entry retrieval failed: $($_.Exception.Message)" -ForegroundColor Red
    }
} else {
    Write-Host "   ⚠️  Skipping individual entry test - no token or entry ID" -ForegroundColor Yellow
}

# Test 7: Test journal stats
Write-Host "`n7. TESTING JOURNAL STATISTICS" -ForegroundColor Yellow
if ($accessToken) {
    try {
        $statsResponse = Invoke-WebRequest -Uri "$BaseUrl/api/v1/journal/stats" -Method GET -Headers $headers -ErrorAction Stop
        
        Write-Host "   ✅ Journal stats retrieved (Status: $($statsResponse.StatusCode))" -ForegroundColor Green
        $stats = $statsResponse.Content | ConvertFrom-Json
        Write-Host "   📊 Stats summary:" -ForegroundColor Cyan
        Write-Host "      Total entries: $($stats.total_entries)" -ForegroundColor Gray
        Write-Host "      Average mood: $($stats.average_mood)" -ForegroundColor Gray
        Write-Host "      Last entry: $($stats.last_entry_date)" -ForegroundColor Gray
    } catch {
        Write-Host "   ❌ Journal stats failed: $($_.Exception.Message)" -ForegroundColor Red
    }
} else {
    Write-Host "   ⚠️  Skipping stats test - no authentication token" -ForegroundColor Yellow
}

# Test 8: Database direct access check
Write-Host "`n8. TESTING DATABASE DIAGNOSTIC" -ForegroundColor Yellow
try {
    $dbDiagResponse = Invoke-WebRequest -Uri "$BaseUrl/api/v1/debug/database/tables" -Method GET -ErrorAction Stop
    
    Write-Host "   ✅ Database diagnostic accessible (Status: $($dbDiagResponse.StatusCode))" -ForegroundColor Green
    $dbData = $dbDiagResponse.Content | ConvertFrom-Json
    
    if ($dbData.tables) {
        $journalTable = $dbData.tables | Where-Object { $_.table_name -eq "journal_entries" }
        if ($journalTable) {
            Write-Host "   ✅ journal_entries table exists" -ForegroundColor Green
            Write-Host "   📊 Row count: $($journalTable.row_count)" -ForegroundColor Cyan
        } else {
            Write-Host "   ❌ journal_entries table not found!" -ForegroundColor Red
        }
    }
} catch {
    Write-Host "   ⚠️  Database diagnostic not available: $($_.Exception.Message)" -ForegroundColor Yellow
}

Write-Host "`n" + "="*60
Write-Host "🔍 JOURNAL DEBUG ANALYSIS COMPLETE" -ForegroundColor Magenta

if ($accessToken) {
    Write-Host "🔑 Authentication: Working" -ForegroundColor Green
} else {
    Write-Host "🔑 Authentication: Failed" -ForegroundColor Red
}

Write-Host "`n💡 RECOMMENDATIONS:" -ForegroundColor Yellow
Write-Host "   1. Check authentication system if token missing" -ForegroundColor Gray
Write-Host "   2. Verify database migrations are applied" -ForegroundColor Gray
Write-Host "   3. Check RLS policies on journal_entries table" -ForegroundColor Gray
Write-Host "   4. Verify user permissions in Supabase" -ForegroundColor Gray 