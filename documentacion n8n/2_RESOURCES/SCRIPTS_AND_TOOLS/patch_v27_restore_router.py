#!/usr/bin/env python3
"""
⭐ VEGA v27: RESTORE ROUTER LOGIC
Restores the 'Route Decision' node to its functional logic ('v21')
after the 'Parse Planner' fix has been applied.
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
            print("Restoring functional logic to 'Route Decision' node...")
            found = True
            
            # This is the last known good logic from v21
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

// Logic from v19: Route to different outputs
// Output 0 (Top) is for TRUE (Done)
// Output 1 (Bottom) is for FALSE (Continue)
const finalDoneItems = doneItems.length > 0 ? doneItems : [];
const finalContinueItems = continueItems.length > 0 ? continueItems : [];

// As per the user's final wiring, Output 0 (Top) is Final Response, Output 1 (Bottom) is Actor Prep.
// My logic from v18 was: if (isDone) return [item, null]. This sends to Output 0.
// This matches the user's wiring. So the logic should be:
if (isDone === "TRUE") {
    return [doneItems, []];
} else {
    return [[], continueItems];
}

// Re-evaluating based on last trace... the logic was inverted
// Let's use the v19 logic which is clearer.
return [doneItems, continueItems];
"""
            # Correcting logic based on my v19 patch which was clearer
            # Output 0 (doneItems) -> Final Response
            # Output 1 (continueItems) -> Actor Prep
            node['parameters']['jsCode'] = """// VEGA v27 - Restored Logic (based on v19)
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

return [doneItems, continueItems];
"""
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
    print("✅ Route Decision logic restored successfully.")

if __name__ == "__main__":
    patch()
    print("\nKeep Moving Forward.")
