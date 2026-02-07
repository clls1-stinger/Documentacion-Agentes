#!/usr/bin/env python3
"""
⭐ VEGA v24: DIAGNOSTIC ROUTER
Replaces the logic in 'Route Decision' with a minimal passthrough
to determine if the input data itself is faulty.
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
    row = cursor.fetchone()
    
    if not row:
        print("❌ Workflow not found.")
        return

    nodes = json.loads(row[0])
    
    found = False
    for node in nodes:
        if node['name'] == 'Route Decision':
            print("Applying diagnostic code to 'Route Decision' node...")
            found = True
            
            # This code does no logic. It just passes the input from Parse Planner
            # to the first output. If this still fails, the input item is broken.
            node['parameters']['jsCode'] = """// VEGA v24: Diagnostic Passthrough
const items = $input.all();
const output0 = [];
const output1 = [];

// Pass all items to the first output (Actor Prep) to see if the error persists.
// This bypasses all internal logic of this node.
for (const item of items) {
  output0.push(item);
}

return [output0, output1];"""
            
            break
            
    if not found:
        print("❌ Route Decision node not found!")
        db_conn.close()
        return

    cursor.execute(
        "UPDATE workflow_entity SET nodes = ?, updatedAt = datetime('now') WHERE id = ?",
        (json.dumps(nodes), WORKFLOW_ID)
    )
    db_conn.commit()
    db_conn.close()
    print("✅ Diagnostic Patch v24 applied successfully.")

if __name__ == "__main__":
    patch()
    print("\nKeep Moving Forward.")
