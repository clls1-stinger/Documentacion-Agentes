#!/usr/bin/env python3
"""
🛰️ Vega Core Authority v4: THE ANTI-HALLUCINATION PATCH
1. Stricter Schema enforcement in Planner Prep.
2. Fuzzy Parser to catch alucinations like 'tool_code' or 'list_directory'.
3. Automatic conversion of Pythonic hallucinations to Bash commands.
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
    nodes = json.loads(cursor.fetchone()[0])
    
    for node in nodes:
        if node['name'] == 'Planner Prep':
            print("   ✏️ Setting Ironclad Schema in Planner Prep...")
            node['parameters']['jsCode'] = r"""return $input.all().map(item => {
  const goal = item.json.user_goal;
  const chatHistory = item.json.chat_history || [];
  const stepHistory = item.json.history || [];
  
  let memoryText = chatHistory.length > 0 ? chatHistory.map(h => `Pregunta: ${h.user}\nRespuesta: ${h.ai}`).join("\n---\n") : "Nueva charla.";
  let historyText = stepHistory.length > 0 ? stepHistory.map((h, i) => `PASO ${i+1}: ${h.action} -> ${h.result}`).join("\n") : "Sin acciones previas.";

  const prompt = `SISTEMA OPERATIVO VEGA. NÚCLEO KERNEL.
Usuario: Emky.

TIENES ESTAS 5 HERRAMIENTAS REALES. NO INVENTES OTRAS:
1. buscar_en_drive(query): Encuentra archivos.
2. descargar_de_drive(fileId, filename): Baja a disco local.
3. subir_a_drive(filename): Sube de local a Drive.
4. ejecutar_comando(command): Bash real (ls, mkdir, unzip, rm).
5. leer_archivo(path): Lee texto local.

REGLAS DE ORO:
- NO INVENTES 'list_directory' o 'tool_code'. Usa solo 'ejecutar_comando' para ver carpetas (ls -R).
- USA ESTE ESQUEMA EXACTO. SI NO LO USAS, EL KERNEL FALLARÁ.
- "next_instruction" DEBE TENER EL COMANDO O NULL.

RESPUESTA UNICAMENTE EN JSON:
{
  "thought": "Análisis breve.",
  "next_instruction": "HerramientaReal(args)",
  "is_done": false,
  "final_response": null
}

OBJETIVO: "${goal}"
HISTORIAL: ${memoryText}
ACCIONES: ${historyText}`;

  return { json: { prompt, history: stepHistory, chat_history: chatHistory, user_goal: goal } };
});"""

        if node['name'] == 'Parse Planner':
            print("   ✏️ Enhancing 'Parse Planner' with Fuzzy Correction...")
            node['parameters']['jsCode'] = r"""const item = $input.item.json;
let raw = item.output || item.response || "";
let parsed = { is_done: false, final_response: null, next_instruction: null };

try {
  let text = (typeof raw === 'string') ? raw : JSON.stringify(raw);
  const match = text.match(/\{[\s\S]*\}/);
  if (match) {
    parsed = JSON.parse(match[0]);
  }
} catch(e) {}

// --- FIXER DE ALUCINACIONES (FUZZY LOGIC) ---
// 1. Si no hay next_instruction pero hay tool_code o tool_call
if (!parsed.next_instruction && (parsed.tool_code || parsed.tool_call)) {
  parsed.next_instruction = parsed.tool_code || parsed.tool_call;
}

// 2. Si intenta usar un list_directory inexistente, convertirlo a ls Bash
if (parsed.next_instruction && parsed.next_instruction.includes('list_directory')) {
  const matchDir = parsed.next_instruction.match(/dir_path=['"](.*?)['"]/);
  const dir = matchDir ? matchDir[1] : "./";
  parsed.next_instruction = `ejecutar_comando(command='ls -R ${dir}')`;
}

// 3. Normalización de estado Final
let isDone = (parsed.is_done === true || String(parsed.is_done).toLowerCase() === 'true');

if (!parsed.next_instruction) {
  isDone = true;
  if (!parsed.final_response) {
    parsed.final_response = "He analizado la situación pero no hay más acciones automáticas pendientes.";
  }
}

parsed.is_done = isDone;
return [{ json: { ...item, planner_output: parsed } }];"""

    cursor.execute("UPDATE workflow_entity SET nodes = ?, updatedAt = datetime('now') WHERE id = ?", 
                  (json.dumps(nodes), WORKFLOW_ID))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    patch()
    print("\n✅ Vega v4 (Anti-Hallucination) applied. F5 in n8n.")
