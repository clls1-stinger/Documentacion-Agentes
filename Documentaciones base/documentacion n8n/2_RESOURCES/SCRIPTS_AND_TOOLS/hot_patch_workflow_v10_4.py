#!/usr/bin/env python3
"""
🔧 Hot Patch n8n Workflow - v10.4 (Idempotent & Definitive Debug Probe)

Esta es la versión definitiva del script de instrumentación. Es idempotente:
primero limpia cualquier sonda de depuración fallida de ejecuciones anteriores
y luego inserta la nueva sonda de forma segura.
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
    print(f"🔧 Hot Patch v10.4 (Idempotent Probe) - Iniciando...")
    
    workflow = get_workflow_from_db()
    nodes = workflow['nodes']
    connections = workflow['connections']

    # 1. LIMPIEZA IDEMPOTENTE: Eliminar cualquier sonda fallida anterior
    print("🧹 Buscando y limpiando sondas de depuración de intentos anteriores...")
    nodes_to_keep = [n for n in nodes if n.get('name') != PROBE_NAME]
    if len(nodes) != len(nodes_to_keep):
        print(f"  - Nodo '{PROBE_NAME}' encontrado y eliminado.")
        workflow['nodes'] = nodes_to_keep
    
    if PROBE_NAME in connections:
        del connections[PROBE_NAME]
        print(f"  - Conexiones salientes de '{PROBE_NAME}' eliminadas.")
    
    # Eliminar cualquier conexión entrante a la sonda
    for source_name, conn_data in connections.items():
        if 'main' in conn_data:
            for output_list in conn_data['main']:
                output_list[:] = [conn for conn in output_list if conn.get('node') != PROBE_NAME]
    print("  - Limpieza completada.")

    # 2. Descubrir la conexión real en el workflow limpio
    target_node = next((n for n in workflow['nodes'] if n.get('name') == TARGET_NODE_NAME), None)
    if not target_node:
        print(f"❌ Error: No se pudo encontrar el nodo destino ('{TARGET_NODE_NAME}').")
        sys.exit(1)

    source_node_name = None
    for potential_source_name, conn_data in connections.items():
        if 'main' in conn_data:
            for output_list in conn_data['main']:
                for conn_detail in output_list:
                    if conn_detail.get('node') == TARGET_NODE_NAME:
                        source_node_name = potential_source_name
                        break
                if source_node_name: break
        if source_node_name: break
    
    if not source_node_name:
        print(f"❌ Error: No se pudo descubrir el nodo que se conecta a '{TARGET_NODE_NAME}' en el workflow limpio.")
        sys.exit(1)

    source_node = next((n for n in workflow['nodes'] if n.get('name') == source_node_name), None)
    print(f"✅ Nodo origen descubierto: '{source_node_name}'.")

    # 3. Crear e insertar la nueva sonda
    probe_node_id = str(uuid.uuid4())
    probe_pos_x = (source_node['position'][0] + target_node['position'][0]) / 2
    probe_pos_y = (source_node['position'][1] + target_node['position'][1]) / 2

    correct_js_code = "console.log(\"\n--- DEBUG PROBE ---\");\nconsole.log(\"Data into Tool Router:\");\nconsole.log(JSON.stringify($input.item.json, null, 2));\nconsole.log(\"--- END DEBUG PROBE ---\\\n\");\nreturn $input.item;"

    probe_node = {
        "parameters": {"jsCode": correct_js_code},
        "id": probe_node_id, "name": PROBE_NAME, "type": "n8n-nodes-base.code", "typeVersion": 2,
        "position": [probe_pos_x, probe_pos_y]
    }
    workflow['nodes'].append(probe_node)
    print(f"✅ Nuevo nodo '{PROBE_NAME}' creado.")

    # 4. Recablear conexiones
    print(" rewire conexiones...")
    for output_list in connections[source_node_name]['main']:
        for conn_detail in output_list:
            if conn_detail.get('node') == TARGET_NODE_NAME:
                print(f"  - Redirigiendo: '{source_node_name}' -> '{PROBE_NAME}'")
                conn_detail['node'] = PROBE_NAME
                conn_detail['id'] = probe_node_id

    connections[PROBE_NAME] = { "main": [[{"node": TARGET_NODE_NAME, "type": "main", "index": 0, "id": target_node['id']}]] }
    print(f"  - Creando conexión: '{PROBE_NAME}' -> '{TARGET_NODE_NAME}'")

    # 5. Guardar
    save_workflow_to_db(workflow['id'], json.dumps(workflow['nodes']), json.dumps(workflow['connections']))
    
    print("\n✨ ¡Listo! El workflow ha sido instrumentado con la sonda de depuración idempotente v10.4.")
    print("   Por favor, ejecuta el workflow UNA VEZ para que pueda capturar los datos en los logs.")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error Inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
