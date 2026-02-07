import json

with open('exec_380_raw.json', 'r') as f:
    data = json.load(f)

def get_actual(v):
    if isinstance(v, str) and v.isdigit():
        return data[int(v)]
    return v

# Index 4 is the node map
node_map = data[4]

for node_name, pointer in node_map.items():
    print(f"\n--- Node: {node_name} ---")
    # Pointer is a list of run pointers
    run_pointers = data[int(pointer)]
    for rp in run_pointers:
        run_info = data[int(rp)]
        # run_info: { data: "...", executionStatus: "..." }
        data_ptr = run_info.get("data")
        if data_ptr:
            actual_data = data[int(data_ptr)]
            # { main: "..." }
            main_ptr = actual_data.get("main")
            if main_ptr:
                channels = data[int(main_ptr)]
                if channels and channels[0]:
                    items_ptr = channels[0]
                    items = data[int(items_ptr)]
                    for item_ptr in items:
                        item = data[int(item_ptr)]
                        # { json: "..." }
                        json_ptr = item.get("json")
                        actual_json = data[int(json_ptr)]
                        if node_name == "Parse Planner":
                            p = actual_json.get("planner_output", {})
                            print(f"  Parsed: is_done={p.get('is_done')}, msg={p.get('final_response')}")
                        elif node_name == "Is Done Switch":
                            print(f"  Switch Item: {actual_json}")
                        elif node_name == "Gemini Planner":
                            print(f"  Planner Output: {actual_json.get('output', actual_json.get('response'))}")
                        elif node_name == "Final Response":
                            print(f"  Response: {actual_json.get('response')}")
