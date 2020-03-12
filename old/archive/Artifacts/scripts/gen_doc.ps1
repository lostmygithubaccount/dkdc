param(
    [string]$docfx,
    # list of packages to build
    [string]$packages = "azureml-core"
)

function Resolve-FullPath($path) 
{
    if (Test-Path $path)
    {
        $p = Resolve-Path $path
        return $p.Path
    }
    return $null
}

function Update-Issues($code, $issue, $issues)
{
    if ($code -ne 0)
    {
        $issues+=$issue
    }
    return $issues
}

$curpath = Get-Location

$issues = New-Object System.Collections.ArrayList

try 
{
    $scriptpath = Resolve-FullPath (Split-Path -parent $PSCommandPath)
    $rootpath = Resolve-FullPath ([System.IO.Path]::Combine($scriptpath, ".."))
    $sourcepath = Resolve-FullPath ([System.IO.Path]::Combine($rootpath, "src"))
    $docpath = [System.IO.Path]::Combine($rootpath, "docbuild")
    $docconfigs = [System.IO.Path]::Combine($rootpath, "docs")

    Remove-Item -Path $docpath -Recurse -Force -ErrorAction SilentlyContinue

    Set-Location -Path $rootpath

    & python -m pip install -U sphinx-docfx-yaml --disable-pip-version-check

    $pkgs = $packages.Split(",")

    $docfxexe = Resolve-FullPath ([System.IO.Path]::Combine($docfx, "docfx.exe"))

    foreach ($pkg in $pkgs) 
    {
        $pkg = $pkg.Trim()
        $pkgpath = [System.IO.Path]::Combine($sourcepath, $pkg)

        & python -m pip install -e $pkgpath --disable-pip-version-check

        $pkgdocpath = "$docpath\$pkg-doc"
        $pkgsrcpath = "$docpath\$pkg"

        Copy-Item $docconfigs -Destination "$pkgdocpath" -Recurse -Force -ErrorAction SilentlyContinue
        

        Copy-Item "$pkgpath\azureml" -Destination "$pkgsrcpath\azureml" -Recurse -Force

        get-childitem -Path $pkgsrcpath -Include tests -Recurse -force | Remove-Item -Force –Recurse

        Set-Location $pkgdocpath
        new-item "_static" -itemtype directory -Force
        new-item "_build" -itemtype directory -Force
        new-item "_templates" -itemtype directory -Force

        Write-Host "Building API doc"
        & sphinx-apidoc --module-first --no-headings --no-toc --implicit-namespaces "$pkgsrcpath" -o "$pkgdocpath" tests/*

        $issues = Update-Issues $LASTEXITCODE ([string]::Format("Sphinx-ApiDoc failed for {0}", $pkg)) $issues

        Write-Host "Building Docs"       
        & sphinx-build . _build -W -N -T

        $issues = Update-Issues $LASTEXITCODE ([string]::Format("Sphinx-Build failed for {0}", $pkg)) $issues
    }
   
    if ($docfxexe -and ($pkgs.Length -eq 1))
    {
        Write-Host "Using DocFX found at $docfxexe"

        & $docfxexe init -q

        #copy yaml files
        $ymlsource = [System.IO.Path]::Combine($pkgdocpath, "_build", "docfx_yaml")
        $ymldestination = [System.IO.Path]::Combine($pkgdocpath, "docfx_project", "api")

        $files = Get-ChildItem -Path $ymlsource
        foreach ($f in $files) 
        {
            Copy-Item $f.FullName -Destination $ymldestination -Recurse -Force
        }

        $docfxconfig = [System.IO.Path]::Combine($pkgdocpath, "docfx_project", "docfx.json")
        # & $docfxexe

        Write-Host "Serving Docs"
        & $docfxexe $docfxconfig --serve
    }
    else
    {
        Write-Host "Skipping docfx part"
    }
}
finally 
{
    if ($issues.Length -ne 0)
    {
        $global:LASTEXITCODE = 13
        Write-Host "#####################################################################"
        foreach ($issue in $issues)
        {
            Write-Host $issue
        }
        Write-Host "#####################################################################"
        [Console]::Out.Flush()
        Write-Error "There are few failures, please see sphinx output"
    }
    Set-Location -Path $curpath
}
