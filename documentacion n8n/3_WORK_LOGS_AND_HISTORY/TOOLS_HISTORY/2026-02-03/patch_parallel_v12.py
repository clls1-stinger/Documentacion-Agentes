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

    # JS CODE FOR CLEAN ACTOR (WITH PARALLEL SUPPORT)
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

// Map for tools
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

// Check for Multiple Actions (Parallelism)
let actions = [];
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
    // Fallback or Error
    actions.push({ accion: 'error', datos: { error: "No action found" } });
}

// Return multiple items for n8n to process in parallel
return actions.map(a => ({
    json: { 
        ...a,
        planner_instruction: item.instruction || "Acción múltiple", 
        user_goal: item.user_goal, 
        history: item.history, 
        counter: item.counter, 
        chat_history: item.chat_history 
    }
}));
"""

    # TOOL ROUTER RULES (CLEAN VERSION)
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
        if node['name'] == 'Clean Actor':
            node['parameters']['jsCode'] = CLEAN_ACTOR_CODE.strip()
            print("Patched Clean Actor for Parallel Actions")
        elif node['name'] == 'Tool Router':
            node['parameters']['rules'] = ROUTER_RULES
            print("Patched Tool Router with cleaner rules")
        elif node['name'] == 'Drive Search':
            # Fix operation to 'search' to avoid the 'execute' undefined error
            node['parameters']['operation'] = 'search'
            node['parameters']['resource'] = 'file'
            if 'filter' not in node['parameters']: node['parameters']['filter'] = {}
            node['parameters']['filter']['q'] = "={{ $json.datos.query || $json.datos.q }}"
            print("Fixed Drive Search operation")
        elif node['name'] == 'Aggregator':
            # Ensure it can handle whatever comes
            node['parameters']['jsCode'] = node['parameters']['jsCode'].replace('($json.datos.query)', '($json.datos.query || $json.datos.q || "")')

    # Save back
    cursor.execute("UPDATE workflow_entity SET nodes = ?, updatedAt = datetime('now') WHERE id = ?", (json.dumps(nodes), w_id))
    conn.commit()
    conn.close()
    print("Workflow patched for Parallel Execution and Strict Routing!")

if __name__ == "__main__":
    patch()
