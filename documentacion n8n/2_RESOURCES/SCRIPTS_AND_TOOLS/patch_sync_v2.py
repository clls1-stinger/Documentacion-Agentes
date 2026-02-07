#!/usr/bin/env python3
"""
🛰️ Vega Core Synchronization v2 (The "No more non-responsive" patch)
1. Fixes Init Context (Smart input detection).
2. Fixes Planner Prep (Prompt structure & History inclusion).
3. Hardens Parse Planner (Detection of JSON in markdown).
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
    cursor.execute("SELECT id, nodes, connections, name FROM workflow_entity WHERE id = ?", (WORKFLOW_ID,))
    result = cursor.fetchone()
    conn.close()
    if not result: return None
    return {
        'id': result[0], 
        'nodes': json.loads(result[1]), 
        'connections': json.loads(result[2]), 
        'name': result[3]
    }

def patch_workflow(workflow):
    nodes = workflow['nodes']
    patched = 0
    
    for node in nodes:
        # 1. Smart Init Context
        if node['name'] == 'Init Context':
            print("   ✏️ Patching 'Init Context'...")
            node['parameters']['jsCode'] = r"""// Detect user message from ANY input node
const inputs = $input.all();
let message = "";

// Check current input
if (inputs.length > 0 && inputs[0].json.chatInput) {
    message = inputs[0].json.chatInput;
} else {
    // Fallback to searching node data
    try { 
        message = $node["When chat message received"].json.chatInput; 
    } catch(e) {
        message = "No se detectó mensaje del usuario.";
    }
}

let longTermHistory = [];
try {
  const historyData = $node["Read History"].json.data || $node["Read History"].json.content;
  if (historyData) {
    longTermHistory = (typeof historyData === 'string') ? JSON.parse(historyData) : historyData;
  }
} catch (e) {
  longTermHistory = [];
}

return [{ 
  json: { 
    user_goal: message, 
    chat_history: longTermHistory, 
    history: [], 
    counter: 0 
  } 
}];"""
            patched += 1

        # 2. Complete Planner Prep
        if node['name'] == 'Planner Prep':
            print("   ✏️ Patching 'Planner Prep'...")
            node['parameters']['jsCode'] = r"""return $input.all().map(item => {
  const goal = item.json.user_goal;
  const chatHistory = item.json.chat_history || [];
  const stepHistory = item.json.history || [];
  const counter = item.json.counter || 0;

  let memoryText = chatHistory.length > 0 ? chatHistory.map(h => `Usuario: ${h.user}\nVega: ${h.ai}`).join("\n---\n") : "Inicio de sesión.";
  let historyText = stepHistory.length > 0 ? stepHistory.map((h, i) => `PASO ${i+1}: ${h.action} -> ${h.result}`).join("\n") : "Ninguna acción técnica en esta sesión.";

  const prompt = `ERES VEGA OS. Kernel de n8n.
Usuario: Emky.

=== MEMORIA DE CONTEXTO ===
${memoryText}

=== CAPACIDADES TÉCNICAS ===
1. buscar_en_drive(query): IDs de archivos.
2. descargar_de_drive(fileId, filename): A disco local.
3. subir_a_drive(filename): De local a Drive.
4. ejecutar_comando(command): Bash (ls, grep, mkdir, unzip, rm, etc.). 
   - REGLA: Para ver archivos usa 'ls -R'.
5. leer_archivo(path): Contenido de texto.

=== PROTOCOLO ===
- OBJETIVO ACTUAL: "${goal}"
- PASOS REALIZADOS: ${historyText}

Si el objetivo requiere acción técnica, USA UNA HERRAMIENTA (is_done: false).
Si terminaste o solo es charla, RESPONDE (is_done: true).

RESPUESTA CORTA Y EN JSON PURO:
{
  "thought": "análisis",
  "next_instruction": "Herramienta(args) o null",
  "is_done": boolean,
  "final_response": "Texto para el usuario (OBLIGATORIA SI is_done: true)"
}`;

  return { json: { prompt, history: stepHistory, chat_history: chatHistory, user_goal: goal, counter } };
});"""
            patched += 1

        # 3. Robust Parse Planner
        if node['name'] == 'Parse Planner':
            print("   ✏️ Patching 'Parse Planner'...")
            node['parameters']['jsCode'] = r"""const item = $input.item.json;
let raw = item.output || item.response || "";
let parsed = { is_done: false };

try {
  let text = (typeof raw === 'string') ? raw : JSON.stringify(raw);
  
  // Regex para extraer el JSON si viene envuelto en markdown o texto
  const match = text.match(/\{[\s\S]*\}/);
  if (match) {
    parsed = JSON.parse(match[0]);
  } else if (text.trim() !== "") {
    // Si no hay JSON pero hay texto, asumimos que es respuesta directa
    parsed = { is_done: true, final_response: text };
  }
} catch(e) {
  parsed = { is_done: true, final_response: "Error técnico: " + e.message };
}

// Normalización
parsed.is_done = (parsed.is_done === true || parsed.is_done === 'true');
if (parsed.is_done && !parsed.final_response) {
  parsed.final_response = "Tarea procesada correctamente.";
}

return [{ json: { ...item, planner_output: parsed } }];"""
            patched += 1

    return patched

def save_workflow_to_db(workflow):
    conn = sqlite3.connect(N8N_DB)
    cursor = conn.cursor()
    cursor.execute("UPDATE workflow_entity SET nodes = ?, updatedAt = datetime('now') WHERE id = ?", 
                  (json.dumps(workflow['nodes']), workflow['id']))
    conn.commit()
    conn.close()

def main():
    print("🛰️ Vega Core Sync v2 starting...\n")
    workflow = get_workflow_from_db()
    if not workflow:
        sys.exit(1)
    
    count = patch_workflow(workflow)
    save_workflow_to_db(workflow)
    print(f"\n✅ Sync complete ({count} nodes). F5 en n8n.")

if __name__ == "__main__":
    main()
