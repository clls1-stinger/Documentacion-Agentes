#!/usr/bin/env python3
"""
♰️ Inspect n8n Node Code - Imprime el código JS de un nodo específico.
"""

import sqlite3
import json
import sys
from pathlib import Path

# --- Configuración ---
N8N_DB = Path.home() / ".n8n" / "database.sqlite"
WORKFLOW_NAME = "Yes (Patched v43 - Anti-Loop Prompt)"
# El nombre del nodo que queremos inspeccionar
NODE_NAME_TO_INSPECT = "Parse Planner" 

def main():
    print(f"\u2670️ Inspeccionando el código del nodo '{NODE_NAME_TO_INSPECT}'...")
    
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
            sys.exit(1)
            
        print("\n✅ Nodo encontrado. Aquí está su código JavaScript ('jsCode'):")
        
        node_code = target_node.get('parameters', {}).get('jsCode', '')
        
        if not node_code:
            print("-- El nodo no tiene código JS o el campo 'jsCode' está vacío. --")
        else:
            print("--- INICIO DEL CÓDIGO ---")
            print(node_code)
            print("--- FIN DEL CÓDIGO ---")

    except Exception as e:
        print(f"\n❌ Error Inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
