#!/usr/bin/env python3
"""
🛰️ Vega Core Authority v7: NUCLEAR STRING COMPARISON
The problem: n8n's boolean Switch is unreliable.
The solution: Convert is_done to a STRING and compare against "TRUE"/"FALSE".
"""

import sqlite3
import json
from pathlib import Path

N8N_DB = Path.home() / ".n8n" / "database.sqlite"
WORKFLOW_ID = "Urf7HpECFvfQooAv"

def patch():
    conn = sqlite3.connect(N8N_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT nodes FROM workflow_entity WHERE id = ?", (WORKFLOW_ID,))
    nodes = json.loads(cursor.fetchone()[0])
    
    for node in nodes:
        if node['name'] == 'Parse Planner':
            print("   ✏️ Patching 'Parse Planner' v7 (STRING is_done)...")
            node['parameters']['jsCode'] = r"""const item = $input.item.json;
let raw = item.output || item.response || "";
let parsed = { is_done: false, final_response: null, next_instruction: null };

try {
  let text = (typeof raw === 'string') ? raw : JSON.stringify(raw);
  const match = text.match(/\{[\s\S]*\}/);
  if (match) {
    parsed = JSON.parse(match[0]);
  }
} catch(e) {
  parsed.is_done = true;
  parsed.final_response = "Error parsing agent JSON: " + e.message;
}

// CORRECCIÓN DE ALUCINACIONES
if (!parsed.next_instruction && parsed.tool_code) parsed.next_instruction = parsed.tool_code;
if (!parsed.next_instruction && parsed.tool_call) parsed.next_instruction = parsed.tool_call;

// NORMALIZACIÓN A STRING (NUCLEAR)
let isDoneString = "FALSE";
if (parsed.is_done === true || String(parsed.is_done).toLowerCase() === 'true') {
  isDoneString = "TRUE";
}

// GUARDIA DE EMERGENCIA
if (isDoneString === "FALSE" && !parsed.next_instruction) {
  isDoneString = "TRUE";
  parsed.final_response = "El agente no proporcionó instrucciones. Finalizando.";
}

const output = { 
  ...item, 
  planner_output: { 
    ...parsed, 
    is_done_string: isDoneString,  // <- NUEVO CAMPO DE STRING
    is_done_bool: (isDoneString === "TRUE"),
    debug_timestamp: new Date().toISOString()
  } 
};

return [{ json: output }];"""

        if node['name'] == 'Is Done Switch':
            print("   ✏️ Patching 'Is Done Switch' v7 (STRING comparison)...")
            node['parameters']['rules'] = {
                "values": [
                    {
                        "conditions": {
                            "conditions": [
                                {
                                    "leftValue": "={{ $json.planner_output.is_done_string }}",
                                    "operator": {
                                        "type": "string",
                                        "operation": "equals"
                                    },
                                    "rightValue": "TRUE"
                                }
                            ]
                        }
                    }
                ]
            }
            node['parameters']['options'] = {
                "fallbackOutput": "extra"
            }

        if node['name'] == 'Final Response':
            print("   ✏️ Patching 'Final Response' v7...")
            node['parameters']['assignments']['assignments'][0]['value'] = "={{ $json.planner_output.final_response || 'ERROR DE RUTEO: isDone=' + $json.planner_output.is_done_string }}"

    cursor.execute("UPDATE workflow_entity SET nodes = ?, updatedAt = datetime('now') WHERE id = ?", 
                  (json.dumps(nodes), WORKFLOW_ID))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    patch()
    print("\n✅ Vega v7 (NUCLEAR STRING) applied. HAZ F5.")
