source activate azureml

pip uninstall azureml-core -y
pip install azureml-core==0.1.0.* --index-url https://azuremlsdktestpypi.azureedge.net/sdk-release/master/588E708E0DF342C4A80BD954289657CF  --extra-index-url https://pypi.python.org/simple


pip uninstall azureml-contrib-datadrift -y
pip install azureml-datadrift==0.1.0.* --index-url https://azuremlsdktestpypi.azureedge.net/sdk-release/master/588E708E0DF342C4A80BD954289657CF  --extra-index-url https://pypi.python.org/simple

pip install azureml-opendatasets
