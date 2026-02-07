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

    # 1. ACTUALIZAR ROUTER (Rules por ACCION)
    # Basado en la imagen del usuario y los nodos que tiene conectados:
    # Output 0 -> Drive Search (buscar_en_drive)
    # Output 1 -> Drive Download (descargar_de_drive)
    # Output 2 -> Drive Upload (subir_a_drive)
    # Output 3 -> Terminal (ejecutar_comando)
    # Output 4 -> Read File (leer_archivo)
    # Output 5 -> Web (navegar_web)

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

    # 2. ASEGURAR QUE CLEAN ACTOR MAPEE TODO A ESOS NOMBRES
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
} else if (parsed.herramienta || parsed.accion) {
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
            planner_instruction: item.instruction,
            user_goal: item.user_goal,
            history: item.history,
            counter: item.counter,
            chat_history: item.chat_history
        } 
    };
});
"""

    for node in nodes:
        if node['name'] == 'Tool Router':
            node['parameters']['rules'] = ROUTER_RULES
            print("Router re-configurado con reglas de ACCIÓN.")
        if node['name'] == 'Clean Actor':
            node['parameters']['jsCode'] = CLEAN_ACTOR_CODE.strip()
            print("Clean Actor mapeado.")

    cursor.execute("UPDATE workflow_entity SET nodes = ?, updatedAt = datetime('now') WHERE id = ?", (json.dumps(nodes), w_id))
    conn.commit()
    conn.close()
    print("Workflow actualizado para ruteo manual por ACCIÓN.")

if __name__ == "__main__":
    patch()
