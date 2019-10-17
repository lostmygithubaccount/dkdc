# Test cancel of remote run

# Copyright (c) Microsoft Corporation. All rights reserved.
#
# Licensed under the MIT License.

import logging
import os
import random
import time
from azureml.core.compute import ComputeTarget, RemoteCompute

from matplotlib import pyplot as plt
from matplotlib.pyplot import imshow
import numpy as np
import pandas as pd
from sklearn import datasets

import azureml.core
from azureml.core import Dataset
from azureml.core.experiment import Experiment
from azureml.core.workspace import Workspace
from azureml.train.automl import AutoMLConfig
from azureml.train.automl.run import AutoMLRun
from azureml.core.conda_dependencies import CondaDependencies
from azureml.core.runconfig import RunConfiguration
from azureml.widgets import RunDetails
from checknotebookoutput import checkNotebookOutput

if __name__ == "__main__":
    ws = Workspace.from_config()

    print(ws.resource_group)
    print(ws.subscription_id)

    # choose a name for the run history container in the workspace
    experiment_name = 'automl-dataset-remote-bai'
    # project folder
    project_folder = './sample_projects/automl-dataset-remote-bai'

    experiment = Experiment(ws, experiment_name)
    automl_runs = list(experiment.get_runs(type='automl'))

    assert(len(automl_runs) == 1)

    compute_name = 'automlc2'

    compute_target = ws.compute_targets[compute_name]

    # create a new RunConfig object
    conda_run_config = RunConfiguration(framework="python")

    # Set compute target to AmlCompute
    conda_run_config.target = compute_target
    conda_run_config.environment.docker.enabled = True
    conda_run_config.environment.docker.base_image = azureml.core.runconfig.DEFAULT_CPU_IMAGE

    cd = CondaDependencies.create(pip_packages=['azureml-sdk[automl]'], conda_packages=['numpy', 'py-xgboost<=0.80'])
    conda_run_config.environment.python.conda_dependencies = cd

    automl_settings = {
        "iteration_timeout_minutes": 10,
        "iterations": 100,
        "n_cross_validations": 5,
        "primary_metric": 'AUC_weighted',
        "preprocess": True,
        "verbosity": logging.INFO
    }

    example_data = 'https://dprepdata.blob.core.windows.net/demo/crime0-random.csv'
    dataset = Dataset.Tabular.from_delimited_files(example_data)
    X = dataset.drop_columns(columns=['Primary Type', 'FBI Code'])
    y = dataset.keep_columns(columns=['Primary Type'], validate=True)

    automl_config = AutoMLConfig(task='classification',
                                 path=project_folder,
                                 run_configuration=conda_run_config,
                                 X=X,
                                 y=y,
                                 **automl_settings)

    remote_run = experiment.submit(automl_config)

    # Canceling runs
    #
    # You can cancel ongoing remote runs using the *cancel()* and *cancel_iteration()* functions

    print(remote_run.id)

    time.sleep(180)

    # Cancel the ongoing experiment and stop scheduling new iterations
    remote_run.cancel()

    print('run cancelled')

    # Wait for the run to complete.  It should complete soon because it has been canceled.
    remote_run.wait_for_completion()

    children = list(remote_run.get_children())

    print(len(children))

    if(len(children) == 100):
        raise Exception('Run wasnt cancelled properly, child run count is 100 should have been less than 100')

    # Check the output cells of the notebook.
    checkNotebookOutput('auto-ml-dataset-remote-execution.nbconvert.ipynb',
                        'warning[except]warning - retrying',
                        'nan')
