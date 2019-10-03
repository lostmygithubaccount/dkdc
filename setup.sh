~/miniconda3/bin/pip uninstall azureml-core -y
~/miniconda3/bin/pip install azureml-core==0.1.0.* --index-url https://azuremlsdktestpypi.azureedge.net/sdk-release/master/588E708E0DF342C4A80BD954289657CF  --extra-index-url https://pypi.python.org/simple

~/miniconda3/bin/pip uninstall azureml-contrib-datadrift -y
~/miniconda3/bin/pip install azureml-datadrift==0.1.0.* --index-url https://azuremlsdktestpypi.azureedge.net/sdk-release/master/588E708E0DF342C4A80BD954289657CF  --extra-index-url https://pypi.python.org/simple

~/miniconda3/bin/pip install azureml-opendatasets
