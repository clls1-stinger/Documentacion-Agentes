#!/usr/bin/env python3
"""
🔧 Patch Chat Output Key
Updates 'Format Chat Response' node to output 'output' field instead of 'response'.
This is standardized for n8n Chat interface to display text cleanly.
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

def patch_output_key(workflow):
    nodes = workflow['nodes']
    patched = 0
    
    for node in nodes:
        if node['name'] == 'Format Chat Response':
            print(f"   Found 'Format Chat Response' node.")
            # Check assignments
            assignments = node.get('parameters', {}).get('assignments', {}).get('assignments', [])
            for assign in assignments:
                # We want to change the target name to 'output'
                # The value should be whatever the input text was (which is $json.response from previous node)
                current_name = assign['name']
                current_value = assign['value']
                
                print(f"   Current assignment: {current_name} = {current_value}")
                
                # Change target field name to 'output' (standard for n8n chat)
                if current_name != 'output':
                    print(f"   ✏️ Renaming output field: {current_name} -> output")
                    assign['name'] = 'output'
                    patched += 1
                
                # Ensure value calls the correct input property
                # The previous node (Save History) passes through the item from Update Memory, which has 'response'
                if assign['value'] != '={{ $json.response }}':
                     print(f"   ✏️ Correcting value expression: {assign['value']} -> {{$json.response}}")
                     assign['value'] = '={{ $json.response }}'
                     patched += 1
                        
    return patched

def save_workflow_to_db(workflow):
    conn = sqlite3.connect(N8N_DB)
    cursor = conn.cursor()
    cursor.execute("UPDATE workflow_entity SET nodes = ?, updatedAt = datetime('now') WHERE id = ?", (json.dumps(workflow['nodes']), workflow['id']))
    conn.commit()
    conn.close()

def main():
    print("🔧 Patching Chat Output Key to 'output'...\n")
    workflow = get_workflow_from_db()
    if not workflow:
        print("Workflow not found")
        sys.exit(1)
    
    count = patch_output_key(workflow)
    if count > 0:
        save_workflow_to_db(workflow)
        print(f"\n✅ Patched {count} items. REFRESH N8N (F5) NOW.")
    else:
        print("\n⚠️ Node is already configured correctly.")

if __name__ == "__main__":
    main()
