#!/usr/bin/env python3
import sqlite3
import json
import os
from pathlib import Path

N8N_DB = Path.home() / ".n8n" / "database.sqlite"
WORKFLOW_ID = "Urf7HpECFvfQooAv"

def patch_ironclad():
    conn = sqlite3.connect(N8N_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT nodes FROM workflow_entity WHERE id = ?", (WORKFLOW_ID,))
    nodes = json.loads(cursor.fetchone()[0])
    
    for node in nodes:
        if node['name'] == 'Is Done Switch':
            print("Patcheando Is Done Switch (Modo Ironclad)...")
            # Cambiamos a comparación de string 'true' / 'false' que es infalible
            node['parameters']['rules'] = {
                "values": [
                    {
                        "conditions": {
                            "conditions": [
                                {
                                    "leftValue": "={{ String($json.planner_output.is_done).toLowerCase() }}",
                                    "operator": {
                                        "type": "string",
                                        "operation": "equals"
                                    },
                                    "rightValue": "true"
                                }
                            ]
                        }
                    }
                ]
            }
            node['parameters']['options'] = {
                "fallbackOutput": "extra"
            }
            
        if node['name'] == 'Parse Planner':
            print("Reforzando Parse Planner...")
            node['parameters']['jsCode'] = """const item = $input.item.json;
let raw = item.output || item.response || "";
let parsed = { is_done: false, final_response: null, next_instruction: null };

try {
  let text = (typeof raw === 'string') ? raw : JSON.stringify(raw);
  const match = text.match(/\\{[\\s\\S]*\\}/);
  if (match) {
    parsed = JSON.parse(match[0]);
  } else if (text.trim() !== "") {
    parsed = { is_done: true, final_response: text };
  }
} catch(e) {
  parsed = { is_done: true, final_response: "Error técnico: " + e.message };
}

// NORMALIZACIÓN ABSOLUTA PARA N8N
// Forzamos que is_done sea un booleano real basado en cualquier variante
let isDone = false;
if (parsed.is_done === true || String(parsed.is_done).toLowerCase() === 'true') {
  isDone = true;
} else if (parsed.next_instruction === null || parsed.next_instruction === "" || !parsed.next_instruction) {
  // Si no hay instrucción, DEBE haber terminado
  if (!parsed.is_done && !parsed.final_response) {
     isDone = true;
     parsed.final_response = "Tarea finalizada sin instrucciones adicionales.";
  }
}
parsed.is_done = isDone;

// Asegurar que si terminó, tenga un mensaje
if (parsed.is_done && (!parsed.final_response || parsed.final_response === "")) {
  parsed.final_response = "He completado tu solicitud.";
}

return [{ json: { ...item, planner_output: parsed } }];"""

    cursor.execute("UPDATE workflow_entity SET nodes = ?, updatedAt = datetime('now') WHERE id = ?", 
                  (json.dumps(nodes), WORKFLOW_ID))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    patch_ironclad()
    print("✅ Parche Ironclad aplicado. Por favor, haz F5 en n8n.")
