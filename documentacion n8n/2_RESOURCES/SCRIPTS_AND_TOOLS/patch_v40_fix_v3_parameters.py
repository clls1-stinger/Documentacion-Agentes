import json
import sqlite3
from pathlib import Path

N8N_DB = Path.home() / ".n8n" / "database.sqlite"
WORKFLOW_ID = "Urf7HpECFvfQooAv"

def fix_drive_v3_params():
    print(f"🔧 Applying Patch v40 - Fix Drive V3 Parameters for {WORKFLOW_ID}...")
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
            print(f"  📦 Configuring node: {node['name']} (V3)")
            # Explicitly set Version 3 (which maps to GoogleDriveV2 class in implementation)
            node['typeVersion'] = 3
            
            # Reset params
            node['parameters'] = {}
            params = node['parameters']
            params['authentication'] = 'oAuth2'

            if node['name'] == "Drive Search":
                # V3 Schema (from reading source code for GoogleDriveV2.node.js)
                # resource: 'fileFolder'
                # operation: 'search'
                # searchMethod: 'query' (Advanced)
                
                params['resource'] = 'fileFolder'
                params['operation'] = 'search'
                
                params['searchMethod'] = 'query'
                params['queryString'] = "name contains '{{ $json.datos.query }}' and trashed = false"
                
                params['returnAll'] = True # Let's try True to verify behavior, or False + Limit
                params['returnAll'] = False
                params['limit'] = 10
                
                params['options'] = {}
                
                print(f"    ✅ Configured Search V3: resource='fileFolder', operation='search', method='query'")
            
            elif node['name'] == "Drive Download":
                # resource: 'file'
                # operation: 'download'
                params['resource'] = 'file'
                params['operation'] = 'download'
                params['fileId'] = "={{ $json.datos.fileId }}"
                print(f"    ✅ Configured Download V3: resource='file', operation='download'")
                
            elif node['name'] == "Drive Upload":
                params['resource'] = 'file'
                params['operation'] = 'upload'
                params['binaryData'] = True
                params['binaryPropertyName'] = "data"
                print(f"    ✅ Configured Upload V3: resource='file', operation='upload'")
            
    cursor.execute("UPDATE workflow_entity SET nodes = ?, name = ?, updatedAt = datetime('now') WHERE id = ?", 
                  (json.dumps(nodes), "Yes (Patched v40 - Fix V3 Params)", WORKFLOW_ID))
    conn.commit()
    conn.close()
    
    # Save generic forensic
    forensics_path = "/home/emky/n8n/documentacion/FORENSICS_AND_LOGS/workflow_yes_patched_v40.json"
    with open(forensics_path, 'w') as f:
        json.dump(nodes, f, indent=2)
        
    print(f"\n✅ Patch v40 applied. Re-aligned to Version 3 with correct 'fileFolder' resource.")

if __name__ == "__main__":
    fix_drive_v3_params()
