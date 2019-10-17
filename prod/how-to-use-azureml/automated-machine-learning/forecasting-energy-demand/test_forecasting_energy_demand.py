from checknotebookoutput import checkNotebookOutput
from checkexperimentresult import checkExperimentResult

checkExperimentResult(experiment_name='automl-energydemandforecasting',
                      expected_run_count=2,
                      expected_num_iteration='10',
                      expected_minimum_score=0.01,
                      expected_maximum_score=0.2,
                      metric_name='normalized_root_mean_squared_error',
                      absolute_minimum_score=0.0,
                      absolute_maximum_score=1.0)

# Check the output cells of the notebook.
# using the lags does in fact generate some expected 'nan's
checkNotebookOutput('auto-ml-forecasting-energy-demand.nbconvert.ipynb',
                    'warning[except]warning - retrying')
