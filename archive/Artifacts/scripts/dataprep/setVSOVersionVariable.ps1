$version = Get-Content version.txt | Out-String
Write-Host "##vso[task.setvariable variable=version]$version"
$segments = $version.Split(".")
$newSegments = foreach($seg in $segments) { $seg.Substring(0, $seg.Length - 1).TrimStart("0") + $seg.Substring([System.Math]::Max(0,$seg.Length - 1)) }
$versionNoLeadingZeros = [string]::Join(".", $newSegments)
Write-Host "##vso[task.setvariable variable=versionNoLeadingZeros]$versionNoLeadingZeros"
