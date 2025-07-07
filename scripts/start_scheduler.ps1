# PowerShell script to start the scheduler and check its status

# Function to start the scheduler
function Start-Scheduler {
    Write-Host "Starting the scheduler..."
    try {
        $response = Invoke-RestMethod -Uri "https://pulsecheck-mobile-app-production.up.railway.app/api/v1/scheduler/start" -Method POST
        Write-Host "Scheduler started successfully: $($response | ConvertTo-Json)"
    }
    catch {
        Write-Host "Error starting scheduler: $($_.Exception.Message)"
    }
}

# Function to check the scheduler status
function Check-SchedulerStatus {
    Write-Host "Checking scheduler status..."
    try {
        $response = Invoke-RestMethod -Uri "https://pulsecheck-mobile-app-production.up.railway.app/api/v1/scheduler/status" -Method GET
        Write-Host "Scheduler status: $($response | ConvertTo-Json)"
    }
    catch {
        Write-Host "Error checking scheduler status: $($_.Exception.Message)"
    }
}

# Start the scheduler
Start-Scheduler

# Wait a moment for the scheduler to initialize
Start-Sleep -Seconds 2

# Check the scheduler status
Check-SchedulerStatus 