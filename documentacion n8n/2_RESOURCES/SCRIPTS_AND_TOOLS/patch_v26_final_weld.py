#!/usr/bin/env python3
"""
⭐ VEGA v26: THE FINAL WELD
1. Gemini Planner/Actor -> gemini-3-flash-preview
2. Route Decision -> n8n-nodes-base.if (v2)
3. Ensure Parse Planner is clean.
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
        # 1. Modelo
        if node['name'] in ['Gemini Planner', 'Gemini Actor']:
            node['parameters']['model'] = 'gemini-3-flash-preview'
        
        # 2. Ruteador
        if node['name'] == 'Route Decision':
            print(f"🛠️ Setting IF v2 in {node['name']}...")
            node['type'] = 'n8n-nodes-base.if'
            node['typeVersion'] = 2 # Intentar V2
            node['parameters'] = {
                "conditions": {
                    "options": {
                        "caseSensitive": True,
                        "leftValue": "",
                        "typeValidation": "strict"
                    },
                    "conditions": [
                        {
                            "id": "c6229606-f187-43ca-938b-d77759b6711e",
                            "leftValue": "={{ $json.planner_output.is_done_string }}",
                            "rightValue": "TRUE",
                            "operator": {
                                "type": "string",
                                "operation": "equals"
                            }
                        }
                    ],
                    "combinator": "and"
                }
            }

    cursor.execute(
        "UPDATE workflow_entity SET nodes = ?, updatedAt = datetime('now') WHERE id = ?",
        (json.dumps(nodes), WORKFLOW_ID)
    )
    db_conn.commit()
    db_conn.close()

if __name__ == "__main__":
    patch()
    print("✅ VEGA v26 Applied. Model set and IF v2 installed.")
