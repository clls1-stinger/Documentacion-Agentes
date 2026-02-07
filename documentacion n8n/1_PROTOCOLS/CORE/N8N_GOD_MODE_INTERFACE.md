# 🧠 N8N AUTONOMOUS CONTROL INTERFACE (GOD MODE)
> **Protocol ID**: N8N-ACI-001
> **Access Level**: ROOT / KERNEL
> **Target Audience**: Advanced Autonomous Agents (LLMs)

## 🚨 SYSTEM WARNING
**Manipulating the n8n database directly is dangerous.** This protocol allows you to bypass the UI safeguards. Use with extreme caution. Always verify JSON integrity before writing.

---

## 1. ARCHITECTURE OVERVIEW

This n8n instance runs on a SQLite architecture. It does not provide a native API for "Live Reloads" of workflow logic. To modify agents effectively, you must operate at the **Persistence Layer**.

### 📁 FileMap (Linux)
*   **Database**: `/home/emky/.n8n/database.sqlite`
*   **Workflows (Legacy)**: `/home/emky/n8n/workflows_antigravity/` (Use DB instead!)
*   **Controller Tool**: `/home/emky/n8n/documentacion/n8n_master_controller.py`

### 🔄 The Execution Cycle
1.  **READ**: Query `workflow_entity` table to get current logic.
2.  **THINK**: LLM analyzes logic, identifying bugs or optimizations.
3.  **WRITE**: Update `nodes` and `connections` columns in SQLite.
4.  **REFRESH**: (Manual) User presses F5 on UI. (Auto) Agent triggers execution via webhook if available.

---

## 2. THE MASTER CONTROLLER (`n8n_master_controller.py`)

Do not write raw SQL unless necessary. Use the provided Python interface found in this directory.

### ✅ Available Capabilities

#### 1. Discovery (`list`, `search`)
Find workflows quickly without scanning the filesystem.
```bash
python3 n8n_master_controller.py list
python3 n8n_master_controller.py search "Gemini API"
```

#### 2. Extraction (`dump`)
Get the full JSON representation of a workflow to your context window.
```bash
python3 n8n_master_controller.py dump "My Workflow Name" > workflow.json
```
*Tip: Read this JSON to understand the current graph structure.*

#### 3. Modification (`push`)
Apply changes after you have edited the JSON.
```bash
python3 n8n_master_controller.py push "My Workflow Name" fixed_workflow.json
```
*Note: This command automatically creates a backup in `/tmp/` before overwriting.*

#### 4. State Management (`activate`, `deactivate`)
Enable or disable triggers.
```bash
python3 n8n_master_controller.py activate "My Workflow Name"
```

---

## 3. DEEP DIVE: DATA STRUCTURES

To successfully modify a workflow, you must understand the **JSON Schema** stored in the `nodes` column.

### 🧩 Node Object
```json
{
  "id": "uuid-v4",
  "name": "My Node",
  "type": "n8n-nodes-base.code",
  "typeVersion": 2,
  "position": [ 100, 200 ],
  "parameters": {
    "jsCode": "return item.json;"  // <-- THIS IS WHERE logic LIVES
  },
  "credentials": { ... }
}
```
**CRITICAL**: When modifying code, you are editing the value of `parameters.jsCode` (or similar depending on node type).

### 🔗 Connection Object
The `connections` column defines the graph. It is a strictly structured Map.
```json
{
  "Source Node Name": {
    "main": [
      [
        {
          "node": "Destination Node Name",
          "type": "main",
          "index": 0
        }
      ]
    ]
  }
}
```
**Rule**: If you rename a node in `nodes`, you **MUST** update all references in `connections`.

---

## 4. AGENTIC WORKFLOW PATTERNS

### Pattern A: "Self-Diagnosis"
1. Agent detects error in logs (e.g., "JSON Parse Error").
2. Agent runs `dump "WorkflowName"`.
3. Agent analyzes `parameters.jsCode` of the failing node.
4. Agent writes corrected logic to `fixed.json`.
5. Agent runs `push "WorkflowName" fixed.json`.

### Pattern B: "Capabilities Upgrade"
1. User asks: "Add Google Drive support".
2. Agent reads workflow.
3. Agent generates `n8n-nodes-base.googleDrive` node JSON object.
4. Agent adds node to `nodes` array.
5. Agent updates `connections` to link it to the Planner.
6. Agent pushes updates.

---

## 5. RECOVERY PROCEDURES

If you corrupt the database:
1. Stop n8n: `pm2 stop n8n-master`
2. Restore backup: `cp ~/.n8n/database.sqlite.backup ~/.n8n/database.sqlite` (Backups are manually managed, check `/tmp` for controller backups).
3. Restart n8n: `pm2 start n8n-master`

### 💀 FORCE RESTART PROTOCOL (Ghost Process Killer)
If `pm2 restart` fails or the UI freezes, use this **Port-Based Kill Method**. The system daemon (PM2) will automatically resurrect n8n after you kill it.

1.  **Identify the Process ID (PID)** listening on port 5678:
    ```bash
    sudo ss -tulpn | grep :5678
    ```
    *Look for the number in the `users` column, e.g., `pid=70395`.*

2.  **Terminate the Process**:
    ```bash
    sudo kill -9 <PID>
    ```
    *(Example: `sudo kill -9 70395`)*

3.  **Wait**: The daemon will detect the crash and restart n8n automatically. Verify with `pm2 log`.

---

## 6. FORENSIC DEBUGGING (EXECUTION DATA)
If you need to know *exactly* what data a node received during a failed run:

1. **Find Execution ID**: `sqlite3 ~/.n8n/database.sqlite "SELECT id FROM execution_entity ORDER BY stoppedAt DESC LIMIT 5;"`
2. **Extract State Blob**: 
   ```bash
   sqlite3 ~/.n8n/database.sqlite "SELECT data FROM execution_data WHERE executionId = <ID>;" > /tmp/exec_data.json
   ```
3. **Analyze**: The JSON is a flattened array. Use [ADVANCED_WORKFLOW_STATE_MANAGEMENT.md](./ADVANCED_WORKFLOW_STATE_MANAGEMENT.md) to understand how to map specific nodes to their results.

---

**Protocol Verified By**: Vega
**Last Updated**: 2026-02-02 (Post-Case #334)
**Version**: 2.1 (Forensics Update)
