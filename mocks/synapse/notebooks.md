# Azure ML Spark Notebooks

Azure ML will enable interactive data preparation and science at scale which leverages Apache Spark. We will enable this through our integration with Azure's flagship data analytics product, Synapse, which owns providing a general Apache Spark compute platform for data processing at scale.

Azure ML will introduce a new Spark compute target, which directly corresponds to an imported Azure ML Synapse Spark Pool. This compute target can be used normally throughout Azure ML. 

For interactive work, data scientists overwhelmingly prefer interactive Python (IPython) notebooks. The most popular choice of notebook editor is Jupyter - the same community has introduced a newer version, JupyterLab.

Orthogonally, the Azure DevDiv team is building new notebook componenets. Both the Azure Synapse and ML teams are integrating this components into their 'integrated notebooks' experience, which is our bet for customers interacting with notebooks long term.

## Scope

We will enable using Azure ML Spark interactively in:
* Azure ML Notebooks
* Jupyter
* JupyterLab

## Technical considerations

Jupyter/Lab are open source tools. There is an open source package for interfacing with Spark called [SparkMagic](https://github.com/jupyter-incubator/sparkmagic). 

The Synapse team is working to provide Jupyter APIs. ETAs:
* dev - 3/23
* prod - 4/15

These dates are not confirmed. The Synapse team's Jupyter APIs will allow us to build Synapse Spark pools directly into our integrated notebooks, providing an experience where the user simply selects a Spark compute target from the notebook's dropdown, selects the "Language" (Kernel), and is now interactively running on the Synapse Spark pool in Azure ML Notebooks. The DevDiv team is providing additional UI components (Spark session configuration, job status, etc) for the Synapse Notebooks which Azure ML Notebooks will simply inheret. 

The DevDiv and Synapse notebooks experiences are rapidly evolving based on customer feedback, so finalized mocks cannot be given.

## Strategy

Azure ML Notebook's long term strategy is to entirely replace Jupyter/Lab for Azure ML users for the vast majority of scenarios. We expect Azure ML Spark notebook users to be familiar with DataBricks or Synapse notebooks, which provide a similar UI for selecting a Spark cluster/pool, starting a Spark session, etc. 

Long term, we expect Azure ML Spark users to largely use Azure ML Notebooks for interactive workloads. Shorter term, we will enable Synapse in both Azure ML Notebooks and Jupyter/Lab as customers are currently more familiar with and already using the latter for interactive data science. 

Still, we will take a split approach:
* enable Synapse Spark through open source options
* enable Azure ML Notebooks to connect to Synapse Spark, offering a best-in-class integrated Spark experience  

Enabling Synapse Spark in open source packages has a few benefits:
* Azure ML contributing to the open source community
* Enabling Synapse Spark to be used in general in Jupyter tooling for data science in general
* timeline considerations due to Private Preview at //build
* lightweight, customizable implementation in user space

Longer term, the plan is to leverage Azure ML Notebooks, DevDiv, and Synapse together:
* Azure ML Notebooks allow selecting an Azure ML Spark compute target in addition to compute instance 
* UI components for Spark session configuration, job status, etc. inhereted from DevDiv componenets
* customize for Azure ML based on customer feedback

## Private Preview - Phase 1

Private Preview is targeted for //build (5/11), which puts technical constaints on the UX - primarily Synapse providing Jupyter APIs. In the short term, we are looking to meet customers at the tools they already use for interactive data preparation, exploration, and science. Compute Instances provide 3 (relevant) options in short term:
* Jupyter
* JupyterLab
* 'inline editing' (integrated notebooks)

For enabling Azure ML Spark in Jupyter/Lab, we will continue the existing POC for enabling Synapse in SparkMagic. We will enhance it specifically for Azure ML to simplify the session start experience. Note that while the same SparkMagic code will work in Azure ML Notebooks, we will focus on providing a more integrated experience through collaboration with DevDiv + Synapse + AzureNotebooks than the self-serve SparkMagic model. 

In a second phase of the private preview, we will enable Azure ML Spark through Azure ML Notebooks with a more integrated experience, largely inherting from Synapse Notebook components. 

### SparkMagic installation

Simply install SparkMagic - this should be pre-installed on a given Compute Instance:

```python
pip install sparkmagic
```

At this point, it is up to users to configure `sparkmagic` to their liking by installing wrapper kernels, additional Jupyter widgets, etc.

### Using Synapse Spark with SparkMagic
**NOTE:** This assumes you have can interactively authenticate with your Synapse Workspace and have a spark pool.

```python
%spark start --synapse workspacename --sparkpool sparky
```

### Using Azure ML Spark with SparkMagic

**NOTE:** This assumes you have linked your Azure ML & Synapse workspaces and have access to a spark pool. 
**NOTE:** No auth should be needed running on a Compute Instance and using the same Azure ML workspace.

```python
%spark start --azureml workspacename --sparktarget sparky # start session
```

### Configure Spark session

```python
%spark config
{
    "driverMemory": "8g",
    "driverCores": 2,
    "executorMemory": "16g",
    "executorCores": 2,
    "numExecturos": 2
}
```

### Stop Spark session

```python
%spark stop
```

### Using Spark session

See SparkMagic documentation.

Run PySpark code:

```python
%%spark

from azureml.core import Workspace, Dataset
ws = Workspace.from_config()

ds = ws.datasets['my-data']
df = ds.to_spark_dataframe()

### data prep

ds2 = Dataset.Tabular.from_spark_dataframe(df)
```

Run SQL code:

```python
%%sql -o tables -q
SHOW TABLES
```

```python
%%sql 
SELECT * FROM mytable
```

## Private Preview - Phase 2

Beyond //build (5/11) we will work to deliver the integrated notebooks experience as soon as possible for Private Preview. This encompasses:
* selecting Azure ML Spark from Notebooks dropdown
* kernel/language selection
* Spark UI inhereted from DevDiv notebook components 

Based on customer feedback, we will customize this UI for data science workloads. In the shorter term, we expect to roughly match the Synapse UI:
* https://www.figma.com/file/UC8n9avTvQMmHZdUVYFuix/Synapse-integration-screens?node-id=1%3A30065

## Public Preview & General Availability

The contribution to SparkMagic enabling usage of Synapse Spark Pools and Azure ML Spark Compute Targets will remain, however we will focus on improving the long term Azure ML Notebooks experience pending customer feedback.
