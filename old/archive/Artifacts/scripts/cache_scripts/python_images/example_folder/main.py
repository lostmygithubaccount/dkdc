import os
from azureml.core import Workspace, RunConfiguration, Experiment, ScriptRunConfig
from azureml.core.conda_dependencies import CondaDependencies
# Should avoid any imports outside the Python standard library, except for azureml.core


ws = Workspace.from_config()
print("workspace details: \n{}\n".format(ws.get_details()))

current_directory = os.path.dirname(__file__)

# Use a dummy hello world script because all we care about is creating the image
hello_world_script = os.path.join(current_directory, "hello_world.py")

experiment = Experiment(ws, "sample_experiment")

# Create and configure a RunConfiguration it so that it generates the image needed
run_config = RunConfiguration(script=hello_world_script)
run_config.environment.docker.enabled = True
run_config.target = "amlcompute"
run_config.amlcompute.vm_size = "STANDARD_D2_V2"

cd = CondaDependencies.create(pip_packages=["requests"])
run_config.environment.python.conda_dependencies = cd

script_run_config = ScriptRunConfig(source_directory=current_directory, run_config=run_config)

run_object = experiment.submit(script_run_config)
run_object.wait_for_completion(wait_post_processing=True, show_output=True)
print(run_object.get_details())
