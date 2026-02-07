#!/usr/bin/env python3
"""
🔧 Patch Planner Prep and Parser - Robustness Upgrade
1. Updates 'Planner Prep' prompt to strictly enforce 'final_response'.
2. Updates 'Parse Planner' to aggressively normalize/complete responses.
"""

import sqlite3
import json
import sys
import os
from pathlib import Path

# Configuración
N8N_DB = Path.home() / ".n8n" / "database.sqlite"
WORKFLOW_ID = "Urf7HpECFvfQooAv"

def get_workflow_from_db():
    conn = sqlite3.connect(N8N_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT id, nodes, name FROM workflow_entity WHERE id = ?", (WORKFLOW_ID,))
    result = cursor.fetchone()
    conn.close()
    if not result: return None
    return {'id': result[0], 'nodes': json.loads(result[1]), 'name': result[2]}

def patch_nodes(workflow):
    nodes = workflow['nodes']
    patched = 0
    
    # NEW PROMPT CODE
    # Note: Using ASCII only to avoid unicode issues
    new_prep_code = r"""return $input.all().map(item => {
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
1. ANALISIS: Revisa la memoria y la bitacora.
2. CHAT: Si el usuario solo saluda, RESPONDE DIRECTAMENTE (is_done: true).
3. ACCION: Si se requiere una tarea tecnica, delega al Actor.
4. CIERRE: Si completaste la tarea, resume lo logrado y despidete (is_done: true).

CRITICO: SI is_done ES TRUE, EL CAMPO final_response ES OBLIGATORIO.
NO DEJES final_response VACIO O NULL. DEBE SER UN TEXTO PARA EL USUARIO.

FORMATO DE RESPUESTA (JSON PURO):
{
  "thought": "Analisis interno...",
  "next_instruction": "Instruccion para el Actor (null si is_done=true)",
  "is_done": boolean,
  "final_response": "Respuesta al usuario (OBLIGATORIA si is_done=true)"
}`;

  return { json: { prompt, history: stepHistory, chat_history: chatHistory, user_goal: goal, counter } };
});"""

    # NEW PARSER CODE
    new_parser_code = r"""const item = $input.item.json;
let raw = item.output || item.response || '{}';
let parsed = { is_done: false, final_response: null };

try {
  // Intentar parsear si es string
  if (typeof raw === 'string') {
     // Limpieza básica de markdown ```json ... ```
     raw = raw.replace(/```json/g, '').replace(/```/g, '').trim();
     parsed = JSON.parse(raw);
  } else {
     parsed = raw;
  }
} catch(e) {
  // Si falla el parseo, asumimos que es texto plano de chat
  parsed = {
    is_done: true,
    final_response: typeof raw === 'string' ? raw : "Error parseando respuesta del agente"
  };
}

// 1. Normalizar is_done a Boolean Real
if (typeof parsed.is_done === 'string') {
    parsed.is_done = (parsed.is_done.toLowerCase() === 'true');
}
parsed.is_done = !!parsed.is_done; // Force boolean

// 2. Validar final_response si hemos terminado
if (parsed.is_done) {
    if (!parsed.final_response || (typeof parsed.final_response === 'string' && parsed.final_response.trim() === '')) {
        // Fallback robusto en Español
        parsed.final_response = "Entendido. Tarea completada."; 
    }
}

return [{ json: { ...item, planner_output: parsed } }];"""

    for node in nodes:
        if node['name'] == 'Planner Prep':
            print(f"   ✏️ Patching 'Planner Prep' (Prompt update)")
            node['parameters']['jsCode'] = new_prep_code
            patched += 1
            
        elif node['name'] == 'Parse Planner':
             print(f"   ✏️ Patching 'Parse Planner' (Logic update)")
             node['parameters']['jsCode'] = new_parser_code
             patched += 1

    return patched

def save_workflow_to_db(workflow):
    conn = sqlite3.connect(N8N_DB)
    cursor = conn.cursor()
    cursor.execute("UPDATE workflow_entity SET nodes = ?, updatedAt = datetime('now') WHERE id = ?", (json.dumps(workflow['nodes']), workflow['id']))
    conn.commit()
    conn.close()

def main():
    print("🔧 Patching Planner and Parser...\n")
    workflow = get_workflow_from_db()
    if not workflow:
        print("Workflow not found")
        sys.exit(1)
    
    count = patch_nodes(workflow)
    if count > 0:
        save_workflow_to_db(workflow)
        print(f"\n✅ Patched {count} items. REFRESH N8N (F5) NOW.")
    else:
        print("\n⚠️ No changes needed.")

if __name__ == "__main__":
    main()
