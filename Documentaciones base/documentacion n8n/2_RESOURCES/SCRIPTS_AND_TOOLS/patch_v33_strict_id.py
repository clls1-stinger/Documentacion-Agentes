
import json
import os

# Paths
INPUT_WORKFLOW = "/home/emky/n8n/documentacion/FORENSICS_AND_LOGS/workflow_yes_patched_v32.json"
OUTPUT_WORKFLOW = "/home/emky/n8n/documentacion/FORENSICS_AND_LOGS/workflow_yes_patched_v33.json"

# Updated System Prompt for Planner Prep
NEW_PLANNER_PROMPT = """return $input.all().map(item => {
  const goal = item.json.user_goal;
  const chatHistory = item.json.chat_history || [];
  const stepHistory = item.json.history || [];
  const counter = item.json.counter || 0;

  let memoryText = chatHistory.length > 0 ? chatHistory.map(h => `User: ${h.user}\\nAI: ${h.ai}`).join("\\n---\\n") : "No hay historial.";
  let historyText = stepHistory.length > 0 ? stepHistory.map((h, i) => `STEP ${i+1}: ${h.action} -> ${h.result}`).join("\\n") : "Sin acciones previas.";

  const prompt = `IDENTIDAD: VEGA OS.
Usuario: Emky.
Estado del Sistema: Operativo.

=== CAPACIDADES (HERRAMIENTAS) ===
1. buscar_en_drive(query): Busca archivos en Google Drive.
   - Retorna: Lista de [FILE] Name (ID).
   - USA ESTA PRIMERO si necesitas un archivo.
2. descargar_de_drive(fileId, filename): Descarga de Drive al sistema local.
   - IMPORTANTE: REQUIERE 'fileId' (ej: '1abc...'), NO un path, NO un nombre.
   - Si no tienes el ID, usa buscar_en_drive primero.
3. subir_a_drive(filename): Sube un archivo local a Google Drive.
4. ejecutar_comando(command): Ejecuta comandos Linux (ls, grep, mkdir, unzip, zip, etc.).
   - USA 'ls -R' para ver archivos locales.
5. leer_archivo(path): Lee contenido de texto.
6. navegar_web(url): Navega la web.

=== OBJETIVO ACTUAL ===
${goal}

=== HISTORIAL DE ACCIONES (MEMORIA OPERATIVA) ===
${historyText}

=== PROTOCOLO DE RESPUESTA (ESTRICTO) ===
1. **NO ALUCINES IDs**: No inventes IDs de archivos. Si no lo ves en el historial, búscalo.
2. **NO USES PATHS EN DESCARGAS**: descargar_de_drive('mis datos', ...) -> ERROR. descargar_de_drive('1A2b...', ...) -> BIEN.
3. **LOGICA**: 
   - ¿Necesito un archivo? -> buscar_en_drive.
   - ¿Tengo el ID? -> descargar_de_drive.
   - ¿Tengo el archivo local? -> ejecutar_comando.
4. **NO HABLES MUCHO**: Accion directa.

=== FORMATO JSON ===
{
  "thought": "Tengo el ID del archivo X en el historial, ahora lo descargo...",
  "next_instruction": "Nombre_Funcion(args...)",
  "is_done": false,
  "final_response": null
}`;
        return { json: { prompt, history: stepHistory, chat_history: chatHistory, user_goal: goal, counter } };
});"""

# Updated JS Code for Clean Actor (Adding ID Check)
NEW_CLEAN_ACTOR_CODE = """
const item = $input.item.json;
let raw = item.final_answer || item.response || item.raw_stdout || "{}";
if (typeof raw !== 'string') raw = JSON.stringify(raw);

let parsed = {};
try { 
    const jsonMatch = raw.match(/```json\\s*([\\s\\S]*?)\\s*```/) || raw.match(/\\{.*\\}/s);
    if (jsonMatch) raw = jsonMatch[1] || jsonMatch[0];
    parsed = JSON.parse(raw); 
} catch(e) {
    parsed = { error: "JSON Parse failed", raw: raw };
}

let accion = (parsed.accion || parsed.action || "").toLowerCase();
let datos = parsed.datos || parsed.parameters || {};

const map = {
    'search_drive': 'buscar_en_drive',
    'download_file': 'descargar_de_drive',
    'file_download': 'descargar_de_drive',
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

let finalAccion = map[accion] || accion;

// --- CRITICAL SAFETY: FILE ID CHECK ---
if (finalAccion === 'descargar_de_drive') {
    const id = datos.fileId || datos.id;
    // Regex for typical Drive IDs (alphanumeric, ~20+ chars, usually starts with 1)
    // loose check: no slashes, length > 10
    if (!id || id.includes('/') || id.includes(' ') || id.length < 5) {
        finalAccion = 'ejecutar_comando'; // Hijack to echo error
        datos = { command: `echo "SYSTEM ERROR: 'descargar_de_drive' requires a valid Google Drive File ID, not a path or filename. You provided: '${id}'. USE 'buscar_en_drive' FIRST to find the ID."` };
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
        print(f"Error: Input file {INPUT_WORKFLOW} not found. Ensure v32 exists.")
        return

    with open(INPUT_WORKFLOW, 'r') as f:
        data = json.load(f)

    # Patch Planner Prep
    for node in data['nodes']:
        if node['name'] == 'Planner Prep':
            node['parameters']['jsCode'] = NEW_PLANNER_PROMPT
            print("Updated 'Planner Prep' prompt.")
        elif node['name'] == 'Clean Actor':
             node['parameters']['jsCode'] = NEW_CLEAN_ACTOR_CODE
             print("Updated 'Clean Actor' logic (ID Checks).")

    # Update Meta Name
    data['meta']['name'] = "Yes (Patched v33 - Strict ID)"

    with open(OUTPUT_WORKFLOW, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"Patched workflow v33 saved to {OUTPUT_WORKFLOW}")

if __name__ == "__main__":
    patch_workflow()
