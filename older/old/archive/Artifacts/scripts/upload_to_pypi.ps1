# usage upload_to_pypi.ps1 -config [path_to_config] -source [path_to_wheels_folder] -username [pypi_username] -password [pypi_password] -[pypi_repo]
param(
[string]$config,
[string]$source,
[string]$username,
[string]$password,
[string]$repo
)

if ($global:__indent__ -eq $null)
{
    $global:__indent__=0
}

function Write-Host
{
    Microsoft.PowerShell.Utility\Write-Host (' ' * $global:__indent__) -NoNewline
    & 'Microsoft.PowerShell.Utility\Write-Host' $args
}

function Indent
{
    $global:__indent__+=4
}

function UnIndent
{
    $global:__indent__ -= 4
    if ($global:__indent__ -lt 0)
    {
        $global:__indent__ = 0
    }
}

function Get-Target($config)
{
    Get-Content -Raw -Path $config | ConvertFrom-Json
}

Write-Host $([string]::Format("Selected target: {0}", $config))
$__config = Get-Target $config

$_release = $__config.releases.PSObject.Properties["pypi"].Value

$distpath = (New-Item "dist" -type directory).FullName

foreach ($package in $_release.packages)
{
    $__file = Get-ChildItem -Path $source -Filter "$package*.whl" | Select-Object -First 1
    Write-Host $([string]::Format("Copying {0} into '{1}'", $__file, $distpath))
    Copy-Item "$source/$__file" -Destination $distpath
}

foreach ($package in $_release.extensions)
{
    $__file = Get-ChildItem -Path $source -Filter "$package*.whl" | Select-Object -First 1
    Write-Host $([string]::Format("Copying {0} into '{1}'", $__file, $distpath))
    Copy-Item "$source/$__file" -Destination $distpath
}

& twine upload "$distpath/*" -r $repo -u $username -p $password --skip-existing

return 0
