param(
  [string]$envname = "env",
  [string]$pyenv = "3.5.2",
  [string]$envfile
)

if (Get-Command "conda" -ErrorAction SilentlyContinue) {
  echo "Conda is installed, moving on..."
} else {

  # $CondaInstaller = "Miniconda3-4.2.12-Windows-x86_64.exe"

  $CondaInstaller = "Miniconda3-4.5.4-Windows-x86_64.exe"
  $CondaInstallerUrl = "https://viennabuildinfra.blob.core.windows.net/" +
                       "build-tools/conda/win32/$CondaInstaller"
  $InstDir =
    Join-Path -Path $env:LOCALAPPDATA -ChildPath "Miniconda/4.5.4c"

  if (!(Test-Path $InstDir)) {
    echo "Downloading miniconda"
    Invoke-WebRequest -Uri $CondaInstallerUrl -OutFile $CondaInstaller
    echo "Installing miniconda into $InstDir"
    Start-Process $CondaInstaller `
      @("/AddToPath=0", "/RegisterPython=0", "/NoRegistry=1", "/S", "/D=$InstDir") `
      -Wait
    echo "Done with install"
  } else {
    echo "Found installation"
  }

  if (!(Test-Path "$InstDir/scripts/conda.exe")) {
    Write-Error "Conda executable not found!"
    exit 1
  }
  echo "Setup complete!"

  foreach ($sub in @("", "\Library\mingw-w64\bin", "\Library\usr\bin", "\Library\bin", "\Scripts")) {
    echo "adding ""...Miniconda...$sub"" to PATH..."
    $env:PATH += ";C:\Users\VssAdministrator\AppData\Local\Miniconda\4.5.4c$sub"
  }

  echo "... PATH = ${env:PATH}"


  function Invoke-CmdScript {
    param([String] $scriptName)
    $cmdLine = """$scriptName"" $args & set"
    & $Env:SystemRoot\system32\cmd.exe /c $cmdLine |
    Select-String '^([^=]+)=(.+)$' | ForEach-Object {
      $varName = $_.Matches[0].Groups[1].Value
      $varValue = $_.Matches[0].Groups[2].Value
      Write-Host "Setting env variable $varName=$varValue"
      Set-Item Env:$varName $varValue
    }
  }
  Invoke-CmdScript "$InstDir\scripts\activate"

}

Write-Host "Turning auto-update off"
conda config --set auto_update_conda false

if ((Get-Command "activate").Name -like "*.ps1") {
  echo "Conda activate extension is installed, moving on..."
} else {
  echo "Installing conda activate extension..."
  $suppress = conda install -y -n root -c pscondaenvs pscondaenvs 2>&1
  Write-Host $suppress
}

#$envs = conda env list --json | ConvertFrom-Json
#if (-not ($envs.envs | select $_.basename | Split-Path -leaf).Contains($envname))

if ($envfile)
{
    Write-Host "Creating environment from file " $envfile
    $suppress = conda env create -f $envfile 2>&1 | Out-File -LiteralPath "conda.log" -Append
    Write-Host $suppress
    $envname = [System.IO.Path]::GetFileNameWithoutExtension($envfile)
}
else
{
    Write-Host "Creating environment " $envname "with python=" $pyenv
    $suppress = conda create -n $envname -y python="$pyenv" 2>&1 | Out-File -LiteralPath "conda.log" -Append
    Write-Host $suppress
}

echo "Activating ""$envname"""
activate $envname *>$null

conda info

echo "Activated ""$envname"""
