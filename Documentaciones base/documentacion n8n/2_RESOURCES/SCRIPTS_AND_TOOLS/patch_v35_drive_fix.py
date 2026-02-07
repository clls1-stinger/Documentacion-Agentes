import json
import sqlite3
from pathlib import Path

N8N_DB = Path.home() / ".n8n" / "database.sqlite"
WORKFLOW_ID = "Urf7HpECFvfQooAv"

def fix_drive_nodes():
    print(f"🔧 Fixing Drive nodes for workflow {WORKFLOW_ID}...")
    conn = sqlite3.connect(N8N_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT nodes FROM workflow_entity WHERE id = ?", (WORKFLOW_ID,))
    nodes = json.loads(cursor.fetchone()[0])
    
    for node in nodes:
        if node['type'] == "n8n-nodes-base.googleDrive":
            print(f"  📦 Found Google Drive node: {node['name']}")
            params = node.get('parameters', {})
            
            # Ensure resource is set to "file" (standard for search/download/upload)
            if 'resource' not in params:
                 params['resource'] = 'file'
                 print(f"    ✅ Added 'resource: file' to {node['name']}")
            
            # Special fix for Drive Search
            if node['name'] == "Drive Search":
                params['operation'] = 'list'
                params['useFilter'] = True
                params['filter'] = "name contains '{{ $json.datos.query }}'"
                print(f"    ✅ Configured search filter for Drive Search")
            
            # Special fix for Drive Download
            if node['name'] == "Drive Download":
                params['operation'] = 'download'
                # fileId should already be there but let's ensure it matches our protocol
                # it was: "={{ $json.datos.fileId }}"
            
            # Special fix for Drive Upload
            if node['name'] == "Drive Upload":
                params['operation'] = 'upload'
                params['fileContent'] = "={{ $json.datos.filename }}" # or binary?
            
            node['parameters'] = params

    cursor.execute("UPDATE workflow_entity SET nodes = ?, name = ?, updatedAt = datetime('now') WHERE id = ?", 
                  (json.dumps(nodes), "Yes (Patched v35 - Drive Fix)", WORKFLOW_ID))
    conn.commit()
    conn.close()
    print("\n✅ Drive nodes fixed and Patch v35 applied.")

if __name__ == "__main__":
    fix_drive_nodes()
