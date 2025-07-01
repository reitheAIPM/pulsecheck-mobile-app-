#!/usr/bin/env pwsh

# Simple Test User Creation - Following Supabase Best Practices + o3 Optimizations
# Based on user-management examples in Supabase docs + o3 timeout/monitoring fixes

Write-Host "🧪 Creating Simple Test User Account..." -ForegroundColor Yellow
Write-Host ""

# Test user credentials
$testEmail = "test.user@example.com"
$testPassword = "TestUser123!"
$testName = "Test User"
$baseUrl = "https://pulsecheck-mobile-app-production.up.railway.app"

Write-Host "📧 Email: $testEmail" -ForegroundColor Cyan
Write-Host "🔑 Password: $testPassword" -ForegroundColor Cyan
Write-Host "👤 Name: $testName" -ForegroundColor Cyan
Write-Host ""

# o3 Optimization: Standardized error handling with timeouts
function Invoke-WithTimeout {
    param (
        [string]$Url,
        [string]$Method = "GET",
        [hashtable]$Body = @{},
        [string]$Description = "API call"
    )
    try {
        if ($Method -eq "GET" -and $Body.Count -eq 0) {
            # Simple GET requests - use curl.exe for compatibility
            $response = curl.exe -s --max-time 15 $Url
            return $response | ConvertFrom-Json
        } else {
            # POST/complex requests - use Invoke-WebRequest with timeout
            $response = Invoke-WebRequest -Uri $Url -Method $Method `
                -Body ($Body | ConvertTo-Json) -ContentType "application/json" `
                -TimeoutSec 15
            return $response.Content | ConvertFrom-Json
        }
    } catch {
        Write-Host "❌ $Description failed: $($_.Exception.Message)" -ForegroundColor Red
        throw
    }
}

# o3 Critical Check: Verify scheduler and testing mode BEFORE creating user
Write-Host "🔄 Step 0: Verifying system readiness..." -ForegroundColor Green

try {
    Write-Host "   Checking system health..." -ForegroundColor Gray
    $health = Invoke-WithTimeout -Url "$baseUrl/health" -Description "Health check"
    Write-Host "   ✅ System status: $($health.status)" -ForegroundColor Gray

    Write-Host "   Checking scheduler status..." -ForegroundColor Gray
    $schedulerStatus = Invoke-WithTimeout -Url "$baseUrl/api/v1/scheduler/status" -Description "Scheduler status check"
    $schedulerRunning = $schedulerStatus.running -eq $true
    Write-Host "   📋 Scheduler running: $schedulerRunning" -ForegroundColor Gray

    Write-Host "   Checking testing mode..." -ForegroundColor Gray
    $testingStatus = Invoke-WithTimeout -Url "$baseUrl/api/v1/scheduler/testing/status" -Description "Testing mode check"
    $testingEnabled = $testingStatus.testing_mode -eq $true
    Write-Host "   ⚡ Testing mode: $testingEnabled" -ForegroundColor Gray

    # o3 Critical Validation: Both must be true for AI responses
    if (-not $schedulerRunning) {
        Write-Host "❌ CRITICAL: Scheduler is not running!" -ForegroundColor Red
        Write-Host "   AI will not respond to journal entries." -ForegroundColor Yellow
        Write-Host "   Start scheduler: Invoke-WebRequest -Uri '$baseUrl/api/v1/scheduler/start' -Method POST -TimeoutSec 15" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "⚠️  Continue anyway? (y/N): " -ForegroundColor Yellow -NoNewline
        $continue = Read-Host
        if ($continue -ne "y" -and $continue -ne "Y") {
            Write-Host "❌ Aborted. Fix scheduler first." -ForegroundColor Red
            exit 1
        }
    }

    if (-not $testingEnabled) {
        Write-Host "⚠️  Testing mode is disabled - AI responses will use production timing (5min-1hr)" -ForegroundColor Yellow
        Write-Host "   Enable for immediate responses: Invoke-WebRequest -Uri '$baseUrl/api/v1/scheduler/testing/enable' -Method POST -TimeoutSec 15" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "⚠️  Continue with production timing? (y/N): " -ForegroundColor Yellow -NoNewline
        $continue = Read-Host
        if ($continue -ne "y" -and $continue -ne "Y") {
            Write-Host "❌ Aborted. Enable testing mode first." -ForegroundColor Red
            exit 1
        }
    }

    if ($schedulerRunning -and $testingEnabled) {
        Write-Host "✅ System ready for immediate AI responses!" -ForegroundColor Green
    }

} catch {
    Write-Host "❌ System readiness check failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "   Continuing anyway, but AI responses may not work..." -ForegroundColor Yellow
    Write-Host ""
}

# Step 1: Create test user via Supabase Auth (standard pattern)
Write-Host "🔄 Step 1: Creating user account..." -ForegroundColor Green

$signupBody = @{
    email = $testEmail
    password = $testPassword
    data = @{
        full_name = $testName
    }
}

try {
    $response = Invoke-WithTimeout -Url "$baseUrl/api/v1/auth/signup" -Method POST -Body $signupBody -Description "User signup"
    Write-Host "✅ User account created successfully!" -ForegroundColor Green
    Write-Host "User ID: $($response.user.id)" -ForegroundColor Cyan
} catch {
    if ($_.Exception.Message -like "*400*") {
        Write-Host "⚠️  User may already exist. Trying sign-in instead..." -ForegroundColor Yellow
        
        $signinBody = @{
            email = $testEmail
            password = $testPassword
        }
        
        try {
            $response = Invoke-WithTimeout -Url "$baseUrl/api/v1/auth/signin" -Method POST -Body $signinBody -Description "User signin"
            Write-Host "✅ User signed in successfully!" -ForegroundColor Green
            Write-Host "User ID: $($response.user.id)" -ForegroundColor Cyan
        } catch {
            Write-Host "❌ Error with user account: $($_.Exception.Message)" -ForegroundColor Red
            exit 1
        }
    } else {
        Write-Host "❌ Error creating user: $($_.Exception.Message)" -ForegroundColor Red
        exit 1
    }
}

# Step 2: Verify profile was created automatically (via trigger)
Write-Host ""
Write-Host "🔄 Step 2: Verifying profile creation..." -ForegroundColor Green

try {
    $profileCheck = Invoke-WithTimeout -Url "$baseUrl/api/v1/admin/comprehensive-logs/$testEmail" -Description "Profile verification"
    Write-Host "✅ Profile created automatically via trigger!" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Profile check: $($_.Exception.Message)" -ForegroundColor Yellow
}

# Step 3: Create a test journal entry for AI response testing
Write-Host ""
Write-Host "🔄 Step 3: Creating test journal entry..." -ForegroundColor Green

$journalEntry = @{
    content = "I'm feeling a bit stressed today with work deadlines approaching. Could use some guidance on managing anxiety and staying focused."
    mood_rating = 4
    energy_level = 6
    user_email = $testEmail
}

try {
    $journalResponse = Invoke-WithTimeout -Url "$baseUrl/api/v1/journal/entries" -Method POST -Body $journalEntry -Description "Journal entry creation"
    Write-Host "✅ Test journal entry created!" -ForegroundColor Green
    Write-Host "Entry ID: $($journalResponse.id)" -ForegroundColor Cyan
    
    # Store for monitoring
    $entryId = $journalResponse.id
    
} catch {
    Write-Host "⚠️  Journal entry: $($_.Exception.Message)" -ForegroundColor Yellow
    $entryId = $null
}

# Step 4: o3 Optimization - Single endpoint monitoring check
Write-Host ""
Write-Host "🔄 Step 4: Checking AI flow status..." -ForegroundColor Green

if ($entryId) {
    try {
        # Wait a moment for potential immediate AI response
        Start-Sleep -Seconds 5
        
        # Use new monitoring endpoint (once implemented)
        $aiStatus = Invoke-WithTimeout -Url "$baseUrl/api/v1/ai-monitoring/last-action/$testEmail" -Description "AI flow monitoring"
        
        Write-Host "📊 AI Flow Status:" -ForegroundColor Cyan
        Write-Host "   Last journal entry: $($aiStatus.last_journal_entry)" -ForegroundColor Gray
        Write-Host "   Last AI comment: $($aiStatus.last_ai_comment)" -ForegroundColor Gray
        Write-Host "   Next scheduled: $($aiStatus.next_scheduled_at)" -ForegroundColor Gray
        Write-Host "   Testing mode: $($aiStatus.testing_mode)" -ForegroundColor Gray
        Write-Host "   Scheduler running: $($aiStatus.scheduler_running)" -ForegroundColor Gray
        
    } catch {
        Write-Host "⚠️  AI monitoring endpoint not yet available: $($_.Exception.Message)" -ForegroundColor Yellow
        Write-Host "   Using legacy monitoring commands..." -ForegroundColor Gray
    }
}

# Step 5: Show monitoring commands with o3 timeout patterns
Write-Host ""
Write-Host "🎯 MONITORING COMMANDS (o3 Optimized):" -ForegroundColor Magenta
Write-Host "===========================================" -ForegroundColor Magenta
Write-Host ""
Write-Host "📊 View all user activity:" -ForegroundColor White
Write-Host "Invoke-WebRequest -Uri '$baseUrl/api/v1/admin/comprehensive-logs/$testEmail' -Method GET -TimeoutSec 15" -ForegroundColor Gray
Write-Host ""
Write-Host "🤖 Monitor AI responses:" -ForegroundColor White  
Write-Host "Invoke-WebRequest -Uri '$baseUrl/api/v1/admin/live-ai-monitoring' -Method GET -TimeoutSec 15" -ForegroundColor Gray
Write-Host ""
Write-Host "⚡ Trigger immediate AI response:" -ForegroundColor White
Write-Host "Invoke-WebRequest -Uri '$baseUrl/api/v1/admin/trigger-immediate-ai/$testEmail' -Method POST -TimeoutSec 15" -ForegroundColor Gray
Write-Host ""
Write-Host "📈 System dashboard:" -ForegroundColor White
Write-Host "Invoke-WebRequest -Uri '$baseUrl/api/v1/admin/monitoring-dashboard' -Method GET -TimeoutSec 15" -ForegroundColor Gray
Write-Host ""
Write-Host "🆕 AI Flow Status (Single Check):" -ForegroundColor White
Write-Host "Invoke-WebRequest -Uri '$baseUrl/api/v1/ai-monitoring/last-action/$testEmail' -Method GET -TimeoutSec 15" -ForegroundColor Gray
Write-Host ""

Write-Host "✅ SIMPLE TEST USER READY!" -ForegroundColor Green
Write-Host ""
Write-Host "💡 o3 Optimization Benefits:" -ForegroundColor Yellow
Write-Host "- 15-second timeouts prevent script hangs" -ForegroundColor White
Write-Host "- Scheduler + testing mode validation before testing" -ForegroundColor White  
Write-Host "- Single endpoint for complete AI flow monitoring" -ForegroundColor White
Write-Host "- Clear error messages for efficient debugging" -ForegroundColor White

if ($schedulerRunning -and $testingEnabled) {
    Write-Host ""
    Write-Host "🚀 Expect AI response within 30-60 seconds!" -ForegroundColor Green
} elseif ($schedulerRunning) {
    Write-Host ""
    Write-Host "⏳ AI response expected in 5 minutes to 1 hour (production timing)" -ForegroundColor Yellow
} else {
    Write-Host ""
    Write-Host "❌ No AI response expected - scheduler not running" -ForegroundColor Red
} 