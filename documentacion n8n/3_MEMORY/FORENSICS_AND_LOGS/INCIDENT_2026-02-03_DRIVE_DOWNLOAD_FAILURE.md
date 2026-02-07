# 🚨 Incident Report: Drive Download "Resource Not Found"

**Date**: 2026-02-03
**Component**: n8n / Gemini ReAct Agent / Clean Actor
**Severity**: Blocking (Workflow halts)

## 🐛 The Issue
The User reported a failure in the **Drive Download** node:
> "Problem in node 'Drive Download': The resource you are requesting could not be found"

This error (Google Drive API 404) occurs when the `fileId` parameter passed to the node is invalid. This typically happens because the Agent (LLM) hallucinates a file path (e.g., `folder/file.txt`) instead of using the required File ID (e.g., `1a2b3c...`).

## 🔍 Forensic Analysis
1. **Inspection**: Checked the configured code in `Clean Actor` node of the active workflow (`Gemini ReAct Agent - Patched V11`).
2. **Finding**: The active code was a simplified version that lacked:
    - Robust Markdown parsing (`JSON.parse` strict).
    - Tool Alias mapping (e.g., `download_file` -> `descargar_de_drive`).
    - **CRITICAL**: The "Active Defense" logic to validate Drive IDs described in `LEARNING_DRIVE_IDS_VS_PATHS.md`.
3. **Hypothesis**: The agent tried to download a file by path, the simple Clean Actor passed it through to the Drive Download node, which failed 404.

## 🛠️ Resolution (Patch V42)
Applied a hot patch (`patch_clean_actor_drive_guard.py`) to the SQLite database.

**Changes:**
1. **Restored Robust Logic**: Re-implemented the code capable of handling Markdown blocks (` ```json `) and mapping aliases.
2. **Inject Drive ID Guard**:
   ```javascript
   // GUARD: Drive ID Protection
    if (accion === 'descargar_de_drive' || accion === 'leer_archivo_drive') {
        let fid = datos.fileId || "";
        if (fid.includes('/') || fid.length < 10 || fid === "FILE_ID") {
             accion = 'ejecutar_comando';
             datos = { 
                 command: `echo "SYSTEM ERROR: Action '${accion}' requires a valid Google Drive FILE ID..."` 
             };
        }
    }
   ```

## 🟢 Status
**FIXED**.
The system will now intercept invalid Drive IDs and return a helpful error message to the Agent via `Execute Command` >> `echo`, guiding it to use `Drive Search` first.

**Action Required**:
- Refresh n8n UI (F5) to load the new node code.
