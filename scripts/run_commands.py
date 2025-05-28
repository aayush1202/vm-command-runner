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

    command = command_generator_agent.generate_script(package="python",  current_version="3.11.9", updated_version="3.12.10", os_type='Linux')

    bash_command = f"""bash -c "$(cat <<'EOF'
    {command}
    EOF
    )"
    """

    for _, row in df.iterrows():
        
        rg = row["ResourceGroup"]
        vm_name = row["VMName"]

        vm = compute_client.virtual_machines.get(rg, vm_name)
        os_type = vm.storage_profile.os_disk.os_type

        if os_type is None:
            print(f"VM {vm_name} does not have an OS type.")
            continue

        print(f"Running on {vm_name} ({os_type})...")

        if os_type.lower() == "linux":
            script = {
                'command_id': 'RunShellScript',
                'script': [command]
            }
        elif os_type.lower() == "windows":
            script = {
                'command_id': 'RunPowerShellScript',
                'script': [command]
            }
        else:
            print(f"Unsupported OS: {os_type}")
            continue

        poller = compute_client.virtual_machines.begin_run_command(rg, vm_name, script)
        result = poller.result()
        print(result.value[0].message if result.value else "No output")

if __name__ == "__main__":
    run()
