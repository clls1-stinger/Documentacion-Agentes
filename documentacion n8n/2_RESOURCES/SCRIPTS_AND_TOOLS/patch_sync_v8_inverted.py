#!/usr/bin/env python3
"""
🛰️ Vega Core Authority v8: INVERTED LOGIC
El problema: El Switch va al puerto 0 siempre (bug de n8n).
La solución: Invertir la lógica - detectar FALSE en lugar de TRUE.
"""

import sqlite3
import json
from pathlib import Path

N8N_DB = Path.home() / ".n8n" / "database.sqlite"
WORKFLOW_ID = "Urf7HpECFvfQooAv"

def patch():
    conn = sqlite3.connect(N8N_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT nodes FROM workflow_entity WHERE id = ?", (WORKFLOW_ID,))
    nodes = json.loads(cursor.fetchone()[0])
    
    for node in nodes:
        if node['name'] == 'Is Done Switch':
            print("   ✏️ Patching 'Is Done Switch' v8 (INVERTED LOGIC)...")
            # INVERTIR: Ahora detectamos FALSE (continuar con herramientas)
            node['parameters']['rules'] = {
                "values": [
                    {
                        "conditions": {
                            "conditions": [
                                {
                                    "leftValue": "={{ $json.planner_output.is_done_string }}",
                                    "operator": {
                                        "type": "string",
                                        "operation": "equals"
                                    },
                                    "rightValue": "FALSE"  # <-- INVERTIDO
                                }
                            ]
                        }
                    }
                ]
            }
            # INVERTR TAMBIÉN: Ahora el fallback es "extra" (debe ir a Final Response)
            node['parameters']['options'] = {
                "fallbackOutput": "extra"
            }

    # ACTUALIZAR CONEXIONES: INVERTIR LOS PUERTOS
    cursor.execute("SELECT connections FROM workflow_entity WHERE id = ?", (WORKFLOW_ID,))
    conns = json.loads(cursor.fetchone()[0])
    
    # SWAP: Puerto 0 ↔ Puerto 1
    switch_conns = conns.get('Is Done Switch', {})
    original_0 = switch_conns['main'][0]
    original_1 = switch_conns['main'][1]
    
    switch_conns['main'][0] = original_1  # Ahora puerto 0 va a Actor Prep
    switch_conns['main'][1] = original_0  # Ahora puerto 1 va a Final Response
    
    print("   🔄 Swapped connections:")
    print(f"      Puerto 0 (regla coincide: FALSE)   → {switch_conns['main'][0]}")
    print(f"      Puerto 1 (fallback: TRUE)          → {switch_conns['main'][1]}")
    
    cursor.execute("UPDATE workflow_entity SET nodes = ?, connections = ?, updatedAt = datetime('now') WHERE id = ?", 
                  (json.dumps(nodes), json.dumps(conns), WORKFLOW_ID))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    patch()
    print("\n✅ Vega v8 (INVERTED LOGIC) applied. HAZ F5.")
