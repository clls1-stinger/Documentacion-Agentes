
import json
import os

PATH = "/home/emky/n8n/documentacion/3_WORK_LOGS_AND_HISTORY/FORENSICS_AND_LOGS/workflow_yes_patched_v40.json"
OUTPUT = "/home/emky/n8n/documentacion/3_WORK_LOGS_AND_HISTORY/FORENSICS_AND_LOGS/workflow_yes_patched_v41.json"

with open(PATH, 'r') as f:
    nodes = json.load(f)

# Find existing full workflow to get connections (since v40 was just nodes)
DUMP_PATH = "/home/emky/n8n/documentacion/3_WORK_LOGS_AND_HISTORY/FORENSICS_AND_LOGS/workflow_yes_dump.json"
with open(DUMP_PATH, 'r') as f:
    full_wf = json.load(f)

connections = full_wf['connections']

# 1. Update Planner Prep (v41 Parallelism)
for node in nodes:
    if node['name'] == 'Planner Prep':
        node['parameters']['jsCode'] = r"""return $input.all().map(item => {
  const goal = item.json.user_goal;
  const chatHistory = item.json.chat_history || [];
  const stepHistory = item.json.history || [];
  const counter = item.json.counter || 0;

  let historyText = stepHistory.length > 0 
    ? stepHistory.map((h, i) => `STEP ${i+1}: Action(s): ${h.action} -> Result: ${h.result}`).join("\n") 
    : "Sin acciones previas.";

  const prompt = `IDENTIDAD: VEGA OS (Parallel Kernel).
Usuario: Emky.
Estado: Multi-Tasking Enabled.

=== CAPACIDADES ===
1. buscar_en_drive(query)
2. descargar_de_drive(fileId, filename)
3. subir_a_drive(filename)
4. ejecutar_comando(command)
5. leer_archivo(path)
6. navegar_web(url)

=== PARALLEL EXECUTION ===
You can now specify MULTIPLE actions to run at the same time.
If you need to search drive AND check local files, do both in one step.
The results will be gathered and sent back to you at once.

=== OBJETIVO ===
${goal}

=== MEMORIA ===
${historyText}

=== FORMATO JSON ===
{
  "thought": "Explicación de por qué estas acciones en paralelo...",
  "next_instruction": "Escribe aquí lo que quieres hacer (puedes listar varias cosas)",
  "is_done": false,
  "final_response": null
}`;
        return { json: { prompt, history: stepHistory, chat_history: chatHistory, user_goal: goal, counter } };
});"""

# 2. Update Actor Prep (Instruction to multi-action)
for node in nodes:
    if node['name'] == 'Actor Prep':
        node['parameters']['jsCode'] = r"""const item = $input.item.json;
const instruction = item.planner_output.next_instruction;
const prompt = `CONVIERTE ESTO A UN ARRAY DE ACCIONES JSON:
Instrucción: "${instruction}"

REGLAS:
- Si hay varias acciones, sepáralas.
- Usa el ENUM de acciones válido.

SALIDA: 
{ 
  "actions": [
    { "accion": "buscar_en_drive", "datos": { "query": "..." } },
    { "accion": "ejecutar_comando", "datos": { "command": "..." } }
  ]
}`;
return [{ json: { ...item, prompt, instruction } }];"""

# 3. Update Gemini Actor (Response Schema)
for node in nodes:
    if node['name'] == 'Gemini Actor':
        node['parameters']['additionalOptions']['responseSchema'] = json.dumps({
            "type": "OBJECT",
            "properties": {
                "actions": {
                    "type": "ARRAY",
                    "items": {
                        "type": "OBJECT",
                        "properties": {
                            "accion": {
                                "type": "STRING",
                                "enum": ["buscar_en_drive", "descargar_de_drive", "subir_a_drive", "ejecutar_comando", "leer_archivo", "navegar_web"]
                            },
                            "datos": {
                                "type": "OBJECT",
                                "properties": {
                                    "query": { "type": "STRING" },
                                    "fileId": { "type": "STRING" },
                                    "filename": { "type": "STRING" },
                                    "command": { "type": "STRING" },
                                    "path": { "type": "STRING" },
                                    "url": { "type": "STRING" }
                                }
                            }
                        },
                        "required": ["accion", "datos"]
                    }
                }
            },
            "required": ["actions"]
        })

# 4. Update Clean Actor (Multi-item output)
for node in nodes:
    if node['name'] == 'Clean Actor':
        node['parameters']['jsCode'] = r"""
const item = $input.item.json;
let raw = item.response || "{}";
if (typeof raw !== 'string') raw = JSON.stringify(raw);

let parsed = {};
try {
    const jsonMatch = raw.match(/```json\s*([\s\S]*?)\s*```/) || raw.match(/\{.*\}/s);
    if (jsonMatch) raw = jsonMatch[1] || jsonMatch[0];
    parsed = JSON.parse(raw);
} catch(e) { parsed = { actions: [] }; }

const actions = parsed.actions || (parsed.accion ? [parsed] : []);

const map = {
    'search_drive': 'buscar_en_drive',
    'download_file': 'descargar_de_drive',
    'run_command': 'ejecutar_comando',
    'run_shell_command': 'ejecutar_comando',
    'list_directory': 'ejecutar_comando',
    'ls': 'ejecutar_comando'
};

const validActions = ['buscar_en_drive', 'descargar_de_drive', 'subir_a_drive', 'ejecutar_comando', 'leer_archivo', 'navegar_web'];

return actions.map(a => {
    let accion = (a.accion || "").toLowerCase();
    let datos = a.datos || {};
    
    accion = map[accion] || accion;
    
    if (accion === 'ls') {
        datos.command = `ls -R ${datos.path || '.'}`;
        accion = 'ejecutar_comando';
    }

    if (!validActions.includes(accion)) {
        accion = 'ejecutar_comando';
        datos = { command: `echo "SYSTEM ERROR: Unknown action '${a.accion}'"` };
    }

    return { json: { ...item, accion, datos, action_count: actions.length } };
});"""

# 5. Add Aggregate Node
agg_node_id = "antigravity_aggregate_v41"
nodes.append({
    "parameters": {
        "aggregate": "aggregateAllItemData",
        "destinationField": "results",
        "include": "all",
        "options": {}
    },
    "id": agg_node_id,
    "name": "Aggregate Results",
    "type": "n8n-nodes-base.aggregate",
    "typeVersion": 1,
    "position": [2950, 3900]
})

# 6. Rewire Connections
# Tool outputs should go to 'Aggregate Results'
tool_nodes = ["Drive Search", "Save to Disk", "Execute Command", "Drive Upload"]
for tool in tool_nodes:
    if tool in connections:
        # Tool outputs originally went to 'Aggregator'
        # We change them to go to agg_node_id
        connections[tool]['main'] = [[{"node": "Aggregate Results", "type": "main", "index": 0}]]

# Connection from Aggregate Results to Aggregator
connections["Aggregate Results"] = {
    "main": [[{"node": "Aggregator", "type": "main", "index": 0}]]
}

# 7. Update Aggregator to handle the array
for node in nodes:
    if node['name'] == 'Aggregator':
        node['parameters']['jsCode'] = r"""
const items = $input.all();
const results = items[0].json.results || [];

let summary = results.map(r => {
    const action = r.accion || "Unknown";
    const result = r.stdout || (r.id ? `File ${r.name} (${r.id})` : "Success");
    return `${action}: ${result}`;
}).join(" | ");

// Access Previous State
const cleanActor = $('Clean Actor').last().json;

return [{ json: {
  action_taken: results.map(r => r.accion).join(", "),
  tool_result: summary,
  tool_result_data: results,
  planner_instruction: cleanActor.instruction,
  user_goal: cleanActor.user_goal,
  history: cleanActor.history,
  counter: cleanActor.counter,
  chat_history: cleanActor.chat_history
} }];"""

# Final construction
final_workflow = {
    "nodes": nodes,
    "connections": connections
}

with open(OUTPUT, 'w') as f:
    json.dump(final_workflow, f, indent=2)

print(f"Workflow v41 generated at {OUTPUT}")
