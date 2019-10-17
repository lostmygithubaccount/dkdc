import argparse
import json
import os
import requests
import subprocess
import sys

from azureml.core import Workspace
from requests.auth import HTTPBasicAuth

CACHE_REGISTRY_NAME = "viennaglobal"


class Acr():
    def __init__(self, name, username, password):
        name.replace(".azurecr.io", "")
        self.url = "{}.azurecr.io".format(name)
        self.name = name
        self.username = username
        self.password = password


def get_images_in_acr(acr):
    image_list_endpoint = "https://{}/v2/_catalog".format(acr.url)

    print("Getting list of images from {}".format(acr.name))
    resp = requests.get(image_list_endpoint, auth=HTTPBasicAuth(acr.username, acr.password))
    images = resp.json()['repositories'] or []
    return images


def get_cache(cache_service_principal_user, cache_service_principal_password, cache_tenant):
    az_login(cache_service_principal_user, cache_service_principal_password, cache_tenant)
    cache_username = get_keyvault_secret("viennaglobal-acr-sp-contributor-username")
    cache_password = get_keyvault_secret("viennaglobal-acr-sp-contributor-password")
    return Acr(name=CACHE_REGISTRY_NAME, username=cache_username, password=cache_password)


def exclude_warnings(cmd_output):
    json_output = ""
    start_index = None
    end_index = None
    curr_index = 0
    for cmd_line in cmd_output.splitlines():
        if cmd_line.startswith("{") and start_index is None:
            start_index = curr_index

        if cmd_line.startswith("}"):
            end_index = curr_index

        curr_index = curr_index + 1

    curr_index = 0
    for cmd_line in cmd_output.splitlines():
        if (curr_index >= start_index) and (curr_index <= end_index):
            if len(json_output) == 0:
                json_output = cmd_line
            else:
                json_output = json_output + "\n" + cmd_line

        curr_index = curr_index + 1

    return json_output


def get_keyvault_secret(secret_name, timeout=300):
    kv_command = ["az", "keyvault", "secret", "show", "--vault-name", "vienna-global", "-n", secret_name]
    full_secret = execute_subprocess_command(subprocess.check_output, kv_command, timeout=timeout)
    if not full_secret:
        raise ValueError("KV to get secret returned nothing")
    return json.loads(exclude_warnings(full_secret.decode('utf-8')))["value"]


def az_login(username, password, tenant):
    print("Executing az_login")
    cmd = ["az", "login", "--service-principal", "-u", username, "-p", password, "--tenant", tenant]
    execute_subprocess_command(subprocess.check_output, cmd, do_not_print=True)


def execute_subprocess_command(subprocess_command, command_to_execute, timeout=None, cwd=None,
                               do_not_print=False):
    # Sometimes, we end printing the az login service principal password.
    try:
        if not do_not_print:
            print("Running : {0}".format(' '.join(command_to_execute)))

        subprocess_args = {
            'shell': True,
            'cwd': cwd,
            'stderr': subprocess.STDOUT
        }

        if os.name == 'nt':
            command_to_execute = ([x.strip("'") for x in command_to_execute])
        else:
            command_to_execute = ' '.join(command_to_execute)

        if sys.version_info[0] != 2:
            subprocess_args['timeout'] = timeout

        return subprocess_command(command_to_execute, **subprocess_args)
    except subprocess.CalledProcessError as e:
        try:
            print("\nError executing subprocess\n")
            print(e.output.decode())
        except Exception:
            pass
        raise


def copy_images_to_cache(source_acr, cache_acr):
    source_images = get_images_in_acr(source_acr)
    cache_images = get_images_in_acr(cache_acr)
    print("Images in {}:\n{}\n".format(source_acr.name, source_images))
    print("Pushing images to {}".format(cache_acr.name))

    failed_push = []
    successfully_pushed = []
    for image in source_images:
        print("\nimage: {}".format(image))
        if image in cache_images:
            print("Skipping image {} which is already in cache".format(image))
            continue
        try:
            source_image_name = source_acr.url + "/" + image
            cache_image_name = cache_acr.url + "/" + image

            execute_subprocess_command(
                subprocess.check_output,
                ["docker", "login", source_acr.url, "-u", source_acr.username, "-p", source_acr.password],
                do_not_print=True)
            execute_subprocess_command(
                subprocess.check_output,
                ["docker", "pull", source_image_name])
            print(execute_subprocess_command(
                subprocess.check_output,
                ["docker", "image", "inspect", source_image_name]))
            execute_subprocess_command(
                subprocess.check_output,
                ["docker", "login", cache_acr.url, "-u", cache_acr.username, "-p", cache_acr.password])
            execute_subprocess_command(
                subprocess.check_output,
                ["docker", "tag", source_image_name, cache_image_name])
            execute_subprocess_command(
                subprocess.check_output,
                ["docker", "push", cache_image_name])

            successfully_pushed.append(image)
        except Exception as e:
            failed_push.append(image)
            print("\nError pushing {} to cache\n".format(image))
            try:
                print(e.output.decode())
            except Exception:
                pass

    print("Successfully pushed the following images to the cache:\n{}\n".format(successfully_pushed))
    print("Failed to push the following images to the cache:\n{}\n".format(failed_push))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # Must provide workspace info, or acr_url
    parser.add_argument("--workspace-name")
    parser.add_argument("--resource-group-name")
    parser.add_argument("--subscription-id")
    parser.add_argument("--workspace-tenant")

    parser.add_argument("--source-acr-name")
    parser.add_argument("--source-service-principal-user", required=True)
    parser.add_argument("--source-service-principal-password", required=True)

    parser.add_argument("--global-keyvault-service-principal-user", required=True)
    parser.add_argument("--global-keyvault-service-principal-password", required=True)
    parser.add_argument("--global-keyvault-tenant", required=True)
    args = parser.parse_args()

    workspace_name = args.workspace_name
    resource_group_name = args.resource_group_name
    subscription_id = args.subscription_id
    workspace_tenant = args.workspace_tenant

    source_acr_name = args.source_acr_name
    source_service_principal_user = args.source_service_principal_user
    source_service_principal_password = args.source_service_principal_password

    global_keyvault_service_principal_user = args.global_keyvault_service_principal_user
    global_keyvault_principal_password = args.global_keyvault_service_principal_password
    global_keyvault_tenant = args.global_keyvault_tenant

    if not (source_acr_name or (workspace_name and resource_group_name and subscription_id and workspace_tenant)):
        error_message = "Must provide source_acr_name or "
        error_message += "workspace_name/resource_group_name/subscription_id/workspace_tenant"
        parser.error(error_message)

    if not source_acr_name:
        az_login(source_service_principal_user, source_service_principal_password, workspace_tenant)
        ws = Workspace.get(name=workspace_name, resource_group=resource_group_name, subscription_id=subscription_id)

        ws_details = ws.get_details()
        print("Workspace details: {}".format(ws_details))
        if "containerRegistry" not in ws_details:
            print("Workspace does not have a container registry, so cannot get images")
            sys.exit(0)
        source_acr_name = ws_details["containerRegistry"].split("/")[-1]

    source_acr = Acr(
        name=source_acr_name, username=source_service_principal_user, password=source_service_principal_password)
    cache_acr = get_cache(
        global_keyvault_service_principal_user, global_keyvault_principal_password, global_keyvault_tenant)

    copy_images_to_cache(source_acr, cache_acr)
