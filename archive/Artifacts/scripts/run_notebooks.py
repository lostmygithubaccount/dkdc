from datetime import datetime
import json
import os
import re
import subprocess
import sys
from shutil import copyfile

result_ok = 'Ok'
result_failed = 'Failed'


class Notebook:
    def __init__(self, name, dependencies, cell_timeout, full_path, preexec, postexec):
        self.name = name
        self.dependencies = dependencies
        self.full_path = full_path
        self.cell_timeout = cell_timeout
        self.dir_path = os.path.dirname(full_path)
        self.preexec = preexec
        self.postexec = postexec

    def _execute_python_script(self, script_name):
        print("Preparing to run script: ", script_name)
        env = os.environ.copy()
        env["PYTHONPATH"] = os.path.dirname(os.path.realpath(__file__))
        error_file = "{}/{}_error.txt".format(
            self.dir_path, script_name)
        with open(error_file, "w") as f:
            returncode = subprocess.call(["python", script_name],
                                         shell=False, cwd=self.dir_path, env=env, stdout=f, stderr=f)
        print("Finished running script.")
        result = self._get_python_script_result(returncode)
        self._generate_result(script_name, result)
        print("Finished running notebook.")
        return result == result_ok

    def _execute_notebook(self, notebook_name, cell_timeout):
        nbcommand = "jupyter nbconvert --execute \"{}/{}\" --to notebook --ExecutePreprocessor.timeout={} \
        --allow-errors --debug 2>&1"
        nbconvertInvokeParam = nbcommand.format(
            self.dir_path, notebook_name, cell_timeout)
        # Remove .ipynb extension with [:-6]
        nbconvert_filename = "{}/{}.nbconvert.ipynb".format(
            self.dir_path, notebook_name[:-6])
        print("Preparing to run notebook with command: ", nbconvertInvokeParam)
        env = os.environ.copy()
        subprocess.call([nbconvertInvokeParam, ""], shell=True, env=env)
        result = self._get_notebook_result(nbconvert_filename)
        self._generate_result(notebook_name, result)
        print("Finished running notebook.")
        return result == result_ok

    def Execute(self):
        if_everything_passed = True
        is_success = False
        for execute_candidate in [self.preexec, self.name, self.postexec]:
            if execute_candidate is not None:
                start = datetime.utcnow()
                if execute_candidate.endswith(".ipynb"):
                    is_success = self._execute_notebook(
                        execute_candidate, self.cell_timeout)
                elif execute_candidate.endswith(".py"):
                    is_success = self._execute_python_script(execute_candidate)
                else:
                    raise Exception(
                        "{}: No known execution method found.".format(execute_candidate))
                time_taken = datetime.utcnow() - start
                metrics = {
                    'region': workspace_location,
                    'subscription': subscription_id,
                    'message': 'Passed' if is_success else 'Failed',
                    'owner': 'Azure',
                    'status': 'Passed' if is_success else 'Failed',
                    'filename': execute_candidate
                }
                subprocess_args = [str(i) for i in [
                    'bash',
                    os.path.dirname(sys.argv[0]) + '/macos_log_appinsights.sh',
                    self.name,
                    0,
                    int(time_taken.total_seconds()),
                    is_success,
                    is_success,
                    metrics
                ]]
                print('Logging notebook run to AppInsights: {}'.format(' '.join(subprocess_args)))
                subprocess.call(subprocess_args)
                if_everything_passed = if_everything_passed and is_success

        return if_everything_passed

    def _get_python_script_result(self, returncode):
        if returncode == 0:
            return result_ok
        else:
            return result_failed

    def _get_notebook_result(self, outputfile):
        print("NBConvert notebook path: ", outputfile)
        if not os.path.isfile(outputfile):
            return result_failed
        pattern = "\"output_type\": \"error\""
        for i, line in enumerate(open(outputfile)):
            match = re.findall(pattern, line)
            if(len(match) > 0):
                return result_failed
        return result_ok

    def _generate_result(self, notebook_name, result):
        testcase_name = notebook_name.replace(".ipynb", "")\
            .replace(".py", "")\
            .replace('-', '_')\
            .replace('.', "_")
        code = "import pytest\ndef test_{}():\n    assert \"{}\"==\"Ok\"".format(
            testcase_name, result)

        test_file = "{}/{}_{}.py".format(
            self.dir_path, 'test', testcase_name)
        test_report = "{}/{}-{}.xml".format(
            self.dir_path, 'Test', testcase_name)
        print("testcase: ", testcase_name)
        print("test_file: ", test_file)
        print("test_report: ", test_report)
        with open(test_file, "w+") as f:
            f.write(code)
        pytest_command = "python -m pytest {} --junitxml {}".format(
            test_file, test_report)
        env = os.environ.copy()
        subprocess.call([pytest_command, ""], shell=True, env=env)
        print("Executed the pytest command: ", pytest_command)


def write_config(fileName, subscription_id,
                 resource_group, workspace_name):
    with open(fileName, "w") as the_file:
        the_file.write("{{\"subscription_id\": \"{0}\", \"resource_group\": \"{1}\", \"workspace_name\": \"{2}\"}}"
                       .format(
                           subscription_id, resource_group, workspace_name))
        the_file.close()
        print("Created config.json at: ", fileName)


def execute_slice(i, slice, total_slices):
    if(i is not None):
        if(i % total_slices == slice - 1):
            return True
        else:
            return False
    return True


def load_notebooks(source_path, release, notebooks, channel):
    include = release.get("include", None)
    if include is not None:
        for key in include.keys():
            value = include[key]
            new_source_path = "{}/{}".format(source_path, value)
            release_json = "{}/release.json".format(new_source_path)
            print("{}: {}".format(key, value))
            if os.path.isfile(release_json):
                with open(release_json) as f:
                    nested_release = json.load(f)
                    load_notebooks(new_source_path,
                                   nested_release, notebooks, channel)
    all_notebooks = release.get('notebooks', None)
    channel_notebooks = None
    channels = release.get("channels", None)
    if channels is not None:
        if channel is not None:
            channel_notebooks = channels.get(channel, None)
    if all_notebooks is not None:
        for nb in all_notebooks:
            notebook = all_notebooks[nb]
            dependencies = notebook.get("dependencies", [])
            preexec = notebook.get("preexec", None)
            postexec = notebook.get("postexec", None)
            cell_timeout = notebook.get("celltimeout", 1200)
            notebook_path = notebook.get("path", "")
            notebook_name = notebook["name"]
            full_path = "{}/{}".format(source_path, notebook_path)

            notebook = Notebook(notebook_name,
                                dependencies,
                                cell_timeout,
                                full_path,
                                preexec,
                                postexec)
            if channel_notebooks is not None and nb in channel_notebooks:
                notebooks.append(notebook)


def run_notebooks(slice, total_slices, source_working_dir, destination_working_dir, channel):
    i = 0
    if_evenrything_passed = True
    source_dir = source_working_dir
    destination_dir = destination_working_dir
    notebooks = []
    with open("{}/{}".format(source_working_dir, 'release.json')) as f:
        release = json.load(f)
        load_notebooks(source_dir, release, notebooks, channel)

    for notebook in notebooks:
        # copy notebook
        if execute_slice(i, slice, total_slices):
            target_folder_name = notebook.full_path.replace(
                "/", "-").replace("F:", "").strip("-")
            destination_path = "{}/{}/{}".format(
                destination_working_dir, target_folder_name, notebook.name)
            if not os.path.exists(os.path.dirname(destination_path)):
                os.makedirs(os.path.dirname(destination_path))

            destination_dir = os.path.dirname(destination_path)

            for execute_candidate in [notebook.preexec, notebook.name, notebook.postexec]:
                if execute_candidate is not None:
                    source_path = "{}/{}".format(notebook.full_path,
                                                 execute_candidate)
                    destination_path = "{}/{}/{}".format(
                        destination_working_dir,
                        target_folder_name, execute_candidate)
                    copyfile(source_path, destination_path)

            # copy dependencies
            for dependency in notebook.dependencies:
                source_path = "{}/{}".format(notebook.full_path, dependency)
                destination_path = "{}/{}".format(
                    destination_dir, dependency)
                copyfile(source_path, destination_path)

            config_json_path = "{}/{}/{}".format(
                destination_dir, '.azureml', 'config.json')
            if not os.path.exists(os.path.dirname(config_json_path)):
                os.makedirs(os.path.dirname(config_json_path))

            write_config(config_json_path,
                         subscription_id, resource_group, workspace_name)
            notebook_to_execute = Notebook(notebook.name,
                                           notebook.dependencies,
                                           notebook.cell_timeout,
                                           destination_path,
                                           notebook.preexec,
                                           notebook.postexec)
            is_success = notebook_to_execute.Execute()
            if_evenrything_passed = if_evenrything_passed and is_success
        i += 1

    return if_evenrything_passed


if __name__ == "__main__":
    args = sys.argv
    source_working_dir = args[1]
    destination_working_dir = args[2]
    channel = args[3]
    subscription_id = args[4]
    resource_group = args[5]
    workspace_name = args[6]
    workspace_location = args[7]
    current_slice = int(args[8])
    total_slice = int(args[9])
    dsvm_password = args[10]

    os.environ["SUBSCRIPTION_ID"] = subscription_id
    os.environ["RESOURCE_GROUP"] = resource_group
    os.environ["WORKSPACE_NAME"] = workspace_name
    os.environ["WORKSPACE_REGION"] = workspace_location
    os.environ["automlvmpass"] = dsvm_password

    evenrything_passed = run_notebooks(current_slice, total_slice,
                                       source_working_dir, destination_working_dir, channel)

    if(not evenrything_passed):
        sys.exit(1)
