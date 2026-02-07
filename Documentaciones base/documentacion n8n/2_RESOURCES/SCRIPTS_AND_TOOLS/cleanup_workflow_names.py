#!/usr/bin/env python3
"""
🔧 Cleanup Workflow Names and Nodes
1. Renames nodes ending in '1' (stripping the suffix).
2. Deletes 'Output to Chat1' as it is redundant.
3. Updates all connections to reflect name changes.
"""

import sqlite3
import json
import sys
import os
from pathlib import Path

# Configuración
N8N_DB = Path.home() / ".n8n" / "database.sqlite"
WORKFLOW_ID = "Urf7HpECFvfQooAv"

# Nodes to specifically delete
DELETE_NODES = ["Output to Chat1"]

# Mapping for renaming (calculated dynamically but good to have explicit logic)
def get_clean_name(name):
    if name.endswith("1"):
        return name[:-1]
    return name

def get_workflow_from_db():
    conn = sqlite3.connect(N8N_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT id, nodes, connections, name FROM workflow_entity WHERE id = ?", (WORKFLOW_ID,))
    result = cursor.fetchone()
    conn.close()
    if not result: return None
    workflow_id, nodes, connections, name = result
    return {'id': workflow_id, 'nodes': json.loads(nodes) if nodes else [], 'connections': json.loads(connections) if connections else {}, 'name': name}

def cleanup_workflow(workflow):
    nodes = workflow['nodes']
    connections = workflow['connections']
    
    # 1. Build Rename Map & Filter Nodes
    rename_map = {}
    valid_nodes = []
    
    print("📋 Analyizing nodes...")
    for node in nodes:
        old_name = node['name']
        
        # Check deletion
        if old_name in DELETE_NODES:
            print(f"   🗑️ Deleting redundant node: {old_name}")
            continue
            
        # Check renaming
        new_name = get_clean_name(old_name)
        if new_name != old_name:
            print(f"   ✏️ Renaming: {old_name} -> {new_name}")
            rename_map[old_name] = new_name
            node['name'] = new_name
        
        valid_nodes.append(node)
    
    workflow['nodes'] = valid_nodes
    
    # 2. Rebuild Connections
    new_connections = {}
    print("\n🔗 Updating connections...")
    
    for source_node, outputs in connections.items():
        # Determine new source name
        if source_node in DELETE_NODES:
            continue
        
        new_source = rename_map.get(source_node, source_node)
        
        new_outputs = {}
        # outputs is usually { "main": [ [ {node, type, index} ] ] }
        for output_type, output_list in outputs.items():
            new_output_list = []
            for sub_list in output_list:
                new_sub_list = []
                for conn in sub_list:
                    target_node = conn['node']
                    
                    # If target is deleted, skip connection
                    if target_node in DELETE_NODES:
                        continue
                        
                    # Rename target if needed
                    new_target = rename_map.get(target_node, target_node)
                    conn['node'] = new_target
                    new_sub_list.append(conn)
                
                if new_sub_list:
                    new_output_list.append(new_sub_list)
            
            if new_output_list:
                new_outputs[output_type] = new_output_list
            
        if new_outputs:
            new_connections[new_source] = new_outputs

    workflow['connections'] = new_connections
    return len(rename_map) + len(DELETE_NODES)

def save_workflow_to_db(workflow):
    conn = sqlite3.connect(N8N_DB)
    cursor = conn.cursor()
    cursor.execute("UPDATE workflow_entity SET nodes = ?, connections = ?, updatedAt = datetime('now') WHERE id = ?", (json.dumps(workflow['nodes']), json.dumps(workflow['connections']), workflow['id']))
    conn.commit()
    conn.close()

def main():
    print("🧹 Cleaning up workflow names and redundant nodes...\n")
    workflow = get_workflow_from_db()
    if not workflow:
        print("Workflow not found")
        sys.exit(1)
    
    changes = cleanup_workflow(workflow)
    if changes > 0:
        save_workflow_to_db(workflow)
        print(f"\n✅ Cleaned {changes} items. REFRESH N8N (F5) NOW.")
    else:
        print("\n⚠️ No changes needed.")

if __name__ == "__main__":
    main()
