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
```

Open questions:

* exact arguments (aml objects vs strings)

Links:

* [Dask cloud deployments](https://docs.dask.org/en/latest/setup/cloud.html)
* [Github repo](https://github.com/dask/dask-cloudprovider) 
* [ECS thread](https://gist.github.com/jacobtomlinson/ee5ba79228e42bcc9975faf0179c3d1a)

