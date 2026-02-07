#!/usr/bin/env python3
"""
⭐ VEGA v29: INJECT TEST DATA
Abandons complex UI automation. This patch hardcodes the test message
into a Set node at the beginning of the workflow. This allows for a
simple "Test Workflow" click in the UI to trigger the test case,
bypassing all webhook/UI automation issues.
"""

import sqlite3
import json
from pathlib import Path
import uuid

N8N_DB = Path.home() / ".n8n" / "database.sqlite"
WORKFLOW_ID = "Urf7HpECFvfQooAv"
TEST_MESSAGE = "Navega a https://www.google.com y dime si la página carga correctamente."

def patch():
    db_conn = sqlite3.connect(N8N_DB)
    cursor = db_conn.cursor()
    cursor.execute("SELECT nodes, connections FROM workflow_entity WHERE id = ?", (WORKFLOW_ID,))
    nodes_raw, conns_raw = cursor.fetchone()
    nodes = json.loads(nodes_raw)
    conns = json.loads(conns_raw)
    
    # 1. Find the trigger node to position the new Set node
    trigger_node = next((n for n in nodes if n['type'] == '@n8n/n8n-nodes-langchain.manualChatTrigger'), None)
    if not trigger_node:
        print("❌ Trigger node not found!")
        return

    # 2. Create the new "Set" node for test data injection
    injector_node_name = "INJECT_TEST_DATA"
    injector_node = {
        "parameters": {
            "assignments": {
                "assignments": [
                    {
                        "id": str(uuid.uuid4()),
                        "name": "chatInput",
                        "value": TEST_MESSAGE
                    }
                ]
            },
            "options": {
                "keepOnlySet": False
            }
        },
        "id": str(uuid.uuid4()),
        "name": injector_node_name,
        "type": "n8n-nodes-base.set",
        "typeVersion": 3.4,
        "position": [trigger_node['position'][0] + 250, trigger_node['position'][1]]
    }
    
    # Add or update the injector node
    existing_injector_idx = next((i for i, n in enumerate(nodes) if n['name'] == injector_node_name), -1)
    if existing_injector_idx != -1:
        nodes[existing_injector_idx] = injector_node
        print(f"✅ Updated existing '{injector_node_name}' node.")
    else:
        nodes.append(injector_node)
        print(f"✅ Added new '{injector_node_name}' node.")

    # 3. Reroute connections
    # The trigger should now point to our injector node.
    # The injector node should then point to what the trigger was originally pointing to.
    
    original_target_node_name = conns[trigger_node['name']]['main'][0][0]['node']
    
    # Trigger -> INJECT_TEST_DATA
    conns[trigger_node['name']]['main'] = [[{ "node": injector_node_name, "type": "main", "index": 0 }]]
    
    # INJECT_TEST_DATA -> original target (e.g., Read History)
    conns[injector_node_name] = {
        "main": [[{ "node": original_target_node_name, "type": "main", "index": 0 }]]
    }
    
    print(f"🔗 Rerouted: {trigger_node['name']} -> {injector_node_name} -> {original_target_node_name}")
    
    # Ensure the Error Dumper is still in place in Parse Planner
    parse_planner_node = next((n for n in nodes if n['name'] == 'Parse Planner'), None)
    if "throw new NodeOperationError" not in parse_planner_node['parameters']['jsCode']:
        print("❌ CRITICAL: Error Dumper (v28) is missing from Parse Planner. Aborting.")
        return

    # Save to DB
    cursor.execute(
        "UPDATE workflow_entity SET nodes = ?, connections = ?, updatedAt = datetime('now') WHERE id = ?",
        (json.dumps(nodes), json.dumps(conns), WORKFLOW_ID)
    )
    db_conn.commit()
    db_conn.close()
    print("✅ Patch v29 (Inject Test Data) applied successfully.")

if __name__ == "__main__":
    patch()
    print("\nKeep Moving Forward. The next manual 'Test Workflow' execution will trigger the diagnostic.")
