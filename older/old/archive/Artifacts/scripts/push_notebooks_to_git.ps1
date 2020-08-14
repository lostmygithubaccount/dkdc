param(
# json file with the test descriptions (release.json)
[string]$scenario,
# names of the tests to run, if empty all the test will be executed
[string]$names,
# run predefined set of notebooks
[string]$channel,
# python version
[string]$pyenv = "3.5.2",
[string]$index,
[string]$sdkpinto,
# path to the folder with the notebook files
[string]$path = "..\notebooks",
# working directory, will be created if not exist
[string]$workdir = "Artifacts",
[string]$subscription = "589c7ae9-223e-45e3-a191-98433e0821a9",
[string]$tenant = "72f988bf-86f1-41af-91ab-2d7cd011db47",
[string]$client = "402c2410-f4fe-4aa0-b993-1a7c7037cab5",
# specifies resource group, if empty the new one will be created
#    (aml_nbgit_rg_[DATETIME]) and deleted after completion
[string]$resourcegroup,
[string]$workspace = 'aml_nbgit_ws',
[string]$location = "eastus2euap",
[string]$baseenv = 'gitsamples',
# SP password
[string]$password,
# parameters to run in parallel on the build agent
[string]$slice,
[string]$totalslices,
# secrets to set as env vars
[string]$secrets,

# repo owner "Azure"
[string]$owner = "Azure",
# project "ViennaDocs"
[string]$project = "ViennaDocs",
# "path/to/my/file/in/repo"
[string]$repopath = "PrivatePreview/notebooks",
# branch "master"
[string]$branch = "test",
# "commit message"
[string]$message = "update",
# authorization token, GIT part will be ignored if token is not set
[string]$token,

# set to true to see more messages from the script
[bool]$debug = $True,
# report as test results
[bool]$runastests = $False
)


$debug = $debug
$defaultTimeout = 1200

if ($sdkpinto)
{
    Write-Host "Pinning sdk to " $sdkpinto
}

function Get-Random-RG($resourcegroup)
{
    $date = Get-Date
    $rg = $resourcegroup + "_" + $date.ToFileTimeUtc()
    $rg
}

function Log-In($subscription, $tenant, $client, $password)
{
    Write-Host "Logging in with SP:"
    & az login --service-principal -u $client -p $password -t $tenant
    & az account set --subscription $subscription
    Write-Host "Done!"
}

function Get-Target($scenario)
{
    Get-Content -Raw -Path $scenario | ConvertFrom-Json
}

function ConvertTo-Hashtable($psObject)
{
    $spec = @{}
    foreach ($obj in $psObject.psobject.properties)
    {
        if ($obj.Value.GetType().Name -eq "PSCustomObject")
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


function Merge-Include($path, $hashTable)
{
    $root = $path
    [System.Collections.ArrayList]$__uploads = @()
    if ($hashTable.uploads)
    {
        foreach ($u in $hashTable.uploads)
        {
            $__uploads.Add([system.io.path]::combine($path, $u))
        }
    }
    $hashTable.uploads = $__uploads

    if ($hashTable -and $hashTable.include)
    {
        foreach ($h in $hashTable.include.GetEnumerator())
        {
            $key = $h.Name

            $newpath = [system.io.path]::combine($path, $h.Value)
            $nbpath = [system.io.path]::combine($newpath, "release.json")

            $raw_include_nb = Get-Target $nbpath
            $ht_include_nb = ConvertTo-Hashtable $raw_include_nb
            $include_nd = Merge-Include $newpath $ht_include_nb

            if ($include_nd.uploads)
            {
                foreach ($u in $include_nd.uploads)
                {
                    $hashTable.uploads.Add($u)
                }
            }

            foreach ($n in $include_nd.notebooks.GetEnumerator())
            {
                $id = $key+"-"+$n.Name
                $n.Value.path=[system.io.path]::Combine($newpath.Substring($root.Length),$n.Value.path).Trim('\')
                $hashTable.notebooks.Add("$id", $n.Value)
            }

            foreach ($chnl in $include_nd.channels.GetEnumerator())
            {
                if ($hashTable.channels.$($chnl.Name))
                {
                     $hashTable.channels.$($chnl.Name) += $chnl.Value | ForEach-Object {"$key-$_"}
                }
                else
                {
                    $hashTable.channels.$($chnl.Name) = $chnl.Value | ForEach-Object {"$key-$_"}
                }
            }

        }
    }

    return $hashTable
}

function Get-Notebook($path, $file, $name)
{
    $tocopy = [io.path]::combine($path, $file)
    Copy-Item $tocopy -Destination $name -Recurse -Force
}

function Resolve-FullPath($path)
{
    $p = Resolve-Path $path
    $p.Path
}

function Pip-Install($package, $extraindex, $flags="--disable-pip-version-check")
{
    Write-Host "Installing package: " $package
    if ($extraindex -ne $null)
    {
        $output = & pip install $package --extra-index-url "https://pypi.python.org/simple" --index-url $extraindex $flags --no-cache-dir 2>&1
    }
    else
    {
        $output = & pip install $package $flags --no-cache-dir 2>&1
    }
    if ($debug)
    {
        Write-Host $output
    }
}

function Conda-Install($package)
{
    Write-Host "Installing conda package: " $package

    $s = & conda install -y $package *>&1
    Write-Host $s
}

function Pip-Update($package, $extraindex, $flags="--disable-pip-version-check")
{
    Pip-Install $package $extraindex @($flags, "-U")
}

function Create-Config($file, $subscription, $resourcegroup, $workspace)
{
    $supress = New-Item -ItemType File -Path $file -Force
    [string]::Format("{{""subscription_id"": ""{0}"", ""resource_group"": ""{1}"", ""workspace_name"": ""{2}""}}", $subscription, $resourcegroup, $workspace)| Add-Content $file
}

function Not-In-Slice($i, $slice, $totalslices)
{
    if ($slice)
    {
        if ($i%$totalslices -eq ($slice-1))
        {
            return $False
        }
        else
        {
            return $True
        }
    }
    else
    {
        return $False
    }
}

function Setup-Base-Env($index, $sdkpinto)
{
    $supress = & conda install -y testpath==0.3.1 *>&1
    if ($debug)
    {
        Write-Host $suppress
    }

    # Install requirements to the base environment
    Write-Host "Setting up environment. That's take a while..."
    $suppress = & conda install -y nb_conda *>&1
    if ($debug)
    {
        Write-Host $suppress
    }

    $suppress = & conda install -y jupyter_client==5.3.1 *>&1
    if ($debug)
    {
        Write-Host $suppress
    }

    # installing pip
    $output = & python -m pip install pip==18.0 2>&1
    Pip-Install "dash[testing]"
    Pip-Install "applicationinsights"
    Pip-Install "pytest"
    Pip-Install "azureml-sdk$sdkpinto" $index

    if ($debug)
    {
        & conda info
    }
    Write-Host "Base environment packages"
    & pip list -v --disable-pip-version-check

}


function Use-Agent-Conda-Env($baseenv, $pyenv, $index, $sdkpinto)
{

    & conda create -y --name $baseenv python=$pyenv
    activate $baseenv
    Setup-Base-Env $index $sdkpinto
}

function Prepare-Env($createenv, $baseenv, $pyenv, $index, $sdkpinto)
{
    Write-Host "Creating environment" $baseenv
    $suppress = & $createenv -envname $baseenv -pyenv $pyenv *>&1
    activate $baseenv
    if ($debug)
    {
        Write-Host $suppress
    }
    Setup-Base-Env $index $sdkpinto
}

function Push-To-GitHub($sourceFile, $repoPath, $gitpush)
{
    if (Test-Path -Path $sourceFile -PathType Container)
    {
       $_files = Get-ChildItem -Path $sourceFile
       $folder = Split-Path $sourceFile -Leaf
       $_repopath = $repoPath + "/" + $folder
       foreach ($_file in $_files)
       {
          $depfullfilename = [io.path]::combine($sourceFile, $_file.Name)

          Push-To-GitHub $depfullfilename $_repopath $gitpush
       }
    }
    else
    {
       & $gitpush $sourceFile $owner $project $repoPath $branch $message $token
    }
}

function Execute-Notebook-In-Env($path, $workdir, $nb, $baseenv, $subscription, $rg, $workspace, $index, $sdkpinto)
{
    Set-Location $workdir
    $supress = New-Item -ItemType Directory -Path $nb.Name -Force
    Set-Location $nb.Name
    $workdir_proj = Get-Location

    if ($nb.Value.projectfolder)
    {
        $supress = New-Item -ItemType Directory -Path $nb.Value.projectfolder -Force
    }

    # Creating ne conda enviroment to run the notebook
    $condaenvname = "sample-" + (Get-Date -UFormat "%Y-%m-%d-%H-%M-%S")
    $suppress = & conda create -y --name $condaenvname --clone $baseenv *>&1

    Write-Host $suppress

    activate $condaenvname
    if ($debug)
    {
        & conda info
    }
    $nbname = $nb.Value.name
    $nbfullname = [io.path]::combine($workdir, $nb.Name, $nbname)
    $nbname_new = [io.path]::GetFileNameWithoutExtension($nbname) + ".nbconvert.ipynb"
    $nbfullname_new = [io.path]::combine($workdir, $nb.Name, $nbname_new)
    if ($nb.Value.path)
    {
        $nbpath = [io.path]::combine($path, $nb.Value.path)
    }
    else
    {
        $nbpath = $path
    }
    Write-Host $nbfullname

    # copy notebooks and its dependencies into the folder
    Get-Notebook $nbpath $nbname $workdir_proj
    foreach ($dep in $nb.Value.dependencies)
    {
        #check if dependency is in specified path otherwise use from the root
        $dep_file = [io.path]::combine($nbpath, $dep)
        if (Test-Path -Path "$dep_file")
        {
            Get-Notebook $nbpath $dep $workdir_proj
        }
        else
        {
            Get-Notebook $path $dep $workdir_proj
        }
    }
    # copy preexec scripts into working directory
    foreach ($dep in $nb.Value.preexec)
    {
        #check if dependency is in specified path otherwise use from the root
        $dep_file = [io.path]::combine($nbpath, $dep)
        if (Test-Path -Path "$dep_file")
        {
            Get-Notebook $nbpath $dep $workdir_proj
        }
        else
        {
            Get-Notebook $path $dep $workdir_proj
        }
    }

    # copy postexec scripts into working directory
    foreach ($dep in $nb.Value.postexec)
    {
        #check if dependency is in specified path otherwise use from the root
        $dep_file = [io.path]::combine($nbpath, $dep)
        if (Test-Path -Path "$dep_file")
        {
            Get-Notebook $nbpath $dep $workdir_proj
        }
        else
        {
            Get-Notebook $path $dep $workdir_proj
        }
    }

    # installing additional requirements per notebook
    foreach ($req in $nb.Value.requirements)
    {
        if ($req.StartsWith("azureml-") -and !$req.StartsWith("azureml-dataprep"))
        {
            Pip-Update "$req$sdkpinto" $index
        }
        else
        {
            Pip-Update $req $index
        }
    }

    foreach ($req in $nb.Value.conda)
    {
        Conda-Install $req
    }

    # installing widgets
    foreach ($wid in $nb.Value.widgets)
    {
        $output = & jupyter nbextension install --py --sys-prefix $wid 2>&1
        Write-Host $output
        $output = & jupyter nbextension enable --py --sys-prefix $wid 2>&1
        Write-Host $output
    }

    & python -m ipykernel install --name=python36 --sys-prefix --display-name="Python 3.6"

    Write-Host "Notebook environment packages"
    & pip list -v --disable-pip-version-check

    Write-Host "Resource group name: " $rg
    $configfullname = [io.path]::combine($workdir, $nb.Name, ".azureml", "config.json")
    Create-Config $configfullname $subscription $rg $workspace

    Write-Host "Running notebook: " $nbfullname

    $nbjson = Get-Target $nbfullname
    $nbowner = $nbjson.metadata.authors.name

    # handling custom timeout
    if ($nb.Value.celltimeout)
    {
        $timeout=$nb.Value.celltimeout
    }
    else
    {
        $timeout=$defaultTimeout
    }

    Write-Host "Cell timeout set to " $timeout

    if ($nb.Value.preexec)
    {
        $prefile = [io.path]::combine($workdir, $nb.Name, $nb.Value.preexec)
        Write-Host "Executing" $nb.Value.preexec
        if ($prefile.endswith(".py"))
        {
            $_output = & python $prefile 2>&1
            $fileoutput = $prefile + ".output"
            Out-File -Force -InputObject $_output -FilePath "$fileoutput"
        }
        elseif ($prefile.endswith(".ipynb"))
        {
            $_output = & jupyter nbconvert --execute $prefile --to notebook --ExecutePreprocessor.timeout=$timeout --allow-errors --debug 2>&1
            $fileoutput = $prefile + ".output"
            Out-File -Force -InputObject $_output -FilePath "$fileoutput"
        }
        else
        {
            Write-Host "Have no idea how to execute this..."
        }
    }

    $_NBExecutionTimer =  [system.diagnostics.stopwatch]::StartNew()

    $output = & jupyter nbconvert --execute $nbfullname --to notebook --ExecutePreprocessor.timeout=$timeout --allow-errors --debug 2>&1

    $_ExecTime = $_NBExecutionTimer.Elapsed.TotalSeconds

    $post_output=""
    $post_exitcode=0
    if ($nb.Value.postexec)
    {
        $postfile = [io.path]::combine($workdir, $nb.Name, $nb.Value.postexec)
        Write-Host "Executing" $nb.Value.postexec
        if ($postfile.endswith(".py"))
        {
            $post_output = & python $postfile 2>&1
            $post_exitcode = $LASTEXITCODE
            $fileoutput = $postfile + ".output"
            Out-File -Force -InputObject $post_output -FilePath "$fileoutput"
        }
        elseif ($postfile.endswith(".ipynb"))
        {
            $post_output = & jupyter nbconvert --execute $postfile --to notebook --ExecutePreprocessor.timeout=$timeout --allow-errors --debug 2>&1
            $post_exitcode = $LASTEXITCODE
            $fileoutput = $postfile + ".output"
            Out-File -Force -InputObject $post_output -FilePath "$fileoutput"
        }
        else
        {
            Write-Host "Have no idea how to execute this..."
        }
    }

    $return_object = @{Original=$nbfullname; Name=$nbname; Executed=$nbfullname_new; Config=$configfullname; Output=$output; Duration=$_ExecTime; Owner=$nbowner; ValidationCode=$post_exitcode; ValidationLog=$post_output}

    return $return_object
}

function Update-Notebook-File-With-Timeout($file, $errormessage = "FAILED WITH TIMEOUT")
{
    $lines = Get-Content $file
    $newlines = New-Object System.Collections.ArrayList
    $newlines.AddRange($lines)
    $faildate = Get-Date
    $msg = "{""cell_type"": ""markdown"",""metadata"": {},""source"": [""## <span style='color:red'>$errormessage</span>\n"",""Look execution output in artifacts for the build number from the commit message $faildate""]},"
    $newlines.Insert(2,$msg)

    Out-File -FilePath $file -InputObject $newlines -Encoding ascii

}

function Generate-Test-Result($generatetest, $file, $testcase, $report, $res)
{
    & python $generatetest --file $file --result $res --testcase $testcase
    & python -m pytest $file --junitxml=$report
}

Write-Host "Running in slice " $slice " of " $totalslices

Write-Host "Check if there are secrets to set"
if ($secrets)
{
    Write-Host "There are some.... "
    $_secrets = $secrets -split ';'
    foreach ($var in $_secrets)
    {
        $_pair = $var -split ','
        $varname = $_pair[0]
        $varvalue = $_pair[1]
        Write-Host "Setting value for" $varname
        [Environment]::SetEnvironmentVariable($varname, $varvalue)
    }
}

if ($password)
{
    Write-Host "Logging into" $subscription
    Log-In $subscription $tenant $client $password
}

$loc = Get-Location

if (!(Test-Path $workdir))
{
    $supress = New-Item -ItemType Directory -Path $workdir -Force
}

$scriptpath = Resolve-FullPath (Split-Path -parent $PSCommandPath)
$workdir = Resolve-FullPath ([io.path]::combine($loc, $workdir))
$scenario = Resolve-FullPath ([io.path]::combine($loc, $scenario))
$createenv = Resolve-FullPath ([io.path]::combine($scriptpath, "create_env_gated.ps1"))
$appinsightslogger = Resolve-FullPath ([io.path]::combine($scriptpath, "custom_metrics_to_appinsights.ps1"))
$generatetest = Resolve-FullPath ([io.path]::combine($scriptpath, "pytest_generate_test_result.py"))
$gitpush = Resolve-FullPath ([io.path]::combine($scriptpath, "update_file_on_git.ps1"))
$path = Resolve-FullPath $path

# Make common scripts available to notebook validation scripts
$env:PYTHONPATH = $env:PYTHONPATH + ";" + $scriptpath

$_NBEnvSetupTimer =  [system.diagnostics.stopwatch]::StartNew()
#if (& conda)
#{
#    Write-Host "Using conda from the path"
#    Use-Agent-Conda-Env $baseenv $pyenv $index $sdkpinto
#}
#else
#{
#    Write-Host "Installing conda"
    Prepare-Env $createenv $baseenv $pyenv $index $sdkpinto
#}

Write-Host "Performing ServicePrincipal Login in InteractiveLoginAuthentication"
& python -c "from azureml._base_sdk_common.common import perform_interactive_login; perform_interactive_login(username='$($client)', password='$($password)', service_principal=True, tenant='$($tenant)');"

& $appinsightslogger "Notebook:BaseEnvironment" 0 $_NBEnvSetupTimer.Elapsed.TotalSeconds True True "{'index': '$index', 'pyenv': '$pyenv'}"

$config_raw = Get-Target $scenario
$config_ht = ConvertTo-Hashtable $config_raw
$config_full_ht = Merge-Include $path $config_ht

#uploading all the files listed in uploads - just from the first slice to avoid conflicts from multiple uploads.
if ($token -and $slice -eq 1)
{
    foreach ($__upload_file in $config_full_ht.uploads)
    {
        $__reppath = ($repopath + '/' + [System.IO.Path]::GetDirectoryName($__upload_file).Substring($path.Length).Trim('\').Replace('\','/')).Trim('/')

        Push-To-GitHub $__upload_file $__reppath $gitpush
    }
}

#Hack HT->JSON->CurrentStructure
$config_json = $config_full_ht | ConvertTo-Json -Depth 10
$config = $config_json | ConvertFrom-Json

Write-Host "Scenario: " $config

if ($names)
{
    $_custom = $names -split ','
    $notebooks = $config.notebooks.PSObject.Properties.Where{$_custom -ccontains $_.Value.name}
}
else
{
    if ($channel)
    {
        $_custom = $config.channels.PSObject.Properties[$channel].Value
        $notebooks = $config.notebooks.PSObject.Properties.Where{$_custom -ccontains $_.Name}
    }
    else
    {
        $notebooks = $config.notebooks.PSObject.Properties
    }
}

# Create random resource group if not specified
if (-not $resourcegroup)
{
    Write-Host "Resource group is not provided"

    $rg = Get-Random-RG "aml_nbgit_rg"

    Write-Host "Creating RG " $rg "in location" $location

    & az account set -s $subscription

    $tag = & python -c "import time; print('creationTime=',str(time.time()))"
    & az group create -l $location -n $rg --tags $tag
}
else
{
    $rg = $resourcegroup
}

#setting envvars for rg
[Environment]::SetEnvironmentVariable("RESOURCE_GROUP", $rg)
[Environment]::SetEnvironmentVariable("SUBSCRIPTION_ID", $subscription)
[Environment]::SetEnvironmentVariable("WORKSPACE_NAME", $workspace)
[Environment]::SetEnvironmentVariable("WORKSPACE_REGION", $location)

$report = New-Object System.Collections.ArrayList

#iterate over the notebooks
$i=0
foreach ($nb in $notebooks)
{
    $notinslice  = Not-In-Slice $i $slice $totalslices
    $i = $i + 1
    if ($notinslice)
    {
        Continue
    }

    $NBResult = Execute-Notebook-In-Env $path $workdir $nb $baseenv $subscription $rg $workspace $index $sdkpinto

    $errortrigger = "[NbConvertApp] output: error"
    $newerrortrigger = "[NbConvertApp] msg_type: error"
    $envtrigger = "No such kernel named"
    $timeouttrigger = "[NbConvertApp] ERROR"

    $comment = "Passed:" + $message
    $failedexec = $False
    # Fail notebook if there is an error or timeout

    $lineerror = ""
    $failurereason = "Pass"

    if (Test-Path -Path $NBResult.Executed)
    {
        Copy-Item $NBResult.Executed $NBResult.Original -force
    }
    else
    {
        $comment = "Not executed:" + $message
        $failedexec = $True
        $failurereason = "Noexec"
    }


    $notebookoutput = $NBResult.Original + ".output"
    Out-File -Force -InputObject $NBResult.Output -FilePath $notebookoutput

    foreach ($line in $NBResult.Output)
    {
        if ($line.ToString().Contains($errortrigger) -or $line.ToString().Contains($newerrortrigger))
        {
            Write-Host "Execution failed"
            $comment = "Failed:" + $message
	        $Exception = $nb.Value.name + ": notebook execution failed. Commit message: " + $comment
	        $report.Add($Exception)
	        Write-Error $Exception
            $failedexec = $True
            $failurereason = "Error"
            Break
        }
        if ($line.ToString().Contains($envtrigger))
        {
            Write-Host "Execution failed"
            $comment = "Failed:" + $message
	        $Exception = $nb.Value.name + ": notebook execution environment failure. Commit message: " + $comment
	        $report.Add($Exception)
	        Write-Error $Exception
            $errormessage = "ENVIRONMENT FAILURE NO KERNEL FOUND " + (Get-Date).ToString()
            Update-Notebook-File-With-Timeout $NBResult.Original $errormessage
            $failedexec = $True
            $failurereason = "Invalid Environment"
            Break
        }
        if ($line.ToString().Contains($timeouttrigger))
        {
            Write-Host "Execution timed out"
            $comment = "Timeout:" + $message
	        $Exception = $nb.Value.name + ": notebook execution timed out. Commit message: " + $comment
	        $report.Add($Exception)
	        Write-Error $Exception
            $errormessage = "FAILED WITH TIMEOUT " + (Get-Date).ToString()
            Update-Notebook-File-With-Timeout $NBResult.Original $errormessage
            $failedexec = $True
            $failurereason = "Timeout"
            Break
        }
    }

    $nbowner = $NBResult.Owner
    $_name = "NotebookSample:" + $NBResult.Name

    $_sourceline = ""

    if ($failedexec)
    {
        $_nbjson = Get-Target $NBResult.Original
        $_nbhash = ConvertTo-Hashtable $_nbjson

        foreach ($c in $_nbhash.cells)
        {
            $trb = $c.outputs.traceback
            if ($trb -and ![system.string]::IsNullOrWhiteSpace($trb))
            {
                $lineerror = $trb -replace '(\x9B|\x1B\[)[0-?]*[ -/]*[@-~]',''
                $_sourceline = $c.source
                break
            }
        }
    }
    # if notebook status is OK check validation script
    elseif ($NBResult.ValidationCode -ne 0)
    {
        $failedexec = $True
        $lineerror = $NBResult.ValidationLog
        $failurereason = "Post-Validation"
        $Exception = $nb.Value.name + ": notebook validation failed: " + $NBResult.ValidationLog
        $report.Add($Exception)
        Write-Error $Exception
    }

    $lineerror = [System.Web.HttpUtility]::UrlEncode($lineerror)
    $_sourceline = [System.Web.HttpUtility]::UrlEncode($_sourceline)
    $_nborig = $NBResult.Original

    & $appinsightslogger $_name 0 $NBResult.Duration (!$failedexec).ToString() (!$failedexec).ToString() "{'region': '$location', 'subscription': '$subscription', 'message': '$comment', 'index': '$index', 'pyenv': '$pyenv', 'owner': '$nbowner', 'status': '$failurereason', 'trace': '$lineerror', 'source': '$_sourceline', 'channel': '$channel', 'filename': '$_nborig'}"

    if ($runastests)
    {
        $fname = [System.IO.Path]::GetFileName($NBResult.Original)
        $dirname = [System.IO.Path]::GetDirectoryName($NBResult.Original)
        $reportfile = [System.IO.Path]::Combine($dirname, "Test-" + $fname + ".xml")
        $testcase = "test_" + $fname.Replace('-',"_").Replace('.',"_")
        $file = [System.IO.Path]::Combine($dirname, $testcase + ".py")
        if ($failedexec)
        {
            $res = "failed"
        }
        else
        {
            $res = "ok"
        }
        Generate-Test-Result $generatetest $file $testcase $reportfile $res
    }

    $updatedrepopath = $repopath
    if ($nb.Value.path)
    {
        $updatedrepopath = $updatedrepopath + "/" + $nb.Value.path
    }

    # Push notebooks and dependencies to GitHub if token specified
    if ($token)
    {
        & $gitpush $NBResult.Original $owner $project $updatedrepopath $branch $comment $token

        $depBaseFolderPath = [System.IO.Path]::GetDirectoryName($NBResult.Original)

        foreach ($dep in $nb.Value.dependencies)
        {
            $depfullname = [io.path]::combine($depBaseFolderPath, $dep)

            Push-To-GitHub $depfullname $updatedrepopath $gitpush
        }
    }

    deactivate
}

deactivate

# deleting resource group if created by script
if (-not $resourcegroup)
{
    Write-Host "Deleting resource group " $rg
    & az group delete --yes --no-wait --name $rg
}

$reportfile = [io.path]::combine($workdir, "execution_report$slice.txt")
Out-File -Force -InputObject $report -FilePath $reportfile

# Push report to GitHub
if ($token)
{
    & $gitpush $reportfile $owner $project $repopath $branch $message $token
}

Set-Location $loc
