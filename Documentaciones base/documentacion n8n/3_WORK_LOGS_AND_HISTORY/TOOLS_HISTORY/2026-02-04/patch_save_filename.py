import sqlite3
import json
import os

DB_PATH = "/home/emky/.n8n/database.sqlite"
WORKFLOW_ID = "osenZpfZMpCRQBSL"

# Target configuration
SAVE_PATH_EXPRESSION = "/home/emky/downloads/{{ $binary.data.fileName }}"

def patch_save_node():
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        print(f"Fetching workflow {WORKFLOW_ID}...")
        cursor.execute("SELECT * FROM workflow_entity WHERE id = ?", (WORKFLOW_ID,))
        row = cursor.fetchone()
        
        if not row:
            print(f"Error: Workflow {WORKFLOW_ID} not found.")
            return

        nodes = json.loads(row['nodes'])
        patched = False
        
        for node in nodes:
            if node.get('name') == 'Save to Disk':
                print("Found 'Save to Disk' node.")
                print(f"Current parameters: {node.get('parameters')}")
                
                # Check if it's the ReadWriteFile node (common for saving)
                if node.get('type') == 'n8n-nodes-base.readWriteFile':
                    # Update fileSelector to use dynamic name
                    # If the user was using a fixed path, this will overwrite it.
                    # We assume saving to downloads is acceptable or we should preserve the dir.
                    
                    current_path = node['parameters'].get('fileSelector', '')
                    directory = os.path.dirname(current_path) if current_path else "/home/emky/downloads"
                    if not directory: directory = "/home/emky/downloads"
                    
                    new_path = f"{directory}/{{{{ $binary.data.fileName }}}}"
                    node['parameters']['fileSelector'] = new_path
                    print(f"Updated fileSelector to: {new_path}")
                    patched = True
                
                # Check generic WriteBinaryFile
                elif node.get('type') == 'n8n-nodes-base.writeBinaryFile':
                     current_name = node['parameters'].get('fileName', '')
                     node['parameters']['fileName'] = "{{ $binary.data.fileName }}"
                     print(f"Updated fileName to: {{{{ $binary.data.fileName }}}}")
                     patched = True

        if patched:
            nodes_json = json.dumps(nodes)
            cursor.execute("""
                UPDATE workflow_entity 
                SET nodes = ?, versionId = versionId + 1, updatedAt = datetime('now')
                WHERE id = ?
            """, (nodes_json, WORKFLOW_ID))
            
            if cursor.rowcount == 1:
                conn.commit()
                print("Successfully updated 'Save to Disk' node in database.")
            else:
                print("Failed to update database.")
        else:
            print("Error: 'Save to Disk' node not found or type mismatch.")
            
        conn.close()

    except Exception as e:
        print(f"Database error: {e}")

if __name__ == "__main__":
    patch_save_node()
