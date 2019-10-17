# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# USAGE
#
# 1. Add following metadata elements to the notebook
#
# "friendly_name": "string", friendly name for notebook
# "exclude_from_index": true/false, setting true excludes the notebook from index
# "index_order": integer, smaller value moves notebook closer to beginning
# "category": "starter", "tutorial", "training", "deployment" or "other"
# "star_tag": [ "featured" ], optional, only supported tag to highlight notebook with :star: symbol
# "task": "string", description of notebook task
# "datasets": [ "dataset 1", "dataset 2"], list of datasets, can be ["None"]
# "compute": [ "compute 1", "compute 2" ], list of computes, can be ["None"]
# "deployment": ["deployment 1", "deployment 2"], list of deployment targets, can be ["None"]
# "framework": ["fw 1", "fw2"], list of ml framework, can be ["None"]
# "tags": ["tag 1", "tag 2"], list of tags in your notebook, can be ["None"]
#
# 2. Then run
#
# build_nb_index.py <root folder of notebooks>
#
# 3. The script should produce index.md file with tables of notebook indices

# Example metadata section

'''
  "metadata": {
    "authors": [
      {
        "name": "cforbe"
      }
    ],
    "kernelspec": {
      "display_name": "Python 3.6",
      "language": "python",
      "name": "python36"
    },
    "language_info": {
      "codemirror_mode": {
        "name": "ipython",
        "version": 3
      },
      "file_extension": ".py",
      "mimetype": "text/x-python",
      "name": "python",
      "nbconvert_exporter": "python",
      "pygments_lexer": "ipython3",
      "version": "3.6.7"
    },
    "friendly_name": "Prepare data for regression modeling",
    "exclude_from_index": false,
    "index_order": 1,
    "category": "tutorial",
    "star_tag": [
      "featured"
    ],
    "task": "Regression",
    "datasets": [
      "NYC Taxi"
    ],
    "compute": [
      "local"
    ],
    "deployment": [
      "None"
    ],
    "framework": [
      "Azure ML AutoML"
    ],
    "tags": [
      "Pipeline scheduler"
    ]
  }
'''

import os
import json
import sys


# Index building walk over notebook folder
def index_post_process(notebooks_dir):
    indexer = NotebookIndex()
    n_dest = len(notebooks_dir)
    for r, d, f in os.walk(notebooks_dir):
        for file in f:
            # Handle only notebooks
            if file.endswith(".ipynb") and not file.endswith('checkpoint.ipynb'):
                try:
                    file_path = os.path.join(r, file)
                    with open(file_path, 'r') as fin:
                        content = json.load(fin)
                    print(file)
                    indexer.add_to_index(os.path.join(r[n_dest:], file), content["metadata"])
                except Exception as e:
                    print("Problem: ", str(e))
    indexer.write_index("./index.md")

# Customize these make index look different.


index_template = '''
# Index
Azure Machine Learning is a cloud service that you use to train, deploy, automate,
and manage machine learning models. This index should assist in navigating the Azure
Machine Learning notebook samples and encourage efficient retrieval of topics and content.
![Impressions](https://PixelServer20190423114238.azurewebsites.net/api/impressions/MachineLearningNotebooks/Index.png)

## Getting Started

|Title| Task | Dataset | Training Compute | Deployment Target | ML Framework | Tags |
|:----|:-----|:-------:|:----------------:|:-----------------:|:------------:|:------------:|
GETTING_STARTED_NBS

## Tutorials

|Title| Task | Dataset | Training Compute | Deployment Target | ML Framework | Tags |
|:----|:-----|:-------:|:----------------:|:-----------------:|:------------:|:------------:|
TUTORIAL_NBS

## Training

|Title| Task | Dataset | Training Compute | Deployment Target | ML Framework | Tags |
|:----|:-----|:-------:|:----------------:|:-----------------:|:------------:|:------------:|
TRAINING_NBS


## Deployment


|Title| Task | Dataset | Training Compute | Deployment Target | ML Framework | Tags |
|:----|:-----|:-------:|:----------------:|:-----------------:|:------------:|:------------:|
DEPLOYMENT_NBS


## Other Notebooks
|Title| Task | Dataset | Training Compute | Deployment Target | ML Framework | Tags |
|:----|:-----|:-------:|:----------------:|:-----------------:|:------------:|:------------:|
OTHER_NBS
'''

ir = "| NB_SYMBOL[NB_NAME](NB_PATH) | NB_TASK | NB_DATASET | NB_COMPUTE | NB_DEPLOYMENT | NB_FRAMEWORK | NB_TAGS |\n"

index_file = "index.md"

nb_types = ["starter", "tutorial", "training", "deployment", "other"]
replace_strings = ["GETTING_STARTED_NBS", "TUTORIAL_NBS", "TRAINING_NBS", "DEPLOYMENT_NBS", "OTHER_NBS"]


class NotebookIndex:
    def __init__(self):
        self.index = index_template
        self.nb_rows = {}
        for elem in nb_types:
            self.nb_rows[elem] = []

    def add_to_index(self, path_to_notebook, metadata):
        repo_url = "https://github.com/Azure/MachineLearningNotebooks/blob/master/"

        if "exclude_from_index" in metadata:
            if metadata["exclude_from_index"]:
                return

        if "friendly_name" in metadata:
            this_row = ir.replace("NB_NAME", metadata["friendly_name"])
        else:
            this_name = os.path.basename(path_to_notebook)
            this_row = ir.replace("NB_NAME", this_name[:-6])

        path_to_notebook = path_to_notebook.replace("\\", "/")
        this_row = this_row.replace("NB_PATH", repo_url + path_to_notebook)

        if "task" in metadata:
            this_row = this_row.replace("NB_TASK", metadata["task"])
        if "datasets" in metadata:
            this_row = this_row.replace("NB_DATASET", ", ".join(metadata["datasets"]))
        if "compute" in metadata:
            this_row = this_row.replace("NB_COMPUTE", ", ".join(metadata["compute"]))
        if "deployment" in metadata:
            this_row = this_row.replace("NB_DEPLOYMENT", ", ".join(metadata["deployment"]))
        if "framework" in metadata:
            this_row = this_row.replace("NB_FRAMEWORK", ", ".join(metadata["framework"]))
        if "tags" in metadata:
            this_row = this_row.replace("NB_TAGS", ", ".join(metadata["tags"]))
        # Fall back
        this_row = this_row.replace("NB_TASK", "")
        this_row = this_row.replace("NB_DATASET", "")
        this_row = this_row.replace("NB_COMPUTE", "")
        this_row = this_row.replace("NB_DEPLOYMENT", "")
        this_row = this_row.replace("NB_FRAMEWORK", "")
        this_row = this_row.replace("NB_TAGS", "")

        if "star_tag" in metadata:
            if "featured" in metadata["star_tag"]:
                this_row = this_row.replace("NB_SYMBOL", ":star:")
        # Fall back
        this_row = this_row.replace("NB_SYMBOL", "")

        index_order = 9999999
        if "index_order" in metadata:
            index_order = metadata["index_order"]

        if "category" in metadata:
            self.nb_rows[metadata["category"]].append((index_order, this_row))
        else:
            self.nb_rows["other"].append((index_order, this_row))

    def sort_and_stringify(self, section):
        sorted_index = sorted(self.nb_rows[section], key=lambda x: x[0])
        sorted_index = [x[1] for x in sorted_index]
        # TODO: Make this portable
        return "\n".join(sorted_index)

    def write_index(self, index_file):
        for nb_type, replace_string in zip(nb_types, replace_strings):
            nb_string = self.sort_and_stringify(nb_type)
            self.index = self.index.replace(replace_string, nb_string)
        with open(index_file, "w") as fin:
            fin.write(self.index)


try:
    dest_repo = sys.argv[1]
except:
    dest_repo = "./MachineLearningNotebooks"
