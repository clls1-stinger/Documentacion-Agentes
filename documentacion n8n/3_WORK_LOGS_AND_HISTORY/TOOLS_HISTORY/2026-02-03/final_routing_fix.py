import sqlite3
import json
import os

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

    # 1. NEW CLEAN ACTOR (Surgical Fix)
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
    parsed = { error: "JSON Parse failed", raw: raw };
}

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
    'navegar_web': 'navegar_web'
};

let actions = [];
// Process parallel executions if present
if (parsed.ejecuciones && Array.isArray(parsed.ejecuciones)) {
    actions = parsed.ejecuciones.map(e => ({
        accion: toolMap[e.herramienta || e.action] || e.herramienta || e.action,
        datos: e.parametros || e.datos || {}
    }));
} else if (parsed.accion || parsed.action) {
    actions.push({
        accion: toolMap[parsed.accion || parsed.action] || parsed.accion || parsed.action,
        datos: parsed.datos || parsed.parameters || {}
    });
} else {
    actions.push({ accion: 'unknown', datos: { raw_output: raw } });
}

return actions.map(a => ({
    json: { 
        accion: a.accion,
        datos: a.datos,
        planner_instruction: item.instruction || "Acción técnica", 
        user_goal: item.user_goal, 
        history: item.history, 
        counter: item.counter, 
        chat_history: item.chat_history 
    }
}));
"""

    # 2. NEW TOOL ROUTER RULES (Strict Field Matching)
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

    # Apply
    for node in nodes:
        if node['name'] == 'Clean Actor':
            node['parameters']['jsCode'] = CLEAN_ACTOR_CODE.strip()
            print("Fixed Clean Actor Parallel Mapping")
        if node['name'] == 'Tool Router':
            node['parameters']['rules'] = ROUTER_RULES
            node['parameters']['mode'] = 'rules'
            print("Fixed Tool Router Strict Field Routing")
        if node['name'] == 'Drive Search':
            node['parameters']['operation'] = 'search'
            node['parameters']['resource'] = 'file'
            print("Fixed Drive Search operation")

    cursor.execute("UPDATE workflow_entity SET nodes = ?, updatedAt = datetime('now') WHERE id = ?", (json.dumps(nodes), w_id))
    conn.commit()
    conn.close()
    print("Workflow 'Gemini ReAct Agent - Patched V11' REPAIRED DEFINITIVELY.")

if __name__ == "__main__":
    patch()
