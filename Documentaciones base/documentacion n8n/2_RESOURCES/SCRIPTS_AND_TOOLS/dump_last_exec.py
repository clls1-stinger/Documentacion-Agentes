import sqlite3
import json
import sys
from pathlib import Path

N8N_DB = Path.home() / ".n8n" / "database.sqlite"

def dump_exec(exec_id=None):
    conn = sqlite3.connect(N8N_DB)
    cursor = conn.cursor()
    if exec_id:
        cursor.execute("SELECT e.id, ed.data FROM execution_entity e JOIN execution_data ed ON e.id = ed.executionId WHERE e.id = ?", (exec_id,))
    else:
        cursor.execute("SELECT e.id, ed.data FROM execution_entity e JOIN execution_data ed ON e.id = ed.executionId ORDER BY e.id DESC LIMIT 1")
    
    result = cursor.fetchone()
    conn.close()
    
    if result:
        eid, data = result
        path = f"/home/emky/n8n/documentacion/FORENSICS_AND_LOGS/raw_exec_{eid}.json"
        with open(path, "w") as f:
            f.write(data)
        print(f"Dumped execution {eid} to {path}")
    else:
        print(f"Execution {exec_id if exec_id else 'latest'} not found")

if __name__ == "__main__":
    eid = sys.argv[1] if len(sys.argv) > 1 else None
    dump_exec(eid)
