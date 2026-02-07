#!/usr/bin/env python3
"""
🔧 Patch Parse Planner Node - Fixes Null Response Issue
"""

import sqlite3
import json
import sys
import os
from pathlib import Path

# Configuración
N8N_DB = Path.home() / ".n8n" / "database.sqlite"
WORKFLOW_NAME = "Yes" 

def get_workflow_from_db():
    conn = sqlite3.connect(N8N_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT id, nodes, connections, name FROM workflow_entity WHERE name = ?", (WORKFLOW_NAME,))
    result = cursor.fetchone()
    conn.close()
    if not result: return None
    workflow_id, nodes, connections, name = result
    return {'id': workflow_id, 'nodes': json.loads(nodes) if nodes else [], 'connections': json.loads(connections) if connections else {}, 'name': name}

def patch_parse_planner_nodes(workflow):
    nodes = workflow['nodes']
    modified_count = 0
    
    new_code = """const item = $input.item.json;
let raw = item.output || item.response || '{}';
let parsed = { is_done: false };
try {
  parsed = (typeof raw === 'string') ? JSON.parse(raw) : raw;
} catch(e) {}

// Normalizar booleano
if (typeof parsed.is_done === 'string') parsed.is_done = parsed.is_done === 'true';

// Ensure final_response exists if is_done is true (Fix for null output)
if (parsed.is_done && !parsed.final_response) {
  parsed.final_response = "(El agente finalizó la tarea pero no generó una respuesta de texto)";
}

return [{ json: { ...item, planner_output: parsed } }];"""

    for node in nodes:
        if node['name'].startswith('Parse Planner'):
            print(f"   found node: {node['name']}")
            node['parameters']['jsCode'] = new_code
            modified_count += 1
            
    return modified_count

def save_workflow_to_db(workflow):
    conn = sqlite3.connect(N8N_DB)
    cursor = conn.cursor()
    cursor.execute("UPDATE workflow_entity SET nodes = ?, updatedAt = datetime('now') WHERE id = ?", (json.dumps(workflow['nodes']), workflow['id']))
    conn.commit()
    conn.close()

def main():
    print("🔧 Patching 'Parse Planner' nodes...\n")
    workflow = get_workflow_from_db()
    if not workflow:
        print("Workflow not found")
        sys.exit(1)
    
    count = patch_parse_planner_nodes(workflow)
    if count > 0:
        save_workflow_to_db(workflow)
        print(f"✅ Patched {count} nodes. REFRESH N8N (F5) NOW.")
    else:
        print("⚠️ No nodes patched.")

if __name__ == "__main__":
    main()
