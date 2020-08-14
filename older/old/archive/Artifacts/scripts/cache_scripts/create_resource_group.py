from azureml._base_sdk_common.common import resource_client_factory
from azureml.core.authentication import AzureCliAuthentication, ServicePrincipalAuthentication
from azure.mgmt.resource.resources.models import ResourceGroup
import argparse
import time


def create(name, subscription_id, location, auth, tags=None):
    if not tags:
        tags = {}

    if "creationTime" not in tags:
        tags["creationTime"] = str(time.time())
    if "creationSource" not in tags:
        tags["creationSource"] = "acr_cache_script"

    resource_management_client = resource_client_factory(auth, subscription_id)
    resource_group_properties = ResourceGroup(location=location, tags=tags)
    resource_management_client.resource_groups.create_or_update(name, resource_group_properties)
    print("Successfully created resource group = {} in subscription = {} with tags = {}".format(
        name, subscription_id, tags))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--resource-group-name", required=True)
    parser.add_argument("--subscription-id", required=True)
    parser.add_argument("--location", required=True)

    parser.add_argument("--tenant-id")
    parser.add_argument("--service-principal-id")
    parser.add_argument("--service-principal-password")

    parser.add_argument("--resource-group-creation-time-addition-minutes", type=float)
    args = parser.parse_args()

    resource_group_name = args.resource_group_name
    subscription_id = args.subscription_id
    location = args.location

    tenant_id = args.tenant_id
    service_principal_id = args.service_principal_id
    service_principal_password = args.service_principal_password

    resource_group_creation_time_addition_minutes = args.resource_group_creation_time_addition_minutes

    if tenant_id and service_principal_id and service_principal_password:
        auth = ServicePrincipalAuthentication(
            tenant_id=tenant_id,
            service_principal_id=service_principal_id,
            service_principal_password=service_principal_password)
    else:
        auth = AzureCliAuthentication()

    tags = {"creationTime": time.time() + resource_group_creation_time_addition_minutes * 60}

    max_retries = 3
    for i in range(0, max_retries):
        try:
            create(name=resource_group_name,
                   subscription_id=subscription_id,
                   location=location,
                   auth=auth,
                   tags=tags)
            break
        except Exception as e:
            print("Resource group creation failed: {}".format(e))
            time.sleep(1)
            continue
