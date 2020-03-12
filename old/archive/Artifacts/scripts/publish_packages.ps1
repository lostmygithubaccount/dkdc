param(
[string]$config,
[string]$source,
[string]$channel = "test"
)

if ($global:__indent__ -eq $null)
{
    $global:__indent__=0
}

function Write-Host
{
    Microsoft.PowerShell.Utility\Write-Host (' ' * $global:__indent__) -NoNewline
    & 'Microsoft.PowerShell.Utility\Write-Host' $args
}

function Indent
{
    $global:__indent__+=4
}

function UnIndent
{
    $global:__indent__ -= 4
    if ($global:__indent__ -lt 0)
    {
        $global:__indent__ = 0
    }
}

function Get-Target($config)
{
    Get-Content -Raw -Path $config | ConvertFrom-Json
}

function Upload-Package($storage, $source, $package)
{
    Indent
    $package = $package -replace "-", '_'
    $__file = Get-ChildItem -Path $source -Filter "$package*.whl" | Select-Object -First 1

	Write-Host $__file
    $__blob = [string]::Concat($storage.prefix, $__file)

    $__text = Get-Content "$source\$__file" -Raw -Encoding Byte
    $__md5 = New-Object -TypeName System.Security.Cryptography.MD5CryptoServiceProvider

    $__hash = [System.Convert]::ToBase64String($__md5.ComputeHash($__text))

    $__existingblod = Get-AzureStorageBlob -Container $storage.container -Blob $__blob -ErrorAction SilentlyContinue
    $__hashblob =  $__existingblod.ICloudBlob.Properties.ContentMD5

    Write-Host "Comparing hash $__hash  -=vs=-  $__hashblob"
    if ($__hash -eq $__hashblob)
    {
        Write-Host "...skipping because of the same contentmd5"
    }
    else
    {
        $supress = Set-AzureStorageBlobContent -Container $storage.container -File "$source\$__file" -Blob $__blob -Force
    }
    UnIndent
}

Write-Host $([string]::Format("Selected target: {0}", $config))
$__config = Get-Target $config

$_release = $__config.releases.PSObject.Properties[$channel].Value

$__storage = $__config.targets.PSObject.Properties[$_release.package_repo].Value

if ($__storage.type -eq "arm")
{
    $supress = Set-AzureSubscription -SubscriptionName $__storage.subscription -ErrorAction SilentlyContinue
    $supress = Set-AzureRmCurrentStorageAccount -Name $__storage.account -ResourceGroupName $__storage.resource
}
else
{
    $supress = Set-AzureSubscription -CurrentStorageAccountName $__storage.account -SubscriptionName $__storage.subscription 
}

Write-Host $([string]::Format("Uploading packages into '{2}' container with prefix {3} in storage '{0}' in '{1}' subscription", $__storage.account, $__storage.subscription, $__storage.container, $__storage.prefix))

foreach ($package in $_release.packages)
{
    Write-Host $([string]::Format("Uploading package: {0}", $package))
    $supress = Upload-Package $__storage $source $package
}

$__storage = $__config.targets.PSObject.Properties[$_release.extensions_repo].Value

if ($__storage.type -eq "arm")
{
    $supress = Set-AzureSubscription -SubscriptionName $__storage.subscription -ErrorAction SilentlyContinue
    $supress = Set-AzureRmCurrentStorageAccount -Name $__storage.account -ResourceGroupName $__storage.resource
}
else
{
    $supress = Set-AzureSubscription -CurrentStorageAccountName $__storage.account -SubscriptionName $__storage.subscription 
}

Write-Host $([string]::Format("Uploading extensions into '{2}' container with prefix {3} in storage '{0}' in '{1}' subscription", $__storage.account, $__storage.subscription, $__storage.container, $__storage.prefix))

foreach ($extension in $_release.extensions)
{
    Write-Host $([string]::Format("Uploading extension: {0}", $extension))
    $supress = Upload-Package $__storage $source $extension
}

return 0
