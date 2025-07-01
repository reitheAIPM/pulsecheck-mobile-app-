# AI Immediate Response Testing Script
# Easily control testing mode for immediate AI responses
# Run: .\test_ai_immediate_mode.ps1

param(
    [string]$Action = "status",  # status, enable, disable, trigger
    [string]$UserId = ""         # User ID for specific testing
)

$BASE_URL = "https://pulsecheck-mobile-app-production.up.railway.app"

Write-Host "🧪 PulseCheck AI Testing Mode Controller" -ForegroundColor Cyan
Write-Host "=======================================" -ForegroundColor Cyan
Write-Host ""

function Show-Usage {
    Write-Host "USAGE:" -ForegroundColor Yellow
    Write-Host "  .\test_ai_immediate_mode.ps1 status           # Check current testing mode"
    Write-Host "  .\test_ai_immediate_mode.ps1 enable           # Enable immediate AI responses"
    Write-Host "  .\test_ai_immediate_mode.ps1 disable          # Restore production timing"
    Write-Host "  .\test_ai_immediate_mode.ps1 trigger <userid> # Force AI response for user"
    Write-Host ""
}

function Get-TestingStatus {
    Write-Host "🔍 Checking Testing Mode Status..." -ForegroundColor Yellow
    try {
        $status = curl.exe -s "$BASE_URL/api/v1/scheduler/testing/status" | ConvertFrom-Json
        
        if ($status.testing_mode) {
            Write-Host "✅ TESTING MODE: ENABLED" -ForegroundColor Green
            Write-Host "   - All timing delays bypassed" -ForegroundColor Gray
            Write-Host "   - AI responses are immediate" -ForegroundColor Gray
            Write-Host "   - Bombardment prevention disabled" -ForegroundColor Gray
        } else {
            Write-Host "⏰ PRODUCTION MODE: ENABLED" -ForegroundColor Orange
            Write-Host "   - Normal timing delays active" -ForegroundColor Gray
            Write-Host "   - Initial comments: 5min-1hour" -ForegroundColor Gray
            Write-Host "   - Bombardment prevention: 30min" -ForegroundColor Gray
        }
        
        Write-Host ""
        Write-Host "SCHEDULER STATUS: $($status.scheduler_status)" -ForegroundColor Gray
        
    } catch {
        Write-Host "❌ Failed to get testing status" -ForegroundColor Red
    }
}

function Enable-TestingMode {
    Write-Host "🧪 Enabling Testing Mode..." -ForegroundColor Yellow
    try {
        $result = curl.exe -s -X POST "$BASE_URL/api/v1/scheduler/testing/enable" | ConvertFrom-Json
        
        if ($result.testing_enabled) {
            Write-Host "✅ TESTING MODE ENABLED!" -ForegroundColor Green
            Write-Host "   $($result.message)" -ForegroundColor Gray
            Write-Host ""
            Write-Host "⚠️  WARNING: $($result.warning)" -ForegroundColor Red
            Write-Host ""
            Write-Host "NEXT STEPS:" -ForegroundColor Cyan
            foreach ($step in $result.next_steps) {
                Write-Host "   $step" -ForegroundColor Gray
            }
        } else {
            Write-Host "❌ Failed to enable testing mode" -ForegroundColor Red
        }
        
    } catch {
        Write-Host "❌ Error enabling testing mode" -ForegroundColor Red
    }
}

function Disable-TestingMode {
    Write-Host "🔄 Disabling Testing Mode..." -ForegroundColor Yellow
    try {
        $result = curl.exe -s -X POST "$BASE_URL/api/v1/scheduler/testing/disable" | ConvertFrom-Json
        
        if ($result.testing_disabled) {
            Write-Host "✅ TESTING MODE DISABLED!" -ForegroundColor Green
            Write-Host "   $($result.message)" -ForegroundColor Gray
            Write-Host ""
            Write-Host "✅ $($result.confirmation)" -ForegroundColor Green
            Write-Host ""
            Write-Host "PRODUCTION TIMING RESTORED:" -ForegroundColor Cyan
            Write-Host "   - Initial comments: $($result.timing_restored.initial_comments)" -ForegroundColor Gray
            Write-Host "   - Collaborative responses: $($result.timing_restored.collaborative_responses)" -ForegroundColor Gray
            Write-Host "   - Bombardment prevention: $($result.timing_restored.bombardment_prevention)" -ForegroundColor Gray
        } else {
            Write-Host "❌ Failed to disable testing mode" -ForegroundColor Red
        }
        
    } catch {
        Write-Host "❌ Error disabling testing mode" -ForegroundColor Red
    }
}

function Trigger-ImmediateResponse {
    param([string]$TargetUserId)
    
    if (-not $TargetUserId) {
        Write-Host "❌ User ID required for triggering immediate response" -ForegroundColor Red
        Write-Host "   Usage: .\test_ai_immediate_mode.ps1 trigger <user_id>" -ForegroundColor Gray
        return
    }
    
    Write-Host "🚀 Triggering Immediate AI Response..." -ForegroundColor Yellow
    Write-Host "   Target User: $TargetUserId" -ForegroundColor Gray
    
    try {
        $result = curl.exe -s -X POST "$BASE_URL/api/v1/scheduler/testing/immediate-response?user_id=$TargetUserId" | ConvertFrom-Json
        
        if ($result.status -eq "triggered") {
            Write-Host "✅ IMMEDIATE RESPONSE TRIGGERED!" -ForegroundColor Green
            Write-Host "   $($result.message)" -ForegroundColor Gray
            Write-Host "   $($result.note)" -ForegroundColor Orange
        } else {
            Write-Host "❌ Failed to trigger immediate response" -ForegroundColor Red
        }
        
    } catch {
        Write-Host "❌ Error triggering immediate response" -ForegroundColor Red
        Write-Host "   Make sure testing mode is enabled first" -ForegroundColor Orange
    }
}

function Trigger-ManualCycle {
    Write-Host "🔄 Triggering Manual AI Cycle..." -ForegroundColor Yellow
    try {
        $result = curl.exe -s -X POST "$BASE_URL/api/v1/scheduler/manual-cycle?cycle_type=main" | ConvertFrom-Json
        
        if ($result.status -eq "triggered") {
            Write-Host "✅ MANUAL CYCLE TRIGGERED!" -ForegroundColor Green
            Write-Host "   $($result.message)" -ForegroundColor Gray
        } else {
            Write-Host "❌ Failed to trigger manual cycle" -ForegroundColor Red
        }
        
    } catch {
        Write-Host "❌ Error triggering manual cycle" -ForegroundColor Red
    }
}

# Main script logic
switch ($Action.ToLower()) {
    "status" {
        Get-TestingStatus
    }
    "enable" {
        Enable-TestingMode
        Write-Host ""
        Write-Host "💡 TIP: Create a journal entry now to test immediate AI response!" -ForegroundColor Cyan
    }
    "disable" {
        Disable-TestingMode
    }
    "trigger" {
        Trigger-ImmediateResponse -TargetUserId $UserId
    }
    "cycle" {
        Trigger-ManualCycle
    }
    default {
        Write-Host "❌ Invalid action: $Action" -ForegroundColor Red
        Write-Host ""
        Show-Usage
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🎯 QUICK COMMANDS:" -ForegroundColor Green
Write-Host "Status:   .\test_ai_immediate_mode.ps1 status"
Write-Host "Enable:   .\test_ai_immediate_mode.ps1 enable"
Write-Host "Disable:  .\test_ai_immediate_mode.ps1 disable"
Write-Host "Cycle:    .\test_ai_immediate_mode.ps1 cycle"
Write-Host "" 