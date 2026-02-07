#!/usr/bin/env python3
"""
⭐ VEGA v24: THE INFALLIBLE ROUTER
Using the official n8n v2 array-of-arrays format with $input.all() 
to ensure multi-output compatibility.
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
            print(f"🛠️ Re-engineering {node['name']} for absolute stability...")
            node['parameters']['jsCode'] = """// VEGA v24: Infallible n8n v2 Multi-output Router
const allItems = $input.all();
const finalResponse = []; // Output 0 (Top)
const actorPrep = [];     // Output 1 (Bottom)

for (const item of allItems) {
    const isDone = item.json.planner_output?.is_done_string === "TRUE";
    
    if (isDone) {
        finalResponse.push(item);
    } else {
        actorPrep.push(item);
    }
}

// n8n v2 expects an array where each element is the array of items for that port
return [finalResponse, actorPrep];"""
            
            # Asegurar que el nodo tenga 2 salidas configuradas
            node['parameters']['mode'] = 'runOnceForAllItems'
            node['outputs'] = ['main', 'main']

    cursor.execute(
        "UPDATE workflow_entity SET nodes = ?, updatedAt = datetime('now') WHERE id = ?",
        (json.dumps(nodes), WORKFLOW_ID)
    )
    db_conn.commit()
    db_conn.close()

if __name__ == "__main__":
    patch()
    print("✅ VEGA v24 Applied. Router re-engineered.")
