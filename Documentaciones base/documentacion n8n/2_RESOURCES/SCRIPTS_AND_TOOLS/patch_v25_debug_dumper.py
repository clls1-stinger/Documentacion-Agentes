#!/usr/bin/env python3
"""
⭐ VEGA v25: DEBUG DUMPER
Inserts debug code into 'Parse Planner' to write its exact output
to a file before sending it to 'Route Decision'. This will let us
see the malformed data that is causing the crash.
"""

import sqlite3
import json
from pathlib import Path

N8N_DB = Path.home() / ".n8n" / "database.sqlite"
WORKFLOW_ID = "Urf7HpECFvfQooAv"
DEBUG_FILE = "/home/emky/n8n/debug_parse_planner_output.json"

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
        if node['name'] == 'Parse Planner':
            print("Applying v25 (corrected) Debug Dumper to 'Parse Planner' node...")
            found = True
            
            node['parameters']['jsCode'] = """// VEGA v22: Paranoid Parse Planner (with v25 Debug Dumper)
const items = $input.all();
const returnItems = [];

for (const item of items) {
  let output = {};
  
  try {
    const inputJson = (item.json && typeof item.json === 'object' && !Array.isArray(item.json)) ? item.json : {};
    const geminiText = inputJson.response || inputJson.text || "";
    let parsed = {};
    
    try {
        const jsonMatch = geminiText.match(/```json\s*([\s\S]*?)\s*```/) || geminiText.match(/\{.*\}/s);
        if (jsonMatch) {
            parsed = JSON.parse(jsonMatch[1] || jsonMatch[0]);
        } else {
            parsed = { thought: geminiText };
        }
    } catch (e) {
        parsed = { thought: "Error parsing JSON: " + geminiText, error: e.message };
    }
    
    parsed.thought = parsed.thought || "No thought provided";
    let isDoneString = "FALSE";
    if (parsed.is_done === true || String(parsed.is_done).toLowerCase() === 'true') {
        isDoneString = "TRUE";
    }
    
    if (isDoneString === "FALSE" && !parsed.next_instruction && !parsed.tool_code) {
         if (parsed.thought.length > 0) {
            parsed.next_instruction = "generate_thought";
         } else {
            isDoneString = "TRUE";
            parsed.final_response = "Error: Agent produced empty output.";
         }
    }

    output = {
      ...inputJson,
      planner_output: {
        ...parsed,
        is_done_string: isDoneString,
        is_done_bool: (isDoneString === "TRUE"),
        timestamp: new Date().toISOString()
      }
    };

  } catch (error) {
    output = {
        error: error.message,
        planner_output: {
            is_done_string: "TRUE",
            final_response: "System Critical Error in Parse Planner: " + error.message
        }
    };
  }

  returnItems.push({
    json: output,
    binary: item.binary
  });
}

// --- VEGA v25 DEBUG DUMPER ---
try {
    // Corrected: Use this.helpers.fs.writeFileSync
    this.helpers.fs.writeFileSync('" + DEBUG_FILE + "', JSON.stringify(returnItems, null, 2));
} catch (e) {
    // If logging fails, add it to the output to ensure visibility
    returnItems.push({ json: { debug_error: "Failed to write debug file: " + e.message } });
}
// --- END DUMPER ---

return returnItems;
"""
            break
            
    if not found:
        print("❌ Parse Planner node not found!")
        db_conn.close()
        return

    cursor.execute(
        "UPDATE workflow_entity SET nodes = ?, updatedAt = datetime('now') WHERE id = ?",
        (json.dumps(nodes), WORKFLOW_ID)
    )
    db_conn.commit()
    db_conn.close()
    print("✅ Diagnostic Dumper v25 (corrected) applied successfully.")

if __name__ == "__main__":
    patch()
    print("\nKeep Moving Forward.")
