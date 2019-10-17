# Test remote run

# Copyright (c) Microsoft Corporation. All rights reserved.
#
# Licensed under the MIT License.

from checknotebookoutput import checkNotebookOutput
from checkexperimentresult import checkExperimentResult

checkExperimentResult(experiment_name='automl-regression-concrete',
                      expected_num_iteration='10',
                      expected_minimum_score=0.6,
                      metric_name='spearman_correlation')

# Check the output cells of the notebook.
checkNotebookOutput('auto-ml-regression-concrete-strength.nbconvert.ipynb',
                    'warning[except]warning - retrying',
                    'nan')
