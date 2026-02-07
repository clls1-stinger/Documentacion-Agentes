#!/usr/bin/env python3
"""
🛰️ Vega Master Orchestrator Patch (with Puppeteer Integration)
1. Fixes Tool Router connections (unscrambles them).
2. Syncs Planner Prep prompt with ACTUAL tools and rules, including Puppeteer.
3. Adds 'leer_archivo' capability (already there, just re-ensured).
4. Adds 'navegar_web' (Puppeteer) capability.
5. Adds a new 'Execute Command (Puppeteer)' node.
"""

import sqlite3
import json
import sys
import os
from pathlib import Path
import uuid

# Configuración
N8N_DB = Path.home() / ".n8n" / "database.sqlite"
WORKFLOW_ID = "Urf7HpECFvfQooAv"
PUPPETEER_BRIDGE_PATH = "/home/emky/n8n/documentacion/SCRIPTS_AND_TOOLS/puppeteer_mcp_bridge.py"
VENV_PYTHON_PATH = "/home/emky/n8n/documentacion/SCRIPTS_AND_TOOLS/.venv_mcp/bin/python"

def get_workflow_from_db():
    """Obtiene el workflow desde SQLite"""
    conn = sqlite3.connect(N8N_DB)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, nodes, connections, name
        FROM workflow_entity 
        WHERE id = ?
    """, (WORKFLOW_ID,))
    
    result = cursor.fetchone()
    conn.close()
    
    if not result:
        print(f"❌ No se encontró el workflow con ID '{WORKFLOW_ID}'")
        sys.exit(1)
    
    workflow_id, nodes, connections, name = result
    
    return {
        'id': workflow_id,
        'nodes': json.loads(nodes) if nodes else [],
        'connections': json.loads(connections) if connections else {},
        'name': name
    }

def patch_workflow(workflow):
    nodes = workflow['nodes']
    connections = workflow['connections']
    patched_count = 0
    
    # 1. Update Planner Prep Prompt
    planner_prep_node = next((n for n in nodes if n['name'] == 'Planner Prep'), None)
    if planner_prep_node:
        new_prompt_code = r"""return $input.all().map(item => {
  const goal = item.json.user_goal;
  const chatHistory = item.json.chat_history || [];
  const stepHistory = item.json.history || [];
  const counter = item.json.counter || 0;

  let memoryText = chatHistory.length > 0 ? chatHistory.map(h => `User: ${h.user}\nAI: ${h.ai}`).join("\n---\n") : "No hay historial.";
  let historyText = stepHistory.length > 0 ? stepHistory.map((h, i) => `STEP ${i+1}: ${h.action} -> ${h.result}`).join("\n") : "Sin acciones previas.";

  const prompt = `IDENTIDAD: VEGA OS.
Usuario: Emky.
Estado del Sistema: Operativo.

=== CAPACIDADES (HERRAMIENTAS) ===
1. buscar_en_drive(query): Busca archivos en Google Drive.
2. descargar_de_drive(fileId, filename): Descarga de Drive al sistema local.
3. subir_a_drive(filename): Sube un archivo local a Google Drive.
4. ejecutar_comando(command): Ejecuta comandos Linux (ls, grep, mkdir, unzip, etc.).
   - USA 'ls -R' PARA LISTAR DIRECTORIOS. No inventes 'list_directory'.
5. leer_archivo(path): Lee el contenido de un archivo de texto local.
6. navegar_web(url): Abre una URL en Brave (debug 9222) y retorna resultado (screenshot path, text).

=== PROTOCOLO DE RESPUESTA ===
- Si la tarea requiere pasos tecnicos, usa las herramientas.
- Si terminaste o es charla, establece is_done: true y llena final_response.
- NUNCA respondas con final_response null si is_done es true.

=== FORMATO JSON (ESTRICTO) ===
{
  "thought": "Breve analisis...",
  "next_instruction": "Nombre_Funcion(args...)",
  "is_done": boolean,
  "final_response": "Texto para el usuario (si is_done=true)"
}`;
        return { json: { prompt, history: stepHistory, chat_history: chatHistory, user_goal: goal, counter } };
});"""
        planner_prep_node['parameters']['jsCode'] = new_prompt_code
        patched_count += 1
        print("   ✅ Updated Planner Prep prompt with Puppeteer capability.")
    else:
        print("   ❌ Planner Prep node not found.")
    
    # 2. Add/Ensure Execute Command (Puppeteer) node exists
    puppeteer_exec_node_name = "Execute Command (Puppeteer)"
    puppeteer_exec_node = next((n for n in nodes if n['name'] == puppeteer_exec_node_name), None)

    if not puppeteer_exec_node:
        print(f"   ⚠️ '{puppeteer_exec_node_name}' not found. Adding new node...")
        tool_router_node = next((n for n in nodes if n['name'] == 'Tool Router'), None)
        pos_x, pos_y = tool_router_node['position'] if tool_router_node else (0,0)
        new_node_position = [pos_x + 300, pos_y + 350] # Adjusted position

        new_exec_node = {
            "parameters": {
                "command": f"={{ '{VENV_PYTHON_PATH} {PUPPETEER_BRIDGE_PATH} ' + $json.accion + ' ' + $json.datos.url }}",
                "options": {}
            },
            "id": str(uuid.uuid4()),
            "name": puppeteer_exec_node_name,
            "type": "n8n-nodes-base.executeCommand",
            "typeVersion": 1,
            "position": new_node_position
        }
        nodes.append(new_exec_node)
        puppeteer_exec_node = new_exec_node # Set it for later use
        patched_count += 1
        print(f"   ✅ Added new node: '{puppeteer_exec_node_name}'.")
    else:
        # Ensure its command is correct in case it was modified
        current_command = puppeteer_exec_node['parameters']['command']
        expected_command = f"={{ '{VENV_PYTHON_PATH} {PUPPETEER_BRIDGE_PATH} ' + $json.accion + ' ' + $json.datos.url }}"
        if current_command != expected_command:
            puppeteer_exec_node['parameters']['command'] = expected_command
            patched_count += 1
            print(f"   ✅ Ensured '{puppeteer_exec_node_name}' command is correct.")
        else:
            print(f"   ℹ️ Node '{puppeteer_exec_node_name}' already exists and has correct command.")
    
    # 3. Update Tool Router rules and connections
    tool_router_node = next((n for n in nodes if n['name'] == 'Tool Router'), None)
    if tool_router_node:
        # Add new rule for navegar_web
        new_rule_navegar_web = {"conditions": {"conditions": [{"leftValue": "={{ $json.accion }}", "operator": {"type": "string", "operation": "equals"}, "rightValue": "navegar_web"}]}}
        
        # Ensure rules are a list and add if not present
        if new_rule_navegar_web not in tool_router_node['parameters']['rules']['values']:
            tool_router_node['parameters']['rules']['values'].append(new_rule_navegar_web)
            patched_count += 1
            print("   ✅ Added navegar_web rule to Tool Router.")
        else:
            print("   ℹ️ navegar_web rule already exists in Tool Router.")

        # Update ALL Tool Router connections, including the new one
        # Current connections are 0->Drive Search, 1->Drive Download, 2->Drive Upload, 3->Execute Command, 4->Read Disk
        # New connection for navegar_web will be 5
        connections['Tool Router'] = {
            "main": [
                [{"node": "Drive Search", "type": "main", "index": 0}],        # 0: buscar
                [{"node": "Drive Download", "type": "main", "index": 0}],      # 1: descargar
                [{"node": "Drive Upload", "type": "main", "index": 0}],        # 2: subir
                [{"node": "Execute Command", "type": "main", "index": 0}],     # 3: ejecutar (general)
                [{"node": "Read Disk", "type": "main", "index": 0}],           # 4: leer
                [{"node": puppeteer_exec_node_name, "type": "main", "index": 0}] # 5: navegar_web (Puppeteer)
            ]
        }
        patched_count += 1
        print("   ✅ Unscrambled Tool Router connections (including Puppeteer).")
    else:
        print("   ❌ Tool Router node not found.")

    return patched_count

def save_workflow_to_db(workflow):
    """Guarda el workflow modificado en SQLite"""
    conn = sqlite3.connect(N8N_DB)
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE workflow_entity 
        SET nodes = ?,
            connections = ?,
            updatedAt = datetime('now')
        WHERE id = ?
    """, (
        json.dumps(workflow['nodes']),
        json.dumps(workflow['connections']),
        workflow['id']
    ))
    
    conn.commit()
    conn.close()
    print(f"✅ Workflow guardado en DB (ID: {workflow['id']})")

def main():
    print("🚀 Running Vega Orchestrator Fix...\n")
    workflow = get_workflow_from_db()
    if not workflow:
        print("Workflow 'Yes' not found.")
        sys.exit(1)
    
    count = patch_workflow(workflow)
    save_workflow_to_db(workflow)
    print(f"\n✨ System synchronized. REFRESH N8N (F5) NOW.")

if __name__ == "__main__":
    main()