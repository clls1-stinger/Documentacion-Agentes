#!/usr/bin/env python3
"""
⭐ VEGA v28: ERROR DUMPER
Injects code into 'Parse Planner' to throw its output as a controlled
error. This makes the data visible in the n8n logs without needing
to write a file, bypassing sandbox issues.
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
        if node['name'] == 'Parse Planner':
            print("Applying v28 Error Dumper to 'Parse Planner' node...")
            found = True
            
            # The code is the same as v22/v26, but with a throw statement at the end.
            node['parameters']['jsCode'] = """// VEGA v26 Logic (with v28 Error Dumper)
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
            parsed = { thought: geminiText, is_done: true, final_response: geminiText };
        }
    } catch (e) {
        parsed = { thought: "Error parsing JSON: " + geminiText, error: e.message, is_done: true, final_response: "Error parsing agent response." };
    }
    
    parsed.thought = parsed.thought || "No thought provided";
    let isDoneString = "FALSE";
    if (parsed.is_done === true || String(parsed.is_done).toLowerCase() === 'true') {
        isDoneString = "TRUE";
    }
    
    if (isDoneString === "FALSE" && !parsed.next_instruction) {
         isDoneString = "TRUE";
         parsed.final_response = "Agent did not provide next instruction. Finishing task.";
    }

    output = {
      ...inputJson,
      planner_output: {
        ...parsed,
        is_done_string: isDoneString,
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

  const finalJson = (output && typeof output === 'object') ? output : { error: "PANIC: Malformed output detected in Parse Planner", original_output: output };

  returnItems.push({
    json: finalJson,
    binary: item.binary
  });
}

// --- VEGA v28 ERROR DUMPER ---
// This will make the execution fail, but the error message in the logs
// will contain the exact data we need to inspect.
const debugData = JSON.stringify(returnItems, null, 2);
throw new NodeOperationError(this.getNode(), debugData, { itemIndex: 0 });


// This part is now unreachable, which is intentional for this debug step.
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
    print("✅ Error Dumper v28 applied successfully.")

if __name__ == "__main__":
    patch()
    print("\nKeep Moving Forward.")
