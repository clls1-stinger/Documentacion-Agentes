import sqlite3
import json
from pathlib import Path

N8N_DB = Path.home() / ".n8n" / "database.sqlite"
EXEC_ID = 429

def inspect():
    conn = sqlite3.connect(N8N_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT data FROM execution_data WHERE executionId = ?", (EXEC_ID,))
    res = cursor.fetchone()
    if not res:
        print(f"❌ No data found for execution {EXEC_ID}")
        return
    raw_data = res[0]
    data = json.loads(raw_data)
    
    # Check node execution order
    # In some versions of n8n, it's inside resultData
    order = data.get('executionData', {}).get('nodeExecutionOrder', [])
    if not order and isinstance(data, list):
         # Handle list format
         for item in data:
             if isinstance(item, dict) and 'lastNodeExecuted' in item:
                 print(f"Last node executed: {item['lastNodeExecuted']}")
    
    print(f"Node execution order: {order}")

if __name__ == "__main__":
    inspect()
