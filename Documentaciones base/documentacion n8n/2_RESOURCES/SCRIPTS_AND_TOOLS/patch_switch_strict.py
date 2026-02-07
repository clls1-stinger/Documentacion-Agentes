#!/usr/bin/env python3
import sqlite3
import json
import os
from pathlib import Path

N8N_DB = Path.home() / ".n8n" / "database.sqlite"
WORKFLOW_ID = "Urf7HpECFvfQooAv"

def patch_switch_strict():
    conn = sqlite3.connect(N8N_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT nodes FROM workflow_entity WHERE id = ?", (WORKFLOW_ID,))
    nodes = json.loads(cursor.fetchone()[0])
    
    patched = False
    for node in nodes:
        if node['name'] == 'Is Done Switch':
            print("Patcheando Is Done Switch (MODO ESTRICTO)...")
            # Usar operación 'equals' en lugar de simplemente 'true'
            node['parameters']['rules'] = {
                "values": [
                    {
                        "conditions": {
                            "conditions": [
                                {
                                    "leftValue": "={{ $json.planner_output.is_done }}",
                                    "operator": {
                                        "type": "boolean",
                                        "operation": "equals"
                                    },
                                    "rightValue": True
                                }
                            ]
                        }
                    }
                ]
            }
            patched = True

    if patched:
        cursor.execute("UPDATE workflow_entity SET nodes = ?, updatedAt = datetime('now') WHERE id = ?", 
                      (json.dumps(nodes), WORKFLOW_ID))
        conn.commit()
    conn.close()
    return patched

if __name__ == "__main__":
    if patch_switch_strict():
        print("✅ Switch en MODO ESTRICTO. Haz F5.")
    else:
        print("❌ No se encontró el nodo.")
