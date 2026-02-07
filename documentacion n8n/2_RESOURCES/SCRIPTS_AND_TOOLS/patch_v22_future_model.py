#!/usr/bin/env python3
"""
⭐ VEGA v22: THE MODEL FROM THE FUTURE
Using gemini-3-flash-preview as specified in user memory.
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
        if node['name'] in ['Gemini Planner', 'Gemini Actor']:
            print(f"🛠️ Setting model to gemini-3-flash-preview in {node['name']}...")
            node['parameters']['model'] = 'gemini-3-flash-preview'

    cursor.execute(
        "UPDATE workflow_entity SET nodes = ?, updatedAt = datetime('now') WHERE id = ?",
        (json.dumps(nodes), WORKFLOW_ID)
    )
    db_conn.commit()
    db_conn.close()

if __name__ == "__main__":
    patch()
    print("✅ VEGA v22 Applied. Modeled updated to gemini-3-flash-preview.")
