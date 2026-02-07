import sqlite3
import os
import json

conn = sqlite3.connect(os.path.expanduser('~/.n8n/database.sqlite'))
cursor = conn.cursor()
cursor.execute('SELECT data FROM execution_data ORDER BY executionId DESC LIMIT 1')
raw = cursor.fetchone()[0]
data = json.loads(raw)

found = False
for entry in data:
    if not isinstance(entry, dict): continue
    res = entry.get('resultData', {})
    if isinstance(res, str): 
        try: res = json.loads(res)
        except: continue
    run = res.get('runData', {})
    if 'Init Context' in run:
        print("--- Init Context Trace ---")
        print(json.dumps(run['Init Context'][0]['data']['main'][0][0]['json'], indent=2))
        found = True
    if 'Parse Planner' in run:
        print("--- Parse Planner Trace ---")
        print(json.dumps(run['Parse Planner'][0]['data']['main'][0][0]['json'], indent=2))
        found = True

if not found:
    print("No relevant nodes found in this execution chunk.")
