#!/usr/bin/env python3
"""
🔧 Hot Patch n8n Workflow - v10 (Insert Debug Probe)

Este script instrumenta el workflow insertando un nodo de depuración
('DEBUG_PROBE') antes del 'Tool Router' para capturar los datos exactos
que este recibe. Es una operación compleja que añade un nodo y recablea
las conexiones.
"""

import sqlite3
import json
import sys
import uuid
from pathlib import Path

# --- Configuración ---
N8N_DB = Path.home() / ".n8n" / "database.sqlite"
WORKFLOW_NAME = "Yes (Patched v43 - Anti-Loop Prompt)"
PROBE_NAME = "DEBUG_PROBE"
TARGET_NODE_NAME = "Tool Router"
# Asumimos, basándonos en los logs, que este es el nodo que alimenta al router
SOURCE_NODE_NAME = "Route Decision" 

def get_workflow_from_db():
    """Obtiene el workflow completo (nodos y conexiones) desde SQLite."""
    conn = sqlite3.connect(N8N_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT id, nodes, connections FROM workflow_entity WHERE name = ?", (WORKFLOW_NAME,))
    result = cursor.fetchone()
    conn.close()
    if not result:
        raise FileNotFoundError(f"No se encontró el workflow '{WORKFLOW_NAME}'")
    return {
        'id': result[0],
        'nodes': json.loads(result[1]),
        'connections': json.loads(result[2])
    }

def save_workflow_to_db(wf_id, nodes_json, connections_json):
    """Guarda el workflow modificado en SQLite."""
    conn = sqlite3.connect(N8N_DB)
    cursor = conn.cursor()
    cursor.execute("UPDATE workflow_entity SET nodes = ?, connections = ?, updatedAt = datetime('now') WHERE id = ?",
                   (nodes_json, connections_json, wf_id))
    conn.commit()
    conn.close()

def main():
    print(f"🔧 Hot Patch v10 (Insert Debug Probe) - Iniciando...")
    
    # 1. Obtener el workflow
    workflow = get_workflow_from_db()
    nodes = workflow['nodes']
    connections = workflow['connections']

    # 2. Encontrar nodos de origen y destino
    source_node = next((n for n in nodes if n.get('name') == SOURCE_NODE_NAME), None)
    target_node = next((n for n in nodes if n.get('name') == TARGET_NODE_NAME), None)

    if not source_node or not target_node:
        print(f"❌ Error: No se pudo encontrar el nodo origen ('{SOURCE_NODE_NAME}') o destino ('{TARGET_NODE_NAME}').")
        sys.exit(1)
        
    print(f"✅ Nodos origen y destino encontrados.")

    # 3. Crear el nuevo nodo de depuración
    probe_node_id = str(uuid.uuid4())
    # Posicionar el nodo visualmente entre el origen y el destino
    probe_pos_x = (source_node['position'][0] + target_node['position'][0]) / 2
    probe_pos_y = (source_node['position'][1] + target_node['position'][1]) / 2

    probe_node = {
        "parameters": {
            "jsCode": "console.log('\n--- DEBUG PROBE ---');\nconsole.log(JSON.stringify($input.item.json, null, 2));\nconsole.log('--- END DEBUG PROBE ---\n');\nreturn $input.item;"
        },
        "id": probe_node_id,
        "name": PROBE_NAME,
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": [probe_pos_x, probe_pos_y]
    }
    nodes.append(probe_node)
    print(f"✅ Nuevo nodo '{PROBE_NAME}' creado.")

    # 4. Recablear las conexiones
    print(" rewire conexiones...")

    # Encontrar la conexión original que va del origen al destino
    original_connection = None
    output_index = -1
    
    source_connections = connections.get(source_node['name'], {}).get('main', [])
    for i, output_connections in enumerate(source_connections):
        for conn_detail in output_connections:
            if conn_detail.get('node') == TARGET_NODE_NAME:
                original_connection = conn_detail
                output_index = i
                break
        if original_connection:
            break

    if not original_connection:
        print(f"❌ Error: No se encontró una conexión de '{SOURCE_NODE_NAME}' a '{TARGET_NODE_NAME}'.")
        sys.exit(1)

    # a) Cambiar la conexión del origen para que apunte a la sonda
    original_connection['node'] = PROBE_NAME
    original_connection['id'] = probe_node_id
    print(f"  - Conexión de '{SOURCE_NODE_NAME}' redirigida a '{PROBE_NAME}'.")

    # b) Crear la nueva conexión desde la sonda al destino
    new_connection = {
        PROBE_NAME: {
            "main": [
                [
                    {
                        "node": TARGET_NODE_NAME,
                        "type": "main",
                        "index": 0,
                        "id": target_node['id']
                    }
                ]
            ]
        }
    }
    connections.update(new_connection)
    print(f"  - Nueva conexión de '{PROBE_NAME}' a '{TARGET_NODE_NAME}' creada.")

    # 5. Guardar el workflow modificado
    save_workflow_to_db(workflow['id'], json.dumps(nodes), json.dumps(connections))
    
    print("\n✨ ¡Listo! El workflow ha sido instrumentado con una sonda de depuración.")
    print("   Por favor, ejecuta el workflow UNA VEZ, y luego podré analizar los logs para el diagnóstico final.")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error Inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
