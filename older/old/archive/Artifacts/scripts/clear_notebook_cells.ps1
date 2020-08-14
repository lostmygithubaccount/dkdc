param(
[string]$notebooks = "..\notebooks",
[bool]$throw = $True,
# File names of notebooks to validate. If null all will be validated
[string[]]$notebooksToValidate
)

$issues = New-Object System.Collections.ArrayList

function Get-Target($scenario)
{
    Get-Content -Raw -Path $scenario | ConvertFrom-Json
}

function Check-Author($scenario, $issues)
{
    $data = Get-Target $scenario.FullName

    if (!$data.metadata.authors.name)
    {
        $issues += "Missing author in: $scenario"
    }
    if ($data.metadata.kernelspec.language -ne "sql")
    {
        if ($data.metadata.kernelspec.display_name -ne "Python 3.6")
        {
            $issues += "metadata.kernelspec.display_name should be set to 'Python 3.6' in: $scenario"
        }
        if ($data.metadata.kernelspec.name -ne "python36")
        {
            $issues += "metadata.kernelspec.name should be set to 'python36' in: $scenario"
        }
    }
    $issues
}

function Check-Pixel($scenario, $issues)
{
    $data = Get-Target $scenario.FullName

    # TODO: update with full path
    $pixeldata="![Impressions](https://PixelServer20190423114238.azurewebsites.net/api/impressions/MachineLearningNotebooks"
    if (! $data.cells.source.Where({ $_.StartsWith($pixeldata)}))
    {
        $issues += "Missing pixel data in: $scenario. Please include pixel server url in a first markdown cell in the notebook"
    }
    $issues
}

foreach ($file in (get-childitem $notebooks -Filter "*.ipynb" -Recurse))
{
    # if list of notebooks to validate is specified, skip notebooks not in the list
    if ($notebooksToValidate -and !$notebooksToValidate.Contains($file.Name)) { continue }
    Write-Host "Processing " $file.FullName
    $issues = Check-Author $file $issues
    $issues = Check-Pixel $file $issues
    $size = $file.length
    $suppress = & jupyter nbconvert --ClearOutputPreprocessor.enabled=True --inplace $file.FullName 2>&1
    if ($throw -eq $True -and $size -ne (Get-Item $file.FullName).length) 
    {
        $issues += "Notebook " + $file + " contains output cells. Run (jupyter nbconvert --ClearOutputPreprocessor.enabled=True --inplace $file) locally to clean the notebook"
    }
}

if ($issues.Length -ne 0)
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