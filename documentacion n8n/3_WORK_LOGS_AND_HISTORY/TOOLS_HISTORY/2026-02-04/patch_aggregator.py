import json
import os

# Configuration
WORKFLOW_ID = "osenZpfZMpCRQBSL"
WORKFLOW_DIR = "/home/emky/n8n/workflows_antigravity"
AGGREGATOR_CODE_PATH = "/home/emky/n8n/documentacion/3_WORK_LOGS_AND_HISTORY/FORENSICS_AND_LOGS/aggregator_code.js"
OUTPUT_FILE = "patched_workflow.json"

def load_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def find_workflow_file(directory, workflow_id):
    for filename in os.listdir(directory):
        if filename.endswith(".json"):
            path = os.path.join(directory, filename)
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if data.get('id') == workflow_id:
                        return path
            except Exception:
                continue
    return None

def patch_workflow():
    print(f"Searching for workflow ID {WORKFLOW_ID} in {WORKFLOW_DIR}...")
    workflow_path = find_workflow_file(WORKFLOW_DIR, WORKFLOW_ID)
    
    if not workflow_path:
        print(f"Error: Workflow with ID {WORKFLOW_ID} not found.")
        return

    print(f"Found workflow file: {workflow_path}")
    
    try:
        # Load workflow
        with open(workflow_path, 'r', encoding='utf-8') as f:
            workflow = json.load(f)
            
        # Load new code
        new_code = load_file(AGGREGATOR_CODE_PATH)
        
        # Patch Aggregator Node
        patched = False
        for node in workflow.get('nodes', []):
            if node.get('name') == 'Aggregator' and node.get('type') == 'n8n-nodes-base.code':
                print("Found Aggregator node. Updating jsCode...")
                node['parameters']['jsCode'] = new_code
                patched = True
                break
        
        if patched:
            with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
                json.dump(workflow, f, indent=2)
            print(f"Success! Patched workflow saved to {OUTPUT_FILE}")
        else:
            print("Error: Aggregator node not found in workflow.")

    except Exception as e:
        print(f"Error patching workflow: {e}")

if __name__ == "__main__":
    patch_workflow()
