#!/usr/bin/env python3
"""
🛰️ Vega Core Authority v6: STEALTH ROUTING & FORENSICS
1. Bulletproof Switch: Uses 'equals true' (explicit boolean).
2. Forensic Logging: Each node now logs its decision in the output JSON.
3. Fallback Guard: Final Response will show 'Routing Error' if reached with is_done=false.
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
            print("   ✏️ Patching 'Parse Planner' v6...")
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

// NORMALIZACIÓN DE BOOLEANOS
let isDone = false;
if (parsed.is_done === true || String(parsed.is_done).toLowerCase() === 'true') {
  isDone = true;
}

// GUARDIA DE EMERGENCIA: Si no hay instrucción y no dice que terminó, es un limbo.
if (!isDone && !parsed.next_instruction) {
  isDone = true;
  parsed.final_response = "El agente no proporcionó instrucciones ni marcó el fin. Finalizando por seguridad.";
}

const output = { 
  ...item, 
  planner_output: { 
    ...parsed, 
    is_done: isDone,
    debug_timestamp: new Date().toISOString()
  } 
};

return [{ json: output }];"""

        if node['name'] == 'Is Done Switch':
            print("   ✏️ Patching 'Is Done Switch' v6 (Explicit Equals)...")
            node['parameters']['rules'] = {
                "values": [
                    {
                        "conditions": {
                            "conditions": [
                                {
                                    "leftValue": "={{ $json.planner_output.is_done }}",
                                    "operator": {
                                        "type": "boolean",
                                        "operation": "equals"
                                    },
                                    "rightValue": True
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
            print("   ✏️ Patching 'Final Response' for Debugging...")
            node['parameters']['assignments']['assignments'][0]['value'] = "={{ $json.planner_output.is_done ? $json.planner_output.final_response : 'ERROR DE RUTEO: El Switch mandó aquí un is_done=' + $json.planner_output.is_done }}"

    cursor.execute("UPDATE workflow_entity SET nodes = ?, updatedAt = datetime('now') WHERE id = ?", 
                  (json.dumps(nodes), WORKFLOW_ID))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    patch()
    print("\n✅ Vega v6 applied. HAZ F5 (RECARGA TOTAL).")
