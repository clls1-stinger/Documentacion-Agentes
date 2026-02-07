#!/usr/bin/env python3
"""
🛰️ Vega Core Authority v5: TRUST THE AGENT
1. Removes dangerous safety checks that force is_done=true.
2. Direct boolean routing (Back to basics).
3. Robust JSON extraction.
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
            print("   ✏️ Patching 'Parse Planner' v5 (Pure logic)...")
            node['parameters']['jsCode'] = r"""const item = $input.item.json;
let raw = item.output || item.response || "";
let parsed = { is_done: false, final_response: null, next_instruction: null };

try {
  let text = (typeof raw === 'string') ? raw : JSON.stringify(raw);
  // Extraer el JSON más grande encontrado
  const match = text.match(/\{[\s\S]*\}/);
  if (match) {
    parsed = JSON.parse(match[0]);
  }
} catch(e) {
  parsed.is_done = true;
  parsed.final_response = "Error parsing agent JSON: " + e.message;
}

// CORRECCIÓN DE ALUCINACIONES COMUNES
if (!parsed.next_instruction && parsed.tool_code) parsed.next_instruction = parsed.tool_code;
if (!parsed.next_instruction && parsed.tool_call) parsed.next_instruction = parsed.tool_call;

// NORMALIZACIÓN DE BOOLEANOS (Crítico para el Switch)
let isDone = false;
if (parsed.is_done === true || String(parsed.is_done).toLowerCase() === 'true') {
  isDone = true;
}

// Si terminó pero no hay respuesta, poner una genérica
if (isDone && (!parsed.final_response || parsed.final_response === "")) {
  parsed.final_response = "Acción completada.";
}

return [{ json: { ...item, planner_output: { ...parsed, is_done: isDone } } }];"""

        if node['name'] == 'Is Done Switch':
            print("   ✏️ Patching 'Is Done Switch' v5 (Native Boolean)...")
            # Volvemos a comparación booleana pura, pero con el campo ya normalizado
            node['parameters']['rules'] = {
                "values": [
                    {
                        "conditions": {
                            "conditions": [
                                {
                                    "leftValue": "={{ $json.planner_output.is_done }}",
                                    "operator": {
                                        "type": "boolean",
                                        "operation": "true"
                                    }
                                }
                            ]
                        }
                    }
                ]
            }
            node['parameters']['options'] = {
                "fallbackOutput": "extra"
            }

    cursor.execute("UPDATE workflow_entity SET nodes = ?, updatedAt = datetime('now') WHERE id = ?", 
                  (json.dumps(nodes), WORKFLOW_ID))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    patch()
    print("\n✅ Vega v5 applied. HAZ F5 (RECARGA TOTAL).")
