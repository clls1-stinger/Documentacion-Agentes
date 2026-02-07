import sqlite3
import os
import json

conn = sqlite3.connect(os.path.expanduser('~/.n8n/database.sqlite'))
cursor = conn.cursor()
cursor.execute('SELECT executionId, data FROM execution_data ORDER BY executionId DESC LIMIT 1')
row = cursor.fetchone()
exec_id = row[0]
raw = row[1]
data = json.loads(raw)

print(f"Execution ID: {exec_id}")
print(f"Root Type: {type(data)}")

if isinstance(data, dict):
    print(f"Root Keys: {list(data.keys())}")
    if 'resultData' in data:
        rd = data['resultData']
        print(f"ResultData Keys: {list(rd.keys())}")
        if 'runData' in rd:
            print(f"RunData Nodes: {list(rd['runData'].keys())}")
elif isinstance(data, list):
    print(f"List length: {len(data)}")
    print(f"First element keys: {list(data[0].keys()) if len(data) > 0 else 'empty'}")
    # Often it's a list of node results
    nodes = set()
    for item in data:
        if isinstance(item, dict) and 'node' in item:
            nodes.add(item['node'])
    if nodes:
        print(f"Nodes found in list: {nodes}")

with open('last_exec_debug.json', 'w') as f:
    json.dump(data, f, indent=2)
