
import sqlite3
import json
import os

DB_PATH = os.path.expanduser("~/.n8n/database.sqlite")
PATCH_PATH = "/home/emky/n8n/documentacion/3_WORK_LOGS_AND_HISTORY/FORENSICS_AND_LOGS/workflow_yes_patched_v41.json"
WF_ID = "7826e7da-e44f-4f56-bd38-66a2c86a0a97"

with open(PATCH_PATH, 'r') as f:
    patch_data = json.load(f)

nodes_json = json.dumps(patch_data['nodes'])
connections_json = json.dumps(patch_data['connections'])

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Backup before patch
cursor.execute("SELECT nodes, connections FROM workflow_entity WHERE id = ?", (WF_ID,))
row = cursor.fetchone()
if row:
    with open("/home/emky/n8n/documentacion/3_WORK_LOGS_AND_HISTORY/FORENSICS_AND_LOGS/backup_v40.json", 'w') as f:
        json.dump({"nodes": json.loads(row[0]), "connections": json.loads(row[1])}, f)

cursor.execute("UPDATE workflow_entity SET nodes = ?, connections = ?, updatedAt = datetime('now') WHERE id = ?", 
               (nodes_json, connections_json, WF_ID))

conn.commit()
conn.close()

print(f"Workflow {WF_ID} patched with V41 (Parallel/Robust Router).")
