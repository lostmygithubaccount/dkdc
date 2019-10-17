from checknotebookoutput import checkNotebookOutput
from checkexperimentresult import checkExperimentResult
from checkcelloutput import checkCellOutput

checkExperimentResult(experiment_name='automl-local-regression',
                      expected_num_iteration='10',
                      expected_minimum_score=0.45,
                      metric_name='spearman_correlation',
                      absolute_minimum_score=-1.0)

# Check the output cells of the notebook.
checkNotebookOutput('auto-ml-regression.nbconvert.ipynb',
                    'warning[except]warning - retrying',
                    'nan',
                    '[stderr][except]warning - retrying')

# Check expected cell output contents.
expected_cells = [
    [],
    ["Found the config file in: "],
    [],
    [],
    [
        "Running on local machine\n",
        "Parent Run ID: ",
        "Current status: DatasetCrossValidationSplit. Generating CV splits.\n",
        "Current status: ModelSelection. Beginning model selection.\n",
        "\n",
        "***********************************************************************" +
        "*****************************\n",
        "ITERATION: The iteration being evaluated.\n",
        "PIPELINE: A summary description of the pipeline being evaluated.\n",
        "DURATION: Time taken for the current iteration.\n",
        "METRIC: The result of computing score on the fitted pipeline.\n",
        "BEST: The best observed score thus far.\n",
        "***********************************************************************" +
        "*****************************\n",
        "\n",
        " ITERATION   PIPELINE                                       DURATION" +
        "      METRIC      BEST\n",
        "         0   ",
        "         1   ",
        "         2   ",
        "         3   ",
        "         4   ",
        "         5   ",
        "         6   ",
        "         7   ",
        "         8   VotingEnsemble",
        "         9   StackEnsemble"]]

checkCellOutput('auto-ml-regression.nbconvert.ipynb', expected_cells)
