import sqlite3
import json
import os

DB_PATH = "/home/emky/.n8n/database.sqlite"
WORKFLOW_ID = "osenZpfZMpCRQBSL"
AGGREGATOR_CODE_PATH = "/home/emky/n8n/documentacion/3_WORK_LOGS_AND_HISTORY/FORENSICS_AND_LOGS/aggregator_code.js"

def load_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def patch_db_direct():
    print(f"Loading patch code from {AGGREGATOR_CODE_PATH}...")
    try:
        new_code = load_file(AGGREGATOR_CODE_PATH)
    except Exception as e:
        print(f"Error loading code file: {e}")
        return

    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row # Access by column name
        cursor = conn.cursor()
        
        # Get workflow
        print(f"Fetching workflow {WORKFLOW_ID}...")
        cursor.execute("SELECT * FROM workflow_entity WHERE id = ?", (WORKFLOW_ID,))
        row = cursor.fetchone()
        
        if not row:
            print(f"Error: Workflow {WORKFLOW_ID} not found in database.")
            conn.close()
            return

        print(f"Found workflow: {row['name']}")
        
        # Parse nodes
        nodes = json.loads(row['nodes'])
        patched = False
        
        for node in nodes:
            if node.get('name') == 'Aggregator' and node.get('type') == 'n8n-nodes-base.code':
                print("Found Aggregator node. Updating jsCode...")
                node['parameters']['jsCode'] = new_code
                patched = True
                break
        
        if patched:
            nodes_json = json.dumps(nodes)
            
            # Update DB
            cursor.execute("""
                UPDATE workflow_entity 
                SET nodes = ?, versionId = versionId + 1, updatedAt = datetime('now')
                WHERE id = ?
            """, (nodes_json, WORKFLOW_ID))
            
            if cursor.rowcount == 1:
                conn.commit()
                print("Successfully updated workflow in database.")
            else:
                print("Failed to update workflow record.")
        else:
            print("Error: Aggregator node not found in workflow nodes.")
            
        conn.close()
        
    except Exception as e:
        print(f"Database error: {e}")

if __name__ == "__main__":
    patch_db_direct()
