# Unilever MLOps Questions

## 1. How is the ML Service integration done with Azure Dev Ops

The Azure ML Service (AML, MLS) is integrated with Azure DevOps through the [Machine Learning extension for Azure DevOps](https://marketplace.visualstudio.com/items?itemName=ms-air-aiagility.vss-services-azureml). This allows scheduling pipelines, triggering deployments, or retraining a model easily using standard DevOps best practices. 

Details and examples can be found at [aka.ms/mlops](https://aka.ms/MLOps). 

### A) For component creation with pre-defined compute



### B) Access management

### C) Code/model check-in

### D) Model Deployment to higher environment.

## Do we need one workspace of multiple as we follow for databricks

## How does the access control managed if one workspace, considering development and devops is managed by different team and developers do not get access in production environment to change the models or code 

## How do we make sure Compute is pre-defined while providing the environment and data science users are only allowed to scale up or down

## How to make sure compute (Vms) are domain joined?

## What would be the interim approach as custom roles to control the access is not available.
