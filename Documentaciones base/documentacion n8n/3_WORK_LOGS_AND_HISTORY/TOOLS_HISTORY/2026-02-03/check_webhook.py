import sqlite3
import json
from pathlib import Path

N8N_DB = Path.home() / ".n8n" / "database.sqlite"
WORKFLOW_NAME = "Gemini ReAct Agent - Patched V11"

def check_webhook():
    conn = sqlite3.connect(N8N_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT nodes FROM workflow_entity WHERE name = ?", (WORKFLOW_NAME,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        print("Workflow not found")
        return
    
    nodes = json.loads(row[0])
    webhook = next((n for n in nodes if n['name'] == 'Webhook_Testing'), None)
    if webhook:
        print("✅ Webhook found")
    else:
        print("❌ Webhook NOT found")

check_webhook()
