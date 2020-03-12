import argparse
import os
import subprocess
import tempfile
from subprocess import Popen
from azureml.core import Workspace
from push_images_to_cache import execute_subprocess_command

PYTHON_SCRIPT_DIR_NAME = "python_images"


def az_login(username, password, tenant):
    print("Executing az_login")
    cmd = ["az", "login", "--service-principal", "-u", username, "-p", password, "--tenant", tenant]
    execute_subprocess_command(subprocess.check_output, cmd, do_not_print=True)


def get_directories():
    python_script_dir_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), PYTHON_SCRIPT_DIR_NAME)
    print("Looking for Python scripts in: {}".format(python_script_dir_path))

    directories = [os.path.join(python_script_dir_path, x) for x in os.listdir(python_script_dir_path)]
    directories = [x for x in directories if os.path.isdir(x)]
    print("directories found: {}".format(directories))
    return directories


def run_files_in_directories(directories):
    failed_scripts = []
    successful_scripts = []
    subprocesses = []

    # Start running each main.py in a subprocess
    for sub_dir in directories:
        print("Looking for main.py in: {}".format(sub_dir))
        main_file_path = os.path.join(sub_dir, "main.py")
        if not os.path.exists(main_file_path):
            print("main.py not found. Skipping directory")
            continue

        output_filename = "".join([c for c in sub_dir if c.isalpha() or c.isdigit() or c == ' ']).rstrip()
        temp_file = tempfile.NamedTemporaryFile(delete=False, prefix=output_filename)
        p = Popen(["python", main_file_path], stdout=temp_file, stderr=temp_file)
        subprocesses.append((p, main_file_path, temp_file))

    # Wait for all subprocesses to finish, then print output
    for subproc, main_file_path, temp_file in subprocesses:
        print("\nWaiting for process: {}".format(main_file_path))
        subproc.wait()
        try:
            print("Finished running {}. Uploading to VSTS with filename: {}".format(main_file_path, temp_file.name))
            with open(temp_file.name, "r") as f:
                # Print on one line so log output is easier to read quickly
                print(f.readlines())
            # Special text to upload files to VSTS
            print("\n##vso[task.uploadfile]" + temp_file.name)

            if subproc.returncode == 0:
                successful_scripts.append(main_file_path)
            else:
                failed_scripts.append(main_file_path)
        except Exception as exc:
            print("Error while getting output, but continuing: {}".format(exc))

    print("\nThe following scripts succeeded: {}".format(successful_scripts))
    if len(failed_scripts):
        raise ValueError("The following scripts failed: {}".format(failed_scripts))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace-name", required=True)
    parser.add_argument("--resource-group-name", required=True)
    parser.add_argument("--subscription-id", required=True)
    parser.add_argument("--location", required=True)

    parser.add_argument("--tenant-id", required=True)
    parser.add_argument("--service-principal-id", required=True)
    parser.add_argument("--service-principal-password", required=True)
    args = parser.parse_args()

    workspace_name = args.workspace_name
    resource_group_name = args.resource_group_name
    subscription_id = args.subscription_id
    location = args.location

    tenant_id = args.tenant_id
    service_principal_id = args.service_principal_id
    service_principal_password = args.service_principal_password

    az_login(service_principal_id, service_principal_password, tenant_id)

    print("Going to try to get/create a workspace")
    ws = Workspace.create(
        name=workspace_name,
        subscription_id=subscription_id,
        resource_group=resource_group_name,
        location=location,
        exist_ok=True)
    print("Workspace details: \n{}\n".format(ws.get_details()))
    ws.write_config()

    directories = get_directories()
    run_files_in_directories(directories)
