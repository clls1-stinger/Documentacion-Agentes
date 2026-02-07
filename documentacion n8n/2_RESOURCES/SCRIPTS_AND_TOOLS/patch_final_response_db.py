#!/usr/bin/env python3
"""
🔧 Patch Final Response Node in DB
Fixes the missing fallback for empty responses directly in SQLite.
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

def patch_final_response(workflow):
    nodes = workflow['nodes']
    patched = 0
    
    for node in nodes:
        if node['name'] == 'Final Response':
            print(f"   Found Final Response node.")
            # Check assignments
            assignments = node.get('parameters', {}).get('assignments', {}).get('assignments', [])
            for assign in assignments:
                if assign['name'] == 'response':
                    old_val = assign['value']
                    # The robust fallback expression
                    new_val = "={{ $json.planner_output.final_response || '(Agent finished without text response)' }}"
                    
                    if old_val != new_val:
                        print(f"   ✏️ Updating assignment: {old_val} -> {new_val}")
                        assign['value'] = new_val
                        patched += 1
                    else:
                        print("   ✅ Assignment already correct.")
                        
    return patched

def save_workflow_to_db(workflow):
    conn = sqlite3.connect(N8N_DB)
    cursor = conn.cursor()
    cursor.execute("UPDATE workflow_entity SET nodes = ?, updatedAt = datetime('now') WHERE id = ?", (json.dumps(workflow['nodes']), workflow['id']))
    conn.commit()
    conn.close()

def main():
    print("🔧 Patching 'Final Response' node fallback...\n")
    workflow = get_workflow_from_db()
    if not workflow:
        print("Workflow not found")
        sys.exit(1)
    
    count = patch_final_response(workflow)
    if count > 0:
        save_workflow_to_db(workflow)
        print(f"\n✅ Patched {count} node(s). REFRESH N8N (F5) NOW.")
    else:
        print("\n⚠️ No changes needed.")

if __name__ == "__main__":
    main()
