from checknotebookoutput import checkNotebookOutput
from checkexperimentresult import checkExperimentResult

checkExperimentResult(experiment_name='automl-dataset-local',
                      expected_num_iteration='2',
                      expected_minimum_score=0.5,
                      metric_name='AUC_weighted')

# Check the output cells of the notebook.
checkNotebookOutput('auto-ml-dataset.nbconvert.ipynb',
                    'warning[except]warning - retrying',
                    'nan')
