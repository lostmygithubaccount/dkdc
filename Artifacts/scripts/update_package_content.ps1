param(
[string]$zipfile,
[string]$targetfile,
[string]$content
)

Add-Type -assembly  System.IO.Compression.FileSystem

$zip = [System.IO.Compression.ZipFile]::Open($zipfile,"Update")
$file = $zip.Entries.Where({$_.name -eq $targetfile})

$handler = [System.IO.StreamWriter]($file).Open()
$handler.BaseStream.SetLength(0)
$handler.Write($content)
$handler.Flush()
$handler.Close()

$zip.Dispose()

Write-Host "Double check content"

$zip = [System.IO.Compression.ZipFile]::Open($zipfile,"Update")
$file = $zip.Entries.Where({$_.name -eq $targetfile})

$handler = [System.IO.StreamReader]($file).Open()
$text = $handler.ReadToEnd()

$handler.Close()
$zip.Dispose()

Write-Host "Content: " $text

if ($text -ne $content)
{
    Write-Error "Not expected content"
}
