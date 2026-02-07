import json

with open('exec_380_raw.json', 'r') as f:
    data = json.load(f)

def get_actual(v):
    if isinstance(v, str) and v.isdigit():
        return data[int(v)]
    if isinstance(v, list):
        return [get_actual(x) for x in v]
    if isinstance(v, dict):
        return {k: get_actual(v2) for k, v2 in v.items()}
    return v

# Index 4 is the node map
node_map = data[4]

for node_name, pointer in node_map.items():
    if node_name not in ["Gemini Planner", "Parse Planner", "Final Response", "Is Done Switch"]: continue
    print(f"\n--- Node: {node_name} ---")
    run_pointers = data[int(pointer)]
    for rp in run_pointers:
        run_info = data[int(rp)]
        data_ptr = run_info.get("data")
        if data_ptr:
            actual_data = data[int(data_ptr)]
            main_ptr = actual_data.get("main")
            if main_ptr:
                channels = data[int(main_ptr)]
                if channels and channels[0]:
                    items_ptr = channels[0]
                    items = data[int(items_ptr)]
                    for item_ptr in items:
                        item = data[int(item_ptr)]
                        json_ptr = item.get("json")
                        actual_json = get_actual(json_ptr)
                        print(json.dumps(actual_json, indent=2))
