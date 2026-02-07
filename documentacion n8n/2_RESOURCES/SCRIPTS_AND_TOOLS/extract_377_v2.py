import json

with open('exec_377.json', 'r') as f:
    data = json.load(f)

for i, entry in enumerate(data):
    if not isinstance(entry, dict):
        # print(f"Entry {i} is {type(entry)}")
        continue
    
    node_name = entry.get('node')
    if not node_name: continue
    
    if 'Planner' in node_name or 'Init Context' in node_name or 'Final Response' in node_name:
        print(f"\n--- Entry {i}: Node {node_name} ---")
        res_data = entry.get('resultData', {})
        if isinstance(res_data, str):
            try: res_data = json.loads(res_data)
            except: pass
            
        if isinstance(res_data, dict):
            run_data = res_data.get('runData', {})
            # n8n sometimes has runData in the root of resultData, or resultData itself is runData
            if not run_data and node_name in res_data:
                run_data = res_data
            
            node_runs = run_data.get(node_name, [])
            if node_runs:
                last_run = node_runs[-1]
                data_block = last_run.get('data', {})
                main_output = data_block.get('main', [])
                if main_output and main_output[0]:
                    print(json.dumps(main_output[0][0].get('json', {}), indent=2))
        else:
            print(f"ResultData is {type(res_data)}: {res_data}")
