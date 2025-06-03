import pandas as pd
import sys
from azure.identity import ClientSecretCredential
from azure.mgmt.compute import ComputeManagementClient
import os
from datetime import datetime
from azure.mgmt.resource.subscriptions import SubscriptionClient

def log_result(log_filename, vm_name, cve, solution, script, result=None, error=None):
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    now = datetime.now().isoformat()
    log_file = os.path.join(log_dir, log_filename)
    with open(log_file, 'a') as f:
        f.write("="*80 + "\n\n")
        f.write(f"[{now}] Patch attemp for VM: {vm_name}\n")
        f.write(f"CVE: {cve}\n")
        f.write(f"Solution Summary: {solution}\n")
        f.write(f"Script used:\n\n{script}\n")
        if result:
            for msg in result.value:
                f.write(f"\n[StatusCode]: {msg.code}\n")
                f.write(f"[Level]: {msg.level}\n")
                f.write(f"[Message]:\n{msg.message}")
        if error:
            f.write(f"\n[Exception]: {str(error)}")
        f.write("\n" + "="*80 + "\n")

# Azure credentials
credential = ClientSecretCredential(
    tenant_id = "89f9dc47-f591-4759-a287-3b2fe3deca27"
    client_id = "4032f3bb-7f2a-456a-899c-746f2c3426bb"
    client_secret = ".Hl8Q~PzMp.EN0zBj2RDOme8BJG31d2RcZcridc."
)
#credential = AzureCliCredential()  # Use Azure CLI credentials

subscription_client = SubscriptionClient(credential)

# Get subscription ID from name
def get_subscription_id_by_name(subscription_name):
    for sub in subscription_client.subscriptions.list():
        if sub.display_name.strip().lower() == subscription_name.strip().lower():
            return sub.subscription_id
    raise ValueError(f"Subscription name '{subscription_name}' not found.")

# Get OS type from Azure
def get_os_type(subscription_id, rg_name, vm_name):
    compute_client = ComputeManagementClient(credential, subscription_id)
    vm = compute_client.virtual_machines.get(rg_name, vm_name)
    return vm.storage_profile.os_disk.os_type

def run_command_on_vm(subscription_id, rg_name, vm_name, os_type, commands):
    compute_client = ComputeManagementClient(credential, subscription_id)
    command_id = "RunShellScript" if os_type.lower() == "linux" else "RunPowerShellScript"
    script = commands

    params = {
        'command_id': command_id,
        'script': script
    }

    print(f"[{vm_name}] Running {command_id}...")
    result = compute_client.virtual_machines.begin_run_command(
        rg_name,
        vm_name,
        params
    ).result()

    return result

def get_resource_group_by_vm_name(subscription_id, vm_name):
    compute_client = ComputeManagementClient(credential, subscription_id)
    for vm in compute_client.virtual_machines.list_all():
        if vm.name.lower() == vm_name.lower():
            # The resource group is part of the VM's ID: /subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.Compute/virtualMachines/{vm}
            rg_name = vm.id.split("/")[4]
            return rg_name
    raise ValueError(f"VM '{vm_name}' not found in subscription '{subscription_id}'")

def get_vm_os_details(subscription_id, rg_name, vm_name):
    compute_client = ComputeManagementClient(credential, subscription_id)
    vm = compute_client.virtual_machines.get(rg_name, vm_name, expand='instanceView')
    image_ref = vm.storage_profile.image_reference
    os_disk = vm.storage_profile.os_disk
    os_type = os_disk.os_type if os_disk else "Unknown"
    details = {
        "os_type": str(os_type),
        "publisher": getattr(image_ref, "publisher", "Unknown"),
        "offer": getattr(image_ref, "offer", "Unknown"),
        "sku": getattr(image_ref, "sku", "Unknown"),
        "version": getattr(image_ref, "version", "Unknown"),
    }
    # Try to get more info from instance view if available
    if hasattr(vm, "instance_view") and vm.instance_view and hasattr(vm.instance_view, "os_name"):
        details["os_name"] = vm.instance_view.os_name
    if hasattr(vm, "instance_view") and vm.instance_view and hasattr(vm.instance_view, "os_version"):
        details["os_version"] = vm.instance_view.os_version
    return details

def run():

    df = pd.read_excel("VMs.xlsx")

    current_time = datetime.now().isoformat(timespec='seconds').replace(":", "-")
    log_filename = f"{current_time}.log"

    for _, row in df.iterrows():

        subscription_name = row["Cloud Account/Subscription Name"]
        vm_name = row["VM Name"]
        commands = row["commands"].strip().splitlines()
        cve = row['cve']
        solution = row['solution_summary']
        try:
            subscription_id = get_subscription_id_by_name(subscription_name)
            print(f"[{vm_name}] Subscription ID: {subscription_id}")

            rg_name = get_resource_group_by_vm_name(subscription_id, vm_name)
            print(f"[{vm_name}] Resource Group Name: {rg_name}")

            os_details = get_vm_os_details(subscription_id, rg_name, vm_name)
            print(f"[{vm_name}] OS Details: {os_details}")

            os_name = os_details.get("os_name", "Unknown")
            os_type = os_details.get("os_type", "Unknown")
            result = run_command_on_vm(subscription_id, rg_name, vm_name, os_type, commands)
            log_result(log_filename, vm_name, cve, solution, commands, result=result, error=None)

        except Exception as e:

            log_result(log_filename, vm_name, cve, solution, commands, result=None, error=e)
            print(f"[{vm_name}] Error: {e}")
            continue

if __name__ == "__main__":
    run()
