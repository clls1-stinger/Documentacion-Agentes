#!/usr/bin/env python3
"""
🔧 Patch Update Memory Node - Generates Binary for Save to Disk
"""

import sqlite3
import json
import sys
import os
from pathlib import Path

# Configuración
N8N_DB = Path.home() / ".n8n" / "database.sqlite"
WORKFLOW_NAME = "Yes"  # Name found in debug_workflow.json

def get_workflow_from_db():
    conn = sqlite3.connect(N8N_DB)
    cursor = conn.cursor()
    
    # Buscar workflow por nombre
    cursor.execute("""
        SELECT id, nodes, connections, name
        FROM workflow_entity 
        WHERE name = ?
    """, (WORKFLOW_NAME,))
    
    result = cursor.fetchone()
    conn.close()
    
    if not result:
        # Fallback search by ID if name changed? No, stick to name for now.
        print(f"❌ No se encontró el workflow '{WORKFLOW_NAME}' en la base de datos.")
        # Try to list all workflows to help user
        return None
    
    workflow_id, nodes, connections, name = result
    
    return {
        'id': workflow_id,
        'nodes': json.loads(nodes) if nodes else [],
        'connections': json.loads(connections) if connections else {},
        'name': name
    }

def patch_update_memory_nodes(workflow):
    nodes = workflow['nodes']
    modified_count = 0
    
    new_code = """const chatHistory = $input.item.json.chat_history || [];
const userGoal = $input.item.json.user_goal;
const aiResponse = $input.item.json.response;

chatHistory.push({
  user: userGoal,
  ai: aiResponse,
  timestamp: new Date().toISOString()
});

const content = JSON.stringify(chatHistory.slice(-20), null, 2);

return [{
  json: { response: aiResponse },
  binary: {
    data: {
      data: Buffer.from(content).toString('base64'),
      mimeType: 'application/json',
      fileExtension: 'json',
      fileName: 'history.json'
    }
  }
}];"""

    for node in nodes:
        if node['name'].startswith('Update Memory'):
            print(f"   found node: {node['name']}")
            node['parameters']['jsCode'] = new_code
            modified_count += 1
            
    return modified_count

def save_workflow_to_db(workflow):
    conn = sqlite3.connect(N8N_DB)
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE workflow_entity 
        SET nodes = ?, 
            updatedAt = datetime('now')
        WHERE id = ?
    """, (
        json.dumps(workflow['nodes']),
        workflow['id']
    ))
    
    conn.commit()
    conn.close()

def main():
    print("🔧 Patching 'Update Memory' nodes for binary output...\n")
    
    workflow = get_workflow_from_db()
    if not workflow:
        sys.exit(1)
        
    print(f"📖 Found workflow: {workflow['name']} (ID: {workflow['id']})")
    
    count = patch_update_memory_nodes(workflow)
    if count > 0:
        print(f"🔨 Patched {count} nodes.")
        save_workflow_to_db(workflow)
        print("💾 Changes saved to database.")
        print("✨ Please REFRESH your n8n browser tab (F5) to see the changes.")
    else:
        print("⚠️ No 'Update Memory' nodes found to patch.")

if __name__ == "__main__":
    main()
