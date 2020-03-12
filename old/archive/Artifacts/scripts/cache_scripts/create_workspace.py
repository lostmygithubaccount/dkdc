from azureml.core.authentication import ServicePrincipalAuthentication
from azureml.core import Workspace
import argparse
import time


def create(workspace_name, resource_group_name, subscription_id, location, auth):
    return Workspace.create(
        name=workspace_name,
        subscription_id=subscription_id,
        resource_group=resource_group_name,
        location=location,
        exist_ok=True,
        auth=auth
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--resource-group-name", required=True)
    parser.add_argument("--subscription-id", required=True)
    parser.add_argument("--location", required=True)
    parser.add_argument("--workspace-name", required=True)

    parser.add_argument("--tenant-id")
    parser.add_argument("--service-principal-id")
    parser.add_argument("--service-principal-password")

    parser.add_argument("--workspace-write-config-location")
    args = parser.parse_args()

    workspace_name = args.workspace_name
    resource_group_name = args.resource_group_name
    subscription_id = args.subscription_id
    location = args.location

    tenant_id = args.tenant_id
    service_principal_id = args.service_principal_id
    service_principal_password = args.service_principal_password

    workspace_write_config_location = args.workspace_write_config_location

    if tenant_id and service_principal_id and service_principal_password:
        print("Using ServicePrincipal auth")
        auth = ServicePrincipalAuthentication(
            tenant_id=tenant_id,
            service_principal_id=service_principal_id,
            service_principal_password=service_principal_password)
    else:
        print("Using default auth")
        auth = None

    max_retries = 3
    for i in range(0, max_retries):
        try:
            ws = create(workspace_name=workspace_name,
                        resource_group_name=resource_group_name,
                        subscription_id=subscription_id,
                        location=location,
                        auth=auth)
            break
        except Exception as e:
            print("Workspace creation failed: {}".format(e))
            time.sleep(1)
            continue

    print("Workspace details: \n{}".format(ws.get_details()))

    if workspace_write_config_location:
        print("Writing workspace config to: {}".format(workspace_write_config_location))
        ws.write_config(path=workspace_write_config_location)
