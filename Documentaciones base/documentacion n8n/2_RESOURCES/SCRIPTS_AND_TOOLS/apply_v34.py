import sqlite3
import json
from pathlib import Path

# Configuración
N8N_DB = Path.home() / ".n8n" / "database.sqlite"
WORKFLOW_JSON_PATH = "/home/emky/n8n/documentacion/FORENSICS_AND_LOGS/workflow_yes_patched_v34.json"
WORKFLOW_ID = "Urf7HpECFvfQooAv"

def apply_patch():
    print(f"🚀 Iniciando aplicación del Parche v34 a workflow {WORKFLOW_ID}...")
    
    if not Path(WORKFLOW_JSON_PATH).exists():
        print(f"❌ Error: No se encuentra el archivo JSON en {WORKFLOW_JSON_PATH}")
        return

    with open(WORKFLOW_JSON_PATH, 'r') as f:
        workflow_data = json.load(f)
    
    nodes = workflow_data['nodes']
    connections = workflow_data['connections']
    name = workflow_data['meta']['name']

    conn = sqlite3.connect(N8N_DB)
    cursor = conn.cursor()
    
    # 1. Backup? (Opcional pero recomendado)
    # cp ~/.n8n/database.sqlite ~/.n8n/database.sqlite.bak
    
    # 2. Update DB
    cursor.execute("""
        UPDATE workflow_entity 
        SET nodes = ?, 
            connections = ?,
            name = ?,
            updatedAt = datetime('now')
        WHERE id = ?
    """, (
        json.dumps(nodes),
        json.dumps(connections),
        name,
        WORKFLOW_ID
    ))
    
    conn.commit()
    conn.close()
    
    print(f"✅ Workflow '{name}' aplicado exitosamente en la DB.")
    print("✨ Siguiente paso: Realizar una prueba del workflow.")

if __name__ == "__main__":
    apply_patch()
