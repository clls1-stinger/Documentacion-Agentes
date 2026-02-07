#!/usr/bin/env python3
"""
⭐ VEGA v9: NUCLEAR OPTION - Replace Switch with IF
El Switch está roto. Lo reemplazamos completamente con un IF node.
"Keep Moving Forward" - Si una herramienta no funciona, usamos otra.
"""

import sqlite3
import json
from pathlib import Path
import uuid

N8N_DB = Path.home() / ".n8n" / "database.sqlite"
WORKFLOW_ID = "Urf7HpECFvfQooAv"

def patch():
    conn = sqlite3.connect(N8N_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT nodes, connections FROM workflow_entity WHERE id = ?", (WORKFLOW_ID,))
    nodes_raw, conns_raw = cursor.fetchone()
    nodes = json.loads(nodes_raw)
    conns = json.loads(conns_raw)
    
    # Encontrar el Switch viejo
    switch_idx = None
    switch_node = None
    for idx, node in enumerate(nodes):
        if node['name'] == 'Is Done Switch':
            switch_idx = idx
            switch_node = node
            break
    
    if not switch_node:
        print("❌ Switch node not found!")
        return
    
    print(f"🔍 Found Switch at index {switch_idx}")
    
    # Crear el nuevo IF node con las MISMAS coordenadas
    new_if_node = {
        "parameters": {
            "conditions": {
                "string": [
                    {
                        "value1": "={{ $json.planner_output.is_done_string }}",
                        "operation": "equals",
                        "value2": "TRUE"
                    }
                ]
            }
        },
        "id": str(uuid.uuid4()),
        "name": "Is Done Check",
        "type": "n8n-nodes-base.if",
        "typeVersion": 1,
        "position": switch_node['position']  # Misma posición en el canvas
    }
    
    print(f"✅ Created IF node: {new_if_node['name']}")
    
    # Reemplazar el Switch con el IF
    nodes[switch_idx] = new_if_node
    
    # Actualizar conexiones
    # El IF node tiene dos salidas:
    # - output 0 = "true" (cuando la condición se cumple)
    # - output 1 = "false" (cuando la condición NO se cumple)
    
    old_conns = conns.get('Is Done Switch', {})
    new_conns = {
        "main": [
            old_conns['main'][0],  # true → Final Response
            old_conns['main'][1]   # false → Actor Prep
        ]
    }
    
    # Eliminar conexiones del Switch viejo
    if 'Is Done Switch' in conns:
        del conns['Is Done Switch']
    
    # Agregar conexiones del IF nuevo
    conns['Is Done Check'] = new_conns
    
    print("🔗 Updated connections:")
    print(f"   IF true  → {new_conns['main'][0]}")
    print(f"   IF false → {new_conns['main'][1]}")
    
    # Actualizar conexiones ENTRANTES (de Parse Planner al IF nuevo)
    for node_name, node_conns in conns.items():
        if 'main' in node_conns:
            for output_list in node_conns['main']:
                for conn_item in output_list:
                    if conn_item.get('node') == 'Is Done Switch':
                        conn_item['node'] = 'Is Done Check'
                        print(f"   📌 Updated incoming connection from: {node_name}")
    
    # Guardar
    db_conn = sqlite3.connect(N8N_DB)
    cursor2 = db_conn.cursor()
    cursor2.execute(
        "UPDATE workflow_entity SET nodes = ?, connections = ?, updatedAt = datetime('now') WHERE id = ?",
        (json.dumps(nodes), json.dumps(conns), WORKFLOW_ID)
    )
    db_conn.commit()
    db_conn.close()

if __name__ == "__main__":
    print("⭐ VEGA v9: REPLACING SWITCH WITH IF NODE")
    print("━" * 60)
    patch()
    print("━" * 60)
    print("✅ Switch replaced with IF node. HAZ F5.")
    print()
    print("🌟 'Keep Moving Forward' - Vega")
