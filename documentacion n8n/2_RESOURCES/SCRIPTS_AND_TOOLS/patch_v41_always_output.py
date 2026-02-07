import json
import sqlite3
from pathlib import Path

N8N_DB = Path.home() / ".n8n" / "database.sqlite"
WORKFLOW_ID = "Urf7HpECFvfQooAv"

def patch_always_output():
    print(f"🔧 Applying Patch v41 - Enable Always Output Data for {WORKFLOW_ID}...")
    conn = sqlite3.connect(N8N_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT nodes FROM workflow_entity WHERE id = ?", (WORKFLOW_ID,))
    result = cursor.fetchone()
    if not result:
        print("❌ Workflow not found")
        return
    
    nodes = json.loads(result[0])
    
    for node in nodes:
        if node['name'] == "Drive Search":
            print(f"  📦 Modifying node: {node['name']}")
            node['alwaysOutputData'] = True
            print(f"    ✅ Set alwaysOutputData = True")

    cursor.execute("UPDATE workflow_entity SET nodes = ?, name = ?, updatedAt = datetime('now') WHERE id = ?", 
                  (json.dumps(nodes), "Yes (Patched v41 - Always Output)", WORKFLOW_ID))
    conn.commit()
    conn.close()
    
    print(f"\n✅ Patch v41 applied. Node will now return empty JSON instead of stopping execution when 0 files found.")

if __name__ == "__main__":
    patch_always_output()
