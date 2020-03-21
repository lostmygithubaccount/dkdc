# Data 2.0 proposal

A dataset is nothing more than ~10 strings specifying what type of storage the data is, the path/query to get the data, and a few other things.

They should be defined as config files, and easily intefaced with through the Azure ML Python SDK.

Datasets should be used in the data plane, not the control plane:
* "but what if users doesn't want to have Azure ML code in their training script" -> they can figure out how to access the Dataset without an Azure ML Dataset - this is possible and something they would have to do anyway
* the value prop of the Azure ML SDK is it makes accessing your assets easy
* end users (data scientists) should generally only be interfacing with datasets by name 

## A dataset

A dataset is a .yaml file containing the strings specifying the dataset. It is a physical object which can be CI/CD'ed, passed around various storage location, etc. 

Example one:

```yaml
name: my_data
type: AzureDataLakeGen2
storage_account: 'mystorage'
subscription_id: '9feiaejia;fejiawef'
resource_group: 'myrg'
region: 'westus'
paths:
  path1: 'mydata/thisfolder/*'
  path2: 'mydata/thatfolder/year=2020/*.csv'
```

How does a user access this dataset? Through the Python SDK, more similar to Environments or Models than Datasets:

```python
# let's assume the above is a local yaml files called 'data.yaml'

from azureml.core import Dataset

dset = Dataset.from_yaml('data.yml')

print(dset.name)
print(dset.type)
print(dset.storage_account)
print(dset.subscription_id)
print(dset.region)
# etc

# change something
dset.name = 'new_name'
dset.region = 'eastus' # I have a copy of the data here, the same dataset should work otherwise

# write out new config files
dset.write_config('local_path')

# validate the dataset (see Environment.build(ws))
dset.validate(ws) # returns True if the storage location exists and you have access

# register the dataset - this simply puts the config in AzureML-managed storage location
dset.register(ws) # throw error if naming conflict 
```

To pass between pipelines, simply pass around the YAML file between steps. This can be hidden from the user, who simply passes around the Dataset object or string (name) of the dataset. 
