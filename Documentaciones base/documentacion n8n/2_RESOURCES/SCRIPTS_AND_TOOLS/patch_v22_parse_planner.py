#!/usr/bin/env python3
"""
⭐ VEGA v22: PARANOID PARSE PLANNER
Sanitizes the 'Parse Planner' node to ensure it NEVER returns a non-object json.
"""

import sqlite3
import json
from pathlib import Path

N8N_DB = Path.home() / ".n8n" / "database.sqlite"
# ID del workflow "Yes" / "Herramienta Definitiva"
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
        if node['name'] == 'Parse Planner':
            print("found Parse Planner node. Applying paranoid fix...")
            found = True
            
            # This updated code wraps the entire logic in a try-catch and forces a valid object return
            node['parameters']['jsCode'] = """// VEGA v22: Paranoid Parse Planner
const items = $input.all();
const returnItems = [];

for (const item of items) {
  let output = {};
  
  try {
    // 1. Paranoid Input Check
    const inputJson = (item.json && typeof item.json === 'object' && !Array.isArray(item.json)) ? item.json : {};
    
    // 2. Extract Response from Gemini
    const geminiText = inputJson.response || inputJson.text || "";
    let parsed = {};
    
    // 3. Robust JSON Parsing
    try {
        // Try to find JSON block ```json ... ```
        const jsonMatch = geminiText.match(/```json\\s*([\\s\\S]*?)\\s*```/) || geminiText.match(/\\{.*\\}/s);
        if (jsonMatch) {
            parsed = JSON.parse(jsonMatch[1] || jsonMatch[0]);
        } else {
            // Fallback: treat whole text as thought if no JSON found
            parsed = { thought: geminiText };
        }
    } catch (e) {
        parsed = { thought: "Error parsing JSON: " + geminiText, error: e.message };
    }
    
    // 4. Normalization
    parsed.thought = parsed.thought || "No thought provided";
    
    let isDoneString = "FALSE";
    if (parsed.is_done === true || String(parsed.is_done).toLowerCase() === 'true') {
        isDoneString = "TRUE";
    }
    
    // Emergency Guard
    if (isDoneString === "FALSE" && !parsed.next_instruction && !parsed.tool_code) {
         // If not done and no instruction, force thought as instruction or fail gracefully
         if (parsed.thought.length > 0) {
            parsed.next_instruction = "generate_thought"; // Dummy instruction to keep moving
         } else {
            isDoneString = "TRUE";
            parsed.final_response = "Error: Agent produced empty output.";
         }
    }

    // 5. Construct Safe Output
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
    // CATASTROPHIC FAILURE HANDLING
    output = {
        error: error.message,
        planner_output: {
            is_done_string: "TRUE",
            final_response: "System Critical Error in Parse Planner: " + error.message
        }
    };
  }

  // 6. Return Clean Item
  returnItems.push({
    json: output,
    binary: item.binary
  });
}

return returnItems;"""
            
            break
            
    if not found:
        print("❌ Parse Planner node not found!")
        return

    cursor.execute(
        "UPDATE workflow_entity SET nodes = ?, updatedAt = datetime('now') WHERE id = ?",
        (json.dumps(nodes), WORKFLOW_ID)
    )
    db_conn.commit()
    db_conn.close()
    print("✅ Patch v22 (Parse Planner) applied. RESTART REQUIRED.")

if __name__ == "__main__":
    patch()
