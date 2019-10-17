from checknotebookoutput import checkNotebookOutput
from checkexperimentresult import checkExperimentResult

checkExperimentResult(experiment_name='non_sample_weight_experiment',
                      expected_num_iteration='10',
                      expected_minimum_score=0.3,
                      metric_name='AUC_weighted')

checkExperimentResult(experiment_name='sample_weight_experiment',
                      expected_num_iteration='10',
                      expected_minimum_score=0.3,
                      metric_name='AUC_weighted')

# Check the output cells of the notebook.
checkNotebookOutput('auto-ml-sample-weight.nbconvert.ipynb',
                    'warning[except]warning - retrying',
                    'nan')
