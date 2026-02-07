import json
import os

filepath = "/home/emky/n8n/workflow_nodes.json"
if os.path.exists(filepath):
    with open(filepath, 'r') as f:
        content = f.read()
        try:
            nodes = json.loads(content)
            for node in nodes:
                if node.get('name') == 'Tool Router':
                    print("--- TOOL ROUTER FULL PARAMS ---")
                    print(json.dumps(node, indent=2))
                    print("-------------------------")
        except Exception as e:
            print(f"Error: {e}")
