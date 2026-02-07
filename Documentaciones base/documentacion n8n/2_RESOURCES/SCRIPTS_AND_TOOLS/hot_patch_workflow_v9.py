#!/usr/bin/env python3
"""
🔧 Hot Patch n8n Workflow - v9 (Definitive Router Path Fix)

Este script aplica el parche final, corrigiendo la ruta de datos que el
'Tool Router' debe leer, alineándola con la salida del 'Parse Planner'.
"""

import sqlite3
import json
import sys
from pathlib import Path

# --- Configuración ---
N8N_DB = Path.home() / ".n8n" / "database.sqlite"
WORKFLOW_NAME = "Yes (Patched v43 - Anti-Loop Prompt)"
NODE_TO_PATCH = "Tool Router"
CORRECT_INPUT_PATH = "{{ $json.planner_output.next_instruction }}" # La ruta anidada correcta

def get_workflow_from_db():
    """Obtiene el workflow desde SQLite."""
    conn = sqlite3.connect(N8N_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT id, nodes FROM workflow_entity WHERE name = ?", (WORKFLOW_NAME,))
    result = cursor.fetchone()
    conn.close()
    if not result:
        raise FileNotFoundError(f"No se encontró el workflow '{WORKFLOW_NAME}'")
    return {'id': result[0], 'nodes': json.loads(result[1])}

def patch_router_path_node(workflow):
    """Modifica el Tool Router para que apunte a la ruta de datos correcta."""
    router_node = next((node for node in workflow['nodes'] if node.get('name') == NODE_TO_PATCH), None)
    
    if not router_node:
        print(f"❌ Error: No se encontró el nodo '{NODE_TO_PATCH}'.")
        return False

    print(f"🔧 Encontrado '{NODE_TO_PATCH}'. Corrigiendo la ruta de entrada de las reglas...")
    
    rules = router_node['parameters']['rules']['values']
    
    for i, rule in enumerate(rules):
        condition = rule['conditions']['conditions'][0]
        
        # Corregir únicamente el campo de entrada
        condition['leftValue'] = CORRECT_INPUT_PATH
        print(f"  - Regla {i+1} actualizada para leer de: '{CORRECT_INPUT_PATH}'")

    print(f"✅ Ruta de entrada del '{NODE_TO_PATCH}' corregida con éxito.")
    return True

def save_workflow_to_db(workflow_id, nodes_json):
    """Guarda el workflow modificado en SQLite."""
    conn = sqlite3.connect(N8N_DB)
    cursor = conn.cursor()
    cursor.execute("UPDATE workflow_entity SET nodes = ?, updatedAt = datetime('now') WHERE id = ?", (nodes_json, workflow_id))
    conn.commit()
    conn.close()

def main():
    print(f"🔧 Hot Patch v9 (Path Fix) - Iniciando...")
    
    workflow = get_workflow_from_db()
    
    if patch_router_path_node(workflow):
        save_workflow_to_db(workflow['id'], json.dumps(workflow['nodes']))
        print("\n✨ ¡Listo! El parche definitivo para el 'Tool Router' ha sido aplicado.")
        print("   Por favor, haz F5 en n8n o reinicia el servicio para activar el cambio y verificar la solución final.")
    else:
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error Inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
