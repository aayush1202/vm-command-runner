import pandas as pd
import sys
from azure.identity import ClientSecretCredential
from azure.mgmt.compute import ComputeManagementClient
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from llm_agents import command_generator_agent

def run():
    subscription_id = "47444342-5807-4fb9-bd2a-04e628a01966"
    tenant_id = "89f9dc47-f591-4759-a287-3b2fe3deca27"
    client_id = "cc307fff-d83c-4afe-b24f-ca3d9f5142cc"
    client_secret = "qBS8Q~m7B1BvB4SdIrrNWzLW-KaR~EouvHZk6aTj"

    creds = ClientSecretCredential(tenant_id, client_id, client_secret)
    compute_client = ComputeManagementClient(creds, subscription_id)

    df = pd.read_excel("VMs.xlsx")

    

    bash_command = f"""bash -c "$(cat <<'EOF'
    {command}
    EOF
    )"
    """

    for _, row in df.iterrows():
        
        rg = 'vm-rg-1'
        vm_name = row["VMName"]
        os_type = row['OS']
        package = row['Package']
        updated_version = row['Version']
        
        command = command_generator_agent.generate_script(package=package, updated_version=updated_version, os_type=os_type)

        command_lines = command.splitlines()

        vm = compute_client.virtual_machines.get(rg, vm_name)        

        if (os_type.lower() == "linux") or (os_type.lower() == "ubuntu") or (os_type.lower() == "debian") or (os_type.lower() == "redhat"):
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

        poller = compute_client.virtual_machines.begin_run_command(rg, vm_name, script)
        result = poller.result()
        print(result.value[0].message if result.value else "No output")

if __name__ == "__main__":
    run()
