import os
from azureml.core import Workspace

os.mkdir('ml_configs')

subscription_id = '6560575d-fa06-4e7d-95fb-f962e74efd7a'
workspace_name  = 'AzureML'
resource_group  = 'cody-azureml-rg'

locations = ['eastus', 'eastus2', 'westus', 'westus2', 'westeurope', 'uksouth', 'southcentralus', 'northcentralus', 'eastuseuap']

for location in locations:

    ws = Workspace.create(workspace_name, 
             subscription_id = subscription_id, 
             resource_group  = resource_group,
             location        = location,
             )

    ws.write_config(path = '', file_name = f'{location}.json')
