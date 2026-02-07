#!/usr/bin/env python3
"""
🔧 EMERGENCY ROLLBACK - Revert v8
El parche v8 rompió el workflow completamente.
Volvemos a v7 y documentamos el problema.
"""

import sqlite3
import json
from pathlib import Path

N8N_DB = Path.home() / ".n8n" / "database.sqlite"
WORKFLOW_ID = "Urf7HpECFvfQooAv"

def rollback():
    conn = sqlite3.connect(N8N_DB)
    cursor = conn.cursor()
    
    # Restaurar nodes a v7
    cursor.execute("SELECT nodes FROM workflow_entity WHERE id = ?", (WORKFLOW_ID,))
    nodes = json.loads(cursor.fetchone()[0])
    
    for node in nodes:
        if node['name'] == 'Is Done Switch':
            print("   🔙 Reverting 'Is Done Switch' to v7...")
            node['parameters']['rules'] = {
                "values": [
                    {
                        "conditions": {
                            "conditions": [
                                {
                                    "leftValue": "={{ $json.planner_output.is_done_string }}",
                                    "operator": {
                                        "type": "string",
                                        "operation": "equals"
                                    },
                                    "rightValue": "TRUE"
                                }
                            ]
                        }
                    }
                ]
            }
            node['parameters']['options'] = {
                "fallbackOutput": "extra"
            }
    
    # Restaurar conexiones originales
    cursor.execute("SELECT connections FROM workflow_entity WHERE id = ?", (WORKFLOW_ID,))
    conns = json.loads(cursor.fetchone()[0])
    
    switch_conns = conns.get('Is Done Switch', {})
    # Asegurar orden original: [Final Response, Actor Prep]
    switch_conns['main'] = [
        [{"node": "Final Response", "type": "main", "index": 0}],
        [{"node": "Actor Prep", "type": "main", "index": 0}]
    ]
    
    print("   ✅ Restored connections:")
    print(f"      Puerto 0 → {switch_conns['main'][0]}")
    print(f"      Puerto 1 → {switch_conns['main'][1]}")
    
    cursor.execute("UPDATE workflow_entity SET nodes = ?, connections = ?, updatedAt = datetime('now') WHERE id = ?", 
                  (json.dumps(nodes), json.dumps(conns), WORKFLOW_ID))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    rollback()
    print("\n✅ Rolled back to v7. HAZ F5.")
    print("\n⚠️ The Switch bug persists. v8 caused worse problems.")
    print("🤔 Next approach: Try using an IF node instead of Switch.")
