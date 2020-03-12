param(
# set to true to see more messages from the script
[bool]$debug = $True,
# build identifier
[string]$buildid = $Env:BUILD_BUILDID,
# Default Auth header to access REST API is for build agents. To run on build agent, once the pipeline task is added, 
# click on "Run on agent" and expand "Additional options" so you can check "Allow scripts to access OAuth token". To test
# locally you need to create a Personal Access Token and use the below example code.
# See https://docs.microsoft.com/en-us/azure/devops/integrate/get-started/authentication/pats
# > $user = <YOUR DOMAIN\USERNAME>
# > $accesstoken = <YOUR PAT>
# > $authHeader = "Basic {0}" -f [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes(("{0}:{1}" -f $user,$accessToken)))
[string]$authHeader = "Bearer $Env:SYSTEM_ACCESSTOKEN",
# TFS Endpoint for Azure DevOps REST API requests
[string]$tfsEndpoint = $env:SYSTEM_TEAMFOUNDATIONCOLLECTIONURI + $env:SYSTEM_TEAMPROJECT
)

function Get-Changed-Files($debug, $buildid, $authHeader, $tfsEndpoint)
{
    # Define empty list to return changed items
    $changes = @()

    # Build URI to query Azure DevOps REST API for the given build id
    $request = '{0}/_apis/build/builds/{1}' -f $tfsEndpoint,$buildid
    if ($debug)
    {
        Write-Host ("Querying Azure DevOps for build id {0}: {1}" -f $buildid,$request)
    }

    # Use auth header to access REST API
    # See https://docs.microsoft.com/en-us/azure/devops/pipelines/scripts/powershell?view=vsts#use-the-oauth-token-to-access-the-rest-api
    $build = Invoke-RestMethod -Uri $request -Headers @{ Authorization = $authHeader }

    if ($null -eq $build -or $build.GetType().Name -ne "PSCustomObject")
    {    
        Write-Error ("Failed to retrieve build id {0} from {1}" -f $buildid,$request)
        return $changes
    }

    if ($build.reason -eq "pullRequest")
    {
        # Build URI to query Azure DevOps REST API for iterations in the pull request that triggered this build
        $request = '{0}/_apis/git/repositories/{1}/pullRequests/{2}/iterations' -f $tfsEndpoint,$build.repository.id,$build.triggerinfo."pr.number"
        if ($debug)
        {
            Write-Host ("Querying Azure DevOps for iterations in pull request {0}: {1}" -f $build.triggerinfo."pr.number",$request)
        }

        # Query Azure DevOps REST API for iterations in the pull request that triggered this build
        $iterations = Invoke-RestMethod -Uri $request -Headers @{ Authorization = $authHeader }
        if ($debug)
        {
            Write-Host ("Retrieved {0} iterations: {1}" -f $iterations.count, $iterations)
        }
        if ($iterations.count -le 0) { return $changes }

        # Build URI to query Azure DevOps REST API for changes in the last pull request iteration
        $request = '{0}/_apis/git/repositories/{1}/pullRequests/{2}/iterations/{3}/changes' -f $tfsEndpoint,$build.repository.id,$build.triggerinfo."pr.number",$iterations.count
        if ($debug)
        {
            Write-Host ("Querying Azure DevOps for changes in the last pull request iteration {0}: {1}" -f $iterations.count,$request)
        }

        # Query Azure DevOps REST API for pull request files
        $pullRequestFiles = Invoke-RestMethod -Uri $request -Headers @{ Authorization = $authHeader }
        if ($debug)
        {
            Write-Host ("Retrieved {0} change entries: {1}" -f $pullRequestFiles.changeEntries.Count, $pullRequestFiles)
        }

        # append changed items to list of changes
        foreach ($changeEntry in $pullRequestFiles.changeEntries)
        {
            $changes += $changeEntry
            if ($debug)
            {
                Write-Host ("Appended item to list of changes: {0}" -f $changeEntry.item.path)
            }
        }
    }
    else
    {
        # Build URI to query Azure DevOps REST API for commits in the given build id
        $request = '{0}/_apis/build/builds/{1}/changes' -f $tfsEndpoint,$buildid
        if ($debug)
        {
            Write-Host ("Querying Azure DevOps for commits in build id {0}: {1}" -f $buildid,$request)
        }

        # Query Azure DevOps REST API for commits in the given build id
        $commits = Invoke-RestMethod -Uri $request -Headers @{ Authorization = $authHeader }
        if ($debug)
        {
            Write-Host ("Retrieved {0} commits: {1}" -f $commits.count, $commits)
        }

        # For each commit, query items that were changed
        foreach ($commit in $commits.value)
        {
            if ($debug)
            {
                Write-Host ("Querying Azure DevOps for changed items in commit id {0}: {1}" -f $commit.id, $commit.location + "/changes")
            }

            # Query items in each commit from REST API. See https://docs.microsoft.com/en-us/rest/api/azure/devops/git/commits/get changes
            $changedItems = Invoke-RestMethod -Uri ($commit.location + "/changes") -Headers @{ Authorization = $authHeader }

            # append changed items to list of changes
            $changedFiles = $changedItems.changes | Where-Object { !$_.item.isFolder }
            $changePaths = @()
            foreach ($changedFile in $changedFiles)
            {
                # check for duplicates as manual builds may contain multiple changes for the same item
                $index = $changePaths.IndexOf($changeEntry.item.path)
    
                # if this is a duplicate, we should keep the most recent change
                if ($index -ge 0)
                {
                    $changes.Item($index) = $changedFile
                    if ($debug)
                    {
                        Write-Host ("Updated item in list of changes with {0}: {1}" -f $changedFile.changeType,$changedFile.item.path)
                    }
                }
                # otherwise, append change to our list
                else
                {
                    $changes += $changedFile
                    $changePaths += $changedFile.item.path   
                    if ($debug)
                    {
                        Write-Host ("Appended item to list of changes: {0}" -f $changedFile.item.path)
                    }
                }
            }
        }
    }

    return $changes
}

return Get-Changed-Files $debug $buildid $authHeader $tfsEndpoint