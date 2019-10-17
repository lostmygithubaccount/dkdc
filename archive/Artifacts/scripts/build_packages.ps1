param(
[string]$config,
[string]$source,
[string]$destination,
[string]$channel = "test"
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

function Build-Package($path_to_packages, $name, $copy_package)
{
    Indent
    Write-Host $([string]::Format("Building package: {0}", $name))
    Indent
    $__curpath = (Get-Item -Path ".\" -Verbose).FullName
    try
    {
        $package_path = "$path_to_packages/$name"
        Set-Location -Path $package_path

        Write-Host "Deleting cached build results"
        if(Test-Path "build")
        {
            Remove-Item "build" -Force -Recurse -ErrorAction Ignore
        }
        if(Test-Path "$name.egg-info") 
        {
            Remove-Item "$name.egg-info" -Force -Recurse -ErrorAction Ignore
        }
        if(Test-Path "dist")
        {
            Remove-Item "dist" -Force -Recurse -ErrorAction Ignore
        }
        
        Start-Sleep -m 1000

        Write-Host 'Building package '$name
        $packagebuild = python "setup.py" bdist_wheel
        Indent
        foreach ($str in $packagebuild)
        {
            Write-Host $str
        }
        UnIndent
        Write-Host 'Done'

        if ($copy_package)
        {
            $__file = Get-ChildItem -Path "dist" -Filter "*.whl" | Select-Object -First 1
            Write-Host $([string]::Format("Copying {0} into '{1}'", $__file, $copy_package))
            Copy-Item "dist/$__file" -Destination $copy_package
        }

    }
    catch
    {        
        return -1
    }
    finally
    {
        Set-Location $__curpath
    }
    UnIndent
    Write-Host $([string]::Format("Package {0} succesfully built", $name))
    UnIndent
}

function Get-Destination($destination)
{
    $__destination = $destination
    if ($__destination)
    {
        if (-not (Test-Path $__destination))
        {
            return (New-Item $__destination -type directory).FullName
        }
        return [system.io.path]::Combine((Get-Location).Path, $__destination)
    }
}

$__original_location = (Get-Location).Path
Set-Location -Path $__original_location
Write-Host $([string]::Format("Selected target: {0}", $config))
$__config = Get-Target $config

$__destination = Get-Destination $destination

$_release = $__config.releases.PSObject.Properties[$channel].Value

$_release.packages

foreach ($package in $__config.source.packages.PSObject.Properties)
{
    if ($_release.packages.Contains($package.Name))
    {
       Write-Host $([string]::Format("Building package: {0}", $package.Name))
       $supress = Build-Package $source $package.Value $__destination
    } 
}

foreach ($extension in $__config.source.extensions.PSObject.Properties)
{
    if ($_release.extensions.Contains($extension.Name))
    {
        Write-Host $([string]::Format("Building extension: {0}", $extension.Name))
        $supress = Build-Package $source $extension.Value $__destination
    }
}

Set-Location -Path $__original_location

return 0
