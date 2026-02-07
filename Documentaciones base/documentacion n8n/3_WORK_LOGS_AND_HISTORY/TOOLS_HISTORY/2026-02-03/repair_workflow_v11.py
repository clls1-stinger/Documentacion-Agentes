import sqlite3
import json

# Config
DB_PATH = "/home/emky/.n8n/database.sqlite"
WORKFLOW_NAME = "Gemini ReAct Agent - Patched V11"

def patch():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT id, nodes FROM workflow_entity WHERE name = ?", (WORKFLOW_NAME,))
    row = cursor.fetchone()
    if not row:
        print(f"Workflow {WORKFLOW_NAME} not found")
        return

    w_id, nodes_json = row
    nodes = json.loads(nodes_json)

    # JS CODE FOR ACTOR PREP
    ACTOR_PREP_CODE = """
const item = $input.item.json;
const instruction = (item.planner_output && item.planner_output.next_instruction) ? item.planner_output.next_instruction : "No instruction";
const structured_context = (item.history || []).filter(h => h.result_data).map(h => h.result_data).flat();

const prompt = `TAREA: Convierte la instrucción técnica en un objeto JSON estructurado para el Router de Herramientas.

INSTRUCCIÓN DEL PLANIFICADOR:
"${instruction}"

CONTEXTO DE ARCHIVOS (IDs y nombres disponibles):
${JSON.stringify(structured_context, null, 2)}

FORMATO DE SALIDA (JSON PURO):
{
  "accion": "nombre_de_la_accion",
  "datos": { "parametro": "valor" }
}

ACCIONES SOPORTADAS:
1. buscar_en_drive(query: string) -> accion: "buscar_en_drive", datos: { "query": "..." }
2. descargar_de_drive(fileId: string, filename: string) -> accion: "descargar_de_drive", datos: { "fileId": "...", "filename": "..." }
3. subir_a_drive(filename: string) -> accion: "subir_a_drive", datos: { "filename": "..." }
4. ejecutar_comando(command: string) -> accion: "ejecutar_comando", datos: { "command": "..." }
5. leer_archivo(filepath: string) -> accion: "leer_archivo", datos: { "filepath": "..." }
6. navegar_web(url: string) -> accion: "navegar_web", datos: { "url": "..." }

REGLA CRÍTICA: USA LOS IDs EXACTOS DEL CONTEXTO SI SE MENCIONA UN ARCHIVO.
RESPONDE SOLO CON EL JSON.`;

return [{ json: { ...item, prompt, instruction } }];
"""

    # JS CODE FOR CLEAN ACTOR
    CLEAN_ACTOR_CODE = """
const item = $input.item.json;
let raw = item.final_answer || item.response || item.raw_stdout || "{}";
if (typeof raw !== 'string') raw = JSON.stringify(raw);

let parsed = {};
try { 
    // Strip markdown if present
    const jsonMatch = raw.match(/```json\\s*([\\s\\S]*?)\\s*```/) || raw.match(/\\{.*\\}/s);
    if (jsonMatch) raw = jsonMatch[1] || jsonMatch[0];
    parsed = JSON.parse(raw); 
} catch(e) {
    parsed = { error: "JSON Parse failed", raw: raw };
}

let accion = (parsed.accion || parsed.action || "").toLowerCase();
let datos = parsed.datos || parsed.parameters || {};

// Mapping for consistency
const map = {
    'search_drive': 'buscar_en_drive',
    'download_file': 'descargar_de_drive',
    'run_command': 'ejecutar_comando',
    'run_shell_command': 'ejecutar_comando',
    'execute_command': 'ejecutar_comando',
    'list_directory': 'ejecutar_comando',
    'read_file': 'leer_archivo',
    'browse': 'navegar_web',
    'browse_web': 'navegar_web',
    'google_search': 'navegar_web'
};

accion = map[accion] || accion;

return [{ json: { 
    accion, 
    datos, 
    planner_instruction: item.instruction, 
    user_goal: item.user_goal, 
    history: item.history, 
    counter: item.counter, 
    chat_history: item.chat_history 
} }];
"""

    # TOOL ROUTER RULES
    ROUTER_RULES = {
        "values": [
            {
                "conditions": {
                    "options": {"caseSensitive": True, "leftValue": "", "typeValidation": "strict", "version": 2},
                    "conditions": [{"leftValue": "={{ $json.accion }}", "operator": {"type": "string", "operation": "equals"}, "rightValue": "buscar_en_drive"}],
                    "combinator": "and"
                }
            },
            {
                "conditions": {
                    "options": {"caseSensitive": True, "leftValue": "", "typeValidation": "strict", "version": 2},
                    "conditions": [{"leftValue": "={{ $json.accion }}", "operator": {"type": "string", "operation": "equals"}, "rightValue": "descargar_de_drive"}],
                    "combinator": "and"
                }
            },
            {
                "conditions": {
                    "options": {"caseSensitive": True, "leftValue": "", "typeValidation": "strict", "version": 2},
                    "conditions": [{"leftValue": "={{ $json.accion }}", "operator": {"type": "string", "operation": "equals"}, "rightValue": "subir_a_drive"}],
                    "combinator": "and"
                }
            },
            {
                "conditions": {
                    "options": {"caseSensitive": True, "leftValue": "", "typeValidation": "strict", "version": 2},
                    "conditions": [{"leftValue": "={{ $json.accion }}", "operator": {"type": "string", "operation": "equals"}, "rightValue": "ejecutar_comando"}],
                    "combinator": "and"
                }
            },
            {
                "conditions": {
                    "options": {"caseSensitive": True, "leftValue": "", "typeValidation": "strict", "version": 2},
                    "conditions": [{"leftValue": "={{ $json.accion }}", "operator": {"type": "string", "operation": "equals"}, "rightValue": "leer_archivo"}],
                    "combinator": "and"
                }
            },
            {
                "conditions": {
                    "options": {"caseSensitive": True, "leftValue": "", "typeValidation": "strict", "version": 2},
                    "conditions": [{"leftValue": "={{ $json.accion }}", "operator": {"type": "string", "operation": "equals"}, "rightValue": "navegar_web"}],
                    "combinator": "and"
                }
            }
        ]
    }

    # APPLY PATCHES
    for node in nodes:
        if node['name'] == 'Actor Prep':
            node['parameters']['jsCode'] = ACTOR_PREP_CODE.strip()
            print("Patched Actor Prep")
        elif node['name'] == 'Clean Actor':
            node['parameters']['jsCode'] = CLEAN_ACTOR_CODE.strip()
            print("Patched Clean Actor")
        elif node['name'] == 'Tool Router':
            node['parameters']['rules'] = ROUTER_RULES
            print("Patched Tool Router")
        elif node['name'] == 'Drive Search':
            # Force v3 search
            node['parameters']['resource'] = 'file'
            node['parameters']['operation'] = 'search'
            if 'filter' not in node['parameters']: node['parameters']['filter'] = {}
            node['parameters']['filter']['q'] = "={{ $json.datos.query }}"
            print("Patched Drive Search")

    # Save
    cursor.execute("UPDATE workflow_entity SET nodes = ?, updatedAt = datetime('now') WHERE id = ?", (json.dumps(nodes), w_id))
    conn.commit()
    conn.close()
    print("Workflow 'Gemini ReAct Agent - Patched V11' repaired and saved.")

if __name__ == "__main__":
    patch()
