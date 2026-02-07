import sqlite3
import json
import os

conn = sqlite3.connect(os.path.expanduser('~/.n8n/database.sqlite'))
cursor = conn.cursor()
cursor.execute('SELECT data FROM execution_data WHERE executionId = 380')
raw = cursor.fetchone()[0]
data = json.loads(raw)

nodes_executed = []
for entry in data:
    if isinstance(entry, dict) and entry.get('node'):
        nodes_executed.append(entry.get('node'))

print("Execution path:", " -> ".join(nodes_executed))
