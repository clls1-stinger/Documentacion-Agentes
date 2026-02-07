import sqlite3
import json
import os
from pathlib import Path

N8N_DB = Path.home() / ".n8n" / "database.sqlite"
TARGET_NAME = "Gemini ReAct Agent - Patched V11"

def check_router():
    conn = sqlite3.connect(N8N_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT nodes, connections FROM workflow_entity WHERE name = ?", (TARGET_NAME,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        print("Workflow not found")
        return

    nodes = json.loads(row[0])
    connections = json.loads(row[1])

    router = next((n for n in nodes if n['name'] == 'Tool Router'), None)
    if router:
        print("ROUTER TYPE:", router['type'])
        if 'Tool Router' in connections:
            conns = connections['Tool Router']
            # n8n connections format: { "main": [ [ { "node": "NextNode", ... } ], [ ... ] ] }
            if "main" in conns:
                for i, output in enumerate(conns["main"]):
                    print(f"OUTPUT {i}:")
                    for dest in output:
                        print(f"  -> {dest['node']} (input index {dest.get('index', 0)})")
            else:
                print("No 'main' outputs found")
        else:
            print("No connections from Tool Router")
    else:
        print("Tool Router node not found")

check_router()
