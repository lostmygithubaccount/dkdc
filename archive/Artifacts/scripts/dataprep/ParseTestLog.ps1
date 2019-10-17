Param(
  [string]$logPath = "$PSScriptRoot\testlog.txt"
)

if (![System.IO.File]::Exists($logPath)) {
    throw "Cannot find test log file"
}

$logContent = Get-Content $logPath -Encoding UTF8
Write-Host ($logContent | Out-String).Replace("\r", "\r\n").Replace("[32m", "").Replace("[39m", "").Replace("[31m", "")

$failureCount = [Int]::Parse($logContent[$logContent.Length - 1].Substring("Exiting... ".Length))
if ($failureCount -ne 0) {
    exit 1
}
exit 0