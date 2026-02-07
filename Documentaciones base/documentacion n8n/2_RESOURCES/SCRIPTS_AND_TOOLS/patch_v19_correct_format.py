#!/usr/bin/env python3
"""
⭐ VEGA v19: CORRECT CODE NODE RETURN FORMAT
El error 404 mostró: "A 'json' property isn't an object" en Route Decision.
Causa: n8n Code Node v2 requiere arrays de arrays: return [ [item], [] ].
Acción: Corregir formato y mantener lógica invertida (0=Final, 1=Actor).
"""

import sqlite3
import json
from pathlib import Path

N8N_DB = Path.home() / ".n8n" / "database.sqlite"
WORKFLOW_ID = "Urf7HpECFvfQooAv"

def patch():
    db_conn = sqlite3.connect(N8N_DB)
    cursor = db_conn.cursor()
    cursor.execute("SELECT nodes FROM workflow_entity WHERE id = ?", (WORKFLOW_ID,))
    nodes = json.loads(cursor.fetchone()[0])
    
    for node in nodes:
        if node['name'] == 'Route Decision':
            print("🛠️ Correcting return format in Route Decision (v2 compatible)...")
            
            # Formato n8n Code v2: 
            # Output 0 (Arriba): Final Response
            # Output 1 (Abajo): Actor Prep
            
            node['parameters']['jsCode'] = """// Ruteo compatible con n8n Code v2
const item = $input.item.json;
const isDone = item.planner_output?.is_done_string;

if (isDone === "TRUE") {
  // TRUE -> Final Response (Output 0 / Arriba)
  // Formato: [[item], []] -> el item sale por el primer puerto
  return [[{ json: item }], []];
} else {
  // FALSE -> Actor Prep (Output 1 / Abajo)
  // Formato: [[], [item]] -> el item sale por el segundo puerto
  return [[], [{ json: item }]];
}"""
            print("✅ Format and logic updated.")
            break
            
    # Guardar
    cursor.execute(
        "UPDATE workflow_entity SET nodes = ?, updatedAt = datetime('now') WHERE id = ?",
        (json.dumps(nodes), WORKFLOW_ID)
    )
    db_conn.commit()
    db_conn.close()

if __name__ == "__main__":
    patch()
    print("✅ VEGA v19 Applied: Corrected Code Return Format. HAZ F5.")
