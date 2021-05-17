import pandas as pd
import dask.dataframe as dd

from distributed import Client
from adlfs import AzureBlobFileSystem

# setup variables
container_name = "malware"
storage_options = {"account_name": "azuremlexamples"}

# create distributed client
c = Client()

# create Azure filesystem
fs = AzureBlobFileSystem(**storage_options)

# list files 
files = fs.ls(f"{container_name}/processed")

# read in training data
for f in files:
    if "train" in f:
        df = dd.read_parquet(f"az://{f}", storage_options=storage_options)

# advanced feature engineering
cols = [col for col in df.columns if df.dtypes[col] != "object"]

# define system input and output
X = df[cols].drop("HasDetections", axis=1).values.persist()
y = df["HasDetections"].values.persist()

# print something
print(len(X))
print(len(y))

