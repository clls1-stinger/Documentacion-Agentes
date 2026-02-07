import sqlite3
import json

# Config
DB_PATH = "/home/emky/.n8n/database.sqlite"
TARGET_ID = "osenZpfZMpCRQBSL"

def patch():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, nodes FROM workflow_entity WHERE id = ?", (TARGET_ID,))
    row = cursor.fetchone()
    if not row:
        print(f"Workflow with ID {TARGET_ID} not found")
        return

    w_id, w_name, nodes_json = row
    print(f"Patching workflow: {w_name} ({w_id})")
    nodes = json.loads(nodes_json)

    # 1. ACTUALIZAR ROUTER (Rules por ACCION)
    ROUTER_RULES = {
        "values": [
            {
                "conditions": {
                    "conditions": [{"leftValue": "={{ $json.accion }}", "operator": {"type": "string", "operation": "equals"}, "rightValue": "buscar_en_drive"}]
                }
            },
            {
                "conditions": {
                    "conditions": [{"leftValue": "={{ $json.accion }}", "operator": {"type": "string", "operation": "equals"}, "rightValue": "descargar_de_drive"}]
                }
            },
            {
                "conditions": {
                    "conditions": [{"leftValue": "={{ $json.accion }}", "operator": {"type": "string", "operation": "equals"}, "rightValue": "subir_a_drive"}]
                }
            },
            {
                "conditions": {
                    "conditions": [{"leftValue": "={{ $json.accion }}", "operator": {"type": "string", "operation": "equals"}, "rightValue": "ejecutar_comando"}]
                }
            },
            {
                "conditions": {
                    "conditions": [{"leftValue": "={{ $json.accion }}", "operator": {"type": "string", "operation": "equals"}, "rightValue": "leer_archivo"}]
                }
            },
            {
                "conditions": {
                    "conditions": [{"leftValue": "={{ $json.accion }}", "operator": {"type": "string", "operation": "equals"}, "rightValue": "navegar_web"}]
                }
            }
        ]
    }

    # 2. CLEAN ACTOR (PARA MULTIPLES BLOQUES + MAPEO)
    CLEAN_ACTOR_CODE = """
const item = $input.item.json;
let raw = item.final_answer || item.response || item.raw_stdout || "{}";
if (typeof raw !== 'string') raw = JSON.stringify(raw);

let parsed = {};
try { 
    const jsonMatch = raw.match(/```json\\\\s*([\\\\s\\\\S]*?)\\\\s*```/) || raw.match(/\\\\{.*\\\\}/s);
    if (jsonMatch) raw = jsonMatch[1] || jsonMatch[0];
    parsed = JSON.parse(raw); 
} catch(e) {
    parsed = { error: "Parse Error", raw: raw };
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
    'navegar_web': 'navegar_web',
    'browse': 'navegar_web'
};

let actions = [];
if (parsed.ejecuciones && Array.isArray(parsed.ejecuciones)) {
    actions = parsed.ejecuciones;
} else if (parsed.actions && Array.isArray(parsed.actions)) {
    actions = parsed.actions;
} else if (parsed.herramienta || parsed.accion || parsed.action) {
    actions = [parsed];
}

return actions.map(a => {
    let tool = (a.herramienta || a.accion || a.action || "").toLowerCase();
    let params = a.parametros || a.datos || a.parameters || {};
    tool = map[tool] || tool;

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

    # 3. ACTOR PREP (EL ALMA)
    ACTOR_PREP_CODE = """
const item = $input.item.json;
const instruction = (item.planner_output && item.planner_output.next_instruction) ? item.planner_output.next_instruction : (item.instruction || "Sin instrucción");
const history = item.history || [];
const structured_context = history.filter(h => h.result_data).map(h => h.result_data).flat();

const prompt = `ERES VEGA, EL AGENTE EJECUTOR (ACTOR). 

INSTRUCCIÓN DEL PLANIFICADOR:
"${instruction}"

CONTEXTO HISTÓRICO Y ARCHIVOS:
${JSON.stringify(structured_context, null, 2)}

TAREA: Analiza la instrucción y genera el JSON de herramientas necesario.
- Puedes ejecutar múltiples acciones en la lista "ejecuciones".
- Usa: buscar_en_drive, descargar_de_drive, ejecutar_comando, leer_archivo, navegar_web.

FORMATO DE SALIDA (JSON):
{
  "ejecuciones": [
    { "herramienta": "ejecutar_comando", "parametros": { "command": "..." } }
  ]
}

RAZONA ANTES DEL JSON SI ES NECESARIO.`;

return [{ json: { ...item, prompt, instruction } }];
"""

    for node in nodes:
        if node['name'] == 'Tool Router':
            node['parameters']['rules'] = ROUTER_RULES
            print("Patched Tool Router")
        if node['name'] == 'Clean Actor':
            node['parameters']['jsCode'] = CLEAN_ACTOR_CODE.strip()
            print("Patched Clean Actor")
        if node['name'] == 'Actor Prep':
            node['parameters']['jsCode'] = ACTOR_PREP_CODE.strip()
            print("Patched Actor Prep")

    cursor.execute("UPDATE workflow_entity SET nodes = ?, updatedAt = datetime('now') WHERE id = ?", (json.dumps(nodes), TARGET_ID))
    conn.commit()
    conn.close()
    print(f"Workflow '{w_name}' (ID: {TARGET_ID}) REPARADO.")

if __name__ == "__main__":
    patch()
