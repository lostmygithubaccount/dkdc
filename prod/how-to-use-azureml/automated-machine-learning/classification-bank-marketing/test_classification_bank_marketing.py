# Test remote run

# Copyright (c) Microsoft Corporation. All rights reserved.
#
# Licensed under the MIT License.

from checknotebookoutput import checkNotebookOutput
from checkexperimentresult import checkExperimentResult

checkExperimentResult(experiment_name='automl-classification-bmarketing',
                      expected_num_iteration='10',
                      expected_minimum_score=0.7,
                      metric_name='AUC_weighted')

# Check the output cells of the notebook.
checkNotebookOutput('auto-ml-classification-bank-marketing.nbconvert.ipynb',
                    'warning[except]warning - retrying',
                    'nan')
