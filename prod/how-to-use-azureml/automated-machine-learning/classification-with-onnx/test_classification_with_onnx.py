# Test classification

from checknotebookoutput import checkNotebookOutput
from checkexperimentresult import checkExperimentResult

checkExperimentResult(experiment_name='automl-classification-onnx',
                      expected_num_iteration='10',
                      expected_minimum_score=0.5,
                      metric_name='AUC_weighted')

# Check the output cells of the notebook.
checkNotebookOutput('auto-ml-classification-with-onnx.nbconvert.ipynb',
                    'warning[except]warning - retrying',
                    'nan')
