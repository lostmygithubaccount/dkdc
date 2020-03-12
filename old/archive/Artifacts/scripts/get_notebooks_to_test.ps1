param(
# set to true to see more messages from the script
[bool]$debug = $True,
# AppInsights App ID, default value is for 'vienna-scenario-tests' App
[string]$appInsightsAppId = "9f18dbf9-bc01-4007-aab0-9e7c3d0de9b3",
# AppInsights API Key
[string]$appInsightsApiKey,
# path to the folder with the notebook files
[string]$pathToNotebooks = ".\notebooks\",
# predefined set of customer example notebooks
[string]$channel = "preview",
# List of added notebooks for which to determine required testing
[string[]]$addedNotebooks,
# List of edited notebooks for which to determine required testing
[string[]]$editedNotebooks,
# Number indicating the maximum number of times automation should execute the notebook in a 24 hour period
[int]$throttlingLimit = 12,
# Number from 0 to 100 indicating percentage of recent tests that need to pass for a notebook to be evaluated
[int]$requiredReliability = 100,
# AppInsights query to determine customer example notebook test history
$appInsightsQuery = @"
let three_day = ago(3d);
let one_day = ago(1d);
requests
| where timestamp >= three_day
| where name startswith "NotebookSample:" 
| where customDimensions.environment == "BUILD"
| where customDimensions.build_info_definition_name=="Notebooks-MasterIndex-PROD"
| where customDimensions.region == "eastus2"
| summarize preview=toboolean(max(iif(timestamp > ago(4h),1,0))), success_three_day=countif(customDimensions.status=="Pass" and timestamp >= three_day), total_three_day=countif(timestamp >= three_day), total_one_day=countif(timestamp >= one_day), percentiles(duration, 95) by name
| project notebook=extract("NotebookSample:(.*)", 1, name), preview, percentile_duration_95=format_timespan(totimespan(percentile_duration_95*10000), 'h:m:s.ffff'), success_three_day, total_three_day, total_one_day
| where preview == true
| sort by notebook asc
"@
)

function Get-Configured-Notebooks-In-Channel($folder,$channel)
{
	$notebooksInChannel = @()
	$channelsToVerify = $channel.Split(',')

	# iterate over release.json configuration files in the notebooks folder
	$configFiles = Get-ChildItem -Path $folder -Recurse release.json
	foreach($configFile in $configFiles)
	{
		# convert each file to json
		$json = Get-Content -Raw -Path $configFile.FullName | ConvertFrom-Json
		# iterate over all entries in the notebooks section
		$notes = Get-Member -Type NoteProperty -InputObject $json.notebooks
		foreach($note in $notes)
		{
			foreach($channelToVerify in $channelsToVerify)
			{
				# if an entry is contained in the specified channel add entry value to list
				if($null -ne $json.channels.$channelToVerify -and $json.channels.$channelToVerify.Contains($note.Name))
				{
					$notebooksInChannel += $json.notebooks."$($note.Name)".name
					break
				}
			}
		}
	}
	return $notebooksInChannel
}

function Get-Added-Notebooks-To-Test($debug,$addedNotebooks,$notebooksInChannel)
{
    $notebooksToTest = @()

    # Iterate over list of added notebooks in order to identify which need to be tested
	foreach ($notebook in $addedNotebooks)
	{
		# if this is an added customer example notebook it requires testing
		$isCustomerExampleNotebook = $notebooksInChannel.Contains($notebook)
		if ($debug)
		{
				Write-Host ("Added notebook {0} is customer example notebook: {1}" -f $notebook,$isCustomerExampleNotebook)
		}
        if ($isCustomerExampleNotebook)
        {
            $notebooksToTest += $notebook
        }
    }
	return $notebooksToTest
}

function Invoke-AppInsights-Query($debug,$appInsightsAppId,$appInsightsApiKey,$appInsightsQuery)
{
	# Create URI to call AppInsights REST API
	# See: https://dev.applicationinsights.io/documentation/Overview/URL-formats
	$encodedQuery = [uri]::EscapeDataString($appInsightsQuery)
	$request = "https://api.applicationinsights.io/v1/apps/{0}/query?query={1}" -f $appInsightsAppId,$encodedQuery
	if ($debug)
	{
		Write-Host ("Querying AppInsights REST API: {0}" -f $request)
	}

	# Query AppInsights REST API using API Key authentication
	# See: https://dev.applicationinsights.io/documentation/Authorization/API-key-authentication
	$response = Invoke-RestMethod -Uri $request -Headers @{ "Content-Type" = "application/json; charset=utf-8"; "X-Api-Key" = $appInsightsApiKey}
	if ($debug)
	{
		Write-Host ("Response from AppInsights REST API: {0}" -f $response)
	}

	# If a valid query result wasn't received return null
	if ($response -and $response.tables.Count -le 0)
	{
		Write-Error "No PrimaryResult table in AppInsights response"
		return $null
	}

	return $response
}

function Get-Edited-Notebooks-To-Test($debug,$editedNotebooks,$notebooksInChannel,$throttlingLimit,$requiredReliability,$appInsightsResponse)
{
	$notebooksToTest = @()

	# if customer example notebooks weren't parsed from release.json files return empty list
	if ($notebooksInChannel.Count -le 0)
	{
		Write-Error "Customer example notebooks weren't parsed from release.json files"
		return $notebooksToTest
	}

	# If we have AppInsights response, parse list of customer example notebook results
	$customerExampleNotebooks = @()
	if ($appInsightsResponse)
	{
		if ($debug)
		{
			Write-Host ("Started parsing AppInsights test results...") -NoNewline
		}
		foreach ($row in $appInsightsResponse.tables[0].rows)
		{
			if ($debug)
			{
				Write-Host ("{0} " -f $row[0]) -NoNewline
			}
			$customerExampleNotebooks += $row[0]
		}
		if ($debug)
		{
			Write-Host ("...finished parsing AppInsights test results.")
		}
	}

	# Iterate over list of edited notebooks in order to identify which need to be tested
	foreach ($notebook in $editedNotebooks)
	{
		# if this isn't an existing customer example notebook it doesn't require testing
		$isCustomerExampleNotebook = $notebooksInChannel.Contains($notebook)
		if ($debug)
		{
				Write-Host ("Edited notebook {0} is customer example notebook: {1}" -f $notebook,$isCustomerExampleNotebook)
		}
		if (!$isCustomerExampleNotebook) { continue }

		# Identify row in AppInsights response corresponding to the current notebook
		$index = $customerExampleNotebooks.IndexOf($notebook)

		# if there are test results for this notebook
		if ($index -ge 0)
		{
			$customerExampleNotebookData = $appInsightsResponse.tables[0].rows[$index]

			# if the notebook hasn't been passing reliably enough we shouldn't gate on testing
			$recentTestReliability = (100 * $customerExampleNotebookData[3]) / $customerExampleNotebookData[4]
			if ($debug)
			{
				Write-Host ("Recent test reliability for notebook {0} is {1}%. Skipping: {2}" -f $notebook,$recentTestReliability,($recentTestReliability -lt $requiredReliability))
			}
			if ($recentTestReliability -lt $requiredReliability) { continue }

			# to avoid exhausting resources do not execute notebooks more than a dozen times in a 24 hour period
			$exceedsThrottlingLimit = $customerExampleNotebookData[5] -ge $throttlingLimit
			if ($debug)
			{
				Write-Host ("The {0} recent executions of notebook {1} exceed throttling limit of {2}: {3}" -f $customerExampleNotebookData[5],$notebook,$throttlingLimit,$exceedsThrottlingLimit)
			}
			if ($exceedsThrottlingLimit) { continue }
		}

		# add notebook to list of notebooks to test
		if ($debug)
		{
			Write-Host ("Adding notebook {0} to list of notebooks to test" -f $notebook)
		}
		$notebooksToTest += $notebook
	}
	return $notebooksToTest
}

# Parse release.json files in notebooks folder to identify notebooks in preview channel
$notebooksInChannel = Get-Configured-Notebooks-In-Channel $pathToNotebooks $channel
# Add any added notebook files that are customer examples to list of notebooks to test
$notebooksToTest = Get-Added-Notebooks-To-Test $debug $addedNotebooks $notebooksInChannel
# If there are edited notebooks to process
if ($editedNotebooks.Count -gt 0)
{
	# if we want to limit testing to notebooks with a minimum pass rate
	if ($requiredReliability -gt 0)
	{
		# Query AppInsights for recent customer example notebook test results
		$appInsightsResponse = Invoke-AppInsights-Query $debug $appInsightsAppId $appInsightsApiKey $appInsightsQuery
		# Add edited customer example notebooks with set pass rate to list of notebooks to test provided it hasn't been run too often
		$notebooksToTest = @(Get-Edited-Notebooks-To-Test $debug $editedNotebooks $notebooksInChannel $throttlingLimit $requiredReliability $appInsightsResponse) + $notebooksToTest
	}
	else
	{
		# Add edited customer example notebooks to list of notebooks to test
		$notebooksToTest = @(Get-Edited-Notebooks-To-Test $debug $editedNotebooks $notebooksInChannel) + $notebooksToTest
	}
}
return $notebooksToTest