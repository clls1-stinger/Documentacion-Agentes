import sqlite3
import json
import os

conn = sqlite3.connect(os.path.expanduser('~/.n8n/database.sqlite'))
cursor = conn.cursor()
cursor.execute('SELECT data FROM execution_data WHERE executionId = 380')
raw = cursor.fetchone()[0]
data = json.loads(raw)

def get_val(ptr):
    try:
        idx = int(ptr)
        if idx < len(data): return data[idx]
    except: pass
    return ptr

node_map = None
for item in data:
    if isinstance(item, dict) and "When chat message received" in item:
        node_map = item
        break

if node_map:
    for node_name in ["Gemini Planner", "Parse Planner", "Init Context"]:
        ptr = node_map.get(node_name)
        if ptr:
            run_info = get_val(ptr)
            if isinstance(run_info, dict):
                data_ptr = run_info.get("data")
                if data_ptr:
                    actual_data = get_val(data_ptr)
                    if isinstance(actual_data, dict):
                        main_ptr = actual_data.get("main")
                        if main_ptr:
                            channels = get_val(main_ptr)
                            if isinstance(channels, list) and channels:
                                channel_ptr = channels[0]
                                items = get_val(channel_ptr)
                                if isinstance(items, list) and items:
                                    item = get_val(items[0])
                                    print(f"--- {node_name} Output ---")
                                    print(json.dumps(item.get("json", {}), indent=2))
else:
    print("Node map not found")
