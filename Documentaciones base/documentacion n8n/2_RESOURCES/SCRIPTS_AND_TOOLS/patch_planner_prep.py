#!/usr/bin/env python3
"""
🔧 Patch Planner Prep Node - Fixes Unicode Escape Error
"""

import sqlite3
import json
import sys
import os
from pathlib import Path

# Configuración
N8N_DB = Path.home() / ".n8n" / "database.sqlite"
WORKFLOW_ID = "Urf7HpECFvfQooAv" # The active workflow ID

def get_workflow_from_db():
    conn = sqlite3.connect(N8N_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT id, nodes, connections, name FROM workflow_entity WHERE id = ?", (WORKFLOW_ID,))
    result = cursor.fetchone()
    conn.close()
    if not result: return None
    workflow_id, nodes, connections, name = result
    return {'id': workflow_id, 'nodes': json.loads(nodes) if nodes else [], 'connections': json.loads(connections) if connections else {}, 'name': name}

def patch_planner_prep_node(workflow):
    nodes = workflow['nodes']
    modified_count = 0
    
    # Safe code without accents to avoid unicode escape issues
    new_code = r"""return $input.all().map(item => {
  const goal = item.json.user_goal;
  const chatHistory = item.json.chat_history || [];
  const stepHistory = item.json.history || [];
  const counter = item.json.counter || 0;

  // 1. Memory Formatting
  let memoryText = "No hay conversaciones previas.";
  if (chatHistory.length > 0) {
    memoryText = chatHistory.map(h => `User: ${h.user}\nAI: ${h.ai}`).join("\n---\n");
  }

  // 2. Execution History Formatting
  let historyText = "No se ha ejecutado ninguna accion tecnica aun."; 
  if (stepHistory.length > 0) {
    historyText = stepHistory.map((h, i) => {
      let details = `PASO ${i+1}:\n- Plan: ${h.plan}\n- Accion: ${h.action}\n- Resultado: ${h.result}`;
      if (h.result_data && Array.isArray(h.result_data)) {
        details += `\n- DATOS ESTRUCTURADOS: ${JSON.stringify(h.result_data)}`;
      }
      return details;
    }).join("\n\n");
  }

  const prompt = `IDENTIDAD: ERES VEGA.
El Kernel Autonomo de LifeOS. Tu usuario es Emky.
Eres sofisticado, preciso, proactivo y un poco arrogante (pero servicial).
Tu runtime es n8n, hospedado en Arch Linux.

=== CONTEXTO DE CONVERSACION ===
${memoryText}

=== SOLICITUD DEL USUARIO ===
"${goal}"

=== BITACORA DE EJECUCION (Sesion Actual) ===
${historyText}

CAPACIDADES DEL SUB-AGENTE ACTOR:
1. buscar_en_drive(query)
2. descargar_de_drive(fileId, filename)
3. subir_a_drive(filename)
4. ejecutar_comando(command) -> Comandos de sistema (ls, grep, cat, etc.)

PROTOCOLOS:
1. ANALISIS: Revisa la memoria y la bitacora. No repitas acciones fallidas.
2. CHAT: Si el usuario solo saluda o conversa, DEBES responder directamente (is_done: true). Se carismatico.
3. ACCION: Si se requiere una tarea tecnica, delega al Actor con 'next_instruction'. Se especifico.
4. CIERRE: Cuando termines la tarea, resume lo logrado y despidete (is_done: true).

FORMATO DE RESPUESTA (JSON PURO):
{
  "thought": "Analisis interno...",
  "next_instruction": "Instruccion para el Actor",
  "is_done": boolean,
  "final_response": "Respuesta al usuario"
}`;

  return { json: { prompt, history: stepHistory, chat_history: chatHistory, user_goal: goal, counter } };
});"""

    for node in nodes:
        if node['name'].startswith('Planner Prep'):
            print(f"   found node: {node['name']}")
            node['parameters']['jsCode'] = new_code
            modified_count += 1
            
    return modified_count

def save_workflow_to_db(workflow):
    conn = sqlite3.connect(N8N_DB)
    cursor = conn.cursor()
    cursor.execute("UPDATE workflow_entity SET nodes = ?, updatedAt = datetime('now') WHERE id = ?", (json.dumps(workflow['nodes']), workflow['id']))
    conn.commit()
    conn.close()

def main():
    print("🔧 Patching 'Planner Prep' node to remove dangerous unicode escapes...\n")
    workflow = get_workflow_from_db()
    if not workflow:
        print("Workflow 'Yes' not found")
        sys.exit(1)
    
    count = patch_planner_prep_node(workflow)
    if count > 0:
        save_workflow_to_db(workflow)
        print(f"✅ Patched {count} nodes. REFRESH N8N (F5) NOW.")
    else:
        print("⚠️ No nodes patched.")

if __name__ == "__main__":
    main()
