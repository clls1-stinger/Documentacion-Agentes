import json

with open('exec_379_raw.json', 'r') as f:
    data = json.load(f)

# The structure is often:
# data[4] = { "When chat message received": "12", "Read History": "13", "Init Context": "14", ... }
# Then indices are positions in the list

node_map = None
for item in data:
    if isinstance(item, dict) and "Init Context" in item:
        node_map = item
        break

if node_map:
    # Init Context's pointer is in node_map["Init Context"]
    ptr = node_map["Init Context"]
    print(f"Init Context pointer: {ptr}")
    # Usually this points to a dictionary describing the run
    run_info = data[int(ptr)]
    # run_info has "data" and "startTime" etc.
    # Usually data pointers are strings too
    # Let's just print a chunk of the list around that ptr
    start_search = int(ptr)
    for j in range(start_search, start_search + 50):
        if j < len(data):
            print(f"Index {j}: {str(data[j])[:200]}")
else:
    print("Node map not found")
