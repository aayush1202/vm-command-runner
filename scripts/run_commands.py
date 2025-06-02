import pandas as pd
import sys
from azure.identity import ClientSecretCredential
from azure.mgmt.compute import ComputeManagementClient
import os
from datetime import datetime

def log_result(log_filename, vm_name, cve, solution, script, result=None, error=None):
    os.makedirs('logs', exist_ok=True)
    log_dir = os.path.join("..", "logs")
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

def run():
    subscription_id = "47444342-5807-4fb9-bd2a-04e628a01966"
    tenant_id = "89f9dc47-f591-4759-a287-3b2fe3deca27"
    client_id = "4032f3bb-7f2a-456a-899c-746f2c3426bb"
    client_secret = ".Hl8Q~PzMp.EN0zBj2RDOme8BJG31d2RcZcridc."

    creds = ClientSecretCredential(tenant_id, client_id, client_secret)
    compute_client = ComputeManagementClient(creds, subscription_id)

    df = pd.read_excel("VMs.xlsx")

    current_time = datetime.now().isoformat(timespec='seconds').replace(":", "-")
    log_filename = f"{current_time}.log"

    for _, row in df.iterrows():
        
        rg = 'vm-rg-1'
        updated_version = row['Version']
        vm_name = row['vm_name']
        cve = row['cve']
        solution = row['solution_summary']
        command = row['command']
        os = row['os_type']
        os_type = 'Linux'

        command_lines = command.splitlines()

        vm = compute_client.virtual_machines.get(rg, vm_name)        

        if (os_type.lower() == "linux"):
            script = {
                'command_id': 'RunShellScript',
                'script': command_lines
            }
        elif os_type.lower() == "windows":
            script = {
                'command_id': 'RunPowerShellScript',
                'script': command_lines
            }
        else:
            print(f"Unsupported OS: {os_type}")
            continue

        script =  {
            'commandId': 'RunShellScript',
            'script': command_lines
        }

        try:
            poller = compute_client.virtual_machines.begin_run_command(rg, vm_name, script)
            result = poller.result()
            log_result(log_filename, vm_name, cve, solution, command, result=result, error=None)
        except Exception as e:
            log_result(log_filename, vm_name, cve, solution, command, result=None, error=e)
            continue

if __name__ == "__main__":
    run()
