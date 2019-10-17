param(
[string]$package="azureml-sdk",
[string]$versions="all",
[string]$extras="automl,notebooks,explain",
[string]$path="dependencies",
[string]$workdir="depmon",

[string]$subscription,
[string]$account,
[string]$resource,
[string]$container
)

function Get-Package-Info($package, $version="")
{
    Write-Host "Getting info for" $package $version
    if ($version)
    {
        $_Uri = [string]::Format("https://pypi.org/pypi/{0}/{1}/json", $package, $version)
    }
    else
    {
        $_Uri = [string]::Format("https://pypi.org/pypi/{0}/json", $package)
    }

    $_rawresponse = Invoke-WebRequest -Uri $_Uri -ErrorVariable $err -ErrorAction SilentlyContinue

    $_rawresponse.Content | ConvertFrom-Json
}


function ConvertTo-Hashtable($psObject)
{ 
    $spec = @{}
    foreach ($obj in $psObject.psobject.properties) 
    { 
        if ($obj.Value -and $obj.Value.GetType().Name -eq "PSCustomObject")
        {
            $spec[$obj.Name] = ConvertTo-Hashtable $obj.Value
        }
        else
        {
            $spec[$obj.Name] = $obj.Value
        }
     } 
     return $spec
}

function Strip-Requirement($reqstring)
{
    if ($reqstring)
    {
        $reqstring.Trim('(').Trim(')').Split(',') -join ','
    }
    else
    {
        ""
    }
}

function Get-Date-DateTime($str)
{
    [datetime]$str
}

function Get-Packages-Recursive($dependencies, $package, $level, $extraslist)
{
    $pi = Get-Package-Info $package
    $content = ConvertTo-Hashtable $pi
    $dependencies[$package]['release-date'] = Get-Date-DateTime $content.releases[$content.info.version][0].upload_time
    $dependencies[$package]['version'] = $content.info.version
    foreach ($ci in $content.info.requires_dist)
    {
         # parsing the requirements
        $reqparts = $ci.Split(";", 2, [System.StringSplitOptions]::RemoveEmptyEntries)
        # if requirement is conditional
        if ($reqparts[1] -and $reqparts[1].Contains("extra"))
        {
            if ($extraslist)
            {
                $rgx = ([regex]".* extra ==.*'(.*)'").Matches($reqparts[1])
                if (!$rgx.Count) 
                { 
                    contunue
                }
                if ($rgx[0].Groups[1].Value -inotin $extraslist)
                {
                    Write-Host "Skipping extras" $rgx[0].Groups[1].Value "on" $package
                    continue
                }
                else
                {
                    Write-Host "Getting extras" $rgx[0].Groups[1].Value "on" $package
                }
            }
            else
            {
                Write-Host "Skipping" $ci "on" $package
                continue
            }            
        }
        $requirement = $reqparts[0].Split(" ",2)

        $requirement[0] = $requirement[0].Split('[')[0]

        $rgx = ([regex]".*\[([^\]]*)\]").Matches($requirement)
        if ($rgx.Count)
        {
            Write-Host "Found dependency on extras" $requirement
            $newextras = $rgx[0].Groups[1].Value.Split(',', [System.StringSplitOptions]::RemoveEmptyEntries) 
        }
        else
        {
            $newextras = $null
        }

        $reqvers = Strip-Requirement $requirement[1]
        if ($dependencies[$requirement[0]])
        {
            $dependencies[$requirement[0]].requirement+=",$reqvers"
            $s = $dependencies[$requirement[0]].requiredby.Add($package)
            if ($level -le $dependencies[$requirement[0]].level)
            {
                $dependencies[$requirement[0]].level = $level
            }
        }
        else
        {
            $reqby =  New-Object System.Collections.ArrayList 
            $reqby.Add($package)
            $dependencies[$requirement[0]] = @{'requirement' = $reqvers; 'requiredby' = $reqby; 'level' = $level}
            $_l = $level+1
            Get-Packages-Recursive $dependencies $requirement[0] $_l $newextras
        }      
    }    
}

New-Item -ItemType Directory -Path $workdir -Force
$loc = Get-Location
Set-Location -Path $workdir

if (!$versions)
{
    $versions = @($null)
}

if ($extras)
{
    $extraslist = $extras.Split(',')
}

$roothtml = "<html><head><title>SDK Release - Dependency Status</title><meta name='api-version' value='2' /></head><body>"

if ($versions -eq "all")
{
    $pinfo = Get-Package-Info "azureml-sdk"
	$versions = $pinfo.releases.psobject.properties.Name -join ","
}

foreach ($version in $versions.Split(','))
{
    $pi = Get-Package-Info $package $version
    $content = ConvertTo-Hashtable $pi

    $dependencies = @{}
    $dependencies[$package] = @{'requirement' = $version; 'release-date' = Get-Date-DateTime $content.releases[$content.info.version][0].upload_time; 'level' = 0; 'requiredby'=@('VALIDATION'); 'version'=$content.info.version}


    foreach ($ci in $content.info.requires_dist)
    {
         # parsing the requirements
        $reqparts = $ci.Split(";", 2, [System.StringSplitOptions]::RemoveEmptyEntries)
        # if requirement is conditional
        if ($reqparts[1] -and $reqparts[1].Contains("extra"))
        {
            if ($extraslist)
            {
                $rgx = ([regex]".* extra ==.*'(.*)'").Matches($reqparts[1])
                if (!$rgx.Count) 
                { 
                    contunue
                }
                if ($rgx[0].Groups[1].Value -inotin $extraslist)
                {
                    Write-Host "Skipping extras" $rgx[0].Groups[1].Value "on" $package
                    continue
                }
                else
                {
                    Write-Host "Getting extras" $rgx[0].Groups[1].Value "on" $package
                }
            }
            else
            {
                Write-Host "Skipping" $ci "on" $package
                continue           
            } 
        }
        $requirement = $reqparts[0].Split(" ",2)

        $requirement[0] = $requirement[0].Split('[')[0]
        $rgx = ([regex]".*\[([^\]]*)\]").Matches($requirement)
        if ($rgx.Count)
        {
            Write-Host "Found dependency on extras" $requirement
            $newextras = $rgx[0].Groups[1].Value.Split(',', [System.StringSplitOptions]::RemoveEmptyEntries) 
        }
        else
        {
            $newextras = $null
        }
        
        $reqvers = Strip-Requirement $requirement[1]
        $reqby =  New-Object System.Collections.ArrayList 
        $s = $reqby.Add($package)

        $dependencies[$requirement[0]] = @{'requirement' = $reqvers; 'requiredby' = $reqby; 'level' = 1}
        $s = Get-Packages-Recursive $dependencies $requirement[0] 2 $newextras
    }


    $s = ""
    foreach ($k in $dependencies.Keys)
    {
        if ($dependencies[$k]["release-date"] -gt $dependencies[$package]["release-date"])
        {
            $bgcolor = "#FFFF00"
        }
        else
        {
            $bgcolor = "#ADFF2F"   
        }
    
        $dependencies[$k]["requirement"] = ($dependencies[$k]["requirement"].Split(',', [System.StringSplitOptions]::RemoveEmptyEntries) | Get-Unique) -join ','
        $dependencies[$k]["requiredby"] = ($dependencies[$k]["requiredby"] | Get-Unique) -join ','

        $s+=[string ]::Format('<tr bgcolor="{6}"><td>{0}</td><td>{1}</td><td>{2}</td><td>{3}</td><td>{4}</td><td>{5}</td></tr>', $k, $dependencies[$k]["release-date"], $dependencies[$k]["version"], $dependencies[$k]["requiredby"], $dependencies[$k]["requirement"], $dependencies[$k]["level"], $bgcolor)
    }

    $html = '<html xmlns="http://www.w3.org/1999/xhtml"><head><title>HTML TABLE</title></head><body><table><tr><th>Name</th><th>ReleaseDate</th><th>Version</th><th>RequiredBy</th><th>Requirement</th><th>Level</th></tr>{0}</table></body></html>'    $html = [string]::Format($html, $s)    $folder = $dependencies[$package]['version']    New-Item -ItemType Directory -Path $folder -Force    $html | Out-File -FilePath "$folder\index.html"    $date = $dependencies[$package]['release-date']    $updated = (Microsoft.PowerShell.Utility\Get-Date).ToUniversalTime()    $roothtml+="<a href='./$path/$folder/'>$folder :: released on $date :: updated on $updated</a></br>"
}

$roothtml+="</body></html>"
$roothtml | Out-File -FilePath "index.html"
if ($subscription)
{
    Write-Host $([string]::Format("Deploying report into '{0}/{1}/{2}'", $account, $container, $path))

    $supress = Set-AzureSubscription -SubscriptionName $subscription -ErrorAction SilentlyContinue
    $supress = Set-AzureRmCurrentStorageAccount -Name $account -ResourceGroupName $resource

    $__files = Get-ChildItem -Recurse –File

    $__blobProperties = @{"ContentType" = "text/html"};

    foreach ($_file in $__files)
    {
        $__blob = [string]::Concat($path, $_file.FullName.Substring((Get-Location).Path.Length))
        Set-AzureStorageBlobContent -File $_file.FullName -Container $container -Blob $__blob -Force -Properties $__blobProperties
    }  
    Write-Host "Report:: Completed"
}

Set-Location -Path $loc