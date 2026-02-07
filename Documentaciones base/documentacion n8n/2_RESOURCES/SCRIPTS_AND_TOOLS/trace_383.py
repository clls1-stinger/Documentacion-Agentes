import json
import sys

with open('exec_383_raw.json', 'r') as f:
    data = json.load(f)

node_map = data[4]

def get_actual(ptr):
    try:
        return data[int(ptr)]
    except:
        return ptr

def print_node_output(node_name):
    print(f"\n--- {node_name} ---")
    ptr = node_map.get(node_name)
    if not ptr: 
        print("Node not found in execution map.")
        return
    runs = get_actual(ptr)
    if not isinstance(runs, list):
        print(f"Unexpected run data type: {type(runs)}")
        return
        
    for r in runs:
        run_info = get_actual(r)
        d_ptr = run_info.get('data')
        if not d_ptr: continue
        actual_data = get_actual(d_ptr)
        main_ptr = actual_data.get('main')
        if not main_ptr: continue
        ch = get_actual(main_ptr)
        if not ch: continue
        items_ptr = ch[0]
        items = get_actual(items_ptr)
        if not isinstance(items, list): continue
        
        for item_ptr in items:
            item = get_actual(item_ptr)
            j_ptr = item.get('json')
            actual_json = get_actual(j_ptr)
            if node_name == "Gemini Planner":
                resp = actual_json.get('response')
                print(f"Response: {get_actual(resp)}")
            elif node_name == "Parse Planner":
                out = actual_json.get('planner_output')
                print(f"Parsed: {json.dumps(get_actual(out), indent=2)}")
            elif node_name == "Final Response":
                resp = actual_json.get('response')
                print(f"Final Response: {resp}")
            elif node_name == "Is Done Switch":
                p_out = actual_json.get('planner_output', {})
                print(f"Switch Input planner_output: {json.dumps(get_actual(p_out), indent=2)}")

nodes_to_check = ["Gemini Planner", "Parse Planner", "Is Done Switch", "Final Response"]
for node in nodes_to_check:
    print_node_output(node)
