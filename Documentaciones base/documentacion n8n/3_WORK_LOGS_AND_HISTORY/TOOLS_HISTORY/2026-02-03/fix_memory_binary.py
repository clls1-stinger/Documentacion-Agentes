import sqlite3
import json
from pathlib import Path

N8N_DB = Path.home() / ".n8n" / "database.sqlite"
WORKFLOW_NAME = "Yes"

def patch():
    conn = sqlite3.connect(N8N_DB)
    cursor = conn.cursor()
    
    # 1. Get Nodes and Connections
    cursor.execute("SELECT nodes, connections FROM workflow_entity WHERE name = ?", (WORKFLOW_NAME,))
    result = cursor.fetchone()
    if not result:
        print(f"Workflow '{WORKFLOW_NAME}' not found")
        return

    nodes = json.loads(result[0])
    connections = json.loads(result[1])
    
    # 2. Patch 'Update Memory' Node (Fix Binary Output)
    memory_node = next((n for n in nodes if n['name'] == 'Update Memory'), None)
    if memory_node:
        memory_node['parameters']['jsCode'] = """
// VEGA v24: Fixed Memory Logic with Binary Output
const items = $input.all();
if (items.length === 0) return [{ json: { error: "No input for memory" } }];

const item = items[0].json;

// 1. Update Technical History (Internal steps)
const history = Array.isArray(item.history) ? item.history : [];
if (item.action_taken) {
    history.push({
      role: "assistant",
      content: `Action: ${item.action_taken}\\nResult: ${item.tool_result || 'No Result'}`
    });
}

// 2. Update Chat History (Interaction with user)
let chatHistory = Array.isArray(item.chat_history) ? item.chat_history : [];
if (item.response && item.user_goal) {
    chatHistory.push({
      user: item.user_goal,
      ai: item.response,
      timestamp: new Date().toISOString()
    });
}

// 3. Update Counter
let counter = typeof item.counter === 'number' ? item.counter : 0;
counter++;

// 4. Prepare Binary Content (for history.json)
const content = JSON.stringify(chatHistory.slice(-20), null, 2);

return [{
  json: {
    user_goal: item.user_goal || "No Goal",
    history: history,
    counter: counter,
    chat_history: chatHistory,
    response: item.response || null,
    last_tool_data: item.tool_result_data || null
  },
  binary: {
    data: {
      data: Buffer.from(content).toString('base64'),
      mimeType: 'application/json',
      fileExtension: 'json',
      fileName: 'history.json'
    }
  }
}];
"""
        print("✅ Patched 'Update Memory' code.")
    
    # 3. Patch 'Save History to Disk' Node (Ensure dataPropertyName is set)
    save_node = next((n for n in nodes if n['name'] == 'Save History to Disk'), None)
    if save_node:
        save_node['parameters']['dataPropertyName'] = 'data'
        print("✅ Patched 'Save History to Disk' parameters.")

    # 4. Patch Connections for 'Route Decision' (Fix IF logic)
    # Output 0 (True) -> Final Response
    # Output 1 (False) -> Actor Prep
    if "Route Decision" in connections:
        connections["Route Decision"]["main"] = [
            [{"node": "Final Response", "type": "main", "index": 0}], # Output 0: TRUE
            [{"node": "Actor Prep", "type": "main", "index": 0}]      # Output 1: FALSE
        ]
        print("✅ Patched 'Route Decision' connections.")

    # 5. Save back to DB
    cursor.execute("UPDATE workflow_entity SET nodes = ?, connections = ? WHERE name = ?", 
                   (json.dumps(nodes), json.dumps(connections), WORKFLOW_NAME))
    conn.commit()
    conn.close()
    print("\\n✨ Workflow 'Yes' patched successfully. Please refresh n8n UI.")

if __name__ == "__main__":
    patch()
