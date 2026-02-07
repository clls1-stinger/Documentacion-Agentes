import json
import os

path = '/home/emky/n8n/documentacion/last_exec_raw.json'
if os.path.exists(path):
    with open(path, 'r') as f:
        data = json.load(f)
    
    # Flatten the list if it's a list
    if isinstance(data, list):
        for entry in reversed(data):
            if isinstance(entry, dict):
                res = entry.get('resultData', {})
                if isinstance(res, str): 
                    try: res = json.loads(res)
                    except: continue
                run = res.get('runData', {})
                if 'Gemini Planner' in run:
                   planner_out = run['Gemini Planner'][-1]['data']['main'][0][0]['json']
                   print(f"Node: {entry.get('node')}")
                   print(f"Planner Output: {planner_out.get('output', planner_out.get('response'))}")
                   break
EOF
