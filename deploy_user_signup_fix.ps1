#!/usr/bin/env pwsh
# ================================================
# DEPLOY USER SIGNUP FIX TO PRODUCTION
# Applies the hotfix migration to resolve signup errors
# ================================================

param(
    [string]$Environment = "production",
    [switch]$DryRun = $false,
    [switch]$Force = $false
)

Write-Host "DEPLOYING USER SIGNUP HOTFIX" -ForegroundColor Cyan
Write-Host "Environment: $Environment" -ForegroundColor Yellow
Write-Host "Dry Run: $DryRun" -ForegroundColor Yellow
Write-Host ""

# Check if Supabase CLI is installed
try {
    $supabaseVersion = npx supabase --version
    Write-Host "Supabase CLI found: $supabaseVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Supabase CLI not found. Please install it first." -ForegroundColor Red
    exit 1
}

# Check if migration file exists
$migrationFile = "supabase/migrations/20250130_fix_user_signup_trigger.sql"
if (-not (Test-Path $migrationFile)) {
    Write-Host "ERROR: Migration file not found: $migrationFile" -ForegroundColor Red
    exit 1
}

Write-Host "Migration file found: $migrationFile" -ForegroundColor Green

# Show migration content preview
Write-Host ""
Write-Host "MIGRATION PREVIEW:" -ForegroundColor Yellow
Write-Host "==================" -ForegroundColor Yellow
Get-Content $migrationFile | Select-Object -First 20
Write-Host "... (showing first 20 lines)"
Write-Host ""

if (-not $Force) {
    $confirmation = Read-Host "Do you want to proceed with deploying this migration? (y/N)"
    if ($confirmation -ne "y" -and $confirmation -ne "Y") {
        Write-Host "Deployment cancelled by user." -ForegroundColor Red
        exit 0
    }
}

Write-Host ""
Write-Host "DEPLOYING MIGRATION..." -ForegroundColor Cyan

if ($DryRun) {
    Write-Host "DRY RUN MODE - Would execute:" -ForegroundColor Yellow
    Write-Host "npx supabase db push --linked" -ForegroundColor White
    Write-Host ""
    Write-Host "Migration would apply the following fixes:" -ForegroundColor Yellow
    Write-Host "  - Fix handle_new_user() function column mapping (user_id -> id)" -ForegroundColor Green
    Write-Host "  - Restore SECURITY DEFINER permissions" -ForegroundColor Green
    Write-Host "  - Add proper error handling to prevent auth failures" -ForegroundColor Green
    Write-Host "  - Verify profiles table structure" -ForegroundColor Green
    Write-Host "  - Ensure RLS policies are correctly configured" -ForegroundColor Green
    Write-Host ""
    Write-Host "DRY RUN COMPLETE - No changes were made" -ForegroundColor Yellow
} else {
    try {
        # Apply migration to linked project (production)
        Write-Host "Applying migration to linked Supabase project..." -ForegroundColor White
        
        # Push the migration
        $output = npx supabase db push --linked 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host ""
            Write-Host "MIGRATION APPLIED SUCCESSFULLY!" -ForegroundColor Green
            Write-Host ""
            Write-Host "USER SIGNUP FIX DEPLOYED" -ForegroundColor Cyan
            Write-Host "=========================" -ForegroundColor Cyan
            Write-Host "- Fixed handle_new_user() trigger function" -ForegroundColor Green
            Write-Host "- Corrected database column mapping" -ForegroundColor Green
            Write-Host "- Restored proper permissions" -ForegroundColor Green
            Write-Host "- Added error handling" -ForegroundColor Green
            Write-Host ""
            Write-Host "TESTING RECOMMENDATIONS:" -ForegroundColor Yellow
            Write-Host "1. Test user signup on your application" -ForegroundColor White
            Write-Host "2. Verify profile creation in Supabase dashboard" -ForegroundColor White
            Write-Host "3. Check auth logs for any remaining errors" -ForegroundColor White
            Write-Host ""
            Write-Host "If signup still fails, check:" -ForegroundColor Yellow
            Write-Host "  - Email confirmation settings in Supabase Auth" -ForegroundColor White
            Write-Host "  - RLS policies on profiles table" -ForegroundColor White
            Write-Host "  - Database connection from your app" -ForegroundColor White
            
        } else {
            Write-Host ""
            Write-Host "MIGRATION FAILED!" -ForegroundColor Red
            Write-Host "Error output:" -ForegroundColor Red
            Write-Host $output
            Write-Host ""
            Write-Host "TROUBLESHOOTING:" -ForegroundColor Yellow
            Write-Host "1. Check your Supabase project connection" -ForegroundColor White
            Write-Host "2. Verify you have admin permissions" -ForegroundColor White
            Write-Host "3. Check if there are any conflicting migrations" -ForegroundColor White
            Write-Host "4. Try running: npx supabase db reset --linked" -ForegroundColor White
            exit 1
        }
        
    } catch {
        Write-Host ""
        Write-Host "DEPLOYMENT ERROR!" -ForegroundColor Red
        Write-Host "Exception: $_" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "POST-DEPLOYMENT VERIFICATION:" -ForegroundColor Cyan
Write-Host "=============================" -ForegroundColor Cyan
Write-Host "Run these commands to verify the fix:" -ForegroundColor White
Write-Host ""
Write-Host "# Check if trigger function exists:" -ForegroundColor Gray
Write-Host "SELECT routine_name FROM information_schema.routines WHERE routine_name = 'handle_new_user';" -ForegroundColor White
Write-Host ""
Write-Host "# Test user signup from your application" -ForegroundColor Gray
Write-Host "# Check Supabase Auth logs for any remaining errors" -ForegroundColor Gray
Write-Host ""

if (-not $DryRun) {
    Write-Host "DEPLOYMENT COMPLETE!" -ForegroundColor Green
    Write-Host "Your user signup should now work correctly." -ForegroundColor Green
}

Write-Host "" 