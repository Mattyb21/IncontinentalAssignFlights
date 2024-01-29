$filePath = "Z:\Incont\Insert Queries\Log.txt"

while ($true) {
    try {
        if (Test-Path -Path $filePath) {
            Get-Content -Path $filePath -Wait
        } else {
            Write-Host "File not found. Waiting for the file to be created..."
            while (-not (Test-Path -Path $filePath)) {
                Start-Sleep -Seconds 5  # You can adjust the sleep interval as needed
            }
        }
    } catch {
        Write-Host "An error occurred: $($_.Exception.Message)"
        Write-Host "Pausing indefinitely. To resume, manually stop and restart the script."
        while ($true) {
            Start-Sleep -Seconds 3600  # Pause indefinitely (adjust as needed)
        }
    }
}
