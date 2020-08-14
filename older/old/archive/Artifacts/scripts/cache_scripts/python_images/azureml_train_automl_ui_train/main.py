import os
from azureml.core import Workspace, Experiment, ScriptRunConfig, Environment
import azureml.train.automl
# Should avoid any imports outside the Python standard library, except for azureml.core


ws = Workspace.from_config()
print("workspace details: \n{}\n".format(ws.get_details()))

current_directory = os.path.dirname(__file__)

# Use a dummy hello world script because all we care about is creating the image
ui_env_dir = os.path.join(current_directory, "ui_env")

experiment = Experiment(ws, "sample_experiment")

automl_pkg = f'azureml-train-automl=={azureml.train.automl.SELFVERSION}'

ui_env = Environment.load_from_directory(ui_env_dir)
ui_env.python.conda_dependencies.add_pip_package(automl_pkg)


runconfig = ScriptRunConfig(source_directory=current_directory, script="hello_world.py")
runconfig.run_config.target = "amlcompute"
runconfig.run_config.amlcompute.vm_size = "STANDARD_D2_V2"
runconfig.run_config.environment = ui_env
run_object = experiment.submit(config=runconfig)

run_object.wait_for_completion(wait_post_processing=True, show_output=True)
print(run_object.get_details())
