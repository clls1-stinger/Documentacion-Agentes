import sqlite3
import json

DB_PATH = "/home/emky/.n8n/database.sqlite"
WORKFLOW_NAME = "Gemini ReAct Agent - Patched V11"

def dump():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, nodes FROM workflow_entity WHERE name = ?", (WORKFLOW_NAME,))
    row = cursor.fetchone()
    if not row:
        print("Workflow not found")
        return
    
    nodes = json.loads(row[1])
    for node in nodes:
        if node.get('name') == "Clean Actor":
             params = node.get('parameters', {})
             code = params.get('jsCode') or params.get('code', {}).get('js')
             if code:
                 print(code)
                 with open('/home/emky/n8n/debug_clean_actor.js', 'w') as f:
                     f.write(code)

if __name__ == "__main__":
    dump()
