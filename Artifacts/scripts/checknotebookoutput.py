# This is used in notebook validation to check the output cells of the notebook.
# The method checkNotebookOutput asserts if any of the strings passed in args
# are found in the output of the notebook specified by fileName.
# The strings can also include the special value [except]. Values after [expect] are allowed
# even if the first value is found.
# For example, "bad[except]not bad" assert for any line containing "bad"
# except if it contains "not bad".
# There is also an option to check for anything written to stderr using the syntax [stderr].
# This also allow [except].
# For example, "[stderr][except]another Python warning" this asserts for any output to stderr
# except lines containing "another Python warning".

# This also checks if the output contain "More information about this error is available here: "
# If it does, it tries to download from the url specified.
# This is needed because the information is not available after the resource group has been
# deleted at the end of the build.

import json
import requests
import os


def downloadLogFile(fileUrl, moreInfoFileName):
    try:
        print("Trying to download from: " + fileUrl)
        response = requests.get(fileUrl)
        contents = response.text
        with open(moreInfoFileName, "w+") as text_file:
            text_file.write(contents)
        print("Download written to file: " + moreInfoFileName)
    except:
        print("Failed to download from: " + fileUrl)


def checkNotebookOutput(fileName, *args):
    moreinfotext = "More information about this error is available here: "
    folder = os.path.dirname(fileName)
    moreInfoFileName = os.path.join(folder, "MoreInfoFile.txt")
    notebook = json.load(open(fileName, 'r'))
    for cell in notebook["cells"]:
        if cell['cell_type'] == 'code':
            for output in cell['outputs']:
                if 'text' in output:
                    for line in output['text']:
                        if line.startswith(moreinfotext):
                            downloadLogFile(line[len(moreinfotext):], moreInfoFileName)
    for cell in notebook["cells"]:
        if cell['cell_type'] == 'code':
            for output in cell['outputs']:
                if 'text' in output:
                    for line in output['text']:
                        for text in args:
                            allowed = text.split("[except]")
                            not_allowed = allowed.pop(0)
                            lower_line = line.lower()
                            if not_allowed == "[stderr]":
                                if 'name' in output:
                                    assert(output['name'] != "stderr" or
                                           any((a.lower() in lower_line) for a in allowed)), \
                                        'Found [stderr] line:\n' + line + '\n in file ' + fileName
                            else:
                                assert(not_allowed.lower() not in lower_line or
                                       any((a.lower() in lower_line) for a in allowed)), not_allowed + \
                                    ' found in line:\n' + line + '\n in file ' + fileName
    print("checkNotebookOutput completed")
