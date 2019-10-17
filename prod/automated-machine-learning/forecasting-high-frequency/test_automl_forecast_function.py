from checknotebookoutput import checkNotebookOutput
from checkexperimentresult import checkExperimentResult

checkExperimentResult(experiment_name='automl-forecast-function-demo',
                      expected_run_count=1,
                      expected_num_iteration='10',
                      expected_minimum_score=0.00,
                      expected_maximum_score=0.50,
                      metric_name='normalized_root_mean_squared_error',
                      absolute_minimum_score=0.0,
                      absolute_maximum_score=1.0)

# Check the output cells of the notebook.
checkNotebookOutput('automl-forecasting-function.nbconvert.ipynb',
                    'warning[except]warning - retrying')
