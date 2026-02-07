#!/usr/bin/env python3
"""
🛠️ Hot Patch n8n Workflow - v11 (Unified Patch - FINAL FINAL FINAL FINAL Correction)

Este script implementa la estrategia 'Nuke and Pave'. Carga el workflow base
desde un archivo, aplica todas las correcciones acumuladas en memoria
y luego lo inserta como un nuevo workflow en la base de datos de n8n.
Esta versión corrige el error de constraint NOT NULL para la columna 'active'.
"""

import sqlite3
import json
import sys
import uuid
from pathlib import Path

# --- Configuración ---
N8N_DB = Path.home() / ".n8n" / "database.sqlite"
# Archivo de workflow original (conocido como bueno) - RUTA AL FORENSIC DUMP
GEMINI_REACT_AGENT_V1_JSON_PATH = Path("./documentacion/FORENSICS_AND_LOGS/workflow_yes_dump.json")
# Nuevo nombre para el workflow parcheado
PATCHED_WORKFLOW_NAME = "Gemini ReAct Agent - Patched V11"
PROMPT_FILE_PATH = Path("./documentacion/SCRIPTS_AND_TOOLS/prompt_v4.txt") # Relative path

# --- Plantilla de Código JS para Planner Prep ---
# NOTA: Los `{{` y `}}` son para que Python los interprete como literales de `{` y `}`
# El `\n` y `\t` en las strings JS son importantes para la legibilidad en n8n
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
# NOTA: Usar r"""...""" y escapar '\n' para evitar problemas con Python y JS.
JS_AGGREGATOR_CODE = r"""let result = "Success";
let structured_data = null;

if (items.length > 0) {{
  // Caso 1: Resultado de Drive Search (contiene 'id' y 'name')
  if (items[0].json.id && items[0].json.name) {{
     result = items.map(i => `[FILE] ${i.json.name} (${i.json.id})`).join(", ");
     structured_data = items.map(i => ({{
       id: i.json.id, 
       name: i.json.name, 
       mimeType: i.json.mimeType || 'unknown'
     }}));
  }} 
  // Caso 2: Resultado de Execute Command (contiene 'stdout' o 'stderr')
  else if (items[0].json.hasOwnProperty('stdout')) {{
     result = items[0].json.stdout;
  }}
  else if (items[0].json.hasOwnProperty('stderr')) {{ // Added check for stderr
     result = items[0].json.stderr;
  }}
  // Caso 3: Resultado binario (de una descarga, etc.)
  else if (items[0].binary) {{
     result = "Binary data processed successfully.";
  }}
  // Fallback por si la estructura cambia en el futuro
  else {{
    result = "Resultado de herramienta no reconocido, pero la operación fue exitosa.";
  }}
}} else {{
  result = "La herramienta se ejecutó pero no produjo ningún resultado (ej. búsqueda sin resultados).";
}}


// Aggregate for History WITH structured data
const prev = $("Clean Actor").last().json;
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
# SINTAXIS CORREGIDA: Usar { para dict, no {{ 
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
    print(f"🔧 Hot Patch v11 (Unified Patch - FINAL Final Correction) - Iniciando estrategia 'Nuke and Pave'...")
    
    # 0. Cargar el workflow base
    print(f"📖 Cargando workflow base desde: '{GEMINI_REACT_AGENT_V1_JSON_PATH}'")
    try:
        with open(GEMINI_REACT_AGENT_V1_JSON_PATH, 'r', encoding='utf-8') as f:
            workflow_data = json.load(f)
    except FileNotFoundError:
        print(f"❌ Error: Archivo de workflow base no encontrado: '{GEMINI_REACT_AGENT_V1_JSON_PATH}'")
        sys.exit(1)

    # Establecer nuevo ID y nombre
    workflow_data['id'] = str(uuid.uuid4())
    workflow_data['name'] = PATCHED_WORKFLOW_NAME
    # Asegurarse de que el campo 'active' esté presente y sea 1
    workflow_data['active'] = 1 
    
    nodes = workflow_data['nodes']
    connections = workflow_data['connections']
    print(f"✅ Workflow base cargado y preparado con nuevo ID: {workflow_data['id']} y nombre: '{PATCHED_WORKFLOW_NAME}'.")

    # 1. Aplicar parche a Planner Prep (Anti-Sesgo)
    print("🔨 Aplicando parche a 'Planner Prep' (Anti-Sesgo)...")
    planner_prep_node = next((n for n in nodes if n.get('name') == 'Planner Prep'), None)
    if not planner_prep_node:
        print("❌ Error: Nodo 'Planner Prep' no encontrado en el workflow base.")
        sys.exit(1)
    
    try:
        prompt_text = PROMPT_FILE_PATH.read_text(encoding='utf-8')
        # Escapar backticks y backslashes para la inyección en el template string de JS
        prompt_text = prompt_text.replace('\\', '\\\\').replace('`', r'\`')
    except FileNotFoundError:
        print(f"❌ Error: Archivo de prompt '{PROMPT_FILE_PATH}' no encontrado.")
        sys.exit(1)
    
    planner_prep_node['parameters']['jsCode'] = JS_PLANNER_PREP_TEMPLATE.replace('{PROMPT_PLACEHOLDER}', prompt_text)
    print("✅ Parche 'Planner Prep' aplicado.")

    # 2. Aplicar parche a Aggregator (Salida de comandos)
    print("🔨 Aplicando parche a 'Aggregator' (Salida de comandos robusta)...")
    aggregator_node = next((n for n in nodes if n.get('name') == 'Aggregator'), None)
    if not aggregator_node:
        print("❌ Error: Nodo 'Aggregator' no encontrado en el workflow base.")
        sys.exit(1)
    aggregator_node['parameters']['jsCode'] = JS_AGGREGATOR_CODE
    print("✅ Parche 'Aggregator' aplicado.")

    # 3. Aplicar parche a Tool Router (Regex y ruta correcta)
    print("🔨 Aplicando parche a 'Tool Router' (Regex y ruta de datos)...")
    tool_router_node = next((n for n in nodes if n.get('name') == 'Tool Router'), None)
    if not tool_router_node:
        print("❌ Error: Nodo 'Tool Router' no encontrado en el workflow base.")
        sys.exit(1)

    rules = tool_router_node['parameters']['rules']['values']
    for rule in rules:
        condition = rule['conditions']['conditions'][0]
        condition['leftValue'] = CORRECT_ROUTER_INPUT_PATH
        condition['operator']['operation'] = 'regex'
        original_value_key = condition.get('rightValue', '').strip('/').strip('i') # Eliminar / y i para buscar en el mapa
        if original_value_key in ROUTER_RULES_MAP:
            condition['rightValue'] = ROUTER_RULES_MAP[original_value_key]
        else:
            print(f"  - ⚠️ Advertencia: No se encontró un regex específico para la regla '{original_value_key}'.")
            # Fallback seguro: intentar convertir a regex simple si no está en el mapa
            condition['rightValue'] = f"/{original_value_key.replace('.', '\\.')}/i"
    print("✅ Parche 'Tool Router' aplicado.")
    
    # 4. Insertar el workflow totalmente parcheado en la DB
    print(f"💾 Insertando el workflow '{PATCHED_WORKFLOW_NAME}' en la base de datos de n8n...")
    try:
        conn = sqlite3.connect(N8N_DB)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO workflow_entity (id, name, nodes, connections, staticData, settings, createdAt, updatedAt, active) VALUES (?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'), ?)",
            (
                workflow_data['id'],
                workflow_data['name'],
                json.dumps(workflow_data['nodes']),
                json.dumps(workflow_data['connections']),
                json.dumps(workflow_data.get('staticData', {})),
                json.dumps(workflow_data.get('settings', {})),
                workflow_data['active'] # Añadir el valor para 'active'
            )
        )
        conn.commit()
        conn.close()
        print(f"✅ Workflow '{PATCHED_WORKFLOW_NAME}' insertado con éxito en la base de datos.")
    except sqlite3.IntegrityError as e:
        print(f"❌ Error de integridad al insertar el workflow (posiblemente ya existe un workflow con ese ID): {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error Inesperado al guardar el workflow: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    print("\n✨ ¡Proceso 'Nuke and Pave' completado con éxito!")
    print(f"   El nuevo workflow '{PATCHED_WORKFLOW_NAME}' está ahora en la base de datos.")
    print("   Por favor, haz F5 en n8n o reinicia el servicio para que el nuevo workflow sea visible y activo.")
    print("   Procederé a la limpieza final de los scripts temporales.")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error General del script: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)