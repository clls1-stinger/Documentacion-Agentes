
const item = $input.item.json;
let raw = item.final_answer || item.response || item.raw_stdout || "{}";
// Handle cases where raw is an object/array (already parsed)
if (typeof raw !== 'string') {
    raw = JSON.stringify(raw);
}

let parsed = {};
try { 
    // Clean up potential markdown blocks if present (though Parse Planner usually handles this)
    const jsonMatch = raw.match(/```json\s*([\s\S]*?)\s*```/) || raw.match(/\{.*\}/s);
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

