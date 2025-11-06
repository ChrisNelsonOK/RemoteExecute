# PowerShell System Information Script
# For Windows systems

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "WINDOWS SYSTEM INFORMATION" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Computer Info
$computerInfo = Get-ComputerInfo
Write-Host "Computer Name: $($env:COMPUTERNAME)" -ForegroundColor Green
Write-Host "OS: $($computerInfo.OsName)" -ForegroundColor Green
Write-Host "OS Version: $($computerInfo.OsVersion)" -ForegroundColor Green
Write-Host "OS Build: $($computerInfo.OsBuildNumber)" -ForegroundColor Green
Write-Host ""

# Current User
Write-Host "Current User: $($env:USERNAME)" -ForegroundColor Yellow
Write-Host "User Domain: $($env:USERDOMAIN)" -ForegroundColor Yellow
Write-Host ""

# Memory Info
$memory = Get-CimInstance Win32_OperatingSystem
$totalMemory = [math]::Round($memory.TotalVisibleMemorySize / 1MB, 2)
$freeMemory = [math]::Round($memory.FreePhysicalMemory / 1MB, 2)
$usedMemory = [math]::Round($totalMemory - $freeMemory, 2)

Write-Host "Memory Information:" -ForegroundColor Magenta
Write-Host "  Total: $totalMemory GB" -ForegroundColor White
Write-Host "  Used: $usedMemory GB" -ForegroundColor White
Write-Host "  Free: $freeMemory GB" -ForegroundColor White
Write-Host ""

# Disk Info
Write-Host "Disk Information:" -ForegroundColor Magenta
Get-PSDrive -PSProvider FileSystem | Where-Object { $_.Used -ne $null } | ForEach-Object {
    $totalSize = [math]::Round($_.Used / 1GB + $_.Free / 1GB, 2)
    $freeSize = [math]::Round($_.Free / 1GB, 2)
    $usedSize = [math]::Round($_.Used / 1GB, 2)
    Write-Host "  Drive $($_.Name): Total: $totalSize GB, Used: $usedSize GB, Free: $freeSize GB" -ForegroundColor White
}
Write-Host ""

# Network Adapters
Write-Host "Network Adapters:" -ForegroundColor Magenta
Get-NetAdapter | Where-Object { $_.Status -eq "Up" } | ForEach-Object {
    Write-Host "  $($_.Name): $($_.InterfaceDescription)" -ForegroundColor White
}
Write-Host ""

# Running Processes (top 10 by memory)
Write-Host "Top 10 Processes by Memory:" -ForegroundColor Magenta
Get-Process | Sort-Object -Property WS -Descending | Select-Object -First 10 | ForEach-Object {
    $memoryMB = [math]::Round($_.WS / 1MB, 2)
    Write-Host "  $($_.Name): $memoryMB MB" -ForegroundColor White
}
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Report completed: $(Get-Date)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
