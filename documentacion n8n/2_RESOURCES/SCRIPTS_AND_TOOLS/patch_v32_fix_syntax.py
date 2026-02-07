#!/usr/bin/env python3
"""
🛰️ Vega Core Authority v32: SYNTAX REPAIR
Fixes the "Unterminated string constant" error in Planner Prep node.
Replaces literal newlines in joins with proper escapes.
"""

import sqlite3
import json
from pathlib import Path

N8N_DB = Path.home() / ".n8n" / "database.sqlite"
WORKFLOW_ID = "Urf7HpECFvfQooAv"

def patch():
    conn = sqlite3.connect(N8N_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT nodes FROM workflow_entity WHERE id = ?", (WORKFLOW_ID,))
    row = cursor.fetchone()
    if not row:
        print(f"❌ Workflow {WORKFLOW_ID} not found.")
        return
    
    nodes = json.loads(row[0])
    patched = False
    
    for node in nodes:
        if node['name'] == 'Planner Prep':
            print("   ✏️ Patching 'Planner Prep' v32 (Correcting Syntax)...")
            # Using raw string to avoid python escape issues, then ensuring multi-lines use \n
            node['parameters']['jsCode'] = r"""return $input.all().map(item => {
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
   - USA 'ls -R' PARA LISTAR DIRECTORIOS.
5. leer_archivo(path): Lee el contenido de un archivo de texto local.
6. navegar_web(url): Abre una URL en Brave (debug 9222).

=== OBJETIVO ACTUAL ===
${goal}

=== HISTORIAL DE ACCIONES (ESTO YA PASO) ===
${historyText}

=== PROTOCOLO DE RESPUESTA (ESTRICTO) ===
- No saludes. No digas 'Online'. No te presentes.
- Si el objetivo requiere pasos tecnicos, USA LAS HERRAMIENTAS INMEDIATAMENTE.
- No termines la tarea (is_done: true) hasta que el objetivo este CUMPLIDO.
- Si el objetivo es 'Busca archivos', la respuesta DEBE incluir 'next_instruction' con 'buscar_en_drive'.

=== FORMATO JSON ===
{
  "thought": "Analisis de que herramienta necesito ahora...",
  "next_instruction": "Nombre_Funcion(args...)",
  "is_done": false,
  "final_response": null
}`;
        return { json: { prompt, history: stepHistory, chat_history: chatHistory, user_goal: goal, counter } };
});"""
            patched = True

    if patched:
        cursor.execute("UPDATE workflow_entity SET nodes = ?, updatedAt = datetime('now') WHERE id = ?", 
                      (json.dumps(nodes), WORKFLOW_ID))
        conn.commit()
        print("✅ Database updated successfully.")
    else:
        print("⚠️ Planner Prep node not found in this workflow.")
        
    conn.close()

if __name__ == "__main__":
    patch()
