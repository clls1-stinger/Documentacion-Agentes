import json
import sqlite3
from pathlib import Path

N8N_DB = Path.home() / ".n8n" / "database.sqlite"
WORKFLOW_ID = "Urf7HpECFvfQooAv"

def force_drive_v2():
    print(f"🔧 Applying Patch v38 - Force Drive V2 Compatibility for {WORKFLOW_ID}...")
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
            print(f"  📦 Downgrading node: {node['name']} to V2")
            node['typeVersion'] = 2
            
            params = node.get('parameters', {})
            # Reset to clean V2 state to avoid parameter pollution
            new_params = {} 
            
            # Common
            new_params['authentication'] = 'oAuth2' # Usually implied but good to check
            # We don't touch credential references in 'nodes' root, they stay same
            
            if node['name'] == "Drive Search":
                new_params['operation'] = 'list'
                new_params['useQueryString'] = True
                new_params['queryString'] = "name contains '{{ $json.datos.query }}' and trashed = false"
                new_params['resource'] = 'file'
                # Pagination defaults
                new_params['limit'] = 10 
                print(f"    ✅ Configured Search (List) V2 for {node['name']}")
            
            elif node['name'] == "Drive Download":
                new_params['operation'] = 'download'
                new_params['fileId'] = "={{ $json.datos.fileId }}"
                new_params['resource'] = 'file'
                print(f"    ✅ Configured Download V2 for {node['name']}")
                
            elif node['name'] == "Drive Upload":
                new_params['operation'] = 'upload'
                new_params['resource'] = 'file'
                # Assuming simple upload for now, or binary logic
                # V2 Upload usually takes 'binaryData' boolean and property name
                new_params['binaryData'] = True 
                new_params['binaryPropertyName'] = "data"
                print(f"    ✅ Configured Upload V2 for {node['name']}")
            
            node['parameters'] = new_params

    cursor.execute("UPDATE workflow_entity SET nodes = ?, name = ?, updatedAt = datetime('now') WHERE id = ?", 
                  (json.dumps(nodes), "Yes (Patched v38 - Force Drive V2)", WORKFLOW_ID))
    conn.commit()
    conn.close()
    
    # Save generic forensic
    forensics_path = "/home/emky/n8n/documentacion/FORENSICS_AND_LOGS/workflow_yes_patched_v38.json"
    with open(forensics_path, 'w') as f:
        json.dump(nodes, f, indent=2)
        
    print(f"\n✅ Patch v38 applied. Downgraded nodes to V2 'list/download' operations.")

if __name__ == "__main__":
    force_drive_v2()
