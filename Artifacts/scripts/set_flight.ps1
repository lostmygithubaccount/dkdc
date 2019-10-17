param(
[string]$current,
[string]$new
)

$path = "src/azureml-core/azureml/_base_sdk_common/appsettings.json"

$__template = Get-Content -Raw -Path $path
$__config = $__template -replace "$current","$new"
$supress = $__config | Out-File -FilePath $path -Encoding ASCII
