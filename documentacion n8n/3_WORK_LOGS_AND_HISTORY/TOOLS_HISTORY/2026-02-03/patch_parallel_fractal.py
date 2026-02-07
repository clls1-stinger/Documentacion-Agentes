#!/usr/bin/env python3
"""
🔧 Patch Parallel Fractal Architecture (V2)
"""
import sqlite3
import json
import sys
from pathlib import Path

N8N_DB = Path.home() / ".n8n" / "database.sqlite"
WORKFLOW_NAME = "Gemini ReAct Agent - Patched V11"

def get_workflow_from_db():
    conn = sqlite3.connect(N8N_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT id, nodes, connections, staticData, settings, name FROM workflow_entity WHERE name = ?", (WORKFLOW_NAME,))
    result = cursor.fetchone()
    conn.close()
    if not result:
        print(f"❌ Workflow '{WORKFLOW_NAME}' not found")
        sys.exit(1)
    return {'id': result[0], 'nodes': json.loads(result[1]), 'connections': json.loads(result[2]), 'name': result[5]}

def save_workflow_to_db(workflow):
    conn = sqlite3.connect(N8N_DB)
    cursor = conn.cursor()
    cursor.execute("UPDATE workflow_entity SET nodes = ?, connections = ? WHERE id = ?", 
                   (json.dumps(workflow['nodes']), json.dumps(workflow['connections']), workflow['id']))
    conn.commit()
    conn.close()
    print(f"✅ Saved workflow {workflow['id']}")

def patch_clean_actor(workflow):
    print("PATCHING Clean Actor...")
    for node in workflow['nodes']:
        if node['name'] == 'Clean Actor':
            node['parameters']['jsCode'] = """
const item = $input.item.json;
let raw = item.response || "{}";
let parsed = {};
try {
    parsed = JSON.parse(raw);
} catch (e) {
    parsed = { ejecuciones: [] };
}

let actions = parsed.ejecuciones || [];

// Map each action to a separate item
return actions.map(a => ({
  json: {
    accion: a.herramienta, 
    datos: a.parametros,
    // Shared Context
    user_goal: item.user_goal,
    history: item.history,
    counter: item.counter
  }
}));
"""
            print("  -> Updated Clean Actor JS Code")
            return
    print("  -> ERROR: Clean Actor node not found")

def patch_tool_router(workflow):
    print("PATCHING Tool Router...")
    # Update logic to match observed connections
    # 0 -> Drive Search
    # 1 -> Drive Download
    # 2 -> Drive Upload
    # 3 -> Execute Command
    # 4 -> Read Disk
    # 5 -> Execute Command (Puppeteer)
    
    for node in workflow['nodes']:
        if node['name'] == 'Tool Router':
            node['type'] = 'n8n-nodes-base.switch'
            # We don't change 'typeVersion' blindly, assuming it is compatible or already 3. 
            # If it was strict Code node before, we might need to reset parameters completely.
            # Assuming it is already a Switch/Route logic node or we force it.
            
            node['parameters'] = {
                "dataType": "string",
                "value1": "={{ $json.accion }}",
                "rules": {
                    "rules": [
                        { "value2": "drive_search", "output": 0 },
                        { "value2": "download_file", "output": 1 },
                        { "value2": "upload_file", "output": 2 },
                        { "value2": "execute_command", "output": 3 },
                        { "value2": "read_file", "output": 4 },
                        { "value2": "browser_action", "output": 5 }
                    ]
                },
                "fallbackOutput": 4 # Fallback to read file or maybe error? Let's use 4 for now.
            }
            print("  -> Updated Tool Router Rules")
            return
    print("  -> ERROR: Tool Router node not found")

def patch_aggregator(workflow):
    print("PATCHING Aggregator...")
    for node in workflow['nodes']:
        if node['name'] == 'Aggregator':
            node['parameters']['jsCode'] = """
const items = $input.all();
if (items.length === 0) return [{ json: { error: "No items to aggregate" } }];

const first = items[0].json;

// Helper to extract result string and structured data
const getResult = (i) => {
    // If it's a binary file download, result is "Binary processed"
    if (i.binary) return "Binary file processed";
    
    // Check various result fields
    if (i.json.stdout) return i.json.stdout;
    if (i.json.tool_result) return i.json.tool_result;
    
    // For Drive Search or others that return array of objects
    if (i.json.id && i.json.name) return `[FILE] ${i.json.name} (${i.json.id})`;
    
    return JSON.stringify(i.json);
};

const results = items.map(i => ({
    tool: i.json.action_taken || i.json.accion,
    result: getResult(i),
    data: i.json.tool_result_data || i.json // Store full data if needed
}));

return [{
    json: {
        results: results,
        actions_completed: items.length,
        user_goal: first.user_goal,
        history: first.history,
        counter: first.counter
    }
}];
"""
            print("  -> Updated Aggregator JS")
            return 
    print("  -> ERROR: Aggregator node not found")

def patch_update_state(workflow):
    print("PATCHING Update State...")
    for node in workflow['nodes']:
        if node['name'] == 'Update State':
            node['parameters']['jsCode'] = """
const item = $input.item.json;
const newHistory = item.history || [];

// Add the consolidated results of this turn
newHistory.push({
    role: "tool_outputs",
    content: JSON.stringify(item.results, null, 2)
});

// Pass to memory/next step
return {
    json: {
        history: newHistory,
        user_goal: item.user_goal,
        counter: item.counter,
        action_taken: "parallel_execution",
        tool_result: "Executed " + item.actions_completed + " actions",
        tool_result_data: item.results
    }
};
"""
            print("  -> Updated Update State JS")
            return
    print("  -> ERROR: Update State node not found")

def main():
    print(f"Applying patches to: {WORKFLOW_NAME}")
    wf = get_workflow_from_db()
    patch_clean_actor(wf)
    patch_tool_router(wf)
    patch_aggregator(wf)
    patch_update_state(wf)
    save_workflow_to_db(wf)

if __name__ == "__main__":
    main()
