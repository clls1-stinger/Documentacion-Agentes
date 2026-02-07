#!/usr/bin/env python3
"""
⭐ VEGA v23: AGGREGATOR & MEMORY SHIELD
Patches 'Aggregator' and 'Update Memory' to be crash-resistant.
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
    updated_count = 0
    
    for node in nodes:
        if node['name'] == 'Aggregator':
            print("🛡️ Patching Aggregator...")
            node['parameters']['jsCode'] = """// VEGA v23: Paranoid Aggregator
let result = "Success";
let structured_data = null;
const items = $input.all();

try {
    if (items.length > 0) {
      if (items[0].json && items[0].json.id && items[0].json.name) {
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
    // Fallback if Clean Actor is unreachable (e.g. first run or weird loop)
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
} }];"""
            updated_count += 1

        elif node['name'] == 'Update Memory':
            print("🛡️ Patching Update Memory...")
            node['parameters']['jsCode'] = """// VEGA v23: Paranoid Memory Logic
const items = $input.all();
if (items.length === 0) return [{ json: { error: "No input for memory" } }];

const item = items[0].json;

// Defensive Property Access
const history = Array.isArray(item.history) ? item.history : [];
const newEntry = {
  role: "assistant", // Default to assistant action log
  content: `Action: ${item.action_taken || 'Unknown'}\\nResult: ${item.tool_result || 'No Result'}`
};

// Add to history
history.push(newEntry);

// Update Counter safely
let counter = typeof item.counter === 'number' ? item.counter : 0;
counter++;

// Build Clean Output
const output = {
  json: {
    user_goal: item.user_goal || "No Goal",
    history: history,
    counter: counter,
    chat_history: item.chat_history || [],
    last_tool_data: item.tool_result_data || null
  }
};

return [output];"""
            updated_count += 1

    if updated_count > 0:
        cursor.execute(
            "UPDATE workflow_entity SET nodes = ?, updatedAt = datetime('now') WHERE id = ?",
            (json.dumps(nodes), WORKFLOW_ID)
        )
        db_conn.commit()
        print(f"✅ Applied Patch v23 to {updated_count} nodes.")
    else:
        print("⚠️ No nodes matched for patching.")

    db_conn.close()

if __name__ == "__main__":
    patch()
