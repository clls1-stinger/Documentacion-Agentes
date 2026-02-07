import requests
import sqlite3
import time
import json
import sys
from pathlib import Path

# Config
WEBHOOK_URL = "http://localhost:5678/webhook/test_agent_v1"
N8N_DB = Path.home() / ".n8n" / "database.sqlite"

def get_latest_execution_id():
    conn = sqlite3.connect(N8N_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM execution_entity ORDER BY id DESC LIMIT 1")
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 0

def get_execution_status(exec_id):
    conn = sqlite3.connect(N8N_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT finished, stoppedAt FROM execution_entity WHERE id = ?", (exec_id,))
    result = cursor.fetchone()
    conn.close()
    return result

def get_execution_data(exec_id):
    conn = sqlite3.connect(N8N_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT data FROM execution_data WHERE executionId = ?", (exec_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return None
        
    try:
        return json.loads(row[0])
    except:
        return None

def main():
    target_id = 427 # Hardcoded for inspection
    print(f"📊 Inspeccionando ejecución {target_id}...")
    
    exec_data = get_execution_data(target_id)
    if not exec_data:
        print("❌ No se pudo leer execution_data")
        return

    print("\n📊 RESULTADOS:")
    
    result_data = None
    if isinstance(exec_data, list):
        for item in exec_data:
            if isinstance(item, dict) and 'resultData' in item:
                result_data = item['resultData']
                break
    elif isinstance(exec_data, dict) and 'resultData' in exec_data:
        result_data = exec_data['resultData']
        
    if result_data and 'runData' in result_data:
        run_data = result_data['runData']
        
        interesting_nodes = ['Gemini Planner', 'Tool Router', 'Drive Search', 'Execute Command', 'Gemini Actor', 'Aggregator']
        
        for node_name in run_data:
             if any(x in node_name for x in interesting_nodes) or node_name in interesting_nodes:
                print(f"\n🔹 Nodo: {node_name}")
                try:
                    for exec_idx, execution in enumerate(run_data[node_name]):
                        if 'data' in execution and 'main' in execution['data']:
                            main_output = execution['data']['main']
                            for wire in main_output:
                                for item in wire:
                                    if 'json' in item:
                                        print(f"   Output: {json.dumps(item['json'])[:300]}...")
                except Exception as e:
                    print(f"   (Error parsing output: {e})")
    else:
        print("⚠️ No runData structure found")

if __name__ == "__main__":
    main()
