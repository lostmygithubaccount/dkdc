# Copyright (c) Microsoft Corporation. All rights reserved.

import json
import os
import subprocess
from pathlib import Path
from azureml.core import Workspace
from azureml.core.compute import ComputeTarget, RemoteCompute

# Get workspace
ws = Workspace.from_config()

# Create a shared CPU DSVM

# VM details
vm_name = "cpudsvm"
location = ws.location
rg = ws.resource_group
vm_size = "Standard_DS3_v2"
image = "microsoft-dsvm:linux-data-science-vm-ubuntu:linuxdsvmubuntu:latest"
admin = "amluser"

# CLI command to create DSVM
create_cmd = "az vm create"
vm_location = " -n {} -l {} -g {}".format(vm_name, location, rg)
vm_specs = (
    " --size {}"
    " --image {}"
    " --admin-username {}"
    " --generate-ssh-keys".format(vm_size, image, admin))

create_cmd = create_cmd + vm_location + vm_specs

print("Creating DSVM using command: ", create_cmd)

proc_cr = subprocess.Popen(
    create_cmd,
    shell=True,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE)

output, error = proc_cr.communicate()

# Get dynamic IP address of VM
ip_cmd = "az vm list-ip-addresses -n {} -g {}".format(vm_name, rg)
print("Getting IP address using command: ", ip_cmd)
proc_ip = subprocess.Popen(ip_cmd, shell=True, stdout=subprocess.PIPE)
output, error = proc_ip.communicate()
output = json.loads(output.decode("ascii"))

ipAddress = str(
    output[0]
    ["virtualMachine"]
    ["network"]
    ["publicIpAddresses"][0]
    ["ipAddress"])

# Attach VM to Workspace

print("Attaching DSVM with IP address ", ipAddress)

attach_config = RemoteCompute.attach_configuration(
    username=admin,
    address=ipAddress,
    private_key_file=os.path.join(str(Path.home()), ".ssh/id_rsa"))

dsvm = ComputeTarget.attach(
    workspace=ws,
    name=vm_name,
    attach_configuration=attach_config)

dsvm.wait_for_completion(show_output=True)
status = dsvm.get_status()

if status != "Succeeded":
    raise Exception('Failed to provision DSVM')
