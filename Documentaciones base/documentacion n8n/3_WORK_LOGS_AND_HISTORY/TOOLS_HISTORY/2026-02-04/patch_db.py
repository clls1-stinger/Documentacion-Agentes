import sqlite3
import json
import os

DB_PATH = "/home/emky/n8n/database.sqlite"
WORKFLOW_ID = "osenZpfZMpCRQBSL"
PATCHED_WORKFLOW_FILE = "/home/emky/n8n/patched_workflow.json"

def patch_db():
    if not os.path.exists(PATCHED_WORKFLOW_FILE):
        print(f"Error: {PATCHED_WORKFLOW_FILE} not found.")
        return

    print(f"Reading patched workflow from {PATCHED_WORKFLOW_FILE}...")
    with open(PATCHED_WORKFLOW_FILE, 'r', encoding='utf-8') as f:
        workflow_data = json.load(f)
    
    # Ensure ID matches
    if workflow_data.get('id') != WORKFLOW_ID:
        print(f"Warning: Workflow ID in file ({workflow_data.get('id')}) does not match target ({WORKFLOW_ID}).")
    
    # Serialize to JSON string
    nodes_json = json.dumps(workflow_data['nodes'])
    connections_json = json.dumps(workflow_data['connections'])
    # Check if 'meta' or 'settings' etc need update. Usually nodes and connections are the key.
    # But wait, n8n stores the whole JSON or parts?
    # Modern n8n typically stores 'nodes' and 'connections' in separate columns in 'workflow_entity' table.
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check current data
        cursor.execute("SELECT name FROM workflow_entity WHERE id = ?", (WORKFLOW_ID,))
        row = cursor.fetchone()
        if not row:
            print(f"Error: Workflow {WORKFLOW_ID} not found in database.")
            return

        print(f"Found workflow: {row[0]}. Updating...")
        
        # Update nodes and connections
        cursor.execute("""
            UPDATE workflow_entity 
            SET nodes = ?, connections = ?, versionId = versionId + 1, updatedAt = datetime('now')
            WHERE id = ?
        """, (nodes_json, connections_json, WORKFLOW_ID))
        
        if cursor.rowcount == 1:
            conn.commit()
            print("Successfully updated workflow in database.")
        else:
            print("Failed to update workflow.")
            
        conn.close()
        
    except Exception as e:
        print(f"Database error: {e}")

if __name__ == "__main__":
    patch_db()
