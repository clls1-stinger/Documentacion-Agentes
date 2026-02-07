#!/usr/bin/env python3
"""
🗑️ Delete n8n Workflow

Este script elimina un workflow específico de la base de datos de n8n
basándose en su nombre. Utilizado como parte de la estrategia 'Nuke and Pave'.
"""

import sqlite3
import sys
from pathlib import Path

# --- Configuración ---
N8N_DB = Path.home() / ".n8n" / "database.sqlite"
WORKFLOW_NAME_TO_DELETE = "Yes (Patched v43 - Anti-Loop Prompt)" # El workflow corrupto

def main():
    print(f"🗑️ Iniciando eliminación del workflow '{WORKFLOW_NAME_TO_DELETE}'...")
    
    try:
        conn = sqlite3.connect(N8N_DB)
        cursor = conn.cursor()

        # Verificar si el workflow existe antes de intentar eliminarlo
        cursor.execute("SELECT id FROM workflow_entity WHERE name = ?", (WORKFLOW_NAME_TO_DELETE,))
        result = cursor.fetchone()

        if result:
            workflow_id = result[0]
            cursor.execute("DELETE FROM workflow_entity WHERE name = ?", (WORKFLOW_NAME_TO_DELETE,))
            conn.commit()
            # CÓDIGO CORREGIDO: Escapar las comillas internas
            print(f"✅ Workflow '{WORKFLOW_NAME_TO_DELETE}' (ID: {workflow_id}) eliminado con éxito de la base de datos.")
        else:
            print(f"⚠️ El workflow '{WORKFLOW_NAME_TO_DELETE}' no se encontró en la base de datos. Nada que eliminar.")

        conn.close()
        
    except Exception as e:
        print(f"\n❌ Error Inesperado durante la eliminación: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()