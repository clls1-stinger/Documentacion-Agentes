#!/usr/bin/env python3
"""
⭐ VEGA v17: FORCE RE-RENDER
El nodo Route Decision existe pero no muestra sus puertos.
Acción: Regenerar ID, mover posición y asegurar propiedad outputs.
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
    
    print("🔥 FORZANDO RE-RENDER DE ROUTE DECISION...")
    
    # Encontrar Route Decision
    target_idx = -1
    for i, n in enumerate(nodes):
        if n['name'] == 'Route Decision':
            target_idx = i
            break
            
    if target_idx == -1:
        print("❌ Node not found")
        return

    node = nodes[target_idx]
    
    # 1. Cambiar ID (Nuevo UUID)
    old_id = node['id']
    new_id = str(uuid.uuid4())
    node['id'] = new_id
    print(f"   🔄 Changed ID: {old_id} -> {new_id}")
    
    # 2. Mover posición (Shift X +20)
    node['position'][0] += 20
    print(f"   📍 Moved Query: {node['position']}")
    
    # 3. Asegurar Outputs
    node['outputs'] = ['main', 'main']
    print(f"   out Outputs set to: {node['outputs']}")
    
    # 4. Actualizar conexiones (Buscar referencias al nombre del nodo, no al ID)
    # En n8n, las conexiones en el JSON usan EL NOMBRE del nodo como clave.
    # Pero internamente n8n usa IDs para cache. Al cambiar el ID forzamos refresh.
    # Las conexiones en 'connections' JSON usan 'node': 'Name'.
    # Así que no necesitamos cambiar el JSON de conexiones, solo el ID del objeto nodo.
    
    nodes[target_idx] = node
    
    # Guardar
    cursor.execute(
        "UPDATE workflow_entity SET nodes = ?, updatedAt = datetime('now') WHERE id = ?",
        (json.dumps(nodes), WORKFLOW_ID)
    )
    db_conn.commit()
    db_conn.close()

if __name__ == "__main__":
    print("⭐ VEGA v17: NUCLEAR RE-RENDER")
    print("━" * 60)
    patch()
    print("━" * 60)
    print("✅ Node ID refreshed. HAZ F5.")
