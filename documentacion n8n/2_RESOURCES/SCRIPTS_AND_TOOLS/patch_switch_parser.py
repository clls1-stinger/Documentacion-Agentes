#!/usr/bin/env python3
import sqlite3
import json
import os
from pathlib import Path

N8N_DB = Path.home() / ".n8n" / "database.sqlite"
WORKFLOW_ID = "Urf7HpECFvfQooAv"

def patch_switch():
    conn = sqlite3.connect(N8N_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT nodes FROM workflow_entity WHERE id = ?", (WORKFLOW_ID,))
    nodes = json.loads(cursor.fetchone()[0])
    
    patched = False
    for node in nodes:
        if node['name'] == 'Is Done Switch':
            print("Patcheando Is Done Switch...")
            # Cambiamos a una comparación de string más robusta
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
            # Aseguramos que el fallback extra vaya a la salida 1
            node['parameters']['options'] = {
                "fallbackOutput": "extra"
            }
            patched = True
            
        if node['name'] == 'Parse Planner':
            print("Hardenizando Parse Planner...")
            node['parameters']['jsCode'] = """const item = $input.item.json;
let raw = item.output || item.response || "";
let parsed = { is_done: false };

try {
  let text = (typeof raw === 'string') ? raw : JSON.stringify(raw);
  const match = text.match(/\\{[\\s\\S]*\\}/);
  if (match) {
    parsed = JSON.parse(match[0]);
  } else if (text.trim() !== "") {
    parsed = { is_done: true, final_response: text };
  }
} catch(e) {
  parsed = { is_done: true, final_response: "Error al parsear: " + e.message };
}

// FORZAR BOOLEANOS REALES PARA N8N
parsed.is_done = (parsed.is_done === true || String(parsed.is_done).toLowerCase() === 'true');

if (parsed.is_done && (!parsed.final_response || parsed.final_response === "")) {
  parsed.final_response = "He completado la tarea solicitada.";
}

return [{ json: { ...item, planner_output: parsed } }];"""

    if patched:
        cursor.execute("UPDATE workflow_entity SET nodes = ?, updatedAt = datetime('now') WHERE id = ?", 
                      (json.dumps(nodes), WORKFLOW_ID))
        conn.commit()
    conn.close()
    return patched

if __name__ == "__main__":
    if patch_switch():
        print("✅ Switch y Parser actualizados. Haz F5.")
    else:
        print("❌ No se encontró el nodo.")
