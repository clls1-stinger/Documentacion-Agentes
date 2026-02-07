#!/usr/bin/env python3
"""
🔧 Hot Patch n8n Workflow - v10.1 (Dynamic & Robust Debug Probe)

Esta versión mejorada del script de instrumentación descubre dinámicamente
el nodo de origen del 'Tool Router' antes de insertar la sonda de depuración.
Esto elimina las suposiciones y lo hace robusto a cambios en el workflow.
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

def get_workflow_from_db():
    """Obtiene el workflow completo (nodos y conexiones) desde SQLite."""
    conn = sqlite3.connect(N8N_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT id, nodes, connections FROM workflow_entity WHERE name = ?", (WORKFLOW_NAME,))
    result = cursor.fetchone()
    conn.close()
    if not result:
        raise FileNotFoundError(f"No se encontró el workflow '{WORKFLOW_NAME}'")
    workflow_data = {'id': result[0], 'nodes': json.loads(result[1]), 'connections': json.loads(result[2])}
    # Crear un mapa de ID a nombre para facilitar la búsqueda
    workflow_data['node_id_map'] = {node['id']: node['name'] for node in workflow_data['nodes']}
    return workflow_data

def save_workflow_to_db(wf_id, nodes_json, connections_json):
    """Guarda el workflow modificado en SQLite."""
    conn = sqlite3.connect(N8N_DB)
    cursor = conn.cursor()
    cursor.execute("UPDATE workflow_entity SET nodes = ?, connections = ?, updatedAt = datetime('now') WHERE id = ?",
                   (nodes_json, connections_json, wf_id))
    conn.commit()
    conn.close()

def main():
    print(f"🔧 Hot Patch v10.1 (Dynamic Probe) - Iniciando...")
    
    # 1. Obtener el workflow
    workflow = get_workflow_from_db()
    nodes = workflow['nodes']
    connections = workflow['connections']
    node_id_map = workflow['node_id_map']

    # 2. Encontrar nodo destino
    target_node = next((n for n in nodes if n.get('name') == TARGET_NODE_NAME), None)
    if not target_node:
        print(f"❌ Error: No se pudo encontrar el nodo destino ('{TARGET_NODE_NAME}').")
        sys.exit(1)
        
    print(f"✅ Nodo destino '{TARGET_NODE_NAME}' encontrado (ID: {target_node['id']}).")

    # 3. Descubrir dinámicamente el nodo origen
    source_node_id = None
    source_node_name = None
    
    # Buscar en las conexiones quién tiene como salida a nuestro nodo destino
    for node_name, conn_data in connections.items():
        for output_type in conn_data.values(): # Itera sobre 'main', 'error', etc.
            for output_list in output_type:
                for conn_detail in output_list:
                    if conn_detail.get('id') == target_node['id']:
                        source_node_name = node_name
                        break
                if source_node_name: break
            if source_node_name: break
        if source_node_name: break
    
    if not source_node_name:
        print(f"❌ Error: No se pudo descubrir dinámicamente el nodo que se conecta a '{TARGET_NODE_NAME}'.")
        sys.exit(1)

    source_node = next((n for n in nodes if n.get('name') == source_node_name), None)
    if not source_node: # Sanity check
        print(f"❌ Error: El nombre de nodo descubierto '{source_node_name}' no corresponde a ningún nodo real.")
        sys.exit(1)

    print(f"✅ Nodo origen descubierto dinámicamente: '{source_node_name}' (ID: {source_node['id']}).")

    # 4. Crear el nuevo nodo de depuración
    probe_node_id = str(uuid.uuid4())
    probe_pos_x = (source_node['position'][0] + target_node['position'][0]) / 2
    probe_pos_y = (source_node['position'][1] + target_node['position'][1]) / 2

    probe_node = {
        "parameters": {"jsCode": "console.log('\n--- DEBUG PROBE ---');\nconsole.log(JSON.stringify($input.item.json, null, 2));\nconsole.log('--- END DEBUG PROBE ---\n');\nreturn $input.item;"},
        "id": probe_node_id, "name": PROBE_NAME, "type": "n8n-nodes-base.code", "typeVersion": 2,
        "position": [probe_pos_x, probe_pos_y]
    }
    nodes.append(probe_node)
    print(f"✅ Nuevo nodo '{PROBE_NAME}' creado.")

    # 5. Recablear las conexiones
    print(" rewire conexiones...")
    
    # a) Modificar la conexión de salida del nodo origen para que apunte a la sonda
    found_and_rewired = False
    for node_name, conn_data in connections.items():
        if node_name == source_node_name:
            for output_type in conn_data.values():
                for output_list in output_type:
                    for conn_detail in output_list:
                        if conn_detail.get('id') == target_node['id']:
                            print(f"  - Redirigiendo conexión: '{source_node_name}' -> '{target_node['name']}' se convierte en '{source_node_name}' -> '{PROBE_NAME}'")
                            conn_detail['node'] = PROBE_NAME
                            conn_detail['id'] = probe_node_id
                            found_and_rewired = True

    if not found_and_rewired:
        print("❌ Error crítico: Se encontró la conexión pero no se pudo recablear.")
        sys.exit(1)

    # b) Crear la nueva conexión desde la sonda al destino
    connections[PROBE_NAME] = {
        "main": [[{"node": TARGET_NODE_NAME, "type": "main", "index": 0, "id": target_node['id']}]]
    }
    print(f"  - Nueva conexión creada: '{PROBE_NAME}' -> '{TARGET_NODE_NAME}'")

    # 6. Guardar el workflow modificado
    save_workflow_to_db(workflow['id'], json.dumps(nodes), json.dumps(connections))
    
    print("\n✨ ¡Listo! El workflow ha sido instrumentado con una sonda de depuración dinámica.")
    print("   Por favor, ejecuta el workflow UNA VEZ, y luego podré analizar los logs para el diagnóstico final.")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error Inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
