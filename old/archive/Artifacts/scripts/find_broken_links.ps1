param(
# set to true to see more messages from the script
[bool]$debug = $True,
# List of files to check for broken links
[string[]]$files,
# Regex to identify links in text file
$linkPattern = @"
(http|https)://([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:/~+#-]*[\w@?^=%&/~+#-])?
"@
)

function Get-Markdown-Cells($debug,$filepath)
{
    $markdownCells = @()
    $json = Get-Content -Raw -Path $filepath | ConvertFrom-Json
    foreach($cell in $json.cells)
    {
        if ($cell.cell_type -eq "markdown")
        {
            $markdownCells += $cell.source
        }
    }
    return $markdownCells
}

function Test-Links($debug,$filepath,$inputObject,$linkPattern)
{
    $result = Select-String -AllMatches -InputObject $inputObject -Pattern $linkPattern
    foreach($match in $result.Matches)
    {
        if ($debug)
        {
            Write-Host ("{0} {1}" -f $filepath,$match.Value)
        }
        try
        {
            # By default powershell uses TLS 1.0, some sites require TLS 1.2
            [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
            # Using Get method as Head causes infinite redirects for some aka.ms links
            $output = Invoke-WebRequest -Uri $match.Value -Method Get 2>&1
        }
        catch
        {
            if ($debug)
            {
                Write-Host $output
            }
            Write-Error ("{0} {1} {2}" -f $filepath,$match.Value,$_)
        }
    }
}

foreach($file in $files)
{
    # only examine markdown cells, as code cells may legitimately contain partial links
    $markdownCells = Get-Markdown-Cells $debug $file
    foreach($cell in $markdownCells)
    {
        Test-Links $debug $file $cell $linkPattern
    }
}