# Dask on Azure ML Cluster

Dask can be setup on Azure ML clusters to provide distributed Python functionality. Most relevant to Azure ML are the data preparation and visualization capabilities (distributed Pandas, matplotlib) and machine learning (distributed sklearn, xgboost, lightgbm). However, Dask is flexible and can be used to distribute generic Python workloads. 

## Introduction

The Azure Machine Learning service is an enterprise-grade ML platform built for productive data science and ML engineering. Dask "is a flexible library for paralell computing in Python," and importantly for us extends the commonly used open source NumPy, Pandas, and Scikit-Learn interfaces to run at scale. With the power of both, we can easily spin up and tear down a powerful data processing and ML cluster.

In this blog, we will setup an Azure ML cluster with ~1 TB of memory to perform exploratory data analysis (EDA) and data preparation for machine learning using Dask on a ~500 GB dataset. This is not intended to be a guide to Azure ML or Dask and assumes you have an Azure ML workspace setup. If you do not have a workspace, you can [create one for free](https://azure.microsoft.com/pricing/details/machine-learning/). For reference materials, see:

* [Azure ML documentation](https://docs.microsoft.com/azure/machine-learning/)
* [Dask documentation](https://docs.dask/org/latest/)
* [AzureML and Dask Blog Github Repository](https://aka.ms/daskbloggit)

The contents in this blog are adapted from [this github repository](https://github.com/danielsc/azureml-and-dask) by my colleague Daniel.

## Setup

We'll start in the Azure Machine Learning studio by setting up our cluster. Of course, this can be done programmatically with either the [Azure ML Python SDK](https://docs.microsoft.com/python/api/overview/azure/ml/intro?view=azure-ml-py) or [Azure ML CLI](https://docs.microsoft.com/azure/machine-learning/service/reference-azure-machine-learning-cli). 

Head over to the Compute tab on the left side navigation, and create a new Training Cluster. I recommend using the `Standard_DS12_v2` VM or similar. 

![Compute setup](dask_blog_media/pic1.png)

## Connecting to the cluster 
