param (
    [Parameter()]
    [ValidateNotNullOrEmpty()]
    [string]$installDir=$(throw "installDir is required"),
    [switch]$NoVersionTag)

if (Test-Path $installDir\*) {
    throw "Provided install directory must be empty, this is a requirment of Visual Studio Installer."
}

$webClient = New-Object System.Net.WebClient
$downloadDir = "$env:USERPROFILE\Downloads"
$vsInstaller = "$downloadDir\vs-enterprise.exe"

Write-Host "Installing Visual C++ 2017 15.latest..."
$webClient.DownloadFile("https://aka.ms/vs/15/release/vs_enterprise.exe", $vsInstaller)
Start-Process -FilePath $vsInstaller -PassThru -Wait -ArgumentList "-q","--wait","--norestart","--add Microsoft.VisualStudio.Component.VC.Runtimes.x86.x64.Spectre","--installPath $installDir"
Write-Host "Completed."

Write-Host "The VC++ Compiler should be located inside 'VC\Tools\MSVC'. Zip up the folder there (named after the version of VC++ downloaded) and uploaded that to viennabuildinfra blob store."
