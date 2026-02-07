# ⚡ SQLite Direct Access Cheatsheet

> **Warning**: Modifying the database directly bypasses n8n safety checks.
> **Database Path**: `/home/emky/n8n/database.sqlite`

## 🔍 Inspection Queries

### Find execution by ID
```sql
SELECT * FROM execution_entity WHERE id = '123';
```

### Find latest failed execution
```bash
sqlite3 /home/emky/n8n/database.sqlite "SELECT id, startedAt, stoppedAt, data FROM execution_entity WHERE status = 'error' ORDER BY id DESC LIMIT 1;"
```

### Dump specific execution data to JSON
```bash
sqlite3 /home/emky/n8n/database.sqlite "SELECT data FROM execution_entity WHERE id = <ID>" > execution_dump.json
```

## 🛠️ Repair Queries

### List all active workflows
```sql
SELECT id, name, active FROM workflow_entity WHERE active = 1;
```

### Disable a crashing workflow (Emergency Stop)
```bash
sqlite3 /home/emky/n8n/database.sqlite "UPDATE workflow_entity SET active = 0 WHERE id = '<WORKFLOW_ID>';"
```

## 🧬 Parsing JSON Blobs
The `data` column in `execution_entity` is a JSON string.
- `resultData.runData`: Contains the output of each node.
- `resultData.error`: Contains the global error if any.

Use `jq` to parse dumps:
```bash
cat execution_dump.json | jq .
```
