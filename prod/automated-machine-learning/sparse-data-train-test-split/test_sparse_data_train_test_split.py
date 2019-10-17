from checknotebookoutput import checkNotebookOutput
from checkexperimentresult import checkExperimentResult

checkExperimentResult(experiment_name='sparse-data-train-test-split',
                      expected_num_iteration='5',
                      expected_minimum_score=0.5,
                      metric_name='AUC_weighted')

# Check the output cells of the notebook.
checkNotebookOutput('auto-ml-sparse-data-train-test-split.nbconvert.ipynb',
                    'warning[except]warning - retrying',
                    'nan')
