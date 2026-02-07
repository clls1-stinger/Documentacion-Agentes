
import json
import os

# Paths
INPUT_WORKFLOW = "/home/emky/n8n/documentacion/FORENSICS_AND_LOGS/workflow_yes_patched_v33.json"
OUTPUT_WORKFLOW = "/home/emky/n8n/documentacion/FORENSICS_AND_LOGS/workflow_yes_patched_v34.json"

# Response Schema for Gemini Actor (Strict Typing)
RESPONSE_SCHEMA = json.dumps({
    "type": "OBJECT",
    "properties": {
        "accion": {
            "type": "STRING",
            "enum": ["buscar_en_drive", "descargar_de_drive", "subir_a_drive", "ejecutar_comando", "leer_archivo", "navegar_web"]
        },
        "datos": {
            "type": "OBJECT",
            "properties": {
                "query": {"type": "STRING"},
                "fileId": {"type": "STRING"},
                "filename": {"type": "STRING"},
                "command": {"type": "STRING"},
                "path": {"type": "STRING"},
                "url": {"type": "STRING"}
            }
        },
        "thought": {"type": "STRING"}
    },
    "required": ["accion", "datos"]
})

# Updated JS Code for Clean Actor (Adding run_shell_command capture)
NEW_CLEAN_ACTOR_CODE = """
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
    'file_download': 'descargar_de_drive',
    'run_command': 'ejecutar_comando',
    'run_shell_command': 'ejecutar_comando', // <--- FIX FOR USER REPORTED ISSUE
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

// Fix for run_shell_command with 'mkdr' or similar
if (accion === 'run_shell_command') {
    accion = 'ejecutar_comando';
}

let finalAccion = map[accion] || accion;

// --- CRITICAL SAFETY: FILE ID CHECK ---
if (finalAccion === 'descargar_de_drive') {
    const id = datos.fileId || datos.id;
    if (!id || id.includes('/') || id.includes(' ') || id.length < 5) {
        finalAccion = 'ejecutar_comando'; 
        datos = { command: `echo "SYSTEM ERROR: 'descargar_de_drive' requires a valid Google Drive File ID. You provided: '${id}'."` };
    }
}

// --- STANDARD SAFETY ---
const validActions = ['buscar_en_drive', 'descargar_de_drive', 'subir_a_drive', 'ejecutar_comando', 'leer_archivo', 'navegar_web'];

if (!validActions.includes(finalAccion)) {
    finalAccion = 'ejecutar_comando';
    datos = { command: `echo "SYSTEM ERROR: Action '${accion}' is unknown. Supported: ${validActions.join(', ')}."` };
}

return [{ json: { accion: finalAccion, datos, planner_instruction: item.instruction, user_goal: item.user_goal, history: item.history, counter: item.counter, chat_history: item.chat_history } }];
"""

def patch_workflow():
    if not os.path.exists(INPUT_WORKFLOW):
        print(f"Error: Input file {INPUT_WORKFLOW} not found.")
        return

    with open(INPUT_WORKFLOW, 'r') as f:
        data = json.load(f)

    # Patch Gemini Actor (Temperature & Schema)
    for node in data['nodes']:
        if node['name'] == 'Gemini Actor':
            # Lower Temperature
            node['parameters']['additionalOptions']['temperature'] = 0.0
            # Inject Response Schema
            node['parameters']['additionalOptions']['responseSchema'] = RESPONSE_SCHEMA
            print("Updated 'Gemini Actor' -> Temp: 0.0, Added Schema.")
        
        elif node['name'] == 'Gemini Planner':
             # Lower Planner Temperature too
             node['parameters']['additionalOptions']['temperature'] = 0.1
             print("Updated 'Gemini Planner' -> Temp: 0.1")

        elif node['name'] == 'Clean Actor':
             node['parameters']['jsCode'] = NEW_CLEAN_ACTOR_CODE
             print("Updated 'Clean Actor' mapping logic.")

    # Update Meta Name
    data['meta']['name'] = "Yes (Patched v34 - Schema+Temp)"

    with open(OUTPUT_WORKFLOW, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"Patched workflow v34 saved to {OUTPUT_WORKFLOW}")

if __name__ == "__main__":
    patch_workflow()
