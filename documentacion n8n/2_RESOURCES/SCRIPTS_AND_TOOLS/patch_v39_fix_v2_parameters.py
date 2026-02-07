import json
import sqlite3
from pathlib import Path

N8N_DB = Path.home() / ".n8n" / "database.sqlite"
WORKFLOW_ID = "Urf7HpECFvfQooAv"

def fix_drive_v2_params():
    print(f"🔧 Applying Patch v39 - Fix V2 Parameters for {WORKFLOW_ID}...")
    conn = sqlite3.connect(N8N_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT nodes FROM workflow_entity WHERE id = ?", (WORKFLOW_ID,))
    result = cursor.fetchone()
    if not result:
        print("❌ Workflow not found")
        return
    
    nodes = json.loads(result[0])
    
    for node in nodes:
        if node.get('type') == "n8n-nodes-base.googleDrive":
            print(f"  📦 Configuring node: {node['name']} (V2)")
            node['typeVersion'] = 2
            
            # Reset params to avoid conflicts
            node['parameters'] = {}
            params = node['parameters']
            params['authentication'] = 'oAuth2'

            if node['name'] == "Drive Search":
                # Correct V2 Schema:
                # Resource: 'fileFolder' (NOT 'file')
                # Operation: 'search' (NOT 'list')
                params['resource'] = 'fileFolder'
                params['operation'] = 'search'
                
                # Use Advanced Search ('query') to allow full control
                params['searchMethod'] = 'query'
                params['queryString'] = "name contains '{{ $json.datos.query }}' and trashed = false"
                
                params['returnAll'] = False
                params['limit'] = 10
                
                # Ensure options is present
                params['options'] = {}
                
                print(f"    ✅ Fixed Search V2: resource='fileFolder', operation='search'")
            
            elif node['name'] == "Drive Download":
                # V2 Download remains 'file' -> 'download'
                params['resource'] = 'file'
                params['operation'] = 'download'
                params['fileId'] = "={{ $json.datos.fileId }}"
                print(f"    ✅ Fixed Download V2: resource='file', operation='download'")
                
            elif node['name'] == "Drive Upload":
                params['resource'] = 'file'
                params['operation'] = 'upload'
                params['binaryData'] = True
                params['binaryPropertyName'] = "data"
                print(f"    ✅ Fixed Upload V2: resource='file', operation='upload'")
            
    cursor.execute("UPDATE workflow_entity SET nodes = ?, name = ?, updatedAt = datetime('now') WHERE id = ?", 
                  (json.dumps(nodes), "Yes (Patched v39 - Fix V2 Params)", WORKFLOW_ID))
    conn.commit()
    conn.close()
    
    # Save generic forensic
    forensics_path = "/home/emky/n8n/documentacion/FORENSICS_AND_LOGS/workflow_yes_patched_v39.json"
    with open(forensics_path, 'w') as f:
        json.dump(nodes, f, indent=2)
        
    print(f"\n✅ Patch v39 applied. Corrected V2 'fileFolder/search' parameters.")

if __name__ == "__main__":
    fix_drive_v2_params()
