#!/bin/bash
#This is inline script, to run this as a file in build need to pass in parameter to this script and down to py script.
curl https://repo.continuum.io/miniconda/Miniconda3-latest-MacOSX-x86_64.sh -o ~/Downloads/Miniconda3-latest-MacOSX-x86_64.sh

bash ~/Downloads/Miniconda3-latest-MacOSX-x86_64.sh -b -p $HOME/miniconda

source ~/miniconda/etc/profile.d/conda.sh

env=$(base_env)

echo "Creating new base conda environment: $env"
conda env create -f 'Artifacts/notebooks/automl/automl_env.yml' -n $env Python=3.6
conda activate $env

echo "Started installing ipykernel..."
pip install ipykernel 
echo "Finished installing ipykernel..."

echo "Started installing kernel python36..."
python -m ipykernel install --name python36 --sys-prefix --display-name "Python 3.6"
echo "Finished installing kernel python36."

conda install nb_conda -y
echo "installing lightgbm" 

conda install lightgbm -c conda-forge -y
echo "Installing pytest..."
pip install pytest
echo "Finished installing pytest."

python 'scripts/run_notebooks.py' 'Artifacts/notebooks/00.AutoML.Getting Started' 'Artifacts/AutoMLNotebookRuns' $(sub) $(resourceGroup) 'notebooks_macos' $(location) $(slice) $(totalslices) -v