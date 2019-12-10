# Unilever MLOps Questions

## 1. How is the ML Service integration done with Azure Dev Ops

The Azure ML Service (AML, MLS) is integrated with Azure DevOps through the [Machine Learning extension for Azure DevOps](https://marketplace.visualstudio.com/items?itemName=ms-air-aiagility.vss-services-azureml). This allows scheduling pipelines, triggering deployments, or retraining a model easily using standard DevOps best practices. 

Details and examples can be found at [aka.ms/mlops](https://aka.ms/MLOps). 

### A) For component creation with pre-defined compute

Component creation with pre-defined compute can be handled by the [Azure ML CLI](https://docs.microsoft.com/en-us/azure/machine-learning/service/reference-azure-machine-learning-cli), an extension to the Azure CLI for working with the ML service. In the MLOps repo, you can find [examples](https://github.com/microsoft/MLOps/tree/master/infra-as-code) of creating a workspace, vnet, and default compute which can be customized for your situation. 

### B) Access management

need more context

### C) Code/model check-in

Yes.

### D) Model deployment to higher environments

Yes.

## 2. Do we need one workspace or multiple as we follow for databricks

Depends.

## 3. How does the access control managed in one workspace, considering development and devops is managed by different team and developers do not get access in production environment to change the models or code 

## 4. How do we make sure compute is pre-defined while providing the environment and data science users are only allowed to scale up or down

RBAC. 

## 5. How to make sure compute (VMs) are domain joined?

See the [examples](https://github.com/microsoft/MLOps/tree/master/infra-as-code). 

## 6. What would be the interim approach as custom roles to control the access is not available.

Two workspaces - dev and prod. Data scientsts/others have access to the sandbox, while only some individuals have access to the prod workspace. Either by manual communication, with tags, or otherwise assets from the dev workspace can be copied to the prod workspace and deployed when ready.  
