import json

with open('/home/emky/n8n/current_workflow.json', 'r') as f:
    nodes = json.load(f)

for node in nodes:
    name = node.get('name')
    if name in ['Clean Actor', 'Aggregator', 'Update State', 'Aggregate Results']:
        print(f"\n--- Node: {name} ({node.get('type')}) ---")
        
        # Check for JS Code
        params = node.get('parameters', {})
        js = params.get('jsCode') or params.get('code', {}).get('js')
        if js:
            print(">>> JS CODE:")
            print(js)
        else:
            print(">>> Configuration:")
            print(json.dumps(params, indent=2))
