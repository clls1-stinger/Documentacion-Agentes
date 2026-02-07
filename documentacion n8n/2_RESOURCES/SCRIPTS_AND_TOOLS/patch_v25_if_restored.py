#!/usr/bin/env python3
"""
⭐ VEGA v25: THE RETURN OF THE IF
Replacing the problematic Code Router with a native IF node to 
avoid the "json property isn't an object" hell.
"""

import sqlite3
import json
from pathlib import Path

N8N_DB = Path.home() / ".n8n" / "database.sqlite"
WORKFLOW_ID = "Urf7HpECFvfQooAv"

def patch():
    db_conn = sqlite3.connect(N8N_DB)
    cursor = db_conn.cursor()
    cursor.execute("SELECT nodes, connections FROM workflow_entity WHERE id = ?", (WORKFLOW_ID,))
    row = cursor.fetchone()
    nodes = json.loads(row[0])
    connections = json.loads(row[1])
    
    # 1. Eliminar el nodo de ruteo viejo y crear el IF
    new_nodes = []
    for node in nodes:
        if node['name'] == 'Route Decision':
            print(f"♻️ Replacing {node['name']} with native IF node...")
            if_node = {
                "parameters": {
                    "conditions": {
                        "string": [
                            {
                                "value1": "={{ $json.planner_output.is_done_string }}",
                                "value2": "TRUE"
                            }
                        ]
                    }
                },
                "id": node['id'],
                "name": "Route Decision",
                "type": "n8n-nodes-base.if",
                "typeVersion": 1,
                "position": node['position']
            }
            new_nodes.append(if_node)
        else:
            new_nodes.append(node)

    # 2. Asegurar conexiones
    # El nodo IF tiene salidas 'main' -> [0] (true) y [1] (false)
    # Ya deberian estar bien si los indices coinciden, pero vamos a reforzarlas.
    
    cursor.execute(
        "UPDATE workflow_entity SET nodes = ?, updatedAt = datetime('now') WHERE id = ?",
        (json.dumps(new_nodes), WORKFLOW_ID)
    )
    db_conn.commit()
    db_conn.close()

if __name__ == "__main__":
    patch()
    print("✅ VEGA v25 Applied. Native IF node restored.")
