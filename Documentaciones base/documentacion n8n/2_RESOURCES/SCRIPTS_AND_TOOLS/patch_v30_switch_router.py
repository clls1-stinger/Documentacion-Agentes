
import json
import os

DUMP_PATH = "/home/emky/n8n/documentacion/FORENSICS_AND_LOGS/workflow_yes_dump.json"
PATCHED_PATH = "/home/emky/n8n/documentacion/FORENSICS_AND_LOGS/workflow_yes_patched_v30.json"

def patch_workflow():
    with open(DUMP_PATH, 'r') as f:
        data = json.load(f)
    
    nodes = data['nodes']
    found = False
    for node in nodes:
        if node['name'] == "Route Decision":
            print(f"Patching node: {node['name']}")
            node['type'] = "n8n-nodes-base.switch"
            node['typeVersion'] = 3.2
            node['parameters'] = {
                "rules": {
                    "values": [
                        {
                            "conditions": {
                                "conditions": [
                                    {
                                        "leftValue": "={{ $json.planner_output.is_done_string }}",
                                        "operator": {
                                            "type": "string",
                                            "operation": "equals"
                                        },
                                        "rightValue": "TRUE"
                                    }
                                ]
                            }
                        },
                        {
                            "conditions": {
                                "conditions": [
                                    {
                                        "leftValue": "={{ $json.planner_output.is_done_string }}",
                                        "operator": {
                                            "type": "string",
                                            "operation": "equals"
                                        },
                                        "rightValue": "FALSE"
                                    }
                                ]
                            }
                        }
                    ]
                },
                "options": {
                    "fallbackOutput": 1
                }
            }
            found = True
            break
    
    if not found:
        print("❌ Could not find Route Decision node")
        return

    with open(PATCHED_PATH, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"✅ Patched workflow saved to {PATCHED_PATH}")

if __name__ == "__main__":
    patch_workflow()
