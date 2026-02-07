#!/usr/bin/env python3
"""
⭐ VEGA v18: LOGIC SWAP (MATCH VISUALS)
El usuario conectó manualmente:
- Arriba (Output 0) -> Final Response
- Abajo (Output 1) -> Actor Prep

Pero mi lógica actual es al revés (0 -> Actor, 1 -> Final).
Acción: Invertir la lógica del Code Node para coincidir con el cableado visual del usuario.
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
            print("🔄 Swapping logic in Route Decision to match visual wiring...")
            
            # Lógica anterior:
            # if (isDone === "TRUE") return [null, {json: item}] (Output 1)
            # else return [{json: item}, null] (Output 0)
            
            # Nueva Lógica (Invertida):
            # Output 0 (Arriba) -> Final Response
            # Output 1 (Abajo) -> Actor Prep
            
            node['parameters']['jsCode'] = """// Ruteo simple basado en is_done_string
const item = $input.item.json;
const isDone = item.planner_output?.is_done_string;

if (isDone === "TRUE") {
  // TRUE -> Final Response (Output 0 / Arriba)
  return [{ json: item }, null];
} else {
  // FALSE -> Actor Prep (Output 1 / Abajo)
  return [null, { json: item }];
}"""
            print("✅ Logic swapped.")
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
    print("✅ VEGA v18 Appplied: Logic matched to visuals. HAZ F5.")
