param(
# json file with the test descriptions (release.json)
[string]$scenario,
# names of the tests to run, if empty all the test will be executed
[string]$path,
[bool]$deletetemp = $True,
# File names of notebooks to validate. If null all will be validated
[string[]]$notebooksToValidate,
[bool]$failonpylint = $True
)

$disable="C,E0401,E0611"

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
                     $hashTable.channels.$($chnl.Name) += @($chnl.Value | ForEach-Object {"$key-$_"})
                }
                else
                {
                    $hashTable.channels.$($chnl.Name) = @($chnl.Value | ForEach-Object {"$key-$_"})
                }
            }

        }
    }
    return $hashTable
}

$stylecoperror = $failonpylint
$config_raw = Get-Target $scenario
$config_ht = ConvertTo-Hashtable $config_raw
$root = $path
$config_full_ht = Merge-Include $path $config_ht
$code = 0
$Failed = $False
$issues = New-Object System.Collections.ArrayList

foreach ($n in $config_full_ht.notebooks.GetEnumerator())
{
    # if list of notebooks to validate is specified, skip notebooks not in the list
    if ($notebooksToValidate -and !$notebooksToValidate.Contains($n.value.name)) { continue }
    
    $str = [system.io.path]::Combine($root, $($n.value.path), $($n.value.name))
    $res = Test-Path -Path $str
    Write-Host "Testing" $str
    if (!$res)
    {
        $Failed = $True
        $issue = "FILE DOES NOT EXIST: " + $str
        $issues += $issue
        Write-Host $issue
    }
    else
    {
        #default nbconvert behavior. output parameter doesn't work :(
        $folder = [System.IO.Path]::GetDirectoryName($str)
        $file = [System.IO.Path]::GetFileNameWithoutExtension($str) + ".py"
        $html = [System.IO.Path]::Combine($folder, $file)
        $output = & python $PSScriptRoot\nbconvert_for_pylint.py $str $html 2>&1
        if (Test-Path -Path $html)
        {
            if ($n.value.pylint)
            {
                $_disable = $n.value.pylint
            }
            else
            {
                $_disable = $disable
            }
            pylint --disable=$_disable $html
            $code = $LASTEXITCODE
            Write-Host "$code pylint issues found for $str with pattern --disable=$_disable"
            if ($code -ne 0)
            {
                if ($stylecoperror -eq $True)
                {
                    #$Failed=$True
                    $issue = "PyLint violation: " + $str
                    $issues += $issue
                    Write-Host $issue
                }
            }
            if ($deletetemp -eq $True)
            {
                $suppress = Remove-Item -Path $html -Force
            }
        }
        else
        {
            $Failed = $True
            $issue = "INVALID NOTEBOOK: " + $str
            $issues += $issue
            Write-Host $issue
        }
    }
}

foreach ($chnl in $config_full_ht.channels.GetEnumerator())
{
    foreach ($id in $chnl.value)
    {
        if (!$config_full_ht.notebooks[$id])
        {
            $Failed = $True
            $issue = "ID " + $id + " in channel " + $($chnl.name) + " is invalid"
            $issues += $issue
            Write-Host $issue
        }
    }
}


if ($Failed)
{
    Write-Host "#####################################################################"
    foreach ($issue in $issues)
    {
        [Console]::Out.Flush()
        Write-Host $issue
    }
    Write-Error "Validation Failed"
    Write-Host "#####################################################################"
}
else
{
    $global:LASTEXITCODE = 0
}