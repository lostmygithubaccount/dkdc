param (
#notebooks set aka channel
[string]$notebookset = "preview",
#path to the folder with release.json file
[string]$path = $null,
#path to write generated yml files, if not specified it will be generated next to the notebook file
[string]$output_path = $null,
#python version, default - skipped
[string]$python = $null,
#comma-separated list of conda channels, default - skipped
[string]$condachannels = $null
)

$scriptpath = (Resolve-Path (Split-Path -parent $PSCommandPath)).path
$commonmodulepath = [io.path]::combine($scriptpath, "common_modules.ps1")

. $commonmodulepath

function Create-YAML($config)
{
    $yml = New-Object System.Collections.ArrayList
    $s = $yml.Add("name: " + [System.IO.Path]::GetFileNameWithoutExtension($config.name))
    if ($condachannels)
	{
		$s = $yml.Add("channels:")
		foreach ($ch in $condachannels.split(','))
		{
			$s = $yml.Add("- " + $ch)
		}
	}
	$s = $yml.Add("dependencies:")
	if ($python)
	{
	    $s = $yml.Add("- python=" + $python)
	}
    if ($config.conda)
    {
        foreach ($c in $config.conda)
        {
            $s = $yml.Add("- " + $c)
        }
    }
    $s = $yml.Add("- pip:")
    $s = $yml.Add("  - azureml-sdk")
    if ($config.requirements)
    {
        foreach ($r in $config.requirements)
        {
            $s = $yml.Add("  - " + $r)
        }
    }
    return	$yml
}

if ($path)
{
	$path = Resolve-FullPath $path
}
else
{	
	$path = Resolve-FullPath ([io.path]::combine($scriptpath, "..\notebooks"))
}
$scenario = Resolve-FullPath ([io.path]::combine($scriptpath, $path, "release.json"))

Write-Host $path
Write-Host $scenario
$config_raw = Get-Target $scenario
$config_ht = ConvertTo-Hashtable $config_raw
$config_full_ht = Merge-Include $path $config_ht
$config_json = $config_full_ht | ConvertTo-Json -Depth 10
$config = $config_json | ConvertFrom-Json

$_custom = $config.channels.PSObject.Properties[$notebookset].Value
$notebooks = $config.notebooks.PSObject.Properties.Where{$_custom -ccontains $_.Name}

foreach ($nb in $notebooks)
{
    $yaml = Create-YAML($nb.Value)
	if ($output_path)
	{
		$ymlfile = [io.path]::combine($output_path,[System.IO.Path]::GetFileNameWithoutExtension($nb.Value.name) + ".yml")
	}
	else
	{
		$ymlfile = [io.path]::combine($scriptpath, $path, $nb.Value.path, [System.IO.Path]::GetFileNameWithoutExtension($nb.Value.name) + ".yml")
	}
    Write-Host $ymlfile
    $yaml | out-file -FilePath "$ymlfile" -Encoding ASCII
}