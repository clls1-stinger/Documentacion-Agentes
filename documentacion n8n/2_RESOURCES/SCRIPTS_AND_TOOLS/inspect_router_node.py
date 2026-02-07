#!/usr/bin/env python3
"""
☒️ Inspect n8n Node - Imprime la configuración de un nodo específico.
(Recreado después de una eliminación prematura)
"""

import sqlite3
import json
import sys
from pathlib import Path

# --- Configuración ---
N8N_DB = Path.home() / ".n8n" / "database.sqlite"
WORKFLOW_NAME = "Yes (Patched v43 - Anti-Loop Prompt)"
NODE_NAME_TO_INSPECT = "Tool Router"

def main():
    print(f"\u2612️ Inspeccionando el nodo '{NODE_NAME_TO_INSPECT}' en el workflow '{WORKFLOW_NAME}'...")
    
    try:
        conn = sqlite3.connect(N8N_DB)
        cursor = conn.cursor()
        cursor.execute("SELECT nodes FROM workflow_entity WHERE name = ?", (WORKFLOW_NAME,))
        result = cursor.fetchone()
        conn.close()

        if not result:
            print(f"❌ Error: No se encontró el workflow '{WORKFLOW_NAME}'.")
            sys.exit(1)

        nodes = json.loads(result[0])
        
        target_node = next((node for node in nodes if node.get('name') == NODE_NAME_TO_INSPECT), None)
        
        if not target_node:
            print(f"❌ Error: No se encontró un nodo con el nombre '{NODE_NAME_TO_INSPECT}'.")
            all_node_names = [node.get('name', 'SIN_NOMBRE') for node in nodes]
            print("\nNombres de nodos disponibles en el workflow:")
            for name in sorted(all_node_names):
                print(f"- {name}")
            sys.exit(1)
            
        print("\n✅ Nodo encontrado. Aquí está su configuración JSON:")
        print(json.dumps(target_node, indent=2))

    except Exception as e:
        print(f"\n❌ Error Inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
