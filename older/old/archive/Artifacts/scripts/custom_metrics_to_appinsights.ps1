Param(
[string]$test_name,
[string]$start_time,
[string]$duration,
[string]$outcome='True',
[string]$is_success='True',
[string]$metrics_dict='{}'
)

$loc = Get-Location
$path_to_apinsights_framework = [io.path]::Combine("$PSCommandPath","..","..","tests","scenarios")
$suppress = Set-Location -Path $path_to_apinsights_framework 2>&1

$codestring = [string]::Format("from {0} import {1}; {1}('{2}',{3},{4},{5},{6},None,None,{7})",
                               "utilities.helpers.app_insights_helpers",
                               "log_test_results_from_python_unit_test",
                               $test_name,$start_time,$duration,$outcome,$is_success,$metrics_dict)

Write-Host "Executing: "$codestring
$suppress = & python -c $codestring 2>&1

Write-Host $suppress

Set-Location -Path $loc