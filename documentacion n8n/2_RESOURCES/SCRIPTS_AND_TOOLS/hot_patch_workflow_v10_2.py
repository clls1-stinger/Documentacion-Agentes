#!/usr/bin/env python3
"""
🚪 Hot Patch n8n Workflow - v10.2 (Corrected Dynamic Debug Probe)

Tercer intento y definitivo para instrumentar el workflow. Esta versión
utiliza una lógica de descubrimiento de conexiones estructuralmente correcta
para garantizar la inserción exitosa de la sonda de depuración.
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
    return {'id': result[0], 'nodes': json.loads(result[1]), 'connections': json.loads(result[2])}

def save_workflow_to_db(wf_id, nodes_json, connections_json):
    """Guarda el workflow modificado en SQLite."""
    conn = sqlite3.connect(N8N_DB)
    cursor = conn.cursor()
    cursor.execute("UPDATE workflow_entity SET nodes = ?, connections = ?, updatedAt = datetime('now') WHERE id = ?",
                   (nodes_json, connections_json, wf_id))
    conn.commit()
    conn.close()

def main():
    print(f"🔧 Hot Patch v10.2 (Corrected Dynamic Probe) - Iniciando...")
    
    workflow = get_workflow_from_db()
    nodes = workflow['nodes']
    connections = workflow['connections']

    target_node = next((n for n in nodes if n.get('name') == TARGET_NODE_NAME), None)
    if not target_node:
        print(f"❌ Error: No se pudo encontrar el nodo destino ('{TARGET_NODE_NAME}').")
        sys.exit(1)
        
    print(f"✅ Nodo destino '{TARGET_NODE_NAME}' encontrado.")

    # CORRECTED DYNAMIC DISCOVERY LOGIC
    source_node_name = None
    for potential_source_name, conn_data in connections.items():
        for output_list in conn_data.get('main', []):
            for conn_detail in output_list:
                if conn_detail.get('node') == TARGET_NODE_NAME:
                    source_node_name = potential_source_name
                    break
            if source_node_name: break
        if source_node_name: break
    
    if not source_node_name:
        print(f"❌ Error: No se pudo descubrir el nodo que se conecta a '{TARGET_NODE_NAME}'.")
        sys.exit(1)

    source_node = next((n for n in nodes if n.get('name') == source_node_name), None)
    print(f"✅ Nodo origen descubierto dinámicamente: '{source_node_name}'.")

    probe_node_id = str(uuid.uuid4())
    probe_pos_x = (source_node['position'][0] + target_node['position'][0]) / 2
    probe_pos_y = (source_node['position'][1] + target_node['position'][1]) / 2

    probe_node = {
        "parameters": {"jsCode": "console.log('\n--- DEBUG PROBE ---');\nconsole.log('Data into Tool Router:');\nconsole.log(JSON.stringify($input.item.json, null, 2));\nconsole.log('--- END DEBUG PROBE ---'\n);\nreturn $input.item;"},
        "id": probe_node_id, "name": PROBE_NAME, "type": "n8n-nodes-base.code", "typeVersion": 2,
        "position": [probe_pos_x, probe_pos_y]
    }
    nodes.append(probe_node)
    print(f"✅ Nuevo nodo '{PROBE_NAME}' creado.")

    print(" rewire conexiones...")
    # a) Modificar la conexión de salida del nodo origen para que apunte a la sonda
    for output_list in connections[source_node_name]['main']:
        for conn_detail in output_list:
            if conn_detail.get('node') == TARGET_NODE_NAME:
                print(f"  - Redirigiendo conexión: '{source_node_name}' -> '{target_node['name']}' se convierte en '{source_node_name}' -> '{PROBE_NAME}'")
                conn_detail['node'] = PROBE_NAME
                conn_detail['id'] = probe_node_id

    # b) Crear la nueva conexión desde la sonda al destino
    connections[PROBE_NAME] = { "main": [[{"node": TARGET_NODE_NAME, "type": "main", "index": 0, "id": target_node['id']}]] }
    print(f"  - Nueva conexión creada: '{PROBE_NAME}' -> '{TARGET_NODE_NAME}'")

    save_workflow_to_db(workflow['id'], json.dumps(nodes), json.dumps(connections))
    
    print("\n✨ ¡Listo! El workflow ha sido instrumentado con la sonda de depuración v10.2.")
    print("   Por favor, ejecuta el workflow UNA VEZ para que pueda capturar los datos en los logs.")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error Inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
