
import json
import os

# Paths
INPUT_WORKFLOW = "/home/emky/n8n/documentacion/FORENSICS_AND_LOGS/workflow_yes_patched_v31.json"
OUTPUT_WORKFLOW = "/home/emky/n8n/documentacion/FORENSICS_AND_LOGS/workflow_yes_patched_v32.json"

# New JS Code for Clean Actor
NEW_CODE = """
const item = $input.item.json;
let raw = item.final_answer || item.response || item.raw_stdout || "{}";
// Handle cases where raw is an object/array (already parsed)
if (typeof raw !== 'string') {
    raw = JSON.stringify(raw);
}

let parsed = {};
try { 
    // Clean up potential markdown blocks if present (though Parse Planner usually handles this)
    const jsonMatch = raw.match(/```json\\s*([\\s\\S]*?)\\s*```/) || raw.match(/\\{.*\\}/s);
    if (jsonMatch) raw = jsonMatch[1] || jsonMatch[0];
    parsed = JSON.parse(raw); 
} catch(e) {
    // If parse fails, treat raw as generic text, maybe log error
    parsed = { error: "JSON Parse failed", raw: raw };
}

let accion = (parsed.accion || parsed.action || "").toLowerCase();
let datos = parsed.datos || parsed.parameters || {};

// --- HALLUCINATION FIXES ---
const map = {
    'search_drive': 'buscar_en_drive',
    'download_file': 'descargar_de_drive',
    'run_command': 'ejecutar_comando',
    'list_directory': 'ejecutar_comando', 
    'ls': 'ejecutar_comando',
    'read_file': 'leer_archivo',
    'browse': 'navegar_web'
};

// --- PARAMETER TRANSFORMERS ---
if (accion === 'list_directory' || accion === 'ls') {
    const path = datos.dir_path || datos.path || '.';
    datos.command = `ls -R ${path}`;
    accion = 'ejecutar_comando';
}

const mappedAccion = map[accion] || accion;

// --- SAFETY & FEEDBACK ---
const validActions = ['buscar_en_drive', 'descargar_de_drive', 'subir_a_drive', 'ejecutar_comando', 'leer_archivo', 'navegar_web'];

if (!validActions.includes(mappedAccion)) {
    // Self-Correcting Error: Tell the agent the tool was wrong via the 'Execute Command' channel
    let errorMsg = `SYSTEM ERROR: Action '${accion}' is unknown. Supported actions: ${validActions.join(', ')}.`;
    if (!accion) errorMsg = "SYSTEM ERROR: No 'accion' field found in tool output.";
    
    accion = 'ejecutar_comando';
    datos = { command: `echo "${errorMsg}"` };
} else {
    accion = mappedAccion;
}

return [{ json: { accion, datos, planner_instruction: item.instruction, user_goal: item.user_goal, history: item.history, counter: item.counter, chat_history: item.chat_history } }];
"""

def patch_workflow():
    if not os.path.exists(INPUT_WORKFLOW):
        print(f"Error: Input file {INPUT_WORKFLOW} not found.")
        return

    with open(INPUT_WORKFLOW, 'r') as f:
        data = json.load(f)

    # Find Clean Actor
    found = False
    for node in data['nodes']:
        if node['name'] == 'Clean Actor':
            node['parameters']['jsCode'] = NEW_CODE
            print("Successfully updated 'Clean Actor' code.")
            found = True
            break
    
    if not found:
        print("Error: 'Clean Actor' node not found.")
        return

    # Update Meta Name
    data['meta']['name'] = "Yes (Patched v32 - Fix Loop)"

    with open(OUTPUT_WORKFLOW, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"Patched workflow saved to {OUTPUT_WORKFLOW}")

if __name__ == "__main__":
    patch_workflow()
