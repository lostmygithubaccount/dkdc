# Imports
################################################################################ 
################################################################################ 
import os
from azureml.core import Workspace

# Parameters
################################################################################ 
################################################################################ 
subscription_id = '6560575d-fa06-4e7d-95fb-f962e74efd7a'
workspace_name  = 'AzureML'
locations       = ['eastus', 
                   'eastus2', 
                   'westus', 
                   'westus2', 
                   'westeurope', 
                   'uksouth', 
                   'southcentralus', 
                   'northcentralus', 
                   'eastuseuap']

# Functions
################################################################################ 
################################################################################ 
def setup_workspaces():
    for location in locations:

        resource_group = f'cody-{location}-rg'

        ws = Workspace.create(workspace_name, 
                 subscription_id = subscription_id, 
                 resource_group  = resource_group,
                 location        = location,
                 )

        ws.write_config(file_name = f'{location}.json')

        cmd = f'az network vnet create '            + \
              f'--name wifi '                       + \
              f'--resource-group {resource_group} ' + \
              f'--subnet-name 5GHz'

        os.system(cmd)

# Run
################################################################################ 
################################################################################ 
if __name__ == '__main__':
    setup_workspaces()
