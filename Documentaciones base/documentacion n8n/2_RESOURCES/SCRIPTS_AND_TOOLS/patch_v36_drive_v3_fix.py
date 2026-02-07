import json
import sqlite3
from pathlib import Path

N8N_DB = Path.home() / ".n8n" / "database.sqlite"
WORKFLOW_ID = "Urf7HpECFvfQooAv"

def fix_drive_v3():
    print(f"🔧 Applying Patch v36 - Google Drive V3 Fix for {WORKFLOW_ID}...")
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
            print(f"  📦 Patching node: {node['name']} (v{node.get('typeVersion')})")
            params = node.get('parameters', {})
            
            # Universal V3 requirement: resource
            params['resource'] = 'file'
            
            if node['name'] == "Drive Search":
                params['operation'] = 'search'
                # V3 Search uses searchMethod and searchQuery/queryString
                params['searchMethod'] = 'name'
                params['searchQuery'] = "={{ $json.datos.query }}"
                print(f"    ✅ Configured Search V3 for {node['name']}")
            
            elif node['name'] == "Drive Download":
                params['operation'] = 'download'
                params['fileId'] = "={{ $json.datos.fileId }}"
                print(f"    ✅ Configured Download V3 for {node['name']}")
                
            elif node['name'] == "Drive Upload":
                params['operation'] = 'upload'
                # Ensure it uses the right path/file
                print(f"    ✅ Configured Upload V3 for {node['name']}")
            
            node['parameters'] = params

    cursor.execute("UPDATE workflow_entity SET nodes = ?, name = ?, updatedAt = datetime('now') WHERE id = ?", 
                  (json.dumps(nodes), "Yes (Patched v36 - Drive V3 Fix)", WORKFLOW_ID))
    conn.commit()
    conn.close()
    
    # Also save a copy to forensics for reference
    forensics_path = "/home/emky/n8n/documentacion/FORENSICS_AND_LOGS/workflow_yes_patched_v36.json"
    with open(forensics_path, 'w') as f:
        json.dump(nodes, f, indent=2)
        
    print(f"\n✅ Patch v36 applied. Forensic copy saved to {forensics_path}")

if __name__ == "__main__":
    fix_drive_v3()
