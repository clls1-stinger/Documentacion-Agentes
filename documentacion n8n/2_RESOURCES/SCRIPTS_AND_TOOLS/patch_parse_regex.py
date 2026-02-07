#!/usr/bin/env python3
"""
🔧 Patch Parse Planner - Regex Extraction
This script updates the 'Parse Planner' node to correctly extract JSON
from mixed output (e.g., when Gemini adds conversational filler before the JSON).
"""

import sqlite3
import json
import sys
import os
from pathlib import Path

# Configuración
N8N_DB = Path.home() / ".n8n" / "database.sqlite"
WORKFLOW_ID = "Urf7HpECFvfQooAv"

def get_workflow_from_db():
    conn = sqlite3.connect(N8N_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT id, nodes, name FROM workflow_entity WHERE id = ?", (WORKFLOW_ID,))
    result = cursor.fetchone()
    conn.close()
    if not result: return None
    return {'id': result[0], 'nodes': json.loads(result[1]), 'name': result[2]}

def patch_parse_logic(workflow):
    nodes = workflow['nodes']
    patched = 0
    
    # ADVANCED QUERY/REGEX PARSER
    # 1. Tries to parse directly.
    # 2. If fails, looks for first '{' and last '}' substring.
    # 3. If that fails, treats as plain text.
    new_parser_code = r"""const item = $input.item.json;
let raw = item.output || item.response || '{}';
let parsed = { is_done: false };

try {
  if (typeof raw === 'string') {
     // Intento 1: Parseo directo (limpiando markdown)
     let clean = raw.replace(/```json/g, '').replace(/```/g, '').trim();
     try {
       parsed = JSON.parse(clean);
     } catch(e1) {
       // Intento 2: Extracción por Regex (buscar primer { y ultimo })
       const firstOpen = clean.indexOf('{');
       const lastClose = clean.lastIndexOf('}');
       if (firstOpen !== -1 && lastClose > firstOpen) {
          const jsonSubstring = clean.substring(firstOpen, lastClose + 1);
          parsed = JSON.parse(jsonSubstring);
          // Opcional: Podríamos capturar el texto sobrante como "observación", pero por ahora lo descartamos.
       } else {
          throw new Error("No valid JSON found");
       }
     }
  } else {
     parsed = raw;
  }
} catch(e) {
  // Si falla todo, asumimos que es texto plano de chat
  parsed = {
    is_done: true,
    final_response: typeof raw === 'string' ? raw : "Error parseando respuesta del agente"
  };
}

// Normalización masiva
if (typeof parsed.is_done === 'string') {
    parsed.is_done = (parsed.is_done.toLowerCase() === 'true');
}
// Asegurar valor booleano
parsed.is_done = !!parsed.is_done; 

// Fallback de respuesta final
if (parsed.is_done) {
    if (!parsed.final_response || (typeof parsed.final_response === 'string' && parsed.final_response.trim() === '')) {
        parsed.final_response = "Entendido. Tarea completada."; 
    }
}

return [{ json: { ...item, planner_output: parsed } }];"""

    for node in nodes:
        if node['name'] == 'Parse Planner':
             print(f"   ✏️ Patching 'Parse Planner' with Regex Extraction Logic")
             node['parameters']['jsCode'] = new_parser_code
             patched += 1

    return patched

def save_workflow_to_db(workflow):
    conn = sqlite3.connect(N8N_DB)
    cursor = conn.cursor()
    cursor.execute("UPDATE workflow_entity SET nodes = ?, updatedAt = datetime('now') WHERE id = ?", (json.dumps(workflow['nodes']), workflow['id']))
    conn.commit()
    conn.close()

def main():
    print("🔧 Patching Parse Planner with Extract Logic...\n")
    workflow = get_workflow_from_db()
    if not workflow:
        print("Workflow 'Yes' not found")
        sys.exit(1)
    
    count = patch_parse_logic(workflow)
    if count > 0:
        save_workflow_to_db(workflow)
        print(f"\n✅ Patched {count} items. REFRESH N8N (F5) NOW.")
    else:
        print("\n⚠️ Node not found.")

if __name__ == "__main__":
    main()
