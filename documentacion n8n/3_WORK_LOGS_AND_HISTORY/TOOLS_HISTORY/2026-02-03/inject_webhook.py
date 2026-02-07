#!/usr/bin/env python3
import sqlite3
import json
import sys
from pathlib import Path

N8N_DB = Path.home() / ".n8n" / "database.sqlite"
WORKFLOW_NAME = "Gemini ReAct Agent - Patched V11"

def inject_webhook():
    conn = sqlite3.connect(N8N_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT id, nodes, connections FROM workflow_entity WHERE name = ?", (WORKFLOW_NAME,))
    result = cursor.fetchone()
    
    if not result:
        print(f"❌ Workflow '{WORKFLOW_NAME}' not found")
        return

    wf_id, nodes_json, connections_json = result
    nodes = json.loads(nodes_json)
    connections = json.loads(connections_json)
    
    # Check if webhook exists
    for node in nodes:
        if node['name'] == 'Webhook_Testing':
            print("⚠️ Webhook 'Webhook_Testing' already exists")
            return
            
    webhook_node = {
        "parameters": {
            "httpMethod": "POST",
            "path": "test_agent_v1",
            "options": {}
        },
        "name": "Webhook_Testing",
        "type": "n8n-nodes-base.webhook",
        "typeVersion": 1,
        "position": [400, 300],
        "webhookId": "test-agent-v1-id"
    }
    
    nodes.append(webhook_node)
    
    # Connect to "Read History" (assuming it exists) or "Clean Actor" if we want to bypass history?
    # Original plan was "Read History".
    target_node_name = "Read History"
    
    # Check if target exists
    if not any(n['name'] == target_node_name for n in nodes):
        print(f"Warning: {target_node_name} not found, connecting to Clean Actor directly?")
        target_node_name = "Clean Actor" # Fallback
    
    if "Webhook_Testing" not in connections:
        connections["Webhook_Testing"] = {"main": [[{"node": target_node_name, "type": "main", "index": 0}]]}
        
    print(f"✅ Injecting Webhook_Testing connected to {target_node_name}")
    
    cursor.execute("UPDATE workflow_entity SET nodes = ?, connections = ? WHERE id = ?", 
                   (json.dumps(nodes), json.dumps(connections), wf_id))
    conn.commit()
    conn.close()
    print("Saved changes.")

inject_webhook()
