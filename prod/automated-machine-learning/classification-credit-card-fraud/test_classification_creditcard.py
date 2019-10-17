# Test remote run

# Copyright (c) Microsoft Corporation. All rights reserved.
#
# Licensed under the MIT License.

from checknotebookoutput import checkNotebookOutput
from checkexperimentresult import checkExperimentResult

checkExperimentResult(experiment_name='automl-classification-ccard',
                      expected_num_iteration='10',
                      expected_minimum_score=0.6,
                      metric_name='average_precision_score_weighted')

# Check the output cells of the notebook.
checkNotebookOutput('auto-ml-classification-credit-card-fraud.nbconvert.ipynb',
                    'warning[except]warning - retrying',
                    'nan')
