from checknotebookoutput import checkNotebookOutput

# Check the output cells of the notebook.
checkNotebookOutput('auto-ml-missing-data-blacklist-early-termination.nbconvert.ipynb',
                    'warning[except]warning - retrying',
                    'nan')
