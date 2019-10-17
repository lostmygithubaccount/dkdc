param(
# full path to the file "C:\Folder\myfile.txt"
[string]$filename,
# repo owner "Azure"
[string]$owner = "Azure",
# project "ViennaDocs"
[string]$project = "ViennaDocs",
# "path/to/my/file/in/repo" 
[string]$path = "PrivatePreview/notebooks",
# branch "master"
[string]$branch = "test",
# "commit message"
[string]$message = "update",
# authorization token
[string]$token
)

function Get-Sha($project, $path, $name, $branch, $token)
{
    $Headers = @{
        Authorization = "bearer $Token"
    }

    Try
    {
        Write-Host "Checking if file already exist"

        # Find the sha from the folder rather than reading the file content because
        # reading the content doesn't work for files over 1Mb.

        $Uri = "https://api.github.com/repos/$owner/$project/git/trees/${branch}:$path"
        $rawresponse = Invoke-WebRequest -Uri $Uri -Headers $Headers -ErrorVariable $err
        Write-Host "Folder found"

        $response = $rawresponse.Content | ConvertFrom-Json

        $sha = $response.tree | where { $_.path -eq $name } | Select -ExpandProperty sha

        return $sha
    }
    Catch
    {
        Write-Host $_
        Write-Host $err
        Write-Host "Nope, it does not"
        return $null
    }    
}

function Upload-File($fullpath,$user,$project, $path, $branch, $message, $token)
{
  
    $name = Split-Path $fullpath -Leaf
    Write-Host "Uploading $fullpath into $path/$name"

    $Uri = "https://api.github.com/repos/$owner/$project/contents/$path/$name"

    $content = [Convert]::ToBase64String([IO.File]::ReadAllBytes($fullpath.Replace('/','\')))

    $Headers = @{
        Authorization = "bearer $token"
        }

    $retryCount = 0
    $success = $false

    do
    {
       $Body = @{
            "message" = $message 
            "content" = $content  
            "branch" = $branch   
       }
 
       try
       {
          $exist = Get-Sha $project $path $name $branch $token

          if ($exist -ne $null)
          {
              Write-Host "File will be overwritten"
              $Body.Add("sha", $exist)
          }

         $JsonBody = $Body | ConvertTo-Json
         Write-Host "Uploading to github"
         $rawresponse = Invoke-WebRequest -Headers $Headers -Body $JsonBody -Method Put -Uri $Uri -Verbose
     
         Write-Host ("Here is the response: " + $rawresponse)

         $success = $true
      }
      catch
      {
          Write-Host "Upload failed: $_"
          $retryCount++
          Start-sleep -Seconds 1
      }

    } until ($retryCount -eq 3 -or $success)

    if (-not $success)
    {
        Write-Error "Failed to upload $fullpath to GitHub"
    }
}

[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

Upload-File $filename $owner $project $path $branch $message $token

