import sqlite3
import json
import os

def resolve_n8n_data(data_list):
    # n8n uses a compression format where strings/objects are stored at the end
    # and referenced by index.
    # The structure is [obj_with_pointers, ..., strings_list]
    # We need to find the strings list (usually at the end of the root array)
    if not isinstance(data_list, list):
        return data_list
    
    # Typically the last elements are the reference pools
    # But let's look for the biggest arrays
    pools = [x for x in data_list if isinstance(x, list)]
    if not pools:
        return data_list
    
    # Simple recursive resolver for the common pointer structure
    def resolve(item, pool):
        if isinstance(item, str) and item.isdigit():
            idx = int(item)
            if idx < len(pool):
                return pool[idx]
        if isinstance(item, dict):
            return {k: resolve(v, pool) for k, v in item.items()}
        if isinstance(item, list):
            return [resolve(i, pool) for i in item]
        return item

    # Let's try to find which list is the pool (often the first large list at the end)
    # n8n data[0] is often the startData pointers
    # data[-1] is often one of the pools
    
    # Instead of full resolution, let's just dump the whole thing to a file 
    # and search for "error" content
    return data_list

conn = sqlite3.connect(os.path.expanduser('~/.n8n/database.sqlite'))
cursor = conn.cursor()
cursor.execute('SELECT data FROM execution_data WHERE executionId=405')
row = cursor.fetchone()
if row:
    # Write to a file for manual inspection if needed
    with open('/home/emky/n8n/documentacion/FORENSICS_AND_LOGS/raw_exec_405.json', 'w') as f:
        f.write(row[0])
    
    data = json.loads(row[0])
    
    # In n8n execution_data:
    # [startData, resultData, executionData, contextData, nodeData..., pools]
    # Let's find "error" string in the whole JSON
    raw_str = row[0]
    error_idx = raw_str.find('"error"')
    # Print surrounding context of "error"
    if error_idx != -1:
        print("--- CONTEXT AROUND 'error' ---")
        print(raw_str[error_idx-50:error_idx+500])
else:
    print("No data found")
