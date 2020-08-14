# To add a new image to the cache via Python script

Create a new folder which includes a `main.py`. Use the following code to get a workspace
```
from azureml.core import Workspace

ws = Workspace.from_config()
```
Avoid any imports from outside the Python standard library, except for `azureml.core`.


Prepare an image using this workspace, and it will get pushed into the cache when the `push_python_scripts_to_cache` release build is run.


A full example can be found in `./example_folder`