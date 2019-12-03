from time import time
from azureml.core import Workspace, Dataset

ws = Workspace.from_config()

t1 = time()

dset = Dataset.get_by_name(ws, 'ufcfights')
df = dset.to_pandas_dataframe()

t2 = time()

print(t2 - t1)
