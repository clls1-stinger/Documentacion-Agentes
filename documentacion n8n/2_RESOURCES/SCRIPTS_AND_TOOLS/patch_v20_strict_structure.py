#!/usr/bin/env python3
"""
⭐ VEGA v20: FORCE CLEAN OBJECT STRUCTURE
The "json" property isn't an object error usually means we are passing something weird in the json field, 
or the item structure itself is malformed.
This patch forces a clean recreation of the output items.
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
            print("found Route Decision node. Applying v20 strict object fix...")
            found = True
            
            # Explicitly construct clean objects to satisfy n8n's strict validation
            node['parameters']['jsCode'] = """// VEGA v21: Paranoid Object Construction
const items = $input.all();
const doneItems = [];
const continueItems = [];

for (const item of items) {
  let jsonData = {};
  
  // PARANOID CHECK: Ensure json is a non-null object and NOT an array
  if (item.json && typeof item.json === 'object' && !Array.isArray(item.json)) {
    jsonData = item.json;
  }
  
  // Logic Check
  const isDone = jsonData?.planner_output?.is_done_string;

  // Construct a CLEAN new item to avoid 'json property is not object' errors
  // We preserve binary if it exists, but ensure json is an object
  const cleanItem = {
    json: jsonData,
    binary: item.binary,
    pairedItem: { item: item.pairedItem?.item || 0 }
  };

  if (isDone === "TRUE") {
    doneItems.push(cleanItem);
  } else {
    continueItems.push(cleanItem);
  }
}

return [doneItems, continueItems];"""
            
            break
            
    if not found:
        print("❌ Route Decision node not found!")
        return

    cursor.execute(
        "UPDATE workflow_entity SET nodes = ?, updatedAt = datetime('now') WHERE id = ?",
        (json.dumps(nodes), WORKFLOW_ID)
    )
    db_conn.commit()
    db_conn.close()
    print("✅ Patch v20 applied. F5 AGAIN.")

if __name__ == "__main__":
    patch()
