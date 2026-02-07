import sqlite3
import os
import json

conn = sqlite3.connect(os.path.expanduser('~/.n8n/database.sqlite'))
cursor = conn.cursor()
cursor.execute('SELECT data FROM execution_data ORDER BY executionId DESC LIMIT 1')
raw = cursor.fetchone()[0]
data = json.loads(raw)

if isinstance(data, list):
    node_names = set()
    for entry in data:
        if isinstance(entry, dict):
            res = entry.get('resultData', {})
            if isinstance(res, str): res = json.loads(res)
            run = res.get('runData', {})
            for k in run.keys():
                node_names.add(k)
    print("Nodes found in execution:", sorted(list(node_names)))
else:
    print("Data is not a list. Type:", type(data))
