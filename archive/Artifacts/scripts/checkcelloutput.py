# This is used in notebook validation to check the output of individual cells of the notebook.
# The method checkCellOutput asserts if the cell doesn't have the specified content.

import json


def checkCellOutput(fileName, expected_stdout):
    notebook = json.load(open(fileName, 'r'))
    code_cells = (cell for cell in notebook["cells"] if cell['cell_type'] == 'code')
    for cell, expected_output in zip(code_cells, expected_stdout):
        source = cell["source"]
        print('Checking cell starting with: ' + source[0])
        for actual_output in cell['outputs']:
            if "text" in actual_output:
                actual_output_text = actual_output["text"]
                for actual_line, expected_line in zip(actual_output_text, expected_output):
                    assert actual_line.startswith(expected_line), \
                        'Actual Line "' + actual_line + '" didn\'t match "' + expected_line + '"'
                assert len(actual_output_text) == len(expected_output), \
                    'Actual output length = ' + str(len(actual_output_text)) + \
                    ', expected_length - ' + str(len(expected_output))
    print("checkCellOutput completed")
