
def patch_clean_actor_validation(workflow):
    nodes = workflow['nodes']
    
    clean_actor_node = None
    for node in nodes:
        if node['name'] == 'Clean Actor':
            clean_actor_node = node
            break
            
    if not clean_actor_node:
        print("❌ 'Clean Actor' node not found")
        return False

    # Enhanced Code with Parse Error Handling, ID Guard AND File System Interception
    new_code = """
const item = $input.item.json;
let raw = item.final_answer || item.response || item.raw_stdout || "{}";
if (typeof raw !== 'string') raw = JSON.stringify(raw);

let parsed = {};
try { 
    // Clean up markdown code blocks
    const jsonMatch = raw.match(/```json\\s*([\\s\\S]*?)\\s*```/) || raw.match(/\\{.*\\}/s);
    if (jsonMatch) raw = jsonMatch[1] || jsonMatch[0];
    parsed = JSON.parse(raw); 
} catch(e) {
    parsed = { 
        accion: 'ejecutar_comando', 
        datos: { command: `echo "ERROR: Failed to parse LLM JSON: ${e.message.replace(/"/g, "'")}"` }
    };
}

const map = {
    'search_drive': 'buscar_en_drive',
    'buscar_en_drive': 'buscar_en_drive',
    'download_file': 'descargar_de_drive',
    'descargar_de_drive': 'descargar_de_drive',
    'upload_file': 'subir_a_drive',
    'subir_a_drive': 'subir_a_drive',
    'run_command': 'ejecutar_comando',
    'run_shell_command': 'ejecutar_comando',
    'ejecutar_comando': 'ejecutar_comando',
    'execute_command': 'ejecutar_comando',
    'read_file': 'leer_archivo',
    'leer_archivo': 'leer_archivo',
    'find': 'ejecutar_comando' 
};

let actions = [];
if (parsed.ejecuciones && Array.isArray(parsed.ejecuciones)) {
    actions = parsed.ejecuciones;
} else if (parsed.actions && Array.isArray(parsed.actions)) {
    actions = parsed.actions;
} else if (parsed.herramienta || parsed.accion || parsed.action) {
    actions = [parsed];
}

if (actions.length === 0) {
     actions = [{ 
        accion: 'ejecutar_comando', 
        datos: { command: 'echo "WARNING: No actions found in LLM response"' }
    }];
}

return actions.map(a => {
    let tool = (a.herramienta || a.accion || a.action || "").toLowerCase();
    let params = a.parametros || a.datos || a.parameters || {};
    tool = map[tool] || tool;

    // --- GUARD 1: Validate Drive IDs ---
    if (tool === 'descargar_de_drive') {
         if (!params.fileId && params.filename) {
             tool = 'buscar_en_drive';
             params = { query: params.filename };
         }
         else if (params.fileId && (params.fileId.includes('/') || params.fileId.includes('.'))) {
            tool = 'buscar_en_drive';
            params = { query: params.fileId };
         }
         else if (!params.fileId) {
             tool = 'ejecutar_comando';
             params = { command: 'echo "ERROR: Missing fileId for drive download"' };
         }
    }
    
    // --- GUARD 2: Intercept 'find' commands on Google Drive paths ---
    if (tool === 'ejecutar_comando' && params.command) {
        // Detect: find "/path/to/Google Drive" -name "query"
        // Also checks for "/run/media" which is the user's mount point
        const findMatch = params.command.match(/find\\s+["']?.*(Google Drive|run\/media).*["']?\\s+-name\\s+["']?([^"']+)["']?/i);
        
        if (findMatch) {
            tool = 'buscar_en_drive';
            // Clean up wildcards from find command (*query*)
            let cleanQuery = findMatch[2].replace(/\\*/g, '');
            params = { query: cleanQuery };
        }
    }
    // --------------------------------

    return { 
        json: { 
            accion: tool, 
            datos: params,
            planner_instruction: item.instruction || item.task,
            user_goal: item.user_goal,
            history: item.history,
            counter: item.counter,
            chat_history: item.chat_history
        } 
    };
});
"""
    clean_actor_node['parameters']['jsCode'] = new_code
    print("✅ 'Clean Actor' patched with ROBUST validation guard + FIND Interceptor.")
    return True

import sqlite3
import json
import sys
from pathlib import Path

# Config
N8N_DB = Path.home() / ".n8n" / "database.sqlite"
WORKFLOW_NAME = "Gemini ReAct Agent - Patched V11"

def get_workflow_from_db():
    conn = sqlite3.connect(N8N_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT id, nodes, connections, staticData, settings, name FROM workflow_entity WHERE name = ?", (WORKFLOW_NAME,))
    result = cursor.fetchone()
    conn.close()
    if not result:
        print(f"❌ Workflow '{WORKFLOW_NAME}' not found")
        sys.exit(1)
    return {'id': result[0], 'nodes': json.loads(result[1]), 'connections': json.loads(result[2]), 'staticData': json.loads(result[3]), 'settings': json.loads(result[4]), 'name': result[5]}

def save_workflow_to_db(workflow):
    conn = sqlite3.connect(N8N_DB)
    cursor = conn.cursor()
    cursor.execute("UPDATE workflow_entity SET nodes = ? WHERE id = ?", (json.dumps(workflow['nodes']), workflow['id']))
    conn.commit()
    conn.close()
    print(f"💾 Updated workflow ID {workflow['id']}")

if __name__ == "__main__":
    wf = get_workflow_from_db()
    if patch_clean_actor_validation(wf):
        save_workflow_to_db(wf)
