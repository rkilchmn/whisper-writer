# Create a Windows service wrapper script (e.g., MyService.ps1)

# Define the service name and description
$serviceName = "Whisper Writer"
$serviceDescription = "Service to run Whisper Writer"

# Path to the PowerShell script you want to run
$scriptPath = "C:\Users\I047787\Documents\project\whisper-writer\start.ps1"

# Check if the service already exists and remove it if it does
$existingService = Get-WmiObject -Class Win32_Service -Filter "Name='$serviceName'"
if ($existingService) {
    Write-Host "Removing existing service '$serviceName'..."
    sc.exe stop $serviceName
    sc.exe delete $serviceName
    Write-Host "Existing service removed."
}

# Register the new service
Write-Host "Registering new service '$serviceName'..."
New-Service -Name $serviceName -BinaryPathName "powershell.exe -NoProfile -ExecutionPolicy Bypass -File $scriptPath" -DisplayName $serviceName -Description $serviceDescription -StartupType Automatic
Write-Host "New service registered."

# Start the service
Write-Host "Starting service '$serviceName'..."
Start-Service -Name $serviceName
Write-Host "Service started."
