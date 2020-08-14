# Check the results for an AutoML experiment

# Copyright (c) Microsoft Corporation. All rights reserved.
#
# Licensed under the MIT License.

from azureml.core.experiment import Experiment
from azureml.core.workspace import Workspace
from azureml.train.automl.run import AutoMLRun


def checkExperimentResult(experiment_name,
                          metric_name,
                          expected_num_iteration,
                          expected_minimum_score,
                          absolute_minimum_score=0.0,
                          expected_maximum_score=1.0,
                          absolute_maximum_score=1.0,
                          expected_run_count=1):
    ws = Workspace.from_config()

    experiment = Experiment(ws, experiment_name)
    automl_runs = list(experiment.get_runs(type='automl'))

    print("Run count: {}".format(len(automl_runs)))

    assert(len(automl_runs) == expected_run_count)

    for run in automl_runs:
        print("Validating run: " + run.id)
        ml_run = AutoMLRun(experiment=experiment, run_id=run.id)

        properties = ml_run.get_properties()
        status = ml_run.get_details()
        print("Number of iterations found = " + properties['num_iterations'])
        assert(properties['num_iterations'] == expected_num_iteration)

        children = list(ml_run.get_children())
        badScoreCount = 0

        for iteration in children:
            metrics = iteration.get_metrics()
            print(iteration.id)
            print(iteration.status)
            assert(iteration.status == 'Completed')
            print(metrics[metric_name])
            assert(metrics[metric_name] >= absolute_minimum_score)
            assert(metrics[metric_name] <= absolute_maximum_score)
            if metrics[metric_name] < expected_minimum_score or \
               metrics[metric_name] > expected_maximum_score:
                badScoreCount += 1
        assert(badScoreCount < int(expected_num_iteration) / 2)
        print('Run status: ' + status['status'])
        assert(status['status'] == 'Completed')
    print("checkExperimentResult complete")
