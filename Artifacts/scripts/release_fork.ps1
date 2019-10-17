# Reset a "release"/"target" branch to be the same as a source branch.
# This essentially "snapshots" the source branch into the "release"/"target" branch.
# Can be used to fork master to an intermediate release branch
# or fork the intermediate release branch to a QFE/hotfix branch
# Flow for code in this case is master -> release -> release_qfe
param (
    [Parameter()]
    [ValidateNotNullOrEmpty()]
    [string]$repoUrl=$(throw "repoUrl is required"),
    [switch]$NoVersionTag,
    [string]$releaseBranch=$null,
    [string]$sourceBranch=$null)

if ([string]::IsNullOrEmpty($releaseBranch))
{
    $releaseBranch = $env:RELEASE_BRANCH;
}
if ([string]::IsNullOrEmpty($sourceBranch))
{
    $sourceBranch = $env:SOURCE_BRANCH;
}

if ([string]::IsNullOrEmpty($releaseBranch))
{
    throw "Release branch env variable is not set. Set this to the forked branch name"
}

if ([string]::CompareOrdinal($releaseBranch, "master") -eq 0)
{
    throw "This script will not overwrite master"
}

if ([string]::IsNullOrEmpty($sourceBranch))
{
    $sourceBranch = "origin/master"
    Write-Host "Source branch env variable is empty, using 'origin/master'"
}

# CAUTION don't print $repoUrl as it contains an access token for write access to the repo.
Write-Host "Forking to release branch. Source = $sourceBranch, Release/Target branch = $releaseBranch"

git config --global core.autocrlf false
git config --global push.default simple

Write-Host "Checking out $releaseBranch"
git checkout -q $releaseBranch
Write-Host "Resetting hard against $sourceBranch"
git reset --hard $sourceBranch

# Version tag is pushed before release head is to avoid race condition
# as builds triggered by release branch changes will also try to
# set the version if it is missing (to just a new rev number).
if (!$NoVersionTag)
{
    $tag = "Master-Cut-" + $env:BUILD_BUILDNUMBER
    Write-Host "Tagging branch with tag: $tag"
    git tag $tag
    git push $repoUrl $tag
}

Write-Host "Force pushing to remote repo, not printed due to secrets"
git push --force -q --repo=$repoUrl