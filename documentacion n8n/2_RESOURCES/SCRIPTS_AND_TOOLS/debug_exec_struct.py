import sqlite3
import json
import os

N8N_DB = os.path.expanduser('~/.n8n/database.sqlite')
conn = sqlite3.connect(N8N_DB)
cursor = conn.cursor()
cursor.execute("SELECT executionId, workflowData, data FROM execution_data ORDER BY executionId DESC LIMIT 1")
row = cursor.fetchone()
conn.close()

if row:
    print(f"Execution ID: {row[0]}")
    data = json.loads(row[2])
    print(f"Type of data: {type(data)}")
    if isinstance(data, list):
        print(f"List length: {len(data)}")
        final_state = data[-1]
        print(f"Final element keys: {list(final_state.keys()) if isinstance(final_state, dict) else 'not a dict'}")
        if isinstance(final_state, dict) and 'resultData' in final_state:
             run_data = final_state['resultData'].get('runData', {})
             print(f"RunData nodes: {list(run_data.keys())}")
    elif isinstance(data, dict):
        print(f"Keys: {list(data.keys())}")
