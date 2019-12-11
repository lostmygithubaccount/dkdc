# Dask Recommendation

Below are dask recommendations.

## Implement dask_cloudprovider.AMLCluster

1 line cluster setup that can be used in dask.distributed.Client. 

```python
from dask_cloudprovider import AMLCluster
from dask.distributed import Client

from azureml.core import Workspace

ws = Workspace.from_config()

cluster = AMLCluster(ws, 'dask-cluster', nodes=12, ...)

cluster.scale(6)  # scale down
cluster.scale(12) # scale up

print(cluster.dashboard_link) # bokeh app link

client = Client(cluster) # start dask client
client.restart()

print(client)
```

Open questions:

* exact arguments (aml objects vs strings)

Links:

* [Dask cloud deployments](https://docs.dask.org/en/latest/setup/cloud.html)
* [Github repo](https://github.com/dask/dask-cloudprovider) 
* [ECS thread](https://gist.github.com/jacobtomlinson/ee5ba79228e42bcc9975faf0179c3d1a)

## Implement Dataset.to_dask_dataframe

Datasets provide easy access to data, taking care of credentials and other annoying tasks. Implementing a to_dask_dataframe() method allows for use of this data with dask.

```python
from azureml.core import Dataset

# file dataset
files = Dataset.get_by_name(ws, 'my-files')

# mount the file dataset
ctx = files.mount('/tmp/mnt/files')
ctx.start()

df = dd.from_csv('/tmp/mnt/files/**.csv')
df = ...

# stop mount
ctx.stop()

# tabular dataset
tabular = Dataset.get_by_name(ws, 'my-tabular')

df = tabular.to_dask_dataframe()
```

Estimate:
* 3-4 dev hours

## Fix ADLFS for Python

Links:

* [ADLFS Dask Github](https://github.com/dask/adlfs)
* [GCFS Dask Github](https://github.com/dask/gcsfs)
* [GCFS Docs](https://gcsfs.readthedocs.io/en/latest/)
* [S3FS Dask Github](https://github.com/dask/s3fs)
* [S3FS Docs](https://s3fs.readthedocs.io/en/latest/)

