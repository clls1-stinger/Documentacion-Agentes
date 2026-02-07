#!/usr/bin/env python3
import sqlite3
import json
from pathlib import Path

N8N_DB = Path.home() / ".n8n" / "database.sqlite"
WORKFLOW_NAME = "Gemini ReAct Agent - Patched V11"

def update_webhook():
    conn = sqlite3.connect(N8N_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT id, nodes FROM workflow_entity WHERE name = ?", (WORKFLOW_NAME,))
    result = cursor.fetchone()
    
    if not result:
        print("Workflow not found")
        return

    wf_id, nodes_json = result
    nodes = json.loads(nodes_json)
    
    updated = False
    for node in nodes:
        if node['name'] == 'Webhook_Testing':
            node['parameters']['path'] = "test_agent_v2"
            updated = True
            print("Updated path to test_agent_v2")
            break
            
    if updated:
        cursor.execute("UPDATE workflow_entity SET nodes = ? WHERE id = ?", 
                       (json.dumps(nodes), wf_id))
        conn.commit()
        print("Saved changes")
    else:
        print("Webhook node not found to update")
    
    conn.close()

update_webhook()
