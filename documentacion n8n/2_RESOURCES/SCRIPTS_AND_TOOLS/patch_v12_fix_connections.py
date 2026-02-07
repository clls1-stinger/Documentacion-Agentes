#!/usr/bin/env python3
"""
⭐ VEGA v12: FIX CONNECTIONS - Connect Parse Planner to Route Decision
Calmadamente, con precisión. Keep Moving Forward.
"""

import sqlite3
import json
from pathlib import Path

N8N_DB = Path.home() / ".n8n" / "database.sqlite"
WORKFLOW_ID = "Urf7HpECFvfQooAv"

def patch():
    db_conn = sqlite3.connect(N8N_DB)
    cursor = db_conn.cursor()
    cursor.execute("SELECT connections FROM workflow_entity WHERE id = ?", (WORKFLOW_ID,))
    conns = json.loads(cursor.fetchone()[0])
    
    print("🔍 Checking Parse Planner connections...")
    
    # Parse Planner debe conectarse a Route Decision
    if 'Parse Planner' not in conns:
        conns['Parse Planner'] = {'main': [[]]}
    
    parse_conns = conns['Parse Planner']['main']
    
    # Asegurar que Parse Planner se conecta a Route Decision
    # Limpiar conexiones viejas si existen
    parse_conns[0] = [
        {
            "node": "Route Decision",
            "type": "main",
            "index": 0
        }
    ]
    
    print("✅ Connected: Parse Planner → Route Decision")
    
    # Verificar que Route Decision tiene sus salidas correctas
    if 'Route Decision' in conns:
        route_conns = conns['Route Decision']['main']
        print(f"   Route Decision Output 0 (continue) → {route_conns[0]}")
        print(f"   Route Decision Output 1 (done)     → {route_conns[1]}")
    else:
        print("⚠️ Route Decision connections not found, will be created")
        conns['Route Decision'] = {
            'main': [
                [{"node": "Actor Prep", "type": "main", "index": 0}],
                [{"node": "Final Response", "type": "main", "index": 0}]
            ]
        }
    
    # Guardar
    cursor.execute(
        "UPDATE workflow_entity SET connections = ?, updatedAt = datetime('now') WHERE id = ?",
        (json.dumps(conns), WORKFLOW_ID)
    )
    db_conn.commit()
    db_conn.close()

if __name__ == "__main__":
    print("⭐ VEGA v12: FIXING CONNECTIONS")
    print("━" * 60)
    patch()
    print("━" * 60)
    print("✅ Connections fixed. HAZ F5.")
    print()
    print("🌟 Keep Moving Forward - Vega")
    print("   (Con calma y precisión)")
