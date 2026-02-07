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

    # 1. RESTAURAR EL ALMA (ACTOR PREP IMPROVED)
    ACTOR_PREP_CODE = """
const item = $input.item.json;
const instruction = (item.planner_output && item.planner_output.next_instruction) ? item.planner_output.next_instruction : "Sin instrucción";
const history = item.history || [];
const structured_context = history.filter(h => h.result_data).map(h => h.result_data).flat();

const prompt = `ERES EL AGENTE EJECUTOR (ACTOR). Tu misión es razonar sobre la instrucción técnica y convertirla en una o varias acciones concretas.

INSTRUCCIÓN DEL PLANIFICADOR:
"${instruction}"

CONTEXTO HISTÓRICO Y ARCHIVOS:
${JSON.stringify(structured_context, null, 2)}

PASOS A SEGUIR:
1. Analiza qué herramientas necesitas: buscar_en_drive, descargar_de_drive, ejecutar_comando, leer_archivo, navegar_web.
2. Si la instrucción pide buscar algo localmente o contar archivos, usa 'ejecutar_comando' con 'find' o 'ls'.
3. Si pide archivos de Drive, usa 'buscar_en_drive' primero para obtener el ID.
4. Puedes ejecutar MÚLTIPLES acciones si es necesario para avanzar más rápido.

FORMATO DE SALIDA (ESTRICTAMENTE JSON):
Responde con un objeto que tenga una lista de ejecuciones bajo la clave "ejecuciones".

EJEMPLO:
{
  "ejecuciones": [
    { "herramienta": "ejecutar_comando", "parametros": { "command": "find . -name '*takeout*'" } },
    { "herramienta": "buscar_en_drive", "parametros": { "query": "name contains 'takeout'" } }
  ]
}

REGLA DE CONTEXTO: Si ya tienes un fileId en el contexto, úsalo directamente en lugar de buscarlo de nuevo.
RAZONA BREVEMENTE ANTES DEL JSON SI LO NECESITASH, PERO ASEGÚRATE DE QUE EL BLOQUE JSON SEA VÁLIDO.`;

return [{ json: { ...item, prompt, instruction } }];
"""

    # 2. CLEAN ACTOR (PARA MULTIPLES BLOQUES)
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
    'download_file': 'descargar_de_drive',
    'run_command': 'ejecutar_comando',
    'run_shell_command': 'ejecutar_comando',
    'execute_command': 'ejecutar_comando'
};

let actions = [];
if (parsed.ejecuciones && Array.isArray(parsed.ejecuciones)) {
    actions = parsed.ejecuciones;
} else if (parsed.actions && Array.isArray(parsed.actions)) {
    actions = parsed.actions;
} else if (parsed.herramienta || parsed.accion) {
    actions = [parsed];
} else if (parsed.error) {
    actions = [{ herramienta: 'ejecutar_comando', parametros: { command: `echo "ERROR: ${parsed.error}"` } }];
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

    # APLICAR CAMBIOS
    for node in nodes:
        if node['name'] == 'Actor Prep':
            node['parameters']['jsCode'] = ACTOR_PREP_CODE.strip()
            print("Parcheado Actor Prep: Devolviendo el Alma.")
        elif node['name'] == 'Clean Actor':
            node['parameters']['jsCode'] = CLEAN_ACTOR_CODE.strip()
            print("Parcheado Clean Actor: Filtrado de bloques múltiples activo.")

    # Guardar
    cursor.execute("UPDATE workflow_entity SET nodes = ?, updatedAt = datetime('now') WHERE id = ?", (json.dumps(nodes), w_id))
    conn.commit()
    conn.close()
    print("Workflow Reparado con Alma y Multi-Acción.")

if __name__ == "__main__":
    patch()
