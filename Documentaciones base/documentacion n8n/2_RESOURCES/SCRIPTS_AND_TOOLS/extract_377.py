import json

with open('exec_377.json', 'r') as f:
    data = json.load(f)

print(f"Data type: {type(data)}")

# If n8n data is a list of entries
if isinstance(data, list):
    for entry in data:
        if not isinstance(entry, dict): continue
        res = entry.get('resultData', {})
        if isinstance(res, str): res = json.loads(res)
        run = res.get('runData', {})
        
        for name, runs in run.items():
            if 'Planner' in name or 'Init Context' in name:
                print(f"\n=== Node: {name} ===")
                # Print the last run's output
                if runs:
                    out = runs[-1].get('data', {}).get('main', [[]])[0]
                    if out:
                        print(json.dumps(out[0].get('json', {}), indent=2))
else:
    print("Not a list")
