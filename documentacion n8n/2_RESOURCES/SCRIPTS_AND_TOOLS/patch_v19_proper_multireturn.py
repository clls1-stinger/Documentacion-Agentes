#!/usr/bin/env python3
"""
⭐ VEGA v19: FIX RETURN STRUCTURE
The previous patch (v18) used incorrect return format for n8n Code Node.
n8n expects [ArrayOutput0, ArrayOutput1], not [Item, null].
This patch fixes the jsCode to use proper array grouping.
Logic remains: Output 0 = TRUE (Done), Output 1 = FALSE (Continue).
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
        print("❌ Workflow not found. Check ID.")
        return

    nodes = json.loads(row[0])
    
    found = False
    for node in nodes:
        if node['name'] == 'Route Decision':
            print("found Route Decision node. updating code...")
            found = True
            
            # Correct n8n Code Node logic for multiple outputs
            node['parameters']['jsCode'] = """// Route based on is_done_string
// Logic: Output 0 (Top) = TRUE (Done), Output 1 (Bottom) = FALSE (Continue)

const items = $input.all();
const doneItems = [];
const continueItems = [];

for (const item of items) {
  const isDone = item.json.planner_output?.is_done_string;
  
  if (isDone === "TRUE") {
    doneItems.push(item);
  } else {
    continueItems.push(item);
  }
}

return [doneItems, continueItems];"""
            
            break
            
    if not found:
        print("❌ Route Decision node not found in workflow!")
        db_conn.close()
        return

    # Guardar
    cursor.execute(
        "UPDATE workflow_entity SET nodes = ?, updatedAt = datetime('now') WHERE id = ?",
        (json.dumps(nodes), WORKFLOW_ID)
    )
    db_conn.commit()
    db_conn.close()
    print("✅ Patch v19 applied successfully.")

if __name__ == "__main__":
    patch()
