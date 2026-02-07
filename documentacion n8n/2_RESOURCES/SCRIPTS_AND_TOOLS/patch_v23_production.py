#!/usr/bin/env python3
"""
⭐ VEGA v23: PRODUCTION CLEANUP
1. Remove all debug "throw" errors from Parse Planner.
2. Ensure Parse Planner correctly handles the Gemini response.
3. Keep the working model and routing.
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
    nodes = json.loads(cursor.fetchone()[0])
    
    for node in nodes:
        if node['name'] == 'Parse Planner':
            print(f"🧹 Cleaning {node['name']} from debug codes...")
            node['parameters']['jsCode'] = """// VEGA v23: Standard Parse Planner
const items = $input.all();
const returnItems = [];

for (const item of items) {
  let output = {};
  try {
    const inputJson = item.json || {};
    const geminiText = inputJson.response || inputJson.text || "";
    let parsed = {};
    
    // Intentar extraer JSON de la respuesta
    const jsonMatch = geminiText.match(/```json\\s*([\\s\\S]*?)\\s*```/) || geminiText.match(/\\{.*\\}/s);
    if (jsonMatch) {
      parsed = JSON.parse(jsonMatch[1] || jsonMatch[0]);
    } else {
      parsed = { thought: geminiText, is_done: true, final_response: geminiText };
    }
    
    let isDoneString = (parsed.is_done === true || String(parsed.is_done).toUpperCase() === 'TRUE') ? "TRUE" : "FALSE";
    
    // Fallback si no hay instrucción ni es done
    if (isDoneString === "FALSE" && !parsed.next_instruction) {
      isDoneString = "TRUE";
      parsed.final_response = parsed.final_response || "No next instruction provided by model.";
    }

    output = {
      ...inputJson,
      planner_output: {
        ...parsed,
        is_done_string: isDoneString
      }
    };
  } catch (error) {
    output = {
      error: error.message,
      planner_output: { is_done_string: "TRUE", final_response: "Error en Parse Planner: " + error.message }
    };
  }
  returnItems.push({ json: output });
}
return returnItems;"""

    cursor.execute(
        "UPDATE workflow_entity SET nodes = ?, updatedAt = datetime('now') WHERE id = ?",
        (json.dumps(nodes), WORKFLOW_ID)
    )
    db_conn.commit()
    db_conn.close()

if __name__ == "__main__":
    patch()
    print("✅ VEGA v23 Applied. Workflow is now in Production mode (No debug dumper).")
