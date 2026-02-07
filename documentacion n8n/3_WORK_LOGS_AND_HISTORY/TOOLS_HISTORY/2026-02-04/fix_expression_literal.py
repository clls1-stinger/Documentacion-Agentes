import sqlite3
import json

DB_PATH = "/home/emky/.n8n/database.sqlite"
WORKFLOW_ID = "osenZpfZMpCRQBSL"

def fix_expression():
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
            params = node.get('parameters', {})
            for key, value in params.items():
                if isinstance(value, str) and value == "{{ $binary.data.fileName }}":
                    params[key] = "={{ $binary.data.fileName }}"
                    print(f"Fixed parameter '{key}' in node '{node.get('name')}': Added leading '='")
                    patched = True
                elif isinstance(value, str) and "{{ $binary.data.fileName }}" in value and not value.startswith('='):
                    # Handle cases like "/home/emky/downloads/{{ $binary.data.fileName }}"
                    params[key] = "=" + value
                    print(f"Fixed parameter '{key}' in node '{node.get('name')}': Prefixed entire string with '='")
                    patched = True

        if patched:
            cursor.execute("""
                UPDATE workflow_entity 
                SET nodes = ?, versionId = versionId + 1, updatedAt = datetime('now')
                WHERE id = ?
            """, (json.dumps(nodes), WORKFLOW_ID))
            conn.commit()
            print("Successfully updated workflow in database.")
        else:
            print("No malformed expressions found to fix.")
            
        conn.close()

    except Exception as e:
        print(f"Database error: {e}")

if __name__ == "__main__":
    fix_expression()
