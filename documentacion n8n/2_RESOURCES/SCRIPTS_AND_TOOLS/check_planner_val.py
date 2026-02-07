import sqlite3
import json
import os

conn = sqlite3.connect(os.path.expanduser('~/.n8n/database.sqlite'))
cursor = conn.cursor()
cursor.execute('SELECT data FROM execution_data WHERE executionId = 377')
raw = cursor.fetchone()[0]
data = json.loads(raw)

# Parse Planner output is at index 142
parse_planner_node_data = data[142]
planner_output_idx = int(parse_planner_node_data['planner_output'])
planner_output = data[planner_output_idx]

print("--- Planner Output (from Parse Planner) ---")
print(json.dumps(planner_output, indent=2))
print(f"is_done type: {type(planner_output.get('is_done'))}")
