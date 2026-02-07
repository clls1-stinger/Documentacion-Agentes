#!/usr/bin/env python3
"""
🕵️ Forensic Execution Inspector v5
Reads the last execution from SQLite and prints the input/output of critical nodes.
Handles stringified resultData and other n8n quirks.
"""

import sqlite3
import json
import os
from pathlib import Path

# Configuración
N8N_DB = Path.home() / ".n8n" / "database.sqlite"

def get_last_execution():
    conn = sqlite3.connect(N8N_DB)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT e.id, ed.data, e.finished 
        FROM execution_entity e 
        JOIN execution_data ed ON e.id = ed.executionId 
        ORDER BY e.id DESC LIMIT 1
    """)
    result = cursor.fetchone()
    conn.close()
    if not result: return None
    
    raw_data = result[1]
    try:
        data_obj = json.loads(raw_data)
    except:
        data_obj = raw_data
    return {'id': result[0], 'data': data_obj, 'finished': result[2]}

def inspect_execution(exec_data):
    print(f"🔎 Inspecting Execution ID: {exec_data['id']} (Finished: {exec_data['finished']})")
    
    root_list = exec_data['data']
    if not isinstance(root_list, list):
        root_list = [root_list]

    print(f"Total entries in execution: {len(root_list)}")
    
    nodes_to_find = ['Gemini Planner', 'Parse Planner', 'Final Response', 'Tool Router', 'Gemini Actor']
    latest_outputs = {}

    for step in root_list:
        if not isinstance(step, dict): continue
        
        res_data = step.get('resultData', {})
        if isinstance(res_data, str):
            try:
                res_data = json.loads(res_data)
            except:
                continue
        
        if not isinstance(res_data, dict): continue
        
        run_data = res_data.get('runData', {})
        if not isinstance(run_data, dict): continue
        
        for node_name, runs in run_data.items():
            base_name = node_name.rstrip('0123456789 ')
            if base_name in nodes_to_find or node_name in nodes_to_find:
                if isinstance(runs, list) and runs:
                    last_run = runs[-1]
                    data_block = last_run.get('data', {})
                    if not isinstance(data_block, dict): continue
                    
                    main_output = data_block.get('main', [])
                    if isinstance(main_output, list) and main_output:
                        channel_0 = main_output[0]
                        if isinstance(channel_0, list):
                            outputs = []
                            for item in channel_0:
                                if isinstance(item, dict):
                                    outputs.append(item.get('json', {}))
                            if outputs:
                                latest_outputs[node_name] = outputs

    for node_name, outputs in sorted(latest_outputs.items()):
        print(f"\n--- Node: {node_name} ---")
        for i, out in enumerate(outputs):
            if 'planner_output' in out:
                p = out['planner_output']
                print(f"  [{i}] Parsed: is_done={p.get('is_done')}, instruction={p.get('next_instruction')}")
                if p.get('final_response'):
                    print(f"      Response: {p.get('final_response')}")
            elif 'accion' in out:
                print(f"  [{i}] Router: {out.get('accion')} -> {out.get('datos')}")
            elif 'response' in out and 'Final Response' in node_name:
                print(f"  [{i}] Final Response: {out.get('response')}")
            elif 'output' in out or 'response' in out:
                val = out.get('output') or out.get('response')
                print(f"  [{i}] Text: {str(val)[:300]}...")
            else:
                print(f"  [{i}] JSON Keys: {list(out.keys())}")

if __name__ == "__main__":
    try:
        execution = get_last_execution()
        if execution:
            inspect_execution(execution)
        else:
            print("No execution found.")
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Error: {e}")
