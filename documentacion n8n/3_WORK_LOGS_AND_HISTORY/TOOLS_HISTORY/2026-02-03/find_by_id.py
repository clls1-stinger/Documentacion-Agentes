import sqlite3
from pathlib import Path

N8N_DB = Path.home() / ".n8n" / "database.sqlite"
TARGET_ID = "Urf7HpECFvfQooAv"

def find_wf():
    conn = sqlite3.connect(N8N_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM workflow_entity WHERE id = ?", (TARGET_ID,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        print(f"Found workflow: {row[0]}")
    else:
        print("ID not found in DB")

find_wf()
