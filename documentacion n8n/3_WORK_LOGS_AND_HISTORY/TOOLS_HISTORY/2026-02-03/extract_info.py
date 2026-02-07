import json
import os

filepath = "/home/emky/n8n/workflow_nodes.json"
if os.path.exists(filepath):
    with open(filepath, 'r') as f:
        content = f.read()
        try:
            nodes = json.loads(content)
            for node in nodes:
                if node.get('name') == 'Clean Actor':
                    print("--- CLEAN ACTOR CODE ---")
                    print(node['parameters'].get('jsCode', 'No jsCode found'))
                    print("------------------------")
                if node.get('name') == 'Tool Router':
                    print("--- TOOL ROUTER RULES ---")
                    print(json.dumps(node['parameters'].get('rules', {}), indent=2))
                    print("-------------------------")
                if node.get('name') == 'Drive Search':
                    print("--- DRIVE SEARCH PARAMS ---")
                    print(json.dumps(node['parameters'], indent=2))
                    print("---------------------------")
        except Exception as e:
            print(f"Error: {e}")
