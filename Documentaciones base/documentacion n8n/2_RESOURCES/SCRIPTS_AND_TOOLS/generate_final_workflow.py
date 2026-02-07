#!/usr/bin/env python3
"""
📄 Generate Final Patched Workflow File

Este script implementa la estrategia 'Nuke and Pave' en memoria y, en lugar de
interactuar con la base de datos, guarda el resultado final en un archivo JSON
limpio para que el usuario lo pueda importar manualmente.
"""

import json
import sys
import uuid
from pathlib import Path

# --- Configuración ---
BASE_WORKFLOW_PATH = Path("./documentacion/FORENSICS_AND_LOGS/workflow_yes_dump.json")
FINAL_WORKFLOW_PATH = Path("./FINAL_PATCHED_WORKFLOW.json") # Guardar en el CWD
PATCHED_WORKFLOW_NAME = "Gemini ReAct Agent - FINAL"
PROMPT_FILE_PATH = Path("./documentacion/SCRIPTS_AND_TOOLS/prompt_v4.txt")

# --- Plantilla de Código JS para Planner Prep ---
JS_PLANNER_PREP_TEMPLATE = r"""return $input.all().map(item => {{
  const goal = item.json.user_goal;
  const history = item.json.history || [];
  const counter = item.json.counter || 0;

  let historyText = "No se ha ejecutado ninguna acción aún.";
  if (history.length > 0) {{
    historyText = history.map((h, i) => {{
      let details = 'PASO ' + (i + 1) + ':\n' 
                  + '- El Planner decidió: ' + h.plan + '\n' 
                  + '- El Actor ejecutó: ' + h.action + '\n' 
                  + '- Resultado: ' + h.result;
      if (h.result_data && Array.isArray(h.result_data) && h.result_data.length > 0) {{
        const dataString = JSON.stringify(h.result_data, null, 2);
        details += '\n- DATOS DISPONIBLES (usa estos IDs exactos):\n' + dataString;
      }}
      return details;
    }}).join('\n\n');
  }}

  const prompt = `{PROMPT_PLACEHOLDER}`;

  return {{ json: {{ prompt, history, user_goal: goal, counter }} }};
}});"""

# --- Código JS para Aggregator ---
JS_AGGREGATOR_CODE = r"""let result = "Success";
let structured_data = null;

if (items.length > 0) {{
  if (items[0].json.id && items[0].json.name) {{
     result = items.map(i => `[FILE] ${i.json.name} (${i.json.id})`).join(", ");
     structured_data = items.map(i => ({{
       id: i.json.id, 
       name: i.json.name, 
       mimeType: i.json.mimeType || 'unknown'
     }}));
  }} 
  else if (items[0].json.hasOwnProperty('stdout')) {{
     result = items[0].json.stdout;
  }}
  else if (items[0].json.hasOwnProperty('stderr')) {{
     result = items[0].json.stderr;
  }}
  else if (items[0].binary) {{
     result = "Binary data processed successfully.";
  }}
  else {{
    result = "Resultado de herramienta no reconocido, pero la operación fue exitosa.";
  }}
}} else {{
  result = "La herramienta se ejecutó pero no produjo ningún resultado (ej. búsqueda sin resultados).";
}}

const prev = $('Clean Actor').last().json;
return [{{ json: {{
  action_taken: prev.accion, 
  tool_result: result,
  tool_result_data: structured_data,
  planner_instruction: prev.instruction, 
  user_goal: prev.user_goal, 
  history: prev.history, 
  counter: prev.counter
}} }}];"""

# --- Definición de Reglas del Router (Regex) ---
ROUTER_RULES_MAP = {
    "buscar_en_drive": "/buscar.*drive/i",
    "descargar_de_drive": "/descargar.*drive/i",
    "subir_a_drive": "/subir.*drive/i",
    "ejecutar_comando": "/ejecutar.*comando/i",
    "leer_archivo": "/leer.*archivo/i",
    "navegar_web": "/navegar.*web/i",
}
CORRECT_ROUTER_INPUT_PATH = "={{ $json.planner_output.next_instruction }}"

def main():
    print(f"📄 Generando archivo de workflow final: '{FINAL_WORKFLOW_PATH}'...")
    
    # Cargar el workflow base
    try:
        with open(BASE_WORKFLOW_PATH, 'r', encoding='utf-8') as f:
            workflow_data = json.load(f)
    except FileNotFoundError:
        print(f"❌ Error: Archivo de workflow base no encontrado: '{BASE_WORKFLOW_PATH}'")
        sys.exit(1)

    # Establecer nuevo nombre
    workflow_data['name'] = PATCHED_WORKFLOW_NAME
    # Borrar el ID existente para que n8n genere uno nuevo en la importación
    if 'id' in workflow_data:
        del workflow_data['id']
    nodes = workflow_data['nodes']

    # Aplicar parche a Planner Prep
    planner_prep_node = next((n for n in nodes if n.get('name') == 'Planner Prep'), None)
    if planner_prep_node:
        try:
            prompt_text = PROMPT_FILE_PATH.read_text(encoding='utf-8')
            prompt_text = prompt_text.replace('\\', '\\\\').replace('`', r'`')
            planner_prep_node['parameters']['jsCode'] = JS_PLANNER_PREP_TEMPLATE.replace('{PROMPT_PLACEHOLDER}', prompt_text)
            print("✅ Parche 'Planner Prep' aplicado a la estructura en memoria.")
        except FileNotFoundError:
            print(f"❌ Error: Archivo de prompt '{PROMPT_FILE_PATH}' no encontrado.")
            sys.exit(1)
    
    # Aplicar parche a Aggregator
    aggregator_node = next((n for n in nodes if n.get('name') == 'Aggregator'), None)
    if aggregator_node:
        aggregator_node['parameters']['jsCode'] = JS_AGGREGATOR_CODE
        print("✅ Parche 'Aggregator' aplicado a la estructura en memoria.")

    # Aplicar parche a Tool Router
    tool_router_node = next((n for n in nodes if n.get('name') == 'Tool Router'), None)
    if tool_router_node:
        rules = tool_router_node['parameters']['rules']['values']
        for rule in rules:
            condition = rule['conditions']['conditions'][0]
            condition['leftValue'] = CORRECT_ROUTER_INPUT_PATH
            condition['operator']['operation'] = 'regex'
            original_value_key = condition.get('rightValue', '').strip('/').strip('i')
            if original_value_key in ROUTER_RULES_MAP:
                condition['rightValue'] = ROUTER_RULES_MAP[original_value_key]
        print("✅ Parche 'Tool Router' aplicado a la estructura en memoria.")

    # Guardar el workflow final a un archivo JSON
    try:
        with open(FINAL_WORKFLOW_PATH, 'w', encoding='utf-8') as f:
            json.dump(workflow_data, f, indent=2, ensure_ascii=False)
        print(f"\n✨ ¡Éxito! El workflow final y completamente parcheado ha sido guardado en:")
        print(f"   {FINAL_WORKFLOW_PATH.resolve()}")
        print("\nPor favor, importa este archivo manualmente en tu instancia de n8n.")
    except Exception as e:
        print(f"\n❌ Error al escribir el archivo de workflow final: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
