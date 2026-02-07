
import sqlite3
import json
import sys
from pathlib import Path

# Config
N8N_DB = Path.home() / ".n8n" / "database.sqlite"
WORKFLOW_NAME = "Gemini ReAct Agent - Patched V11"

# System Map to inject
SYSTEM_MAP = {
    "MOUNT_POINT": "/run/media/emky/MEGATRON",
    "OBSIDIAN_ROOT": "/run/media/emky/MEGATRON/Google Drive/Habitos Obsidian",
    "DAILY_NOTES_DIR": "/run/media/emky/MEGATRON/Google Drive/Habitos Obsidian/Hábitos/Notas Diarias",
    "PROJECTS_DIR": "/run/media/emky/MEGATRON/Google Drive/Habitos Obsidian/CODE",
    "WORKFLOWS_DIR": "/home/emky/n8n/workflows_antigravity",
    "BRAIN_DIR": "/home/emky/.gemini/antigravity/brain"
}

def get_workflow_from_db():
    conn = sqlite3.connect(N8N_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT id, nodes, connections, staticData, settings, name FROM workflow_entity WHERE name = ?", (WORKFLOW_NAME,))
    result = cursor.fetchone()
    conn.close()
    if not result:
        print(f"❌ Workflow '{WORKFLOW_NAME}' not found")
        sys.exit(1)
    return {'id': result[0], 'nodes': json.loads(result[1]), 'connections': json.loads(result[2]), 'staticData': json.loads(result[3]), 'settings': json.loads(result[4]), 'name': result[5]}

def save_workflow_to_db(workflow):
    conn = sqlite3.connect(N8N_DB)
    cursor = conn.cursor()
    cursor.execute("UPDATE workflow_entity SET nodes = ? WHERE id = ?", (json.dumps(workflow['nodes']), workflow['id']))
    conn.commit()
    conn.close()
    print(f"💾 Updated workflow ID {workflow['id']}")

def patch_actor_prep_node(workflow):
    nodes = workflow['nodes']
    
    actor_prep_node = None
    for node in nodes:
        if node['name'] == 'Actor Prep':
            actor_prep_node = node
            break
            
    if not actor_prep_node:
        print("❌ 'Actor Prep' node not found")
        return False

    # Serialize map for injection
    system_map_json = json.dumps(SYSTEM_MAP, indent=2)

    # Enhanced 'Actor Prep' logic with SYSTEM MAP Injection
    new_code = f"""
const item = $input.item.json;
const instruction = (item.planner_output && item.planner_output.next_instruction) ? item.planner_output.next_instruction : (item.instruction || "Sin instrucción");
const history = item.history || [];

// Extraemos datos de búsquedas previas
const filesFound = history
  .filter(h => h.result_data)
  .map(h => h.result_data)
  .flat();

// MAPA DEL SISTEMA (Inyectado via Patch)
const SYSTEM_MAP = {system_map_json};

const prompt = `ERES VEGA, EL AGENTE EJECUTOR (ACTOR). 

INSTRUCCIÓN DEL PLANIFICADOR:
"${{instruction}}"

MAPA DEL SISTEMA (RUTAS VÁLIDAS):
Usa estas rutas base para leer/escribir archivos locales. NO INVENTES OTRAS RUTAS.
${{JSON.stringify(SYSTEM_MAP, null, 2)}}

CONTEXTO HISTÓRICO Y ARCHIVOS DISPONIBLES (Usa estos IDs exactos para Drive):
${{JSON.stringify(filesFound, null, 2)}}

TAREA: Analiza la instrucción y genera el JSON de herramientas necesario.
- Si buscas archivos locales, usa las rutas del MAPA DEL SISTEMA.
- Si buscas en Drive, usa buscar_en_drive.
- Si descargas, usa descargar_de_drive con el ID exacto.

FORMATO DE SALIDA (JSON):
{{
  "ejecuciones": [
    {{ "herramienta": "...", "parametros": {{ ... }} }}
  ]
}}

RAZONA ANTES DEL JSON.`;

return [{{ json: {{ ...item, prompt, instruction }} }}];
"""
    actor_prep_node['parameters']['jsCode'] = new_code
    print("✅ 'Actor Prep' patched with SYSTEM MAP + Memory logic.")
    return True

if __name__ == "__main__":
    wf = get_workflow_from_db()
    if patch_actor_prep_node(wf):
        save_workflow_to_db(wf)
