param(
[string]$index
)
$indexfile = "src/azureml-core/azureml/_project/index_location.txt"

$index | Out-File -FilePath $indexfile -Encoding ASCII
