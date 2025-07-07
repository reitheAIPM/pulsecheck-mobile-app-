param(
    [string]$BaseUrl = "https://pulsecheck-mobile-app-production.up.railway.app/api/v1",
    [string]$UserId = ""
)

Write-Host "🔍 AI Opportunity Detection Debug Script" -ForegroundColor Yellow
Write-Host "=======================================" -ForegroundColor Yellow

if (-not $UserId) {
    $UserId = Read-Host "Enter your user ID"
}

Write-Host "📋 Checking scheduler status..." -ForegroundColor Green
try {
    $schedulerStatus = Invoke-WebRequest -Uri "$BaseUrl/scheduler/status" -Method GET | 
                      Select-Object -ExpandProperty Content | ConvertFrom-Json
    
    Write-Host "✅ Scheduler Status: $($schedulerStatus.status)" -ForegroundColor Green
    Write-Host "📊 Recent Cycles:" -ForegroundColor Cyan
    foreach ($cycle in $schedulerStatus.recent_cycles) {
        Write-Host "  - $($cycle.cycle_id): Users=$($cycle.users_processed), Opportunities=$($cycle.opportunities_found), Engagements=$($cycle.engagements_executed)" -ForegroundColor White
    }
} catch {
    Write-Host "❌ Error checking scheduler status: $($_.Exception.Message)" -ForegroundColor Red
    return
}

Write-Host "`n🧪 Checking testing mode..." -ForegroundColor Green
try {
    $testingStatus = Invoke-WebRequest -Uri "$BaseUrl/scheduler/testing/status" -Method GET | 
                    Select-Object -ExpandProperty Content | ConvertFrom-Json
    
    Write-Host "✅ Testing Mode: $($testingStatus.testing_mode)" -ForegroundColor Green
    Write-Host "📋 Status: $($testingStatus.status)" -ForegroundColor Cyan
} catch {
    Write-Host "❌ Error checking testing mode: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n📝 Checking recent journal entries..." -ForegroundColor Green
try {
    $journalEntries = Invoke-WebRequest -Uri "$BaseUrl/journal/entries" -Method GET | 
                     Select-Object -ExpandProperty Content | ConvertFrom-Json
    
    Write-Host "✅ Found $($journalEntries.Count) journal entries" -ForegroundColor Green
    
    if ($journalEntries.Count -gt 0) {
        Write-Host "📄 Recent entries:" -ForegroundColor Cyan
        foreach ($entry in $journalEntries | Select-Object -First 5) {
            $contentPreview = if ($entry.content.Length -gt 100) { 
                "$($entry.content.Substring(0, 100))..." 
            } else { 
                $entry.content 
            }
            Write-Host "  - ID: $($entry.id)" -ForegroundColor White
            Write-Host "    Created: $($entry.created_at)" -ForegroundColor Gray
            Write-Host "    Content: $contentPreview" -ForegroundColor Gray
            Write-Host "    Length: $($entry.content.Length) characters" -ForegroundColor Gray
        }
    } else {
        Write-Host "❌ No journal entries found" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Error checking journal entries: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n🤖 Checking AI responses..." -ForegroundColor Green
try {
    $aiResponses = Invoke-WebRequest -Uri "$BaseUrl/ai/insights" -Method GET | 
                  Select-Object -ExpandProperty Content | ConvertFrom-Json
    
    Write-Host "✅ Found $($aiResponses.Count) AI responses" -ForegroundColor Green
    
    if ($aiResponses.Count -gt 0) {
        Write-Host "🤖 Recent AI responses:" -ForegroundColor Cyan
        foreach ($response in $aiResponses | Select-Object -First 3) {
            Write-Host "  - ID: $($response.id)" -ForegroundColor White
            Write-Host "    Entry ID: $($response.journal_entry_id)" -ForegroundColor Gray
            Write-Host "    Persona: $($response.persona_used)" -ForegroundColor Gray
            Write-Host "    Created: $($response.created_at)" -ForegroundColor Gray
        }
    } else {
        Write-Host "❌ No AI responses found" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Error checking AI responses: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n🔄 Triggering manual cycle..." -ForegroundColor Green
try {
    $manualCycle = Invoke-WebRequest -Uri "$BaseUrl/scheduler/manual-cycle" -Method POST -Body '{"cycle_type": "main"}' -ContentType "application/json" | 
                  Select-Object -ExpandProperty Content | ConvertFrom-Json
    
    Write-Host "✅ Manual cycle triggered: $($manualCycle.status)" -ForegroundColor Green
    Write-Host "📋 Cycle type: $($manualCycle.cycle_type)" -ForegroundColor Cyan
    Write-Host "⏰ Timestamp: $($manualCycle.timestamp)" -ForegroundColor Gray
    
    # Wait a moment for the cycle to complete
    Start-Sleep -Seconds 3
    
    Write-Host "`n📊 Checking updated scheduler status..." -ForegroundColor Green
    $updatedStatus = Invoke-WebRequest -Uri "$BaseUrl/scheduler/status" -Method GET | 
                    Select-Object -ExpandProperty Content | ConvertFrom-Json
    
    Write-Host "📋 Latest cycle results:" -ForegroundColor Cyan
    $latestCycle = $updatedStatus.recent_cycles | Sort-Object timestamp -Descending | Select-Object -First 1
    Write-Host "  - Cycle ID: $($latestCycle.cycle_id)" -ForegroundColor White
    Write-Host "  - Users processed: $($latestCycle.users_processed)" -ForegroundColor White
    Write-Host "  - Opportunities found: $($latestCycle.opportunities_found)" -ForegroundColor White
    Write-Host "  - Engagements executed: $($latestCycle.engagements_executed)" -ForegroundColor White
    Write-Host "  - Duration: $($latestCycle.duration_seconds) seconds" -ForegroundColor White
    
} catch {
    Write-Host "❌ Error triggering manual cycle: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n🎯 Diagnosis Summary:" -ForegroundColor Yellow
Write-Host "=====================" -ForegroundColor Yellow

if ($schedulerStatus.status -eq "running") {
    Write-Host "✅ Scheduler is running" -ForegroundColor Green
} else {
    Write-Host "❌ Scheduler is not running" -ForegroundColor Red
}

if ($testingStatus.testing_mode -eq $true) {
    Write-Host "✅ Testing mode is enabled" -ForegroundColor Green
} else {
    Write-Host "❌ Testing mode is not enabled" -ForegroundColor Red
}

if ($journalEntries.Count -gt 0) {
    Write-Host "✅ Journal entries found" -ForegroundColor Green
} else {
    Write-Host "❌ No journal entries found" -ForegroundColor Red
}

if ($latestCycle.opportunities_found -gt 0) {
    Write-Host "✅ Opportunities are being detected" -ForegroundColor Green
} else {
    Write-Host "❌ No opportunities detected - possible issues:" -ForegroundColor Red
    Write-Host "  - Journal entries may be too short (< 10 characters)" -ForegroundColor Yellow
    Write-Host "  - Journal entries may look like AI responses" -ForegroundColor Yellow
    Write-Host "  - Daily AI response limit may be reached" -ForegroundColor Yellow
    Write-Host "  - User tier/preferences may be restricting responses" -ForegroundColor Yellow
}

Write-Host "`n💡 Recommendations:" -ForegroundColor Yellow
Write-Host "==================" -ForegroundColor Yellow
Write-Host "1. Check if your latest journal entry is longer than 10 characters" -ForegroundColor White
Write-Host "2. Ensure your journal entry doesn't start with AI-like phrases" -ForegroundColor White
Write-Host "3. Check if you've reached your daily AI response limit" -ForegroundColor White
Write-Host "4. Consider upgrading to premium for more AI responses" -ForegroundColor White

Write-Host "`n✅ Debug script completed!" -ForegroundColor Green 