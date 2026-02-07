import sqlite3
import json

DB_PATH = "/home/emky/.n8n/database.sqlite"
WORKFLOW_NAME = "Gemini ReAct Agent - Patched V11"

# --- CODE DEFINITIONS ---

CLEAN_ACTOR_CODE = """
// V1 MILESTONE: Robust Input + Drive Guard + Markdown Support
const items = $input.all();
if (items.length === 0) return [];
const item = items[0].json; 

let raw = item.final_answer || item.response || item.raw_stdout || "{}";
if (typeof raw !== 'string') raw = JSON.stringify(raw);

let parsed = {};
try { 
    // Robust parsing for Markdown or plain JSON
    const jsonMatch = raw.match(/```json\\s*([\\s\\S]*?)\\s*```/) || raw.match(/\\{.*\\}/s);
    if (jsonMatch) raw = jsonMatch[1] || jsonMatch[0];
    parsed = JSON.parse(raw); 
} catch(e) {
    parsed = { error: "JSON Parse failed", raw: raw };
}

// Normalize actions list
const actions = parsed.actions || (parsed.accion ? [parsed] : []) || [];

// Map for tools aliases
const toolMap = {
    'search_drive': 'buscar_en_drive',
    'buscar_en_drive': 'buscar_en_drive',
    'download_file': 'descargar_de_drive',
    'descargar_de_drive': 'descargar_de_drive',
    'run_command': 'ejecutar_comando',
    'ejecutar_comando': 'ejecutar_comando',
    'run_shell_command': 'ejecutar_comando',
    'execute_command': 'ejecutar_comando',
    'subir_a_drive': 'subir_a_drive',
    'leer_archivo': 'leer_archivo',
    'navegar_web': 'navegar_web',
    'list_directory': 'ejecutar_comando',
    'ls': 'ejecutar_comando'
};

const validActions = Object.values(toolMap);

return actions.map(a => {
    let accion = (a.accion || "").toLowerCase();
    let datos = a.datos || {};
    
    // 1. Map Alias -> Official Name
    accion = toolMap[accion] || accion;
    
    // 2. Handle 'ls' shortcut
    if (a.accion === 'ls' || a.accion === 'list_directory') {
        accion = 'ejecutar_comando';
        datos = { command: `ls -R ${datos.path || '.'}` };
    }

    // 3. GUARD: Drive ID Protection
    if (accion === 'descargar_de_drive' || accion === 'leer_archivo_drive') {
        let fid = datos.fileId || "";
        if (fid.includes('/') || fid.length < 10 || fid === "FILE_ID") {
             accion = 'ejecutar_comando';
             datos = { 
                 command: `echo "SYSTEM ERROR: Action '${accion}' requires a valid Google Drive FILE ID (alphanumeric hash), NOT a path. You provided: '${fid}'. FAILURE PREVENTED. Use 'buscar_en_drive' to find the ID first."` 
             };
        }
    }

    // 4. Validate Action
    if (!validActions.includes(accion)) {
        accion = 'ejecutar_comando';
        datos = { command: `echo "SYSTEM ERROR: Unknown action '${a.accion}'"` };
    }

    return { 
        json: { 
            ...item, 
            accion, 
            datos,
            action_count: actions.length
        } 
    };
});
"""

AGGREGATOR_CODE = """
// V1 MILESTONE: Robust Aggregation (Run Once ALL Compatible)
let result = "Success";
let structured_data = null;
const items = $input.all();

if (items.length > 0) {
  // Check first item for result types
  const first = items[0].json;
  
  // Case A: Google Drive Search/List results
  if (first.id && first.name) {
      result = items.map(i => `[FILE] ${i.json.name} (${i.json.id})`).join(", ");
      structured_data = items.map(i => ({
        id: i.json.id, 
        name: i.json.name, 
        mimeType: i.json.mimeType || 'unknown'
      }));
  } 
  // Case B: Command execution (stdout/stderr)
  else if (first.hasOwnProperty('stdout')) {
      // Map all stdouts if multiple commands ran
      result = items.map(i => i.json.stdout).filter(x=>x).join("\\n---\\n");
  }
  else if (first.hasOwnProperty('stderr')) {
       result = items.map(i => i.json.stderr).filter(x=>x).join("\\n---\\n");
  }
  // Case C: Generic Result
  else {
      // JSON.stringify safe fallback
      result = items.map(i => JSON.stringify(i.json)).join(" | ");
  }
}

// Context Retrieval - Robust Access
// We access 'Clean Actor' to get the original plan context passed down
// .last() gets the last execution of that node relative to current item
// but in 'Run Once All', context is unified.
const prev = $('Clean Actor').last().json; 

return [{ json: {
  action_taken: prev.accion, 
  tool_result: result,
  tool_result_data: structured_data,
  planner_instruction: prev.planner_instruction || prev.response, // Fallback keys 
  user_goal: prev.user_goal, 
  history: prev.history, 
  counter: prev.counter,
  chat_history: prev.chat_history
} }];
"""

UPDATE_STATE_CODE = """
// V1 MILESTONE: Robust State Update
const items = $input.all();
const item = items[0].json; 

const newHistory = item.history || [];

newHistory.push({
  role: "assistant", // Standardize role
  plan: item.planner_instruction,
  action: item.action_taken,
  result: item.tool_result,
  result_data: item.tool_result_data,
  timestamp: new Date().toISOString()
});

const newCounter = (item.counter || 0) + 1;

// Safety Cap (prevent infinite loops)
if (newCounter >= 25) {
     console.log('⚠️ Iteration Limit Reached (25)');
}

return [{ json: { 
  user_goal: item.user_goal, 
  history: newHistory, 
  counter: newCounter,
  chat_history: item.chat_history
} }];
"""

def patch():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT id, nodes FROM workflow_entity WHERE name = ?", (WORKFLOW_NAME,))
    row = cursor.fetchone()
    if not row:
        print(f"Error: Workflow '{WORKFLOW_NAME}' not found")
        return

    w_id, nodes_json = row
    nodes = json.loads(nodes_json)
    
    modified_count = 0
    
    for node in nodes:
        name = node.get('name')
        new_code = None
        
        if name == "Clean Actor":
            new_code = CLEAN_ACTOR_CODE
        elif name == "Aggregator" and node.get('type') == 'n8n-nodes-base.code':
            new_code = AGGREGATOR_CODE
        elif name == "Update State":
            new_code = UPDATE_STATE_CODE
            
        if new_code:
            print(f"Patching node: {name}...")
            # Handle different parameter structures (v1 vs v2 code node)
            if 'jsCode' in node.get('parameters', {}):
                node['parameters']['jsCode'] = new_code
            else:
                if 'code' not in node.get('parameters', {}): node['parameters']['code'] = {}
                node['parameters']['code']['js'] = new_code
            modified_count += 1

    if modified_count > 0:
        cursor.execute("UPDATE workflow_entity SET nodes = ? WHERE id = ?", (json.dumps(nodes), w_id))
        conn.commit()
        print(f"Success: Patched {modified_count} nodes in '{WORKFLOW_NAME}'.")
    else:
        print("Warning: No matching nodes found to patch.")

    conn.close()

if __name__ == "__main__":
    patch()
