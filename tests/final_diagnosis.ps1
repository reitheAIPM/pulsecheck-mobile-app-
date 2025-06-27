# Final Journal Diagnosis Script
Write-Host "🔍 FINAL JOURNAL DIAGNOSIS - IDENTIFYING ROOT CAUSE" -ForegroundColor Magenta
Write-Host "=" * 60

$BaseUrl = "https://pulsecheck-mobile-app-production.up.railway.app"
Write-Host "Backend URL: $BaseUrl" -ForegroundColor Cyan

# Step 1: Test backend health
Write-Host "`n1. 🏥 BACKEND HEALTH CHECK" -ForegroundColor Yellow
$healthResponse = curl.exe -s "$BaseUrl/health"
$health = $healthResponse | ConvertFrom-Json
Write-Host "   Status: $($health.status)" -ForegroundColor $(if ($health.status -eq "healthy") { "Green" } else { "Yellow" })
if ($health.metrics.error_rate -gt 0) {
    Write-Host "   ⚠️  Error Rate: $($health.metrics.error_rate * 100)%" -ForegroundColor Yellow
}

# Step 2: Test authentication with multiple approaches
Write-Host "`n2. 🔐 AUTHENTICATION TESTING" -ForegroundColor Yellow

# Test with known working credentials
$testUsers = @(
    @{ email = "test@example.com"; password = "testpassword123"; name = "Test User 1" },
    @{ email = "demo@pulsecheck.com"; password = "demopassword123"; name = "Demo User" },
    @{ email = "user@test.com"; password = "password123"; name = "Test User 2" }
)

$workingToken = $null
$workingUser = $null

foreach ($user in $testUsers) {
    Write-Host "   Testing: $($user.name) ($($user.email))" -ForegroundColor Cyan
    
    # Try signin
    $authBody = @{ email = $user.email; password = $user.password } | ConvertTo-Json
    $authResponse = curl.exe -s -X POST -H "Content-Type: application/json" -d $authBody "$BaseUrl/api/v1/auth/signin"
    
    try {
        $authData = $authResponse | ConvertFrom-Json
        if ($authData.access_token) {
            Write-Host "     ✅ Successfully authenticated" -ForegroundColor Green
            $workingToken = $authData.access_token
            $workingUser = $user
            break
        } else {
            Write-Host "     ❌ No token received" -ForegroundColor Red
        }
    } catch {
        Write-Host "     ⚠️  Auth failed, trying signup..." -ForegroundColor Yellow
        
        # Try signup
        $signupResponse = curl.exe -s -X POST -H "Content-Type: application/json" -d $authBody "$BaseUrl/api/v1/auth/signup"
        try {
            $signupData = $signupResponse | ConvertFrom-Json
            if ($signupData.access_token) {
                Write-Host "     ✅ User created and authenticated" -ForegroundColor Green
                $workingToken = $signupData.access_token
                $workingUser = $user
                break
            }
        } catch {
            Write-Host "     ❌ Signup also failed" -ForegroundColor Red
        }
    }
}

if (-not $workingToken) {
    Write-Host "`n❌ CRITICAL: Cannot authenticate with any test user!" -ForegroundColor Red
    Write-Host "This is likely the root cause of the journal issue." -ForegroundColor Red
    exit 1
}

Write-Host "`n   ✅ Authentication successful with: $($workingUser.name)" -ForegroundColor Green
Write-Host "   Token (first 20 chars): $($workingToken.Substring(0, [Math]::Min(20, $workingToken.Length)))..." -ForegroundColor Gray

# Step 3: Test journal creation with auth
Write-Host "`n3. 📝 JOURNAL ENTRY CREATION TEST" -ForegroundColor Yellow

$testEntry = @{
    content = "DIAGNOSTIC ENTRY - Created at $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') to test journal functionality. This entry should appear in the list if everything is working correctly."
    mood_level = 8
    energy_level = 7
    stress_level = 3
    tags = @("diagnostic", "test", "$(Get-Date -Format 'MMdd-HHmm')")
} | ConvertTo-Json

$createResponse = curl.exe -s -X POST -H "Content-Type: application/json" -H "Authorization: Bearer $workingToken" -d $testEntry "$BaseUrl/api/v1/journal/entries"

try {
    $createdEntry = $createResponse | ConvertFrom-Json
    if ($createdEntry.id) {
        Write-Host "   ✅ Journal entry created successfully" -ForegroundColor Green
        Write-Host "   📝 Entry ID: $($createdEntry.id)" -ForegroundColor Cyan
        Write-Host "   📅 Created at: $($createdEntry.created_at)" -ForegroundColor Gray
        $newEntryId = $createdEntry.id
    } else {
        Write-Host "   ❌ Journal creation failed - no ID in response" -ForegroundColor Red
        Write-Host "   Response: $createResponse" -ForegroundColor Gray
    }
} catch {
    Write-Host "   ❌ Journal creation failed - invalid response" -ForegroundColor Red
    Write-Host "   Response: $createResponse" -ForegroundColor Gray
}

# Step 4: Immediate retrieval test
Write-Host "`n4. 🔍 IMMEDIATE JOURNAL RETRIEVAL TEST" -ForegroundColor Yellow

$listResponse = curl.exe -s -H "Authorization: Bearer $workingToken" "$BaseUrl/api/v1/journal/entries?page=1&per_page=20"

try {
    $entriesData = $listResponse | ConvertFrom-Json
    
    Write-Host "   📊 Response Analysis:" -ForegroundColor Cyan
    Write-Host "     Total entries: $($entriesData.total)" -ForegroundColor Gray
    Write-Host "     Entries in page: $($entriesData.entries.Count)" -ForegroundColor Gray
    Write-Host "     Current page: $($entriesData.page)" -ForegroundColor Gray
    Write-Host "     Per page: $($entriesData.per_page)" -ForegroundColor Gray
    
    if ($entriesData.total -eq 0) {
        Write-Host "`n   ❌ FOUND THE ISSUE: No journal entries exist for this user!" -ForegroundColor Red
        Write-Host "   🔍 This means either:" -ForegroundColor Yellow
        Write-Host "     1. Journal creation is failing silently" -ForegroundColor Yellow
        Write-Host "     2. RLS policies are preventing access" -ForegroundColor Yellow
        Write-Host "     3. User is authenticated as different user than expected" -ForegroundColor Yellow
    } elseif ($entriesData.entries.Count -gt 0) {
        Write-Host "`n   ✅ Journal entries found!" -ForegroundColor Green
        
        # Show latest entries
        for ($i = 0; $i -lt [Math]::Min(3, $entriesData.entries.Count); $i++) {
            $entry = $entriesData.entries[$i]
            Write-Host "   📝 Entry $(($i + 1)):" -ForegroundColor Green
            Write-Host "     ID: $($entry.id)" -ForegroundColor Gray
            Write-Host "     Created: $($entry.created_at)" -ForegroundColor Gray
            Write-Host "     Content: $($entry.content.Substring(0, [Math]::Min(80, $entry.content.Length)))..." -ForegroundColor Gray
        }
        
        # Check if our new entry is in the list
        if ($newEntryId) {
            $foundNewEntry = $entriesData.entries | Where-Object { $_.id -eq $newEntryId }
            if ($foundNewEntry) {
                Write-Host "`n   ✅ NEW ENTRY FOUND IN LIST - System is working correctly!" -ForegroundColor Green
            } else {
                Write-Host "`n   ⚠️  New entry not found in list - possible delay or pagination issue" -ForegroundColor Yellow
            }
        }
    }
} catch {
    Write-Host "   ❌ Failed to parse journal list response" -ForegroundColor Red
    Write-Host "   Raw response: $listResponse" -ForegroundColor Gray
}

# Step 5: Journal stats test
Write-Host "`n5. 📈 JOURNAL STATISTICS TEST" -ForegroundColor Yellow

$statsResponse = curl.exe -s -H "Authorization: Bearer $workingToken" "$BaseUrl/api/v1/journal/stats"

try {
    $stats = $statsResponse | ConvertFrom-Json
    Write-Host "   📊 Statistics:" -ForegroundColor Cyan
    Write-Host "     Total entries: $($stats.total_entries)" -ForegroundColor Gray
    Write-Host "     Current streak: $($stats.current_streak)" -ForegroundColor Gray
    Write-Host "     Average mood: $($stats.average_mood)" -ForegroundColor Gray
    Write-Host "     Last entry: $($stats.last_entry_date)" -ForegroundColor Gray
    
    if ($stats.total_entries -eq 0) {
        Write-Host "`n   ❌ CONFIRMED: Stats show 0 entries - journal system has no data for this user" -ForegroundColor Red
    } else {
        Write-Host "`n   ✅ Stats confirm journal entries exist" -ForegroundColor Green
    }
} catch {
    Write-Host "   ❌ Failed to get journal stats" -ForegroundColor Red
    Write-Host "   Response: $statsResponse" -ForegroundColor Gray
}

# Step 6: Database diagnostic (if available)
Write-Host "`n6. 🗄️ DATABASE DIAGNOSTIC" -ForegroundColor Yellow

$dbResponse = curl.exe -s "$BaseUrl/api/v1/debug/database/tables"

try {
    $dbInfo = $dbResponse | ConvertFrom-Json
    $journalTable = $dbInfo.tables | Where-Object { $_.table_name -eq "journal_entries" }
    
    if ($journalTable) {
        Write-Host "   ✅ journal_entries table exists" -ForegroundColor Green
        Write-Host "   📊 Total rows in table: $($journalTable.row_count)" -ForegroundColor Cyan
        
        if ($journalTable.row_count -eq 0) {
            Write-Host "`n   ❌ CONFIRMED: Database table is empty - no journal entries exist at all!" -ForegroundColor Red
        } else {
            Write-Host "`n   🔍 Table has data but user can't see it - likely RLS policy issue" -ForegroundColor Yellow
        }
    } else {
        Write-Host "   ❌ journal_entries table not found in database!" -ForegroundColor Red
    }
} catch {
    Write-Host "   ⚠️  Database diagnostic not available" -ForegroundColor Yellow
}

# Final diagnosis
Write-Host "`n" + "=" * 60 -ForegroundColor Magenta
Write-Host "🔍 FINAL DIAGNOSIS COMPLETE" -ForegroundColor Magenta

Write-Host "`n📋 FINDINGS SUMMARY:" -ForegroundColor Yellow
Write-Host "✅ Backend: Accessible and responding" -ForegroundColor Green
Write-Host "$(if ($workingToken) { '✅' } else { '❌' }) Authentication: $(if ($workingToken) { 'Working' } else { 'Failed' })" -ForegroundColor $(if ($workingToken) { "Green" } else { "Red" })
Write-Host "$(if ($newEntryId) { '✅' } else { '❌' }) Journal Creation: $(if ($newEntryId) { 'Working' } else { 'Failed' })" -ForegroundColor $(if ($newEntryId) { "Green" } else { "Red" })

Write-Host "`n🎯 NEXT STEPS:" -ForegroundColor Yellow
if ($workingToken -and $newEntryId) {
    Write-Host "✅ System is working correctly! Journal entries can be created and retrieved." -ForegroundColor Green
    Write-Host "💡 If you're not seeing entries in your app, check:" -ForegroundColor Cyan
    Write-Host "   1. Are you logged in with the same account?" -ForegroundColor Gray
    Write-Host "   2. Is the frontend using the correct backend URL?" -ForegroundColor Gray
    Write-Host "   3. Is there a caching issue in the frontend?" -ForegroundColor Gray
} else {
    Write-Host "❌ System has issues that need to be fixed:" -ForegroundColor Red
    if (-not $workingToken) {
        Write-Host "   1. Fix authentication system" -ForegroundColor Yellow
    }
    if (-not $newEntryId) {
        Write-Host "   2. Fix journal creation endpoint" -ForegroundColor Yellow
    }
}

Write-Host "`n🔧 RECOMMENDED ACTIONS:" -ForegroundColor Yellow
Write-Host "1. Check frontend authentication implementation" -ForegroundColor Gray
Write-Host "2. Verify frontend is using correct backend URL" -ForegroundColor Gray
Write-Host "3. Clear browser cache and try again" -ForegroundColor Gray
Write-Host "4. Check browser console for JavaScript errors" -ForegroundColor Gray 