import sqlite3
from pathlib import Path

N8N_DB = Path.home() / ".n8n" / "database.sqlite"
KEEP_ID = "Urf7HpECFvfQooAv"

def cleanup():
    if not N8N_DB.exists():
        print(f"❌ Database not found at {N8N_DB}")
        return

    conn = sqlite3.connect(N8N_DB)
    cursor = conn.cursor()
    
    # 1. Count before
    cursor.execute("SELECT count(*) FROM workflow_entity")
    before_count = cursor.fetchone()[0]
    
    # 2. Delete others
    print(f"🗑️ Deleting all workflows except {KEEP_ID}...")
    cursor.execute("DELETE FROM workflow_entity WHERE id != ?", (KEEP_ID,))
    deleted_count = cursor.rowcount
    
    # 3. Activate the good one
    print(f"✅ Activating workflow {KEEP_ID}...")
    cursor.execute("UPDATE workflow_entity SET active = 1 WHERE id = ?", (KEEP_ID,))
    
    conn.commit()
    conn.close()
    
    print("-" * 40)
    print(f"Initial count: {before_count}")
    print(f"Deleted:       {deleted_count}")
    print(f"Remaining:     {before_count - deleted_count}")
    print("-" * 40)
    print("✨ Please REFRESH your n8n browser tab (F5).")

if __name__ == "__main__":
    cleanup()
