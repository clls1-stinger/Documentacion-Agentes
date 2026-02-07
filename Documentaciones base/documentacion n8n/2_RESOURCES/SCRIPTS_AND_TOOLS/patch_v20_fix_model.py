#!/usr/bin/env python3
"""
⭐ VEGA v20: AUTONOMOUS FIX & TEST
1. Fix model name in Gemini Planner (gemini-2.5-pro -> gemini-1.5-flash).
2. Ensure everything is ready for autonomous execution.
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
    
    # 1. Corregir Gemini Planner
    for node in nodes:
        if node['name'] == 'Gemini Planner':
            print(f"🛠️ Fixing model in {node['name']}...")
            node['parameters']['model'] = 'gemini-1.5-flash'
            
        if node['name'] == 'Gemini Actor':
            print(f"🛠️ Fixing model in {node['name']}...")
            node['parameters']['model'] = 'gemini-1.5-flash'

    # Guardar
    cursor.execute(
        "UPDATE workflow_entity SET nodes = ?, updatedAt = datetime('now') WHERE id = ?",
        (json.dumps(nodes), WORKFLOW_ID)
    )
    db_conn.commit()
    db_conn.close()

if __name__ == "__main__":
    patch()
    print("✅ VEGA v20 Applied. Model fixed to gemini-1.5-flash.")
