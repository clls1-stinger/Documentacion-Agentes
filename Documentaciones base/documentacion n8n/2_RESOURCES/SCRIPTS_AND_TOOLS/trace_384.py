import json
import sys

with open('exec_384_raw.json', 'r') as f:
    data = json.load(f)

node_map = data[4]

def get_actual(ptr):
    try:
        if isinstance(ptr, str) and ptr.isdigit():
            return data[int(ptr)]
        return ptr
    except:
        return ptr

def print_node_output(node_name):
    print(f"\n--- {node_name} ---")
    ptr = node_map.get(node_name)
    if not ptr: return
    runs = get_actual(ptr)
    for r in runs:
        run_info = get_actual(r)
        d_ptr = run_info.get('data')
        if not d_ptr: continue
        actual_data = get_actual(d_ptr)
        main_ptr = actual_data.get('main')
        ch = get_actual(main_ptr)
        items_ptr = ch[0]
        items = get_actual(items_ptr)
        for item_ptr in items:
            item = get_actual(item_ptr)
            j_ptr = item.get('json')
            actual_json = get_actual(j_ptr)
            print(json.dumps(actual_json, indent=2))

print_node_output("Parse Planner")
print_node_output("Is Done Switch")
