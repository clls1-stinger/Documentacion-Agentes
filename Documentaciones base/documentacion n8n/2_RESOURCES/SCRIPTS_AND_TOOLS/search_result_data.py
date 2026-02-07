import sqlite3
import json
import os

N8N_DB = os.path.expanduser('~/.n8n/database.sqlite')
conn = sqlite3.connect(N8N_DB)
cursor = conn.cursor()
cursor.execute("SELECT data FROM execution_data ORDER BY executionId DESC LIMIT 1")
data_str = cursor.fetchone()[0]
conn.close()

data = json.loads(data_str)

if isinstance(data, list):
    for i, item in enumerate(data):
        if isinstance(item, dict) and 'resultData' in item:
            print(f"Index {i} has resultData")
            rd = item['resultData']
            if isinstance(rd, str):
                rd = json.loads(rd)
            run_data = rd.get('runData', {})
            print(f"Nodes in this index: {list(run_data.keys())}")
            
            # If we find Parse Planner, let's see its output
            if 'Parse Planner' in run_data:
                node_runs = run_data['Parse Planner']
                if node_runs:
                    last_run = node_runs[-1]
                    main_output = last_run.get('data', {}).get('main', [])
                    if main_output and main_output[0]:
                         print(f"Parse Planner Output: {json.dumps(main_output[0][0].get('json', {}), indent=2)}")
            
            if 'Final Response' in run_data:
                 print("Final Response node was reached in this index.")
else:
    print("Data is not a list")
