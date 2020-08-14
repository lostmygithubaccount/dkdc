import os
from azureml.core import Workspace, Experiment
from azureml.core.compute import AmlCompute, ComputeTarget
from azureml.train.automl import AutoMLConfig

ws = Workspace.from_config()
print("workspace details: \n{}\n".format(ws.get_details()))

current_directory = os.path.dirname(__file__)
get_data_script = os.path.join(current_directory, "get_data.py")

experiment = Experiment(ws, "sample_experiment")

# Create and configure a RunConfiguration it so that it generates the image needed


# Choose a name for your cluster.
batchai_cluster_name = "automlimage"

found = False
# Check if this compute target already exists in the workspace.
cts = ws.compute_targets
if batchai_cluster_name in cts and cts[batchai_cluster_name].type == 'BatchAI':
    found = True
    print('Found existing compute target.')
    compute_target = cts[batchai_cluster_name]

if not found:
    print('Creating a new compute target...')
    provisioning_config = AmlCompute.provisioning_configuration(vm_size="STANDARD_D2_V2", max_nodes=1)
    compute_target = ComputeTarget.create(ws, batchai_cluster_name, provisioning_config)

compute_target.wait_for_completion(show_output=True, min_node_count=None, timeout_in_minutes=20)

# Create AutoMLConfig to submit remote job
automl_config = AutoMLConfig(task='classification',
                             primary_metric='precision_score_weighted',
                             iteration_timeout_minutes=1,
                             iterations=2,
                             data_script=get_data_script,
                             path=current_directory,
                             compute_target=compute_target)

run_object = experiment.submit(automl_config, show_output=False)

run_object.wait_for_completion(wait_post_processing=True, show_output=True)
print(run_object.get_details())
