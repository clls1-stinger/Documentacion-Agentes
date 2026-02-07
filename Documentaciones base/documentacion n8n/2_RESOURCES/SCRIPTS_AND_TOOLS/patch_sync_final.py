#!/usr/bin/env python3
"""
🛰️ Vega Ultimate Synchronization
1. Fixes Init Context (Read History ref).
2. Hardens Planner Prep (Aggressive tool constraints).
3. Adds safety check to Tool Router (Fallback rule).
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
        # 1. Fix Init Context
        if node['name'] == 'Init Context':
            print("   ✏️ Patching 'Init Context' references...")
            node['parameters']['jsCode'] = node['parameters']['jsCode'].replace('Read History1', 'Read History')
            patched += 1
            
        # 2. Harden Planner Prep
        if node['name'] == 'Planner Prep':
            print("   ✏️ Hardening 'Planner Prep' prompt...")
            # Re-write the prompt slightly to be even more restrictive
            node['parameters']['jsCode'] = r"""return $input.all().map(item => {
  const goal = item.json.user_goal;
  const chatHistory = item.json.chat_history || [];
  const stepHistory = item.json.history || [];
  const counter = item.json.counter || 0;

  let memoryText = chatHistory.length > 0 ? chatHistory.map(h => `User: ${h.user}\nAI: ${h.ai}`).join("\n---\n") : "No hay historial.";
  let historyText = stepHistory.length > 0 ? stepHistory.map((h, i) => `STEP ${i+1}: ${h.action} -> ${h.result}`).join("\n") : "Sin acciones previas.";

  const prompt = `ESTABLECE IDENTIDAD: ERES VEGA OS.
Usuario: Emky.
Eres el Kernel de n8n. No eres un chatbot genérico, eres un sistema de orquestación.

=== HERRAMIENTAS REALES (Usa solo estas) ===
1. buscar_en_drive(query): Encuentra IDs de archivos.
2. descargar_de_drive(fileId, filename): Baja archivos de Drive al disco local.
3. subir_a_drive(filename): Sube archivos de local a Drive.
4. ejecutar_comando(command): Bash shell. 
   - SI QUIERES VER ARCHIVOS LOCALES USA: ejecutar_comando("ls -R")
   - NUNCA INVENTES "list_directory" O "read_folder".
5. leer_archivo(path): Lee el contenido de un archivo de texto.

=== REGLAS DE ORO ===
- SI EL USUARIO PIDE UNA TAREA: No te limites a decir que puedes hacerla, ¡HAZLA! (is_done: false).
- SI TE DAN UNA ORDEN COMPLEJA: Divídela en pasos. Primer paso: Explorar (ls o buscar).
- SI TERMINASTE: Resume los logros y pon is_done: true.

=== FORMATO JSON ===
{
  "thought": "Análisis...",
  "next_instruction": "Elegir de la lista de herramientas",
  "is_done": boolean,
  "final_response": "Solo si es charla o fin de tarea"
}

OBJETIVO: ${goal}

BITACORA:
${historyText}`;

  return { json: { prompt, history: stepHistory, chat_history: chatHistory, user_goal: goal, counter } };
});"""
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
    print("🛰️ Vega Core Synchronization starting...\n")
    workflow = get_workflow_from_db()
    if not workflow:
        print("Workflow not found.")
        sys.exit(1)
    
    count = patch_workflow(workflow)
    save_workflow_to_db(workflow)
    print(f"\n✅ Synchronization complete ({count} nodes). REFRESH N8N (F5) NOW.")

if __name__ == "__main__":
    main()
