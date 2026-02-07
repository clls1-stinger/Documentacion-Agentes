import json

NODES_FILE = "/home/emky/n8n/documentacion/3_WORK_LOGS_AND_HISTORY/FORENSICS_AND_LOGS/current_nodes.json"

def inspect_nodes():
    try:
        with open(NODES_FILE, 'r', encoding='utf-8') as f:
            nodes = json.load(f)
            
        for node in nodes:
            if node.get('name') == 'Save to Disk' or node.get('name') == 'Drive Download':
                print(f"--- Node: {node.get('name')} ({node.get('type')}) ---")
                print(json.dumps(node.get('parameters', {}), indent=2))

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    inspect_nodes()
