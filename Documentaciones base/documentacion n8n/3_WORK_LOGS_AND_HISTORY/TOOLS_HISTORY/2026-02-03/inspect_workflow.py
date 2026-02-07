import sqlite3
import json
import os
from pathlib import Path

N8N_DB = Path.home() / ".n8n" / "database.sqlite"
TARGET_NAME = "Gemini ReAct Agent - Patched V11"

def list_workflows():
    conn = sqlite3.connect(N8N_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM workflow_entity")
    rows = cursor.fetchall()
    conn.close()
    print("Available Workflows:")
    for row in rows:
        print(f" - {row[0]}")

def get_workflow(name):
    conn = sqlite3.connect(N8N_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT nodes, connections FROM workflow_entity WHERE name = ?", (name,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    return json.loads(row[0]), json.loads(row[1])

list_workflows()

# Try to find a reasonable default if "Yes" isn't there
# It's likely "Gemini Chat Workflow" or similar based on file names
target = TARGET_NAME
# You can uncomment this if you want to hardcode the one you see in the list
# target = "Gemini Chat Workflow" 

res = get_workflow(target)

if res:
    nodes, connections = res
    print(f"\n--- INSPECTING: {target} ---")
    
    print("\n[TOOL ROUTER]")
    router_node = next((n for n in nodes if n['name'] == 'Tool Router'), None)
    if router_node:
        print(json.dumps(router_node, indent=2))
        print("\nCONNECTIONS FROM TOOL ROUTER:")
        if 'Tool Router' in connections:
            print(json.dumps(connections['Tool Router'], indent=2))
    else:
        print("Tool Router not found")

    print("\n[CLEAN ACTOR]")
    actor_node = next((n for n in nodes if n['name'] == 'Clean Actor'), None)
    if actor_node:
        print(json.dumps(actor_node, indent=2))
    else:
        print("Clean Actor not found")
else:
    print(f"\nCould not find workflow: {target}")
