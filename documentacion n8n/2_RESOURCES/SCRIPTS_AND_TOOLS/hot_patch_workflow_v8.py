#!/usr/bin/env python3
"""
🔧 Hot Patch n8n Workflow - v8 (Final Aggregator Fix)

Este script aplica un parche final al nodo 'Aggregator' para que
maneje correctamente la salida (incluso vacía) de 'Execute Command'.
"""

import sqlite3
import json
import sys
from pathlib import Path

# --- Configuración ---
N8N_DB = Path.home() / ".n8n" / "database.sqlite"
WORKFLOW_NAME = "Yes (Patched v43 - Anti-Loop Prompt)"
NODE_TO_PATCH = "Aggregator"

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

def patch_aggregator_node_v2(workflow):
    """Modifica el nodo Aggregator para usar hasOwnProperty y capturar stdout vacío."""
    aggregator_node = next((node for node in workflow['nodes'] if node.get('name') == NODE_TO_PATCH), None)
    
    if not aggregator_node:
        print(f"❌ Error: No se encontró el nodo '{NODE_TO_PATCH}'.")
        return False

    print("🔧 Encontrado 'Aggregator'. Aplicando parche final...")
    
    # Código mejorado con hasOwnProperty
    new_code = r"""let result = "Success";
let structured_data = null;

if (items.length > 0) {
  // Caso 1: Resultado de Drive Search (contiene 'id' y 'name')
  if (items[0].json.id && items[0].json.name) {
     result = items.map(i => `[FILE] ${i.json.name} (${i.json.id})`).join(", ");
     structured_data = items.map(i => ({
       id: i.json.id,
       name: i.json.name,
       mimeType: i.json.mimeType || 'unknown'
     }));
  }
  // Caso 2: Resultado de Execute Command (contiene 'stdout')
  else if (items[0].json.hasOwnProperty('stdout')) {
     result = items[0].json.stdout;
     // Si stdout es un string vacío, result será "", lo cual es correcto.
  }
  // Caso 3: Resultado binario (de una descarga, etc.)
  else if (items[0].binary) {
     result = "Binary data processed successfully.";
     // Podríamos añadir más metadata aquí si fuera necesario
  }
  // Fallback por si la estructura cambia en el futuro
  else {
    result = "Resultado de herramienta no reconocido, pero la operación fue exitosa.";
  }
} else {
  result = "La herramienta se ejecutó pero no produjo ningún resultado (ej. búsqueda sin resultados).";
}


// Aggregate for History WITH structured data
const prev = $('Clean Actor').last().json;
return [{ json: { 
  action_taken: prev.accion,
  tool_result: result,
  tool_result_data: structured_data,
  planner_instruction: prev.instruction,
  user_goal: prev.user_goal,
  history: prev.history,
  counter: prev.counter
} }];"""
    
    aggregator_node['parameters']['jsCode'] = new_code
    print("✅ Nodo 'Aggregator' modificado con lógica 'hasOwnProperty' y manejo de casos mejorado.")
    return True

def save_workflow_to_db(workflow_id, nodes_json):
    """Guarda el workflow modificado en SQLite."""
    conn = sqlite3.connect(N8N_DB)
    cursor = conn.cursor()
    cursor.execute("UPDATE workflow_entity SET nodes = ?, updatedAt = datetime('now') WHERE id = ?", (nodes_json, workflow_id))
    conn.commit()
    conn.close()

def main():
    print(f"🔧 Hot Patch v8 (Final Aggregator Fix) - Iniciando...")
    
    workflow = get_workflow_from_db()
    
    if patch_aggregator_node_v2(workflow):
        save_workflow_to_db(workflow['id'], json.dumps(workflow['nodes']))
        print("\n✨ ¡Listo! El parche final del 'Aggregator' ha sido aplicado.")
        print("   Por favor, haz F5 en n8n o reinicia el servicio para activar el cambio final y verificar la solución.")
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
