import sqlite3
import json
import os

conn = sqlite3.connect(os.path.expanduser('~/.n8n/database.sqlite'))
cursor = conn.cursor()
cursor.execute('SELECT data FROM execution_data WHERE executionId = 379')
raw = cursor.fetchone()[0]
data = json.loads(raw)

# data is a list of entries
print(f"Total entries: {len(data)}")

# Create a map to decode strings
string_table = {}
# Usually indices are strings or small dicts. 
# n8n sometimes uses a dictionary at the start to map strings to IDs to save space.

def get_actual_data(val):
    if isinstance(val, str) and val.isdigit():
        idx = int(val)
        if idx < len(data):
            return data[idx]
    return val

for i, entry in enumerate(data):
    if not isinstance(entry, dict): continue
    
    # Check if it has runData
    res_data = entry.get('resultData')
    if res_data:
        # If it's a pointer to another entry
        actual_res = get_actual_data(res_data)
        if isinstance(actual_res, dict):
            run_data = actual_res.get('runData')
            if run_data:
                actual_run = get_actual_data(run_data)
                if isinstance(actual_run, dict):
                    for node_name, runs in actual_run.items():
                        if any(k in node_name for k in ['Planner', 'Actor', 'Drive', 'Router']):
                            print(f"\nNode: {node_name}")
                            for run in runs:
                                # run is a pointer?
                                actual_run_val = get_actual_data(run)
                                if isinstance(actual_run_val, dict):
                                    main = actual_run_val.get('data', {}).get('main', [])
                                    if main:
                                        # main is list of channels
                                        for channel in main:
                                            actual_channel = get_actual_data(channel)
                                            if isinstance(actual_channel, list):
                                                for item in actual_channel:
                                                    actual_item = get_actual_data(item)
                                                    if isinstance(actual_item, dict):
                                                        json_data = actual_item.get('json', {})
                                                        actual_json = get_actual_data(json_data)
                                                        print(json.dumps(actual_json, indent=2))
                                            elif isinstance(actual_channel, str) and actual_channel.isdigit():
                                                # List might be pointed to
                                                list_data = get_actual_data(actual_channel)
                                                for item in list_data:
                                                    actual_item = get_actual_data(item)
                                                    print(json.dumps(actual_item.get('json', {}), indent=2))

