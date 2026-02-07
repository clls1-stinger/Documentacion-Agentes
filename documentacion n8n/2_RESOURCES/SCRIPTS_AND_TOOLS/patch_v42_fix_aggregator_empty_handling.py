import json
import sqlite3
from pathlib import Path

N8N_DB = Path.home() / ".n8n" / "database.sqlite"
WORKFLOW_ID = "Urf7HpECFvfQooAv"

NEW_JS_CODE = r"""// VEGA v24: Paranoid Aggregator (Empty Handling)
let result = "Success";
let structured_data = null;
const items = $input.all();

try {
    if (items.length > 0) {
      // HANDLE EMPTY SEARCH RESULT (Always Output Data)
      if (items.length === 1 && Object.keys(items[0].json).length === 0) {
          result = "No results found.";
          structured_data = [];
      }
      else if (items[0].json && items[0].json.id && items[0].json.name) {
         // Drive Search result
         result = items.map(i => `[FILE] ${i.json.name} (${i.json.id})`).join(", ");
         structured_data = items.map(i => ({
           id: i.json.id,
           name: i.json.name,
           mimeType: i.json.mimeType || 'unknown'
         }));
      } else if (items[0].json && items[0].json.stdout) {
         result = items[0].json.stdout;
      } else if (items[0].binary) {
         result = "Binary processed";
      } else if (items[0].json && items[0].json.error) {
         result = "Error: " + items[0].json.error;
      }
    }
} catch (e) {
    result = "Error processing tool output: " + e.message;
}

// Access Previous State Defensively
let prev = {};
try {
    const cleanActor = $('Clean Actor').last();
    prev = (cleanActor && cleanActor.json) ? cleanActor.json : {};
} catch(e) {
    prev = {
        user_goal: "UNKNOWN (State Lost)",
        history: [],
        counter: 0,
        chat_history: []
    };
}

// Ensure critical fields exist
prev.history = Array.isArray(prev.history) ? prev.history : [];
prev.chat_history = Array.isArray(prev.chat_history) ? prev.chat_history : [];

return [{ json: {
  action_taken: prev.accion || "Unknown Action",
  tool_result: result,
  tool_result_data: structured_data,
  planner_instruction: prev.instruction || "No instruction",
  user_goal: prev.user_goal,
  history: prev.history,
  counter: prev.counter || 0,
  chat_history: prev.chat_history
} }];
"""

def fix_aggregator_empty():
    print(f"🔧 Applying Patch v42 - Fix Aggregator Empty Handling for {WORKFLOW_ID}...")
    conn = sqlite3.connect(N8N_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT nodes FROM workflow_entity WHERE id = ?", (WORKFLOW_ID,))
    result = cursor.fetchone()
    if not result:
        print("❌ Workflow not found")
        return
    
    nodes = json.loads(result[0])
    
    for node in nodes:
        if node['name'] == "Aggregator":
            print(f"  📦 Modifying node: {node['name']}")
            node['parameters']['jsCode'] = NEW_JS_CODE
            print(f"    ✅ Updated JS Code to handle empty JSON results")

    cursor.execute("UPDATE workflow_entity SET nodes = ?, name = ?, updatedAt = datetime('now') WHERE id = ?", 
                  (json.dumps(nodes), "Yes (Patched v42 - Aggregator Fix)", WORKFLOW_ID))
    conn.commit()
    conn.close()
    
    print(f"\n✅ Patch v42 applied. Aggregator will now correctly report 'No results found' to the Planner.")

if __name__ == "__main__":
    fix_aggregator_empty()
