Param(
    [string]$sdkVersion
)

# Download specific version if it was passed in, otherwise download newest
if (-not $sdkVersion)
{
    Write-Output "Installing SDK without specific version"
    pip install azureml-sdk[notebooks,automl]
}
else
{
    Write-Output "Installing SDK using $sdkVersion"
    pip install azureml-sdk[notebooks,automl]==$sdkVersion
}