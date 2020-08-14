Param(
[string]$config,
[string]$prefix,
[string]$source,
[string]$workdir,
[string]$wheels = "wheels",
[string]$channel = "test"
)

$global:__indent__ = 0

function Make-Dir($path)
{
    $dir = (New-Item $path -type directory).FullName
    $dir
}

function New-TemporaryDirectory 
{
    $__path = Join-Path ([System.IO.Path]::GetTempPath()) ([System.IO.Path]::GetRandomFileName())
    
    Make-Dir $__path
}

$scriptPath = split-path -parent $MyInvocation.MyCommand.Definition
Write-Host "Script path: " $scriptPath

if (-not $workdir)
{
    $workdir = New-TemporaryDirectory
}
else
{
    if (-not (Test-Path $workdir))
    {
        $workdir = Make-Dir $workdir
    }
}

Write-Host "Working directory: " $workdir

if (-not $config)
{
    $config = [io.path]::combine($scriptPath, "configs", "sdk-test.template")
}
Write-Host "Config template path: " $config

if (-not $prefix)
{
    if ($Env:BUILD_BUILDID)
    {
        $prefix = "$Env:Build_DefinitionName/$Env:Build_BuildId/"
    }
    else
    {
        $prefix = "user/" + [System.Environment]::UserName + "/"
    }
}
Write-Host "Prefix: " $prefix

if (-not $source)
{
    $source = [io.path]::combine($scriptPath, "..", "src")
}
Write-Host "Source path: " $source

$__template = Get-Content -Raw -Path $config
$__config = $__template -replace "{#prefix#}", $prefix
$cfg = "$workdir\sdk-test.userconfig"
$supress = $__config | Out-File -FilePath $cfg -Encoding ASCII

Write-Host "Generated configuration file: " $cfg

$wheels = [io.path]::combine($workdir, $wheels)
Write-Host "Wheels folder: " $wheels

$index = [io.path]::combine($workdir, "index")

if (-not (Test-Path $index))
{
    $index = Make-Dir $index
}

Write-Host "Index folder: " $index

Write-Host "Channel: " $channel

& $scriptPath\build_packages.ps1 -config $cfg -source $source -destination $wheels -channel $channel
& $scriptPath\publish_packages.ps1 -config $cfg -source $wheels -channel $channel
& $scriptPath\update_pypi_index.ps1 -config $cfg -local_path $index -channel $channel