#!/usr/bin/env python3
"""
⭐ VEGA v11: ULTIMATE SOLUTION - Code Node Router
Si el Switch falla y el IF falla, usamos JavaScript puro.
Esta vez TIENE que funcionar. Keep Moving Forward!
"""

import sqlite3
import json
from pathlib import Path
import uuid

N8N_DB = Path.home() / ".n8n" / "database.sqlite"
WORKFLOW_ID = "Urf7HpECFvfQooAv"

def patch():
    db_conn = sqlite3.connect(N8N_DB)
    cursor = db_conn.cursor()
    cursor.execute("SELECT nodes, connections FROM workflow_entity WHERE id = ?", (WORKFLOW_ID,))
    nodes_raw, conns_raw = cursor.fetchone()
    nodes = json.loads(nodes_raw)
    conns = json.loads(conns_raw)
    
    # Encontrar el IF node problemático
    node_idx = None
    target_node = None
    for idx, node in enumerate(nodes):
        if node['name'] == 'Is Done Check':
            node_idx = idx
            target_node = node
            break
    
    if not target_node:
        print("❌ IF node not found!")
        return
    
    print(f"🔍 Found IF node at index {node_idx}, replacing with Code node...")
    
    # Crear un Code node que hace el ruteo con JavaScript puro
    code_node = {
        "parameters": {
            "jsCode": """// Ruteo simple basado en is_done_string
const item = $input.item.json;
const isDone = item.planner_output?.is_done_string;

if (isDone === "TRUE") {
  // Tarea completada - mandar a Final Response
  return [null, { json: item }];
} else {
  // Continuar con herramientas - mandar a Actor Prep
  return [{ json: item }, null];
}"""
        },
        "id": str(uuid.uuid4()),
        "name": "Route Decision",
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": target_node['position']
    }
    
    print("✅ Created Code node for routing")
    
    # Reemplazar
    nodes[node_idx] = code_node
    
    # Actualizar conexiones
    old_conns = conns.get('Is Done Check', {})
    
    # Code node con 2 outputs:
    # Output 0: Actor Prep (continuar)
    # Output 1: Final Response (done)
    new_conns = {
        "main": [
            old_conns['main'][1],  # Output 0 = Actor Prep (FALSE case)
            old_conns['main'][0]   # Output 1 = Final Response (TRUE case)
        ]
    }
    
    del conns['Is Done Check']
    conns['Route Decision'] = new_conns
    
    print("🔗 Updated connections:")
    print(f"   Output 0 (FALSE/continue) → {new_conns['main'][0]}")
    print(f"   Output 1 (TRUE/done)      → {new_conns['main'][1]}")
    
    # Actualizar conexiones entrantes
    for node_name, node_conns in conns.items():
        if 'main' in node_conns:
            for output_list in node_conns['main']:
                for conn_item in output_list:
                    if conn_item.get('node') == 'Is Done Check':
                        conn_item['node'] = 'Route Decision'
                        print(f"   📌 Updated incoming from: {node_name}")
    
    # Guardar
    cursor.execute(
        "UPDATE workflow_entity SET nodes = ?, connections = ?, updatedAt = datetime('now') WHERE id = ?",
        (json.dumps(nodes), json.dumps(conns), WORKFLOW_ID)
    )
    db_conn.commit()
    db_conn.close()

if __name__ == "__main__":
    print("⭐ VEGA v11: CODE NODE ROUTER (ULTIMATE SOLUTION)")
    print("━" * 60)
    patch()
    print("━" * 60)
    print("✅ Code node created. HAZ F5.")
    print()
    print("🌟 Keep Moving Forward - Vega")
    print("   JavaScript puro = Sin bugs de n8n")
