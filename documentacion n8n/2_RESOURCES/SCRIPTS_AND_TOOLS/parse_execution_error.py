import sqlite3
import json
import os

conn = sqlite3.connect(os.path.expanduser('~/.n8n/database.sqlite'))
cursor = conn.cursor()
cursor.execute('SELECT data FROM execution_data WHERE executionId=405')
row = cursor.fetchone()
if row:
    data = json.loads(row[0])
    # data is a list [startData, resultData, executionData, contextData, ...]
    # executionData (index 2) often contains the error
    error = data[2].get('error')
    last_node = data[2].get('lastNodeExecuted')
    print(f"Failed Node: {last_node}")
    print(f"Error Message: {error}")
    
    # Let's see the trace if available
    run_data = data[2].get('runData', {})
    if last_node in run_data:
        node_runs = run_data[last_node]
        if node_runs:
            print(f"Last node run error: {node_runs[-1].get('error')}")
else:
    print("Execution data not found")
