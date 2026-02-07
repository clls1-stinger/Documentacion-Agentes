#!/usr/bin/env python3
"""
🔧 Patch Workflow - Add Chat Response Formatting Node after Save History
This script:
1. Adds a new 'Set' node named 'Format Chat Response' that strips binary data and keeps only the text 'response'.
2. Updates connections: Updates 'Save History to Disk1' to point to this new node.
3. Updates connections: 'Format Chat Response' will be the new terminal node.
"""

import sqlite3
import json
import sys
import os
from pathlib import Path
import uuid

# Configuración
N8N_DB = Path.home() / ".n8n" / "database.sqlite"
WORKFLOW_ID = "Urf7HpECFvfQooAv"

def get_workflow_from_db():
    conn = sqlite3.connect(N8N_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT id, nodes, connections, name FROM workflow_entity WHERE id = ?", (WORKFLOW_ID,))
    result = cursor.fetchone()
    conn.close()
    if not result: return None
    workflow_id, nodes, connections, name = result
    return {'id': workflow_id, 'nodes': json.loads(nodes) if nodes else [], 'connections': json.loads(connections) if connections else {}, 'name': name}

def patch_add_format_node(workflow):
    nodes = workflow['nodes']
    connections = workflow['connections']
    
    # 1. Check if 'Format Chat Response' already exists to avoid duplicates
    for node in nodes:
        if node['name'] == 'Format Chat Response':
            print("⚠️ 'Format Chat Response' node already exists.")
            return 0

    # 2. Find 'Save History to Disk1' node to position the new one
    save_node = next((n for n in nodes if n['name'] == 'Save History to Disk1'), None)
    if not save_node:
        print("❌ 'Save History to Disk1' node not found!")
        return 0

    # Calculate position for new node (to the right of Save History)
    pos_x = save_node['position'][0] + 250
    pos_y = save_node['position'][1]

    # 3. Create the new node definition
    new_node_id = str(uuid.uuid4())
    new_node = {
        "parameters": {
            "mode": "manual",
            "duplicateItem": False,
            "assignments": {
                "assignments": [
                    {
                        "id": "chat_resp",
                        "name": "response",
                        "value": "={{ $json.response }}",
                        "type": "string"
                    }
                ]
            },
            "options": {}
        },
        "id": new_node_id,
        "name": "Format Chat Response",
        "type": "n8n-nodes-base.set",
        "typeVersion": 3.4,
        "position": [pos_x, pos_y]
    }
    # Fix python boolean
    new_node['parameters']['duplicateItem'] = False

    nodes.append(new_node)
    
    # 4. Update Connections
    # Save History to Disk1 -> Format Chat Response
    if "Save History to Disk1" not in connections:
        connections["Save History to Disk1"] = {"main": [[{"node": "Format Chat Response", "type": "main", "index": 0}]]}
    else:
        # Append or replace? It should be the end, so usually empty.
        # But verify structure: connections[SourceNodeName] = { "main": [ [ {node: Target...} ] ] }
        print("   Updating connection for Save History to Disk1...")
        connections["Save History to Disk1"] = {"main": [[{"node": "Format Chat Response", "type": "main", "index": 0}]]}

    return 1

def save_workflow_to_db(workflow):
    conn = sqlite3.connect(N8N_DB)
    cursor = conn.cursor()
    cursor.execute("UPDATE workflow_entity SET nodes = ?, connections = ?, updatedAt = datetime('now') WHERE id = ?", (json.dumps(workflow['nodes']), json.dumps(workflow['connections']), workflow['id']))
    conn.commit()
    conn.close()

def main():
    print("🔧 Adding 'Format Chat Response' node to cleanup output...\n")
    workflow = get_workflow_from_db()
    if not workflow:
        print("Workflow 'Yes' not found")
        sys.exit(1)
    
    count = patch_add_format_node(workflow)
    if count > 0:
        save_workflow_to_db(workflow)
        print(f"✅ Added {count} node(s) and updated connections. REFRESH N8N (F5) NOW.")
    else:
        print("⚠️ No changes made.")

if __name__ == "__main__":
    main()
