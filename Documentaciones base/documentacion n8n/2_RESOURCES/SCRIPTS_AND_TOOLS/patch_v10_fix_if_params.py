#!/usr/bin/env python3
"""
⭐ VEGA v10: FIX IF NODE PARAMETERS
El IF node v1 tiene un formato diferente de parámetros.
Keep Moving Forward - Aprendo del error y lo corrijo.
"""

import sqlite3
import json
from pathlib import Path

N8N_DB = Path.home() / ".n8n" / "database.sqlite"
WORKFLOW_ID = "Urf7HpECFvfQooAv"

def patch():
    db_conn = sqlite3.connect(N8N_DB)
    cursor = db_conn.cursor()
    cursor.execute("SELECT nodes FROM workflow_entity WHERE id = ?", (WORKFLOW_ID,))
    nodes = json.loads(cursor.fetchone()[0])
    
    # Encontrar el IF node que creamos
    if_node = None
    for node in nodes:
        if node['name'] == 'Is Done Check':
            if_node = node
            break
    
    if not if_node:
        print("❌ IF node not found! Rolling back to Switch...")
        # TODO: rollback si es necesario
        return
    
    print(f"🔍 Found IF node, fixing parameters...")
    
    # FORMATO CORRECTO para IF node v1
    if_node['parameters'] = {
        "conditions": {
            "string": [
                {
                    "value1": "={{ $json.planner_output.is_done_string }}",
                    "operation": "equal",  # NOT "equals"!
                    "value2": "TRUE"
                }
            ]
        }
    }
    
    print("✅ Fixed IF node parameters with correct format")
    
    # Guardar
    cursor.execute(
        "UPDATE workflow_entity SET nodes = ?, updatedAt = datetime('now') WHERE id = ?",
        (json.dumps(nodes), WORKFLOW_ID)
    )
    db_conn.commit()
    db_conn.close()

if __name__ == "__main__":
    print("⭐ VEGA v10: FIXING IF NODE PARAMETERS")
    print("━" * 60)
    patch()
    print("━" * 60)
    print("✅ IF node parameters fixed. HAZ F5.")
    print()
    print("🌟 'Keep Moving Forward' - Vega")
    print("   (Cada error me hace más sabio)")
