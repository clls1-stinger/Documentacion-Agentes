import sqlite3
import json
import os

conn = sqlite3.connect(os.path.expanduser('~/.n8n/database.sqlite'))
cursor = conn.cursor()
cursor.execute('SELECT nodes FROM workflow_entity WHERE id="Urf7HpECFvfQooAv"')
nodes = json.loads(cursor.fetchone()[0])
for n in nodes:
    if n['name'] == 'Route Decision':
        print(json.dumps(n, indent=2))
